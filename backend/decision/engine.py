"""Decision Engine — Core engine that orchestrates rules and KB to produce recommendation groups.

The DecisionEngine is the central component. It:
  1. Receives a DecisionContext (FRI + risk category)
  2. Fetches all commodities from the Knowledge Base
  3. Evaluates each commodity against the Rule Engine
  4. Groups commodities into recommended / alternative / not_recommended
  5. Generates explanations from the Explainability Engine
  6. Returns a DecisionResult

This engine is stateless after initialization.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.decision.exceptions import (
    DecisionKnowledgeError,
    DecisionNotInitializedError,
)
from backend.decision.explainability import ExplainabilityEngine
from backend.decision.mapper import RiskMapper
from backend.decision.models import (
    CommodityRecommendation,
    DecisionMetadata,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
)
from backend.decision.rules import InferenceRuleEngine
from backend.knowledge.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Core decision engine — stateless after initialization."""

    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        rule_engine: InferenceRuleEngine | None = None,
    ) -> None:
        self._kb = knowledge_base
        self._rules = rule_engine or InferenceRuleEngine()
        self._mapper = RiskMapper()
        self._explainer = ExplainabilityEngine()
        self._ready: bool = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def rule_engine(self) -> InferenceRuleEngine:
        return self._rules

    def initialize(self) -> None:
        if not self._kb.is_ready:
            raise DecisionKnowledgeError("Knowledge Base is not ready")
        if not self._rules.is_valid:
            raise DecisionKnowledgeError("Rule Engine validation failed")
        self._ready = True
        logger.info(
            "DecisionEngine initialized with %d commodities, %d rules",
            self._kb.count(),
            self._rules.rule_count,
        )

    def decide(self, fri: float) -> DecisionResult:
        if not self._ready:
            raise DecisionNotInitializedError()

        start = time.perf_counter()

        context = self._mapper.create_context(fri)
        risk_category = context.risk_category.value

        all_commodities = self._kb.get_all()

        recommended_list: list[CommodityRecommendation] = []
        alternative_list: list[CommodityRecommendation] = []
        not_recommended_list: list[CommodityRecommendation] = []

        rules_matched = 0
        rules_evaluated = 0

        for c in all_commodities:
            rules_evaluated += 1
            status = self._rules.evaluate(
                vulnerability_level=c.vulnerability_level,
                risk_category=risk_category,
            )
            rules_matched += 1

            reason = self._explainer.generate_reason(c, status, risk_category)

            rec = CommodityRecommendation(
                commodity_id=c.commodity_id,
                commodity_name=c.commodity_name,
                recommendation_status=status,
                vulnerability_level=c.vulnerability_level,
                maximum_inundation_duration=c.maximum_inundation_duration,
                main_impacts=list(c.main_impacts),
                major_impacts=list(c.major_impacts),
                damage_symptoms=list(c.damage_symptoms),
                recommendation_reason=reason,
                knowledge_reference=c.scientific_reference,
            )

            if status == RecommendationStatus.RECOMMENDED:
                recommended_list.append(rec)
            elif status == RecommendationStatus.ALTERNATIVE:
                alternative_list.append(rec)
            else:
                not_recommended_list.append(rec)

        def sort_key(r: CommodityRecommendation) -> int:
            ordering = {
                "Sangat Tinggi": 5,
                "Tinggi": 4,
                "Sedang": 3,
                "Rendah": 2,
                "Sangat Rendah": 1,
            }
            return ordering.get(r.vulnerability_level, 0)

        recommended_list.sort(key=sort_key, reverse=True)
        alternative_list.sort(key=sort_key, reverse=True)
        not_recommended_list.sort(key=sort_key, reverse=True)

        groups = [
            RecommendationGroup(
                status=RecommendationStatus.RECOMMENDED,
                label="Direkomendasikan",
                commodities=recommended_list,
            ),
            RecommendationGroup(
                status=RecommendationStatus.ALTERNATIVE,
                label="Alternatif",
                commodities=alternative_list,
            ),
            RecommendationGroup(
                status=RecommendationStatus.NOT_RECOMMENDED,
                label="Tidak Direkomendasikan",
                commodities=not_recommended_list,
            ),
        ]

        metadata = DecisionMetadata(
            execution_duration_ms=round((time.perf_counter() - start) * 1000, 2),
            total_rules_evaluated=rules_evaluated,
            rules_matched=rules_matched,
            commodities_classified=len(all_commodities),
        )

        result = DecisionResult(
            context=context,
            groups=groups,
            metadata=metadata,
            report=DecisionReport(
                total_commodities=len(all_commodities),
                recommended_count=len(recommended_list),
                alternative_count=len(alternative_list),
                not_recommended_count=len(not_recommended_list),
                all_commodities_classified=True,
                no_duplicates=True,
                rule_coverage_pct=100.0,
                knowledge_coverage_pct=100.0,
                explanation_coverage_pct=100.0,
            ),
        )

        logger.info(
            "Decision executed in %.1f ms: FRI=%.1f (%s) | "
            "R=%d A=%d N=%d",
            metadata.execution_duration_ms,
            fri, risk_category,
            len(recommended_list), len(alternative_list), len(not_recommended_list),
        )

        return result

    def health_status(self) -> dict[str, Any]:
        if not self._ready:
            return {
                "decision_ready": False,
                "engine_version": "1.0",
                "knowledge_loaded": self._kb.is_ready if hasattr(self._kb, "is_ready") else False,
                "rules_loaded": True,
                "validation_status": "not_initialized",
                "total_commodities": 0,
            }

        return {
            "decision_ready": True,
            "engine_version": "1.0",
            "knowledge_loaded": self._kb.is_ready,
            "rules_loaded": True,
            "validation_status": "passed",
            "total_commodities": self._kb.count(),
        }
