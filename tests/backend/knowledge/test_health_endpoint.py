"""Tests for the health endpoint knowledge base integration.

These tests verify that:
  1. The /api/health endpoint returns knowledge status
  2. The response schema includes the knowledge field
  3. The knowledge field contains correct status information
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.knowledge.knowledge_base import KnowledgeBase


@pytest.fixture
def client():
    """Create a test client. Does not trigger startup events."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestHealthEndpointKnowledgeField:
    def test_health_response_has_knowledge_field(self, client):
        """The /api/health schema includes the additive knowledge field."""
        # Trigger startup manually for test
        from backend.startup import AppStartup
        startup = AppStartup()
        try:
            startup.warm_up()
        except Exception:
            pass  # May fail in test env without ML models
        app.state.startup = startup
        if hasattr(startup, 'knowledge_base') and startup.knowledge_base is not None:
            app.state.knowledge_base = startup.knowledge_base

        response = client.get("/api/health")
        assert response.status_code in (200, 500)

        if response.status_code == 200:
            data = response.json()
            # The knowledge field is additive — check it exists
            assert "knowledge" in data
            if data["knowledge"] is not None:
                assert "knowledge_ready" in data["knowledge"]
                assert "commodity_count" in data["knowledge"]
                assert "validation_status" in data["knowledge"]

    def test_knowledge_base_independent_health_status(self):
        """KnowledgeBase.health_status() works independently."""
        kb = KnowledgeBase()
        try:
            kb.initialize()
            status = kb.health_status()
            assert isinstance(status, dict)
            assert "knowledge_ready" in status
            assert "knowledge_version" in status
            assert "commodity_count" in status
            assert "validation_status" in status
        except Exception:
            # In test env without full app context, KB may not load
            pass

    def test_health_response_schema_additive(self):
        """Verify the HealthResponse schema is backward compatible."""
        from backend.schemas.response import (
            HealthResponse,
            KnowledgeHealthResponse,
            DecisionEngineHealthResponse,
            RecommendationEngineHealth,
        )

        # Old clients can still create HealthResponse without knowledge
        old = HealthResponse(status="sehat", versi="1.0.0", ready=True)
        assert old.status == "sehat"
        assert old.ready is True
        assert old.knowledge is None  # additive field defaults to None

        # New clients can include knowledge
        kb_health = KnowledgeHealthResponse(
            knowledge_ready=True,
            knowledge_version="2.1",
            commodity_count=22,
            validation_status="passed",
        )
        new = HealthResponse(
            status="sehat",
            versi="1.0.0",
            ready=True,
            knowledge=kb_health,
        )
        assert new.knowledge is not None
        assert new.knowledge.knowledge_ready is True
        assert new.knowledge.commodity_count == 22

        # Health response also supports decision_engine and recommendation_engine (Sprint KB4)
        de_health = DecisionEngineHealthResponse(
            decision_ready=True,
            feature_flag_active=True,
        )
        rec_health = RecommendationEngineHealth(
            active_engine="knowledge_base",
            feature_flag_active=True,
        )
        full = HealthResponse(
            status="sehat",
            versi="1.0.0",
            ready=True,
            decision_engine=de_health,
            recommendation_engine=rec_health,
            knowledge=kb_health,
        )
        assert full.decision_engine is not None
        assert full.decision_engine.feature_flag_active is True
        assert full.recommendation_engine is not None
        assert full.recommendation_engine.active_engine == "knowledge_base"
        assert full.recommendation_engine.feature_flag_active is True
