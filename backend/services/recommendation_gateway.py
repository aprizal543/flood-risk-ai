"""recommendation_gateway — Unified gateway for commodity recommendations.

Routes requests to either the Legacy recommendation engine or the
Knowledge-Based Decision Engine based on the USE_KNOWLEDGE_RECOMMENDATION
feature flag.

Endpoints MUST NOT know which engine is active.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Request

from backend.config import is_knowledge_recommendation_enabled
from backend.decision.models import DecisionResult
from backend.services.recommendation_mapper import (
    to_knowledge_recommendation,
    to_knowledge_source,
    to_legacy_rekomendasi,
)

logger = logging.getLogger(__name__)


def augment_with_knowledge(
    fri: float,
    risk_label: str,
    top_n: int,
    base_result: dict[str, Any],
    request: Request,
) -> dict[str, Any]:
    """Augment a base prediction result with knowledge-based recommendation data.

    In legacy mode (feature flag OFF): returns base_result unchanged.
    In KB mode (feature flag ON): adds knowledge_recommendation and
    knowledge_source fields to the response, and replaces the legacy
    rekomendasi with KB-derived data.

    This function is the single seam for all recommendation switching.
    """
    logger.info("KB ENTRY | FRI=%.2f | risk=%s | top_n=%d", fri, risk_label, top_n)

    flag_enabled = is_knowledge_recommendation_enabled()
    logger.info("KB FLAG | enabled=%s", flag_enabled)

    if not flag_enabled:
        logger.info("KB FALLBACK | reason=feature_flag_disabled | engine=legacy_scoring")
        return base_result

    service = getattr(request.app.state, "recommendation_service", None)
    logger.info(
        "KB SERVICE READY | exists=%s | ready=%s | type=%s",
        service is not None,
        getattr(service, "is_ready", None),
        type(service).__name__ if service is not None else None,
    )
    if service is None or not service.is_ready:
        logger.warning("KB FALLBACK | reason=service_unavailable | engine=legacy_scoring")
        return base_result

    try:
        logger.info("KB ENGINE | invoking=KnowledgeRecommendationService.recommend")
        decision_result: DecisionResult = service.recommend(fri)

        augmented = dict(base_result)
        logger.info(
            "KB MAPPER | recommended=%d | alternative=%d | not_recommended=%d",
            len(decision_result.recommended),
            len(decision_result.alternative),
            len(decision_result.not_recommended),
        )
        augmented["rekomendasi"] = to_legacy_rekomendasi(decision_result, fri, top_n)
        augmented["knowledge_recommendation"] = to_knowledge_recommendation(decision_result)
        augmented["knowledge_source"] = to_knowledge_source(decision_result)
        logger.info(
            "KB RESPONSE GENERATED | has_knowledge_recommendation=%s | has_knowledge_source=%s",
            "knowledge_recommendation" in augmented,
            "knowledge_source" in augmented,
        )

        rec_counts = {
            "R": len(decision_result.recommended),
            "A": len(decision_result.alternative),
            "N": len(decision_result.not_recommended),
        }
        logger.info(
            "KB recommendation: FRI=%.1f %s | R=%d A=%d N=%d | %.1fms",
            fri, risk_label,
            rec_counts["R"], rec_counts["A"], rec_counts["N"],
            decision_result.metadata.execution_duration_ms,
        )
        return augmented

    except Exception as e:
        logger.exception("KB FALLBACK | reason=exception | error=%s", e)
        return base_result


def get_active_engine() -> str:
    """Return the name of the currently active recommendation engine."""
    if is_knowledge_recommendation_enabled():
        return "knowledge_base"
    return "legacy_scoring"


def is_knowledge_active() -> bool:
    return is_knowledge_recommendation_enabled()
