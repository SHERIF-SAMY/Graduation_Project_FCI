def build_sql(entities: dict) -> tuple[str, dict]:
    """
    Generates a parameterized SQL query and its parameters for safety.
    Maps extracted entities to SQL WHERE clauses on the Products_LLm view.
    Supports both English and Arabic entity values.
    """
    query = "SELECT TOP 20 * FROM Products_LLm WHERE Status = 1"
    params = {}
    
    if entities.get("category"):
        query += " AND CategoryName LIKE :category"
        params["category"] = f"%{entities['category']}%"
        
    if entities.get("brand"):
        query += " AND Brand LIKE :brand"
        params["brand"] = f"%{entities['brand']}%"
        
    if entities.get("location"):
        query += " AND LocationArea LIKE :location"
        params["location"] = f"%{entities['location']}%"
        
    # Safe float parsing for max_price
    try:
        if entities.get("max_price") is not None:
            params["max_price"] = float(entities["max_price"])
            query += " AND FinalPricePerDay <= :max_price"
    except (ValueError, TypeError):
        pass
        
    cond = entities.get("condition")
    if cond:
        cond_lower = str(cond).lower().strip()
        # Support English and Arabic condition values
        if cond_lower in ("new", "جديد", "جديدة"):
            query += " AND Condition = 1"
        elif cond_lower in ("used", "مستعمل", "مستخدم", "مستعملة"):
            query += " AND Condition = 2"
             
    if entities.get("name_keyword"):
        query += " AND Name LIKE :name_keyword"
        params["name_keyword"] = f"%{entities['name_keyword']}%"
        
    query += " ORDER BY FinalPricePerDay ASC"
    return query, params
