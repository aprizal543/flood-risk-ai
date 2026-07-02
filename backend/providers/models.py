"""models.py – Model data standar untuk penyedia cuaca."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class RawWeatherData:
    """Data cuaca mentah dari penyedia eksternal."""
    tanggal: date
    rr: float
    rh_avg: float
    tmax: float
    tmin: float
    latitude: float
    longitude: float
    sumber: str
