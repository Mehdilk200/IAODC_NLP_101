import re

# كلمات مفتاحية بسيطة (Rules-based NLP)
OCCASIONS = {
    "wedding": ["عرس", "زواج", "mariage", "wedding"],
    "work": ["خدمة", "عمل", "bureau", "office", "work", "meeting", "réunion"],
    "party": ["حفلة", "party", "soirée"],
    "casual": ["كاجوال", "casual", "راحة", "daily", "everyday"],
}

SEASONS = {
    "winter": ["شتا", "winter", "hiver", "cold", "بارد"],
    "summer": ["صيف", "summer", "été", "hot", "سخون"],
}

STYLES = {
    "formal": ["رسمي", "formal", "classy", "elegant", "suit", "costume"],
    "streetwear": ["ستريت", "streetwear", "hoodie", "sneakers", "oversize"],
    "traditional": ["تقليدي", "traditional", "jabador", "جلابة", "djellaba"],
}

COLORS = {
    "black": ["كحل", "أسود", "black"],
    "white": ["بيض", "أبيض", "white"],
    "navy": ["كحلي", "navy"],
    "beige": ["بيج", "beige"],
    "grey": ["رمادي", "grey", "gray"],
}


def _pick_category(text: str, mapping: dict) -> str | None:
    t = text.lower()
    for key, words in mapping.items():
        if any(w.lower() in t for w in words):
            return key
    return None


def extract_preferences(text: str) -> dict:
    t = text.strip()

    gender = None
    if re.search(r"\b(man|men|male|rajl|رجل)\b", t.lower()):
        gender = "men"
    if re.search(r"\b(woman|women|female|mra|امرأة)\b", t.lower()):
        gender = "women"

    budget = None
    m = re.search(r"(\d{2,5})\s*(dh|dhs|درهم|mad)", t.lower())
    if m:
        budget = int(m.group(1))

    occasion = _pick_category(t, OCCASIONS)
    season = _pick_category(t, SEASONS)
    style = _pick_category(t, STYLES)
    color = _pick_category(t, COLORS)

    return {
        "gender": gender,
        "budget": budget,
        "occasion": occasion,
        "season": season,
        "style": style,
        "color": color,
        "raw_text": t
    }


def build_search_query(prefs: dict) -> str:
    parts = []

    gender = prefs.get("gender") or "men"
    parts.append(gender)

    # أولوية للمناسبة
    if prefs.get("occasion") == "wedding":
        parts += ["wedding guest", "suit", "formal"]

    # الموسم
    if prefs.get("season"):
        parts.append(prefs["season"])

    # style
    if prefs.get("style") and prefs.get("occasion") != "wedding":
        parts.append(prefs["style"])

    # color
    if prefs.get("color"):
        parts.append(prefs["color"])

    # كلمات كتعاون تجيب Pinterest looks
    parts += ["outfit", "look", "pinterest"]

    return " ".join(parts)
