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

class ChatResponse(BaseModel):
    answer: str
    intent: str
    products: List[Product]
    total_found: int
    latency_ms: int
    cached: bool

class SearchResponse(BaseModel):
    products: List[Product]
    total_found: int
    latency_ms: int
    cached: bool
