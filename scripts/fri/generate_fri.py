"""
generate_fri.py – Flood Risk Index generation pipeline.

Orchestrates scoring, aggregation, confidence, and validation modules
to produce the final FRI dataset from engineered features.
"""

import json
import logging
import sys
from pathlib import Path

import pandas as pd

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.fri.scoring import compute_all_scores
from scripts.fri.aggregation import compute_fri, classify_risk, DEFAULT_WEIGHTS
from scripts.fri.confidence import compute_confidence
from scripts.fri.validators import validate_fri_dataset, generate_validation_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

INPUT_PATH = ROOT / "data" / "processed" / "bmkg_features.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "bmkg_fri_dataset.csv"
METADATA_PATH = ROOT / "data" / "processed" / "bmkg_fri.metadata.json"
REPORT_PATH = ROOT / "outputs" / "reports" / "fri_validation_report.md"


def load_features(path: Path) -> pd.DataFrame:
    """Load the feature-engineered dataset."""
    df = pd.read_csv(path, parse_dates=["tanggal"])
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def compute_thresholds(df: pd.DataFrame) -> dict:
    """Compute percentile thresholds from the dataset."""
    thresholds = {}
    for col in ("rain3", "rain7", "rain14", "rh_avg", "temp_range"):
        vals = df[col].dropna()
        thresholds[col] = {
            "p25": float(vals.quantile(0.25)),
            "p50": float(vals.quantile(0.50)),
            "p75": float(vals.quantile(0.75)),
        }
    logger.info("Computed percentile thresholds from dataset")
    return thresholds


def save_outputs(df: pd.DataFrame, thresholds: dict) -> None:
    """Save dataset, metadata, and validation report."""
    # CSV
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Saved FRI dataset to {OUTPUT_PATH}")

    # Metadata
    fri = df["fri"].dropna()
    metadata = {
        "total_records": len(df),
        "fri_computed": int(fri.notna().sum()) if not fri.empty else 0,
        "date_range": {
            "start": str(df["tanggal"].min().date()),
            "end": str(df["tanggal"].max().date()),
        },
        "weights": DEFAULT_WEIGHTS,
        "thresholds": thresholds,
        "fri_statistics": {
            "mean": round(float(fri.mean()), 2),
            "std": round(float(fri.std()), 2),
            "min": round(float(fri.min()), 2),
            "max": round(float(fri.max()), 2),
        },
        "classification_counts": df["risk_level"].value_counts().to_dict(),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info(f"Saved metadata to {METADATA_PATH}")

    # Validation report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = generate_validation_report(df)
    REPORT_PATH.write_text(report, encoding="utf-8")
    logger.info(f"Saved validation report to {REPORT_PATH}")


def main() -> None:
    """Run the FRI generation pipeline."""
    logger.info("Starting FRI generation pipeline")

    df = load_features(INPUT_PATH)
    expected_rows = len(df)

    # Compute thresholds from data
    thresholds = compute_thresholds(df)

    # Score individual variables
    df = compute_all_scores(df, thresholds)

    # Aggregate into FRI
    df = compute_fri(df)

    # Classify risk level
    df = classify_risk(df)

    # Compute confidence
    df = compute_confidence(df)

    # Validate
    if not validate_fri_dataset(df, expected_rows):
        logger.error("Validation failed, aborting")
        sys.exit(1)

    # Save
    save_outputs(df, thresholds)

    # Summary
    fri = df["fri"].dropna()
    logger.info("=" * 50)
    logger.info("FRI GENERATION SUMMARY")
    logger.info(f"  Records     : {len(df)}")
    logger.info(f"  FRI computed: {len(fri)}")
    logger.info(f"  FRI mean    : {fri.mean():.2f}")
    logger.info(f"  FRI range   : {fri.min():.2f} – {fri.max():.2f}")
    logger.info(f"  Risk levels : {df['risk_level'].value_counts().to_dict()}")
    logger.info("=" * 50)
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
