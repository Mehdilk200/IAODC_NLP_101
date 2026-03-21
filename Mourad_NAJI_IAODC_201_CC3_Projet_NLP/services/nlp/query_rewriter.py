"""
Query Rewriter
Transforms NLP preference slots into an optimised semantic search query.
"""
from __future__ import annotations
from services.nlp.preference_extractor import PreferenceResult

# Fashion-domain vocabulary boosters per slot value
OCCASION_BOOST: dict[str, list[str]] = {
    "wedding":   ["wedding", "formal", "suit", "elegant"],
    "work":      ["office", "professional", "business"],
    "party":     ["party", "night-out", "stylish"],
    "gala":      ["gala", "black-tie", "formal", "evening"],
    "casual":    ["casual", "everyday", "relaxed"],
    "eid":       ["eid", "traditional", "festive", "moroccan"],
    "ceremony":  ["ceremony", "formal", "occasion"],
    "date":      ["date-night", "dinner", "romantic"],
    "sport":     ["athletic", "sporty", "activewear"],
    "festival":  ["festival", "music", "outdoor", "boho"],
    "family":    ["family", "gathering", "casual"],
}

STYLE_BOOST: dict[str, list[str]] = {
    "formal":      ["formal", "elegant", "suit", "dress"],
    "smart":       ["smart-casual", "blazer", "professional"],
    "streetwear":  ["streetwear", "urban", "sneakers", "hoodie"],
    "traditional": ["moroccan", "traditional", "jabador", "kaftan"],
    "athletic":    ["athletic", "sport", "activewear"],
    "bohemian":    ["boho", "flowy", "linen", "relaxed"],
}

SEASON_BOOST: dict[str, list[str]] = {
    "winter": ["winter", "cozy", "layered", "warm"],
    "summer": ["summer", "light", "breathable", "fresh"],
    "fall":   ["fall", "autumn", "warm-tones"],
    "spring": ["spring", "fresh", "light"],
    "any":    [],
}

DEFAULT_GENDER = "men"


def build_search_query(prefs: PreferenceResult) -> str:
    """
    Build an optimised semantic query from extracted preferences.
    Priority order: gender > occasion > season > style > color > boosters
    """
    parts: list[str] = []

    gender = prefs.gender or DEFAULT_GENDER
    parts.append(f"{gender} fashion outfit")

    if prefs.occasion:
        parts += OCCASION_BOOST.get(prefs.occasion, [prefs.occasion])

    if prefs.season and prefs.season != "any":
        parts += SEASON_BOOST.get(prefs.season, [prefs.season])

    if prefs.style:
        parts += STYLE_BOOST.get(prefs.style, [prefs.style])

    if prefs.color:
        parts.append(f"{prefs.color} color outfit")

    # Always add fashion-domain anchors for better semantic matching
    parts += ["lookbook", "style", "look"]

    # Budget hint (textual)
    if prefs.budget:
        if prefs.budget < 300:
            parts.append("affordable")
        elif prefs.budget > 800:
            parts.append("premium luxury")

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_parts: list[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            unique_parts.append(p)

    return " ".join(unique_parts)


def rewrite_for_rag(prefs: PreferenceResult) -> str:
    """
    Build a descriptive sentence-form query for embedding (better for semantic search).
    e.g. "men formal elegant wedding winter navy suit outfit lookbook style"
    """
    pieces: list[str] = []

    gender = prefs.gender or DEFAULT_GENDER
    pieces.append(gender)

    if prefs.style:
        pieces.append(prefs.style)
    if prefs.occasion:
        pieces.append(prefs.occasion)
    if prefs.season and prefs.season != "any":
        pieces.append(prefs.season)
    if prefs.color:
        pieces.append(prefs.color)
    if prefs.formality:
        pieces.append(prefs.formality)

    pieces += ["outfit", "style", "look"]

    return " ".join(pieces)
