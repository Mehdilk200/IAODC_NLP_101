"""
SerpAPI Image Client
Confidence-gated fashion image search with TTL caching and retry logic.
"""
from __future__ import annotations
import os
import logging
import time
from typing import Optional

import requests
from dotenv import load_dotenv
from services.cache.cache_manager import image_cache, make_cache_key

load_dotenv()

logger = logging.getLogger(__name__)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search.json"

# Only fetch images when confidence is high enough
MIN_CONFIDENCE_FOR_IMAGES = 0.25

FASHION_KEYWORDS = [
    "outfit", "fashion", "style", "look", "wear",
    "streetwear", "suit", "jacket", "coat", "shoes",
    "dress", "blazer", "hoodie", "sneakers", "formal",
    "kaftan", "jabador", "djellaba",
]

QUERY_BOOSTERS = ["outfit", "fashion look", "style inspiration", "lookbook"]


def _build_fashion_query(base_query: str) -> str:
    return base_query + " " + " ".join(QUERY_BOOSTERS[:2])


def _is_fashion_result(item: dict) -> bool:
    title = item.get("title", "").lower()
    link  = item.get("link", "").lower()
    return any(kw in title or kw in link for kw in FASHION_KEYWORDS)


def search_images(
    query: str,
    num: int = 4,
    confidence: float = 1.0,
) -> list[dict]:
    """
    Search for fashion images via SerpAPI.
    Returns empty list if confidence is too low (preserve API credits).
    """
    if confidence < MIN_CONFIDENCE_FOR_IMAGES:
        logger.info(f"Skipping image search (confidence={confidence:.2f} < threshold)")
        return []

    if not SERPAPI_KEY:
        logger.warning("SERPAPI_KEY not set — skipping image search")
        return []

    cache_key = make_cache_key("images", query, num)
    cached    = image_cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Image cache hit for query: {query[:50]}")
        return cached

    fashion_query = _build_fashion_query(query)
    params = {
        "engine":  "google_images",
        "q":       fashion_query,
        "api_key": SERPAPI_KEY,
        "ijn":     "0",
        "num":     "20",
    }

    # Retry logic
    for attempt in range(3):
        try:
            resp = requests.get(SERPAPI_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            break
        except requests.RequestException as e:
            logger.warning(f"SerpAPI attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return []

    results: list[dict] = []
    for item in data.get("images_results", []):
        if not _is_fashion_result(item):
            continue
        thumbnail = item.get("thumbnail")
        if not thumbnail:
            continue
        results.append({
            "title":     item.get("title", ""),
            "thumbnail": thumbnail,
            "link":      item.get("link", ""),
            "source":    item.get("source", ""),
        })
        if len(results) >= num:
            break

    image_cache.set(cache_key, results)
    logger.info(f"SerpAPI: fetched {len(results)} images for '{query[:50]}'")
    return results
