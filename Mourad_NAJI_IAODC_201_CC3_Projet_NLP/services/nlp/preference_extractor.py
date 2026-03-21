"""
NLP Preference Extractor
Multi-language (English, French, Arabic, Darija) with confidence scoring.
"""
from __future__ import annotations
import re
import hashlib
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  Slot pattern dictionaries
# ─────────────────────────────────────────────

OCCASION_PATTERNS: dict[str, list[str]] = {
    "wedding":      ["عرس", "زواج", "mariage", "wedding", "نيشان", "7afla"],
    "work":         ["خدمة", "عمل", "bureau", "office", "work", "meeting", "réunion",
                     "interview", "stage", "ستاج", "presentation", "travail"],
    "party":        ["حفلة", "party", "soirée", "fête", "7afla", "night-out", "clubbing"],
    "gala":         ["gala", "galla", "banquet", "black-tie", "award"],
    "casual":       ["كاجوال", "casual", "راحة", "daily", "everyday", "عادي", "quotidien",
                     "weekend", "sortie", "brunch"],
    "eid":          ["عيد", "eid", "aid"],
    "ceremony":     ["ceremony", "مراسيم", "cérémonie", "graduation", "تخرج"],
    "date":         ["date", "rendez-vous", "romantic", "dinner", "رومانسي"],
    "sport":        ["sport", "gym", "workout", "رياضة", "training"],
    "festival":     ["festival", "concert", "music", "outdoor-event"],
    "family":       ["عيلة", "family", "famille", "gathering", "فطور"],
}

SEASON_PATTERNS: dict[str, list[str]] = {
    "winter": ["شتا", "winter", "hiver", "cold", "بارد", "froid", "شتاء", "snow", "neige"],
    "summer": ["صيف", "summer", "été", "hot", "سخون", "chaud", "الصيف", "warm", "chaleur"],
    "fall":   ["خريف", "fall", "automne", "autumn", "kharif"],
    "spring": ["ربيع", "spring", "printemps", "rbii3", "rbii"],
    "any":    ["any", "all-season", "all year", "year-round"],
}

STYLE_PATTERNS: dict[str, list[str]] = {
    "formal":      ["رسمي", "formal", "classy", "elegant", "suit", "costume", "chic",
                    "habillé", "formelle", "blazer", "tuxedo"],
    "smart":       ["smart", "smart-casual", "semi-formal", "business casual", "bureau",
                    "office", "professional", "presentable"],
    "streetwear":  ["ستريت", "streetwear", "hoodie", "sneakers", "oversize", "urban",
                    "casual-street", "hype", "skate", "jogger"],
    "traditional": ["تقليدي", "traditional", "jabador", "جلابة", "djellaba", "kaftan",
                    "قفطان", "takchita", "beldi", "مغربي", "moroccan"],
    "athletic":    ["sport", "gym", "athletic", "tracksuit", "sweatpants", "رياضي"],
    "bohemian":    ["boho", "bohemian", "hippie", "festival", "flowy", "linen"],
}

COLOR_PATTERNS: dict[str, list[str]] = {
    "black":    ["كحل", "أسود", "black", "noir", "all-black", "dark"],
    "white":    ["بيض", "أبيض", "white", "blanc", "all-white", "cream", "ivory"],
    "navy":     ["كحلي", "navy", "marine", "bleu marine", "dark blue"],
    "beige":    ["بيج", "beige", "camel", "cream", "ivory", "offwhite"],
    "grey":     ["رمادي", "grey", "gray", "gris", "charcoal"],
    "blue":     ["أزرق", "blue", "bleu", "denim", "cobalt"],
    "green":    ["أخضر", "green", "vert", "olive", "sage", "emerald", "mint"],
    "red":      ["أحمر", "red", "rouge", "burgundy", "wine", "maroon"],
    "brown":    ["بني", "brown", "marron", "tan", "caramel", "rust"],
    "yellow":   ["أصفر", "yellow", "jaune", "mustard"],
    "pink":     ["وردي", "pink", "rose", "blush", "dusty-rose", "mauve"],
    "purple":   ["بنفسجي", "purple", "violet", "lavender", "lilac"],
    "gold":     ["ذهبي", "gold", "doré", "golden"],
}

GENDER_PATTERNS: dict[str, list[str]] = {
    "men":   ["man", "men", "male", "rajl", "رجل", "homme", "مسيو", "boy", "للرجال",
              "gars", "رجالي", "rjal"],
    "women": ["woman", "women", "female", "mra", "امرأة", "femme", "fille", "girl",
              "للنساء", "نسائي", "nsa"],
}

BUDGET_PATTERN = re.compile(
    r"(\d{2,5})\s*(dh|dhs|درهم|mad|euro?s?|€|\$|dollars?|dirhams?)", re.IGNORECASE
)

