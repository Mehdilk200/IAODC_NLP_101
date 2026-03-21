from typing import Any, Optional
import hashlib
import time

class SimpleMemoryCache:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl

    def _get_key(self, obj: Any) -> str:
        return hashlib.sha256(str(obj).encode()).hexdigest()

    def get(self, key_source: Any) -> Optional[Any]:
        key = self._get_key(key_source)
        if key in self.cache:
            val, expiry = self.cache[key]
            if time.time() < expiry:
                return val
            else:
                del self.cache[key]
        return None

    def set(self, key_source: Any, value: Any):
        key = self._get_key(key_source)
        self.cache[key] = (value, time.time() + self.ttl)

# Global instances
recommend_cache = SimpleMemoryCache(ttl=3600)  # 1 hour
image_cache = SimpleMemoryCache(ttl=86400)      # 24 hours
