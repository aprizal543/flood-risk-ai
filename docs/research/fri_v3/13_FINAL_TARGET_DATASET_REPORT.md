# Sprint 4.2 — FRI v3 Final Dataset Report (Configuration F)

## Version

3.0 — Final Target Dataset

## Status

PASS

## Formula

```
FRI_v3_Final = 0.15 × Score(RR) + 0.35 × Score(Rain7) + 0.30 × Score(RH_avg) + 0.20 × Score(Tavg)
```

### Configuration F (Selected from Sprint 4.1A Sensitivity Analysis)

| Feature | Weight | Rationale |
|---------|--------|-----------|
| RR | 15% | Daily rainfall trigger (reduced from 10%) |
| Rain7 | 35% | Antecedent saturation (reduced from 50%) |
| RH_avg | 30% | Humidity persistence (unchanged from v2) |
| Tavg | 20% | Thermal context (increased from 10%) |
| **Total** | **100%** | — |


## Output Dataset

| Metric | Value |
|--------|-------|
| Output File | `data/processed/bmkg_fri_v3_final.csv` |
| Configuration | F (RR=15%, Rain7=35%, RH_avg=30%, Tavg=20%) |
| Record Count | 726 |
| Missing FRI_v3_Final | 0 |
| NaN Records | 0 |
| Duplicate Rows | 0 |

## Summary Statistics Comparison

| Statistic | FRI v2 | FRI v3_Final (Config F) | Delta |
|-----------|--------|-------------------------|-------|
| Mean | 45.3997 | 44.3797 | -1.0200 |
| Median | 45.9526 | 44.4895 | -1.4631 |
| Standard Deviation | 18.6841 | 14.4378 | -4.2463 |
| Variance | 349.0950 | 208.4490 | -140.6460 |
| Minimum | 8.5039 | 8.5039 | +0.0000 |
| Maximum | 86.5562 | 79.0060 | -7.5502 |
| Range | 78.0523 | 70.5021 | -7.5502 |
| Q1 | 30.4169 | 33.2646 | +2.8477 |
| Q3 | 61.5189 | 56.1283 | -5.3906 |
| Iqr | 31.1020 | 22.8637 | -8.2383 |
| Skewness | -0.1457 | -0.0799 | +0.0659 |
| Kurtosis | -1.0238 | -0.9256 | +0.0982 |

## Binned Distribution Comparison

| Bin | FRI v2 Count | FRI v3_Final Count | Delta |
|-----|--------------|--------------------|-------|
| 0-20 | 95 | 23 | -72 |
| 20-40 | 185 | 253 | +68 |
| 40-60 | 245 | 327 | +82 |
| 60-80 | 197 | 123 | -74 |
| 80-100 | 4 | 0 | -4 |

## Risk Class Comparison

### Transitions (FRI v2 → FRI v3_Final)

| Class Change | Count |
|--------------|-------|
| Records changing class | 101 |
| Change percentage | 13.91% |

### Risk Class Contingency Table

| v3 \ v2 | Low | Medium | High | Total |
|---------|-----|--------|------|-------|
| Low | 175 | 5 | 0 | 180 |
| Medium | 30 | 399 | 66 | 495 |
| High | 0 | 0 | 51 | 51 |
| Total | 205 | 404 | 117 | 726 |

### Risk Class Proportions

| Risk Class | FRI v2 Count | FRI v2 % | FRI v3_Final Count | FRI v3_Final % | Delta % |
|------------|--------------|----------|--------------|----------|---------|
| Low | 205 | 28.24% | 180 | 24.79% | -3.44% |
| Medium | 404 | 55.65% | 495 | 68.18% | +12.53% |
| High | 117 | 16.12% | 51 | 7.02% | -9.09% |

## Validation Checklist

| Check | Result |
|-------|--------|
| record_count_726 | PASS |
| date_range_unchanged | PASS |
| duplicate_rows_zero | PASS |
| duplicate_dates_zero | PASS |
| feature_columns_exact | PASS |
| fri_v3_final_no_nan | PASS |
| fri_v3_final_range_0_100 | PASS |
| fri_v2_preserved | PASS |
| risk_class_present | PASS |
| confidence_present | PASS |
| weight_sum_100 | PASS |

## Scientific Observations

1. **Distribution spread**: FRI v3_Final (σ=14.44) is narrower than FRI v2 (σ=18.68) but wider than equal-weight Config B (σ=12.53). Configuration F preserves 77% of v2's spread vs. Config B's 67%.
2. **Central tendency**: Mean shifted from 45.40 (v2) to 44.38 (v3_Final), a delta of -1.02.
3. **Skewness**: v2 skewness = -0.1457, v3_Final skewness = -0.0799 — distribution is more symmetric and closer to symmetric.
4. **Range**: v2 range = 78.05, v3_Final range = 70.50.
5. **Risk class shifts**: 101 of 726 records (13.91%) changed risk class between v2 and v3_Final.
6. **No NaN values**: FRI_v3_Final has zero missing values across all 726 records.

### Why Configuration F Is Superior to Configuration B (Equal Weight)

- **High-risk retention**: Config F has more high-risk records vs. Config B's 2.8% collapse. See `11_WEIGHT_COMPARISON_TABLE.csv` for full comparison.
- **Distribution spread**: Config F (σ={f_std:.2f}) preserves substantially more variance than Config B (σ={b_std:.2f}), which is critical for ML training.
- **Tavg contribution limited to 20%**: Config F avoids the artifact-inflated Tavg variance issue (see `10_FEATURE_CONTRIBUTION_ANALYSIS.md`) by capping Tavg at 20%.
- **Rain7 remains primary**: At 35%, Rain7 retains hydrological primacy without dominant control of the index.
- **RH_avg maintained at 30%**: Humidity persistence — a key agricultural risk factor — is preserved at its v2 level.

### Important Caveat

These are distributional observations only. No conclusions regarding model performance, prediction quality, or recommendation suitability can be drawn from target distribution alone. Model training and evaluation are required to validate the research hypotheses documented in `03_RESEARCH_HYPOTHESIS.md`.

## Figures

- Histogram: `docs\research\fri_v3\fri_v3_final_histogram.png`
- Boxplot: `docs\research\fri_v3\fri_v3_final_boxplot.png`
- Distribution table: `docs\research\fri_v3\fri_v3_final_distribution_table.csv`

## Scope Confirmation

This sprint generated the FRI v3 Final dataset (Configuration F) only. No preprocessing, imputation, train/test split, Random Forest training, backend, frontend, realtime, security, authentication, or deployment changes are part of this output.
