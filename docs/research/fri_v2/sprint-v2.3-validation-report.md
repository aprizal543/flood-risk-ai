# Sprint v2.3 Validation Report

## Status

PASS

## Input And Output

| Metric | Value |
|--------|-------|
| Input Dataset | `data\processed\bmkg_fri_v2.csv` |
| Train Dataset | `data\ml\train_dataset_v2.csv` |
| Test Dataset | `data\ml\test_dataset_v2.csv` |
| Metadata | `data\ml\preprocessing_metadata_v2.json` |
| Total Records | 726 |
| Train Records | 581 (80.03%) |
| Test Records | 145 (19.97%) |
| Chronological Split Index | 581 |
| Full Date Range | 2024-07-01 to 2026-06-26 |
| Train Date Range | 2024-07-01 to 2026-02-01 |
| Test Date Range | 2026-02-02 to 2026-06-26 |
| Shuffle | `False` |

## Validation Checklist

| Check | Result |
|-------|--------|
| input_checksum_unchanged | PASS |
| record_count_726 | PASS |
| columns_exact | PASS |
| no_duplicate_rows | PASS |
| no_duplicate_dates | PASS |
| date_range_unchanged | PASS |
| chronological_order_preserved | PASS |
| missing_after_zero | PASS |
| target_unchanged | PASS |
| date_unchanged | PASS |
| feature_non_missing_values_unchanged | PASS |
| only_feature_missing_values_changed | PASS |
| train_size_nearest_80_percent | PASS |
| test_size_remaining_20_percent | PASS |
| split_chronological_no_overlap | PASS |
| shuffle_false | PASS |
| no_model_training | PASS |

## Scope Confirmation

This sprint performed dataset preparation only. No model training, model evaluation, hyperparameter tuning, Random Forest creation, `.pkl` export, backend modification, frontend modification, realtime modification, API modification, security modification, authentication modification, or deployment modification was performed.
