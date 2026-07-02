# Rainfall Anomaly Specification

## Objective

This document specifies the rainfall anomaly calculation methodology for the Flood Risk Index system. It evaluates multiple approaches, recommends the most appropriate method given the constraints of a two-year BMKG dataset, and defines how rainfall anomaly integrates into the feature engineering and FRI computation pipelines.

---

## Why Rainfall Anomaly Is Required

### Motivation

Raw daily rainfall (RR) captures absolute precipitation intensity but fails to convey whether a given rainfall amount is *normal* or *unusual* for the location and time period. Two identical rainfall values may carry different risk implications:

- 30 mm during the peak of wet season → expected, drainage infrastructure prepared
- 30 mm during the dry season → anomalous, catchment unprepared, higher effective flood risk

Rainfall anomaly provides a **relative measure** that contextualises observed rainfall against a baseline expectation, enabling the FRI to distinguish between climatologically normal wet conditions and genuinely anomalous events.

### Role in the FRI System

| Purpose | Mechanism |
|---------|-----------|
| Contextualise daily rainfall | Identify whether observed precipitation deviates from expected norms |
| Improve discrimination | Separate routine wet-season rainfall from genuinely anomalous events |
| Support feature engineering | Provide an additional derived variable for ML models |
| Enhance scientific rigour | Align with standard meteorological practice of anomaly-based analysis |

### Relationship to Existing Variables

Rainfall anomaly complements—rather than replaces—the existing rainfall features:

| Variable | What It Captures | Temporal Scale |
|----------|-----------------|----------------|
| RR | Absolute daily intensity | Single day |
| Rain3/7/14 | Accumulated volume | Multi-day |
| **Rainfall Anomaly** | Deviation from expected baseline | Relative to reference period |

---

## Comparison of Anomaly Calculation Approaches

### Approach 1: Monthly Climatology

**Method**: Compute monthly mean rainfall, then calculate anomaly as deviation from the corresponding month's mean.

```
anomaly(t) = RR(t) - mean_monthly(month(t))
```

**Advantages**:
- Simple and interpretable
- Standard meteorological approach (used by BMKG, WMO)
- Captures seasonal cycle

**Disadvantages for this dataset**:
- Requires multi-year record for robust monthly means (WMO standard: 30 years)
- With only ~2 years, each month has only 2 samples for mean estimation
- Cannot distinguish within-month variability (early vs. late month)

**Assessment**: Unsuitable as primary method due to insufficient record length for stable monthly climatology.

---

### Approach 2: Rolling Mean

**Method**: Compute a rolling (moving) average over a defined window and calculate anomaly as deviation from that local average.

```
anomaly(t) = RR(t) - rolling_mean(RR, window=N)(t)
```

**Advantages**:
- Adapts to local trends
- No requirement for multi-year data
- Captures recent baseline conditions

**Disadvantages**:
- Window size selection is arbitrary
- Short windows are noisy; long windows smooth out real variability
- Cannot distinguish seasonal norms from transient wet/dry spells
- Rolling mean includes the current observation if not offset (information leakage concern)

**Assessment**: Viable for capturing short-term deviations but lacks climatological grounding. Better suited as a complementary feature than as the primary anomaly definition.

---

### Approach 3: Z-Score (Standardised Anomaly)

**Method**: Compute anomaly as the number of standard deviations from the mean.

```
z_score(t) = (RR(t) - μ) / σ
```

Where μ and σ are computed from the full dataset or a rolling/monthly window.

**Advantages**:
- Scale-invariant (dimensionless)
- Standard statistical measure
- Enables comparison across variables

**Disadvantages for this dataset**:
- Assumes approximately normal distribution; daily rainfall is highly skewed (many zeros, heavy right tail)
- Zero-inflation violates normality assumptions
- σ estimation unreliable with short records
- Z-score can be misleading for non-Gaussian distributions

**Assessment**: Inappropriate for daily rainfall which is strongly non-normal (zero-inflated, right-skewed). Normalisation assumptions are violated, producing misleading standardised values.

---

### Approach 4: Percentile-Based Anomaly

**Method**: Express each observation's position within the empirical cumulative distribution, optionally conditioned on season or month.

```
anomaly_percentile(t) = percentile_rank(RR(t), reference_distribution)
```

Or as deviation from median:
```
anomaly(t) = RR(t) - P50(reference_distribution)
```

**Advantages**:
- Distribution-free (no normality assumption)
- Robust to skewness and zero-inflation
- Directly interpretable ("this rainfall is higher than X% of observations")
- Consistent with the percentile-based scoring already adopted for the FRI

**Disadvantages**:
- Percentile ranks compress extreme values (P95 and P99 both map to "high")
- With limited data, percentile resolution is coarse
- Conditional percentiles (per-month) would have very small sample sizes (~60 days per month)

**Assessment**: Most appropriate for this dataset and methodologically consistent with the FRI scoring framework.

---

## Method Comparison Summary

