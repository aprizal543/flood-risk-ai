"""Endpoint penyedia data cuaca."""

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.dependencies.auth import get_current_user
from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError, WeatherProviderError
from backend.providers.openmeteo_provider import OpenMeteoProvider
from backend.schemas.response import ErrorResponse

router = APIRouter(tags=["Provider Cuaca"])

_provider = OpenMeteoProvider()


@router.get(
    "/api/provider/openmeteo",
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
    summary="Ambil data cuaca dari Open-Meteo",
    description="Mengambil data observasi cuaca harian terbaru untuk wilayah tertentu "
                "menggunakan Open-Meteo API. Data yang dikembalikan siap digunakan untuk prediksi.",
)
def get_openmeteo_weather(
    _: object = Depends(get_current_user),
    wilayah: str = Query(..., description="Nama wilayah/kota", examples=["Pekanbaru"]),
):
    try:
        data = _provider.get_current_weather(wilayah)
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProviderConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except WeatherProviderError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "berhasil",
        "wilayah": wilayah,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "tanggal": data.tanggal.isoformat(),
        "rr": data.rr,
        "rh_avg": data.rh_avg,
        "tmax": data.tmax,
        "tmin": data.tmin,
        "sumber": data.sumber,
    }
