# Target Variable Specification

## Objective

This document formally defines the Flood Risk Index (FRI) as the regression target variable for the flood risk prediction system. It specifies the mathematical construction of the target, distinguishes it from downstream classification outputs, and establishes quality indicators for each computed value.

---

## Target Variable Definition

### Primary Target: Flood Risk Index (FRI)

| Property | Specification |
|----------|--------------|
| Name | `fri` |
| Type | Continuous (regression target) |
| Range | [0, 100] |
| Unit | Dimensionless index |
| Resolution | Daily (one value per calendar date) |
| Construction | Deterministic computation from scored meteorological features |

The FRI is **not** an observed variable. It is a derived quantity computed through a defined scientific scoring and aggregation pipeline. It serves simultaneously as:
1. The output of the deterministic index system
2. The regression target for machine learning models that predict FRI from raw features

---

## Regression Target vs. Dashboard Classification

A critical architectural distinction separates the continuous FRI (analytical core) from the categorical risk level (user-facing output):

```
┌─────────────────────────────────────────────────────┐
│  ANALYTICAL LAYER (Regression Target)                │
│                                                       │
│  FRI ∈ [0, 100]  ← continuous, computed              │
│  • Used for model training and evaluation            │
│  • Preserves full information granularity            │
│  • Enables threshold sensitivity analysis            │
└───────────────────────┬─────────────────────────────┘
                        │ Classification boundary
                        ▼
┌─────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (Dashboard Classification)       │
│                                                       │
│  Risk Level ∈ {Low, Medium, High}  ← categorical    │
│  • User-facing simplification                        │
│  • Drives commodity and mitigation recommendations   │
│  • Boundaries: 0–33 (Low), 34–66 (Medium), 67–100  │
└─────────────────────────────────────────────────────┘
```

### Why This Separation Matters

1. **Information preservation**: Training ML models on the continuous FRI retains the full ordinal and magnitude information that would be lost in a 3-class discretisation.
2. **Threshold flexibility**: Classification boundaries (33/66) can be adjusted post-hoc without retraining models.
3. **Evaluation precision**: Regression metrics (MAE, RMSE, R²) provide finer-grained model assessment than classification accuracy.
4. **Research utility**: The continuous target supports analysis of risk gradients, trend detection, and percentile-based reporting.

---

## Risk Scoring Layer

### Architecture

The scoring layer transforms each raw or engineered feature into a standardised risk score S_i ∈ [0, 100]:

```
Raw/Engineered Feature Value
        ↓
    Scoring Function f_i(x)
        ↓
    Risk Score S_i ∈ [0, 100]
```

### Scoring Functions

| Variable | Scoring Method | Direction | Reference |
|----------|---------------|-----------|-----------|
| RR | BMKG piecewise linear | Positive (higher rainfall → higher score) | 07_THRESHOLD_JUSTIFICATION.md §1 |
| Rain3 | Percentile mapping | Positive | 07_THRESHOLD_JUSTIFICATION.md §2 |
| Rain7 | Percentile mapping | Positive | 07_THRESHOLD_JUSTIFICATION.md §2 |
| Rain14 | Percentile mapping | Positive | 07_THRESHOLD_JUSTIFICATION.md §2 |
| RH_avg | Percentile mapping | Positive | 07_THRESHOLD_JUSTIFICATION.md §3 |
| TempRange | Percentile mapping (inverse) | Negative (lower range → higher score) | 07_THRESHOLD_JUSTIFICATION.md §4 |

### Score Properties

- **Bounded**: S_i ∈ [0, 100] by construction
- **Monotonic**: Each scoring function is monotonically related to risk (positive or negative direction as specified)
- **Continuous**: Piecewise linear functions with no discontinuities
- **Deterministic**: The same input always produces the same score (no stochastic component)

---

## Weighted Aggregation Layer

### Formula

```
FRI_raw = Σ (w_i × S_i)    for i ∈ {RR, Rain3, Rain7, Rain14, RH_avg, TempRange}
```

### Normalisation to 0–100 Scale

Given the constraints (Σ w_i = 1.0, S_i ∈ [0, 100], w_i > 0), the weighted sum is inherently bounded:

```
FRI_min = Σ (w_i × 0) = 0
FRI_max = Σ (w_i × 100) = 100
```

Therefore **no additional normalisation is required**. The FRI is naturally on the 0–100 scale by construction. This property holds regardless of the specific weight values chosen, provided the constraints are satisfied.

### Weight Values

