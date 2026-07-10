"""Tests for KnowledgeRecommendationService."""

from __future__ import annotations

import pytest

from backend.decision.exceptions import DecisionNotInitializedError
from backend.decision.models import DecisionResult
from backend.knowledge import KnowledgeBase


class TestKnowledgeRecommendationService:
    def test_recommend_returns_decision_result(self, recommendation_service):
        result = recommendation_service.recommend(50.0)
        assert isinstance(result, DecisionResult)
        assert result.context.fri == 50.0

    def test_recommend_all_risk_levels(self, recommendation_service):
        for fri in [10, 50, 90]:
            result = recommendation_service.recommend(float(fri))
            total = sum(len(g.commodities) for g in result.groups)
            assert total == 22

    def test_recommend_as_dict(self, recommendation_service):
        d = recommendation_service.recommend_as_dict(45.0)
        assert d["status"] == "berhasil"
        assert "recommended" in d
        assert "alternative" in d
        assert "not_recommended" in d
        assert "metadata" in d

    def test_is_ready(self, recommendation_service):
        assert recommendation_service.is_ready is True

    def test_health_status(self, recommendation_service):
        status = recommendation_service.health_status()
        assert status["decision_ready"] is True

    def test_low_fri_has_more_recommended(self, recommendation_service):
        low = recommendation_service.recommend(10.0)
        high = recommendation_service.recommend(90.0)
        assert len(low.recommended) >= len(high.recommended)

    def test_not_initialized_raises(self):
        from backend.decision import DecisionEngine, KnowledgeRecommendationService
        kb = KnowledgeBase()
        kb.initialize()
        engine = DecisionEngine(knowledge_base=kb)
        service = KnowledgeRecommendationService(engine)
        with pytest.raises(DecisionNotInitializedError):
            service.recommend(50.0)

    def test_kangkung_always_recommended(self, recommendation_service):
        for fri in [10, 50, 90]:
            result = recommendation_service.recommend(float(fri))
            rec_ids = [c.commodity_id for c in result.recommended]
            assert "kangkung_air" in rec_ids, f"Kangkung Air not recommended at FRI={fri}"


class TestRecommendationServiceIntegration:
    def test_full_dataset_coverage(self, recommendation_service):
        result = recommendation_service.recommend(50.0)
        all_ids = set()
        for g in result.groups:
            for c in g.commodities:
                all_ids.add(c.commodity_id)
        assert len(all_ids) == 22

    def test_explanations_are_indonesian(self, recommendation_service):
        result = recommendation_service.recommend(50.0)
        for g in result.groups:
            for c in g.commodities:
                assert c.recommendation_reason
                assert "  " not in c.recommendation_reason

    def test_no_scoring_fields(self, recommendation_service):
        result = recommendation_service.recommend(50.0)
        for g in result.groups:
            for c in g.commodities:
                assert not hasattr(c, "skor")
                assert not hasattr(c, "score")
                assert not hasattr(c, "confidence")
                assert not hasattr(c, "tingkat_keyakinan")
