"""exceptions.py – Custom exceptions untuk penyedia cuaca."""


class WeatherProviderError(Exception):
    """Error umum dari penyedia data cuaca."""
    pass


class LocationNotFoundError(WeatherProviderError):
    """Lokasi tidak ditemukan oleh layanan geocoding."""
    pass


class ProviderConnectionError(WeatherProviderError):
    """Gagal terhubung ke penyedia data cuaca."""
    pass
