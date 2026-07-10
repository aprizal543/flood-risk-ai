"""Explainability Engine — Generates human-readable explanations from Knowledge Base data.

Explanations are built entirely from KB fields — never hardcoded in API endpoints.
"""

from __future__ import annotations

from backend.decision.models import RecommendationStatus
from backend.knowledge.models import CommodityKnowledge

_VULN_DESCRIPTIONS: dict[str, str] = {
    "Sangat Tinggi": "sangat toleran terhadap genangan",
    "Tinggi": "cukup toleran terhadap genangan",
    "Sedang": "memiliki toleransi sedang terhadap genangan",
    "Rendah": "kurang toleran terhadap genangan",
    "Sangat Rendah": "sangat rentan terhadap genangan",
}

_FLOOD_TOL_DESCRIPTIONS: dict[str, str] = {
    "Sangat Tinggi": "dapat bertahan lebih dari 7 hari dalam genangan",
    "Tinggi": "dapat bertahan 2-3 hari dalam genangan",
    "Sedang": "dapat bertahan 12-24 jam dalam genangan",
    "Rendah": "hanya dapat bertahan kurang dari 6 jam dalam genangan",
    "Sangat Rendah": "tidak dapat bertahan dalam genangan",
}

_RISK_MATCH_DESCRIPTIONS: dict[str, str] = {
    "Sangat Tinggi": "sangat sesuai untuk ditanam pada berbagai kondisi risiko banjir",
    "Tinggi": "cocok untuk ditanam pada kondisi risiko rendah hingga sedang",
    "Sedang": "cukup sesuai untuk kondisi risiko tertentu dengan pengelolaan drainase",
    "Rendah": "kurang sesuai dan memerlukan perlindungan tambahan",
    "Sangat Rendah": "tidak sesuai dan sangat berisiko mengalami kerusakan",
}


class ExplainabilityEngine:
    """Generates human-readable explanations from Knowledge Base data."""

    @staticmethod
    def generate_reason(
        commodity: CommodityKnowledge,
        status: RecommendationStatus,
        risk_category: str,
    ) -> str:
        name = commodity.commodity_name
        vuln = commodity.vulnerability_level
        inundation = commodity.maximum_inundation_duration

        vuln_desc = _VULN_DESCRIPTIONS.get(vuln, f"memiliki tingkat toleransi {vuln}")
        tol_desc = _FLOOD_TOL_DESCRIPTIONS.get(vuln, "")
        match_desc = _RISK_MATCH_DESCRIPTIONS.get(vuln, "")

        if status == RecommendationStatus.RECOMMENDED:
            return (
                f"{name} direkomendasikan karena {vuln_desc} "
                f"({tol_desc}) sehingga {match_desc} "
                f"pada kondisi Risiko {risk_category} saat ini."
            )

        if status == RecommendationStatus.ALTERNATIVE:
            return (
                f"{name} dapat dipertimbangkan sebagai alternatif pada kondisi "
                f"Risiko {risk_category} karena {vuln_desc} "
                f"({tol_desc}), namun perlu pengelolaan drainase yang baik "
                f"dan perlindungan tambahan."
            )

        return (
            f"{name} tidak direkomendasikan pada kondisi Risiko {risk_category} "
            f"karena {vuln_desc} ({tol_desc}; "
            f"genangan maksimal {inundation.lower()}) "
            f"sehingga {match_desc}."
        )

    @staticmethod
    def generate_detailed_explanation(
        commodity: CommodityKnowledge,
        status: RecommendationStatus,
        risk_category: str,
    ) -> dict:
        impacts = list(commodity.main_impacts)
        symptoms = list(commodity.damage_symptoms)
        reference = commodity.scientific_reference
        duration = commodity.growing_duration_days

        reason = ExplainabilityEngine.generate_reason(commodity, status, risk_category)

        return {
            "ringkasan": reason,
            "faktor_utama": [
                f"Tingkat toleransi banjir: {commodity.vulnerability_level}",
                f"Durasi genangan maksimal: {commodity.maximum_inundation_duration}",
                f"Kebutuhan drainase: {commodity.drainage_requirement}",
            ],
            "dampak_utama": impacts,
            "gejala_kerusakan": symptoms,
            "durasi_tanam_hari": duration,
            "referensi": reference,
        }
