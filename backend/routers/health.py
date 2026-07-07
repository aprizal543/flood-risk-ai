"""Health check endpoint and cache diagnostics."""

from fastapi import APIRouter, Request

from backend.providers.geocoding import geocoding_cache, geocoding_metrics
from backend.providers.openmeteo_provider import forecast_cache, forecast_metrics
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
