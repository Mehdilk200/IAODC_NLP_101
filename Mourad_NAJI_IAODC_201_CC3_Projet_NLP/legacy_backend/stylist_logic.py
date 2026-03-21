import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "outfits.json"

def load_db():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_slots(text: str) -> dict:
    t = text.lower()

    # intent / style
    style = "casual"
    if any(w in t for w in ["mariage", "wedding", "عرس", "3رس", "formal", "costume", "blazer"]):
        style = "formal"
    elif any(w in t for w in ["work", "bureau", "office", "service", "خدمة", "ستاج", "stage"]):
        style = "smart"
    elif any(w in t for w in ["street", "hoodie", "sneakers", "ستريت"]):
        style = "street"

    # weather
    weather = "normal"
    if any(w in t for w in ["cold", "winter", "برد", "شتا"]):
        weather = "cold"
    elif any(w in t for w in ["hot", "summer", "سخون", "صيف"]):
        weather = "hot"
    elif any(w in t for w in ["rain", "مطر"]):
        weather = "rain"

    # budget (optional)
    budget = None
    m = re.search(r"(\d{2,5})\s*(dh|dhs|درهم)?", t)
    if m:
        budget = int(m.group(1))

    return {"style": style, "weather": weather, "budget": budget}

def recommend_outfits(message: str) -> dict:
    db = load_db()
    slots = extract_slots(message)

    outfits = db.get("outfits", [])

    # filter by style + weather
    candidates = [
        o for o in outfits
        if o["style"] == slots["style"]
        and ("any" in o["weather"] or slots["weather"] in o["weather"])
    ]

    # fallback: style only
    if not candidates:
        candidates = [o for o in outfits if o["style"] == slots["style"]]

    return {
        "understood": slots,
        "recommendations": candidates[:3]
    }