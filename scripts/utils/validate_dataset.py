"""
validate_dataset.py – BMKG Merged Dataset Validation Pipeline

Reads data/interim/bmkg_merged.csv and produces validation reports in
Markdown and JSON format without modifying the dataset.
"""

import json
import logging
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
REPORT_DIR = ROOT / "outputs" / "reports"
REQUIRED_COLUMNS = ["TANGGAL", "TN", "TX", "TAVG", "RH_AVG", "RR", "source_file"]


def load_dataset(path: Path) -> pd.DataFrame:
    """Load merged CSV and parse TANGGAL as datetime."""
    df = pd.read_csv(path, parse_dates=["TANGGAL"])
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def validate_columns(df: pd.DataFrame) -> dict:
    """Check required columns exist. Returns validation result."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return {"required": REQUIRED_COLUMNS, "missing": missing, "pass": len(missing) == 0}


def dataset_summary(df: pd.DataFrame) -> dict:
    """Compute dataset summary statistics."""
    return {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "start_date": str(df["TANGGAL"].min().date()),
        "end_date": str(df["TANGGAL"].max().date()),
        "total_days": (df["TANGGAL"].max() - df["TANGGAL"].min()).days + 1,
    }


def missing_values(df: pd.DataFrame) -> dict:
    """Count and percentage of missing values per column."""
    result = {}
    for col in df.columns:
        count = int(df[col].isna().sum())
        result[col] = {"count": count, "percentage": round(count / len(df) * 100, 2)}
    return result


def sentinel_values(df: pd.DataFrame) -> dict:
    """Count 8888 and 9999 occurrences in numeric columns."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    result = {}
    for col in numeric_cols:
        result[col] = {
            "8888": int((df[col] == 8888).sum()),
            "9999": int((df[col] == 9999).sum()),
        }
    return result


def duplicate_rows(df: pd.DataFrame) -> dict:
    """Count exact duplicate rows."""
    count = int(df.duplicated().sum())
    return {"count": count}


def duplicate_dates(df: pd.DataFrame) -> dict:
    """Count duplicate dates in TANGGAL."""
    dupes = df[df["TANGGAL"].duplicated(keep=False)]
    return {
        "count": int(df["TANGGAL"].duplicated().sum()),
        "dates": sorted(dupes["TANGGAL"].dt.strftime("%Y-%m-%d").unique().tolist()),
    }


def missing_dates(df: pd.DataFrame) -> dict:
    """Find calendar dates missing between min and max date."""
    full_range = pd.date_range(df["TANGGAL"].min(), df["TANGGAL"].max(), freq="D")
    present = set(df["TANGGAL"].dt.normalize())
    missing = sorted(set(full_range) - present)
    return {
        "count": len(missing),
        "dates": [d.strftime("%Y-%m-%d") for d in missing],
    }


def data_types(df: pd.DataFrame) -> dict:
    """Return data type of each column."""
    return {col: str(dtype) for col, dtype in df.dtypes.items()}


def descriptive_stats(df: pd.DataFrame) -> dict:
    """Descriptive statistics for numeric columns."""
    numeric = df.select_dtypes(include="number")
    desc = numeric.describe().round(2)
    return {col: {k: float(v) for k, v in desc[col].items()} for col in desc.columns}


def source_file_distribution(df: pd.DataFrame) -> dict:
    """Rows per source file."""
    dist = df["source_file"].value_counts().sort_index()
    return dist.to_dict()


def build_report(df: pd.DataFrame) -> dict:
    """Run all validations and return consolidated report."""
    col_check = validate_columns(df)
    summary = dataset_summary(df)
    missing_val = missing_values(df)
    sentinels = sentinel_values(df)
    dup_rows = duplicate_rows(df)
    dup_dates = duplicate_dates(df)
    miss_dates = missing_dates(df)
    dtypes = data_types(df)
    stats = descriptive_stats(df)
    src_dist = source_file_distribution(df)

    # Overall validation result
    issues = []
    if not col_check["pass"]:
        issues.append(f"Missing columns: {col_check['missing']}")
    if dup_rows["count"] > 0:
        issues.append(f"{dup_rows['count']} duplicate rows")
    if miss_dates["count"] > 0:
        issues.append(f"{miss_dates['count']} missing calendar dates")

    total_missing = sum(v["count"] for v in missing_val.values())
    total_sentinels = sum(v["8888"] + v["9999"] for v in sentinels.values())

    validation_result = {
        "status": "PASS" if not issues else "WARNINGS",
        "issues": issues,
        "total_missing_values": total_missing,
        "total_sentinel_values": total_sentinels,
    }

    return {
        "1_dataset_summary": summary,
        "2_column_validation": col_check,
        "3_missing_values": missing_val,
        "4_sentinel_values": sentinels,
        "5_duplicate_rows": dup_rows,
        "6_duplicate_dates": dup_dates,
        "7_missing_calendar_dates": miss_dates,
        "8_data_types": dtypes,
        "9_descriptive_statistics": stats,
        "10_source_file_distribution": src_dist,
        "11_validation_result": validation_result,
    }


