import math
import hashlib
from typing import Optional
from collections import Counter
from datetime import datetime
from sqlalchemy import text
from sql.db import get_engine
from recommendation.models import UserProfile

ACTION_WEIGHTS = {
    "search": 1, 
    "view_product": 2, 
    "click_product": 3,
    "recommendation_click": 4, 
    "favorite": 5, 
    "rent_request": 10,
}

# Simple arabic stopword list to filter out from keywords
ARABIC_STOPWORDS = {"في", "من", "على", "الى", "إلى", "عن", "ب", "ل", "ك", "و", "او", "أو", "مع", "هذا", "هذه", "الذي", "التي", "كل", "بعض", "غير", "ان", "أن", "انه", "أنه", "لها", "له", "هم", "هن", "هو", "هي"}
ENGLISH_STOPWORDS = {"in", "on", "at", "to", "for", "with", "a", "an", "the", "and", "or", "is", "are", "am", "was", "were", "of", "it", "this", "that", "these", "those"}

def _weight(action_type: str, created_at: datetime, now: datetime) -> float:
    """Calculates weight combining action importance and time decay."""
    action_w = ACTION_WEIGHTS.get(action_type, 1)
    
    # Calculate days old (minimum 0 to avoid negative values if clocks are slightly off)
    days_old = max(0.0, (now - created_at).total_seconds() / (24 * 3600))
    
    # Exponential decay over 30 days
    time_decay = math.exp(-days_old / 30.0)
    
    return action_w * time_decay

def _extract_keywords(query: str, weight: float, counter: Counter):
    if not query:
        return
    words = [w.strip().lower() for w in query.split() if w.strip()]
    for word in words:
        if word not in ARABIC_STOPWORDS and word not in ENGLISH_STOPWORDS and len(word) > 1:
            counter[word] += weight

def build_user_profile(user_id: Optional[str] = None, session_id: Optional[str] = None) -> UserProfile:
    """Builds a weighted user profile from the last 50 interactions."""
    
    # If no identifiers provided, return empty profile
    if not user_id and not session_id:
        return UserProfile()
        
    engine = get_engine()
    
    query = """
        SELECT TOP 50 * FROM UserInteractions
        WHERE (UserId = :uid OR SessionId = :sid)
        ORDER BY CreatedAt DESC
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query), {"uid": user_id, "sid": session_id})
        rows = [dict(row._mapping) for row in result.fetchall()]
        
    interaction_count = len(rows)
    
    # Cold-start
    if interaction_count < 3:
        # Just grab the language if available
        pref_lang = next((r["PreferredLanguage"] for r in rows if r.get("PreferredLanguage")), "ar")
        return UserProfile(preferred_language=pref_lang, interaction_count=interaction_count)
        
    now = datetime.utcnow()
    
    brands = Counter()
    categories = Counter()
    locations = Counter()
    keywords = Counter()
    
    total_price_weight = 0.0
    weighted_price_sum = 0.0
    
    for row in rows:
        w = _weight(row.get("ActionType", "search"), row.get("CreatedAt", now), now)
        
        if brand := row.get("Brand"):
            brands[brand] += w
        if cat := row.get("Category"):
            categories[cat] += w
        if loc := row.get("LocationArea"):
            locations[loc] += w
            
        if price := row.get("PriceRange"):
            weighted_price_sum += price * w
            total_price_weight += w
            
        if query_text := row.get("SearchQuery"):
            _extract_keywords(query_text, w, keywords)
            
    # Compile the profile
    profile = UserProfile(interaction_count=interaction_count)
    
    if brands:
        profile.favorite_brand = brands.most_common(1)[0][0]
    if categories:
        profile.favorite_category = categories.most_common(1)[0][0]
    if locations:
        profile.preferred_location = locations.most_common(1)[0][0]
        
    if total_price_weight > 0:
        profile.average_budget = weighted_price_sum / total_price_weight
        
    if keywords:
        profile.top_keywords = [word for word, _ in keywords.most_common(5)]
        
    profile.preferred_language = next((r["PreferredLanguage"] for r in rows if r.get("PreferredLanguage")), "ar")
    
    profile.profile_confidence = min(interaction_count / 20.0, 1.0)
    
    # Generate profile hash for caching
    hash_input = f"{profile.favorite_brand}:{profile.favorite_category}:{profile.average_budget}:{'-'.join(profile.top_keywords)}"
    profile.profile_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    
    return profile
