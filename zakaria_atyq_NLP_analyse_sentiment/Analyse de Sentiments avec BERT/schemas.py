from pydantic import BaseModel, Field
from typing import List, Optional

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class PredictResponse(BaseModel):
    text: str
    sentiment: str
    label: int
    confidence: float
    proba_pos: float
    proba_neg: float
    inference_ms: float

class HealthResponse(BaseModel):
    status: str
    device: str
    model: str
    uptime_s: float

class ModelInfoResponse(BaseModel):
    model_source: str
    device: str
    max_len: int
    total_predictions: int
    load_time_s: float
    parameters: int