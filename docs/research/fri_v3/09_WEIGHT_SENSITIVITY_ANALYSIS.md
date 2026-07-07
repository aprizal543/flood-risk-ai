# FRI Weight Sensitivity Analysis

## Objective

Evaluate how different weighting configurations affect the FRI target distribution. Identify the most scientifically justified configuration for Random Forest training.

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

## Summary Statistics Comparison

| Config | Mean | Median | Std | CV | Min | Max | Range | Skew | Kurt |
|--------|------|--------|-----|-----|-----|------|-------|------|------|
| A | 45.40 | 45.95 | 18.68 | 0.4115 | 8.50 | 86.56 | 78.05 | -0.1457 | -1.0238 |
| B | 41.64 | 41.07 | 12.53 | 0.3010 | 8.50 | 75.78 | 67.27 | 0.1717 | -0.6257 |
| C | 39.92 | 39.19 | 14.30 | 0.3583 | 8.50 | 80.10 | 71.60 | 0.2605 | -0.6710 |
| D | 38.55 | 37.18 | 14.10 | 0.3657 | 8.50 | 80.36 | 71.86 | 0.4180 | -0.5134 |
| E | 42.67 | 43.11 | 15.08 | 0.3535 | 8.50 | 79.58 | 71.07 | -0.0085 | -0.9388 |
| F | 44.38 | 44.49 | 14.44 | 0.3253 | 8.50 | 79.01 | 70.50 | -0.0799 | -0.9256 |
| G | 37.19 | 35.38 | 14.03 | 0.3774 | 8.50 | 80.62 | 72.12 | 0.5724 | -0.3649 |
| H | 43.00 | 42.75 | 13.97 | 0.3249 | 8.50 | 79.27 | 70.76 | 0.0269 | -0.8332 |
| I | 41.29 | 41.30 | 14.63 | 0.3544 | 8.50 | 79.84 | 71.34 | 0.1147 | -0.8174 |

## Risk Class Distribution

| Config | Low | Low % | Medium | Medium % | High | High % |
|--------|-----|-------|--------|----------|------|--------|
| A | 205 | 28.2% | 404 | 55.6% | 117 | 16.1% |
| B | 200 | 27.5% | 506 | 69.7% | 20 | 2.8% |
| C | 249 | 34.3% | 445 | 61.3% | 32 | 4.4% |
| D | 283 | 39.0% | 415 | 57.2% | 28 | 3.9% |
| E | 216 | 29.8% | 469 | 64.6% | 41 | 5.6% |
| F | 180 | 24.8% | 495 | 68.2% | 51 | 7.0% |
| G | 316 | 43.5% | 385 | 53.0% | 25 | 3.4% |
| H | 199 | 27.4% | 491 | 67.6% | 36 | 5.0% |
| I | 229 | 31.5% | 459 | 63.2% | 38 | 5.2% |

## Binned Distribution

| Config | 0-20 | 20-40 | 40-60 | 60-80 | 80-100 |
|--------|------|-------|-------|-------|--------|
| A | 95 | 185 | 245 | 197 | 4 |
| B | 16 | 325 | 313 | 72 | 0 |
| C | 47 | 331 | 268 | 79 | 1 |
| D | 47 | 375 | 233 | 70 | 1 |
| E | 38 | 274 | 309 | 105 | 0 |
| F | 23 | 253 | 327 | 123 | 0 |
| G | 54 | 419 | 184 | 68 | 1 |
| H | 24 | 282 | 325 | 95 | 0 |
| I | 42 | 308 | 287 | 89 | 0 |

## Sensitivity to Weight Changes

Delta from Configuration A (current production):

| Config | Δ Mean | Δ Std | Δ CV | Δ Range | Δ Low % | Δ Med % | Δ High % |
|--------|--------|-------|------|---------|---------|---------|----------|
| B | -3.76 | -6.15 | -0.1105 | -10.78 | -0.69% | +14.05% | -13.36% |
| C | -5.48 | -4.38 | -0.0532 | -6.46 | +6.06% | +5.65% | -11.71% |
| D | -6.85 | -4.58 | -0.0458 | -6.19 | +10.74% | +1.52% | -12.26% |
| E | -2.73 | -3.60 | -0.0580 | -6.98 | +1.52% | +8.95% | -10.47% |
| F | -1.02 | -4.25 | -0.0862 | -7.55 | -3.44% | +12.53% | -9.09% |
| G | -8.21 | -4.65 | -0.0341 | -5.93 | +15.29% | -2.62% | -12.67% |
| H | -2.40 | -4.71 | -0.0866 | -7.29 | -0.83% | +11.98% | -11.16% |
| I | -4.11 | -4.05 | -0.0571 | -6.72 | +3.31% | +7.58% | -10.88% |

## Key Findings

1. **Configuration A (v2)** — widest spread (σ=18.68), most extreme values (max=86.56), but Rain7 alone controls 50%.
2. **Configuration B (equal weight)** — narrowest spread (σ=12.53), High class collapses to 2.8%.
3. **Configurations C, D, G** — produce low High-risk (3.4–4.4%) unsuitable for flood risk.
4. **Configuration F (15/35/30/20)** — best High-risk retention (7.0%) among non-v2 configs. Rain7 reduced from 50% to 35%, RH_avg maintained at 30%.
5. **Configuration E (20/40/20/20)** — highest σ (15.08), but Rain7 still at 40% and High only 5.6%.
6. **Configuration I (25/35/20/20)** — σ=14.63, High=5.2%, but Rain7+RR=60% (same as v2).

## Visualizations

- Histogram panel: `docs\research\fri_v3\fri_sensitivity_histograms.png`
- Boxplot: `docs\research\fri_v3\fri_sensitivity_boxplot.png`
- Density overlay: `docs\research\fri_v3\fri_sensitivity_density.png`
- Risk class bars: `docs\research\fri_v3\fri_sensitivity_risk_bars.png`
