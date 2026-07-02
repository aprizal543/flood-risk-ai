"""rainfall.py – Derivasi fitur akumulasi curah hujan."""

import pandas as pd


def compute_rain3(rr_series: pd.Series) -> pd.Series:
    """Hitung akumulasi curah hujan 3 hari."""
    return rr_series.rolling(window=3, min_periods=1).sum()


def compute_rain7(rr_series: pd.Series) -> pd.Series:
    """Hitung akumulasi curah hujan 7 hari."""
    return rr_series.rolling(window=7, min_periods=1).sum()


def compute_rain14(rr_series: pd.Series) -> pd.Series:
    """Hitung akumulasi curah hujan 14 hari."""
    return rr_series.rolling(window=14, min_periods=1).sum()
