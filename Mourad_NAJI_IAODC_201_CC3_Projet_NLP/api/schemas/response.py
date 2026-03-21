"""
Pydantic v2 Response Schemas
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class ImageResult(BaseModel):
    title: str
    thumbnail: str
    link: str
    source: str = ""


class OutfitItem(BaseModel):
    top: str = ""
    bottom: str = ""
    shoes: str = ""
    accessories: str = ""


class OutfitRecommendation(BaseModel):
    outfit_id: str
    title: str
    style: str
    season: list[str]
    occasion: list[str]
    gender: str
    color_palette: list[str]
    estimated_price: int
    items: dict
    tags: list[str]
    semantic_score: float
    metadata_match: float
    final_score: float
    explanation: str
    images: list[ImageResult] = []


class PreferenceSummary(BaseModel):
    gender: Optional[str]
    occasion: Optional[str]
    season: Optional[str]
    style: Optional[str]
    color: Optional[str]
    budget: Optional[int]
    confidence: float
    confidence_map: dict


class RecommendResponse(BaseModel):
    session_id: str
    understood: PreferenceSummary
    query_rewritten: str
    confidence: float
    recommendations: list[OutfitRecommendation]
    fallback_message: Optional[str] = None
    did_you_mean: Optional[str] = None
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    version: str
    index_status: str
    index_total: int
    cache_stats: dict


class FeedbackResponse(BaseModel):
    status: str
    session_id: str
    message: str
