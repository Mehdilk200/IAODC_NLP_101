"""
Fashion Embedder
Wraps sentence-transformers for generating normalized outfit embeddings.
Singleton pattern — model loaded once at startup.
"""
from __future__ import annotations
import numpy as np
import logging

logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_instance: "FashionEmbedder | None" = None


class FashionEmbedder:
    def __init__(self):
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(MODEL_NAME)
        self.dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dim}")

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single string. Returns normalized float32 array of shape (dim,)."""
        return self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed a list of strings. Returns (N, dim) normalized float32 array."""
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        ).astype("float32")


def get_embedder() -> FashionEmbedder:
    """Get or create the global FashionEmbedder singleton."""
    global _instance
    if _instance is None:
        _instance = FashionEmbedder()
    return _instance
