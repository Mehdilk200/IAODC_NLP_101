import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from api.schemas.recommend import Preferences

logger = logging.getLogger(__name__)

class NLPService:
    """Advanced Preference Reasoning Layer with Confidence Scoring."""
    
    PATTERNS = {
        "style": ["casual", "formal", "streetwear", "elegant", "sporty", "vintage", "traditional", "chic", "glamorous", "minimalist"],
        "occasion": ["wedding", "office", "party", "date", "beach", "gym", "funeral", "celebration", "hangout", "dinner", "gala"],
        "color": ["black", "white", "blue", "red", "green", "yellow", "pink", "brown", "grey", "navy", "beige", "noir", "blanc", "rouge", "bleu"],
        "season": ["winter", "summer", "spring", "autumn", "fall", "hiver", "ete", "printemps", "automne"],
        "gender": {"men": ["men", "homme", "male", "garçon"], "women": ["women", "femme", "female", "fille"]},
        "material": ["leather", "cotton", "wool", "silk", "linen", "denim", "velvet"]
    }

    def __init__(self):
        
        pass

    def extract_preferences(self, text: str) -> Tuple[Preferences, float]:
        """
        Extracts preferences and returns (Preferences, OverallConfidence).
        Implements multi-language token matching and budget parsing.
        """
        
        text_lower = text.lower()
        prefs = Preferences()
        confidence_map = {}

    
        is_query = any(word in text_lower for word in ["bghit", "need", "find", "search", "show", "give", "suggest", "tenue", "outfit"])
        base_confidence = 1.0 if is_query else 0.7

        # 2. Domain Slots
        for slot, keywords in self.PATTERNS.items():
            if slot == "gender":
                for g_key, g_words in keywords.items():
                    if any(w in text_lower for w in g_words):
                        prefs.gender = g_key
                        confidence_map[slot] = 1.0
                        break
            elif slot == "color":
                found = [c for c in keywords if c in text_lower]
                if found:
                    prefs.colors = found
                    confidence_map[slot] = 1.0
            elif slot == "material":
                found = [m for m in keywords if m in text_lower]
                if found:
                    prefs.materials = found
                    confidence_map[slot] = 1.0
            else:
                for k in keywords:
                    if k in text_lower:
                        setattr(prefs, slot, k)
                        confidence_map[slot] = 1.0
                        break

        
        budget_match = re.search(r'(\d+)\s*(?:dh|dirham|dollars|\$|€|bits)', text_lower)
        if budget_match:
            prefs.budget = float(budget_match.group(1))
            confidence_map["budget"] = 1.0

       
        if not confidence_map:
            overall_confidence = 0.2
        else:
            
            extracted_slots = len(confidence_map)
            overall_confidence = min(base_confidence, (extracted_slots / 3))  

        return prefs, round(overall_confidence, 2)

nlp_service = NLPService()
