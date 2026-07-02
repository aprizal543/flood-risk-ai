"""geocoding.py – Open-Meteo Geocoding API."""

from dataclasses import dataclass

import requests

from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


@dataclass(frozen=True)
class GeoLocation:
    """Hasil geocoding."""
    latitude: float
    longitude: float
    name: str


def geocode(wilayah: str) -> GeoLocation:
    """Cari koordinat untuk nama wilayah menggunakan Open-Meteo Geocoding API.

    Args:
        wilayah: Nama kota/wilayah.

    Returns:
        GeoLocation dengan latitude, longitude, dan nama tampilan.

    Raises:
        LocationNotFoundError: Jika wilayah tidak ditemukan.
        ProviderConnectionError: Jika gagal terhubung.
    """
    try:
        resp = requests.get(GEOCODING_URL, params={"name": wilayah, "count": 1}, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ProviderConnectionError(f"Gagal terhubung ke layanan geocoding: {e}")

    data = resp.json()
    results = data.get("results")
    if not results:
        raise LocationNotFoundError(f"Lokasi '{wilayah}' tidak ditemukan.")

    r = results[0]
    return GeoLocation(
        latitude=r["latitude"],
        longitude=r["longitude"],
        name=r.get("name", wilayah),
    )
