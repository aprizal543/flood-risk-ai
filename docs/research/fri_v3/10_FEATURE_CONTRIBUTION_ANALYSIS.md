# Feature Contribution Analysis

## Objective

Analyze the statistical properties of each FRI feature (RR, Rain7, RH_avg, Tavg) to understand why different weighting configurations produce different target distributions.

## 1. Raw Feature Statistics

| Feature | Mean | Std | Variance | CV | Min | Max | Missing | Missing % |
|---------|------|-----|----------|----|-----|------|---------|----------|
| RR | 9.34 | 17.74 | 314.88 | 1.9000 | 0.00 | 115.80 | 74 | 10.2% |
| Rain7 | 58.42 | 53.04 | 2812.79 | 0.9079 | 0.00 | 297.60 | 0 | 0.0% |
| RH_avg | 81.27 | 6.16 | 37.92 | 0.0758 | 63.00 | 98.00 | 5 | 0.7% |
| Tavg | 27.33 | 1.18 | 1.38 | 0.0430 | 23.50 | 30.00 | 5 | 0.7% |

## 2. Score Statistics (0-100 scale)

| Score Variable | Mean | Std | Variance | CV | Min | Max | Missing | Missing % |
|----------------|------|-----|----------|----|-----|------|---------|----------|
| score_RR | 16.13 | 22.72 | 516.09 | 1.4083 | 0.00 | 100.00 | 74 | 10.2% |
| score_Rain7 | 46.80 | 27.91 | 778.73 | 0.5963 | 0.00 | 100.00 | 0 | 0.0% |
| score_RH_avg | 50.16 | 24.47 | 598.75 | 0.4879 | 0.00 | 100.00 | 5 | 0.7% |
| score_Tavg | 50.40 | 25.23 | 636.43 | 0.5005 | 0.00 | 100.00 | 5 | 0.7% |

## 3. Key Findings

### 3.1 Rain7 Has the Largest Variance

Score_Rain7 variance = 778.73 vs Score_RR = 516.09, Score_RH_avg = 598.75, Score_Tavg = 636.43.

Rain7's score variance is 1.5× larger than RR, 1.3× larger than RH_avg, and 1.2× larger than Tavg.

This is the fundamental reason equal weighting compresses the distribution: Rain7's naturally high variance is diluted from 50% to 25%.

### 3.2 RR Score Variance

Score_RR variance (516.09) is the lowest of the four. RR is daily rainfall — it has many zero/low days and occasional spikes. The BMKG scoring function maps 0mm→0, compressing most observations into the 0-20 range.

### 3.3 RH_avg Score Variance

Score_RH_avg variance (598.75) reflects moderate variation in humidity. RH_avg tends to be high during wet periods and lower during dry periods, providing useful but not dominant signal.

### 3.4 Tavg Score Variance — Artificially Inflated by Scoring

Score_Tavg variance (636.43) is the second highest among the four scores. However, this is an artifact of percentile-based scoring: raw Tavg has the lowest natural variance (1.38) of any feature. The percentile transformation (23.5–30.0°C mapped to 0–100) artificially amplifies small temperature differences into large score differences.

This means Tavg's apparent discriminative power in the score space is misleading. A variable with raw variance of only 1.38°C² cannot provide meaningful flood risk discrimination despite its inflated score variance. **This is a strong argument against high Tavg weights.**

## 4. Score Correlation Matrix

| | score_RR | score_Rain7 | score_RH_avg | score_Tavg |
|---|----------|-------------|--------------|------------|
| score_RR | 1.000 | 0.468 | 0.407 | -0.371 |
| score_Rain7 | 0.468 | 1.000 | 0.477 | -0.318 |
| score_RH_avg | 0.407 | 0.477 | 1.000 | -0.790 |
| score_Tavg | -0.371 | -0.318 | -0.790 | 1.000 |

### Information Redundancy

- **RR-Rain7 correlation**: 0.468 — Moderate positive correlation (expected: Rain7 is a cumulative function of RR).
- **RH_avg correlation with rainfall**: Generally moderate — humidity rises during wet periods but is not a direct precipitation measure.
- **Tavg correlation with other variables**: Low — temperature is largely independent of precipitation in tropical settings.

## 5. Why Equal Weighting Compressed the Distribution

The equal-weight configuration (B) reduces Rain7's contribution from 50% to 25%. Since Rain7 has the highest score variance, this reduction directly lowers the aggregate variance. Meanwhile, Tavg (which has the second highest score variance but the lowest raw feature variance) is increased from 10% to 25%. However, Tavg's score variance is an artifact of percentile scoring — its raw variance (1.38) is negligible. The net effect is a narrower distribution concentrated in the medium-risk range.

## 6. Visualizations

- Correlation heatmap: `docs\research\fri_v3\fri_feature_correlation.png`
- Variance comparison: `docs\research\fri_v3\fri_feature_variance.png`
- Score histograms: `docs\research\fri_v3\fri_score_histograms.png`
- Missing values: `docs\research\fri_v3\fri_missing_values.png`
