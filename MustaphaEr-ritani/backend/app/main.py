"""
AI Resume Screening System - FastAPI Backend
Main application entry point
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import nltk

logger = logging.getLogger(__name__)

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routes import upload, job, match
from app.core.config import settings


# ─────────────────────────────────────────────
# Lifespan: startup & shutdown events
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: connect DB, download NLTK data."""
    # Startup
    await connect_to_mongo()
    # Download NLTK stopwords if not already present
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)

    logger.info("Application started successfully")
    yield

    # Shutdown
    await close_mongo_connection()
    logger.info("Application shut down")


# ─────────────────────────────────────────────
# FastAPI App Instance
# ─────────────────────────────────────────────
app = FastAPI(
    title="AI Resume Screening System",
    description="NLP-powered CV matching and candidate ranking API",
    version="1.0.0",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Static files (for uploaded CVs)
# ─────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["CV Upload"])
app.include_router(job.router, prefix="/api/jobs", tags=["Job Descriptions"])
app.include_router(match.router, prefix="/api/match", tags=["Matching & Ranking"])


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "app": "AI Resume Screening System",
        "version": "1.0.0",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Backend is running"}
