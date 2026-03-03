"""
Similarity Service.
Computes cosine similarity between embeddings and converts to percentage score.
"""

import numpy as np
from typing import List


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Returns:
        Float in range [-1, 1], where 1 = identical, 0 = orthogonal
    """
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def similarity_to_score(similarity: float) -> float:
    """
    Convert cosine similarity [-1, 1] to a percentage score [0, 100].

    Uses a calibrated formula:
    - Raw cosine similarity is shifted and scaled to [0, 100]
    - Scores below 0 are clamped to 0
    """
    # Shift from [-1, 1] to [0, 1], then scale to [0, 100]
    score = ((similarity + 1) / 2) * 100
    return round(max(0.0, min(100.0, score)), 2)


def compute_match_score(
    cv_embedding: List[float],
    job_embedding: List[float],
) -> float:
    """
    Compute the final match score between a CV and a job description.

    Returns:
        Match percentage (0–100)
    """
    similarity = cosine_similarity(cv_embedding, job_embedding)
    return similarity_to_score(similarity)


def rank_candidates(
    candidates: List[dict],
    job_embedding: List[float],
) -> List[dict]:
    """
    Rank a list of candidates by their match score against a job.

    Args:
        candidates: List of candidate dicts with 'embedding' key
        job_embedding: Job description embedding vector

    Returns:
        Sorted list of candidates (highest score first) with 'score' added
    """
    ranked = []
    for candidate in candidates:
        emb = candidate.get("embedding")
        if emb:
            score = compute_match_score(emb, job_embedding)
        else:
            score = 0.0
        candidate["score"] = score
        ranked.append(candidate)

    return sorted(ranked, key=lambda x: x["score"], reverse=True)
