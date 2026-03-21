"""
Cache Manager
Thread-safe in-memory TTL cache. Drop-in Redis-ready design.
Keys are sha256 hashes of the query/request content.
"""
from __future__ import annotations
import threading
import time
import hashlib
import json
from typing import Any, Optional


class TTLCache:
    """A simple thread-safe in-memory cache with per-entry TTL."""

    def __init__(self, default_ttl: int = 300):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock  = threading.Lock()
        self.default_ttl = default_ttl

    def _make_key(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def get(self, raw_key: str) -> Optional[Any]:
        key = self._make_key(raw_key)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, raw_key: str, value: Any, ttl: Optional[int] = None) -> None:
        key     = self._make_key(raw_key)
        expires = time.monotonic() + (ttl if ttl is not None else self.default_ttl)
        with self._lock:
            self._store[key] = (value, expires)

    def invalidate(self, raw_key: str) -> None:
        key = self._make_key(raw_key)
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        with self._lock:
            now   = time.monotonic()
            total = len(self._store)
            alive = sum(1 for _, (_, exp) in self._store.items() if exp > now)
        return {"total_keys": total, "alive_keys": alive, "expired_keys": total - alive}


# ─────────────────────────────────────────────
# Named cache instances with domain-specific TTLs
# ─────────────────────────────────────────────

# NLP extraction results — short TTL (user may rephrase quickly)
nlp_cache = TTLCache(default_ttl=300)       # 5 minutes

# RAG retrieval results — medium TTL (corpus is stable)
rag_cache = TTLCache(default_ttl=600)       # 10 minutes

# SerpAPI image results — long TTL (expensive external API)
image_cache = TTLCache(default_ttl=1800)    # 30 minutes


def make_cache_key(*args) -> str:
    """Create a stable string key from arbitrary arguments."""
    return json.dumps(args, sort_keys=True, default=str)
