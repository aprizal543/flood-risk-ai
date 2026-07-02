"""builder.py – Membangun fitur ML dari data mentah BMKG.

Menghasilkan DataFrame dengan urutan kolom sesuai feature_list.json:
rr, rain3, rain7, rain14, rh_avg, temp_range, rainfall_anomaly, month, day_of_year
"""

from datetime import date, datetime

import pandas as pd

from ml.feature_engineering.rainfall import compute_rain3, compute_rain7, compute_rain14
from ml.feature_engineering.temperature import compute_temp_range
from ml.feature_engineering.calendar import compute_month, compute_day_of_year
from ml.feature_engineering.anomaly import compute_rainfall_anomaly

FEATURE_ORDER = [
    "rr", "rain3", "rain7", "rain14", "rh_avg",
    "temp_range", "rainfall_anomaly", "month", "day_of_year",
]


def build_features(raw_data: dict, history: list[dict] | None = None) -> pd.DataFrame:
    """Bangun fitur ML dari data observasi mentah BMKG.

    Args:
        raw_data: Dict berisi {tanggal, rr, rh_avg, tmax, tmin}.
        history: Opsional — list dict historis (urut kronologis) untuk rolling features.
                 Jika None, rain3/rain7/rain14 diisi dengan nilai rr hari ini.

    Returns:
        DataFrame satu baris dengan kolom sesuai feature_list.json.
    """
    tanggal = _parse_tanggal(raw_data["tanggal"])
    rr = float(raw_data["rr"])
    rh_avg = float(raw_data["rh_avg"])
    tmax = float(raw_data["tmax"])
    tmin = float(raw_data["tmin"])

    temp_range = compute_temp_range(tmax, tmin)
    month = compute_month(tanggal)
    day_of_year = compute_day_of_year(tanggal)
    rainfall_anomaly = compute_rainfall_anomaly(rr)

    if history is not None:
        # Build series from history + current day
        rr_values = [float(h["rr"]) for h in history] + [rr]
        rr_series = pd.Series(rr_values)
        rain3 = float(compute_rain3(rr_series).iloc[-1])
        rain7 = float(compute_rain7(rr_series).iloc[-1])
        rain14 = float(compute_rain14(rr_series).iloc[-1])
    else:
        # Manual mode — no history available
        rain3 = rr
        rain7 = rr
        rain14 = rr

    row = {
        "rr": rr,
        "rain3": rain3,
        "rain7": rain7,
        "rain14": rain14,
        "rh_avg": rh_avg,
        "temp_range": temp_range,
        "rainfall_anomaly": rainfall_anomaly,
        "month": month,
        "day_of_year": day_of_year,
    }
    return pd.DataFrame([row])[FEATURE_ORDER]


def _parse_tanggal(value) -> date:
    """Parse tanggal dari berbagai format."""
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(str(value), "%Y-%m-%d").date()
