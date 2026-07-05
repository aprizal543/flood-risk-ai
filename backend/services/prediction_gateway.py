"""prediction_gateway.py – Unified entry point untuk seluruh inferensi ML.

Semua endpoint (manual, CSV, realtime) memanggil gateway ini.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.providers.models import RawWeatherData
from ml.feature_engineering.builder import build_features_v2
from ml.service.predictor import prediksi


def predict_from_raw(
    weather: RawWeatherData,
    history: list[dict] | None = None,
    weather_history: list[RawWeatherData] | None = None,
    model: str = "rf",
    top_n: int = 5,
    include_features: bool = False,
) -> dict:
    """Jalankan pipeline prediksi lengkap dari data cuaca mentah.

    Args:
        weather: Data cuaca terstandar untuk hari prediksi.
        history: Opsional — list dict historis {'rr': float} untuk rolling features.
        weather_history: Opsional — list RawWeatherData historis (lebih lengkap dari history).
                         Jika diberikan, akan digunakan sebagai pengganti history.
        model: Model prediksi ('rf' atau 'lstm').
        top_n: Jumlah rekomendasi komoditas.

    Returns:
        Dict lengkap berisi FRI, tingkat_risiko, rekomendasi, dan mitigasi.
    """
    # Convert weather_history to simple history format if provided
    effective_history = history
    if weather_history is not None:
        effective_history = [{"rr": w.rr} for w in weather_history]

    features = build_prediction_features_v2(weather, history=effective_history)
    result = prediksi(features, model=model, top_n=top_n)
    if include_features:
        result["_features"] = features
    return result


def build_prediction_features_v2(
    weather: RawWeatherData,
    history: list[dict] | None = None,
    weather_history: list[RawWeatherData] | None = None,
) -> dict:
    """Build FRI v2 realtime features without invoking model prediction.

    This function is the Sprint v2.5A migration seam. Sprint v2.5B can connect
    this validated feature vector to the v2 model loader.
    """
    raw_data = {
        "tanggal": weather.tanggal.isoformat() if hasattr(weather.tanggal, "isoformat") else str(weather.tanggal),
        "rr": weather.rr,
        "rh_avg": weather.rh_avg,
        "tavg": weather.tavg,
        "tmax": weather.tmax,
        "tmin": weather.tmin,
    }

    effective_history = history
    if weather_history is not None:
        effective_history = [{"rr": w.rr} for w in weather_history]

    df = build_features_v2(raw_data, history=effective_history)
    return df.iloc[0].to_dict()
