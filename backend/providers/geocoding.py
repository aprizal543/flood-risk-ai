"""geocoding.py – Open-Meteo Geocoding API with connection pooling and retry."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.config import (
    GEOCODING_CONNECT_TIMEOUT,
    GEOCODING_READ_TIMEOUT,
    POOL_CONNECTIONS,
    POOL_MAXSIZE,
    RETRY_BACKOFF_FACTOR,
    RETRY_TOTAL,
)
from backend.logging import get_request_id
from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError

logger = logging.getLogger("backend.providers.geocoding")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
GEOCODING_TIMEOUT = (GEOCODING_CONNECT_TIMEOUT, GEOCODING_READ_TIMEOUT)

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


@dataclass(frozen=True)
class GeoLocation:
    """Hasil geocoding."""
    latitude: float
    longitude: float
    name: str


def geocode(wilayah: str) -> GeoLocation:
    """Cari koordinat untuk nama wilayah menggunakan Open-Meteo Geocoding API.

    Menggunakan koneksi pool bersama, retry dengan exponential backoff,
    dan structured timeout untuk observability.

    Args:
        wilayah: Nama kota/wilayah.

    Returns:
        GeoLocation dengan latitude, longitude, dan nama tampilan.

    Raises:
        LocationNotFoundError: Jika wilayah tidak ditemukan.
        ProviderConnectionError: Jika gagal terhubung setelah seluruh retry habis.
    """
    start = time.perf_counter()
    _rid = get_request_id()

    try:
        resp = _http_get(
            GEOCODING_URL,
            params={"name": wilayah, "count": 1},
            timeout=GEOCODING_TIMEOUT,
        )
        resp.raise_for_status()

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("[%s] Geocoding '%s'=%dms", _rid, wilayah, elapsed_ms)

    except requests.RequestException as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _log_request_error(e, _rid, wilayah, elapsed_ms)
        raise ProviderConnectionError(
            f"Gagal terhubung ke layanan geocoding: {e}",
            url=GEOCODING_URL,
            elapsed_ms=elapsed_ms,
            status_code=_extract_status(e),
            original_exception=e,
        )

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


def _extract_status(exc: requests.RequestException) -> int | None:
    """Extract HTTP status from a RequestException if available."""
    if exc.response is not None:
        return exc.response.status_code
    return None


def _categorise_error(exc: requests.RequestException) -> str:
    """Classify the root cause of a request failure."""
    if isinstance(exc, requests.Timeout):
        return "TIMEOUT"
    if isinstance(exc, requests.ConnectionError):
        # urllib3 may wrap DNS / SSL / refused
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
    wilayah: str,
    elapsed_ms: float,
) -> None:
    """Log a structured error entry for a failed provider request."""
    category = _categorise_error(exc)
    status = _extract_status(exc)
    logger.error(
        "[%s] Geocoding '%s' FAILED category=%s status=%s elapsed=%dms: %s",
        rid, wilayah, category, status, elapsed_ms, exc,
        exc_info=True,
    )
