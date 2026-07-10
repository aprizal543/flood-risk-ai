"""Mapper — Converts FRI values to risk categories and maps KB attributes.

This module is the bridge between numerical FRI predictions and
the categorical decision rules in the Rule Engine.
"""

from __future__ import annotations

from backend.decision.models import DecisionContext, RiskCategory
from backend.knowledge.models import CommodityKnowledge


class RiskMapper:
    """Maps FRI values to risk categories and commodity attributes."""

    @staticmethod
    def to_risk_category(fri: float) -> RiskCategory:
        return RiskCategory.from_fri(fri)

    @staticmethod
    def to_risk_level_str(fri: float) -> str:
        return RiskCategory.from_fri(fri).value

    @staticmethod
    def vulnerability_ordinal(level: str) -> int:
        mapping = {
            "Sangat Tinggi": 5,
            "Tinggi": 4,
            "Sedang": 3,
            "Rendah": 2,
            "Sangat Rendah": 1,
        }
        return mapping.get(level, 0)

    @staticmethod
    def risk_ordinal(category: str) -> int:
        return RiskCategory.ordinal(category)

    @staticmethod
    def commodity_to_dict(c: CommodityKnowledge) -> dict:
        return {
            "commodity_id": c.commodity_id,
            "commodity_name": c.commodity_name,
            "commodity_category": c.commodity_category,
            "vulnerability_level": c.vulnerability_level,
            "flood_tolerance_category": c.flood_tolerance_category,
            "maximum_inundation_duration": c.maximum_inundation_duration,
            "drainage_requirement": c.drainage_requirement,
            "growing_duration_days": c.growing_duration_days,
            "optimal_risk_level": c.optimal_risk_level,
            "economic_priority": c.economic_priority,
            "main_impacts": list(c.main_impacts),
            "major_impacts": list(c.major_impacts),
            "damage_symptoms": list(c.damage_symptoms),
            "scientific_reference": c.scientific_reference,
        }

    @staticmethod
    def create_context(fri: float) -> DecisionContext:
        return DecisionContext.create(fri)
