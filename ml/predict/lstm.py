"""lstm.py – LSTM prediction module."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml.predict.preprocess import ARTIFACTS_DIR, prepare_sequence

LOOKBACK = 7
_model: Any = None


def _load_model():
    """Lazy-load the LSTM Keras model."""
    global _model
    if _model is None:
        from keras.models import load_model
        _model = load_model(ARTIFACTS_DIR / "best_lstm.keras")
    return _model


def predict_lstm(df: pd.DataFrame) -> float:
    """Predict FRI using LSTM from a prepared multi-row DataFrame.

    Args:
        df: DataFrame with at least LOOKBACK (7) rows,
            columns matching feature_list.json, ordered chronologically.

    Returns:
        Predicted FRI value (float).

    Raises:
        ValueError: If fewer than LOOKBACK rows provided.
    """
    model = _load_model()
    sequence = prepare_sequence(df, lookback=LOOKBACK)
    prediction = model.predict(sequence, verbose=0)[0][0]
    return float(prediction)
