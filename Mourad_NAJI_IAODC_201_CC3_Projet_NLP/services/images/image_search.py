import os
import logging
import httpx
from typing import Optional, Dict, Any
from services.cache.memory_cache import image_cache

logger = logging.getLogger(__name__)


class ImageSearchService:
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY", "").strip()
        self.provider = os.getenv("IMAGES_PROVIDER", "auto").lower().strip()
        self.base_url = "https://api.pexels.com/v1/search"
        self.local_static_base = "/static/images"
        self.placeholder = f"{self.local_static_base}/placeholder.jpg"

    async def get_image_url(self, outfit: Dict[str, Any], user_query: str) -> str:
        outfit_id = str(outfit.get("id", "unknown"))

        # cache version جديد باش ما يبقاش يجيب الصور القديمة
        cache_key = f"img_v2_{outfit_id}_{user_query}".lower()

        cached_url = image_cache.get(cache_key)
        if cached_url:
            return cached_url

        # If dataset already has a good external image url, keep it
        existing_url = (outfit.get("image_url") or "").strip()
        if existing_url.startswith("http") and "source.unsplash.com" not in existing_url:
            image_cache.set(cache_key, existing_url)
            return existing_url

        # Pexels
        if (self.provider in ("auto", "pexels")) and self.pexels_api_key:
            pexels_url = await self._search_pexels(outfit, user_query)
            if pexels_url:
                image_cache.set(cache_key, pexels_url)
                return pexels_url

        # Local fallback
        local_url = self._get_local_fallback(outfit)
        image_cache.set(cache_key, local_url)
        return local_url

    async def _search_pexels(self, outfit: Dict[str, Any], user_query: str) -> Optional[str]:
        if not self.pexels_api_key:
            return None

        tags = outfit.get("tags", []) or []
        title = outfit.get("title", "") or ""

        # Query موجه للفاشن
        style_keywords = "outfit fashion clothing street style lookbook"
        tag_part = " ".join([str(t).replace("_", " ") for t in tags[:5]])

        search_query = f"{title} {tag_part} {user_query} {style_keywords}".strip()
        search_query = " ".join(search_query.split())[:120]

        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": search_query,
            "per_page": 10,
            "orientation": "portrait"
        }

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get(self.base_url, headers=headers, params=params)

            if response.status_code != 200:
                if response.status_code == 429:
                    logger.warning("Pexels API rate limit exceeded.")
                elif response.status_code == 401:
                    logger.error("Pexels API key invalid.")
                else:
                    logger.error(f"Pexels API error: {response.status_code}")
                return None

            data = response.json()
            photos = data.get("photos", []) or []
            if not photos:
                return None

            # اختيار أحسن صورة (alt فيها كلمات ديال الفاشن)
            wanted = [
                "outfit", "fashion", "clothing", "wear", "street", "style",
                "suit", "dress", "jacket", "jeans", "shoes", "model"
            ]
            wanted += [str(t).lower().replace("_", " ") for t in tags[:6]]

            def score(p: Dict[str, Any]) -> int:
                alt = (p.get("alt") or "").lower()
                s = 0
                for w in wanted:
                    if w and w in alt:
                        s += 2
                if p.get("height", 0) > p.get("width", 0):
                    s += 1
                return s

            best = max(photos, key=score)
            src = best.get("src", {}) or {}
            return src.get("portrait") or src.get("large") or src.get("medium")

        except Exception as e:
            logger.error(f"Error fetching from Pexels: {e}")
            return None

    def _get_local_fallback(self, outfit: Dict[str, Any]) -> str:
        import random
        from pathlib import Path

        category = "casual"
        tags = outfit.get("tags", []) or []
        tags_lower = [str(t).lower() for t in tags]

        if any(t in ["formal", "wedding", "ceremony", "suit", "dress"] for t in tags_lower):
            category = "formal"
        elif "streetwear" in tags_lower:
            category = "streetwear"
        elif outfit.get("gender") in ("men", "male") or "men" in tags_lower or "male" in tags_lower:
            category = "men"
        elif outfit.get("gender") in ("women", "female") or "women" in tags_lower or "female" in tags_lower:
            category = "women"

        base_path = Path(__file__).parent.parent.parent / "data" / "images" / category
        if base_path.exists() and base_path.is_dir():
            images = [f for f in os.listdir(base_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if images:
                chosen = random.choice(images)
                return f"{self.local_static_base}/{category}/{chosen}"

        return self.placeholder


# Global instance
image_search_service = ImageSearchService()


# Backward-compatible alias (async)
async def get_outfit_image(outfit: dict, query: str = "") -> str:
    return await image_search_service.get_image_url(outfit, query)
