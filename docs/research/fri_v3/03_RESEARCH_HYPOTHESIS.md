# Research Hypotheses — FRI Version 3

## Objective

Formally document all research hypotheses motivating the FRI v3 equal-weight revision. These hypotheses are clearly labelled as unverified claims that must be tested experimentally during the implementation phase.

---

## Hypothesis Classification

| Label | Category | Description |
|-------|----------|-------------|
| H₁ | Target Distribution | Effects of equal weighting on FRI distribution shape |
| H₂ | ML Performance | Effects on Random Forest prediction quality |
| H₃ | Prediction Diversity | Effects on spread and discrimination of predictions |
| H₄ | Risk Classification | Effects on risk class proportions |
| H₅ | Recommendation | Effects on downstream commodity recommendations |
| H₆ | Negative Case | Potential adverse effects |

---

## H₁: Target Distribution Hypothesis

### H₁ₐ — Distribution Spread

> **Statement**: Equal weighting (25/25/25/25) will produce an FRI target distribution with wider spread and reduced concentration around medium values compared to FRI v2 (10/50/30/10).

**Rationale**: FRI v2's Rain7 dominance (50%) causes the target to track a single variable closely, reducing multi-dimensional signal mixing. Equal weighting combines four independent sources of variation, increasing distributional variance.

**Test**: Compare FRI v2 vs. FRI v3 histograms, standard deviation, and interquartile range.

**Prediction**: σ(FRI_v3) > σ(FRI_v2) and IQR(FRI_v3) > IQR(FRI_v2).

---

### H₁_b — Skewness Change

> **Statement**: Equal weighting will alter the skewness of the FRI distribution.

**Rationale**: Changing the relative contribution of rainfall, humidity, and temperature shifts the long-tail behaviour. The direction of change depends on the empirical distributions of the individual scores.

**Test**: Compare skewness (third central moment) of FRI v2 vs. FRI v3 distributions.

**Prediction**: Direction unspecified. Open empirical question.

---

## H₂: ML Performance Hypothesis

### H₂ₐ — Overall Performance (No Degradation)

> **Statement**: Random Forest trained on FRI v3 target will achieve comparable or better MAE, RMSE, and R² compared to the FRI v2-trained model, evaluated on held-out test data.

**Rationale**: If FRI v3 produces a more balanced target distribution, the model may learn more generalisable patterns. However, the null hypothesis is that performance is equivalent.

**Test**: Train RandomForest_v3 on Dataset_v3. Evaluate on held-out test set. Compare metrics against RandomForest_v2 on the same test split.

**Criterion**: MAE_v3 ≤ 1.10 × MAE_v2 and R²_v3 ≥ R²_v2 − 0.05 (non-inferiority margin).

**Prediction**: Comparable performance (H₀ of no degradation expected to hold).

---

### H₂_b — Extreme Value Performance

> **Statement**: Random Forest trained on FRI v3 will show improved prediction accuracy for extreme (high-risk) FRI values.

**Rationale**: If FRI v3 produces a wider target distribution with more samples at the extremes, the model will have better support for learning extreme-value patterns.

**Test**: Compare MAE and RMSE on the top 10% of FRI values in the test set.

**Prediction**: MAE_v3(extreme) < MAE_v2(extreme).

---

## H₃: Prediction Diversity Hypothesis

### H₃ₐ — Reduced Regression to the Mean

> **Statement**: Random Forest trained on FRI v3 will exhibit reduced regression-to-the-mean behaviour, measured by a higher standard deviation of predictions.

**Rationale**: Random Forest averages across trees; if the target distribution is wider, the ensemble predictions can spread over a larger range without being pulled toward a narrow central region.

**Test**: Compare σ(predictions) between v2 and v3 models on the same test set.

**Prediction**: σ(pred_v3) > σ(pred_v2).

---

### H₃_b — Prediction Distribution Range

> **Statement**: The min-to-max range of predicted FRI values will be larger for the v3 model than the v2 model.

