# Sprint v2.1 Feature Engineering Validation Report

## Status

PASS

## Dataset Summary

| Metric | Value |
|--------|-------|
| Source Dataset | `data\interim\bmkg_clean.csv` |
| Output Dataset | `data\processed\bmkg_features_v2.csv` |
| Record Count | 726 |
| Source Date Range | 2024-07-01 to 2026-06-26 |
| Duplicate Rows | 0 |
| Duplicate Dates | 0 |
| Feature Count | 4 |
| Feature Order | RR, Rain7, RH_avg, Tavg |

## Missing Values

| Feature | Missing Count |
|---------|---------------|
| `RR` | 74 |
| `Rain7` | 0 |
| `RH_avg` | 5 |
| `Tavg` | 5 |

## Validation Checklist

| Check | Result |
|-------|--------|
| record_count_726 | PASS |
| date_range_unchanged | PASS |
| duplicate_rows_zero | PASS |
| duplicate_dates_zero | PASS |
| feature_order_exact | PASS |
| removed_features_absent | PASS |
| rain7_correct | PASS |
| rr_missing_unchanged | PASS |
| rh_avg_missing_unchanged | PASS |
| tavg_missing_unchanged | PASS |

## Removed Feature Verification

The output dataset contains none of the removed FRI v2 features: `Rain3`, `Rain14`, `TempRange`, `RainfallAnomaly`.

## Scope Confirmation

This validation covers feature engineering only. It does not generate FRI scores, labels, model artifacts, backend inference changes, frontend changes, or realtime prediction changes.
