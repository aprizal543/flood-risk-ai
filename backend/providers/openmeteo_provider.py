"""openmeteo_provider.py – Implementasi penyedia cuaca Open-Meteo."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from backend.providers.exceptions import ProviderConnectionError, WeatherProviderError
from backend.providers.geocoding import geocode
from backend.providers.models import RawWeatherData
from backend.providers.weather_provider import WeatherProvider

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WIB = ZoneInfo("Asia/Jakarta")


class OpenMeteoProvider(WeatherProvider):
    """Penyedia data cuaca menggunakan Open-Meteo API."""

    def get_current_weather(self, wilayah: str) -> RawWeatherData:
        """Ambil data cuaca hari ini dari forecast Open-Meteo.

        Menentukan tanggal lokal (Asia/Jakarta), lalu mencari indeks
        yang cocok di daily.time[] untuk memastikan sinkronisasi.

        Args:
            wilayah: Nama kota/wilayah.

        Returns:
            RawWeatherData terstandar.
        """
        location = geocode(wilayah)
        today = datetime.now(WIB).date()

        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "daily": "precipitation_sum,relative_humidity_2m_mean,temperature_2m_max,temperature_2m_min",
            "start_date": (today - timedelta(days=1)).isoformat(),
            "end_date": today.isoformat(),
            "timezone": "Asia/Jakarta",
        }

        try:
            resp = requests.get(WEATHER_URL, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise ProviderConnectionError(f"Gagal terhubung ke Open-Meteo Weather API: {e}")

        data = resp.json()
        daily = data.get("daily")
        if not daily or not daily.get("time"):
            raise WeatherProviderError("Respons Open-Meteo tidak mengandung data harian.")

        # Find today's index in daily.time[]
        today_str = today.isoformat()
        times = daily["time"]
        idx = None
        for i, t in enumerate(times):
            if t == today_str:
                idx = i
                break

        # Fallback to latest available if today not found
        if idx is None:
            idx = len(times) - 1

        forecast_date = date.fromisoformat(times[idx])
        rr = daily["precipitation_sum"][idx]
        rh = daily["relative_humidity_2m_mean"][idx]
        tmax = daily["temperature_2m_max"][idx]
        tmin = daily["temperature_2m_min"][idx]

        # Handle None values from API
        if any(v is None for v in (rr, rh, tmax, tmin)):
            raise WeatherProviderError("Data cuaca tidak lengkap dari Open-Meteo.")

        return RawWeatherData(
            tanggal=forecast_date,
            rr=float(rr),
            rh_avg=float(rh),
            tmax=float(tmax),
            tmin=float(tmin),
            latitude=location.latitude,
            longitude=location.longitude,
            sumber="Open-Meteo",
        )

    def get_weather_history(self, wilayah: str, days: int = 14) -> list[RawWeatherData]:
        """Ambil data cuaca historis + hari ini untuk wilayah tertentu.

        Args:
            wilayah: Nama kota/wilayah.
            days: Jumlah hari historis (default 14).

        Returns:
            List RawWeatherData terurut kronologis (terlama → terbaru).
            Hari terakhir = hari ini (forecast).
        """
        location = geocode(wilayah)
        today = datetime.now(WIB).date()
        start_date = today - timedelta(days=days - 1)

        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "daily": "precipitation_sum,relative_humidity_2m_mean,temperature_2m_max,temperature_2m_min",
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "timezone": "Asia/Jakarta",
        }

        try:
            resp = requests.get(WEATHER_URL, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise ProviderConnectionError(f"Gagal terhubung ke Open-Meteo Weather API: {e}")

        data = resp.json()
        daily = data.get("daily")
        if not daily or not daily.get("time"):
            raise WeatherProviderError("Respons Open-Meteo tidak mengandung data historis.")

        results = []
        for i, t in enumerate(daily["time"]):
            rr = daily["precipitation_sum"][i]
            rh = daily["relative_humidity_2m_mean"][i]
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            # Skip days with incomplete data
            if any(v is None for v in (rr, rh, tmax, tmin)):
                continue
            results.append(RawWeatherData(
                tanggal=date.fromisoformat(t),
                rr=float(rr),
                rh_avg=float(rh),
                tmax=float(tmax),
                tmin=float(tmin),
                latitude=location.latitude,
                longitude=location.longitude,
                sumber="Open-Meteo",
            ))

        if not results:
            raise WeatherProviderError("Tidak ada data historis lengkap dari Open-Meteo.")

        return results
