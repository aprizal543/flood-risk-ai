"""Health check endpoint."""

from fastapi import APIRouter

from backend.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Status kesehatan API",
    description="Memeriksa apakah layanan API berjalan dengan baik.",
)
def health_check() -> HealthResponse:
    return HealthResponse(status="sehat", versi="1.0.0")
