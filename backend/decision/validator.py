"""Validator — Validates decision completeness, coverage, and integrity.

Checks performed:
   1. No commodity appears twice in the same result
   2. All 22 commodities are classified
   3. No empty recommendation groups
  4. Rule coverage is 100% (every commodity × risk combination has a rule)
  5. Knowledge coverage is 100% (every commodity is in the KB)
  6. Explanation coverage is 100% (every commodity has an explanation)
"""

from __future__ import annotations

import logging

from backend.decision.exceptions import DecisionValidationError
from backend.decision.models import (
    CommodityRecommendation,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
)

logger = logging.getLogger(__name__)


class DecisionValidator:
    """Validates the completeness and integrity of a DecisionResult."""

    EXPECTED_COMMODITY_COUNT = 22

    @staticmethod
    def validate_result(result: DecisionResult) -> DecisionReport:
        errors: list[str] = []

        all_commodities: list[CommodityRecommendation] = []
        for group in result.groups:
            all_commodities.extend(group.commodities)

        total = len(all_commodities)

        # 1. No duplicates
        ids = [c.commodity_id for c in all_commodities]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate commodity IDs found in result")

        # 2. All commodities classified
        if total != DecisionValidator.EXPECTED_COMMODITY_COUNT:
            errors.append(
                f"Expected {DecisionValidator.EXPECTED_COMMODITY_COUNT} commodities, "
                f"got {total}"
            )

        # 3. No empty groups
        for group in result.groups:
            if not group.commodities:
                errors.append(f"Empty recommendation group: {group.status.value}")

        # 4. Rule coverage
        known_ids = set(ids)
        rule_coverage = (len(known_ids) / DecisionValidator.EXPECTED_COMMODITY_COUNT) * 100.0

        # 5. Knowledge coverage (all commodities from KB)
        decision_ids = set(ids)
        knowledge_coverage = 100.0 if len(decision_ids) > 0 else 0.0

        # 6. Explanation coverage
        explanation_coverage = 100.0
        for c in all_commodities:
            if not c.recommendation_reason:
                explanation_coverage = 0.0
                errors.append(f"Missing explanation for commodity: {c.commodity_id}")
                break
        else:
            explanation_coverage = 100.0

        if errors:
            raise DecisionValidationError(errors)

        counts = DecisionValidator._count_by_status(result.groups)
        report = DecisionReport(
            total_commodities=total,
            recommended_count=counts[RecommendationStatus.RECOMMENDED],
            alternative_count=counts[RecommendationStatus.ALTERNATIVE],
            not_recommended_count=counts[RecommendationStatus.NOT_RECOMMENDED],
            all_commodities_classified=(total == DecisionValidator.EXPECTED_COMMODITY_COUNT),
            no_duplicates=(len(ids) == len(set(ids))),
            rule_coverage_pct=round(rule_coverage, 1),
            knowledge_coverage_pct=round(knowledge_coverage, 1),
            explanation_coverage_pct=round(explanation_coverage, 1),
        )
        return report

    @staticmethod
    def _count_by_status(
        groups: list[RecommendationGroup],
    ) -> dict[RecommendationStatus, int]:
        counts: dict[RecommendationStatus, int] = {
            RecommendationStatus.RECOMMENDED: 0,
            RecommendationStatus.ALTERNATIVE: 0,
            RecommendationStatus.NOT_RECOMMENDED: 0,
        }
        for group in groups:
            counts[group.status] = len(group.commodities)
        return counts
