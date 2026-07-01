from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = None
    auth_token: Optional[str] = None

class SearchRequest(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    location: Optional[str] = None
    max_price: Optional[float] = None
    condition: Optional[str] = None
    name_keyword: Optional[str] = None
