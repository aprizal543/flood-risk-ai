"""
01_merge_dataset.py – BMKG Daily Climate Dataset Merge Pipeline

Reads all BMKG .xlsx files from data/raw/pekanbaru/, skips metadata rows,
validates required columns, merges into a single DataFrame, and saves to
data/interim/bmkg_merged.csv.
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

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "pekanbaru"
OUTPUT_PATH = Path(__file__).resolve().parents[2] / "data" / "interim" / "bmkg_merged.csv"
REQUIRED_COLUMNS = ["TANGGAL", "TN", "TX", "TAVG", "RH_AVG", "RR"]


def find_excel_files(directory: Path) -> list[Path]:
    """Find all .xlsx files in directory, ignoring temporary Excel files."""
    files = sorted(
        f for f in directory.glob("*.xlsx") if not f.name.startswith("~$")
    )
    logger.info(f"Found {len(files)} Excel files in {directory}")
    return files


def read_excel_file(filepath: Path) -> pd.DataFrame | None:
    """Read a BMKG Excel file, skipping metadata rows.

    Detects the header row by scanning for 'TANGGAL' in column A.
    Returns None if the file cannot be read.
    """
    try:
        # Read without header to find the header row
        raw = pd.read_excel(filepath, header=None, engine="openpyxl")
        # Find row where first column equals 'TANGGAL'
        mask = raw.iloc[:, 0].astype(str).str.strip().str.upper() == "TANGGAL"
        header_indices = mask[mask].index.tolist()
        if not header_indices:
            logger.warning(f"No header row found in {filepath.name}, skipping")
            return None
        header_idx = header_indices[0]
        # Re-read with correct header
        df = pd.read_excel(
            filepath, header=header_idx, engine="openpyxl"
        )
        # Strip column name whitespace
        df.columns = df.columns.str.strip()
        # Drop rows that are entirely NaN (trailing empty rows)
        df = df.dropna(how="all")
        # Keep only rows with valid date in TANGGAL
        df = df[pd.to_datetime(df["TANGGAL"], dayfirst=True, errors="coerce").notna()].reset_index(drop=True)
        df["source_file"] = filepath.name
        logger.info(f"  Read {len(df)} rows from {filepath.name}")
        return df
    except Exception as e:
        logger.error(f"Failed to read {filepath.name}: {e}")
        return None


def validate_columns(df: pd.DataFrame, filepath: Path) -> bool:
    """Check that all required columns are present in the DataFrame."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        logger.warning(
            f"{filepath.name} missing columns: {missing}, skipping"
        )
        return False
    return True


def merge_datasets(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate all DataFrames, convert TANGGAL to datetime, sort, and deduplicate."""
    merged = pd.concat(dataframes, ignore_index=True)
    merged["TANGGAL"] = pd.to_datetime(merged["TANGGAL"], dayfirst=True, errors="coerce")
    merged = merged.sort_values("TANGGAL").reset_index(drop=True)
    before = len(merged)
    merged = merged.drop_duplicates().reset_index(drop=True)
    dupes_removed = before - len(merged)
    if dupes_removed:
        logger.info(f"Removed {dupes_removed} exact duplicate rows")
    return merged


def save_dataset(df: pd.DataFrame, output_path: Path) -> None:
    """Save the merged DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved merged dataset to {output_path}")


def print_summary(df: pd.DataFrame) -> None:
    """Log a summary of the merged dataset."""
    logger.info("=" * 50)
    logger.info("MERGE SUMMARY")
    logger.info(f"  Total rows   : {len(df)}")
    logger.info(f"  Columns      : {list(df.columns)}")
    logger.info(f"  Date range   : {df['TANGGAL'].min()} to {df['TANGGAL'].max()}")
    logger.info(f"  Source files : {df['source_file'].nunique()}")
    logger.info("=" * 50)


def main() -> None:
    """Run the full merge pipeline."""
    logger.info("Starting BMKG dataset merge pipeline")

    files = find_excel_files(RAW_DIR)
    if not files:
        logger.error(f"No Excel files found in {RAW_DIR}")
        sys.exit(1)

    dataframes: list[pd.DataFrame] = []
    for f in files:
        df = read_excel_file(f)
        if df is not None and validate_columns(df, f):
            dataframes.append(df)

    if not dataframes:
        logger.error("No valid datasets to merge")
        sys.exit(1)

    merged = merge_datasets(dataframes)
    save_dataset(merged, OUTPUT_PATH)
    print_summary(merged)
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
