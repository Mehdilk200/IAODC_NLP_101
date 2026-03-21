"""
Pydantic v2 Request Schemas
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class RecommendRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=1000,
                         description="User's free-form style request")
    session_id: Optional[str] = Field(None, description="Session ID for personalization")
    num_results: int = Field(default=5, ge=1, le=10,
                             description="Number of outfit recommendations")
    include_images: bool = Field(default=True, description="Fetch outfit images via SerpAPI")


class ImagesRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    num: int = Field(default=4, ge=1, le=12)


class FeedbackRequest(BaseModel):
    session_id: str
    outfit_id: str
    rating: int = Field(ge=1, le=5)
    liked: bool
