# Sprint 4.3 — Dataset Split & Preprocessing Report (v3)

## Objective

Prepare the complete Random Forest v3 training dataset (Configuration F).

## Status

✅ Dataset Preparation Completed

---

## Input Dataset

| Property | Value |
|----------|-------|
| Input File | `data\processed\bmkg_fri_v3_final.csv` |
| Input SHA256 | `c05d153781c724011a95e81c97b3dde7cec3f6fdb8e924fcbcb2e54714b3a5fd` |
| Record Count | 726 |
| Date Range | 2024-07-01 to 2026-06-26 |
| Target | `FRI_v3_Final` |
| Weights | RR=15%, Rain7=35%, RH_avg=30%, Tavg=20% |

## Data Validation

| Check | Result |
|-------|--------|
| record_count_726 | PASS |
| columns_exact | PASS |
| no_duplicate_rows | PASS |
| no_duplicate_dates | PASS |
| date_range_unchanged | PASS |
| chronological_order_preserved | PASS |
| features_exact | PASS |
| target_present | PASS |
| target_no_nan | PASS |

### Missing Values Before Imputation

| Column | NaN Count |
|--------|-----------|
| RR | 74 |
| Rain7 | 0 |
| RH_avg | 5 |
| Tavg | 5 |
| Date | 0 |
| FRI_v2 | 0 |
| FRI_v3_Final | 0 |
| Risk_Class_v3_Final | 0 |
| Confidence_v3_Final | 0 |

### Missing Values After Imputation

| Column | NaN Count |
|--------|-----------|
| RR | 0 |
| Rain7 | 0 |
| RH_avg | 0 |
| Tavg | 0 |
| Date | 0 |
| FRI_v2 | 0 |
| FRI_v3_Final | 0 |
| Risk_Class_v3_Final | 0 |
| Confidence_v3_Final | 0 |

### Median Values Used (Computed from Full Dataset Before Split)

| Column | Median |
|--------|--------|
| RR | 0.8 |
| RH_avg | 81.0 |
| Tavg | 27.4 |

### Imputation Method

**Median imputation** — identical to v2 pipeline. Medians computed from full dataset before split (acceptable for median; no target leakage).

---

## Split Strategy

| Property | Value |
|----------|-------|
| Method | Chronological (no shuffle) |
| Split Point | Row index 581 |
| Training Records | 581 (80.0275%) |
| Testing Records | 145 (19.9725%) |
| Train Date Range | 2024-07-01 to 2026-02-01 |
| Test Date Range | 2026-02-02 to 2026-06-26 |

**Rationale**: Identical to v2 split strategy. Replicates the exact 581/145 chronological split used for Random Forest v2 training.

---

## Feature Summary

| # | Feature | Count | Mean | Std | Min | Max |
|---|---|-------|------|-----|-----|-----|
| 1 | RR | 726 | 8.469008 | 17.000769 | 0.0 | 115.8 |
| 2 | Rain7 | 726 | 58.416529 | 52.99916 | 0.0 | 297.6 |
| 3 | RH_avg | 726 | 81.26832 | 6.132435 | 63.0 | 98.0 |
| 4 | Tavg | 726 | 27.333747 | 1.17026 | 23.5 | 30.0 |

## Target Summary

| Metric | Value |
|--------|-------|
| Target | `FRI_v3_Final` |
| Count | 726 |
| Mean | 44.379675 |
| Std | 14.427815 |
| Min | 8.503937 |
| Max | 79.006024 |

### Risk Class Distribution (Full Dataset)

| Class | Count | Percentage |
|-------|-------|------------|
| Low | 180 | 24.79% |
| Medium | 495 | 68.18% |
| High | 51 | 7.02% |

---

## Files Generated

| File | Description | Rows | Columns |
|------|-------------|------|---------|
| `data/ml/train_dataset_v3.csv` | Training dataset (with Date) | 581 | ['Date', 'RR', 'Rain7', 'RH_avg', 'Tavg', 'FRI_v3_Final'] |
| `data/ml/test_dataset_v3.csv` | Testing dataset (with Date) | 145 | ['Date', 'RR', 'Rain7', 'RH_avg', 'Tavg', 'FRI_v3_Final'] |
| `data/ml/X_train_v3.csv` | Training features only | 581 | ['RR', 'Rain7', 'RH_avg', 'Tavg'] |
| `data/ml/X_test_v3.csv` | Testing features only | 145 | ['RR', 'Rain7', 'RH_avg', 'Tavg'] |
| `data/ml/y_train_v3.csv` | Training target only | 581 | [FRI_v3_Final] |
| `data/ml/y_test_v3.csv` | Testing target only | 145 | [FRI_v3_Final] |
| `data/ml/preprocessing_metadata_v3.json` | Full preprocessing metadata | — | — |

---

## Metadata Summary

| Field | Value |
|-------|-------|
| Model Version | v3 |
| FRI Version | FRI_v3_Final (Configuration F) |
| Dataset Version | 3.0 |
| Split Strategy | chronological (no shuffle), first 581 rows train, remaining 145 test |
| Imputation | median |
| Validation Overall | PASS |

---

## Consistency Check vs v2

| Check | Expected | Result |
|-------|----------|--------|
| same_preprocessing_flow | true | PASS |
| same_feature_order | true | PASS |
| same_export_format | true | PASS |
| same_split_strategy | true | PASS |
| same_imputation_method | true | PASS |
| different_target | true (difference expected) | PASS |
| different_weights | true (difference expected) | PASS |
| different_version | true (difference expected) | PASS |

**Allowed differences**: `different_target`, `different_weights`, `different_version`.

---

## Confirmation

- ✅ No model training performed
- ✅ No .pkl file created
- ✅ No backend, frontend, Azure, or deployment changes
- ✅ Dataset ready for Google Colab — only `pd.read_csv(...)` then train Random Forest
- ✅ No scaling, normalization, or encoding applied (same as v2)
- ✅ Chronological split preserves temporal integrity
- ✅ No data leakage (median from full dataset, but no target information used)
