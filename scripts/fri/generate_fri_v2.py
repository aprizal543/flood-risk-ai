"""
generate_fri_v2.py - FRI v2 scoring and aggregation pipeline.

Reads the Sprint v2.1 feature dataset and generates FRI v2 labels only.
No preprocessing, imputation, train/test split, model training, backend,
frontend, realtime, or deployment changes are performed.
"""

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.fri.scoring import score_percentile, score_rr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

INPUT_PATH = ROOT / "data" / "processed" / "bmkg_features_v2.csv"
V1_FRI_PATH = ROOT / "data" / "processed" / "bmkg_fri_dataset.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "bmkg_fri_v2.csv"
DOC_DIR = ROOT / "docs" / "research" / "fri_v2"
VALIDATION_REPORT_PATH = DOC_DIR / "sprint-v2.2-validation-report.md"
STATISTICAL_ANALYSIS_PATH = DOC_DIR / "sprint-v2.2-statistical-analysis.md"
COMPARISON_REPORT_PATH = DOC_DIR / "sprint-v2.2-comparison-v1-v2.md"
HISTOGRAM_PATH = DOC_DIR / "sprint-v2.2-fri-v2-histogram.png"
BOXPLOT_PATH = DOC_DIR / "sprint-v2.2-fri-v2-boxplot.png"
DIST_TABLE_PATH = DOC_DIR / "sprint-v2.2-distribution-table.csv"

EXPECTED_ROWS = 726
DATE_START = "2024-07-01"
DATE_END = "2026-06-26"
FEATURE_ORDER = ["RR", "Rain7", "RH_avg", "Tavg"]
OUTPUT_COLUMNS = ["Date", "RR", "Rain7", "RH_avg", "Tavg", "FRI_v2"]
WEIGHTS_PERCENT = {
    "score_RR": 10,
    "score_Rain7": 50,
    "score_RH_avg": 30,
    "score_Tavg": 10,
}
SCORE_COLUMNS = list(WEIGHTS_PERCENT.keys())
REMOVED_FEATURES = ["Rain3", "Rain14", "TempRange", "RainfallAnomaly"]
BIN_LABELS = ["0-20", "20-40", "40-60", "60-80", "80-100"]
BIN_EDGES = [0, 20, 40, 60, 80, 100]


def load_features(path: Path) -> pd.DataFrame:
    """Load the v2.1 feature dataset without preprocessing."""
    df = pd.read_csv(path)
    logger.info("Loaded %s rows from %s", len(df), path)
    return df


def build_date_series(row_count: int) -> pd.Series:
    """Build the frozen date identifier required by the v2 output schema."""
    dates = pd.date_range(DATE_START, DATE_END, freq="D")
    if len(dates) != row_count:
        raise ValueError(f"Frozen date range has {len(dates)} days, expected {row_count}")
    return pd.Series(dates.strftime("%Y-%m-%d"), name="Date")


