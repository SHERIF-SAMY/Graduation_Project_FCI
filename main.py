from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy import text
import uvicorn
import time

from utils.arabic_utils import translate_arabic_to_english

from models.request_models import ChatRequest, SearchRequest
from models.response_models import ChatResponse, SearchResponse, Product
from pipeline.orchestrator import run_chat_pipeline
from agents.sql_builder import build_sql
from sql.executor import execute_query
from ranking.ranker import rank_products
from formatter.response_formatter import format_search_response, format_product
from sql.db import get_engine

app = FastAPI(title="AI Rental Marketplace Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/app")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = await run_chat_pipeline(request.query, session_id=request.session_id or "default")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
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
    """Real-time search as user types — supports Arabic and English queries."""
    q = q.strip()
    if not q:
        # Return all active products if no query
        query = "SELECT TOP 8 * FROM Products_LLm WHERE Status = 1 ORDER BY FinalPricePerDay ASC"
        rows = execute_query(query)
    else:
        # Translate Arabic terms to English so they match the database
        q_english = translate_arabic_to_english(q)

        # Build search params — search original query AND the translated version
        search_terms = list({q, q_english})  # deduplicate

        all_rows: list = []
        seen_ids: set = set()

        for term in search_terms:
            sql_query = """
                SELECT TOP 8 * FROM Products_LLm
                WHERE Status = 1
                  AND (
                    Name         LIKE :q
                    OR Brand     LIKE :q
                    OR CategoryName LIKE :q
                    OR ProductType  LIKE :q
                    OR LocationArea LIKE :q
                  )
                ORDER BY FinalPricePerDay ASC
            """
            try:
                term_rows = execute_query(sql_query, {"q": f"%{term}%"})
                for row in term_rows:
                    row_id = row.get("Id")
                    if row_id not in seen_ids:
                        seen_ids.add(row_id)
                        all_rows.append(row)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        rows = all_rows[:8]  # cap at 8

    from formatter.response_formatter import format_product
    products = [format_product(r).model_dump() for r in rows]
    return {"products": products, "total": len(products)}

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
