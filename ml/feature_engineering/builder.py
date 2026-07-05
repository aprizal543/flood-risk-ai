"""builder.py - Build ML features from raw weather observations.

FRI v2 feature engineering produces exactly: RR, Rain7, RH_avg, Tavg.

The legacy v1 builder is retained temporarily for compatibility with the
currently deployed v1 model and engineered endpoint. It is deprecated and must
not be used to construct the FRI v2 realtime feature vector.
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

FEATURE_ORDER_V2 = ["RR", "Rain7", "RH_avg", "Tavg"]


def build_features(raw_data: dict, history: list[dict] | None = None) -> pd.DataFrame:
    """Deprecated v1 feature builder retained for compatibility.

    Builds the legacy v1 feature vector:
    rr, rain3, rain7, rain14, rh_avg, temp_range, rainfall_anomaly, month,
    day_of_year.

    Do not use this function for FRI v2 realtime feature construction.

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


def build_features_v2(raw_data: dict, history: list[dict] | None = None) -> pd.DataFrame:
    """Build the FRI v2 realtime feature vector.

    Output order is exactly: RR, Rain7, RH_avg, Tavg.
    Rain7 uses the same rolling methodology as the training dataset:
    rolling(window=7, min_periods=1).sum() over historical RR plus current RR.
    """
    rr = float(raw_data["rr"])
    rh_avg = float(raw_data["rh_avg"])
    tavg = _resolve_tavg(raw_data)

    if history is not None:
        rr_values = [float(h["rr"]) for h in history] + [rr]
        rr_series = pd.Series(rr_values)
        rain7 = float(compute_rain7(rr_series).iloc[-1])
    else:
        rain7 = rr

    row = {
        "RR": rr,
        "Rain7": rain7,
        "RH_avg": rh_avg,
        "Tavg": tavg,
    }
    return pd.DataFrame([row])[FEATURE_ORDER_V2]


def _resolve_tavg(raw_data: dict) -> float:
    """Resolve average daily temperature for FRI v2 features.

    Open-Meteo provides `temperature_2m_mean`, mapped into `tavg`; use it when
    present. The tmax/tmin fallback exists only for non-provider legacy inputs
    such as manual or CSV data until their contracts are migrated.
    """
    if raw_data.get("tavg") is not None:
        return float(raw_data["tavg"])
    return (float(raw_data["tmax"]) + float(raw_data["tmin"])) / 2


def _parse_tanggal(value) -> date:
    """Parse tanggal dari berbagai format."""
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(str(value), "%Y-%m-%d").date()
