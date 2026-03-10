import os
import time
import logging
from typing import Optional
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from src.controller.config import MODEL_DIR, MODEL_NAME, MAX_LEN

log = logging.getLogger("sentiment-api")

class SentimentModel:
    def __init__(self):
        self.tokenizer: Optional[BertTokenizer] = None
        self.model: Optional[BertForSequenceClassification] = None
        self.device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.source: str = ""
        self.load_time: float = 0.0
        self.total_predictions: int = 0

    def load(self):
        t0 = time.time()
        if os.path.isdir(MODEL_DIR):
            source = MODEL_DIR
            log.info(f"📂 Chargement depuis '{source}'...")
        else:
            source = MODEL_NAME
            log.warning(f"⚠️ '{MODEL_DIR}' introuvable — fallback HuggingFace ({MODEL_NAME})")

        try:
            self.tokenizer = BertTokenizer.from_pretrained(source)
            self.model = BertForSequenceClassification.from_pretrained(source)
            self.model.to(self.device)
            self.model.eval()
            self.source = source
            self.load_time = round(time.time() - t0, 2)
            log.info(f"✅ Modèle prêt sur {self.device} en {self.load_time}s")
        except Exception as e:
            log.error(f"❌ Erreur chargement modèle: {e}")
            raise

    def predict(self, text: str) -> dict:
        t0 = time.time()
        enc = self.tokenizer(text, max_length=MAX_LEN, padding="max_length", truncation=True, return_tensors="pt")
        ids = enc["input_ids"].to(self.device)
        mask = enc["attention_mask"].to(self.device)

        with torch.no_grad():
            logits = self.model(input_ids=ids, attention_mask=mask).logits
            probs = torch.softmax(logits, dim=1)[0]

        p_neg = round(probs[0].item(), 4)
        p_pos = round(probs[1].item(), 4)
        label = int(probs.argmax().item())
        self.total_predictions += 1

        return {
            "text": text,
            "sentiment": "positif" if label == 1 else "negatif",
            "label": label,
            "confidence": round(max(p_neg, p_pos), 4),
            "proba_pos": p_pos,
            "proba_neg": p_neg,
            "inference_ms": round((time.time() - t0) * 1000, 2),
        }

    @property
    def n_params(self) -> int:
        if self.model is None:
            return 0
        return sum(p.numel() for p in self.model.parameters())

sentiment_model = SentimentModel()