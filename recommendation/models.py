from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime
from sql.db import Base

# SQLAlchemy ORM Models
class UserInteraction(Base):
    __tablename__ = "UserInteractions"
    
    Id                = Column(Integer, primary_key=True, autoincrement=True)
    UserId            = Column(String(100), nullable=True)
    SessionId         = Column(String(100), nullable=True)
    ProductId         = Column(Integer, nullable=True)
    ActionType        = Column(String(50), nullable=False)
    SearchQuery       = Column(String(500), nullable=True)
    Category          = Column(String(100), nullable=True)
    Brand             = Column(String(100), nullable=True)
    LocationArea      = Column(String(100), nullable=True)
    PriceRange        = Column(Float, nullable=True)
    PreferredLanguage = Column(String(10), nullable=True)
    CreatedAt         = Column(DateTime, default=datetime.utcnow)

class ProductStat(Base):
    __tablename__ = "ProductStats"
    
    ProductId         = Column(Integer, primary_key=True)
    TotalViews        = Column(Integer, default=0)
    TotalClicks       = Column(Integer, default=0)
    TotalFavorites    = Column(Integer, default=0)
    TotalRentRequests = Column(Integer, default=0)
    LastUpdated       = Column(DateTime, default=datetime.utcnow)


# Pydantic Schemas
class UserProfile(BaseModel):
    favorite_brand:     Optional[str]   = None
    favorite_category:  Optional[str]   = None
    preferred_location: Optional[str]   = None
    average_budget:     Optional[float] = None
    top_keywords:       List[str]       = []
    preferred_language: str             = "ar"
    interaction_count:  int             = 0
    profile_confidence: float           = 0.0   # 0.0–1.0
    profile_hash:       str             = ""    # for cache key

class RecommendationRequest(BaseModel):
    user_id:    Optional[str] = None
    session_id: Optional[str] = None
    query:      Optional[str] = None
    limit:      int = Field(default=5, ge=1, le=20)

from models.response_models import Product

class RecommendationResponse(BaseModel):
    recommendation_type: str
    user_profile:        UserProfile
    products:            List[Product]
    explanation:         str
    latency_ms:          int
    debug:               Optional[List[dict]] = None