| Variable | Weight | Status |
|----------|--------|--------|
| RR | w₁ = TBD | Pending literature review + EDA |
| Rain3 | w₂ = TBD | Pending literature review + EDA |
| Rain7 | w₃ = TBD | Pending literature review + EDA |
| Rain14 | w₄ = TBD | Pending literature review + EDA |
| RH_avg | w₅ = TBD | Pending literature review + EDA |
| TempRange | w₆ = TBD | Pending literature review + EDA |

### Weight Constraints

| Constraint | Expression | Rationale |
|-----------|-----------|-----------|
| Unity sum | Σ w_i = 1.0 | Preserves 0–100 scale without post-hoc normalisation |
| Positivity | w_i > 0 ∀ i | All variables contribute to risk |
| Rainfall dominance | w₁ + w₂ + w₃ + w₄ ≥ 0.60 | Precipitation is the primary tropical flood driver |
| No single dominance | max(w_i) ≤ 0.35 | Index remains multi-factorial |
| Secondary cap | w₅ + w₆ ≤ 0.25 | Indirect indicators bounded |

Weight determination methodology is documented in 08_WEIGHT_SELECTION.md.

---

## Confidence Score

### Definition

Each FRI value is accompanied by a confidence score indicating the completeness of the underlying feature set:

```
confidence = Σ w_i (for all i where S_i is not NaN) / Σ w_i (all)
```

Since Σ w_i (all) = 1.0:

```
confidence = Σ w_i (available)
```

### Interpretation

| Confidence | Interpretation | Action |
|-----------|----------------|--------|
| 1.0 | All features available; full-confidence FRI | Use directly |
| 0.75 – 0.99 | Minor data gap; FRI reliable | Use with note |
| 0.50 – 0.74 | Significant gap; FRI approximate | Flag as uncertain |
| < 0.50 | Majority of features missing; FRI unreliable | Exclude from analysis |

### Purpose

The confidence score serves as a data quality indicator that:
1. Quantifies information loss due to missing observations
2. Enables downstream systems to weight or filter FRI values by reliability
3. Provides transparency about the evidential basis of each daily risk assessment
4. Supports quality-aware aggregation in reporting (e.g., confidence-weighted monthly averages)

---

## Handling of Missing Values

### Principles

1. **No imputation of raw observations**: Missing BMKG values (converted from sentinels 8888/9999 or originally absent) are not filled, interpolated, or estimated.
2. **Score propagation**: If a raw feature is NaN, its score S_i is NaN.
3. **Partial aggregation**: FRI is computed from available scores with weight renormalisation.
4. **Quality flagging**: The confidence score records the degree of incompleteness.

### Computation with Missing Scores

When k out of 6 scores are available:

```
FRI = Σ (w_i × S_i) / Σ w_i    for i ∈ available_scores
confidence = Σ w_i (available) / 1.0
```

This renormalisation ensures:
- FRI remains on the 0–100 scale regardless of missingness
- The relative contribution of available variables is preserved
- No artificial inflation or deflation of the index occurs

### Edge Cases

| Scenario | Handling |
|----------|----------|
| All scores available | FRI computed normally; confidence = 1.0 |
| One score missing | FRI computed from remaining 5; confidence < 1.0 |
| Only RR available | FRI = S_RR (single variable); confidence = w_RR; flagged as unreliable |
| No scores available | FRI = NaN; confidence = 0; excluded from analysis |

---

## Target Variable Summary

```
┌──────────────────────────────────────────────────┐
│  For each calendar date t:                        │
│                                                    │
│  Outputs:                                          │
│    fri(t)         ∈ [0, 100]  or NaN              │
│    confidence(t)  ∈ [0, 1.0]                      │
│    risk_level(t)  ∈ {Low, Medium, High} or NaN    │
│                                                    │
│  Decomposition (interpretability):                 │
│    score_rr(t)         ∈ [0, 100]                 │
│    score_rain3(t)      ∈ [0, 100]                 │
│    score_rain7(t)      ∈ [0, 100]                 │
│    score_rain14(t)     ∈ [0, 100]                 │
│    score_rh_avg(t)     ∈ [0, 100]                 │
│    score_temprange(t)  ∈ [0, 100]                 │
└──────────────────────────────────────────────────┘
```

---

## Relationship to Thesis

| Section | Thesis Chapter | Purpose |
|---------|---------------|---------|
| Target variable definition | Chapter III §3.x (Variable Operasional) | Defines the dependent variable |
| Scoring layer | Chapter III §3.x (Metode Pengolahan Data) | Data transformation methodology |
| Aggregation and weights | Chapter III §3.x (Metode Analisis) | Analytical method specification |
| Confidence score | Chapter III §3.x (Validasi Data) | Quality assurance mechanism |
| Classification mapping | Chapter IV §4.x (Implementasi Sistem) | System output design |