| Criterion | Monthly Climatology | Rolling Mean | Z-Score | Percentile |
|-----------|:------------------:|:------------:|:-------:|:----------:|
| Works with 2-year record | ✗ | ✓ | ✗ | ✓ |
| Handles zero-inflation | ✓ | ✓ | ✗ | ✓ |
| Handles skewed distribution | ✓ | ✓ | ✗ | ✓ |
| Captures seasonality | ✓ | Partially | Partially | Conditionally |
| Methodological consistency with FRI | — | — | — | ✓ |
| Interpretability | High | Medium | Medium | High |
| Statistical robustness | Low (n≈2/month) | Medium | Low | Medium-High |

---

## Recommended Approach

### Primary Method: Unconditional Percentile Rank

The rainfall anomaly for the FRI system shall use the **percentile rank** of each daily rainfall value within the full dataset distribution:

```
rain_anomaly_pct(t) = percentile_rank(RR(t), all_valid_RR) × 100
```

This produces a value in [0, 100] representing where today's rainfall falls relative to the historical distribution.

### Justification

1. **Methodological consistency**: The FRI scoring layer already uses percentile-based transformations for Rain3, Rain7, Rain14, RH_avg, and TempRange. Using the same approach for rainfall anomaly maintains internal coherence.

2. **Distribution-free**: No parametric assumptions about rainfall distribution. This is essential given that daily rainfall in Pekanbaru is zero-inflated (many dry days) with a heavy right tail (occasional extreme events).

3. **Feasible with available data**: Unconditional percentiles computed from ~726 valid daily observations provide reasonable resolution (each percentile point represents ~7 observations). Conditional (per-month) percentiles are avoided due to small per-month sample sizes.

4. **Interpretable**: A rain_anomaly_pct of 90 means "today's rainfall exceeded 90% of all observed days"—directly meaningful to both researchers and practitioners.

5. **Bounded output**: The [0, 100] range integrates naturally with other FRI components without requiring separate normalisation.

### Complementary Method: Rolling Mean Deviation

As a secondary feature for ML models (not directly in FRI scoring), a rolling mean deviation provides additional signal about short-term regime shifts:

```
rain_deviation_30d(t) = RR(t) - rolling_mean(RR, window=30, min_periods=7)(t-1)
```

Note: The rolling window excludes the current day (offset by 1) to prevent information leakage.

---

## Integration into FRI System

### Feature Engineering Stage

The rainfall anomaly is computed during Sprint 3 (Feature Engineering) as a derived variable:

| Feature | Formula | Output Range |
|---------|---------|--------------|
| `rain_anomaly_pct` | percentile_rank(RR, all_valid_RR) × 100 | [0, 100] |
| `rain_deviation_30d` | RR - rolling_mean(RR, 30d, shifted) | Unbounded (mm) |

### FRI Scoring Stage

The `rain_anomaly_pct` is **not** separately scored in the FRI because:
1. It is derived from RR, which is already scored using BMKG categories
2. Including both would double-count the same physical quantity
3. The percentile-based nature of rain_anomaly_pct means it is effectively pre-scored

However, `rain_anomaly_pct` serves as:
- An **ML feature** for models predicting FRI from raw inputs
- A **diagnostic indicator** for identifying unusual events in EDA
- A **contextual variable** in the decision logic layer (explaining *why* risk is elevated)

### FRI Scoring vs. ML Features

```
┌─────────────────────────────────────────────────────┐
│  FRI Scoring Variables (deterministic index):        │
│    RR, Rain3, Rain7, Rain14, RH_avg, TempRange      │
│                                                       │
│  ML Feature Set (predictive model, superset):        │
│    All FRI variables + rain_anomaly_pct +            │
│    rain_deviation_30d + Month + ...                  │
└─────────────────────────────────────────────────────┘
```

---

## Limitations of the Chosen Approach

1. **No seasonal conditioning**: Unconditional percentiles do not distinguish between wet-season and dry-season baselines. A rainfall value at P70 during peak wet season may be routine, while the same percentile during dry season is anomalous. This is acceptable because seasonal context is partially captured by the accumulation variables (Rain7, Rain14).

2. **Limited extreme resolution**: With ~726 observations, percentile resolution at the tails is coarse (P99 represents ~7 days). Truly extreme events cannot be finely differentiated.

3. **Static reference**: Percentiles are computed once from the training dataset. If the system operates on new data beyond the training period, percentiles may need updating.

---

## Relationship to Thesis

| Section | Thesis Chapter | Purpose |
|---------|---------------|---------|
| Method comparison | Chapter III §3.x (Metode Pengolahan Data) | Justifies methodological choice |
| Recommendation rationale | Chapter III §3.x (Justifikasi Metode) | Explains why alternatives were rejected |
| Integration with FRI | Chapter III §3.x (Arsitektur Sistem) | Positions anomaly within overall system |
| Limitations | Chapter V §5.x (Keterbatasan Penelitian) | Acknowledges constraints |
