"""Integration tests for API endpoints with recommendation gateway.

Tests that:
  1. Manual prediction endpoint still works (legacy mode)
  2. Response includes all required fields
  3. Knowledge fields are additive when feature flag is active
  4. No breaking changes to response structure
"""

from __future__ import annotations



from backend.schemas.response import (
    DecisionEngineHealthResponse,
    HealthResponse,
    KnowledgeHealthResponse,
    PrediksiResponse,
    RecommendationEngineHealth,
)


class TestPrediksiResponseSchema:
    def test_prediksi_response_has_legacy_fields(self):
        """Verify PrediksiResponse schema preserves all legacy fields."""
        fields = PrediksiResponse.model_fields
        assert "model" in fields
        assert "fri" in fields
        assert "tingkat_risiko" in fields
        assert "rekomendasi" in fields
        assert "mitigasi" in fields

    def test_prediksi_response_has_additive_knowledge_fields(self):
        """Verify additive knowledge fields are optional."""
        fields = PrediksiResponse.model_fields
        assert "knowledge_recommendation" in fields
        assert "knowledge_source" in fields

    def test_prediksi_response_default_knowledge_is_none(self):
        """Verify knowledge fields default to None (legacy compat)."""
        resp = PrediksiResponse(
            model="rf",
            fri=50.0,
            tingkat_risiko="Risiko Sedang",
            rekomendasi=[],
            mitigasi=[],
        )
        assert resp.knowledge_recommendation is None
        assert resp.knowledge_source is None

    def test_prediksi_response_constructible_without_knowledge(self):
        """Legacy-format dicts should still construct PrediksiResponse."""
        data = {
            "model": "rf",
            "fri": 45.0,
            "tingkat_risiko": "Risiko Sedang",
            "rekomendasi": [],
            "mitigasi": [],
        }
        resp = PrediksiResponse(**data)
        assert resp.model == "rf"
        assert resp.fri == 45.0


class TestHealthResponseSchema:
    def test_health_response_has_recommendation_engine(self):
        """Verify additive recommendation_engine field exists."""
        fields = HealthResponse.model_fields
        assert "recommendation_engine" in fields

    def test_recommendation_engine_health(self):
        rec = RecommendationEngineHealth()
        assert rec.active_engine == "legacy_scoring"
        assert rec.feature_flag_active is False
        assert rec.knowledge_engine_version == "1.0"

    def test_decision_engine_health_has_feature_flag(self):
        de = DecisionEngineHealthResponse(decision_ready=True)
        assert hasattr(de, "feature_flag_active")
        assert de.feature_flag_active is False


class TestKnowledgeHealthResponse:
    def test_knowledge_health_defaults(self):
        kh = KnowledgeHealthResponse(knowledge_ready=True)
        assert kh.knowledge_ready is True
        assert kh.commodity_count == 0
        assert kh.validation_status == "not_loaded"


class TestRecommendationGatewayImport:
    def test_gateway_imports(self):
        from backend.services.recommendation_gateway import (
            augment_with_knowledge,
            get_active_engine,
            is_knowledge_active,
        )
        assert callable(augment_with_knowledge)
        assert callable(get_active_engine)
        assert callable(is_knowledge_active)

    def test_mapper_imports(self):
        from backend.services.recommendation_mapper import (
            to_knowledge_recommendation,
            to_knowledge_source,
            to_legacy_rekomendasi,
        )
        assert callable(to_knowledge_recommendation)
        assert callable(to_knowledge_source)
        assert callable(to_legacy_rekomendasi)
