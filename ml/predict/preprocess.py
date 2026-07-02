"""preprocess.py – Feature validation, ordering, and scaler access."""

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"

_feature_list: list[str] | None = None
_scaler: Any = None


def get_feature_list() -> list[str]:
    """Load and cache the feature list from artifacts."""
    global _feature_list
    if _feature_list is None:
        path = ARTIFACTS_DIR / "feature_list.json"
        _feature_list = json.loads(path.read_text(encoding="utf-8"))
    return _feature_list


def get_scaler():
    """Load and cache the MinMaxScaler from artifacts."""
    global _scaler
    if _scaler is None:
        _scaler = joblib.load(ARTIFACTS_DIR / "scaler_lstm.pkl")
    return _scaler


def validate_input(data: dict) -> list[str]:
    """Validate that all required features are present. Returns list of missing keys."""
    features = get_feature_list()
    return [f for f in features if f not in data]


def prepare_dataframe(data: dict) -> pd.DataFrame:
    """Convert input dict to a single-row DataFrame ordered by feature_list.

    Raises ValueError if required features are missing.
    """
    missing = validate_input(data)
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    features = get_feature_list()
    return pd.DataFrame([{f: data[f] for f in features}])


def prepare_sequence(df: pd.DataFrame, lookback: int = 7) -> np.ndarray:
    """Prepare a scaled sequence for LSTM prediction.

    Args:
        df: DataFrame with shape (>=lookback, n_features) ordered by feature_list.
        lookback: Number of timesteps required.

    Returns:
        Scaled array with shape (1, lookback, n_features).

    Raises:
        ValueError: If insufficient rows for lookback window.
    """
    features = get_feature_list()
    if len(df) < lookback:
        raise ValueError(f"LSTM requires {lookback} rows, got {len(df)}")
    arr = df[features].iloc[-lookback:].values.astype(np.float64)
    scaler = get_scaler()
    scaled = scaler.transform(arr)
    return scaled.reshape(1, lookback, len(features))
