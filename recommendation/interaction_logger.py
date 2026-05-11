import asyncio
from typing import Optional
from sql.db import SessionLocal
from recommendation.models import UserInteraction
from recommendation.stats_updater import merge_stat

async def log_interaction(
    action_type: str,
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    product_id: Optional[int] = None,
    search_query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    location_area: Optional[str] = None,
    price_range: Optional[float] = None,
    preferred_language: Optional[str] = None,
) -> None:
    """Fire-and-forget. Never raises. Calls asyncio.to_thread(_sync_log)."""
    
    # Don't log empty searches if they lack useful context
    if action_type == "search" and not any([search_query, category, brand, location_area, price_range]):
        return
        
    await asyncio.to_thread(
        _sync_log, 
        action_type, user_id, session_id, product_id, search_query, 
        category, brand, location_area, price_range, preferred_language
    )

def _sync_log(
    action_type: str,
    user_id: Optional[str],
    session_id: Optional[str],
    product_id: Optional[int],
    search_query: Optional[str],
    category: Optional[str],
    brand: Optional[str],
    location_area: Optional[str],
    price_range: Optional[float],
    preferred_language: Optional[str],
) -> None:
    if SessionLocal is None:
        return
        
    try:
        with SessionLocal() as session:
            interaction = UserInteraction(
                UserId=user_id,
                SessionId=session_id,
                ProductId=product_id,
                ActionType=action_type,
                SearchQuery=search_query,
                Category=category,
                Brand=brand,
                LocationArea=location_area,
                PriceRange=price_range,
                PreferredLanguage=preferred_language
            )
            session.add(interaction)
            
            if product_id:
                merge_stat(session, product_id, action_type)
                
            session.commit()
    except Exception as e:
        print(f"[InteractionLogger] Failed to log interaction: {e}")