def save_json(report: dict, path: Path) -> None:
    """Save report as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Saved JSON report to {path}")


def save_markdown(report: dict, path: Path) -> None:
    """Save report as Markdown."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Dataset Validation Report\n"]

    # 1. Summary
    s = report["1_dataset_summary"]
    lines.append("## 1. Dataset Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Records | {s['total_records']} |")
    lines.append(f"| Total Columns | {s['total_columns']} |")
    lines.append(f"| Start Date | {s['start_date']} |")
    lines.append(f"| End Date | {s['end_date']} |")
    lines.append(f"| Total Days | {s['total_days']} |\n")

    # 2. Missing Values
    mv = report["3_missing_values"]
    lines.append("## 2. Missing Values\n")
    lines.append("| Column | Count | Percentage |")
    lines.append("|--------|-------|------------|")
    for col, v in mv.items():
        lines.append(f"| {col} | {v['count']} | {v['percentage']}% |")
    lines.append("")

    # 3. Sentinel Values
    sv = report["4_sentinel_values"]
    lines.append("## 3. Sentinel Values (8888 / 9999)\n")
    lines.append("| Column | 8888 | 9999 |")
    lines.append("|--------|------|------|")
    for col, v in sv.items():
        lines.append(f"| {col} | {v['8888']} | {v['9999']} |")
    lines.append("")

    # 4. Duplicate Rows
    dr = report["5_duplicate_rows"]
    lines.append(f"## 4. Duplicate Rows\n")
    lines.append(f"Count: **{dr['count']}**\n")

    # 5. Duplicate Dates
    dd = report["6_duplicate_dates"]
    lines.append(f"## 5. Duplicate Dates\n")
    lines.append(f"Count: **{dd['count']}**\n")
    if dd["dates"]:
        lines.append("Dates: " + ", ".join(dd["dates"]) + "\n")

    # 6. Missing Calendar Dates
    md = report["7_missing_calendar_dates"]
    lines.append(f"## 6. Missing Calendar Dates\n")
    lines.append(f"Count: **{md['count']}**\n")
    if md["dates"]:
        lines.append("Dates: " + ", ".join(md["dates"]) + "\n")

    # 7. Data Types
    dt = report["8_data_types"]
    lines.append("## 7. Data Types\n")
    lines.append("| Column | Type |")
    lines.append("|--------|------|")
    for col, dtype in dt.items():
        lines.append(f"| {col} | {dtype} |")
    lines.append("")

    # 8. Descriptive Statistics
    stats = report["9_descriptive_statistics"]
    lines.append("## 8. Descriptive Statistics\n")
    if stats:
        stat_keys = list(next(iter(stats.values())).keys())
        header = "| Stat | " + " | ".join(stats.keys()) + " |"
        sep = "|------|" + "|".join(["------"] * len(stats)) + "|"
        lines.append(header)
        lines.append(sep)
        for sk in stat_keys:
            row = f"| {sk} | " + " | ".join(str(stats[c].get(sk, "")) for c in stats) + " |"
            lines.append(row)
    lines.append("")

    # 9. Source File Distribution
    sfd = report["10_source_file_distribution"]
    lines.append("## 9. Source File Distribution\n")
    lines.append("| File | Rows |")
    lines.append("|------|------|")
    for f, count in sfd.items():
        lines.append(f"| {f} | {count} |")
    lines.append("")

    # 10. Validation Result
    vr = report["11_validation_result"]
    lines.append(f"## 10. Validation Result\n")
    lines.append(f"**Status: {vr['status']}**\n")
    lines.append(f"- Total missing values: {vr['total_missing_values']}")
    lines.append(f"- Total sentinel values: {vr['total_sentinel_values']}")
    if vr["issues"]:
        lines.append("\nIssues:")
        for issue in vr["issues"]:
            lines.append(f"- {issue}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Saved Markdown report to {path}")


def main() -> None:
    """Run the validation pipeline."""
    logger.info("Starting dataset validation pipeline")

    df = load_dataset(INPUT_PATH)
    report = build_report(df)
    save_json(report, REPORT_DIR / "dataset_validation.json")
    save_markdown(report, REPORT_DIR / "dataset_validation_report.md")

    status = report["11_validation_result"]["status"]
    logger.info(f"Validation complete – Status: {status}")


if __name__ == "__main__":
    main()
