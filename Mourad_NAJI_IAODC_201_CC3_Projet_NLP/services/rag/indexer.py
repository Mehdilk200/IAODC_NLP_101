"""
FAISS Outfit Index
Builds and persists a FAISS IndexFlatIP over all outfit descriptions.
Automatically rebuilds when outfits.json is modified.
"""
from __future__ import annotations
import json
import os
import pickle
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

DATA_PATH     = Path(__file__).parent.parent.parent / "data" / "outfits.json"
INDEX_DIR     = Path(__file__).parent.parent.parent / "data" / "faiss_index"
INDEX_FILE    = INDEX_DIR / "outfits.index"
META_FILE     = INDEX_DIR / "outfits_meta.pkl"
MTIME_FILE    = INDEX_DIR / "outfits_mtime.txt"

_instance: "OutfitIndex | None" = None


class OutfitIndex:
    """FAISS-backed index over outfit descriptions with Numpy fallback."""

    def __init__(self):
        self.index = None
        self.outfits: list[dict] = []
        self.vectors: np.ndarray | None = None
        self.total: int = 0
        self._built = False
        self._use_faiss = False # Force False to avoid segfaults on Mac x86

    @classmethod
    def get_instance(cls) -> "OutfitIndex":
        global _instance
        if _instance is None:
            _instance = cls()
        return _instance

    def build_or_load(self) -> None:
        """Load from disk if up-to-date, otherwise rebuild from outfits.json."""
        # Check if we should use FAISS or fallback to Pure Numpy
        # On some Mac Intel environments, Faiss + Torch segfaults.
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        current_mtime = str(os.path.getmtime(DATA_PATH))
        saved_mtime   = MTIME_FILE.read_text().strip() if MTIME_FILE.exists() else ""

        if (
            INDEX_FILE.exists()
            and META_FILE.exists()
            and current_mtime == saved_mtime
        ):
            logger.info("Loading semantic index from disk…")
            if self._use_faiss:
                try:
                    import faiss
                    self.index = faiss.read_index(str(INDEX_FILE))
                except Exception as e:
                    logger.warning(f"Could not load FAISS index ({e}). Falling back to Numpy.")
                    self._use_faiss = False
            else:
                logger.info("FAISS disabled. Using Numpy.")
                
            with open(META_FILE, "rb") as f:
                self.outfits = pickle.load(f)
            
            # Load vectors for numpy fallback
            VEC_FILE = INDEX_DIR / "outfits_vectors.npy"
            if VEC_FILE.exists():
                self.vectors = np.load(VEC_FILE)
            
            self.total    = len(self.outfits)
            self._built   = True
            logger.info(f"Index loaded: {self.total} outfits (Using {'FAISS' if self._use_faiss else 'Numpy'})")
            return

        logger.info("Building semantic index from outfits.json…")
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.outfits = data.get("outfits", [])

        from services.rag.embedder import get_embedder
        embedder  = get_embedder()
        descriptions = [_outfit_to_text(o) for o in self.outfits]
        vectors      = embedder.embed_batch(descriptions)
        self.vectors = vectors

        try:
            import faiss
            dim        = vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(vectors)
            faiss.write_index(self.index, str(INDEX_FILE))
            self._use_faiss = True
        except Exception as e:
            logger.warning(f"Failed to build FAISS index ({e}). Using Numpy fallback.")
            self._use_faiss = False

        # Save metadata and vectors
        with open(META_FILE, "wb") as f:
            pickle.dump(self.outfits, f)
        np.save(INDEX_DIR / "outfits_vectors.npy", vectors)
        MTIME_FILE.write_text(current_mtime)

        self.total = len(self.outfits)
        self._built = True
        logger.info(f"Index built: {self.total} outfits (Using {'FAISS' if self._use_faiss else 'Numpy'})")

    def search(self, query_vector: np.ndarray, top_k: int = 20) -> list[tuple[dict, float]]:
        """Return top_k (outfit, score) pairs."""
        if not self._built:
            self.build_or_load()

        if self._use_faiss and self.index:
            try:
                q = query_vector.reshape(1, -1)
                scores, indices = self.index.search(q, min(top_k, self.total))
                results: list[tuple[dict, float]] = []
                for idx, score in zip(indices[0], scores[0]):
                    if idx >= 0:
                        results.append((self.outfits[idx], float(score)))
                return results
            except Exception as e:
                logger.error(f"FAISS search failed ({e}). Falling back to Numpy.")
                self._use_faiss = False

        # Numpy Fallback (Inner Product == Cosine Similarity for normalized vectors)
        if self.vectors is not None:
            scores = np.dot(self.vectors, query_vector)
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [(self.outfits[i], float(scores[i])) for i in top_indices]
        
        return []


def _outfit_to_text(outfit: dict) -> str:
    """Create a rich text representation of an outfit for embedding."""
    parts = [
        outfit.get("description", ""),
        outfit.get("style", ""),
        outfit.get("gender", ""),
        " ".join(outfit.get("occasion", [])),
        " ".join(outfit.get("season", [])),
        " ".join(outfit.get("color_palette", [])),
        " ".join(outfit.get("tags", [])),
        outfit.get("why", ""),
        " ".join(outfit.get("items", {}).values()),
    ]
    return " ".join(p for p in parts if p).strip()
