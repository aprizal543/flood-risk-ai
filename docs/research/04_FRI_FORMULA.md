# FRI Formula

## Overview

This document describes the mathematical formulation of the Flood Risk Index, from individual variable scoring through weighted aggregation to final risk classification.

---

## Pipeline

```
Raw Variable Value
    ↓
Scientific Scoring (0–100)
    ↓
Weighted Aggregation
    ↓
Flood Risk Index (0–100)
    ↓
Risk Classification (Low / Medium / High)
```

---

## Step 1: Scientific Scoring Layer

Each variable x_i is transformed into a risk score S_i ∈ [0, 100].

### 1.1 RR Scoring (BMKG-Based)

The scoring function for daily rainfall uses piecewise linear interpolation across BMKG categories:

```
S_RR(x) =
    0                               if x = 0
    20 × (x / 5)                    if 0 < x ≤ 5       (Hujan ringan)
    20 + 20 × ((x - 5) / 15)       if 5 < x ≤ 20      (Hujan sedang)
    40 + 30 × ((x - 20) / 30)      if 20 < x ≤ 50     (Hujan lebat)
    70 + 20 × ((x - 50) / 50)      if 50 < x ≤ 100    (Hujan sangat lebat)
    100                             if x > 100          (Hujan ekstrem)
```

### 1.2 Percentile-Based Scoring (Rain3, Rain7, Rain14, RH_avg)

For variables without official thresholds, scoring maps the observed value to its position within the empirical cumulative distribution:

```
S_i(x) = percentile_rank(x, distribution_i) × 100
```

Where `distribution_i` is computed from the Pekanbaru cleaned dataset.

Operationally, this is implemented as:
```
S_i(x) = clip(interp(x, [P0, P25, P50, P75, P100], [0, 25, 50, 75, 100]), 0, 100)
```

Percentile anchors (P0, P25, P50, P75, P100) are computed once from the training dataset and stored as configuration.

### 1.3 TempRange Scoring (Inverse Percentile)

TempRange has an inverse relationship with flood risk:

```
S_TempRange(x) = 100 - percentile_rank(x, distribution_TempRange) × 100
```

Lower TempRange → Higher score → Higher risk.

---

## Step 2: Weighted Aggregation

The Flood Risk Index is computed as a weighted linear combination of individual scores:

```
FRI = Σ (w_i × S_i)    for i ∈ {RR, Rain3, Rain7, Rain14, RH_avg, TempRange}
```

### Constraints

1. **Σ w_i = 1.0** (weights sum to unity)
2. **w_RR + w_Rain3 + w_Rain7 + w_Rain14 ≥ 0.60** (rainfall dominance constraint)
3. **w_i > 0 ∀ i** (all variables contribute positively)

### Weight Values

| Variable | Weight | Status |
|----------|--------|--------|
| RR | w₁ = TBD | Pending literature review + EDA |
| Rain3 | w₂ = TBD | Pending literature review + EDA |
| Rain7 | w₃ = TBD | Pending literature review + EDA |
| Rain14 | w₄ = TBD | Pending literature review + EDA |
| RH_avg | w₅ = TBD | Pending literature review + EDA |
| TempRange | w₆ = TBD | Pending literature review + EDA |

### Weight Determination Methodology

Weights will be assigned using one or a combination of:
1. **Expert judgment** informed by hydrometeorological literature
2. **Statistical analysis** (correlation of individual scores with flood indicators)
3. **Sensitivity analysis** (parameter sweep to assess FRI behavior under different weight configurations)

---

## Step 3: Flood Risk Index Output

```
FRI ∈ [0, 100]   (continuous)
```

Properties:
- FRI = 0 when all individual scores are 0 (no risk indicators present)
- FRI = 100 when all individual scores are 100 (all indicators at maximum)
- FRI is monotonically increasing with respect to each score component

---

## Step 4: Risk Classification

```
Category(FRI) =
    "Low"     if FRI ∈ [0, 33]
    "Medium"  if FRI ∈ (33, 66]
    "High"    if FRI ∈ (66, 100]
```

### Classification Threshold Rationale

The tercile-based split (33/66) provides:
- Equal theoretical range per category
- Interpretable boundaries for non-technical stakeholders
- Preliminary values subject to calibration against observed flood events

---

## Handling Missing Values

When one or more input variables have NaN (due to missing observations or removed sentinels):

```
FRI = Σ (w_i × S_i) / Σ w_i    for all i where S_i is not NaN
```

This re-normalizes weights to available variables, maintaining the 0–100 scale. A `confidence` field indicates the fraction of total weight represented:

```
confidence = Σ w_i (available) / Σ w_i (all)
```

Records with confidence below a minimum threshold (e.g., 0.5) are flagged as unreliable.

---

## Mathematical Properties

1. **Bounded**: FRI ∈ [0, 100] by construction (all scores bounded, weights positive and sum to 1)
2. **Continuous**: Piecewise linear scoring ensures no discontinuities
3. **Interpretable**: Each unit represents equal incremental risk
4. **Decomposable**: Individual variable contributions (w_i × S_i) can be reported for interpretability
