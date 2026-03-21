"""
Hybrid Retriever
Combines semantic FAISS search with metadata filtering and cross-encoder reranking.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass

import numpy as np

from services.nlp.preference_extractor import PreferenceResult
from services.rag.embedder import get_embedder
from services.rag.indexer import OutfitIndex

logger = logging.getLogger(__name__)

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_reranker = None

TOP_K_SEMANTIC   = 20   # how many to fetch from FAISS
TOP_K_AFTER_FILTER = 10  # after metadata filtering
TOP_K_FINAL       = 5   # after reranking


@dataclass
class RetrievedOutfit:
    outfit: dict
    semantic_score: float
    reranker_score: float = 0.0
    metadata_match: float = 0.0


def _get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(RERANKER_MODEL)
            logger.info(f"Cross-encoder loaded: {RERANKER_MODEL}")
        except Exception as e:
            logger.warning(f"Cross-encoder unavailable ({e}). Skipping reranking.")
            _reranker = False  # sentinel — don't retry
    return _reranker if _reranker is not False else None


def _metadata_score(outfit: dict, prefs: PreferenceResult) -> float:
    """
    Compute how many preference slots are satisfied by the outfit's metadata.
    Returns 0.0–1.0 (ratio of matched slots).
    """
    checks: list[bool] = []

    if prefs.gender:
        checks.append(outfit.get("gender") == prefs.gender or outfit.get("gender") == "unisex")

    if prefs.season:
        outfit_seasons = [s.lower() for s in outfit.get("season", [])]
        checks.append(prefs.season in outfit_seasons or "any" in outfit_seasons)

    if prefs.occasion:
        outfit_occasions = [o.lower() for o in outfit.get("occasion", [])]
        checks.append(prefs.occasion in outfit_occasions)

    if prefs.style:
        checks.append(outfit.get("style", "").lower() == prefs.style.lower())

    if prefs.color:
        palette = " ".join(outfit.get("color_palette", [])).lower()
        checks.append(prefs.color.lower() in palette)

    if prefs.budget:
        price = outfit.get("estimated_price", 0)
        checks.append(price <= prefs.budget * 1.15)  # 15% tolerance

    if not checks:
        return 0.5  # neutral when no prefs to check against
    return sum(checks) / len(checks)


def _passes_hard_filter(outfit: dict, prefs: PreferenceResult) -> bool:
    """Hard filter: only exclude outfits that fail on BOTH gender AND budget."""
    # Gender hard filter
    if prefs.gender:
        og = outfit.get("gender", "")
        if og and og != prefs.gender and og != "unisex":
            return False

    # Budget hard filter (strict: don't show if 2x over budget)
    if prefs.budget and prefs.budget > 0:
        price = outfit.get("estimated_price", 0)
        if price > prefs.budget * 2.0:
            return False

    return True


def retrieve(
    query: str,
    prefs: PreferenceResult,
    top_k: int = TOP_K_FINAL,
) -> list[RetrievedOutfit]:
    """
    Full retrieval pipeline:
    1. Embed query
    2. FAISS top-K semantic search
    3. Metadata hard filter
    4. Compute metadata match score
    5. Cross-encoder reranking
    6. Return top_k results
    """
    embedder = get_embedder()
    index    = OutfitIndex.get_instance()

    if not index._built:
        index.build_or_load()

    # Step 1-2: Semantic search
    query_vec = embedder.embed_text(query)
    raw_results = index.search(query_vec, top_k=TOP_K_SEMANTIC)
    logger.debug(f"Semantic search returned {len(raw_results)} candidates")

    # Step 3-4: Filter + metadata scoring
    candidates: list[RetrievedOutfit] = []
    for outfit, sem_score in raw_results:
        if not _passes_hard_filter(outfit, prefs):
            continue
        meta_score = _metadata_score(outfit, prefs)
        candidates.append(RetrievedOutfit(
            outfit=outfit,
            semantic_score=sem_score,
            metadata_match=meta_score,
        ))

    # Fallback: if filtering removed everything, use all semantic results
    if not candidates:
        logger.warning("Hard filter removed all candidates — using unfiltered results")
        candidates = [
            RetrievedOutfit(outfit=o, semantic_score=s, metadata_match=0.5)
            for o, s in raw_results
        ]

    # Sort by semantic score before reranking
    candidates.sort(key=lambda x: x.semantic_score, reverse=True)
    candidates = candidates[:TOP_K_AFTER_FILTER]

    # Step 5: Cross-encoder reranking
    reranker = _get_reranker()
    if reranker and candidates:
        try:
            pairs = [(query, _outfit_to_reranker_text(c.outfit)) for c in candidates]
            scores = reranker.predict(pairs)
            # Normalize reranker scores to 0-1
            min_s, max_s = min(scores), max(scores)
            span = max_s - min_s if max_s != min_s else 1.0
            for c, raw_score in zip(candidates, scores):
                c.reranker_score = (raw_score - min_s) / span
        except Exception as e:
            logger.warning(f"Reranking failed: {e}")

    return candidates[:top_k]


def _outfit_to_reranker_text(outfit: dict) -> str:
    return (
        f"{outfit.get('description', '')} "
        f"Style: {outfit.get('style', '')}. "
        f"Occasion: {', '.join(outfit.get('occasion', []))}. "
        f"Season: {', '.join(outfit.get('season', []))}."
    )
