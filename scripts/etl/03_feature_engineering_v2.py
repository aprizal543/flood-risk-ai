"""
03_feature_engineering_v2.py - FRI v2 Feature Engineering Pipeline

Reads data/interim/bmkg_clean.csv and writes a new FRI v2 feature dataset to
data/processed/bmkg_features_v2.csv without modifying the FRI v1 pipeline or
any source dataset.

Scope: feature engineering only. No FRI scoring, aggregation, labeling,
training, backend inference, or model artifact generation.
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
OUTPUT_PATH = ROOT / "data" / "processed" / "bmkg_features_v2.csv"
VALIDATION_JSON_PATH = ROOT / "data" / "processed" / "bmkg_features_v2.validation.json"
VALIDATION_REPORT_PATH = ROOT / "docs" / "research" / "fri_v2" / "sprint-v2.1-validation-report.md"
MIGRATION_NOTES_PATH = ROOT / "docs" / "research" / "fri_v2" / "sprint-v2.1-migration-notes.md"

EXPECTED_ROWS = 726
EXPECTED_START_DATE = "2024-07-01"
EXPECTED_END_DATE = "2026-06-26"
FEATURE_ORDER = ["RR", "Rain7", "RH_avg", "Tavg"]
REMOVED_FEATURES = ["Rain3", "Rain14", "TempRange", "RainfallAnomaly"]


def load_dataset(path: Path) -> pd.DataFrame:
    """Load the frozen clean BMKG dataset without mutating it."""
    df = pd.read_csv(path, parse_dates=["tanggal"])
    logger.info("Loaded %s rows from %s", len(df), path)
    return df


def build_v2_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build the closed FRI v2 feature set in canonical order."""
    rain7 = df["rr"].rolling(window=7, min_periods=1).sum()
    return pd.DataFrame(
        {
            "RR": df["rr"],
            "Rain7": rain7,
            "RH_avg": df["rh_avg"],
            "Tavg": df["tavg"],
        }
    )


def validate_output(source: pd.DataFrame, features: pd.DataFrame) -> dict:
    """Validate FRI v2 feature output against the frozen constraints."""
    expected_rain7 = source["rr"].rolling(window=7, min_periods=1).sum()
    rain7_match = features["Rain7"].equals(expected_rain7)
    source_missing = {
        "RR": int(source["rr"].isna().sum()),
        "RH_avg": int(source["rh_avg"].isna().sum()),
        "Tavg": int(source["tavg"].isna().sum()),
    }
    output_missing = {col: int(features[col].isna().sum()) for col in features.columns}
    removed_present = [feature for feature in REMOVED_FEATURES if feature in features.columns]

    checks = {
        "record_count_726": len(source) == EXPECTED_ROWS and len(features) == EXPECTED_ROWS,
        "date_range_unchanged": str(source["tanggal"].min().date()) == EXPECTED_START_DATE
        and str(source["tanggal"].max().date()) == EXPECTED_END_DATE,
        "duplicate_rows_zero": int(source.duplicated().sum()) == 0,
        "duplicate_dates_zero": int(source["tanggal"].duplicated().sum()) == 0,
        "feature_order_exact": list(features.columns) == FEATURE_ORDER,
        "removed_features_absent": not removed_present,
        "rain7_correct": rain7_match,
        "rr_missing_unchanged": output_missing["RR"] == source_missing["RR"],
        "rh_avg_missing_unchanged": output_missing["RH_avg"] == source_missing["RH_avg"],
        "tavg_missing_unchanged": output_missing["Tavg"] == source_missing["Tavg"],
    }

    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "source_dataset": {
            "path": str(INPUT_PATH.relative_to(ROOT)),
            "record_count": int(len(source)),
            "date_range": {
                "start": str(source["tanggal"].min().date()),
                "end": str(source["tanggal"].max().date()),
            },
            "duplicate_rows": int(source.duplicated().sum()),
            "duplicate_dates": int(source["tanggal"].duplicated().sum()),
            "missing_values_retained_columns": source_missing,
        },
        "feature_dataset": {
            "path": str(OUTPUT_PATH.relative_to(ROOT)),
            "record_count": int(len(features)),
            "feature_count": int(len(features.columns)),
            "feature_order": list(features.columns),
            "missing_values": output_missing,
            "data_types": {col: str(dtype) for col, dtype in features.dtypes.items()},
            "removed_features_present": removed_present,
        },
    }


def save_dataset(features: pd.DataFrame, path: Path) -> None:
    """Save the FRI v2 feature dataset without overwriting v1 outputs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(path, index=False)
    logger.info("Saved FRI v2 features to %s", path)


def save_json(report: dict, path: Path) -> None:
    """Save machine-readable validation results."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Saved validation JSON to %s", path)


