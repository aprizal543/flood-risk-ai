"""recommendation_mapper — Transforms DecisionResult between response formats.

Mapping responsibilities:
  DecisionResult → Legacy-compatible rekomendasi (PenjelasanResponse format)
  DecisionResult → Knowledge recommendation groups (additive)
  DecisionResult → Knowledge source metadata (additive)
"""

from __future__ import annotations

from backend.decision.models import DecisionResult, RecommendationStatus


def to_legacy_rekomendasi(
    result: DecisionResult,
    fri: float,
    top_n: int = 17,
) -> list[dict]:
    """Map a DecisionResult to legacy-compatible rekomendasi list.

    Preserves the legacy PenjelasanResponse shape so existing frontends
    continue to work without changes.

    Legacy format:
      {
        "komoditas": str,
        "komoditas_id": str,
        "skor": float,
        "tingkat_keyakinan": float,
        "tingkat_risiko": str,
        "alasan": list[str],
        "ringkasan": str,
      }
    """
    from backend.decision.mapper import RiskMapper

    risk_category = result.context.risk_category.value
    tingkat_risiko = f"Risiko {risk_category}"

    # Gather all commodities ordered: recommended → alternative → not_recommended
    all_commodities = []
    for group in result.groups:
        all_commodities.extend(group.commodities)

    # Use an ordinal-based "score" for sorting (legacy field — not a real score)
    vuln_ordinal = RiskMapper.vulnerability_ordinal

    rekomendasi = []
    for i, c in enumerate(all_commodities):
        if i >= top_n:
            break

        base_ordinal = vuln_ordinal(c.vulnerability_level)
        # Legacy-compatible skor: ordinal-based (not a real score)
        skor = round((base_ordinal / 5.0) * 100, 1)

        alasan = [c.recommendation_reason]
        ringkasan = c.recommendation_reason

        rekomendasi.append({
            "komoditas": c.commodity_name,
            "komoditas_id": c.commodity_id,
            "skor": skor,
            "tingkat_keyakinan": round(skor, 1),
            "tingkat_risiko": tingkat_risiko,
            "alasan": alasan,
            "ringkasan": ringkasan,
        })

    return rekomendasi


def to_knowledge_recommendation(result: DecisionResult) -> dict:
    """Map DecisionResult groups to additive knowledge_recommendation response."""
    def item(c) -> dict:
        return {
            "komoditas": c.commodity_name,
            "komoditas_id": c.commodity_id,
            "vulnerability": c.vulnerability_level,
            "max_inundation": c.maximum_inundation_duration,
            "maximum_inundation_duration": c.maximum_inundation_duration,
            "main_impacts": list(c.main_impacts),
            "damage_symptoms": list(c.damage_symptoms),
            "impacts": list(c.main_impacts),
            "symptoms": list(c.damage_symptoms),
            "reason": c.recommendation_reason,
            "source": c.knowledge_reference,
        }

    return {
        "recommended": [
            item(c)
            for c in (result.get_group(RecommendationStatus.RECOMMENDED).commodities
                      if result.get_group(RecommendationStatus.RECOMMENDED) else [])
        ],
        "alternative": [
            item(c)
            for c in (result.get_group(RecommendationStatus.ALTERNATIVE).commodities
                      if result.get_group(RecommendationStatus.ALTERNATIVE) else [])
        ],
        "not_recommended": [
            item(c)
            for c in (result.get_group(RecommendationStatus.NOT_RECOMMENDED).commodities
                      if result.get_group(RecommendationStatus.NOT_RECOMMENDED) else [])
        ],
    }


def to_knowledge_source(result: DecisionResult | None = None) -> dict:
    """Return additive knowledge_source metadata."""
    return {
        "version": result.metadata.engine_version if result and result.metadata else "1.0",
        "engine": "KB-DSS",
        "execution_duration_ms": (
            round(result.metadata.execution_duration_ms, 2)
            if result and result.metadata
            else 0.0
        ),
    }
