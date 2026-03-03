"""
Embedding Service.
Generates sentence embeddings using Sentence Transformers.
Model: sentence-transformers/all-MiniLM-L6-v2
"""

import logging
from typing import List
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_model():
    """
    Lazy-load and cache the SentenceTransformer model.
    Only loaded once per application lifecycle.
    """
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"✅ Embedding model loaded: {settings.EMBEDDING_MODEL}")
        return model
    except Exception as e:
        logger.exception(f"Failed to load embedding model: {e}")
        raise RuntimeError(f"Could not load embedding model: {e}")


def generate_embedding(text: str) -> List[float]:
    """
    Generate a sentence embedding for the given text.

    Args:
        text: Input text to embed

    Returns:
        List of floats representing the embedding vector (384 dimensions)
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    model = _get_model()
    # Truncate to avoid token limit issues (model max: 256 tokens)
    text = text[:5000]
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single batch.
    More efficient than calling generate_embedding() in a loop.

    Args:
        texts: List of input texts

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    model = _get_model()
    # Truncate each text
    texts = [t[:5000] for t in texts]
    embeddings = model.encode(texts, convert_to_numpy=True, batch_size=32)
    return [emb.tolist() for emb in embeddings]
