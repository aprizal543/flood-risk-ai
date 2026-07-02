"""Endpoint penyedia data cuaca."""

from fastapi import APIRouter, HTTPException, Query

from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError, WeatherProviderError
from backend.providers.openmeteo_provider import OpenMeteoProvider

router = APIRouter(tags=["Provider Cuaca"])

_provider = OpenMeteoProvider()


@router.get(
    "/api/provider/openmeteo",
    summary="Ambil data cuaca dari Open-Meteo",
    description="Mengambil data observasi cuaca harian terbaru untuk wilayah tertentu "
                "menggunakan Open-Meteo API. Data yang dikembalikan siap digunakan untuk prediksi.",
)
def get_openmeteo_weather(wilayah: str = Query(..., description="Nama wilayah/kota", examples=["Pekanbaru"])):
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
