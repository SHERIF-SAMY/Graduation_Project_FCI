import time
import asyncio
from typing import List, Tuple, Dict, Set
from sqlalchemy import text
from sql.db import get_engine
from formatter.response_formatter import format_product
from recommendation.models import RecommendationRequest, RecommendationResponse, UserProfile
from recommendation.preference_builder import build_user_profile
from recommendation.personalized_ranker import rank_personalized
from agents.recommendation_explainer import generate_recommendation_explanation

# FUTURE: Replace dict with Redis
_rec_cache = {}
CACHE_TTL = 300

def _get_engine():
    return get_engine()

def _build_sql(brand: str = None, category: str = None, exclude_ids: Set[int] = None, order_by: str = "FinalPricePerDay ASC") -> Tuple[str, dict]:
    clauses = ["Status = 1"]
    params = {}
    
    if brand:
        clauses.append("Brand LIKE :brand")
        params["brand"] = f"%{brand}%"
        
    if category:
        clauses.append("CategoryName LIKE :cat")
        params["cat"] = f"%{category}%"
        
    if exclude_ids:
        # Safe: Set of ints
        id_list = ",".join(str(int(i)) for i in exclude_ids)
        clauses.append(f"Id NOT IN ({id_list})")
        
    where = " AND ".join(clauses)
    query = f"SELECT TOP 50 * FROM Products_LLm WHERE {where} ORDER BY {order_by}"
    return query, params

def _query_candidates(brand: str = None, category: str = None, exclude_ids: Set[int] = None, source: str = "fallback") -> List[dict]:
    query, params = _build_sql(brand, category, exclude_ids)
    with _get_engine().connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(row._mapping) for row in result.fetchall()]
        for r in rows:
            r["_recommendation_source"] = source
        return rows

def _query_trending(exclude_ids: Set[int] = None) -> List[dict]:
    # We use ProductStats to find trending, joining with Products_LLm
    clauses = ["p.Status = 1"]
    if exclude_ids:
        id_list = ",".join(str(int(i)) for i in exclude_ids)
        clauses.append(f"p.Id NOT IN ({id_list})")
        
    where = " AND ".join(clauses)
    query = f"""
        SELECT TOP 50 p.* 
        FROM Products_LLm p
        LEFT JOIN ProductStats s ON p.Id = s.ProductId
        WHERE {where}
        ORDER BY (ISNULL(s.TotalViews, 0) + ISNULL(s.TotalClicks, 0)*2 + ISNULL(s.TotalFavorites, 0)*3 + ISNULL(s.TotalRentRequests, 0)*5) DESC, p.FinalPricePerDay ASC
    """
    with _get_engine().connect() as conn:
        result = conn.execute(text(query))
        rows = [dict(row._mapping) for row in result.fetchall()]
        for r in rows:
            r["_recommendation_source"] = "trending"
        return rows

def _query_newest(exclude_ids: Set[int] = None) -> List[dict]:
    query, params = _build_sql(exclude_ids=exclude_ids, order_by="Id DESC")
    with _get_engine().connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(row._mapping) for row in result.fetchall()]
        for r in rows:
            r["_recommendation_source"] = "newest"
        return rows

def _fetch_candidates(profile: UserProfile, limit: int) -> List[dict]:
    """Candidate Expansion Ladder"""
    candidates = []
    seen_ids = set()
    
    # Attempt 1: Brand AND Category
    if profile.favorite_brand and profile.favorite_category:
        rows = _query_candidates(brand=profile.favorite_brand, category=profile.favorite_category, source="brand_and_category_preference")
        candidates.extend(rows)
        seen_ids.update(r["Id"] for r in rows)
        
    if len(candidates) >= limit * 2:
        return candidates
        
    # Attempt 2: Category only
    if profile.favorite_category:
        rows = _query_candidates(category=profile.favorite_category, exclude_ids=seen_ids, source="category_preference")
        candidates.extend(rows)
        seen_ids.update(r["Id"] for r in rows)
        
    if len(candidates) >= limit * 2:
        return candidates
        
    # Attempt 3: Trending
    rows = _query_trending(exclude_ids=seen_ids)
    candidates.extend(rows)
    seen_ids.update(r["Id"] for r in rows)
    
    if len(candidates) >= limit * 2:
        return candidates
        
    # Attempt 4: Newest
    rows = _query_newest(exclude_ids=seen_ids)
    candidates.extend(rows)
    
    return candidates

def _fetch_stats(product_ids: List[int]) -> Dict[int, dict]:
    if not product_ids:
        return {}
    
    id_list = ",".join(str(int(i)) for i in product_ids)
    query = f"SELECT * FROM ProductStats WHERE ProductId IN ({id_list})"
    
    stats = {}
    with _get_engine().connect() as conn:
        result = conn.execute(text(query))
        for row in result.fetchall():
            row_dict = dict(row._mapping)
            stats[row_dict["ProductId"]] = row_dict
    return stats

def _dedup(ranked: List[dict]) -> List[dict]:
    """Keeps highest scoring version of each Id"""
    seen = {}
    for p in ranked:
        pid = p["Id"]
        if pid not in seen or p["_score"] > seen[pid]["_score"]:
            seen[pid] = p
    return sorted(list(seen.values()), key=lambda x: x["_score"], reverse=True)

async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    start_time = time.time()
    
    # 1. Profile load
    profile = await asyncio.to_thread(build_user_profile, request.user_id, request.session_id)
    
    # Cache check
    cache_key = f"{request.user_id or ''}:{request.session_id or ''}:{profile.profile_hash}:{request.limit}:{request.query or ''}"
    if cache_key in _rec_cache:
        ts, cached = _rec_cache[cache_key]
        if time.time() - ts < CACHE_TTL:
            cached.latency_ms = int((time.time() - start_time) * 1000)
            return cached
            
    # Determine type
    rec_type = "cold_start" if profile.interaction_count < 3 else "personalized"
    
    # 2. Candidate retrieval (Parallel not possible with stats until IDs are known)
    candidates = await asyncio.to_thread(_fetch_candidates, profile, request.limit)
    
    # 3. Fetch ProductStats
    product_ids = [p["Id"] for p in candidates]
    stats = await asyncio.to_thread(_fetch_stats, product_ids)
    
    # 4. Rank + annotate
    ranked = rank_personalized(candidates, profile, stats, query=request.query)
    
    # 5. Dedup + Diversity + Top-N
    ranked = _dedup(ranked)[:request.limit]
    
    # 6. Explanation
    explanation = await generate_recommendation_explanation(profile, ranked, rec_type)
    
    # Prepare response
    formatted_products = []
    debug_info = []
    for p in ranked:
        formatted = format_product(p)
        formatted_products.append(formatted)
        
        debug_info.append({
            "id": p["Id"],
            "name": p.get("Name"),
            "score": p["_score"],
            "personalization_score": p.get("_personalization_score"),
            "query_relevance_score": p.get("_query_relevance_score"),
            "match_reasons": p.get("_match_reasons"),
            "source": p.get("_recommendation_source"),
            "breakdown": p.get("_score_breakdown")
        })
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    response = RecommendationResponse(
        recommendation_type=rec_type,
        user_profile=profile,
        products=formatted_products,
        explanation=explanation,
        latency_ms=latency_ms,
        debug=debug_info
    )
    
    # Cache
    _rec_cache[cache_key] = (time.time(), response)
    
    return response
