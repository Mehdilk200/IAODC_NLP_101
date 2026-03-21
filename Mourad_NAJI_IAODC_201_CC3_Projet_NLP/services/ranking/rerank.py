from typing import List, Tuple, Dict, Any
import logging
import numpy as np
from sentence_transformers import CrossEncoder
from api.schemas.recommend import Preferences, OutfitResult

logger = logging.getLogger(__name__)

PLACEHOLDER_IMAGE = "/static/images/placeholder.jpg"


class RankingService:
    """Production-grade two-stage ranking system with Reranking and MMR."""

    def __init__(self):
        try:
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')
            logger.info("Cross-Encoder reranker loaded.")
        except Exception as e:
            logger.error(f"Failed to load Cross-Encoder: {e}")
            self.reranker = None

    def rerank_and_score(
        self,
        query: str,
        candidates: List[Tuple[Dict, float]],
        prefs: Preferences
    ) -> List[OutfitResult]:
        if not candidates:
            return []

        # 1) Cross-Encoder Fine-Ranking
        if self.reranker:
            pairs = [[query, f"{c[0].get('name', '')} {c[0].get('description', '')}"] for c in candidates]
            cross_scores = self.reranker.predict(pairs)
            cross_scores = 1 / (1 + np.exp(-np.array(cross_scores)))  # approx sigmoid to [0,1]
        else:
            cross_scores = [c[1] for c in candidates]

        results: List[OutfitResult] = []

        for i, (outfit, sim_score) in enumerate(candidates):
            cross_score = float(cross_scores[i])

            # 2) Metadata Score
            meta_score = 0.0
            reasons = []

            # Hard constraint: Gender
            if prefs.gender and outfit.get("gender") and outfit.get("gender").lower() != prefs.gender.lower():
                continue

            # Soft constraint: Style
            if prefs.style and outfit.get("style", "").lower() == prefs.style:
                meta_score += 0.3
                reasons.append(f"matched your **{prefs.style}** style")

            # Soft constraint: Budget
            price = float(outfit.get("estimated_price", 0))
            if prefs.budget:
                if price <= prefs.budget:
                    meta_score += 0.3
                    reasons.append("fits your budget")
                elif price <= prefs.budget * 1.25:
                    meta_score += 0.1
                    reasons.append("quality pick slightly above budget")
                else:
                    meta_score -= 0.5

            # 3) Final score
            final_score = (cross_score * 0.5) + (meta_score * 0.3) + (sim_score * 0.2)
            explanation = self._generate_explanation(reasons, outfit, final_score)

            results.append(OutfitResult(
                id=str(outfit.get("id", "0")),
                title=outfit.get("name", outfit.get("title", "Modern Outfit")),
                description=outfit.get("description", ""),
                tags=outfit.get("tags", []),
                price=price,
                image_url=PLACEHOLDER_IMAGE,  # ✅ always string here
                score=round(max(0, final_score), 3),
                explanation=explanation
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return self._apply_diversity(results)

    def _generate_explanation(self, reasons: List[str], outfit: Dict, score: float) -> str:
        if score > 0.8:
            prefix = "This is a **top-tier match** for you. It "
        elif score > 0.5:
            prefix = "I recommend this because it "
        else:
            prefix = "This is a solid option that "

        if not reasons:
            return f"{prefix}is highly relevant to your fashion request."

        return f"{prefix}{', and '.join(reasons)}. The {outfit.get('style', 'look')} perfectly fits the vibe."

    def _apply_diversity(self, results: List[OutfitResult], limit: int = 10) -> List[OutfitResult]:
        seen_styles = {}
        diverse_results = []
        for r in results:
            style = r.title.split()[0] if r.title else "Style"
            seen_styles[style] = seen_styles.get(style, 0) + 1
            if seen_styles[style] <= 2:
                diverse_results.append(r)
            if len(diverse_results) >= limit:
                break
        return diverse_results


ranking_service = RankingService()
