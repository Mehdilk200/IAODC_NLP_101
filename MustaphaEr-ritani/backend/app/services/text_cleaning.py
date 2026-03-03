"""
Text Cleaning Service.
Normalizes and cleans raw text for NLP processing.
Supports English and French.
"""

import re
import string
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-load NLTK to avoid startup delays
_stopwords_cache = {}


def _get_stopwords(language: str = "english") -> set:
    """Load and cache NLTK stopwords for a given language."""
    if language not in _stopwords_cache:
        try:
            from nltk.corpus import stopwords
            _stopwords_cache[language] = set(stopwords.words(language))
        except Exception:
            logger.warning(f"Could not load stopwords for {language}, using empty set.")
            _stopwords_cache[language] = set()
    return _stopwords_cache[language]


def clean_text(text: str, language: str = "en") -> str:
    """
    Full text cleaning pipeline:
    1. Lowercase
    2. Remove URLs and emails
    3. Remove special characters (keep letters, digits, spaces)
    4. Remove extra whitespace
    5. Remove stopwords
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove standalone numbers (e.g. phone numbers, years) but keep mixed like 'h2' or '3d'
    text = re.sub(r"\b\d+\b", " ", text)

    # Remove special characters (keep alphanumeric and spaces)
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s\+\#]", " ", text) # Keep + and # for C++, C#

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords based on language
    nltk_lang = "french" if language == "fr" else "english"
    stop_words = _get_stopwords(nltk_lang)

    # Also include English stopwords for multilingual CVs
    if language == "fr":
        stop_words = stop_words | _get_stopwords("english")

    words = text.split()
    words = [w for w in words if w not in stop_words and len(w) > 1]

    return " ".join(words)


def detect_language(text: str) -> str:
    """
    Detect the language of the text.
    Returns ISO 639-1 code ('en', 'fr', etc.)
    Defaults to 'en' if detection fails.
    """
    try:
        from langdetect import detect
        lang = detect(text[:500])  # Use first 500 chars for speed
        return lang
    except Exception:
        return "en"
