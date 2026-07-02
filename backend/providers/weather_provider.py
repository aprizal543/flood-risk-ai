"""weather_provider.py – Abstraksi penyedia data cuaca."""

from abc import ABC, abstractmethod

from backend.providers.models import RawWeatherData


class WeatherProvider(ABC):
    """Antarmuka abstrak untuk penyedia data cuaca."""

    @abstractmethod
    def get_current_weather(self, wilayah: str) -> RawWeatherData:
        """Ambil data cuaca terkini untuk wilayah tertentu.

        Args:
            wilayah: Nama wilayah/kota (contoh: 'Pekanbaru').

        Returns:
            RawWeatherData berisi observasi cuaca terstandar.

        Raises:
            LocationNotFoundError: Jika wilayah tidak ditemukan.
            ProviderConnectionError: Jika gagal terhubung ke layanan.
            WeatherProviderError: Error umum lainnya.
        """
        ...
