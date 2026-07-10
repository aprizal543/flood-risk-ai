"""KnowledgeRecommendationService — High-level orchestrator for the KB-based recommendation flow.

Flow:
  1. Receive FRI
  2. Determine Risk Category
  3. Execute Rule Engine
  4. Query Knowledge Base
  5. Generate Recommendation Groups
  6. Generate Explainability
  7. Return DecisionResult
"""

from __future__ import annotations

import logging
from typing import Any

from backend.decision.engine import DecisionEngine
from backend.decision.exceptions import DecisionNotInitializedError
from backend.decision.models import DecisionResult

logger = logging.getLogger(__name__)


class KnowledgeRecommendationService:
    """High-level service that orchestrates the KB-based recommendation pipeline.

    This service is the main entry point for the new recommendation system.
    It is independent from the frontend and produces structured DecisionResult objects.
    """

    def __init__(self, engine: DecisionEngine) -> None:
        self._engine = engine

    @property
    def is_ready(self) -> bool:
        return self._engine.is_ready

    def recommend(self, fri: float) -> DecisionResult:
        """Produce a complete recommendation result from a single FRI value.

        Args:
            fri: Flood Risk Index value (0-100).

        Returns:
            DecisionResult with groups, explanations, and metadata.

        Raises:
            DecisionNotInitializedError: If engine is not ready.
        """
        if not self._engine.is_ready:
            raise DecisionNotInitializedError()

        return self._engine.decide(fri)

    def recommend_as_dict(self, fri: float) -> dict[str, Any]:
        result = self.recommend(fri)
        return self._result_to_dict(result)

    def _result_to_dict(self, result: DecisionResult) -> dict[str, Any]:
        return {
            "status": "berhasil",
            "fri": result.context.fri,
            "tingkat_risiko": f"Risiko {result.context.risk_category.value}",
            "recommended": [
                {
                    "commodity_id": c.commodity_id,
                    "commodity_name": c.commodity_name,
                    "vulnerability_level": c.vulnerability_level,
                    "recommendation_reason": c.recommendation_reason,
                }
                for c in result.recommended
            ],
            "alternative": [
                {
                    "commodity_id": c.commodity_id,
                    "commodity_name": c.commodity_name,
                    "vulnerability_level": c.vulnerability_level,
                    "recommendation_reason": c.recommendation_reason,
                }
                for c in result.alternative
            ],
            "not_recommended": [
                {
                    "commodity_id": c.commodity_id,
                    "commodity_name": c.commodity_name,
                    "vulnerability_level": c.vulnerability_level,
                    "recommendation_reason": c.recommendation_reason,
                }
                for c in result.not_recommended
            ],
            "metadata": {
                "execution_duration_ms": result.metadata.execution_duration_ms,
                "total_commodities": result.report.total_commodities,
            },
        }

    def health_status(self) -> dict[str, Any]:
        return self._engine.health_status()
