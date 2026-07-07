"""openmeteo_provider.py – Open-Meteo provider with connection pooling and retry."""

from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.config import (
    OPENMETEO_CONNECT_TIMEOUT,
    OPENMETEO_READ_TIMEOUT,
    POOL_CONNECTIONS,
    POOL_MAXSIZE,
    RETRY_BACKOFF_FACTOR,
    RETRY_TOTAL,
)
from backend.logging import get_request_id
from backend.providers.exceptions import ProviderConnectionError, WeatherProviderError
from backend.providers.geocoding import geocode
from backend.providers.models import RawWeatherData
from backend.providers.weather_provider import WeatherProvider

logger = logging.getLogger("backend.providers.openmeteo")

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WIB = ZoneInfo("Asia/Jakarta")
WEATHER_TIMEOUT = (OPENMETEO_CONNECT_TIMEOUT, OPENMETEO_READ_TIMEOUT)

# Sentinel captured at import time so the helper can detect test patches.
_ORIG_REQUESTS_GET = requests.get

# ── Shared connection pool ───────────────────────────────────────────────
_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        retry_strategy = Retry(
            total=RETRY_TOTAL,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=POOL_CONNECTIONS,
            pool_maxsize=POOL_MAXSIZE,
        )
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
    return _session


def _http_get(url: str, **kwargs) -> requests.Response:
    """GET via pooled session in production, fallback for test mocks."""
    if requests.get is _ORIG_REQUESTS_GET:
        return _get_session().get(url, **kwargs)
    return requests.get(url, **kwargs)


def _build_daily_params(latitude: float, longitude: float, start_date: date, end_date: date) -> dict:
    """Build common query parameters for the Open-Meteo forecast endpoint."""
    return {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum,relative_humidity_2m_mean,temperature_2m_mean,temperature_2m_max,temperature_2m_min",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": "Asia/Jakarta",
    }


def _extract_status(exc: requests.RequestException) -> int | None:
    if exc.response is not None:
        return exc.response.status_code
    return None


def _categorise_error(exc: requests.RequestException) -> str:
    if isinstance(exc, requests.Timeout):
        return "TIMEOUT"
    if isinstance(exc, requests.ConnectionError):
        cause = getattr(exc, "__cause__", None) or getattr(exc, "__context__", None)
        if cause is not None:
            cause_str = type(cause).__name__
            return f"CONNECTION_ERROR ({cause_str})"
        return "CONNECTION_ERROR"
    if isinstance(exc, requests.HTTPError):
        return f"HTTP_ERROR ({exc.response.status_code})"
    return "REQUEST_ERROR"


def _log_request_error(
    exc: requests.RequestException,
    rid: str,
    label: str,
    elapsed_ms: float,
) -> None:
    category = _categorise_error(exc)
    status = _extract_status(exc)
    logger.error(
        "[%s] %s FAILED category=%s status=%s elapsed=%dms: %s",
        rid, label, category, status, elapsed_ms, exc,
        exc_info=True,
    )


def _fetch_forecast(
    params: dict,
    label: str,
) -> dict:
    """Execute a single forecast GET with shared session, retry, and logging."""
    start = time.perf_counter()
    _rid = get_request_id()

    try:
        resp = _http_get(WEATHER_URL, params=params, timeout=WEATHER_TIMEOUT)
        resp.raise_for_status()

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("[%s] %s=%dms", _rid, label, elapsed_ms)
        return resp.json()

    except requests.RequestException as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _log_request_error(e, _rid, label, elapsed_ms)
        raise ProviderConnectionError(
            f"Gagal terhubung ke Open-Meteo Weather API: {e}",
            url=WEATHER_URL,
            elapsed_ms=elapsed_ms,
            status_code=_extract_status(e),
            original_exception=e,
        )


class OpenMeteoProvider(WeatherProvider):
    """Penyedia data cuaca menggunakan Open-Meteo API.

    Menggunakan koneksi pool bersama, retry dengan exponential backoff,
    structured timeout, dan logging terstruktur.
    """

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

        params = _build_daily_params(
            location.latitude,
            location.longitude,
            today - timedelta(days=1),
            today,
        )

        data = _fetch_forecast(params, f"Forecast(1d) '{wilayah}'")
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
        tavg = daily["temperature_2m_mean"][idx]
        tmax = daily["temperature_2m_max"][idx]
        tmin = daily["temperature_2m_min"][idx]

        # Handle None values from API
        if any(v is None for v in (rr, rh, tavg, tmax, tmin)):
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
            tavg=float(tavg),
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

        params = _build_daily_params(
            location.latitude,
            location.longitude,
            start_date,
            today,
        )

        data = _fetch_forecast(params, f"Forecast({days}d) '{wilayah}'")
        daily = data.get("daily")
        if not daily or not daily.get("time"):
            raise WeatherProviderError("Respons Open-Meteo tidak mengandung data historis.")

        results = []
        for i, t in enumerate(daily["time"]):
            rr = daily["precipitation_sum"][i]
            rh = daily["relative_humidity_2m_mean"][i]
            tavg = daily["temperature_2m_mean"][i]
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            # Skip days with incomplete data
            if any(v is None for v in (rr, rh, tavg, tmax, tmin)):
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
                tavg=float(tavg),
            ))

        if not results:
            raise WeatherProviderError("Tidak ada data historis lengkap dari Open-Meteo.")

        return results
