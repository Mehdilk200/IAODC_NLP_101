import os
import json
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "outfits.json"
INDEX_DIR = BASE_DIR / "data" / "faiss_index"
INDEX_FILE = INDEX_DIR / "outfits.index"
META_FILE  = INDEX_DIR / "outfits_meta.pkl"
VEC_FILE   = INDEX_DIR / "outfits_vectors.npy"

class FashionStore:
    _instance = None

    def __init__(self):
        self.index = None
        self.outfits = []
        self.vectors = None
        self.total = 0
        self._use_faiss = False # Forcing False for stability in Mac Intel env
        self._built = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def build_or_load(self):
        if self._built: return
        
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        
        if INDEX_FILE.exists() and META_FILE.exists() and VEC_FILE.exists():
            logger.info("Loading FashionStore from disk...")
            with open(META_FILE, "rb") as f:
                self.outfits = pickle.load(f)
            self.vectors = np.load(VEC_FILE)
            self.total = len(self.outfits)
            
            if self._use_faiss:
                try:
                    import faiss
                    self.index = faiss.read_index(str(INDEX_FILE))
                except:
                    self._use_faiss = False
            self._built = True
            return

        logger.info("Building FashionStore from scratch...")
        if not DATA_PATH.exists():
            logger.error(f"Data file not found at {DATA_PATH}")
            return

        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            self.outfits = data.get("outfits", [])

        from services.rag.embedder import get_embedder
        embedder = get_embedder()
        texts = [f"{o.get('style', '')} {o.get('description', '')} {' '.join(o.get('tags', []))}" for o in self.outfits]
        self.vectors = embedder.embed_batch(texts)
        
        # Save
        with open(META_FILE, "wb") as f:
            pickle.dump(self.outfits, f)
        np.save(VEC_FILE, self.vectors)
        
        try:
            import faiss
            dim = self.vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(self.vectors)
            faiss.write_index(self.index, str(INDEX_FILE))
        except:
            pass
            
        self.total = len(self.outfits)
        self._built = True

    def search(self, query_vector: np.ndarray, top_k: int = 20) -> List[Tuple[Dict, float]]:
        if not self._built: self.build_or_load()
        
        # Always use Numpy for stability on Mac x86 if Faiss is fussy
        if not self._use_faiss or self.index is None:
            scores = np.dot(self.vectors, query_vector)
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [(self.outfits[i], float(scores[i])) for i in top_indices]
            
        import faiss
        q = query_vector.reshape(1, -1)
        scores, indices = self.index.search(q, top_k)
        return [(self.outfits[idx], float(score)) for score, idx in zip(scores[0], indices[0]) if idx >= 0]
