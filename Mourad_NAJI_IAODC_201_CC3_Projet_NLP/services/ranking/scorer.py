"""
Combined Ranking Scorer
Computes a final score from semantic, reranker, metadata, and budget signals.
"""
from __future__ import annotations
from services.rag.retriever import RetrievedOutfit
from services.nlp.preference_extractor import PreferenceResult


# Weight constants (must sum to 1.0)
W_SEMANTIC  = 0.45
W_RERANKER  = 0.30
W_METADATA  = 0.15
W_BUDGET    = 0.10


def budget_fit_score(outfit: dict, budget: int | None) -> float:
    """
    1.0 if price <= budget
    Tapers linearly to 0.0 at 2x budget
    0.5 if no budget specified
    """
    if not budget or budget <= 0:
        return 0.5
    price = outfit.get("estimated_price", 0)
    if price <= budget:
        return 1.0
    if price >= budget * 2:
        return 0.0
    # Linear decay between budget and 2*budget
    return 1.0 - (price - budget) / budget


def compute_final_score(candidate: RetrievedOutfit, prefs: PreferenceResult) -> float:
    """
    Combine all signals into a single final ranking score.
    """
    b_score = budget_fit_score(candidate.outfit, prefs.budget)

    final = (
        W_SEMANTIC * candidate.semantic_score
        + W_RERANKER  * candidate.reranker_score
        + W_METADATA  * candidate.metadata_match
        + W_BUDGET    * b_score
    )
    return round(min(max(final, 0.0), 1.0), 4)


def rank_candidates(
    candidates: list[RetrievedOutfit],
    prefs: PreferenceResult,
) -> list[tuple[RetrievedOutfit, float]]:
    """
    Apply combined scoring and return sorted (candidate, final_score) pairs.
    """
    scored = [(c, compute_final_score(c, prefs)) for c in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
