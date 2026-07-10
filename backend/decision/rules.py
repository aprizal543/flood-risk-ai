"""Rule Engine — Deterministic inference rules for commodity recommendation.

All rules are defined as a decision table mapping
(vulnerability_level × risk_category) → RecommendationStatus.

Rules NEVER use heuristic scoring, weights, or ranking scores.
Rules are 100% deterministic.
"""

from __future__ import annotations

import logging
from typing import ClassVar

from backend.decision.exceptions import DecisionRuleError
from backend.decision.models import (
    RecommendationStatus,
)

logger = logging.getLogger(__name__)


class InferenceRuleEngine:
    """Deterministic rule engine for commodity recommendation.

    Uses a decision table that maps vulnerability_level and risk_category
    to one of three recommendation statuses: recommended, alternative, not_recommended.
    """

    STATUS_RECOMMENDED = RecommendationStatus.RECOMMENDED
    STATUS_ALTERNATIVE = RecommendationStatus.ALTERNATIVE
    STATUS_NOT_RECOMMENDED = RecommendationStatus.NOT_RECOMMENDED

    VULN_LEVELS: ClassVar[list[str]] = [
        "Sangat Tinggi", "Tinggi", "Sedang", "Rendah", "Sangat Rendah",
    ]
    RISK_LEVELS: ClassVar[list[str]] = ["Rendah", "Sedang", "Tinggi"]

    DECISION_TABLE: ClassVar[dict[str, dict[str, RecommendationStatus]]] = {
        "Sangat Tinggi": {
            "Rendah": RecommendationStatus.RECOMMENDED,
            "Sedang": RecommendationStatus.RECOMMENDED,
            "Tinggi": RecommendationStatus.RECOMMENDED,
        },
        "Tinggi": {
            "Rendah": RecommendationStatus.RECOMMENDED,
            "Sedang": RecommendationStatus.RECOMMENDED,
            "Tinggi": RecommendationStatus.ALTERNATIVE,
        },
        "Sedang": {
            "Rendah": RecommendationStatus.RECOMMENDED,
            "Sedang": RecommendationStatus.ALTERNATIVE,
            "Tinggi": RecommendationStatus.NOT_RECOMMENDED,
        },
        "Rendah": {
            "Rendah": RecommendationStatus.ALTERNATIVE,
            "Sedang": RecommendationStatus.NOT_RECOMMENDED,
            "Tinggi": RecommendationStatus.NOT_RECOMMENDED,
        },
        "Sangat Rendah": {
            "Rendah": RecommendationStatus.NOT_RECOMMENDED,
            "Sedang": RecommendationStatus.NOT_RECOMMENDED,
            "Tinggi": RecommendationStatus.NOT_RECOMMENDED,
        },
    }

    def __init__(self) -> None:
        self._validate_table()

    def _validate_table(self) -> None:
        for vuln in self.VULN_LEVELS:
            if vuln not in self.DECISION_TABLE:
                raise DecisionRuleError(
                    vuln, f"Missing vulnerability level '{vuln}' in decision table"
                )
            for risk in self.RISK_LEVELS:
                if risk not in self.DECISION_TABLE[vuln]:
                    raise DecisionRuleError(
                        vuln, f"Missing risk category '{risk}' for vulnerability '{vuln}'"
                    )
                status = self.DECISION_TABLE[vuln][risk]
                if not isinstance(status, RecommendationStatus):
                    raise DecisionRuleError(
                        vuln, f"Invalid status '{status}' for {vuln}/{risk}"
                    )
        logger.info(
            "InferenceRuleEngine initialized: %d vulnerability levels × %d risk levels = %d rules",
            len(self.VULN_LEVELS), len(self.RISK_LEVELS),
            len(self.VULN_LEVELS) * len(self.RISK_LEVELS),
        )

    def evaluate(self, vulnerability_level: str, risk_category: str) -> RecommendationStatus:
        vuln_row = self.DECISION_TABLE.get(vulnerability_level)
        if vuln_row is None:
            raise DecisionRuleError(
                vulnerability_level,
                f"Unknown vulnerability level '{vulnerability_level}'",
            )
        status = vuln_row.get(risk_category)
        if status is None:
            raise DecisionRuleError(
                risk_category,
                f"Unknown risk category '{risk_category}' for vulnerability '{vulnerability_level}'",
            )
        return status

    def evaluate_all(
        self,
        vulnerability_levels: list[str],
        risk_category: str,
    ) -> list[tuple[str, RecommendationStatus]]:
        results: list[tuple[str, RecommendationStatus]] = []
        for vuln in vulnerability_levels:
            status = self.evaluate(vuln, risk_category)
            results.append((vuln, status))
        return results

    @property
    def rule_count(self) -> int:
        return len(self.VULN_LEVELS) * len(self.RISK_LEVELS)

    @property
    def is_valid(self) -> bool:
        try:
            self._validate_table()
            return True
        except DecisionRuleError:
            return False

    def get_status_reason(
        self,
        vulnerability_level: str,
        risk_category: str,
        commodity_name: str,
    ) -> str:
        status = self.evaluate(vulnerability_level, risk_category)

        templates = {
            RecommendationStatus.RECOMMENDED: (
                "{name} direkomendasikan untuk ditanam pada kondisi Risiko {risk} "
                "karena memiliki toleransi banjir {vuln} yang sangat sesuai."
            ),
            RecommendationStatus.ALTERNATIVE: (
                "{name} dapat dipertimbangkan sebagai alternatif pada kondisi Risiko {risk} "
                "meskipun toleransi banjirnya {vuln} — perlu pengelolaan drainase yang baik."
            ),
            RecommendationStatus.NOT_RECOMMENDED: (
                "{name} tidak direkomendasikan pada kondisi Risiko {risk} "
                "karena toleransi banjirnya {vuln} dan tidak sesuai dengan tingkat risiko saat ini."
            ),
        }

        template = templates.get(status)
        if template:
            return template.format(
                name=commodity_name,
                risk=risk_category,
                vuln=vulnerability_level.lower(),
            )
        return ""
