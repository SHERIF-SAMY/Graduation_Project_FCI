def build_sql(entities: dict) -> tuple[str, dict]:
    """
    Generates a parameterized SQL query and its parameters for safety.
    Maps extracted entities to SQL WHERE clauses on the Products_LLm view.

    Key rules:
    - name_keyword searches across Name, CategoryName, AND ProductType using OR,
      so "laptop" finds results even if the DB category is "Computers" not "Electronics".
    - When name_keyword is present, the category filter is skipped to avoid
      the LLM's category guess blocking valid results.
    """
    query = "SELECT TOP 20 * FROM Products_LLm WHERE Status = 1"
    params = {}

    name_keyword = entities.get("name_keyword")

    # Only apply category filter when there is NO name_keyword,
    # because the LLM often guesses the wrong category for product-name queries.
    if entities.get("category") and not name_keyword:
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
        if cond_lower in ("new", "جديد", "جديدة"):
            query += " AND Condition = 1"
        elif cond_lower in ("used", "مستعمل", "مستخدم", "مستعملة"):
            query += " AND Condition = 2"

    if name_keyword:
        # Normalize to singular: strip trailing 's' so "laptops" → "laptop",
        # "cameras" → "camera", matching "Dell Laptop" / "Canon DSLR Camera" in the DB.
        kw = name_keyword.strip().lower()
        if kw.endswith("s") and len(kw) > 3:
            kw = kw[:-1]   # "laptops" → "laptop", "cameras" → "camera"

        # Blacklist of generic words that shouldn't be used as a name filter
        generic_words = {"product", "thing", "item", "anything", "منتج", "منتجات", "حاجة", "اشياء", "أشياء", "اي حاجة", "أي حاجة"}
        
        if kw not in generic_words:
            # Search across Name, CategoryName, and ProductType using OR
            query += (
                " AND ("
                "Name LIKE :kw"
                " OR CategoryName LIKE :kw"
                " OR ProductType  LIKE :kw"
                ")"
            )
            params["kw"] = f"%{kw}%"

    query += " ORDER BY FinalPricePerDay ASC"
    return query, params
