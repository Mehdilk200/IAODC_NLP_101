"""
Fallback Handler
Generates clarification questions when NLP confidence is too low.
"""
from __future__ import annotations
from services.nlp.preference_extractor import PreferenceResult

LOW_CONFIDENCE_THRESHOLD = 0.35

CLARIFICATION_TEMPLATES = [
    "Could you tell me a bit more? For example:",
    "Great, I'd love to help! To find the perfect outfit, I need a few details:",
    "I want to get this just right for you. Could you clarify:",
]

SLOT_QUESTIONS = {
    "gender":   "👤 Is this for a man or a woman?",
    "occasion": "🎯 What's the occasion? (e.g. wedding, work, casual outing, date night…)",
    "season":   "🌤 What's the weather like? (summer, winter, fall, spring…)",
    "style":    "👔 What style do you prefer? (formal, smart-casual, streetwear, traditional…)",
    "color":    "🎨 Any preferred color? (black, navy, beige, white…)",
    "budget":   "💰 What's your budget? (e.g. 500dh, 1000dh…)",
}


def needs_fallback(prefs: PreferenceResult) -> bool:
    return prefs.confidence < LOW_CONFIDENCE_THRESHOLD


def build_fallback_message(prefs: PreferenceResult) -> str:
    """
    Returns a clarification message listing only the missing slots.
    """
    missing: list[str] = []
    if not prefs.gender:   missing.append("gender")
    if not prefs.occasion: missing.append("occasion")
    if not prefs.season:   missing.append("season")
    if not prefs.style:    missing.append("style")

    # Always show budget if missing
    if not prefs.budget:
        missing.append("budget")

    if not missing:
        return ""

    import random
    intro = random.choice(CLARIFICATION_TEMPLATES)
    questions = "\n".join(f"  • {SLOT_QUESTIONS[s]}" for s in missing if s in SLOT_QUESTIONS)
    return f"{intro}\n\n{questions}"


def build_did_you_mean(prefs: PreferenceResult) -> str | None:
    """
    Suggests the most likely interpretation when confidence is medium.
    """
    parts: list[str] = []
    if prefs.gender:   parts.append(f"**{prefs.gender}**")
    if prefs.style:    parts.append(f"**{prefs.style}** style")
    if prefs.occasion: parts.append(f"for a **{prefs.occasion}**")
    if prefs.season:   parts.append(f"in **{prefs.season}**")

    if not parts:
        return None

    return "Did you mean: " + " ".join(parts) + "? I'll recommend based on that — feel free to correct me!"
