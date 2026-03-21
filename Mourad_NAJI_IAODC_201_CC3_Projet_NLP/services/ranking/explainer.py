"""
Explanation Generator
Produces natural-language explanations for why an outfit was recommended.
"""
from __future__ import annotations
from services.nlp.preference_extractor import PreferenceResult


def generate_explanation(
    outfit: dict,
    prefs: PreferenceResult,
    final_score: float,
) -> str:
    """
    Generate a human-readable explanation of why this outfit was recommended.
    """
    parts: list[str] = []
    score_pct = int(final_score * 100)

    # Score framing
    if score_pct >= 85:
        match_word = "perfect"
    elif score_pct >= 70:
        match_word = "great"
    elif score_pct >= 55:
        match_word = "good"
    else:
        match_word = "solid"

    parts.append(f"This is a **{match_word} match** ({score_pct}% fit score)")

    reasons: list[str] = []

    # Occasion match
    if prefs.occasion:
        outfit_occasions = [o.lower() for o in outfit.get("occasion", [])]
        if prefs.occasion in outfit_occasions:
            reasons.append(f"perfect for your **{prefs.occasion}** occasion")

    # Season match
    if prefs.season:
        outfit_seasons = [s.lower() for s in outfit.get("season", [])]
        if prefs.season in outfit_seasons or "any" in outfit_seasons:
            reasons.append(f"ideal for **{prefs.season}** weather")

    # Style match
    if prefs.style and outfit.get("style", "").lower() == prefs.style.lower():
        reasons.append(f"matches your **{prefs.style}** style preference")

    # Color match
    if prefs.color:
        palette = " ".join(outfit.get("color_palette", [])).lower()
        if prefs.color.lower() in palette:
            reasons.append(f"features your preferred **{prefs.color}** tones")

    # Budget match
    if prefs.budget:
        price = outfit.get("estimated_price", 0)
        if price <= prefs.budget:
            reasons.append(f"fits within your **{prefs.budget} dh** budget (est. {price} dh)")
        elif price <= prefs.budget * 1.15:
            reasons.append(f"slightly above budget at ~{price} dh (your budget: {prefs.budget} dh)")

    if reasons:
        parts.append("— " + ", ".join(reasons))

    # Add the outfit's own "why" text as a style note
    why = outfit.get("why", "")
    if why:
        parts.append(f"\n\n💡 *{why}*")

    return " ".join(parts[:2]) + ("".join(parts[2:]) if len(parts) > 2 else "")


def generate_outfit_title(outfit: dict) -> str:
    """Generate a clean display title for the outfit card."""
    style    = outfit.get("style", "").title()
    occasion = outfit.get("occasion", [""])[0].title() if outfit.get("occasion") else ""
    season   = outfit.get("season", [""])[0].title() if outfit.get("season") else ""
    colors   = outfit.get("color_palette", [])
    color    = colors[0].title() if colors else ""

    parts = [c for c in [color, style, occasion, season] if c and c.lower() != "any"]
    return " ".join(parts[:3]) + " Look" if parts else "Curated Outfit"
