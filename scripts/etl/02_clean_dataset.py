"""
02_clean_dataset.py – BMKG Data Cleaning Pipeline

Reads data/interim/bmkg_merged.csv, renames columns to snake_case,
converts sentinel values (8888/9999) to NaN, enforces data types,
and saves to data/interim/bmkg_clean.csv.

No rows are dropped, no values are filled or interpolated.
"""

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
INPUT_PATH = ROOT / "data" / "interim" / "bmkg_merged.csv"
OUTPUT_PATH = ROOT / "data" / "interim" / "bmkg_clean.csv"

COLUMN_MAP = {
    "TANGGAL": "tanggal",
    "TN": "tn",
    "TX": "tx",
    "TAVG": "tavg",
    "RH_AVG": "rh_avg",
    "RR": "rr",
}

NUMERIC_COLS = ["tn", "tx", "tavg", "rh_avg", "rr"]
SENTINELS = [8888, 9999]


def load_dataset(path: Path) -> pd.DataFrame:
    """Load merged CSV with TANGGAL parsed as datetime."""
    df = pd.read_csv(path, parse_dates=["TANGGAL"])
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to snake_case per COLUMN_MAP."""
    df = df.rename(columns=COLUMN_MAP)
    logger.info(f"Renamed columns: {list(COLUMN_MAP.values())}")
    return df


def replace_sentinel_values(df: pd.DataFrame) -> pd.DataFrame:
    """Replace BMKG sentinel values (8888, 9999) with NaN in numeric columns."""
    total = 0
    for col in NUMERIC_COLS:
        mask = df[col].isin(SENTINELS)
        count = mask.sum()
        if count:
            df.loc[mask, col] = pd.NA
            total += count
            logger.info(f"  {col}: replaced {count} sentinel values")
    logger.info(f"Total sentinel values replaced: {total}")
    return df


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Enforce data types: tanggal->datetime64, numeric cols->float64."""
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    for col in NUMERIC_COLS:
        df[col] = df[col].astype("float64")
    logger.info("Data types converted")
    return df


def validate_dataset(df: pd.DataFrame, expected_rows: int) -> bool:
    """Validate row count, types, duplicates. Returns True if valid."""
    valid = True

    if len(df) != expected_rows:
        logger.error(f"Row count mismatch: {len(df)} != {expected_rows}")
        valid = False

    if df["tanggal"].duplicated().any():
        dupes = df["tanggal"].duplicated().sum()
        logger.warning(f"Duplicate dates found: {dupes}")
        valid = False

    expected_types = {"tanggal": "datetime64[ns]"} | {c: "float64" for c in NUMERIC_COLS}
    for col, expected in expected_types.items():
        actual = str(df[col].dtype)
        if actual != expected:
            logger.error(f"Type mismatch for {col}: {actual} != {expected}")
            valid = False

    if valid:
        logger.info("Validation passed")
    return valid


def save_dataset(df: pd.DataFrame, path: Path) -> None:
    """Save cleaned DataFrame to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Saved cleaned dataset to {path}")


def print_summary(df: pd.DataFrame) -> None:
    """Log summary of cleaned dataset."""
    logger.info("=" * 50)
    logger.info("CLEANING SUMMARY")
    logger.info(f"  Total rows   : {len(df)}")
    logger.info(f"  Columns      : {list(df.columns)}")
    logger.info(f"  Date range   : {df['tanggal'].min()} to {df['tanggal'].max()}")
    logger.info(f"  NaN per column:")
    for col in NUMERIC_COLS:
        nan_count = df[col].isna().sum()
        logger.info(f"    {col:>8}: {nan_count}")
    logger.info("=" * 50)


def main() -> None:
    """Run the cleaning pipeline."""
    logger.info("Starting BMKG data cleaning pipeline")

    df = load_dataset(INPUT_PATH)
    expected_rows = len(df)

    df = rename_columns(df)
    df = replace_sentinel_values(df)
    df = convert_data_types(df)
    df = df.sort_values("tanggal").reset_index(drop=True)

    if not validate_dataset(df, expected_rows):
        logger.error("Validation failed, aborting")
        sys.exit(1)

    save_dataset(df, OUTPUT_PATH)
    print_summary(df)
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
