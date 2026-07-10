"""Tests for the DecisionEngine."""

from __future__ import annotations

import pytest

from backend.decision.engine import DecisionEngine
from backend.decision.exceptions import (
    DecisionKnowledgeError,
    DecisionNotInitializedError,
)
from backend.decision.models import RecommendationStatus
from backend.knowledge import KnowledgeBase


class TestDecisionEngine:
    def setup_method(self):
        self.kb = KnowledgeBase()
        self.kb.initialize()

    def test_not_ready_by_default(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        assert engine.is_ready is False

    def test_initialize(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        assert engine.is_ready is True

    def test_initialize_fails_without_kb(self):
        empty_kb = KnowledgeBase()
        engine = DecisionEngine(knowledge_base=empty_kb)
        with pytest.raises(DecisionKnowledgeError):
            engine.initialize()

    def test_decide_returns_result(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        result = engine.decide(45.0)
        assert result.context.fri == 45.0
        assert len(result.groups) == 3

    def test_decide_all_commodities_classified(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        result = engine.decide(50.0)
        total = sum(len(g.commodities) for g in result.groups)
        assert total == 22

    def test_decide_no_duplicates(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        result = engine.decide(30.0)
        all_ids = []
        for g in result.groups:
            all_ids.extend(c.commodity_id for c in g.commodities)
        assert len(all_ids) == len(set(all_ids))

    def test_decide_low_risk(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        result = engine.decide(10.0)
        recs = result.recommended
        assert len(recs) > 0

    def test_decide_high_risk(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        result = engine.decide(90.0)
        recs = result.recommended
        non_recs = result.not_recommended
        assert len(recs) > 0
        assert len(non_recs) > 0

    def test_decide_without_initialize_raises(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        with pytest.raises(DecisionNotInitializedError):
            engine.decide(50.0)

    def test_health_status_not_ready(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        status = engine.health_status()
        assert status["decision_ready"] is False

    def test_health_status_ready(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        status = engine.health_status()
        assert status["decision_ready"] is True
        assert status["total_commodities"] == 22

    def test_all_groups_populated(self):
        engine = DecisionEngine(knowledge_base=self.kb)
        engine.initialize()
        result = engine.decide(50.0)
        statuses = {g.status for g in result.groups}
        assert RecommendationStatus.RECOMMENDED in statuses
        assert RecommendationStatus.ALTERNATIVE in statuses
        assert RecommendationStatus.NOT_RECOMMENDED in statuses


class TestDecisionEngineIntegration:
    def test_full_range_of_fri_values(self):
        kb = KnowledgeBase()
        kb.initialize()
        engine = DecisionEngine(knowledge_base=kb)
        engine.initialize()

        for fri in [0, 10, 25, 33, 45, 55, 66, 75, 90, 100]:
            result = engine.decide(float(fri))
            total = sum(len(g.commodities) for g in result.groups)
            assert total == 22, f"FRI={fri}: expected 22 commodities, got {total}"

    def test_each_commodity_has_reason(self):
        kb = KnowledgeBase()
        kb.initialize()
        engine = DecisionEngine(knowledge_base=kb)
        engine.initialize()
        result = engine.decide(50.0)
        for g in result.groups:
            for c in g.commodities:
                assert c.recommendation_reason, f"{c.commodity_id} has no reason"
                assert c.knowledge_reference, f"{c.commodity_id} has no reference"
