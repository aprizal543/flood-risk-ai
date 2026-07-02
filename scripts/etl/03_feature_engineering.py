"""
03_feature_engineering.py – Feature Engineering Pipeline

Reads data/interim/bmkg_clean.csv, derives temporal, rainfall, temperature,
and anomaly features, and saves to data/processed/bmkg_features.csv.

No imputation, no normalisation (except rainfall_anomaly), no FRI computation.
"""

import json
import logging
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "interim" / "bmkg_clean.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "bmkg_features.csv"
METADATA_PATH = ROOT / "data" / "processed" / "bmkg_features.metadata.json"


def load_dataset(path: Path) -> pd.DataFrame:
    """Load cleaned dataset with tanggal as datetime."""
    df = pd.read_csv(path, parse_dates=["tanggal"])
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive month and day_of_year from tanggal."""
    df["month"] = df["tanggal"].dt.month
    df["day_of_year"] = df["tanggal"].dt.dayofyear
    logger.info("Created temporal features: month, day_of_year")
    return df


def create_rainfall_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive rolling rainfall accumulations (3, 7, 14 days).

    Uses min_periods=1 to compute partial sums from available observations.
    Audit columns record how many valid days contributed to each window.
    """
    for window in (3, 7, 14):
        col = f"rain{window}"
        valid_col = f"rain{window}_valid_days"
        df[col] = df["rr"].rolling(window=window, min_periods=1).sum()
        df[valid_col] = df["rr"].notna().astype(int).rolling(window=window, min_periods=1).sum().astype("Int64")
    logger.info("Created rainfall features: rain3, rain7, rain14 + audit columns")
    return df


def create_temperature_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive diurnal temperature range."""
    df["temp_range"] = df["tx"] - df["tn"]
    logger.info("Created temperature feature: temp_range")
    return df


def create_anomaly_feature(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rainfall_anomaly as unconditional percentile rank of rr (0–100)."""
    df["rainfall_anomaly"] = df["rr"].rank(pct=True) * 100
    logger.info("Created anomaly feature: rainfall_anomaly")
    return df


def validate_features(df: pd.DataFrame, expected_rows: int) -> bool:
    """Validate feature engineering output."""
    valid = True
    if len(df) != expected_rows:
        logger.error(f"Row count mismatch: {len(df)} != {expected_rows}")
        valid = False

    if df["tanggal"].duplicated().any():
        logger.error(f"Duplicate dates found: {df['tanggal'].duplicated().sum()}")
        valid = False

    expected_cols = [
        "tanggal", "tn", "tx", "tavg", "rh_avg", "rr", "source_file",
        "month", "day_of_year", "rain3", "rain7", "rain14",
        "temp_range", "rainfall_anomaly",
        "rain3_valid_days", "rain7_valid_days", "rain14_valid_days",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
        valid = False

    # Verify valid_days never exceed window size
    for window in (3, 7, 14):
        col = f"rain{window}_valid_days"
        if col in df.columns and (df[col].max() > window):
            logger.error(f"{col} exceeds window size {window}")
            valid = False

    if valid:
        logger.info("Feature validation passed")
    return valid


def save_dataset(df: pd.DataFrame, path: Path) -> None:
    """Save feature-engineered dataset to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Saved features to {path}")


def write_metadata(df: pd.DataFrame, path: Path) -> None:
    """Write metadata JSON describing the feature dataset."""
    nan_counts = {col: int(df[col].isna().sum()) for col in df.columns}
    metadata = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "date_range": {
            "start": str(df["tanggal"].min().date()),
            "end": str(df["tanggal"].max().date()),
        },
        "nan_counts": nan_counts,
        "feature_groups": {
            "raw": ["rr", "tavg", "tx", "tn", "rh_avg"],
            "temporal": ["month", "day_of_year"],
            "rainfall_derived": ["rain3", "rain7", "rain14"],
            "temperature_derived": ["temp_range"],
            "anomaly": ["rainfall_anomaly"],
            "audit": ["rain3_valid_days", "rain7_valid_days", "rain14_valid_days"],
        },
        "rolling_window_config": {
            "rain3": {"window": 3, "min_periods": 1},
            "rain7": {"window": 7, "min_periods": 1},
            "rain14": {"window": 14, "min_periods": 1},
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info(f"Saved metadata to {path}")


def print_summary(df: pd.DataFrame) -> None:
    """Log summary of feature-engineered dataset."""
    logger.info("=" * 50)
    logger.info("FEATURE ENGINEERING SUMMARY")
    logger.info(f"  Total rows    : {len(df)}")
    logger.info(f"  Total columns : {len(df.columns)}")
    logger.info(f"  Date range    : {df['tanggal'].min().date()} to {df['tanggal'].max().date()}")
    logger.info(f"  NaN counts:")
    for col in ["rain3", "rain7", "rain14", "temp_range", "rainfall_anomaly"]:
        logger.info(f"    {col:>18}: {df[col].isna().sum()}")
    logger.info("=" * 50)


def main() -> None:
    """Run the feature engineering pipeline."""
    logger.info("Starting feature engineering pipeline")

    df = load_dataset(INPUT_PATH)
    expected_rows = len(df)

    df = create_temporal_features(df)
    df = create_rainfall_features(df)
    df = create_temperature_features(df)
    df = create_anomaly_feature(df)

    if not validate_features(df, expected_rows):
        logger.error("Validation failed, aborting")
        sys.exit(1)

    save_dataset(df, OUTPUT_PATH)
    write_metadata(df, METADATA_PATH)
    print_summary(df)
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
