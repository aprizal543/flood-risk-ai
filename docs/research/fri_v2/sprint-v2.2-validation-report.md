# Sprint v2.2 Validation Report

## Status

PASS

## Output Dataset

| Metric | Value |
|--------|-------|
| Output File | `data/processed/bmkg_fri_v2.csv` |
| Record Count | 726 |
| Date Range | 2024-07-01 to 2026-06-26 |
| Duplicate Rows | 0 |
| Duplicate Dates | 0 |
| FRI_v2 Missing Values | 0 |
| FRI_v2 Minimum | 8.5039 |
| FRI_v2 Maximum | 86.5562 |

## Weight Verification

| Score | Weight |
|-------|--------|
| `score_RR` | 10% |
| `score_Rain7` | 50% |
| `score_RH_avg` | 30% |
| `score_Tavg` | 10% |
| Total | 100% |

## Validation Checklist

| Check | Result |
|-------|--------|
| record_count_726 | PASS |
| date_range_unchanged | PASS |
| duplicate_rows_zero | PASS |
| duplicate_dates_zero | PASS |
| feature_columns_exact | PASS |
| output_columns_exact | PASS |
| removed_features_absent | PASS |
| fri_range_0_100 | PASS |
| fri_v2_no_nan | PASS |
| weight_sum_100 | PASS |

## Scope Confirmation

Sprint v2.2 generated FRI labels only. No preprocessing, median imputation, train/test split, Random Forest training, backend, frontend, realtime, security, authentication, or deployment changes are part of this output.