def save_validation_report(report: dict, path: Path) -> None:
    """Save human-readable validation report."""
    source = report["source_dataset"]
    dataset = report["feature_dataset"]
    checks = report["checks"]
    lines = [
        "# Sprint v2.1 Feature Engineering Validation Report",
        "",
        "## Status",
        "",
        report["status"],
        "",
        "## Dataset Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Source Dataset | `{source['path']}` |",
        f"| Output Dataset | `{dataset['path']}` |",
        f"| Record Count | {dataset['record_count']} |",
        f"| Source Date Range | {source['date_range']['start']} to {source['date_range']['end']} |",
        f"| Duplicate Rows | {source['duplicate_rows']} |",
        f"| Duplicate Dates | {source['duplicate_dates']} |",
        f"| Feature Count | {dataset['feature_count']} |",
        f"| Feature Order | {', '.join(dataset['feature_order'])} |",
        "",
        "## Missing Values",
        "",
        "| Feature | Missing Count |",
        "|---------|---------------|",
    ]
    for feature, count in dataset["missing_values"].items():
        lines.append(f"| `{feature}` | {count} |")

    lines.extend(
        [
            "",
            "## Validation Checklist",
            "",
            "| Check | Result |",
            "|-------|--------|",
        ]
    )
    for check, passed in checks.items():
        lines.append(f"| {check} | {'PASS' if passed else 'FAIL'} |")

    lines.extend(
        [
            "",
            "## Removed Feature Verification",
            "",
            "The output dataset contains none of the removed FRI v2 features: `Rain3`, `Rain14`, `TempRange`, `RainfallAnomaly`.",
            "",
            "## Scope Confirmation",
            "",
            "This validation covers feature engineering only. It does not generate FRI scores, labels, model artifacts, backend inference changes, frontend changes, or realtime prediction changes.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved validation report to %s", path)


def save_migration_notes(path: Path) -> None:
    """Save migration notes for retained and removed feature engineering outputs."""
    lines = [
        "# Sprint v2.1 Feature Engineering Migration Notes",
        "",
        "## Objective",
        "",
        "Document the FRI v2 feature engineering revision without changing the FRI v1 pipeline.",
        "",
        "## Retained Features",
        "",
        "| Feature | Source | Decision |",
        "|---------|--------|----------|",
        "| `RR` | `rr` from `data/interim/bmkg_clean.csv` | Retained as direct daily rainfall input |",
        "| `Rain7` | 7-day rolling sum of `rr` with `min_periods=1` | Retained as the only engineered rainfall accumulation feature |",
        "| `RH_avg` | `rh_avg` from `data/interim/bmkg_clean.csv` | Retained as humidity input |",
        "| `Tavg` | `tavg` from `data/interim/bmkg_clean.csv` | Retained as average temperature input |",
        "",
        "## Removed Features",
        "",
        "| Feature | v2 Migration Decision |",
        "|---------|-----------------------|",
        "| `Rain3` | Removed from FRI v2 feature dataset |",
        "| `Rain14` | Removed from FRI v2 feature dataset |",
        "| `TempRange` | Removed and replaced by retained `Tavg` input |",
        "| `RainfallAnomaly` | Removed from FRI v2 feature dataset |",
        "",
        "## Output Dataset",
        "",
        "`data/processed/bmkg_features_v2.csv` contains exactly four columns in canonical order: `RR`, `Rain7`, `RH_avg`, `Tavg`.",
        "",
        "## V1 Preservation",
        "",
        "The existing v1 script `scripts/etl/03_feature_engineering.py` and v1 output `data/processed/bmkg_features.csv` are not replaced by this sprint.",
        "",
        "## Explicit Non-Scope",
        "",
        "This sprint does not implement scoring, aggregation, FRI label generation, Random Forest retraining, backend inference, frontend changes, dashboard changes, security changes, authentication changes, realtime prediction changes, or model replacement.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved migration notes to %s", path)


def main() -> None:
    """Run the FRI v2 feature engineering pipeline."""
    logger.info("Starting FRI v2 feature engineering pipeline")
    source = load_dataset(INPUT_PATH)
    features = build_v2_features(source)
    report = validate_output(source, features)

    if report["status"] != "PASS":
        save_json(report, VALIDATION_JSON_PATH)
        logger.error("FRI v2 feature validation failed")
        sys.exit(1)

    save_dataset(features, OUTPUT_PATH)
    save_json(report, VALIDATION_JSON_PATH)
    save_validation_report(report, VALIDATION_REPORT_PATH)
    save_migration_notes(MIGRATION_NOTES_PATH)
    logger.info("FRI v2 feature engineering pipeline complete")


if __name__ == "__main__":
    main()
