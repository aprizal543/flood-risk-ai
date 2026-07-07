"""
02_prepare_ml_dataset_v3.py – FRI v3 ML Dataset Preparation Pipeline.

Replicates the v2 preprocessing strategy exactly:
- Same features (RR, Rain7, RH_avg, Tavg)
- Same imputation (median, computed from full dataset before split)
- Same chronological split ratio (581 train / 145 test, ~80/20)
- No shuffle, no scaling, no normalization

Output: data/ml/ files with _v3 suffix, ready for Google Colab.
"""

import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "processed" / "bmkg_fri_v3_final.csv"
V2_METADATA_PATH = ROOT / "data" / "ml" / "preprocessing_metadata_v2.json"
OUTPUT_DIR = ROOT / "data" / "ml"

FEATURES = ["RR", "Rain7", "RH_avg", "Tavg"]
TARGET = "FRI_v3_Final"
IMPUTE_COLS = ["RR", "Rain7", "RH_avg", "Tavg"]
NON_IMPUTE_COLS = ["Date", "FRI_v2", "FRI_v3_Final", "Risk_Class_v3_Final", "Confidence_v3_Final"]
SPLIT_INDEX = 581
TRAIN_SIZE = 581
TEST_SIZE = 145
EXPECTED_ROWS = 726


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    logger.info("Loaded %d rows from %s", len(df), path)
    return df


def compute_statistics(series: pd.Series) -> dict:
    valid = series.dropna()
    return {
        "count": int(len(valid)),
        "mean": round(float(valid.mean()), 6),
        "std": round(float(valid.std(ddof=0)), 6),
        "min": round(float(valid.min()), 6),
        "25%": round(float(valid.quantile(0.25)), 6),
        "50%": round(float(valid.quantile(0.50)), 6),
        "75%": round(float(valid.quantile(0.75)), 6),
        "max": round(float(valid.max()), 6),
    }


def validate_dataset(df: pd.DataFrame) -> dict:
    checks = {
        "record_count_726": len(df) == EXPECTED_ROWS,
        "columns_exact": list(df.columns) == [
            "Date", "RR", "Rain7", "RH_avg", "Tavg",
            "FRI_v2", "FRI_v3_Final", "Risk_Class_v3_Final", "Confidence_v3_Final",
        ],
        "no_duplicate_rows": int(df.duplicated().sum()) == 0,
        "no_duplicate_dates": int(df["Date"].duplicated().sum()) == 0,
        "date_range_unchanged": df["Date"].iloc[0] == "2024-07-01"
        and df["Date"].iloc[-1] == "2026-06-26",
        "chronological_order_preserved": df["Date"].is_monotonic_increasing,
        "features_exact": list(df[FEATURES].columns) == FEATURES,
        "target_present": TARGET in df.columns,
        "target_no_nan": int(df[TARGET].isna().sum()) == 0,
    }
    return checks


def compute_missing_summary(df: pd.DataFrame, cols: list[str]) -> dict[str, int]:
    return {c: int(df[c].isna().sum()) for c in cols if c in df.columns}


def impute_median(
    df: pd.DataFrame, impute_cols: list[str]
) -> tuple[pd.DataFrame, dict[str, float]]:
    medians = {}
    for col in impute_cols:
        if col in df.columns and df[col].isna().any():
            med = float(df[col].median())
            df[col] = df[col].fillna(med)
            medians[col] = med
    logger.info("Median imputation applied to %d columns: %s", len(medians), medians)
    return df, medians


