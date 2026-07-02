"""
aggregation.py – Weighted aggregation of risk scores into FRI.

Implements the FRI formula: FRI = Σ(w_i × S_i) with NaN-aware renormalisation.
"""

import numpy as np
import pandas as pd

# Default weights (preliminary, pending literature review + EDA)
DEFAULT_WEIGHTS: dict[str, float] = {
    "score_rr": 0.25,
    "score_rain3": 0.20,
    "score_rain7": 0.15,
    "score_rain14": 0.10,
    "score_rh_avg": 0.15,
    "score_temp_range": 0.15,
}

SCORE_COLUMNS = list(DEFAULT_WEIGHTS.keys())


def compute_fri(df: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Compute Flood Risk Index using weighted aggregation with NaN renormalisation.

    FRI = Σ(w_i × S_i) / Σ(w_i for available scores)
    Maintains 0–100 scale regardless of missing scores.
    """
    w = weights or DEFAULT_WEIGHTS
    weight_arr = np.array([w[col] for col in SCORE_COLUMNS])
    scores = df[SCORE_COLUMNS].values  # shape (n, 6)

    mask = ~np.isnan(scores)
    weighted = np.where(mask, scores * weight_arr, 0.0)
    weight_sums = (mask * weight_arr).sum(axis=1)

    with np.errstate(divide="ignore", invalid="ignore"):
        fri = np.where(weight_sums > 0, weighted.sum(axis=1) / weight_sums, np.nan)

    df["fri"] = fri
    return df


def classify_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Classify FRI into Low / Medium / High risk levels."""
    conditions = [
        df["fri"] <= 33,
        (df["fri"] > 33) & (df["fri"] <= 66),
        df["fri"] > 66,
    ]
    choices = ["Low", "Medium", "High"]
    df["risk_level"] = np.select(conditions, choices, default=None)
    df.loc[df["fri"].isna(), "risk_level"] = None
    return df
