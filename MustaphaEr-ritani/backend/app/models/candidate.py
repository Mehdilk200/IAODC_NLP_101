"""
Pydantic models for Candidate data.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None
    language: Optional[str] = "en"


class CandidateCreate(CandidateBase):
    cv_text: str
    skills: List[str] = []
    embedding: Optional[List[float]] = None


class CandidateResponse(CandidateBase):
    id: str
    cv_text: str
    skills: List[str] = []
    score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class CandidateInDB(CandidateCreate):
    id: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
