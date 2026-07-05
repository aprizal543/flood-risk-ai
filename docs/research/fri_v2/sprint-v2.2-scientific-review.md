# Sprint v2.2 Scientific Review

## Objective

Evaluate whether the generated FRI v2 is a scientifically reasonable flood-risk target before machine-learning dataset preparation. This review is read-only analysis and does not modify source code, datasets, models, backend, frontend, or deployment configuration.

## Reviewed Inputs

- `docs/research/fri_v2/01_SPECIFICATION.md`
- `docs/research/fri_v2/02_ADR.md`
- `docs/research/fri_v2/09_DECISION_LOG.md`
- `docs/research/fri_v2/sprint-v2.2-validation-report.md`
- `docs/research/fri_v2/sprint-v2.2-statistical-analysis.md`
- `docs/research/fri_v2/sprint-v2.2-comparison-v1-v2.md`
- `data/processed/bmkg_fri_v2.csv`
- `docs/research/fri_v2/sprint-v2.2-fri-v2-histogram.png`
- `docs/research/fri_v2/sprint-v2.2-fri-v2-boxplot.png`
- `docs/research/fri_v2/sprint-v2.2-distribution-table.csv`

## Distribution Review

Status: PASS

| Statistic | Value |
|-----------|-------|
| Count | 726 |
| Minimum | 8.5039 |
| Q1 | 30.4169 |
| Median | 45.9526 |
| Q3 | 61.5189 |
| Maximum | 86.5562 |
| Mean | 45.3997 |
| Standard Deviation | 18.6841 |
| Skewness | -0.1457 |
| Kurtosis | -1.0238 |

The distribution is scientifically reasonable for a deterministic flood-risk index. It spans low, medium, and high risk conditions without collapsing into a narrow range. The slight negative skew indicates a modest concentration toward medium-to-higher values, but the skew is small enough that the index remains usable as a continuous target.

The low kurtosis indicates a relatively flat distribution compared with a normal distribution. This is acceptable for a flood-risk index built from rainfall accumulation and humidity because meteorological risk is expected to vary across wet and dry periods rather than cluster tightly around a single central value.

Figure references:

- Histogram: `sprint-v2.2-fri-v2-histogram.png`
- Distribution table: `sprint-v2.2-distribution-table.csv`

## Boxplot Review

Status: PASS

| Boxplot Metric | Value |
|----------------|-------|
| Q1 | 30.4169 |
| Q3 | 61.5189 |
| IQR | 31.1020 |
| Lower Fence | -16.2360 |
| Upper Fence | 108.1719 |
| IQR Outlier Count | 0 |

The boxplot does not indicate statistical outliers under the 1.5 IQR rule. The observed maximum of 86.5562 is high but remains below the upper fence and within the expected 0-100 FRI range. Extreme values appear realistic rather than unstable because they are bounded and rare.

Figure reference:

- Boxplot: `sprint-v2.2-fri-v2-boxplot.png`

## Weight Validation

Status: PASS

| Feature | Weight | Scientific Role |
|---------|--------|-----------------|
| `RR` | 10% | Direct daily rainfall trigger |
| `Rain7` | 50% | Dominant antecedent rainfall signal |
| `RH_avg` | 30% | Atmospheric moisture persistence signal |
| `Tavg` | 10% | Supporting thermal condition signal |
| Total | 100% | Complete deterministic aggregation |

The resulting distribution is consistent with the intended methodology. `Rain7` dominates the index behaviour, humidity provides a strong secondary contribution, and `RR` and `Tavg` remain supporting signals. The output is not dominated by daily rainfall spikes, which is scientifically appropriate because flood formation is usually more dependent on accumulated antecedent rainfall than on a single daily observation.

## Category Review

Status: PASS WITH MINOR RECOMMENDATION

| FRI_v2 Bin | Count | Percentage |
|------------|-------|------------|
| 0-20 | 95 | 13.09% |
| 20-40 | 185 | 25.48% |
| 40-60 | 245 | 33.75% |
| 60-80 | 197 | 27.13% |
| 80-100 | 4 | 0.55% |

