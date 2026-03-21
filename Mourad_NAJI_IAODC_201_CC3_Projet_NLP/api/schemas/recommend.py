from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RecommendRequest(BaseModel):
    query: str = Field(..., description="User text preferences")
    top_k: int = Field(default=5, ge=1, le=20)

class Preferences(BaseModel):
    style: Optional[str] = None
    colors: List[str] = []
    occasion: Optional[str] = None
    budget: Optional[float] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    materials: List[str] = []
    must_have: List[str] = []
    avoid: List[str] = []

class OutfitResult(BaseModel):
    id: str
    title: str
    description: str
    tags: List[str]
    price: float
    image_url: str
    score: float
    explanation: str

class RecommendResponse(BaseModel):
    query: str
    preferences: Preferences
    confidence: float
    results: List[OutfitResult]
    fallback_message: Optional[str] = None
