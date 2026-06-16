def rank_products(products: list, entities: dict) -> list:
    """
    Ranks products based on match with extracted entities, price, and condition.
    Returns top 5 products.
    """
    ranked = []
    for product in products:
        score = 0.0
        
        # Priority 1: Entity match
        name = str(product.get('Name', '')).lower()
        keyword = (entities.get('name_keyword') or '').lower() if entities else ''
        if keyword and keyword in name:
            score += 4.0
            
        category = (entities.get('category') or '').lower() if entities else ''
        prod_category = str(product.get('CategoryName', '')).lower()
        if category and category in prod_category:
            score += 3.0
            
        brand = (entities.get('brand') or '').lower() if entities else ''
        prod_brand = str(product.get('Brand', '')).lower()
        if brand and brand in prod_brand:
            score += 3.0
            
        # Priority 2: Price fit
        max_price = entities.get('max_price') if entities else None
        val = product.get('FinalPricePerDay')
        if val is None:
            val = product.get('PricePerDay')
        price = float(val) if val is not None else float('inf')
        # If max_price is specified and price is within budget
        if max_price is not None and price <= max_price:
            score += 2.0
            
        # Priority 3: Condition match
        condition = product.get('Condition')
        # Normalize condition: DB stores int (1=New, 2=Used), convert to string label for comparison
        if condition == 1 or str(condition).strip() in ("1", "New", "new"):
            condition_label = "new"
        else:
            condition_label = "used"
            
        expected_condition = (entities.get('condition') or '').lower() if entities else ''
        if expected_condition and expected_condition == condition_label:
            score += 2.0
        elif condition_label == "new" and not expected_condition:
            score += 0.5  # Slightly prefer New items when condition not specified
            
        ranked.append((score, product))
    
    # Sort by score descending
    ranked.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 5 products
    return [r[1] for r in ranked[:5]]