| Risk Class | Count | Percentage |
|------------|-------|------------|
| Low | 205 | 28.24% |
| Medium | 404 | 55.65% |
| High | 117 | 16.12% |

The dataset is not too concentrated for regression. Most records fall between 20 and 80, which provides sufficient continuous variation for machine-learning preparation. Extreme high-risk values above 80 are underrepresented, with only 4 records, but this is plausible for observed daily BMKG data because severe flood-risk combinations should be uncommon.

Minor recommendation: Sprint v2.3 should preserve chronological splitting and avoid shuffling so rare high-risk periods are not artificially redistributed. Evaluation should report performance separately for high-risk records because the extreme tail is sparse.

## Scientific Consistency

Status: PASS

FRI v2 satisfies the approved scientific principles:

- Antecedent rainfall dominates flood formation: reflected by `Rain7` weight of 50% and correlation with `FRI_v2` of 0.8685.
- Humidity contributes but does not dominate: reflected by `RH_avg` weight of 30% and correlation with `FRI_v2` of 0.6865.
- Temperature has supporting influence: reflected by `Tavg` weight of 10% and correlation with `FRI_v2` of -0.4684.
- Daily rainfall influences but does not override accumulated rainfall: reflected by `RR` weight of 10% and correlation with `FRI_v2` of 0.5243, lower than `Rain7`.

The implemented weighting reflects the frozen methodology and produces behaviour consistent with hydrometeorological expectations.

## Comparison With FRI v1

Status: PASS

| Metric | Value |
|--------|-------|
| Mean Difference (FRI_v2 - FRI_v1) | +4.8608 |
| Median Difference (FRI_v2 - FRI_v1) | +4.7258 |
| Records With Category Change | 153 |
| Category Change Percentage | 21.07% |

Advantages:

- FRI v2 is more interpretable because it uses four variables instead of the broader v1 feature set.
- Weekly accumulated rainfall is clearly dominant, matching the approved scientific rationale.
- Removed features reduce methodological complexity and possible dilution from overlapping rainfall windows.
- FRI v2 remains bounded, continuous, and complete with no missing `FRI_v2` labels.

Disadvantages:

- Extreme high-risk values are less frequent than in v1, with only 4 records in the 80-100 bin.
- Removing `Rain3`, `Rain14`, `TempRange`, and `RainfallAnomaly` may reduce sensitivity to short bursts, longer antecedent saturation, temperature-range storm proxies, and anomaly context.
- Category changes in 21.07% of records require careful evaluation in Sprint v2.3 and later scientific evaluation.

Expected improvement for Random Forest:

FRI v2 should provide a cleaner and more interpretable target because the target is driven by fewer, better-defined hydrometeorological components. This may reduce noise from overlapping engineered variables, but the sparse extreme tail must be monitored.

Expected improvement for realtime prediction:

FRI v2 is likely easier to reproduce in realtime because it relies on `RR`, `Rain7`, `RH_avg`, and `Tavg`. The dominant `Rain7` signal should improve stability compared with daily-rainfall-heavy behaviour.

Expected improvement for interpretability:

Interpretability improves substantially. The target can be explained as weekly rainfall dominance plus humidity support, with daily rainfall and temperature as secondary signals.

## Final Recommendation

Final verdict: APPROVED WITH MINOR RECOMMENDATIONS

Sprint FRI v2.3 Dataset Preparation may begin.

Minor recommendations for Sprint v2.3:

- Preserve chronological ordering.
- Apply median imputation only in the approved preprocessing sprint.
- Use chronological 80/20 split with `shuffle=False`.
- Report high-risk subset performance because the `80-100` FRI range is sparse.

## Scope Confirmation

This review created documentation and review figures only under `docs/research/fri_v2/`. It did not regenerate FRI, retrain any model, modify datasets, or change backend/frontend/source code.
