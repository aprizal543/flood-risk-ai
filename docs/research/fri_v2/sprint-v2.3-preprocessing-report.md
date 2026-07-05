# Sprint v2.3 Preprocessing Report

## Methodology

Sprint v2.3 prepares the FRI v2 machine-learning dataset using median imputation on feature columns only, followed by a chronological 80/20 split with `shuffle=False`.

No mean, mode, interpolation, KNN, MICE, forward fill, backward fill, row drop, column drop, model training, or model evaluation is used.

## Feature And Target Schema

| Role | Columns |
|------|---------|
| Features | `RR`, `Rain7`, `RH_avg`, `Tavg` |
| Target | `FRI_v2` |
| Non-imputed Identifier | `Date` |

## Missing Values Before And After

| Column | Before | After |
|--------|--------|-------|
| `Date` | 0 | 0 |
| `RR` | 74 | 0 |
| `Rain7` | 0 | 0 |
| `RH_avg` | 5 | 0 |
| `Tavg` | 5 | 0 |
| `FRI_v2` | 0 | 0 |

## Median Values Applied

| Feature | Median |
|---------|--------|
| `RR` | 0.800000 |
| `Rain7` | 47.100000 |
| `RH_avg` | 81.000000 |
| `Tavg` | 27.400000 |

## Dataset Dimensions

| Dataset | Rows | Columns | Date Range |
|---------|------|---------|------------|
| Full processed dataset | 726 | 6 | 2024-07-01 to 2026-06-26 |
| Train dataset | 581 | 6 | 2024-07-01 to 2026-02-01 |
| Test dataset | 145 | 6 | 2026-02-02 to 2026-06-26 |

## Feature Statistics Before Preprocessing

| Feature | Mean | Std | Min | Median | Max |
|---------|------|-----|-----|--------|-----|
| `RR` | 9.339417 | 17.744856 | 0.000000 | 0.800000 | 115.800000 |
| `Rain7` | 58.416529 | 53.035699 | 0.000000 | 47.100000 | 297.600000 |
| `RH_avg` | 81.270180 | 6.157893 | 63.000000 | 81.000000 | 98.000000 |
| `Tavg` | 27.333287 | 1.175113 | 23.500000 | 27.400000 | 30.000000 |
| `FRI_v2` | 45.399672 | 18.684084 | 8.503937 | 45.952602 | 86.556225 |

## Feature Statistics After Preprocessing

| Feature | Mean | Std | Min | Median | Max |
|---------|------|-----|-----|--------|-----|
| `RR` | 8.469008 | 17.012490 | 0.000000 | 0.800000 | 115.800000 |
| `Rain7` | 58.416529 | 53.035699 | 0.000000 | 47.100000 | 297.600000 |
| `RH_avg` | 81.268320 | 6.136663 | 63.000000 | 81.000000 | 98.000000 |
| `Tavg` | 27.333747 | 1.171067 | 23.500000 | 27.400000 | 30.000000 |
| `FRI_v2` | 45.399672 | 18.684084 | 8.503937 | 45.952602 | 86.556225 |

## Only Missing Values Changed

All non-missing feature values are unchanged. `Date` and `FRI_v2` are unchanged. Only missing values in `RR`, `RH_avg`, and `Tavg` were filled with their feature medians; `Rain7` had no missing values.

## Chronological Split Explanation

The split uses the original chronological order with `shuffle=False`. The first 581 records become training data and the final 145 records become test data. No random split, TimeSeriesSplit, KFold, or stratified split is used.

## Ready For Google Colab

`train_dataset_v2.csv`, `test_dataset_v2.csv`, and `preprocessing_metadata_v2.json` are ready to be uploaded to Google Colab for the next approved Random Forest training sprint. No model has been trained in this sprint.
