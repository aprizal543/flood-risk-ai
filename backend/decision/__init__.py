"""Decision Engine — Knowledge-Based Decision Engine for commodity recommendation.

Replaces the legacy scoring-based recommendation with a deterministic,
rule-based engine driven by the Knowledge Base.
"""

from backend.decision.engine import DecisionEngine
from backend.decision.exceptions import (
    DecisionEngineError,
    DecisionNotInitializedError,
    DecisionRuleError,
    DecisionValidationError,
)
from backend.decision.mapper import RiskMapper
from backend.decision.models import (
    CommodityRecommendation,
    DecisionContext,
    DecisionMetadata,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
    RiskCategory,
)
from backend.decision.recommendation_service import KnowledgeRecommendationService
from backend.decision.rules import InferenceRuleEngine
from backend.decision.validator import DecisionValidator

__all__ = [
    "DecisionEngine",
    "DecisionEngineError",
    "DecisionNotInitializedError",
    "DecisionRuleError",
    "DecisionValidationError",
    "RiskMapper",
    "CommodityRecommendation",
    "DecisionContext",
    "DecisionMetadata",
    "DecisionReport",
    "DecisionResult",
    "RecommendationGroup",
    "RecommendationStatus",
    "RiskCategory",
    "KnowledgeRecommendationService",
    "InferenceRuleEngine",
    "DecisionValidator",
]
