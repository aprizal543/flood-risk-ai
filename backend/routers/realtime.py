"""Endpoint prediksi realtime menggunakan data cuaca Open-Meteo."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.dependencies.auth import get_current_user

from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError, WeatherProviderError
from backend.security.limits import REALTIME_LIMIT
from backend.security.rate_limit import limiter
from backend.providers.openmeteo_provider import OpenMeteoProvider
from backend.services.prediction_gateway import predict_from_raw

logger = logging.getLogger("backend.realtime")
router = APIRouter(tags=["Prediksi Realtime"])

_provider = OpenMeteoProvider()
WIB = ZoneInfo("Asia/Jakarta")


@router.get(
    "/api/prediksi/realtime",
    summary="Prediksi risiko banjir realtime",
    description="Mengambil data cuaca 14 hari terakhir dari Open-Meteo untuk wilayah tertentu, "
                "melakukan feature engineering dengan rolling features historis, "
                "lalu mengembalikan FRI, rekomendasi komoditas, dan tindakan mitigasi.",
)
@limiter.limit(REALTIME_LIMIT)
def predict_realtime(
    request: Request,
    _: object = Depends(get_current_user),
    wilayah: str = Query(..., description="Nama wilayah/kota", examples=["Pekanbaru"]),
    model: str = Query(default="rf", pattern="^(rf|lstm)$", description="Model prediksi"),
    top_n: int = Query(default=5, ge=1, le=17, description="Jumlah rekomendasi"),
):
    # Fetch 14-day history (includes yesterday as latest)
    try:
        history_data = _provider.get_weather_history(wilayah, days=14)
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProviderConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except WeatherProviderError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Latest day = last in history; preceding days = history for rolling features
    weather = history_data[-1]
    preceding = history_data[:-1] if len(history_data) > 1 else None

    # Predict using full history
    try:
        result = predict_from_raw(weather, weather_history=preceding, model=model, top_n=top_n, include_features=True)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    logger.info("Realtime: %s FRI=%.2f %s (%d hari historis)",
                wilayah, result["fri"], result["tingkat_risiko"],
                len(preceding) if preceding else 0)

    now = datetime.now(WIB)
    features = result["_features"]

    return {
        "status": "berhasil",
        "wilayah": wilayah,
        "sumber_data": weather.sumber,
        "forecast_date": weather.tanggal.isoformat(),
        "updated_at": now.isoformat(),
        "waktu_prediksi": now.isoformat(),
        "model": result["model"],
        "versi_model": "1.0",
        "RR": features["RR"],
        "Rain7": features["Rain7"],
        "RH_avg": features["RH_avg"],
        "Tavg": features["Tavg"],
        "cuaca": {
            "tanggal": weather.tanggal.isoformat(),
            "rr": weather.rr,
            "rh_avg": weather.rh_avg,
            "tmax": weather.tmax,
            "tmin": weather.tmin,
            "latitude": weather.latitude,
            "longitude": weather.longitude,
        },
        "hari_historis": len(preceding) if preceding else 0,
        "fri": result["fri"],
        "tingkat_risiko": result["tingkat_risiko"],
        "rekomendasi": result["rekomendasi"],
        "mitigasi": result["mitigasi"],
    }