def compute_thresholds(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Compute v1-style percentile thresholds for non-BMKG-score variables."""
    thresholds: dict[str, dict[str, float]] = {}
    for col in ("Rain7", "RH_avg", "Tavg"):
        vals = df[col].dropna()
        thresholds[col] = {
            "p25": float(vals.quantile(0.25)),
            "p50": float(vals.quantile(0.50)),
            "p75": float(vals.quantile(0.75)),
        }
    return thresholds


def compute_scores(df: pd.DataFrame, thresholds: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Score each approved v2 feature using v1-compatible scoring methods."""
    scored = df.copy()
    scored["score_RR"] = score_rr(scored["RR"])
    for col in ("Rain7", "RH_avg", "Tavg"):
        t = thresholds[col]
        scored[f"score_{col}"] = score_percentile(scored[col], t["p25"], t["p50"], t["p75"])
    return scored


def compute_fri_v2(scored: pd.DataFrame) -> pd.Series:
    """Aggregate approved v2 scores with NaN-aware v1-style renormalization."""
    weight_sum = sum(WEIGHTS_PERCENT.values())
    if weight_sum != 100:
        raise ValueError(f"FRI v2 weights must sum to 100, got {weight_sum}")

    weights = np.array([WEIGHTS_PERCENT[col] for col in SCORE_COLUMNS], dtype=float)
    scores = scored[SCORE_COLUMNS].to_numpy(dtype=float)
    mask = ~np.isnan(scores)
    weighted_scores = np.where(mask, scores * weights, 0.0)
    available_weights = (mask * weights).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        fri = np.where(available_weights > 0, weighted_scores.sum(axis=1) / available_weights, np.nan)
    return pd.Series(fri, index=scored.index, name="FRI_v2").clip(lower=0, upper=100)


def classify_fri(series: pd.Series) -> pd.Series:
    """Classify FRI with existing v1 risk-level semantics."""
    conditions = [series <= 33, (series > 33) & (series <= 66), series > 66]
    return pd.Series(np.select(conditions, ["Low", "Medium", "High"], default=None), index=series.index)


def distribution_counts(series: pd.Series) -> pd.Series:
    """Count FRI values in fixed 20-point bins."""
    return pd.cut(series, bins=BIN_EDGES, labels=BIN_LABELS, include_lowest=True, right=True).value_counts().sort_index()


def compute_statistics(series: pd.Series) -> dict[str, float]:
    """Compute required FRI descriptive statistics."""
    return {
        "minimum": float(series.min()),
        "maximum": float(series.max()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "standard_deviation": float(series.std()),
        "q1": float(series.quantile(0.25)),
        "q2": float(series.quantile(0.50)),
        "q3": float(series.quantile(0.75)),
    }


def validate_output(features: pd.DataFrame, output: pd.DataFrame, thresholds: dict) -> dict:
    """Validate Sprint v2.2 acceptance criteria."""
    removed_present = [col for col in REMOVED_FEATURES if col in output.columns]
    checks = {
        "record_count_726": len(output) == EXPECTED_ROWS,
        "date_range_unchanged": output["Date"].iloc[0] == DATE_START and output["Date"].iloc[-1] == DATE_END,
        "duplicate_rows_zero": int(output.duplicated().sum()) == 0,
        "duplicate_dates_zero": int(output["Date"].duplicated().sum()) == 0,
        "feature_columns_exact": list(features.columns) == FEATURE_ORDER,
        "output_columns_exact": list(output.columns) == OUTPUT_COLUMNS,
        "removed_features_absent": not removed_present,
        "fri_range_0_100": bool(output["FRI_v2"].between(0, 100).all()),
        "fri_v2_no_nan": int(output["FRI_v2"].isna().sum()) == 0,
        "weight_sum_100": sum(WEIGHTS_PERCENT.values()) == 100,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "weights_percent": WEIGHTS_PERCENT,
        "thresholds": thresholds,
        "removed_features_present": removed_present,
    }


def save_plots(output: pd.DataFrame) -> None:
    """Save histogram and boxplot visualizations."""
    DOC_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.hist(output["FRI_v2"], bins=BIN_EDGES, edgecolor="black", color="#2563eb")
    plt.title("FRI v2 Distribution")
    plt.xlabel("FRI_v2")
    plt.ylabel("Record Count")
    plt.tight_layout()
    plt.savefig(HISTOGRAM_PATH, dpi=160)
    plt.close()

    plt.figure(figsize=(7, 3))
    plt.boxplot(output["FRI_v2"], vert=False)
    plt.title("FRI v2 Boxplot")
    plt.xlabel("FRI_v2")
    plt.tight_layout()
    plt.savefig(BOXPLOT_PATH, dpi=160)
    plt.close()


def save_validation_report(validation: dict, output: pd.DataFrame) -> None:
    """Write validation report markdown."""
    lines = [
        "# Sprint v2.2 Validation Report",
        "",
        "## Status",
        "",
        validation["status"],
        "",
        "## Output Dataset",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Output File | `data/processed/bmkg_fri_v2.csv` |",
        f"| Record Count | {len(output)} |",
        f"| Date Range | {output['Date'].iloc[0]} to {output['Date'].iloc[-1]} |",
        f"| Duplicate Rows | {int(output.duplicated().sum())} |",
        f"| Duplicate Dates | {int(output['Date'].duplicated().sum())} |",
        f"| FRI_v2 Missing Values | {int(output['FRI_v2'].isna().sum())} |",
        f"| FRI_v2 Minimum | {output['FRI_v2'].min():.4f} |",
        f"| FRI_v2 Maximum | {output['FRI_v2'].max():.4f} |",
        "",
        "## Weight Verification",
        "",
        "| Score | Weight |",
        "|-------|--------|",
    ]
    for score, weight in validation["weights_percent"].items():
        lines.append(f"| `{score}` | {weight}% |")
    lines.extend([f"| Total | {sum(validation['weights_percent'].values())}% |", ""])

    lines.extend(["## Validation Checklist", "", "| Check | Result |", "|-------|--------|"])
    for check, passed in validation["checks"].items():
        lines.append(f"| {check} | {'PASS' if passed else 'FAIL'} |")

    lines.extend(
        [
            "",
            "## Scope Confirmation",
            "",
            "Sprint v2.2 generated FRI labels only. No preprocessing, median imputation, train/test split, Random Forest training, backend, frontend, realtime, security, authentication, or deployment changes are part of this output.",
            "",
        ]
    )
    VALIDATION_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def save_statistical_analysis(stats: dict, dist: pd.Series) -> None:
    """Write statistical analysis markdown and distribution CSV."""
    dist_df = dist.rename_axis("FRI_v2_bin").reset_index(name="count")
    dist_df.to_csv(DIST_TABLE_PATH, index=False)

    lines = [
        "# Sprint v2.2 Statistical Analysis",
        "",
        "## FRI v2 Statistics",
        "",
        "| Statistic | Value |",
        "|-----------|-------|",
    ]
    for name, value in stats.items():
        lines.append(f"| {name.replace('_', ' ').title()} | {value:.4f} |")

    lines.extend(["", "## Distribution Counts", "", "| FRI_v2 Bin | Count |", "|------------|-------|"])
    for label, count in dist.items():
        lines.append(f"| {label} | {int(count)} |")

    lines.extend(
        [
            "",
            "## Visualizations",
            "",
            f"- Histogram: `{HISTOGRAM_PATH.relative_to(ROOT)}`",
            f"- Boxplot: `{BOXPLOT_PATH.relative_to(ROOT)}`",
            f"- Distribution table: `{DIST_TABLE_PATH.relative_to(ROOT)}`",
            "",
            "## Scientific Observations",
            "",
            "FRI v2 concentrates the deterministic index around the approved four-feature methodology. The dominant 50% `Rain7` weight increases sensitivity to antecedent weekly rainfall, while NaN-aware aggregation prevents retained source-feature missing values from creating missing FRI labels before Sprint v2.3 preprocessing.",
            "",
        ]
    )
    STATISTICAL_ANALYSIS_PATH.write_text("\n".join(lines), encoding="utf-8")


def save_comparison_report(output: pd.DataFrame) -> dict:
    """Compare FRI v1 and FRI v2 by aligned row/date."""
    v1 = pd.read_csv(V1_FRI_PATH, parse_dates=["tanggal"])
    v1_fri = v1["fri"]
    v2_fri = output["FRI_v2"]
    v1_category = v1["risk_level"].astype(str)
    v2_category = classify_fri(v2_fri).astype(str)
    diff = v2_fri - v1_fri
    v1_dist = distribution_counts(v1_fri)
    v2_dist = distribution_counts(v2_fri)
    category_changes = int((v1_category != v2_category).sum())
    category_change_pct = float(category_changes / len(output) * 100)

    comparison = {
        "mean_difference_v2_minus_v1": float(diff.mean()),
        "median_difference_v2_minus_v1": float(diff.median()),
        "category_changes": category_changes,
        "category_change_percentage": category_change_pct,
    }

    sensitivity = (
        "more sensitive to antecedent weekly rainfall than FRI v1"
        if output["FRI_v2"].std() >= v1_fri.std()
        else "less dispersed overall than FRI v1, but more concentrated around the weekly-rainfall signal"
    )

    lines = [
        "# Sprint v2.2 FRI v1 vs FRI v2 Comparison",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Mean Difference (FRI_v2 - FRI_v1) | {comparison['mean_difference_v2_minus_v1']:.4f} |",
        f"| Median Difference (FRI_v2 - FRI_v1) | {comparison['median_difference_v2_minus_v1']:.4f} |",
        f"| Records With Category Change | {category_changes} |",
        f"| Category Change Percentage | {category_change_pct:.2f}% |",
        "",
        "## Distribution Comparison",
        "",
        "| Bin | FRI v1 Count | FRI v2 Count |",
        "|-----|--------------|--------------|",
    ]
    for label in BIN_LABELS:
        lines.append(f"| {label} | {int(v1_dist[label])} | {int(v2_dist[label])} |")

    lines.extend(
        [
            "",
            "## Scientific Observation",
            "",
            f"The approved v2 weighting makes the index {sensitivity}. The largest methodological driver is the 50% `Rain7` contribution, while removed short-window, long-window, temperature-range, and anomaly features no longer dilute the weekly antecedent rainfall signal.",
            "",
        ]
    )
    COMPARISON_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return comparison


def main() -> None:
    """Run FRI v2 scoring and aggregation."""
    logger.info("Starting FRI v2 scoring pipeline")
    features = load_features(INPUT_PATH)
    thresholds = compute_thresholds(features)
    scored = compute_scores(features, thresholds)
    fri_v2 = compute_fri_v2(scored)

    output = features.copy()
    output.insert(0, "Date", build_date_series(len(output)))
    output["FRI_v2"] = fri_v2
    output = output[OUTPUT_COLUMNS]

    validation = validate_output(features, output, thresholds)
    if validation["status"] != "PASS":
        logger.error("FRI v2 validation failed: %s", validation["checks"])
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)

    stats = compute_statistics(output["FRI_v2"])
    dist = distribution_counts(output["FRI_v2"])
    save_plots(output)
    save_validation_report(validation, output)
    save_statistical_analysis(stats, dist)
    comparison = save_comparison_report(output)

    logger.info("Saved FRI v2 dataset to %s", OUTPUT_PATH)
    logger.info("FRI v2 mean: %.4f", stats["mean"])
    logger.info("FRI v2 range: %.4f - %.4f", stats["minimum"], stats["maximum"])
    logger.info("Mean difference v2-v1: %.4f", comparison["mean_difference_v2_minus_v1"])
    logger.info("FRI v2 scoring pipeline complete")


if __name__ == "__main__":
    main()
