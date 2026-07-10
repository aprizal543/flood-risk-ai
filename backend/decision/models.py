"""Strongly-typed data models for the Decision Engine.

All models use Pydantic BaseModel with frozen=True.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RecommendationStatus(str, Enum):
    RECOMMENDED = "recommended"
    ALTERNATIVE = "alternative"
    NOT_RECOMMENDED = "not_recommended"


class RiskCategory(str, Enum):
    RENDAH = "Rendah"
    SEDANG = "Sedang"
    TINGGI = "Tinggi"

    @classmethod
    def from_fri(cls, fri: float) -> RiskCategory:
        if fri <= 33.0:
            return cls.RENDAH
        if fri <= 66.0:
            return cls.SEDANG
        return cls.TINGGI

    @classmethod
    def ordinal(cls, category: str) -> int:
        mapping = {"Rendah": 1, "Sedang": 2, "Tinggi": 3}
        return mapping.get(category, 0)


class DecisionContext(BaseModel, frozen=True):
    fri: float = Field(..., ge=0.0, le=100.0)
    risk_category: RiskCategory
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def create(cls, fri: float) -> DecisionContext:
        return cls(fri=fri, risk_category=RiskCategory.from_fri(fri))


class DecisionRule(BaseModel, frozen=True):
    rule_id: str
    description: str
    condition: str
    status: RecommendationStatus
    priority: int = Field(ge=1, le=100)


class CommodityRecommendation(BaseModel, frozen=True):
    commodity_id: str
    commodity_name: str
    recommendation_status: RecommendationStatus
    vulnerability_level: str
    maximum_inundation_duration: str
    main_impacts: list[str]
    major_impacts: list[str]
    damage_symptoms: list[str]
    recommendation_reason: str
    knowledge_reference: str


class RecommendationGroup(BaseModel, frozen=True):
    status: RecommendationStatus
    label: str
    commodities: list[CommodityRecommendation]


class DecisionMetadata(BaseModel, frozen=True):
    engine_version: str = "1.0"
    decision_timestamp: datetime = Field(default_factory=datetime.now)
    execution_duration_ms: float = 0.0
    total_rules_evaluated: int = 0
    rules_matched: int = 0
    commodities_classified: int = 0
    knowledge_version: str | None = None
    validation_status: str = "passed"


class DecisionReport(BaseModel, frozen=True):
    total_commodities: int
    recommended_count: int
    alternative_count: int
    not_recommended_count: int
    all_commodities_classified: bool
    no_duplicates: bool
    rule_coverage_pct: float
    knowledge_coverage_pct: float
    explanation_coverage_pct: float


class DecisionResult(BaseModel, frozen=True):
    context: DecisionContext
    groups: list[RecommendationGroup]
    metadata: DecisionMetadata
    report: DecisionReport

    def get_group(self, status: RecommendationStatus) -> RecommendationGroup | None:
        for g in self.groups:
            if g.status == status:
                return g
        return None

    @property
    def recommended(self) -> list[CommodityRecommendation]:
        group = self.get_group(RecommendationStatus.RECOMMENDED)
        return group.commodities if group else []

    @property
    def alternative(self) -> list[CommodityRecommendation]:
        group = self.get_group(RecommendationStatus.ALTERNATIVE)
        return group.commodities if group else []

    @property
    def not_recommended(self) -> list[CommodityRecommendation]:
        group = self.get_group(RecommendationStatus.NOT_RECOMMENDED)
        return group.commodities if group else []


class DecisionEngineHealth(BaseModel, frozen=True):
    ready: bool
    engine_version: str = "1.0"
    knowledge_loaded: bool = False
    rules_loaded: bool = False
    validation_status: str = "not_validated"
    total_commodities: int = 0
    errors: list[str] = Field(default_factory=list)


class InferenceRule(BaseModel, frozen=True):
    rule_id: str
    description: str
    condition_vulnerability: str | None = None
    condition_risk: str | None = None
    status: RecommendationStatus
    priority: int = 50
    reason_template: str

    def matches(self, vulnerability_level: str, risk_category: str) -> bool:
        if self.condition_vulnerability and self.condition_vulnerability != vulnerability_level:
            return False
        if self.condition_risk and self.condition_risk != risk_category:
            return False
        return True
