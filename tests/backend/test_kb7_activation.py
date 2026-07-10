"""Sprint KB7 runtime activation tests."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from starlette.requests import Request

from backend.decision.models import (
    CommodityRecommendation,
    DecisionContext,
    DecisionMetadata,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
)
from backend.providers.models import RawWeatherData
from backend.schemas.request import PrediksiEngineeredRequest, PrediksiManualRequest
from backend.services.recommendation_gateway import augment_with_knowledge
from backend.services.recommendation_mapper import to_knowledge_recommendation


@pytest.fixture
def decision_result() -> DecisionResult:
    commodity = CommodityRecommendation(
        commodity_id="kangkung_air",
        commodity_name="Kangkung Air",
        recommendation_status=RecommendationStatus.RECOMMENDED,
        vulnerability_level="Sangat Tinggi",
        maximum_inundation_duration=">7 hari",
        main_impacts=["Adaptif terhadap genangan"],
        major_impacts=["Adaptif terhadap genangan"],
        damage_symptoms=["Tidak ada gejala kerusakan berarti"],
        recommendation_reason="Cocok untuk area rawan banjir.",
        knowledge_reference="Ref A",
    )
    return DecisionResult(
        context=DecisionContext.create(50.0),
        groups=[
            RecommendationGroup(
                status=RecommendationStatus.RECOMMENDED,
                label="Direkomendasikan",
                commodities=[commodity],
            ),
            RecommendationGroup(
                status=RecommendationStatus.ALTERNATIVE,
                label="Alternatif",
                commodities=[],
            ),
            RecommendationGroup(
                status=RecommendationStatus.NOT_RECOMMENDED,
                label="Tidak Direkomendasikan",
                commodities=[],
            ),
        ],
        metadata=DecisionMetadata(execution_duration_ms=0.2, total_rules_evaluated=1),
        report=DecisionReport(
            total_commodities=1,
            recommended_count=1,
            alternative_count=0,
            not_recommended_count=0,
            all_commodities_classified=True,
            no_duplicates=True,
            rule_coverage_pct=100.0,
            knowledge_coverage_pct=100.0,
            explanation_coverage_pct=100.0,
        ),
    )


@pytest.fixture
def request_with_service(decision_result):
    service = MagicMock()
    service.is_ready = True
    service.recommend.return_value = decision_result
    app = SimpleNamespace(state=SimpleNamespace(recommendation_service=service))
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
            "app": app,
        }
    )


def base_prediction() -> dict:
    return {
        "model": "rf",
        "fri": 50.0,
        "tingkat_risiko": "Risiko Sedang",
        "rekomendasi": [],
        "mitigasi": [],
        "_features": {"RR": 10.0, "Rain7": 70.0, "RH_avg": 80.0, "Tavg": 27.0},
    }


def test_feature_flag_off_returns_legacy(monkeypatch, request_with_service):
    monkeypatch.setattr(
        "backend.services.recommendation_gateway.is_knowledge_recommendation_enabled",
        lambda: False,
    )
    base = base_prediction()

    result = augment_with_knowledge(50.0, "Risiko Sedang", 5, base, request_with_service)

    assert result is base
    assert "knowledge_recommendation" not in result
    assert "knowledge_source" not in result


def test_feature_flag_on_generates_knowledge(monkeypatch, request_with_service):
    monkeypatch.setattr(
        "backend.services.recommendation_gateway.is_knowledge_recommendation_enabled",
        lambda: True,
    )

    result = augment_with_knowledge(
        50.0, "Risiko Sedang", 5, base_prediction(), request_with_service
    )

    assert "knowledge_recommendation" in result
    assert "knowledge_source" in result
    assert result["knowledge_recommendation"]["recommended"][0]["komoditas_id"] == "kangkung_air"


def test_mapper_uses_frontend_contract(decision_result):
    result = to_knowledge_recommendation(decision_result)
    item = result["recommended"][0]

    assert "main_impacts" in item
    assert "damage_symptoms" in item
    assert "maximum_inundation_duration" in item
    assert item["komoditas"] == "Kangkung Air"
    assert item["max_inundation"] == ">7 hari"
    assert item["impacts"] == ["Adaptif terhadap genangan"]


def test_manual_endpoint_includes_knowledge(monkeypatch, request_with_service):
    from backend.routers import prediction

    monkeypatch.setattr(
        "backend.services.recommendation_gateway.is_knowledge_recommendation_enabled",
        lambda: True,
    )
    monkeypatch.setattr(prediction, "predict_from_raw", lambda *args, **kwargs: base_prediction())

    response = prediction.predict_manual(
        request_with_service,
        PrediksiManualRequest(
            tanggal="2026-07-08", rr=10, rh_avg=80, tmax=32, tmin=24, top_n=5
        ),
        object(),
    )

    assert response.knowledge_recommendation is not None
    assert response.knowledge_source is not None


def test_engineered_endpoint_includes_knowledge(monkeypatch, request_with_service):
    from backend.routers import prediction

    monkeypatch.setattr(
        "backend.services.recommendation_gateway.is_knowledge_recommendation_enabled",
        lambda: True,
    )
    monkeypatch.setattr(prediction, "run_prediction", lambda *args, **kwargs: base_prediction())

    response = prediction.predict_engineered(
        request_with_service,
        PrediksiEngineeredRequest(
            rr=10,
            rain3=30,
            rain7=70,
            rain14=100,
            rh_avg=80,
            temp_range=8,
            rainfall_anomaly=50,
            month=7,
            day_of_year=190,
            top_n=5,
        ),
        object(),
    )

    assert response.knowledge_recommendation is not None
    assert response.knowledge_source is not None


def test_realtime_endpoint_includes_knowledge(monkeypatch, request_with_service):
    from backend.routers import realtime

    weather = RawWeatherData(
        tanggal=date(2026, 7, 8),
        rr=10,
        rh_avg=80,
        tmax=32,
        tmin=24,
        latitude=0.5,
        longitude=101.4,
        sumber="test",
    )

    monkeypatch.setattr(
        "backend.services.recommendation_gateway.is_knowledge_recommendation_enabled",
        lambda: True,
    )
    monkeypatch.setattr(realtime._provider, "get_weather_history", lambda *args, **kwargs: [weather])
    monkeypatch.setattr(realtime, "predict_from_raw", lambda *args, **kwargs: base_prediction())

    response = realtime.predict_realtime(
        request_with_service,
        object(),
        wilayah="Pekanbaru",
        model="rf",
        top_n=5,
    )

    assert response["knowledge_recommendation"] is not None
    assert response["knowledge_source"] is not None


@pytest.mark.asyncio
async def test_csv_endpoint_includes_knowledge(monkeypatch, request_with_service):
    from backend.routers import csv_prediction

    class Upload:
        filename = "test.csv"

        async def read(self):
            return b"tanggal,rr,rh_avg,tmax,tmin\n2026-07-07,5,80,31,24\n2026-07-08,10,82,32,24\n"

    monkeypatch.setattr(
        "backend.services.recommendation_gateway.is_knowledge_recommendation_enabled",
        lambda: True,
    )
    monkeypatch.setattr(csv_prediction, "predict_from_raw", lambda *args, **kwargs: base_prediction())

    response = await csv_prediction.predict_csv(request_with_service, object(), Upload())

    assert response["knowledge_recommendation"] is not None
    assert response["knowledge_source"] is not None
