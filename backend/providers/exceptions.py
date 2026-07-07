"""exceptions.py – Custom exceptions untuk penyedia cuaca."""

from typing import Any


class WeatherProviderError(Exception):
    """Error umum dari penyedia data cuaca."""
    pass


class LocationNotFoundError(WeatherProviderError):
    """Lokasi tidak ditemukan oleh layanan geocoding."""
    pass


class ProviderConnectionError(WeatherProviderError):
    """Gagal terhubung ke penyedia data cuaca.

    Carries structured context for observability:
    - url: the request URL that failed
    - elapsed_ms: time elapsed before failure
    - status_code: HTTP status code (if available)
    - original_exception: the root cause exception
    """

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        elapsed_ms: float | None = None,
        status_code: int | None = None,
        original_exception: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.url = url
        self.elapsed_ms = elapsed_ms
        self.status_code = status_code
        self.original_exception = original_exception

    def to_log_dict(self) -> dict[str, Any]:
        return {
            "message": str(self),
            "url": self.url,
            "elapsed_ms": self.elapsed_ms,
            "status_code": self.status_code,
            "original_exception": repr(self.original_exception) if self.original_exception else None,
        }
