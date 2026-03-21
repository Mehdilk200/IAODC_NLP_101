"""
Diversity Filter — Maximal Marginal Relevance (MMR)
Ensures outfit recommendations are diverse and not near-duplicates.
"""
from __future__ import annotations
import numpy as np
from services.rag.embedder import get_embedder
from services.rag.retriever import RetrievedOutfit


def mmr_rerank(
    ranked: list[tuple[RetrievedOutfit, float]],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[tuple[RetrievedOutfit, float]]:
    """
    Maximal Marginal Relevance selection.
    lambda_param: 1.0 = pure relevance, 0.0 = pure diversity.
    """
    if len(ranked) <= top_k:
        return ranked

    embedder = get_embedder()

    # Embed outfit descriptions
    descriptions = [_outfit_text(c.outfit) for c, _ in ranked]
    try:
        vectors = embedder.embed_batch(descriptions)  # (N, dim)
    except Exception:
        # If embedding fails, return top_k by score only
        return ranked[:top_k]

    selected_indices: list[int] = []
    remaining_indices = list(range(len(ranked)))

    # Always pick the highest-scored outfit first
    best_idx = 0
    selected_indices.append(best_idx)
    remaining_indices.remove(best_idx)

    while len(selected_indices) < top_k and remaining_indices:
        selected_vecs = vectors[selected_indices]  # (S, dim)
        best_score    = -np.inf
        best_i        = remaining_indices[0]

        for i in remaining_indices:
            relevance    = ranked[i][1]  # final score
            # Max similarity to already-selected outfits
            sims         = np.dot(vectors[i], selected_vecs.T)  # (S,)
            max_sim      = float(np.max(sims))

            mmr_score    = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score = mmr_score
                best_i     = i

        selected_indices.append(best_i)
        remaining_indices.remove(best_i)

    return [ranked[i] for i in selected_indices]


def _outfit_text(outfit: dict) -> str:
    return " ".join([
        outfit.get("style", ""),
        " ".join(outfit.get("color_palette", [])),
        " ".join(outfit.get("occasion", [])),
        outfit.get("description", "")[:100],
    ])
