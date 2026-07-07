"""Health check endpoint."""

from fastapi import APIRouter, Request

from backend.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Status kesehatan API",
    description="Memeriksa apakah layanan API berjalan dengan baik.",
)
def health_check(request: Request) -> HealthResponse:
    startup = getattr(request.app.state, "startup", None)
    ready = startup.is_ready if startup else False
    return HealthResponse(status="sehat", versi="1.0.0", ready=ready)
