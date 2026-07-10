"""Shared fixtures for Decision Engine tests."""

from __future__ import annotations

import pytest

from backend.decision import (
    DecisionEngine,
    InferenceRuleEngine,
    KnowledgeRecommendationService,
)
from backend.knowledge import KnowledgeBase


@pytest.fixture(scope="session")
def knowledge_base() -> KnowledgeBase:
    kb = KnowledgeBase()
    kb.initialize()
    return kb


@pytest.fixture(scope="session")
def rule_engine() -> InferenceRuleEngine:
    return InferenceRuleEngine()


@pytest.fixture(scope="session")
def decision_engine(knowledge_base: KnowledgeBase) -> DecisionEngine:
    engine = DecisionEngine(knowledge_base=knowledge_base)
    engine.initialize()
    return engine


@pytest.fixture(scope="session")
def recommendation_service(decision_engine: DecisionEngine) -> KnowledgeRecommendationService:
    return KnowledgeRecommendationService(decision_engine)
