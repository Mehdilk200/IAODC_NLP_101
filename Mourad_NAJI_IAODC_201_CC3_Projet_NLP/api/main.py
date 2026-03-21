import logging
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import recommend

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="StyleAI API",
    description="Production-grade AI Fashion Stylist using RAG + FAISS",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup_event():
    from services.rag.faiss_store import FashionStore
    store = FashionStore.get_instance()
    store.build_or_load()
    logger.info("Fashion Store initialized and index ready.")

# Routes
app.include_router(recommend.router)

# Health
@app.get("/health")
async def health():
    return {"status": "ok"}

# Static Files (Local Images)
IMAGES_DIR = Path(__file__).parent.parent / "data" / "images"
if not IMAGES_DIR.exists():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# Frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    logger.warning(f"Frontend directory not found at {FRONTEND_DIR}")
