# Sprint 4.1A — FRI Weight Sensitivity Report

## Version

4.1A — Sensitivity Analysis

## Status

✅ Weight Recommendation Approved

## Configurations Evaluated

| Config | Description | RR | Rain7 | RH_avg | Tavg |
|--------|-------------|----|-------|--------|------|
| A | Current production (Rain7-dominant) | 10% | 50% | 30% | 10% |
| B | Equal weight (v3 candidate) | 25% | 25% | 25% | 25% |
| C | Balanced rainfall, moderate secondary | 30% | 30% | 20% | 20% |
| D | RR-heavy with equal secondary | 35% | 25% | 20% | 20% |
| E | Moderate Rain7, balanced secondary | 20% | 40% | 20% | 20% |
| F | V2-like with reduced Rain7, higher RH | 15% | 35% | 30% | 20% |
| G | RR-dominant (inverse of v2) | 40% | 20% | 20% | 20% |
| H | Moderate Rain7, equal secondary | 20% | 30% | 30% | 20% |
| I | Rain7-heavy, reduced secondary | 25% | 35% | 20% | 20% |

## Statistical Comparison

| Config | Mean | Std | CV | Min | Max | Range | Skewness | Kurtosis |
|--------|------|-----|-----|-----|------|-------|----------|----------|
| A | 45.40 | 18.68 | 0.4115 | 8.50 | 86.56 | 78.05 | -0.1457 | -1.0238 |
| B | 41.64 | 12.53 | 0.3010 | 8.50 | 75.78 | 67.27 | 0.1717 | -0.6257 |
| C | 39.92 | 14.30 | 0.3583 | 8.50 | 80.10 | 71.60 | 0.2605 | -0.6710 |
| D | 38.55 | 14.10 | 0.3657 | 8.50 | 80.36 | 71.86 | 0.4180 | -0.5134 |
| E | 42.67 | 15.08 | 0.3535 | 8.50 | 79.58 | 71.07 | -0.0085 | -0.9388 |
| F | 44.38 | 14.44 | 0.3253 | 8.50 | 79.01 | 70.50 | -0.0799 | -0.9256 |
| G | 37.19 | 14.03 | 0.3774 | 8.50 | 80.62 | 72.12 | 0.5724 | -0.3649 |
| H | 43.00 | 13.97 | 0.3249 | 8.50 | 79.27 | 70.76 | 0.0269 | -0.8332 |
| I | 41.29 | 14.63 | 0.3544 | 8.50 | 79.84 | 71.34 | 0.1147 | -0.8174 |

## Risk Class Distribution

| Config | Low | Low% | Medium | Med% | High | High% |
|--------|-----|------|--------|------|------|-------|
| A | 205 | 28.2% | 404 | 55.6% | 117 | 16.1% |
| B | 200 | 27.5% | 506 | 69.7% | 20 | 2.8% |
| C | 249 | 34.3% | 445 | 61.3% | 32 | 4.4% |
| D | 283 | 39.0% | 415 | 57.2% | 28 | 3.9% |
| E | 216 | 29.8% | 469 | 64.6% | 41 | 5.6% |
| F | 180 | 24.8% | 495 | 68.2% | 51 | 7.0% |
| G | 316 | 43.5% | 385 | 53.0% | 25 | 3.4% |
| H | 199 | 27.4% | 491 | 67.6% | 36 | 5.0% |
| I | 229 | 31.5% | 459 | 63.2% | 38 | 5.2% |

## Key Statistical Findings

1. **Rain7 has the highest score variance** (778.7) — 1.2× Tavg, 1.3× RH_avg, 1.5× RR.

2. **Tavg has the lowest score variance** (636.4) — increasing its weight from 10% to 25% (as in equal-weight) dilutes overall spread.

3. **RR-Rain7 correlation** (0.468) confirms they share substantial information, supporting reduced combined weight.

4. **Configuration A (v2)** — widest spread (σ=18.68), but Rain7 alone controls 50% of the index.

5. **Configuration B (equal weight)** — narrowest spread (σ=12.53), High class collapses to 2.8%.

6. **Configuration F (15/35/30/20)** — best High-risk retention (7.0%) among non-v2 configs. Rain7 reduced from 50% to 35%, RH_avg maintained at 30%.

## Feature Contribution Analysis

### Score Variance (Drives Distribution Width)

| Variable | Score Variance | Contribution to v2 | Contribution to F |
|----------|---------------|--------------------|--------------------|
| score_RR | 516.1 | 51.6 | 77.4 |
| score_Rain7 | 778.7 | 389.4 | 272.6 |
| score_RH_avg | 598.7 | 179.6 | 179.6 |
| score_Tavg | 636.4 | 63.6 | 127.3 |

### Missing Data Impact

RR has the most missing values (10.2%), which affects FRI computation on days without rainfall data.

## Recommended Weighting

**Configuration F**: RR=15%, Rain7=35%, RH_avg=30%, Tavg=20%

This configuration achieves:
- Std = 14.44 (adequate variance for ML training)
- High-risk = 7.0% (best extreme-value signal among non-v2 configs)
- No single variable exceeds 35% (Rain7 capped at 35%)
- Combined rainfall (RR+Rain7) = 50% (reduced from 60%)
- Secondary variables (RH_avg+Tavg) = 50% (increased from 40%)

## Files Created

- `docs/research/fri_v3/09_WEIGHT_SENSITIVITY_ANALYSIS.md`
- `docs/research/fri_v3/10_FEATURE_CONTRIBUTION_ANALYSIS.md`
- `docs/research/fri_v3/11_WEIGHT_COMPARISON_TABLE.csv`
- `docs/research/fri_v3/12_FINAL_WEIGHT_RECOMMENDATION.md`
- `docs/research/fri_v3/SPRINT_4.1A_SENSITIVITY_REPORT.md`

## Limitations

1. Distribution analysis alone cannot confirm ML performance. Model training is required.
2. Optimal weights may differ under different scoring functions or threshold methodologies.
3. The 726-record dataset may not capture long-term climatological variance patterns.

## Next Step

1. Generate FRI target using Configuration F (RR=15%, Rain7=35%, RH_avg=30%, Tavg=20%).
2. Train Random Forest on the new target.
3. Evaluate against v2 baseline.
4. If MAE/R² are acceptable, proceed to production deployment.
