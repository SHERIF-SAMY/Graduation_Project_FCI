from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy import text
import uvicorn
import time
import asyncio
import json
import httpx
from typing import Optional

from utils.arabic_utils import translate_arabic_to_english
from utils.jwt_utils import extract_user_id_from_jwt

from models.request_models import ChatRequest, SearchRequest
from models.response_models import ChatResponse, SearchResponse, Product
from pipeline.orchestrator import run_chat_pipeline
from agents.sql_builder import build_sql
from sql.executor import execute_query
from ranking.ranker import rank_products
from formatter.response_formatter import format_search_response, format_product
from sql.db import get_engine

from recommendation.models import RecommendationRequest, RecommendationResponse
from recommendation.recommendation_engine import get_recommendations
from recommendation.interaction_logger import log_interaction
from memory.session_store import get_ui_history, clear_session

def _is_arabic(text: str) -> bool:
    if not text:
        return False
    return any('\u0600' <= c <= '\u06FF' for c in text)

app = FastAPI(title="AI Rental Marketplace Assistant", version="1.0.0")

# Force browsers to always fetch fresh static files (fixes ngrok cache issues)
@app.middleware("http")
async def no_cache_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/app"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/app")

@app.post("/auth/login")
async def auth_login_proxy(body: dict):
    """
    Proxy to the .NET Auth API to avoid CORS issues from the browser.
    Forwards { email, password } to the .NET backend and returns the token response.
    """
    dotnet_url = "https://rentalplatform.runasp.net/api/Account/login"
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.post(
                dotnet_url,
                json=body,
                headers={"Content-Type": "application/json"}
            )
        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        if response.status_code not in (200, 201):
            raise HTTPException(
                status_code=response.status_code,
                detail=data.get("message", "Login failed")
            )
        return data
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Cannot reach auth server: {str(e)}")




@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, fastapi_req: Request):
    lang = "ar" if _is_arabic(request.query) else "en"
    asyncio.create_task(log_interaction(
        "search", session_id=request.session_id,
        search_query=request.query, preferred_language=lang
    ))
    
    # Extract user_id from auth_token/Authorization header if missing
    user_id = (request.user_id or "").strip() or None
    auth_token = (request.auth_token or "").strip() or None

    # Fallback: check Authorization header if auth_token not in body
    if not auth_token:
        auth_header = fastapi_req.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            auth_token = auth_header[7:].strip()

    # Auto-extract user_id from JWT if missing
    if not user_id and auth_token:
        user_id = extract_user_id_from_jwt(auth_token)
        if user_id:
            print(f"[Chat] ✅ user_id auto-extracted from JWT: {user_id!r}")
        else:
            print(f"[Chat] ⚠️ auth_token present but user_id could not be extracted")
    else:
        print(f"[Chat] DEBUG | user_id={user_id!r} | auth_token={'SET' if auth_token else 'NONE'}")

    try:
        result = await run_chat_pipeline(
            request.query, 
            session_id=request.session_id or "default",
            user_id=user_id,       # ✅ local variable — not request.user_id
            auth_token=auth_token  # ✅ local variable — not request.auth_token
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    """
    Returns the stored UI chat history for a given session_id.
    Each item contains the user's message and the full AI response (including products).
    This allows the frontend to restore the conversation when the user navigates back.
    """
    history = get_ui_history(session_id)
    return {"session_id": session_id, "history": history, "count": len(history)}


@app.post("/chat/clear")
def clear_chat_session(body: dict):
    """
    Clears the in-memory chat history and booking context for a given session_id.
    Called by the frontend when the user presses the 'Clear Chat' button.
    """
    session_id = body.get("session_id", "")
    if not session_id:
        raise HTTPException(status_code=422, detail="session_id is required")
    clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    asyncio.create_task(log_interaction(
        "search", category=request.category, brand=request.brand,
        location_area=request.location, price_range=request.max_price
    ))
    start_time = time.time()
    
    # For /search, treat explicitly provided fields as 'entities'
    entities = request.model_dump(exclude_none=True)
    
    sql_query, sql_params = build_sql(entities)
    try:
        raw_products = execute_query(sql_query, sql_params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
        
    ranked_products = rank_products(raw_products, entities)
    latency_ms = int((time.time() - start_time) * 1000)
    
    return format_search_response(ranked_products, latency_ms, cached=False)

@app.get("/health")
def health_endpoint():
    status = {"status": "ok", "db": "unknown"}
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["db"] = "ok"
    except Exception as e:
        status["db"] = f"error: {str(e)}"
    return status

@app.get("/categories")
def get_categories():
    try:
        query = "SELECT DISTINCT CategoryId, CategoryName FROM Products_LLm WHERE Status = 1"
        rows = execute_query(query)
        return {"categories": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/live")
def live_search(q: str = ""):
    """Real-time search supporting natural language, filters (location, price, etc.) using LLM."""
    q = q.strip()
    if not q:
        # Return default active products if no query
        query = "SELECT TOP 8 * FROM Products_LLm WHERE Status = 1 ORDER BY FinalPricePerDay ASC"
        try:
            rows = execute_query(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        from agents.entity_extractor import extract_entities
        
        # 1. Extract entities using the same LLM logic as the chatbot
        entities = extract_entities(q)
        
        # 2. Build the SQL query using the extracted entities
        sql_query, sql_params = build_sql(entities)
        
        # 3. Execute and rank
        try:
            raw_products = execute_query(sql_query, sql_params)
            rows = rank_products(raw_products, entities)[:8]  # cap at 8
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    from formatter.response_formatter import format_product
    products = [format_product(r).model_dump() for r in rows]
    return {"products": products, "total": len(products)}

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    asyncio.create_task(log_interaction("view_product", product_id=product_id))
    try:
        query = "SELECT * FROM Products_LLm WHERE Id = :id"
        rows = execute_query(query, {"id": product_id})
        if not rows:
            raise HTTPException(status_code=404, detail="Product not found")
        return format_product(rows[0]).model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations", response_model=RecommendationResponse)
async def recommendations_endpoint(
    user_id:    Optional[str] = Query(default=None, max_length=100),
    session_id: Optional[str] = Query(default=None, max_length=100),
    query:      Optional[str] = Query(default=None, max_length=500),
    limit:      int           = Query(default=5, ge=1, le=20),
):
    if not user_id and not session_id:
        raise HTTPException(422, "Provide at least one of: user_id or session_id")
    req = RecommendationRequest(user_id=user_id, session_id=session_id,
                                 query=query, limit=limit)
    return await get_recommendations(req)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
