"""calendar.py – Derivasi fitur kalender."""

from datetime import date


def compute_month(tanggal: date) -> int:
    """Ekstrak bulan dari tanggal."""
    return tanggal.month


def compute_day_of_year(tanggal: date) -> int:
    """Ekstrak hari dalam setahun dari tanggal."""
    d = tanggal
    return d.timetuple().tm_yday
