from recommendation.models import UserProfile

DIVERSITY_PENALTY = {
    "same_brand": 3, 
    "same_category": 2, 
    "same_price_tier": 1
}

def _popularity_score(product_id: int, stats: dict) -> float:
    s = stats.get(product_id, {})
    raw = (s.get("TotalViews", 0) * 1 + 
           s.get("TotalClicks", 0) * 2 +
           s.get("TotalFavorites", 0) * 3 + 
           s.get("TotalRentRequests", 0) * 5)
    return min(raw / 50.0, 1.0)

def _query_relevance(product: dict, query: str) -> float:
    if not query:
        return 0.0
        
    score = 0.0
    query_lower = query.lower()
    
    # 1. Keyword match in name
    if name := product.get("Name"):
        if query_lower in name.lower():
            score += 40.0
        else:
            # Partial word matches
            words = [w for w in query_lower.split() if len(w) > 2]
            name_lower = name.lower()
            for w in words:
                if w in name_lower:
                    score += 15.0
                    
    # 2. Category match
    if cat := product.get("CategoryName"):
        if query_lower in cat.lower() or cat.lower() in query_lower:
            score += 30.0
            
    # 3. Brand match
    if brand := product.get("Brand"):
        if query_lower in brand.lower() or brand.lower() in query_lower:
            score += 30.0
            
    return min(score, 100.0)

def rank_personalized(candidates: list[dict], profile: UserProfile, stats: dict, query: str = None) -> list[dict]:
    
    # 1. Score each product
    for p in candidates:
        breakdown = {}
        reasons = []
        
        # Keyword match (4 max)
        kw_pts = 0
        name_lower = str(p.get("Name", "")).lower()
        brand_lower = str(p.get("Brand", "")).lower()
        for kw in profile.top_keywords:
            if kw in name_lower or kw in brand_lower:
                kw_pts = 4.0
                reasons.append("keyword_match")
                break
        breakdown["keyword_match"] = kw_pts
        
        # Category match (5 max)
        cat_pts = 0
        if profile.favorite_category and profile.favorite_category.lower() == str(p.get("CategoryName", "")).lower():
            cat_pts = 5.0
            reasons.append("category_match")
        breakdown["category_match"] = cat_pts
        
        # Brand match (5 max)
        brand_pts = 0
        if profile.favorite_brand and profile.favorite_brand.lower() == str(p.get("Brand", "")).lower():
            brand_pts = 5.0
            reasons.append("brand_match")
        breakdown["brand_match"] = brand_pts
        
        # Location match (3 max)
        loc_pts = 0
        if profile.preferred_location and profile.preferred_location.lower() == str(p.get("LocationArea", "")).lower():
            loc_pts = 3.0
            reasons.append("location_match")
        breakdown["location_match"] = loc_pts
        
        # Price similarity (soft budget, 3 max)
        price_pts = 0
        price = p.get("FinalPricePerDay", p.get("PricePerDay", 0))
        if profile.average_budget and price:
            try:
                price = float(price)
                # Soft score: max(0, 1 - abs(price-budget)/budget) * 3
                diff_ratio = abs(price - profile.average_budget) / profile.average_budget
                price_pts = max(0.0, 1.0 - diff_ratio) * 3.0
                if price_pts > 1.5:
                    reasons.append("budget_match")
            except (ValueError, TypeError):
                pass
        breakdown["price_match"] = price_pts
        
        # Popularity (2 max)
        pop_pts = _popularity_score(p.get("Id"), stats) * 2.0
        breakdown["popularity"] = pop_pts
        
        # Rating (2 max) - Assuming no Rating column for now, returning 0
        rating_pts = 0.0
        breakdown["rating"] = rating_pts
        
        # Calculate Personalization Score (0-100)
        raw_pers = kw_pts + cat_pts + brand_pts + loc_pts + price_pts + pop_pts + rating_pts
        pers_score = (raw_pers / 24.0) * 100.0
        
        # Calculate Query Relevance Score (0-100)
        query_score = _query_relevance(p, query)
        if query_score > 30:
            reasons.append("query_relevance")
            
        # Hybrid weights based on confidence
        pers_w = 0.7 * profile.profile_confidence + 0.3 * (1.0 - profile.profile_confidence)
        query_w = 1.0 - pers_w
        
        # Overwrite if query exists
        if query:
            final_score = (pers_score * pers_w) + (query_score * query_w)
        else:
            final_score = pers_score
            
        p["_score"] = final_score
        p["_personalization_score"] = pers_score
        p["_query_relevance_score"] = query_score
        p["_match_reasons"] = list(set(reasons))
        p["_score_breakdown"] = breakdown
        
        if "_recommendation_source" not in p:
            # Set default source if not provided by retrieval ladder
            p["_recommendation_source"] = "personalized" if pers_score > 30 else "fallback"

    # 2. Diversity Penalty Pass (Greedy)
    selected = []
    seen = {"brands": set(), "categories": set(), "price_tiers": set()}
    
    # Sort initially by score to process highest first
    candidates.sort(key=lambda x: x["_score"], reverse=True)
    
    for p in candidates:
        penalty = 0
        brand = p.get("Brand")
        cat = p.get("CategoryName")
        price = p.get("FinalPricePerDay", p.get("PricePerDay", 0))
        
        try:
            tier = round(float(price) / 50.0) * 50
        except (ValueError, TypeError):
            tier = 0
            
        if brand and brand in seen["brands"]:
            penalty += DIVERSITY_PENALTY["same_brand"]
        if cat and cat in seen["categories"]:
            penalty += DIVERSITY_PENALTY["same_category"]
        if tier in seen["price_tiers"]:
            penalty += DIVERSITY_PENALTY["same_price_tier"]
            
        p["_score"] = max(0, p["_score"] - penalty)
        
        if brand: seen["brands"].add(brand)
        if cat: seen["categories"].add(cat)
        seen["price_tiers"].add(tier)
        
        selected.append(p)
        
    # Final sort
    selected.sort(key=lambda x: x["_score"], reverse=True)
    return selected
