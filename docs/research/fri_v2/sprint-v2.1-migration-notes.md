# Sprint v2.1 Feature Engineering Migration Notes

## Objective

Document the FRI v2 feature engineering revision without changing the FRI v1 pipeline.

## Retained Features

| Feature | Source | Decision |
|---------|--------|----------|
| `RR` | `rr` from `data/interim/bmkg_clean.csv` | Retained as direct daily rainfall input |
| `Rain7` | 7-day rolling sum of `rr` with `min_periods=1` | Retained as the only engineered rainfall accumulation feature |
| `RH_avg` | `rh_avg` from `data/interim/bmkg_clean.csv` | Retained as humidity input |
| `Tavg` | `tavg` from `data/interim/bmkg_clean.csv` | Retained as average temperature input |

## Removed Features

| Feature | v2 Migration Decision |
|---------|-----------------------|
| `Rain3` | Removed from FRI v2 feature dataset |
| `Rain14` | Removed from FRI v2 feature dataset |
| `TempRange` | Removed and replaced by retained `Tavg` input |
| `RainfallAnomaly` | Removed from FRI v2 feature dataset |

## Output Dataset

`data/processed/bmkg_features_v2.csv` contains exactly four columns in canonical order: `RR`, `Rain7`, `RH_avg`, `Tavg`.

## V1 Preservation

The existing v1 script `scripts/etl/03_feature_engineering.py` and v1 output `data/processed/bmkg_features.csv` are not replaced by this sprint.

## Explicit Non-Scope

This sprint does not implement scoring, aggregation, FRI label generation, Random Forest retraining, backend inference, frontend changes, dashboard changes, security changes, authentication changes, realtime prediction changes, or model replacement.
