from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    id: int
    name: str
    category: str
    brand: Optional[str] = None
    condition: str
    price_per_day: float
    location: str
    rental_guarantee: bool
    status: str
    image_url: Optional[str] = None

class BookingAction(BaseModel):
    state: str
    order_id: Optional[int] = None
    requires_input: Optional[str] = None  # "dates" | "delivery" | "address" | "confirmation"
    summary: Optional[dict] = None

class ChatResponse(BaseModel):
    answer: str
    intent: str
    products: List[Product]
    total_found: int
    latency_ms: int
    cached: bool
    booking_action: Optional[BookingAction] = None

class SearchResponse(BaseModel):
    products: List[Product]
    total_found: int
    latency_ms: int
    cached: bool