**Test**: Compare max(pred_v3) − min(pred_v3) vs. max(pred_v2) − min(pred_v2).

**Prediction**: Range_v3 > Range_v2.

---

## H₄: Risk Classification Hypothesis

### H₄ₐ — Class Proportion Shift

> **Statement**: Equal weighting will change the proportion of Low, Medium, and High risk classifications.

**Rationale**: Shifting weight from Rain7 (50% → 25%) to RR (10% → 25%) and Tavg (10% → 25%) will redistribute the index values across the 0–100 scale.

**Test**: Compare class proportions between FRI v2 and FRI v3.

**Prediction**: Direction unspecified. Open empirical question.

---

### H₄_b — Extreme Class Recovery

> **Statement**: FRI v3 will produce a higher proportion of Low (<20) and High (>80) bin values than FRI v2.

**Rationale**: Reduced rainfall dominance may allow non-rainfall variables (RH_avg, Tavg) to push the index into extreme regions when these variables are at their extremes even if rainfall is moderate.

**Test**: Compare counts in 0–20 and 80–100 bins.

**Prediction**: Count_v3(0–20) > Count_v2(0–20) and Count_v3(80–100) > Count_v2(80–100).

---

## H₅: Recommendation Hypothesis

### H₅ₐ — Recommendation Diversity

> **Statement**: Commodity recommendations derived from FRI v3 will show greater diversity across weather conditions than recommendations derived from FRI v2.

**Rationale**: If FRI v3 produces a wider risk distribution, the recommendation engine will be triggered across a broader range of risk levels, resulting in more differentiated outputs.

**Test**: Compare variance of recommended commodity IDs across test set.

**Prediction**: Var(rec_v3) > Var(rec_v2).

---

## H₆: Negative Case Hypotheses

### H₆ₐ — Accuracy Degradation Risk

> **Statement**: Equal weighting may reduce predictive accuracy relative to v2 if the Rain7 dominance in v2 was capturing genuine hydrological signal rather than over-weighting a single variable.

**Rationale**: If Rain7 is legitimately the most important flood risk driver, reducing its weight from 50% to 25% could reduce the target's physical validity, making it harder for the model to learn.

**Test**: H₂ₐ non-inferiority criterion. If MAE_v3 > 1.10 × MAE_v2, the hypothesis is supported.

### H₆_b — Increased Low-Risk False Positives

> **Statement**: Equal weighting may increase the number of Low-to-Medium classification errors by inflating the influence of Tavg and RH_avg during dry periods.

**Test**: Confusion matrix analysis of FRI v3 vs. v2 classifications.

---

## Summary Table

| Hypothesis | Domain | Direction | Test Metric | Risk |
|-----------|--------|-----------|-------------|------|
| H₁ₐ | Distribution | Wider spread | σ, IQR | Low |
| H₁_b | Distribution | Unknown | Skewness | Low |
| H₂ₐ | ML Performance | Non-inferior | MAE, RMSE, R² | High (blocker if violated) |
| H₂_b | ML Performance | Improved extreme | MAE(top 10%) | Medium |
| H₃ₐ | Prediction Diversity | Higher σ | σ(pred) | Medium |
| H₃_b | Prediction Diversity | Larger range | Range | Medium |
| H₄ₐ | Classification | Shift | Class proportions | Low |
| H₄_b | Classification | More extremes | Bin counts | Low |
| H₅ₐ | Recommendation | More diverse | Recommendation variance | Low |
| H₆ₐ | Negative | Degradation | MAE ratio | High (acceptance criterion) |
| H₆_b | Negative | False positives | Confusion matrix | Medium |

---

## Hypothesis Validation Status

All hypotheses listed in this document are **unvalidated** as of Sprint 4.0 Design Freeze.

Validation will occur during the Experiment Phase (see `04_EXPERIMENT_PLAN.md`). Hypotheses that survive experimental testing will be promoted to findings. Hypotheses that are refuted will be documented as negative results.
