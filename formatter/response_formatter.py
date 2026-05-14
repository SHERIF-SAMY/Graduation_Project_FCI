from models.response_models import Product, ChatResponse, SearchResponse

def format_product(db_row: dict) -> Product:
    # Ensure PricePerDay can be parsed as float, default to 0.0
    try:
        price = float(db_row.get('PricePerDay', 0.0))
    except (TypeError, ValueError):
        price = 0.0

    # Robustly parse Condition — DB may return int 1/2 or string "New"/"Used"/"1"/"2"
    raw_condition = db_row.get('Condition')
    if raw_condition in (1, "1", "New", "new"):
        condition_label = "New"
    else:
        condition_label = "Used"

    return Product(
        id=db_row.get('Id', 0),
        name=db_row.get('Name', 'Unknown'),
        category=db_row.get('CategoryName', 'Unknown'),
        brand=db_row.get('Brand'),
        condition=condition_label,
        price_per_day=price,
        location=db_row.get('LocationArea', 'Unknown'),
        rental_guarantee=bool(db_row.get('RentalGuarantee', False)),
        status="Available" if db_row.get('Status') in (1, "1") else "Unavailable",
        image_url=db_row.get('ImageUrl')
    )

def format_chat_response(answer: str, intent: str, products_raw: list, latency_ms: int, cached: bool, booking_action: dict = None) -> dict:
    products = [format_product(p) for p in products_raw]
    response_data = {
        "answer": answer,
        "intent": intent,
        "products": [p.model_dump() for p in products],
        "total_found": len(products_raw),
        "latency_ms": latency_ms,
        "cached": cached
    }
    if booking_action:
        response_data["booking_action"] = booking_action
    
    return response_data

def format_search_response(products_raw: list, latency_ms: int, cached: bool) -> dict:
    products = [format_product(p) for p in products_raw]
    response = SearchResponse(
        products=products,
        total_found=len(products_raw),
        latency_ms=latency_ms,
        cached=cached
    )
    return response.model_dump()
