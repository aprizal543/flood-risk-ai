"""
confidence.py – Confidence score computation for FRI values.

Confidence reflects both feature availability (non-NaN scores) and
rolling window completeness (audit valid_days columns).
"""

import numpy as np
import pandas as pd

from scripts.fri.aggregation import DEFAULT_WEIGHTS, SCORE_COLUMNS


def compute_confidence(df: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Compute confidence score based on feature completeness and audit columns.

    Confidence = (weight_available_scores / total_weight) × window_quality

    window_quality penalises rolling features computed from incomplete windows.
    """
    w = weights or DEFAULT_WEIGHTS
    weight_arr = np.array([w[col] for col in SCORE_COLUMNS])
    scores = df[SCORE_COLUMNS].values
    mask = ~np.isnan(scores)

    # Base confidence: fraction of total weight with available scores
    weight_available = (mask * weight_arr).sum(axis=1)
    base_confidence = weight_available / weight_arr.sum()

    # Window quality: average completeness of rolling windows
    window_quality = np.ones(len(df))
    audit_cols = {
        "rain3_valid_days": 3,
        "rain7_valid_days": 7,
        "rain14_valid_days": 14,
    }
    available_audits = [col for col in audit_cols if col in df.columns]
    if available_audits:
        ratios = np.column_stack([
            df[col].fillna(0).values / window_size
            for col, window_size in audit_cols.items()
            if col in df.columns
        ])
        window_quality = ratios.mean(axis=1)

    df["confidence"] = np.clip(base_confidence * window_quality, 0, 1)
    return df
