"""
/api/v1/images — Standalone image search
"""
from fastapi import APIRouter
from api.schemas.request import ImagesRequest
from services.images.serpapi_client import search_images

router = APIRouter(tags=["Images"])


@router.post("/images")
async def images(req: ImagesRequest):
    results = search_images(req.query, num=req.num, confidence=1.0)
    return {"query": req.query, "count": len(results), "images": results}