FORMALITY_BOOSTERS = {
    "very-formal": ["black-tie", "tuxedo", "gala", "gown", "costume 3 pièces"],
    "formal":      ["suit", "blazer", "formal", "rسمي", "costume"],
    "smart":       ["smart", "business casual", "semi-formal"],
    "casual":      ["casual", "everyday", "relaxed", "راحة"],
}


# ─────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────

@dataclass
class PreferenceResult:
    gender: Optional[str] = None
    budget: Optional[int] = None
    occasion: Optional[str] = None
    season: Optional[str] = None
    style: Optional[str] = None
    color: Optional[str] = None
    formality: Optional[str] = None
    confidence: float = 0.0
    confidence_map: dict = field(default_factory=dict)
    raw_text: str = ""
    text_hash: str = ""

    def to_dict(self) -> dict:
        return {
            "gender": self.gender,
            "budget": self.budget,
            "occasion": self.occasion,
            "season": self.season,
            "style": self.style,
            "color": self.color,
            "formality": self.formality,
            "confidence": round(self.confidence, 3),
            "confidence_map": {k: round(v, 3) for k, v in self.confidence_map.items()},
            "raw_text": self.raw_text,
        }


# ─────────────────────────────────────────────
#  Core extraction logic
# ─────────────────────────────────────────────

def _match_slot(text: str, patterns: dict[str, list[str]]) -> tuple[Optional[str], float]:
    """Return (best_key, confidence). Confidence = 1.0 for exact, 0.7 for partial."""
    t = text.lower()
    for key, words in patterns.items():
        for w in words:
            # Exact word-boundary match → high confidence
            if re.search(r"\b" + re.escape(w.lower()) + r"\b", t):
                return key, 1.0
            # Substring match → lower confidence
            if w.lower() in t:
                return key, 0.75
    return None, 0.0


def _extract_budget(text: str) -> tuple[Optional[int], float]:
    m = BUDGET_PATTERN.search(text)
    if m:
        return int(m.group(1)), 1.0
    return None, 0.0


def _extract_gender(text: str) -> tuple[Optional[str], float]:
    t = text.lower()
    male_score = sum(
        1.0 if re.search(r"\b" + re.escape(w) + r"\b", t) else (0.7 if w in t else 0)
        for w in GENDER_PATTERNS["men"]
    )
    female_score = sum(
        1.0 if re.search(r"\b" + re.escape(w) + r"\b", t) else (0.7 if w in t else 0)
        for w in GENDER_PATTERNS["women"]
    )
    if male_score > female_score and male_score > 0:
        return "men", min(male_score / 3, 1.0)
    if female_score > male_score and female_score > 0:
        return "women", min(female_score / 3, 1.0)
    return None, 0.0


def _infer_formality(style: Optional[str], occasion: Optional[str]) -> Optional[str]:
    if style == "formal" or occasion in ("wedding", "gala"):
        return "very-formal" if occasion == "gala" else "formal"
    if style == "smart" or occasion in ("work", "interview"):
        return "smart"
    if style in ("streetwear", "athletic", "bohemian") or occasion == "casual":
        return "casual"
    return None


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def extract_preferences(text: str) -> PreferenceResult:
    """
    Extract structured fashion preferences from free-form user text.
    Supports English, French, Arabic, Darija.
    Returns a PreferenceResult with per-slot confidence scores.
    """
    t = text.strip()
    text_hash = hashlib.sha256(t.encode()).hexdigest()[:16]

    gender, g_conf       = _extract_gender(t)
    budget, b_conf       = _extract_budget(t)
    occasion, oc_conf    = _match_slot(t, OCCASION_PATTERNS)
    season, se_conf      = _match_slot(t, SEASON_PATTERNS)
    style, st_conf       = _match_slot(t, STYLE_PATTERNS)
    color, co_conf       = _match_slot(t, COLOR_PATTERNS)

    confidence_map: dict[str, float] = {}
    if gender:   confidence_map["gender"]   = g_conf
    if budget:   confidence_map["budget"]   = b_conf
    if occasion: confidence_map["occasion"] = oc_conf
    if season:   confidence_map["season"]   = se_conf
    if style:    confidence_map["style"]    = st_conf
    if color:    confidence_map["color"]    = co_conf

    # Overall confidence: average of detected slots, penalise if fewer than 2 slots found
    overall = sum(confidence_map.values()) / max(len(confidence_map), 1)
    if len(confidence_map) < 2:
        overall *= 0.6  # penalty for very sparse input

    formality = _infer_formality(style, occasion)

    return PreferenceResult(
        gender=gender,
        budget=budget,
        occasion=occasion,
        season=season,
        style=style,
        color=color,
        formality=formality,
        confidence=overall,
        confidence_map=confidence_map,
        raw_text=t,
        text_hash=text_hash,
    )
