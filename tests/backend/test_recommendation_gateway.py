"""Tests for the recommendation gateway and mapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.decision.models import (
    CommodityRecommendation,
    DecisionContext,
    DecisionMetadata,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
)
from backend.services.recommendation_gateway import (
    augment_with_knowledge,
    get_active_engine,
    is_knowledge_active,
)
from backend.services.recommendation_mapper import (
    to_knowledge_recommendation,
    to_knowledge_source,
    to_legacy_rekomendasi,
)


@pytest.fixture
def sample_decision_result() -> DecisionResult:
    c1 = CommodityRecommendation(
        commodity_id="kangkung_air",
        commodity_name="Kangkung Air",
        recommendation_status=RecommendationStatus.RECOMMENDED,
        vulnerability_level="Sangat Tinggi",
        maximum_inundation_duration=">7 hari",
        main_impacts=["Pertumbuhan subur"],
        major_impacts=["Pertumbuhan subur"],
        damage_symptoms=["Tidak ada gejala"],
        recommendation_reason="Sangat toleran terhadap genangan",
        knowledge_reference="FAO guides",
    )
    c2 = CommodityRecommendation(
        commodity_id="kangkung_air",
        commodity_name="Kangkung Air",
        recommendation_status=RecommendationStatus.ALTERNATIVE,
        vulnerability_level="Sangat Tinggi",
        maximum_inundation_duration=">7 hari",
        main_impacts=["A"],
        major_impacts=["A"],
        damage_symptoms=["B"],
        recommendation_reason="Cukup toleran",
        knowledge_reference="Ref B",
    )
    c3 = CommodityRecommendation(
        commodity_id="cabai",
        commodity_name="Cabai",
        recommendation_status=RecommendationStatus.NOT_RECOMMENDED,
        vulnerability_level="Sangat Rendah",
        maximum_inundation_duration="<24 jam",
        main_impacts=["C"],
        major_impacts=["C"],
        damage_symptoms=["D"],
        recommendation_reason="Sangat rentan",
        knowledge_reference="Ref C",
    )
    ctx = DecisionContext.create(50.0)
    meta = DecisionMetadata(execution_duration_ms=3.5, total_rules_evaluated=3)
    report = DecisionReport(
        total_commodities=3, recommended_count=1, alternative_count=1,
        not_recommended_count=1, all_commodities_classified=True,
        no_duplicates=True, rule_coverage_pct=100.0,
        knowledge_coverage_pct=100.0, explanation_coverage_pct=100.0,
    )
    groups = [
        RecommendationGroup(status=RecommendationStatus.RECOMMENDED, label="R", commodities=[c1]),
        RecommendationGroup(status=RecommendationStatus.ALTERNATIVE, label="A", commodities=[c2]),
        RecommendationGroup(status=RecommendationStatus.NOT_RECOMMENDED, label="N", commodities=[c3]),
    ]
    return DecisionResult(context=ctx, groups=groups, metadata=meta, report=report)


class TestRecommendationMapper:
    def test_to_legacy_rekomendasi(self, sample_decision_result):
        recs = to_legacy_rekomendasi(sample_decision_result, fri=50.0, top_n=17)
        assert len(recs) == 3
        assert recs[0]["komoditas_id"] == "kangkung_air"
        assert recs[0]["komoditas"] == "Kangkung Air"
        assert "skor" in recs[0]
        assert "tingkat_keyakinan" in recs[0]
        assert "tingkat_risiko" in recs[0]
        assert "alasan" in recs[0]
        assert "ringkasan" in recs[0]

    def test_to_legacy_rekomendasi_limited(self, sample_decision_result):
        recs = to_legacy_rekomendasi(sample_decision_result, fri=50.0, top_n=2)
        assert len(recs) == 2

    def test_to_knowledge_recommendation(self, sample_decision_result):
        kr = to_knowledge_recommendation(sample_decision_result)
        assert "recommended" in kr
        assert "alternative" in kr
        assert "not_recommended" in kr
        assert len(kr["recommended"]) == 1
        assert len(kr["alternative"]) == 1
        assert len(kr["not_recommended"]) == 1
        assert kr["recommended"][0]["komoditas_id"] == "kangkung_air"
        assert kr["recommended"][0]["komoditas"] == "Kangkung Air"
        assert kr["recommended"][0]["vulnerability"] == "Sangat Tinggi"
        assert kr["recommended"][0]["max_inundation"] == ">7 hari"
        assert kr["recommended"][0]["impacts"] == ["Pertumbuhan subur"]
        assert kr["recommended"][0]["symptoms"] == ["Tidak ada gejala"]
        assert kr["recommended"][0]["reason"] == "Sangat toleran terhadap genangan"
        assert kr["recommended"][0]["source"] == "FAO guides"
        assert kr["alternative"][0]["komoditas_id"] == "kangkung_air"
        assert kr["not_recommended"][0]["komoditas_id"] == "cabai"

    def test_to_knowledge_source(self, sample_decision_result):
        ks = to_knowledge_source(sample_decision_result)
        assert ks["version"] == "1.0"
        assert ks["engine"] == "KB-DSS"
        assert ks["execution_duration_ms"] == 3.5

    def test_to_knowledge_source_none(self):
        ks = to_knowledge_source(None)
        assert ks["version"] == "1.0"
        assert ks["engine"] == "KB-DSS"


class TestRecommendationGateway:
    def test_get_active_engine_default(self):
        engine = get_active_engine()
        assert engine in ("legacy_scoring", "knowledge_base")

    def test_is_knowledge_active(self):
        result = is_knowledge_active()
        assert isinstance(result, bool)

    @patch("backend.services.recommendation_gateway.is_knowledge_recommendation_enabled", lambda: False)
    def test_augment_legacy_mode(self, sample_decision_result):
        request = MagicMock()
        base = {"fri": 50.0, "tingkat_risiko": "Risiko Sedang", "rekomendasi": [], "mitigasi": []}
        result = augment_with_knowledge(50.0, "Risiko Sedang", 5, base, request)
        assert result == base
        assert "knowledge_recommendation" not in result

    @patch("backend.services.recommendation_gateway.is_knowledge_recommendation_enabled", lambda: True)
    def test_augment_kb_mode_no_service(self, sample_decision_result):
        request = MagicMock()
        request.app.state.recommendation_service = None
        base = {"fri": 50.0, "tingkat_risiko": "Risiko Sedang", "rekomendasi": [], "mitigasi": []}
        result = augment_with_knowledge(50.0, "Risiko Sedang", 5, base, request)
        assert "knowledge_recommendation" not in result

    @patch("backend.services.recommendation_gateway.is_knowledge_recommendation_enabled", lambda: True)
    def test_augment_kb_mode_success(self, sample_decision_result):
        mock_service = MagicMock()
        mock_service.is_ready = True
        mock_service.recommend.return_value = sample_decision_result

        request = MagicMock()
        request.app.state.recommendation_service = mock_service

        base = {"fri": 50.0, "tingkat_risiko": "Risiko Sedang", "rekomendasi": [], "mitigasi": []}
        result = augment_with_knowledge(50.0, "Risiko Sedang", 5, base, request)

        assert "knowledge_recommendation" in result
        assert "knowledge_source" in result
        assert result["knowledge_recommendation"]["recommended"][0]["komoditas_id"] == "kangkung_air"
        assert result["knowledge_source"]["engine"] == "KB-DSS"
        assert len(result["rekomendasi"]) == 3

    @patch("backend.services.recommendation_gateway.is_knowledge_recommendation_enabled", lambda: True)
    def test_augment_kb_mode_fallback_on_error(self, sample_decision_result):
        mock_service = MagicMock()
        mock_service.is_ready = True
        mock_service.recommend.side_effect = Exception("Engine error")

        request = MagicMock()
        request.app.state.recommendation_service = mock_service

        base = {"fri": 50.0, "tingkat_risiko": "Risiko Sedang", "rekomendasi": [], "mitigasi": []}
        result = augment_with_knowledge(50.0, "Risiko Sedang", 5, base, request)

        # Should fall back gracefully
        assert "knowledge_recommendation" not in result
        assert result["fri"] == 50.0
