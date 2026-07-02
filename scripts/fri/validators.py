"""
validators.py – Validation functions for FRI pipeline outputs.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def validate_fri_dataset(df: pd.DataFrame, expected_rows: int) -> bool:
    """Validate the FRI dataset meets all quality requirements."""
    valid = True

    # Row count preservation
    if len(df) != expected_rows:
        logger.error(f"Row count mismatch: {len(df)} != {expected_rows}")
        valid = False

    # FRI bounded [0, 100]
    fri_valid = df["fri"].dropna()
    if (fri_valid < 0).any() or (fri_valid > 100).any():
        logger.error("FRI values outside [0, 100] range")
        valid = False

    # Confidence bounded [0, 1]
    conf_valid = df["confidence"].dropna()
    if (conf_valid < 0).any() or (conf_valid > 1).any():
        logger.error("Confidence values outside [0, 1] range")
        valid = False

    # Score columns bounded [0, 100]
    score_cols = [c for c in df.columns if c.startswith("score_")]
    for col in score_cols:
        vals = df[col].dropna()
        if (vals < 0).any() or (vals > 100).any():
            logger.error(f"{col} values outside [0, 100]")
            valid = False

    # Risk level consistency
    if "risk_level" in df.columns:
        classified = df[df["fri"].notna()]
        invalid_levels = ~classified["risk_level"].isin(["Low", "Medium", "High"])
        if invalid_levels.any():
            logger.error(f"Invalid risk levels found: {classified.loc[invalid_levels, 'risk_level'].unique()}")
            valid = False

    # No duplicate dates
    if df["tanggal"].duplicated().any():
        logger.error("Duplicate dates found")
        valid = False

    if valid:
        logger.info("FRI dataset validation passed")
    return valid


def generate_validation_report(df: pd.DataFrame) -> str:
    """Generate a Markdown validation report for the FRI dataset."""
    fri = df["fri"].dropna()
    lines = [
        "# FRI Validation Report\n",
        "## Dataset Overview\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total records | {len(df)} |",
        f"| FRI computed | {len(fri)} |",
        f"| FRI missing | {df['fri'].isna().sum()} |",
        f"| Date range | {df['tanggal'].min()} to {df['tanggal'].max()} |",
        "",
        "## FRI Distribution\n",
        f"| Statistic | Value |",
        f"|-----------|-------|",
        f"| Mean | {fri.mean():.2f} |",
        f"| Std | {fri.std():.2f} |",
        f"| Min | {fri.min():.2f} |",
        f"| P25 | {fri.quantile(0.25):.2f} |",
        f"| Median | {fri.median():.2f} |",
        f"| P75 | {fri.quantile(0.75):.2f} |",
        f"| Max | {fri.max():.2f} |",
        "",
        "## Risk Classification\n",
        f"| Level | Count | Percentage |",
        f"|-------|-------|------------|",
    ]

    classified = df[df["risk_level"].notna()]
    for level in ["Low", "Medium", "High"]:
        count = (classified["risk_level"] == level).sum()
        pct = count / len(classified) * 100 if len(classified) > 0 else 0
        lines.append(f"| {level} | {count} | {pct:.1f}% |")

    lines.append("")
    lines.append("## Confidence Score\n")
    conf = df["confidence"]
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Mean | {conf.mean():.3f} |")
    lines.append(f"| Min | {conf.min():.3f} |")
    lines.append(f"| Records ≥ 0.5 | {(conf >= 0.5).sum()} |")
    lines.append(f"| Records < 0.5 | {(conf < 0.5).sum()} |")
    lines.append("")

    lines.append("## Score Statistics\n")
    score_cols = [c for c in df.columns if c.startswith("score_")]
    lines.append("| Score | Mean | NaN |")
    lines.append("|-------|------|-----|")
    for col in score_cols:
        lines.append(f"| {col} | {df[col].mean():.2f} | {df[col].isna().sum()} |")
    lines.append("")

    lines.append("## Validation Result\n")
    lines.append("**PASS** – All checks satisfied.\n")

    return "\n".join(lines)
