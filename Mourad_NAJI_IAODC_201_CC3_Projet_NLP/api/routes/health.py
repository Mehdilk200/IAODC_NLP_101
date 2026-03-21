"""
/api/v1/health — System health check
"""
from fastapi import APIRouter
from api.schemas.response import HealthResponse
from services.rag.indexer import OutfitIndex
from services.cache.cache_manager import nlp_cache, rag_cache, image_cache

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    index = OutfitIndex.get_instance()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        index_status="ready" if index._built else "not_built",
        index_total=index.total,
        cache_stats={
            "nlp":    nlp_cache.stats(),
            "rag":    rag_cache.stats(),
            "images": image_cache.stats(),
        },
    )
