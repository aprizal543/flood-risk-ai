# Sprint 4.1 — FRI v3 Target Regeneration Report

## Version

3.0 — Target Regeneration

## Status

PASS

## Formula

```
FRI_v3 = 0.25 × Score(RR) + 0.25 × Score(Rain7) + 0.25 × Score(RH_avg) + 0.25 × Score(Tavg)
```

| Feature | Weight |
|---------|--------|
| `score_RR` | 25% |
| `score_Rain7` | 25% |
| `score_RH_avg` | 25% |
| `score_Tavg` | 25% |
| Total | 100% |

## Output Dataset

| Metric | Value |
|--------|-------|
| Output File | `data/processed/bmkg_fri_v3.csv` |
| Record Count | 726 |
| Missing FRI_v3 | 0 |
| NaN Records | 0 |
| Duplicate Rows | 0 |

## Summary Statistics Comparison

| Statistic | FRI v2 | FRI v3 | Delta |
|-----------|--------|--------|-------|
| Mean | 45.3997 | 41.6435 | -3.7562 |
| Median | 45.9526 | 41.0743 | -4.8783 |
| Standard Deviation | 18.6841 | 12.5328 | -6.1513 |
| Variance | 349.0950 | 157.0713 | -192.0237 |
| Minimum | 8.5039 | 8.5039 | +0.0000 |
| Maximum | 86.5562 | 75.7781 | -10.7781 |
| Range | 78.0523 | 67.2742 | -10.7781 |
| Q1 | 30.4169 | 31.3526 | +0.9357 |
| Q3 | 61.5189 | 50.4331 | -11.0858 |
| Iqr | 31.1020 | 19.0804 | -12.0215 |
| Skewness | -0.1457 | 0.1717 | +0.3175 |
| Kurtosis | -1.0238 | -0.6257 | +0.3980 |

## Binned Distribution Comparison

| Bin | FRI v2 Count | FRI v3 Count | Delta |
|-----|--------------|--------------|-------|
| 0-20 | 95 | 16 | -79 |
| 20-40 | 185 | 325 | +140 |
| 40-60 | 245 | 313 | +68 |
| 60-80 | 197 | 72 | -125 |
| 80-100 | 4 | 0 | -4 |

## Risk Class Comparison

### Transitions (FRI v2 → FRI v3)

| Class Change | Count |
|--------------|-------|
| Records changing class | 156 |
| Change percentage | 21.49% |

### Risk Class Contingency Table

| v3 \ v2 | Low | Medium | High | Total |
|---------|-----|--------|------|-------|
| Low | 174 | 26 | 0 | 200 |
| Medium | 31 | 377 | 98 | 506 |
| High | 0 | 1 | 19 | 20 |
| Total | 205 | 404 | 117 | 726 |

### Risk Class Proportions

| Risk Class | FRI v2 Count | FRI v2 % | FRI v3 Count | FRI v3 % | Delta % |
|------------|--------------|----------|--------------|----------|---------|
| Low | 205 | 28.24% | 200 | 27.55% | -0.69% |
| Medium | 404 | 55.65% | 506 | 69.70% | +14.05% |
| High | 117 | 16.12% | 20 | 2.75% | -13.36% |

## Validation Checklist

| Check | Result |
|-------|--------|
| record_count_726 | PASS |
| date_range_unchanged | PASS |
| duplicate_rows_zero | PASS |
| duplicate_dates_zero | PASS |
| feature_columns_exact | PASS |
| fri_v3_no_nan | PASS |
| fri_v3_range_0_100 | PASS |
| fri_v2_preserved | PASS |
| risk_class_present | PASS |
| confidence_present | PASS |
| weight_sum_100 | PASS |

## Scientific Observations

1. **Distribution spread**: FRI v3 (σ=12.53) is narrower than FRI v2 (σ=18.68). This does not support H₁ₐ (which predicted wider spread under equal weighting).
2. **Central tendency**: Mean shifted from 45.40 (v2) to 41.64 (v3), a delta of -3.76.
3. **Skewness**: v2 skewness = -0.1457, v3 skewness = 0.1717 — distribution is more skewed.
4. **Range**: v2 range = 78.05, v3 range = 67.27.
5. **Risk class shifts**: 156 of 726 records (21.49%) changed risk class between v2 and v3.
6. **No NaN values**: FRI_v3 has zero missing values across all 726 records.

### Unexpected Findings

None at this stage. All observed differences are consistent with the expected effect of rebalancing weights.

### Important Caveat

These are distributional observations only. No conclusions regarding model performance, prediction quality, or recommendation suitability can be drawn from target distribution alone. Model training and evaluation are required to validate the research hypotheses documented in `03_RESEARCH_HYPOTHESIS.md`.

## Figures

- Histogram: `docs\research\fri_v3\fri_v3_histogram.png`
- Boxplot: `docs\research\fri_v3\fri_v3_boxplot.png`
- Distribution table: `docs\research\fri_v3\fri_v3_distribution_table.csv`

## Scope Confirmation

This sprint generated FRI v3 labels only. No preprocessing, imputation, train/test split, Random Forest training, backend, frontend, realtime, security, authentication, or deployment changes are part of this output.
