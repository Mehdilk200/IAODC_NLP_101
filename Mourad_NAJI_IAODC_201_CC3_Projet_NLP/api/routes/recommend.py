from fastapi import APIRouter, HTTPException
from api.schemas.recommend import RecommendRequest, RecommendResponse
from services.nlp.extract import nlp_service
from services.rag.faiss_store import FashionStore
from services.rag.embedder import get_embedder
from services.ranking.rerank import ranking_service
from services.cache.memory_cache import recommend_cache
from services.images.image_search import image_search_service

router = APIRouter(tags=["Recommendation"])

@router.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    """
    SaaS Recommendation Pipeline: 
    Cache -> NLP (Confidence Check) -> Hybrid Retrieval -> Cross-Encoder Reranking -> Explanation 
    """
    # 1. Edge Caching
    cached = recommend_cache.get(req.query)
    if cached:
        return cached

    # 2. Advanced NLP & Reasoning
    prefs, confidence = nlp_service.extract_preferences(req.query)
    
    fallback_message = None
    if confidence < 0.4:
        fallback_message = "I'm not quite sure I caught all your preferences. I've provided some broad matches below, but feel free to specify a style or occasion (e.g., 'casual' or 'wedding') for better results!"

    # 3. Hybrid Semantic Search
    store = FashionStore.get_instance()
    embedder = get_embedder()
    query_vec = embedder.embed_text(req.query)
    # Increase k for reranking pool (Precision over Recall)
    candidates = store.search(query_vec, top_k=min(req.top_k * 4, 40))
    
    # 4. Probabilistic Reranking (Cross-Encoder + Heuristics)
    results = ranking_service.rerank_and_score(req.query, candidates, prefs)
    
    # 5. Final Filtering
    top_results = results[:req.top_k]

    # 5. Enrich with images (Async Pexels search)
    for item in top_results:
        # Convert Pydantic to dict for the service, then update the attribute
        item.image_url = await image_search_service.get_image_url(item.model_dump(), req.query)

    response = RecommendResponse(
        query=req.query,
        preferences=prefs,
        confidence=confidence,
        results=top_results,
        fallback_message=fallback_message
    )
    
    # 6. Persistent Cache Hydration
    recommend_cache.set(req.query, response)
    
    return response
