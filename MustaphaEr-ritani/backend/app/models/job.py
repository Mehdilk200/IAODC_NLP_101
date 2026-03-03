"""
Pydantic models for Job Description data.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class JobBase(BaseModel):
    title: str
    description: str
    required_skills: Optional[List[str]] = []
    company: Optional[str] = None
    location: Optional[str] = None


class JobCreate(JobBase):
    embedding: Optional[List[float]] = None


class JobResponse(JobBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobInDB(JobCreate):
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MatchRequest(BaseModel):
    candidate_id: str
    job_id: str


class BulkMatchRequest(BaseModel):
    job_id: str
    candidate_ids: Optional[List[str]] = None  # None = match all candidates


class MatchResult(BaseModel):
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    language: Optional[str] = "en"
