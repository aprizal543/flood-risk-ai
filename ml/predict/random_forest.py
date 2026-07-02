"""random_forest.py – Random Forest prediction module."""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ml.predict.preprocess import ARTIFACTS_DIR, prepare_dataframe

_model: Any = None


def _load_model():
    """Lazy-load the Random Forest model."""
    global _model
    if _model is None:
        _model = joblib.load(ARTIFACTS_DIR / "random_forest.pkl")
    return _model


def predict_rf(df: pd.DataFrame) -> float:
    """Predict FRI using Random Forest from a prepared single-row DataFrame.

    Args:
        df: DataFrame with columns matching feature_list.json, single row.

    Returns:
        Predicted FRI value (float).
    """
    model = _load_model()
    prediction = model.predict(df)[0]
    return float(prediction)
