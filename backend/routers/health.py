"""Health check endpoint and cache diagnostics.

Additively extended with Knowledge Base status during Sprint KB2,
Decision Engine status during Sprint KB3,
and Recommendation Engine status during Sprint KB4.
No breaking changes to existing response structure.
"""

from fastapi import APIRouter, Request

from backend.providers.geocoding import geocoding_cache, geocoding_metrics
from backend.providers.openmeteo_provider import forecast_cache, forecast_metrics
from backend.schemas.response import (
    HealthResponse,
    KnowledgeHealthResponse,
    DecisionEngineHealthResponse,
    KnowledgeEngineHealth,
    RecommendationEngineHealth,
)
from backend.services.recommendation_gateway import get_active_engine, is_knowledge_active

router = APIRouter(tags=["Health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Status kesehatan API",
    description="Memeriksa apakah layanan API berjalan dengan baik. "
                "Termasuk status Knowledge Base, Decision Engine, dan Recommendation Engine.",
)
def health_check(request: Request) -> HealthResponse:
    startup = getattr(request.app.state, "startup", None)
    ready = startup.is_ready if startup else False
    feature_flag = is_knowledge_active()

    # Knowledge Base status (additive)
    kb = getattr(request.app.state, "knowledge_base", None)
    kb_health = None
    if kb is not None:
        status = kb.health_status() if hasattr(kb, "health_status") else {}
        kb_health = KnowledgeHealthResponse(
            knowledge_ready=status.get("knowledge_ready", False),
            knowledge_version=status.get("knowledge_version"),
            commodity_count=status.get("commodity_count", 0),
            validation_status=status.get("validation_status", "unknown"),
        )

    # Decision Engine status (additive)
    de = getattr(request.app.state, "decision_engine", None)
    de_health = None
    if de is not None:
        d_status = de.health_status() if hasattr(de, "health_status") else {}
        de_health = DecisionEngineHealthResponse(
            decision_ready=d_status.get("decision_ready", False),
            engine_version=d_status.get("engine_version", "1.0"),
            rules_loaded=d_status.get("rules_loaded", False),
            validation_status=d_status.get("validation_status", "not_initialized"),
            total_commodities=d_status.get("total_commodities", 0),
            feature_flag_active=feature_flag,
        )

    # Recommendation Engine status (additive, Sprint KB4)
    de_ready = de_health.decision_ready if de_health else False
    rs = getattr(request.app.state, "recommendation_service", None)
    rs_ready = bool(getattr(rs, "is_ready", False))
    kb_ready = kb_health.knowledge_ready if kb_health else False
    rec_engine = RecommendationEngineHealth(
        active_engine=get_active_engine(),
        feature_flag_active=feature_flag,
        knowledge_engine_version="1.0",
        decision_engine_ready=de_ready,
        recommendation_service_ready=rs_ready,
        knowledge_dataset_ready=kb_ready,
        knowledge_dataset_version=kb_health.knowledge_version if kb_health else None,
        knowledge_dataset_commodities=kb_health.commodity_count if kb_health else 0,
    )

    knowledge_engine = KnowledgeEngineHealth(
        status="enabled" if feature_flag and de_ready and rs_ready and kb_ready else "disabled",
        feature_flag=feature_flag,
        active_engine=get_active_engine(),
        decision_engine="ready" if de_ready else "not_ready",
        recommendation_service="ready" if rs_ready else "not_ready",
        knowledge_dataset="loaded" if kb_ready else "not_loaded",
        knowledge_dataset_version=kb_health.knowledge_version if kb_health else None,
        knowledge_dataset_commodities=kb_health.commodity_count if kb_health else 0,
    )

    return HealthResponse(
        status="sehat",
        versi="1.0.0",
        ready=ready,
        decision_engine=de_health,
        recommendation_engine=rec_engine,
        knowledge=kb_health,
        knowledge_engine=knowledge_engine,
    )


@router.get(
    "/api/system/cache",
    summary="Cache diagnostics",
    description="Returns hit/miss metrics and current size for geocoding and forecast caches.",
)
def cache_diagnostics() -> dict:
    return {
        "geocoding": {
            **geocoding_metrics.snapshot(),
            "entries": geocoding_cache.size,
            "maxsize": geocoding_cache.maxsize,
            "ttl_seconds": geocoding_cache.ttl,
        },
        "forecast": {
            **forecast_metrics.snapshot(),
            "entries": forecast_cache.size,
            "maxsize": forecast_cache.maxsize,
            "ttl_seconds": forecast_cache.ttl,
        },
    }