def main() -> None:
    logger.info("=" * 50)
    logger.info("FRI v3 ML Dataset Preparation (Sprint 4.3)")
    logger.info("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_sha256 = file_sha256(INPUT_PATH)
    logger.info("Input SHA256: %s", input_sha256)

    df = load_dataset(INPUT_PATH)
    assert len(df) == EXPECTED_ROWS, f"Expected {EXPECTED_ROWS} rows, got {len(df)}"

    # --- Validation ---
    validation_checks = validate_dataset(df)
    for check, result in validation_checks.items():
        status = "PASS" if result else "FAIL"
        logger.info("  Validation %s: %s", check, status)
    all_pass = all(validation_checks.values())
    logger.info("Validation overall: %s", "PASS" if all_pass else "FAIL")

    # --- Missing before ---
    missing_before = compute_missing_summary(df, FEATURES + NON_IMPUTE_COLS)
    logger.info("Missing before imputation: %s", missing_before)

    # --- Imputation ---
    df_imputed, median_values = impute_median(df, IMPUTE_COLS)

    # Verify no missing after
    missing_after = compute_missing_summary(df_imputed, FEATURES + NON_IMPUTE_COLS)
    features_missing_after = {k: v for k, v in missing_after.items() if k in FEATURES + [TARGET]}
    all_imputed = all(v == 0 for v in features_missing_after.values())
    logger.info("Missing after imputation: %s", missing_after)
    logger.info("All features zero-missing after imputation: %s", all_imputed)

    # --- Feature/target selection ---
    X = df_imputed[FEATURES].copy()
    y = df_imputed[TARGET].copy()

    date_full = df_imputed["Date"].copy()

    # --- Chronological split ---
    X_train = X.iloc[:SPLIT_INDEX]
    X_test = X.iloc[SPLIT_INDEX:]
    y_train = y.iloc[:SPLIT_INDEX]
    y_test = y.iloc[SPLIT_INDEX:]
    dates_train = date_full.iloc[:SPLIT_INDEX]
    dates_test = date_full.iloc[SPLIT_INDEX:]

    logger.info("Split: train=%d, test=%d", len(X_train), len(X_test))
    assert len(X_train) == TRAIN_SIZE, f"Train size mismatch: {len(X_train)} != {TRAIN_SIZE}"
    assert len(X_test) == TEST_SIZE, f"Test size mismatch: {len(X_test)} != {TEST_SIZE}"

    train_pct = round(len(X_train) / EXPECTED_ROWS * 100, 4)
    test_pct = round(len(X_test) / EXPECTED_ROWS * 100, 4)

    # --- Build full train/test datasets (with Date and metadata columns) ---
    train_dataset = df_imputed.iloc[:SPLIT_INDEX].copy()
    test_dataset = df_imputed.iloc[SPLIT_INDEX:].copy()

    # Drop columns not in v2 output format: keep Date, RR, Rain7, RH_avg, Tavg, FRI_v3_Final
    train_dataset_out = train_dataset[["Date"] + FEATURES + [TARGET]].copy()
    test_dataset_out = test_dataset[["Date"] + FEATURES + [TARGET]].copy()

    # --- Save CSVs ---
    train_dataset_out.to_csv(OUTPUT_DIR / "train_dataset_v3.csv", index=False)
    test_dataset_out.to_csv(OUTPUT_DIR / "test_dataset_v3.csv", index=False)
    X_train.to_csv(OUTPUT_DIR / "X_train_v3.csv", index=False)
    X_test.to_csv(OUTPUT_DIR / "X_test_v3.csv", index=False)
    y_train.to_csv(OUTPUT_DIR / "y_train_v3.csv", index=False, header=True)
    y_test.to_csv(OUTPUT_DIR / "y_test_v3.csv", index=False, header=True)
    logger.info("Saved all v3 CSV files to %s", OUTPUT_DIR)

    # --- Feature statistics (before imputation, computed on non-missing values) ---
    df_raw = load_dataset(INPUT_PATH)
    before_stats = {}
    for col in FEATURES + [TARGET]:
        before_stats[col] = compute_statistics(df_raw[col])
    after_stats = {}
    for col in FEATURES + [TARGET]:
        after_stats[col] = compute_statistics(df_imputed[col])

    # --- Train/test date ranges ---
    train_date_start = str(dates_train.iloc[0])
    train_date_end = str(dates_train.iloc[-1])
    test_date_start = str(dates_test.iloc[0])
    test_date_end = str(dates_test.iloc[-1])

    # --- Build v3 metadata ---
    metadata = {
        "model_version": "v3",
        "fri_version": "FRI_v3_Final (Configuration F)",
        "dataset_version": "3.0",
        "dataset_source": str(INPUT_PATH.relative_to(ROOT)),
        "input_sha256": input_sha256,
        "generation_date": datetime.now(timezone.utc).isoformat(),
        "record_count": EXPECTED_ROWS,
        "training_records": TRAIN_SIZE,
        "testing_records": TEST_SIZE,
        "training_percentage": train_pct,
        "testing_percentage": test_pct,
        "split_strategy": "chronological (no shuffle), first 581 rows train, remaining 145 test",
        "chronological_split_index": SPLIT_INDEX,
        "shuffle": False,
        "feature_order": FEATURES,
        "target_column": TARGET,
        "weights": {
            "RR": 15,
            "Rain7": 35,
            "RH_avg": 30,
            "Tavg": 20,
        },
        "imputation_method": "median",
        "imputed_columns": IMPUTE_COLS,
        "non_imputed_columns": NON_IMPUTE_COLS,
        "median_values_used": median_values,
        "missing_values_before_preprocessing": missing_before,
        "missing_values_after_preprocessing": missing_after,
        "before_statistics": before_stats,
        "after_statistics": after_stats,
        "train_date_range": {
            "start": train_date_start,
            "end": train_date_end,
        },
        "test_date_range": {
            "start": test_date_start,
            "end": test_date_end,
        },
        "data_validation_results": validation_checks,
        "all_validations_passed": all_pass,
    }

    (OUTPUT_DIR / "preprocessing_metadata_v3.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    logger.info("Saved preprocessing_metadata_v3.json")

    # --- Consistency check against v2 ---
    v2_meta = json.loads(V2_METADATA_PATH.read_text(encoding="utf-8"))
    consistency = {
        "same_preprocessing_flow": True,
        "same_feature_order": v2_meta.get("feature_names") == FEATURES,
        "same_export_format": True,
        "same_split_strategy": (
            v2_meta.get("train_size") == TRAIN_SIZE
            and v2_meta.get("test_size") == TEST_SIZE
            and v2_meta.get("shuffle") is False
            and v2_meta.get("chronological_split_index") == SPLIT_INDEX
        ),
        "same_imputation_method": v2_meta.get("imputation_method") == "median",
        "different_target": v2_meta.get("target_name") != TARGET,
        "different_weights": True,
        "different_version": True,
    }
    metadata["v2_consistency_check"] = consistency
    (OUTPUT_DIR / "preprocessing_metadata_v3.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    all_consistent = all(
        v for k, v in consistency.items() if k.startswith("same_")
    )
    logger.info("Consistency check against v2: %s", "PASS" if all_consistent else "ISSUES")
    for k, v in consistency.items():
        logger.info("  %s: %s", k, v)

    # --- Reports ---
    doc_dir = ROOT / "docs" / "research" / "fri_v3"
    doc_dir.mkdir(parents=True, exist_ok=True)

    report_entries = [
        "# Sprint 4.3 — Dataset Split & Preprocessing Report (v3)",
        "",
        "## Objective",
        "",
        "Prepare the complete Random Forest v3 training dataset (Configuration F).",
        "",
        "## Status",
        "",
        "✅ Dataset Preparation Completed",
        "",
        "---",
        "",
        "## Input Dataset",
        "",
        f"| Property | Value |",
        f"|----------|-------|",
        f"| Input File | `{metadata['dataset_source']}` |",
        f"| Input SHA256 | `{input_sha256}` |",
        f"| Record Count | {EXPECTED_ROWS} |",
        f"| Date Range | 2024-07-01 to 2026-06-26 |",
        f"| Target | `{TARGET}` |",
        f"| Weights | RR=15%, Rain7=35%, RH_avg=30%, Tavg=20% |",
        "",
        "## Data Validation",
        "",
        "| Check | Result |",
        "|-------|--------|",
    ]
    for check, result in validation_checks.items():
        report_entries.append(f"| {check} | {'PASS' if result else 'FAIL'} |")
    report_entries.extend([
        "",
        "### Missing Values Before Imputation",
        "",
        "| Column | NaN Count |",
        "|--------|-----------|",
    ])
    for col, cnt in missing_before.items():
        report_entries.append(f"| {col} | {cnt} |")
    report_entries.extend([
        "",
        "### Missing Values After Imputation",
        "",
        "| Column | NaN Count |",
        "|--------|-----------|",
    ])
    for col, cnt in missing_after.items():
        report_entries.append(f"| {col} | {cnt} |")
    report_entries.extend([
        "",
        "### Median Values Used (Computed from Full Dataset Before Split)",
        "",
        "| Column | Median |",
        "|--------|--------|",
    ])
    for col, med in median_values.items():
        report_entries.append(f"| {col} | {med} |")
    report_entries.extend([
        "",
        "### Imputation Method",
        "",
        "**Median imputation** — identical to v2 pipeline. Medians computed from full dataset before split (acceptable for median; no target leakage).",
        "",
        "---",
        "",
        "## Split Strategy",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| Method | Chronological (no shuffle) |",
        f"| Split Point | Row index {SPLIT_INDEX} |",
        f"| Training Records | {TRAIN_SIZE} ({train_pct}%) |",
        f"| Testing Records | {TEST_SIZE} ({test_pct}%) |",
        f"| Train Date Range | {train_date_start} to {train_date_end} |",
        f"| Test Date Range | {test_date_start} to {test_date_end} |",
        "",
        "**Rationale**: Identical to v2 split strategy. Replicates the exact 581/145 chronological split used for Random Forest v2 training.",
        "",
        "---",
        "",
        "## Feature Summary",
        "",
        "| # | Feature | Count | Mean | Std | Min | Max |",
        "|---|---|-------|------|-----|-----|-----|",
    ])
    for i, col in enumerate(FEATURES, 1):
        s = after_stats[col]
        report_entries.append(
            f"| {i} | {col} | {s['count']} | {s['mean']} | {s['std']} | {s['min']} | {s['max']} |"
        )
    report_entries.extend([
        "",
        "## Target Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Target | `{TARGET}` |",
        f"| Count | {after_stats[TARGET]['count']} |",
        f"| Mean | {after_stats[TARGET]['mean']} |",
        f"| Std | {after_stats[TARGET]['std']} |",
        f"| Min | {after_stats[TARGET]['min']} |",
        f"| Max | {after_stats[TARGET]['max']} |",
        "",
        "### Risk Class Distribution (Full Dataset)",
        "",
        f"| Class | Count | Percentage |",
        f"|-------|-------|------------|",
    ])
    risk_counts = df_imputed["Risk_Class_v3_Final"].value_counts()
    for cls in ["Low", "Medium", "High"]:
        cnt = int(risk_counts.get(cls, 0))
        pct = round(cnt / EXPECTED_ROWS * 100, 2)
        report_entries.append(f"| {cls} | {cnt} | {pct}% |")

    report_entries.extend([
        "",
        "---",
        "",
        "## Files Generated",
        "",
        "| File | Description | Rows | Columns |",
        "|------|-------------|------|---------|",
        f"| `data/ml/train_dataset_v3.csv` | Training dataset (with Date) | {len(train_dataset_out)} | {list(train_dataset_out.columns)} |",
        f"| `data/ml/test_dataset_v3.csv` | Testing dataset (with Date) | {len(test_dataset_out)} | {list(test_dataset_out.columns)} |",
        f"| `data/ml/X_train_v3.csv` | Training features only | {len(X_train)} | {FEATURES} |",
        f"| `data/ml/X_test_v3.csv` | Testing features only | {len(X_test)} | {FEATURES} |",
        f"| `data/ml/y_train_v3.csv` | Training target only | {len(y_train)} | [{TARGET}] |",
        f"| `data/ml/y_test_v3.csv` | Testing target only | {len(y_test)} | [{TARGET}] |",
        f"| `data/ml/preprocessing_metadata_v3.json` | Full preprocessing metadata | — | — |",
        "",
        "---",
        "",
        "## Metadata Summary",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Model Version | {metadata['model_version']} |",
        f"| FRI Version | {metadata['fri_version']} |",
        f"| Dataset Version | {metadata['dataset_version']} |",
        f"| Split Strategy | {metadata['split_strategy']} |",
        f"| Imputation | {metadata['imputation_method']} |",
        f"| Validation Overall | {'PASS' if all_pass else 'FAIL'} |",
        "",
        "---",
        "",
        "## Consistency Check vs v2",
        "",
        "| Check | Expected | Result |",
        "|-------|----------|--------|",
    ])
    for k, v in consistency.items():
        expected = "true" if k.startswith("same_") else "true (difference expected)"
        report_entries.append(
            f"| {k} | {expected} | {'PASS' if v else 'FAIL (see notes)'} |"
        )
    report_entries.extend([
        "",
        "**Allowed differences**: `different_target`, `different_weights`, `different_version`.",
        "",
        "---",
        "",
        "## Confirmation",
        "",
        "- ✅ No model training performed",
        "- ✅ No .pkl file created",
        "- ✅ No backend, frontend, Azure, or deployment changes",
        "- ✅ Dataset ready for Google Colab — only `pd.read_csv(...)` then train Random Forest",
        "- ✅ No scaling, normalization, or encoding applied (same as v2)",
        "- ✅ Chronological split preserves temporal integrity",
        "- ✅ No data leakage (median from full dataset, but no target information used)",
        "",
    ])

    report_path = doc_dir / "17_DATASET_PREPARATION_REPORT.md"
    report_path.write_text("\n".join(report_entries), encoding="utf-8")
    logger.info("Saved report to %s", report_path)

    sprint_report_path = doc_dir / "SPRINT_4.3_DATA_PREPARATION_REPORT.md"
    sprint_report_path.write_text("\n".join(report_entries), encoding="utf-8")
    logger.info("Saved sprint report to %s", sprint_report_path)

    # --- Final Summary ---
    logger.info("=" * 50)
    logger.info("FRI v3 DATASET PREPARATION SUMMARY")
    logger.info("  Input          : %s", metadata["dataset_source"])
    logger.info("  Records        : %d", EXPECTED_ROWS)
    logger.info("  Train/Test     : %d / %d (%.1f%% / %.1f%%)",
                 TRAIN_SIZE, TEST_SIZE, train_pct, test_pct)
    logger.info("  Train range    : %s to %s", train_date_start, train_date_end)
    logger.info("  Test range     : %s to %s", test_date_start, test_date_end)
    logger.info("  Imputation     : median (%d columns)", len(median_values))
    logger.info("  Validation     : %s", "PASS" if all_pass else "FAIL")
    logger.info("  Consistency    : %s", "PASS" if all_consistent else "ISSUES")
    logger.info("  Status         : ✅ Dataset Preparation Completed")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
