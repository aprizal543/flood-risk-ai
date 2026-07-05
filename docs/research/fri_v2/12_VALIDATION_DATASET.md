# FRI v2 Validation Dataset

## Version

2.0.1 — Documentation Completion

## Objective

Freeze the dataset specification used for future FRI v2 validation. This document extends `01_SPECIFICATION.md` and does not modify, regenerate, clean, merge, or expand the dataset.

## Dataset Specification

| Field | Frozen Value |
|-------|--------------|
| Dataset Name | BMKG Clean Dataset |
| Dataset Version | FRI v2 Design Freeze Dataset |
| Record Count | 726 records |
| Date Range | 2024-07-01 to 2026-06-26 |
| Target Variable | FRI v2 (future) |
| Missing Values | Original missing values are intentionally preserved through Sprint v2.1 |
| Duplicate Values | 0 expected |
| Dataset Checksum | Placeholder: `TO_BE_RECORDED_BEFORE_IMPLEMENTATION` |

## Frozen Feature List

| Feature | Role | Expected Data Type |
|---------|------|--------------------|
| `RR` | Daily rainfall trigger | Numeric |
| `Rain7` | Seven-day accumulated rainfall | Numeric |
| `RH_avg` | Average relative humidity | Numeric |
| `Tavg` | Average temperature | Numeric |

## Frozen Dataset State

The frozen BMKG dataset remains unchanged for FRI v2.

| Property | Frozen State |
|----------|--------------|
| Dataset mutation | Forbidden |
| Record count | 726 records |
| Date range | 2024-07-01 to 2026-06-26 |
| Original missing values | Preserved |
| Cleaning changes | Not allowed |
| Merge changes | Not allowed |
| Preprocessing | Not executed before Sprint v2.3 |

## Feature Engineering State (Sprint v2.1)

Sprint v2.1 performs feature engineering only. It computes or selects the FRI v2 feature set and does not perform preprocessing.

| Feature | Expected Missing Values | Status For Sprint v2.1 |
|---------|-------------------------|------------------------|
| `RR` | 74 | Valid; inherited from frozen BMKG dataset |
| `Rain7` | 0 | Valid; computed by 7-day rolling rainfall sum with `min_periods=1` |
| `RH_avg` | 5 | Valid; inherited from frozen BMKG dataset |
| `Tavg` | 5 | Valid; inherited from frozen BMKG dataset |

Sprint v2.1 explicitly does not apply median imputation, interpolation, normalization, standardization, scaling, clipping, encoding, or outlier removal. Missing values are expected to remain identical to the frozen BMKG dataset for retained source features.

## Preprocessing State (Sprint v2.3)

Preprocessing is not part of Sprint v2.1. Median imputation is scheduled only for Sprint FRI v2.3 during dataset preparation for machine learning.

Sprint v2.3 preprocessing will:

- Preserve chronological ordering.
- Apply median imputation.
- Perform chronological 80/20 split.
- Keep `shuffle=False`.
- Prepare the dataset for Google Colab training.

No preprocessing is allowed before Sprint v2.3.

## Excluded From FRI v2 Validation Features

The following variables must not be used as FRI v2 validation features:

- `Rain3`
- `Rain14`
- `TempRange`
- `RainfallAnomaly`

## Expected Statistics

| Statistic | Expected Rule |
|-----------|---------------|
| Record count | Exactly 726 |
| Date minimum | `2024-07-01` |
| Date maximum | `2026-06-26` |
| Duplicate rows | 0 |
| Missing values in validation features | Preserved from frozen BMKG dataset: `RR` = 74, `Rain7` = 0, `RH_avg` = 5, `Tavg` = 5 |
| Feature count | Exactly 4 retained FRI v2 features |
| Feature names | Must exactly match `RR`, `Rain7`, `RH_avg`, `Tavg` |
| Feature data types | Numeric and unchanged from validated dataset schema |
| Target | `FRI v2` is future-generated only after scoring sprint approval |

## Validation Checklist

- [ ] Record count unchanged.
- [ ] Date range unchanged.
- [ ] Duplicate = 0.
- [ ] Missing values match the frozen BMKG dataset.
- [ ] No new missing values introduced.
- [ ] Existing missing values remain unchanged.
- [ ] Median imputation has NOT been executed.
- [ ] Data types unchanged.
- [ ] Feature names unchanged.
- [ ] Dataset checksum recorded.

## Validation Rules

- Validation must be read-only.
- Validation must not rewrite dataset files.
- Validation must not run cleaning or merge scripts.
- Validation must not add historical data.
- Validation must not generate model artifacts.
- Validation must not execute preprocessing before Sprint v2.3.

## Scientific Note

The preservation of missing values until Sprint FRI v2.3 is intentional. This ensures that Feature Engineering and Preprocessing remain isolated implementation layers.

Maintaining this separation preserves the scientific validity of the FRI v2 migration by ensuring that only one methodological component changes per sprint.

## Cross-References

- `01_SPECIFICATION.md` defines the FRI v2 dataset and feature constraints.
- `04_BOUNDARY.md` forbids dataset, cleaning, and merge changes.
- `07_IMPLEMENTATION_RULES.md` requires dataset immutability.
- `10_DEPENDENCY_MAP.md` documents downstream impacts of dataset and feature changes.
