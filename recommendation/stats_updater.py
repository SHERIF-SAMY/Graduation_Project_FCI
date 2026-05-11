from sqlalchemy import text

STAT_COLUMN_MAP = {
    "view_product":   "TotalViews",
    "click_product":  "TotalClicks",
    "favorite":       "TotalFavorites",
    "rent_request":   "TotalRentRequests",
}

def merge_stat(session, product_id: int, action_type: str) -> None:
    """Atomically updates ProductStats using MERGE."""
    col = STAT_COLUMN_MAP.get(action_type)
    if not col or not product_id:
        return
        
    query = f"""
        MERGE ProductStats AS target
        USING (VALUES (:pid)) AS src(ProductId) ON target.ProductId = src.ProductId
        WHEN MATCHED THEN UPDATE SET {col} = {col} + 1, LastUpdated = GETDATE()
        WHEN NOT MATCHED THEN INSERT (ProductId, {col}) VALUES (:pid, 1);
    """
    session.execute(text(query), {"pid": product_id})
