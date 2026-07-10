"""Integration tests for the full Decision Engine pipeline."""

from __future__ import annotations


from backend.decision import (
    DecisionEngine,
)
from backend.decision.models import RecommendationStatus


class TestFullDecisionPipeline:
    def test_complete_pipeline(self, recommendation_service):
        result = recommendation_service.recommend(55.0)
        assert result.context.fri == 55.0
        assert result.context.risk_category.value == "Sedang"
        assert len(result.groups) == 3

        recs = result.recommended
        alts = result.alternative
        nots = result.not_recommended

        assert len(recs) + len(alts) + len(nots) == 22

        for c in recs:
            assert c.recommendation_status == RecommendationStatus.RECOMMENDED
        for c in alts:
            assert c.recommendation_status == RecommendationStatus.ALTERNATIVE
        for c in nots:
            assert c.recommendation_status == RecommendationStatus.NOT_RECOMMENDED

    def test_every_commodity_has_complete_data(self, recommendation_service):
        result = recommendation_service.recommend(45.0)
        for g in result.groups:
            for c in g.commodities:
                assert c.commodity_id
                assert c.commodity_name
                assert c.recommendation_status
                assert c.vulnerability_level
                assert c.maximum_inundation_duration
                assert c.recommendation_reason
                assert c.knowledge_reference

    def test_recommendation_count_by_risk_level(self, recommendation_service):
        low = recommendation_service.recommend(20.0)
        mid = recommendation_service.recommend(50.0)
        high = recommendation_service.recommend(80.0)

        assert len(low.recommended) >= len(mid.recommended)
        assert len(mid.recommended) >= len(high.recommended)
        assert len(high.not_recommended) >= len(low.not_recommended)

    def test_specific_commodities_at_low_risk(self, recommendation_service):
        result = recommendation_service.recommend(20.0)
        rec_ids = {c.commodity_id for c in result.recommended}
        not_ids = {c.commodity_id for c in result.not_recommended}

        assert "kangkung_air" in rec_ids
        assert "talas" in rec_ids
        assert "cabai" in not_ids or "tomat" in not_ids

    def test_specific_commodities_at_high_risk(self, recommendation_service):
        result = recommendation_service.recommend(85.0)
        rec_ids = {c.commodity_id for c in result.recommended}
        alt_ids = {c.commodity_id for c in result.alternative}
        not_ids = {c.commodity_id for c in result.not_recommended}

        assert "kangkung_air" in rec_ids
        assert "talas" in alt_ids
        assert "cabai" in not_ids
        assert "tomat" in not_ids

    def test_metadata_populated(self, recommendation_service):
        result = recommendation_service.recommend(50.0)
        meta = result.metadata
        assert meta.execution_duration_ms > 0
        assert meta.total_rules_evaluated == 22
        assert meta.rules_matched == 22
        assert meta.commodities_classified == 22

    def test_report_generated(self, recommendation_service):
        result = recommendation_service.recommend(50.0)
        report = result.report
        assert report.total_commodities == 22
        assert report.all_commodities_classified is True
        assert report.no_duplicates is True
        assert report.rule_coverage_pct == 100.0
        assert report.knowledge_coverage_pct == 100.0
        assert report.explanation_coverage_pct == 100.0

    def test_decision_engine_independent_from_ml(self):
        assert DecisionEngine is not None


class TestRuleCoverage:
    def test_all_vulnerability_levels_covered(self, decision_engine):
        known_levels = {"Sangat Tinggi", "Tinggi", "Sedang", "Rendah", "Sangat Rendah"}
        kb = decision_engine._kb
        kb_levels = set(kb.list_vulnerability_levels())
        assert kb_levels.issubset(known_levels)

    def test_all_risk_levels_produce_valid_results(self, recommendation_service):
        for fri in [0, 33, 34, 66, 67, 100]:
            result = recommendation_service.recommend(float(fri))
            total = sum(len(g.commodities) for g in result.groups)
            assert total == 22, f"FRI={fri} failed"
