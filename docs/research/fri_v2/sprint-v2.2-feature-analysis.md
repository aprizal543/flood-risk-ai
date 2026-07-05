# Sprint v2.2 Feature Relationship Analysis

## Objective

Evaluate relationships between approved FRI v2 features and `FRI_v2` before machine-learning preparation. This analysis is read-only and uses the already generated `data/processed/bmkg_fri_v2.csv`.

## Feature Relationship Figures

Generated review figures:

- `sprint-v2.2-scatter-rain7-fri-v2.png`
- `sprint-v2.2-scatter-rr-fri-v2.png`
- `sprint-v2.2-scatter-rh-avg-fri-v2.png`
- `sprint-v2.2-scatter-tavg-fri-v2.png`
- `sprint-v2.2-feature-scatter-matrix.png`

## Correlation Matrix

| Variable | RR | Rain7 | RH_avg | Tavg | FRI_v2 |
|----------|----|-------|--------|------|--------|
| `RR` | 1.0000 | 0.4605 | 0.3308 | -0.3222 | 0.5243 |
| `Rain7` | 0.4605 | 1.0000 | 0.4613 | -0.3383 | 0.8685 |
| `RH_avg` | 0.3308 | 0.4613 | 1.0000 | -0.8109 | 0.6865 |
| `Tavg` | -0.3222 | -0.3383 | -0.8109 | 1.0000 | -0.4684 |
| `FRI_v2` | 0.5243 | 0.8685 | 0.6865 | -0.4684 | 1.0000 |

The correlation structure agrees with the intended weighting. `Rain7` has the strongest relationship with `FRI_v2`, followed by `RH_avg`, then `RR`, with `Tavg` acting as a weaker inverse-supporting signal.

## Rain7 vs FRI_v2

Status: PASS

Figure: `sprint-v2.2-scatter-rain7-fri-v2.png`

| Metric | Value |
|--------|-------|
| Correlation with `FRI_v2` | 0.8685 |
| Direction | Strong positive |
| Expected Behaviour | Higher weekly accumulated rainfall should increase flood-risk index |

`Rain7` shows the strongest relationship with `FRI_v2`, which is scientifically expected because `Rain7` carries the dominant 50% weight. The relationship supports the principle that antecedent rainfall accumulation is the main flood-formation driver.

Possible anomalies:

- Some records with moderate `Rain7` still reach elevated FRI values because humidity contributes 30%.
- Very high `Rain7` values do not always produce maximum FRI values because `RR`, `RH_avg`, and `Tavg` still participate in the weighted score.

## RR vs FRI_v2

Status: PASS

Figure: `sprint-v2.2-scatter-rr-fri-v2.png`

| Metric | Value |
|--------|-------|
| Correlation with `FRI_v2` | 0.5243 |
| Direction | Moderate positive |
| Expected Behaviour | Daily rainfall should influence risk but should not override accumulated rainfall |

`RR` has a positive relationship with `FRI_v2`, but the relationship is weaker than `Rain7`. This is consistent with the approved 10% weight and supports the design decision that a single daily rainfall observation should not dominate the flood-risk target.

Possible anomalies:

- High daily rainfall can appear at moderate FRI values when antecedent weekly rainfall and humidity are lower.
- Low daily rainfall can still appear at elevated FRI values when `Rain7` remains high from previous days.

## RH_avg vs FRI_v2

Status: PASS

Figure: `sprint-v2.2-scatter-rh-avg-fri-v2.png`

| Metric | Value |
|--------|-------|
| Correlation with `FRI_v2` | 0.6865 |
| Direction | Strong positive |
| Expected Behaviour | Higher humidity should support elevated flood-risk conditions |

`RH_avg` has a strong positive relationship with `FRI_v2`, consistent with its 30% weight. This supports the scientific role of humidity as a persistence and atmospheric moisture indicator.

Possible anomalies:

- High humidity without high rainfall accumulation does not always produce high FRI values, which is expected because humidity contributes but does not dominate.
- Humidity is strongly inversely correlated with `Tavg` (-0.8109), so future model preparation should monitor multicollinearity, although Random Forest can generally tolerate correlated predictors.

## Tavg vs FRI_v2

Status: PASS

Figure: `sprint-v2.2-scatter-tavg-fri-v2.png`

| Metric | Value |
|--------|-------|
| Correlation with `FRI_v2` | -0.4684 |
| Direction | Moderate inverse |
| Expected Behaviour | Temperature should act as a supporting environmental signal |

`Tavg` shows a moderate inverse relationship with `FRI_v2`. This is scientifically plausible in the local meteorological context because lower average temperatures may coincide with cloudy, humid, rainy conditions, while hotter days often correspond to lower humidity and lower rainfall persistence.

Possible anomalies:

- The frozen specification assigns `Tavg` a positive scoring contribution, but the observed empirical relationship with FRI is inverse because `Tavg` is strongly negatively correlated with `RH_avg` and moderately negatively correlated with rainfall variables.
- This is not a blocking issue because `Tavg` has only 10% weight, but Sprint v2.6 scientific evaluation should revisit whether the `Tavg` scoring direction remains optimal.

## Feature Ranges

| Feature | Count | Mean | Std | Min | Q1 | Median | Q3 | Max |
|---------|-------|------|-----|-----|----|--------|----|-----|
| `RR` | 652 | 9.3394 | 17.7449 | 0.0000 | 0.0000 | 0.8000 | 11.0750 | 115.8000 |
| `Rain7` | 726 | 58.4165 | 53.0357 | 0.0000 | 15.8750 | 47.1000 | 85.9500 | 297.6000 |
| `RH_avg` | 721 | 81.2702 | 6.1579 | 63.0000 | 77.0000 | 81.0000 | 86.0000 | 98.0000 |
| `Tavg` | 721 | 27.3333 | 1.1751 | 23.5000 | 26.5000 | 27.4000 | 28.2000 | 30.0000 |

## Scientific Conclusion

The feature relationships are consistent with the approved FRI v2 methodology. `Rain7` dominates, `RH_avg` contributes strongly but secondarily, `RR` influences without overriding accumulation, and `Tavg` remains a limited supporting variable.

The only scientific point to monitor is the inverse empirical relationship between `Tavg` and `FRI_v2`. This does not block Sprint v2.3, but it should be documented in later scientific evaluation because temperature directionality can affect interpretation.

## Recommendation

Approved for Sprint FRI v2.3 Dataset Preparation, with the minor recommendation that model evaluation later report whether `Tavg` improves or weakens predictive performance.
