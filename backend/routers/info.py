"""Info and health monitoring endpoints."""

from fastapi import APIRouter

from backend.services.metadata_service import get_model_info, get_version_info, get_health_detail

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
def health_detail():
    return get_health_detail()
