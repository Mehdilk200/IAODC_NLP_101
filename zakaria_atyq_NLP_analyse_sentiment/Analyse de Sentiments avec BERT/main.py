from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uvicorn
import os
import time
import random
from dotenv import load_dotenv
from model import sentiment_model
from schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
from src.controller.config import HOST, PORT, CORS_ORIGINS, LOG_LEVEL

load_dotenv()
app = FastAPI(title="MegaShop API - BERT Sentiment Analysis", version="1.0.0")
start_time = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewBase(BaseModel):
    product_id: int
    author: str
    text: str
    sentiment: Optional[str] = None
    confidence: Optional[float] = None

class Review(ReviewBase):
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    image: str
    description: Optional[str] = None

mock_products = [
    {"id": 1, "name": "iPhone 15 Pro", "category": "Smartphones", "price": 1299, 
     "image": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500",
     "description": "Le dernier iPhone avec processeur A17 Pro"},
    {"id": 2, "name": "Samsung S24 Ultra", "category": "Smartphones", "price": 1199,
     "image": "https://images.unsplash.com/photo-1705739040822-487a9856bebd?w=500",
     "description": "Smartphone avec zoom x100"},
    {"id": 3, "name": "MacBook Pro M3", "category": "Ordinateurs", "price": 2499,
     "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500",
     "description": "Le plus puissant des MacBook"},
]

@app.on_event("startup")
async def startup_event():
    try:
        sentiment_model.load()
        print(f"✅ Modèle BERT chargé sur {sentiment_model.device}")
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")

async def analyze_sentiment_with_bert(text: str):
    try:
        result = sentiment_model.predict(text)
        sentiment = "pos" if result["sentiment"] == "positif" else "neg"
        return {"sentiment": sentiment, "confidence": result["confidence"], "inference_ms": result["inference_ms"]}
    except:
        return simulate_sentiment(text)

def simulate_sentiment(text: str):
    words = text.lower().split()
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor']
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    if pos_count > neg_count:
        return {"sentiment": "pos", "confidence": 0.85, "inference_ms": 50}
    elif neg_count > pos_count:
        return {"sentiment": "neg", "confidence": 0.85, "inference_ms": 50}
    else:
        return {"sentiment": "pos" if random.random() > 0.5 else "neg", "confidence": 0.65, "inference_ms": 50}

@app.get("/")
async def root():
    return {"app": "MegaShop API", "status": "online", "model": "BERT-base"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", device=str(sentiment_model.device), model="BERT-base", uptime_s=round(time.time() - start_time, 2))

@app.get("/model/info", response_model=ModelInfoResponse)
async def model_info():
    return ModelInfoResponse(
        model_source=sentiment_model.source,
        device=str(sentiment_model.device),
        max_len=128,
        total_predictions=sentiment_model.total_predictions,
        load_time_s=sentiment_model.load_time,
        parameters=sentiment_model.n_params
    )

@app.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, search: Optional[str] = None, limit: int = Query(50), skip: int = Query(0)):
    filtered = mock_products
    if category:
        filtered = [p for p in mock_products if p["category"] == category]
    if search:
        filtered = [p for p in filtered if search.lower() in p["name"].lower()]
    return filtered[skip:skip+limit]

@app.post("/reviews")
async def create_review(review: ReviewBase):
    review_dict = review.dict()
    review_dict["created_at"] = datetime.now()
    product = next((p for p in mock_products if p["id"] == review.product_id), None)
    if not product:
        raise HTTPException(404, f"Produit avec ID {review.product_id} non trouvé")
    sentiment_result = await analyze_sentiment_with_bert(review_dict["text"])
    review_dict["sentiment"] = sentiment_result["sentiment"]
    review_dict["confidence"] = sentiment_result["confidence"]
    review_dict["analyzed_at"] = datetime.now()
    review_dict["_id"] = "mock_id"
    return review_dict

@app.post("/predict", response_model=PredictResponse)
async def predict_sentiment(request: PredictRequest):
    result = await analyze_sentiment_with_bert(request.text)
    sentiment = "positif" if result["sentiment"] == "pos" else "negatif"
    return PredictResponse(
        text=request.text,
        sentiment=sentiment,
        label=1 if result["sentiment"] == "pos" else 0,
        confidence=result["confidence"],
        proba_pos=result["confidence"] if result["sentiment"] == "pos" else 1 - result["confidence"],
        proba_neg=1 - result["confidence"] if result["sentiment"] == "pos" else result["confidence"],
        inference_ms=result["inference_ms"]
    )

@app.get("/stats")
async def get_stats():
    return {
        "total_products": len(mock_products),
        "total_predictions": sentiment_model.total_predictions,
        "model": {"name": "BERT-base", "device": str(sentiment_model.device)}
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)