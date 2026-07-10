"""Info and health monitoring endpoints."""

from fastapi import APIRouter, Request

from backend.services.metadata_service import get_model_info, get_version_info, get_health_detail
from backend.services.recommendation_gateway import get_active_engine, is_knowledge_active

router = APIRouter(tags=["Info & Monitoring"])


@router.get(
    "/api/info/model",
    summary="Informasi model ML",
    description="Mengembalikan detail model prediksi termasuk nama fitur dan status artifact.",
)
def model_info():
    return get_model_info()


@router.get(
    "/api/info/version",
    summary="Informasi versi aplikasi",
    description="Mengembalikan versi aplikasi, Python, dan FastAPI.",
)
def version_info():
    return get_version_info()


@router.get(
    "/api/health/detail",
    summary="Status kesehatan detail",
    description="Memeriksa ketersediaan semua komponen sistem: artifact ML, knowledge base, dan engine.",
)
def health_detail(request: Request):
    detail = get_health_detail()

    # Recommendation engine info (additive, Sprint KB4)
    detail["recommendation_engine"] = get_active_engine()
    detail["recommendation_feature_flag"] = is_knowledge_active()

    # Extend with Knowledge Base details (additive)
    kb = getattr(request.app.state, "knowledge_base", None)
    if kb is not None and hasattr(kb, "health_status"):
        kb_status = kb.health_status()
        detail["knowledge_base_engine"] = (
            "sehat" if kb_status.get("knowledge_ready") else "tidak tersedia"
        )
        detail["knowledge_base_detail"] = kb_status

    # Extend with Decision Engine details (additive)
    de = getattr(request.app.state, "decision_engine", None)
    if de is not None and hasattr(de, "health_status"):
        de_status = de.health_status()
        detail["decision_engine"] = (
            "sehat" if de_status.get("decision_ready") else "tidak tersedia"
        )
        detail["decision_engine_detail"] = de_status
        rs = getattr(request.app.state, "recommendation_service", None)
        if rs is not None and hasattr(rs, "is_ready"):
            detail["kb_recommendation_service"] = "aktif" if rs.is_ready else "tidak tersedia"

    return detail
