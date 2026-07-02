"""predict.py – Unified prediction interface for the FRI system.

Exposes a single `predict()` function that returns FRI predictions
from both Random Forest and LSTM models with risk classification.
"""

import pandas as pd

from ml.predict.preprocess import prepare_dataframe, get_feature_list, validate_input
from ml.predict.random_forest import predict_rf
from ml.predict.lstm import predict_lstm, LOOKBACK
from ml.predict.risk import classify_risk


def predict(data: dict | list[dict]) -> dict:
    """Generate FRI predictions from input data.

    Args:
        data: Either a single dict of features (for RF only) or a list of
              dicts representing consecutive days (for both RF and LSTM).
              LSTM requires at least 7 consecutive days.

    Returns:
        {
            "random_forest": {"fri": float, "risk": str},
            "lstm": {"fri": float, "risk": str} | None
        }
        LSTM result is None if insufficient data for lookback window.

    Raises:
        ValueError: If required features are missing from input.
    """
    # Normalise input to list
    rows = data if isinstance(data, list) else [data]

    # Validate all rows
    for i, row in enumerate(rows):
        missing = validate_input(row)
        if missing:
            raise ValueError(f"Row {i}: missing features {missing}")

    features = get_feature_list()
    df = pd.DataFrame(rows)[features]

    # Random Forest: predict from last row
    rf_fri = predict_rf(df.iloc[[-1]])
    result: dict = {
        "random_forest": {"fri": rf_fri, "risk": classify_risk(rf_fri)},
        "lstm": None,
    }

    # LSTM: predict if sufficient rows
    if len(df) >= LOOKBACK:
        lstm_fri = predict_lstm(df)
        result["lstm"] = {"fri": lstm_fri, "risk": classify_risk(lstm_fri)}

    return result
