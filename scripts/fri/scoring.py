"""
scoring.py – Risk score computation for individual FRI variables.

Implements BMKG-based scoring for RR and percentile-based scoring for
derived features, per 01_FRI_SPECIFICATION.md and 07_THRESHOLD_JUSTIFICATION.md.
"""

import numpy as np
import pandas as pd


def score_rr(series: pd.Series) -> pd.Series:
    """Score daily rainfall using BMKG intensity categories with linear interpolation.

    Categories:
        0 mm         → 0
        >0 – 5 mm   → 0–20   (Hujan ringan)
        >5 – 20 mm  → 20–40  (Hujan sedang)
        >20 – 50 mm → 40–70  (Hujan lebat)
        >50 – 100mm → 70–90  (Hujan sangat lebat)
        >100 mm     → 90–100 (Hujan ekstrem)
    """
    breakpoints = [0, 5, 20, 50, 100]
    scores = [0, 20, 40, 70, 90]
    result = np.interp(series, breakpoints, scores, right=100)
    return pd.Series(result, index=series.index).where(series.notna())


def score_percentile(series: pd.Series, p25: float, p50: float, p75: float) -> pd.Series:
    """Score a variable using percentile-based linear interpolation (0–100).

    Maps: ≤P25→0-25, P25-P50→25-50, P50-P75→50-75, ≥P75→75-100.
    Uses the series min/max as P0/P100 anchors.
    """
    valid = series.dropna()
    p0 = valid.min()
    p100 = valid.max()
    breakpoints = [p0, p25, p50, p75, p100]
    scores_bp = [0, 25, 50, 75, 100]
    result = np.interp(series, breakpoints, scores_bp)
    return pd.Series(result, index=series.index).where(series.notna())


def score_percentile_inverse(series: pd.Series, p25: float, p50: float, p75: float) -> pd.Series:
    """Score using inverse percentile mapping (lower value → higher score).

    Used for TempRange where low values indicate storm/overcast conditions.
    """
    valid = series.dropna()
    p0 = valid.min()
    p100 = valid.max()
    breakpoints = [p0, p25, p50, p75, p100]
    scores_bp = [100, 75, 50, 25, 0]
    result = np.interp(series, breakpoints, scores_bp)
    return pd.Series(result, index=series.index).where(series.notna())


def compute_all_scores(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Compute all risk scores and add as columns to the DataFrame.

    Args:
        df: Feature dataset.
        thresholds: Dict with keys 'rain3', 'rain7', 'rain14', 'rh_avg', 'temp_range',
                    each containing 'p25', 'p50', 'p75'.

    Returns:
        DataFrame with score_* columns added.
    """
    df["score_rr"] = score_rr(df["rr"])

    for var in ("rain3", "rain7", "rain14", "rh_avg"):
        t = thresholds[var]
        df[f"score_{var}"] = score_percentile(df[var], t["p25"], t["p50"], t["p75"])

    t = thresholds["temp_range"]
    df["score_temp_range"] = score_percentile_inverse(df["temp_range"], t["p25"], t["p50"], t["p75"])

    return df
