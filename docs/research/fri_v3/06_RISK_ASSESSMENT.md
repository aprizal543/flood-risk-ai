# Risk Assessment — FRI Version 3 Weight Revision

## Objective

Identify, classify, and document risks associated with the FRI v3 equal-weight revision. All risks are assessed as hypotheses until experimentally validated.

---

## Risk Register

| ID | Risk | Category | Likelihood | Impact | Severity | Mitigation |
|----|------|----------|------------|--------|----------|------------|
| R1 | Predictive accuracy degrades | Technical | Medium | High | **High** | Non-inferiority test; rollback to v2 |
| R2 | Target distribution collapses | Technical | Low | High | **Medium** | Pre-training distribution check |
| R3 | Extreme-value predictions weaken | Technical | Medium | Medium | **Medium** | Subgroup analysis on high-FRI records |
| R4 | Increased low-risk false positives | Technical | Medium | Medium | **Medium** | Confusion matrix analysis |
| R5 | Rainfall sensitivity reduced, missing real flood events | Domain | Medium | High | **High** | Hydrological plausibility review |
| R6 | Seasonality patterns become implausible | Domain | Low | Medium | **Low** | Visual seasonal curve inspection |
| R7 | Recommendation quality degrades | Downstream | Medium | Medium | **Medium** | Recommendation variance analysis |
| R8 | Production rollback required | Operational | Medium | Low | **Low** | Production artifact preserved |
| R9 | Implementation exceeds scope (unintended code changes) | Process | Low | Medium | **Low** | Strict sprint boundary enforcement |
| R10 | Equal-weight results indistinguishable from v2 (wasted effort) | Project | Medium | Low | **Low** | Distribution comparison will detect differences |

---

## Detailed Risk Analysis

### R1 — Predictive Accuracy Degrades

**Description**: The v3-trained Random Forest performs worse than v2 on the held-out test set. The target distribution change makes learning harder.

**Assessment**: This is the highest-impact risk. If MAE_v3 > 1.10 × MAE_v2, the null hypothesis of non-inferiority is violated.

**Threshold for action**: MAE_v3 / MAE_v2 > 1.10.

**Contingency**: Abandon v3, document negative finding, retain v2 in production.

### R2 — Target Distribution Collapses

**Description**: Equal weighting produces a narrower or more skewed distribution than v2.

**Assessment**: Low likelihood because combining four diverse signals (RR, Rain7, RH_avg, Tavg) with equal weights naturally increases mixing.

**Detection**: Compare σ and IQR of FRI_v3 vs. FRI_v2.

**Contingency**: If σ_v3 / σ_v2 < 0.90, investigate weight interaction effects before proceeding.

### R3 — Extreme-Value Predictions Weaken

**Description**: The model performs worse on high-risk FRI values (>80), reducing the system's ability to flag dangerous conditions.

**Assessment**: Medium likelihood. If Rain7 is the primary indicator of extreme risk, reducing its weight may flatten the tail.

**Detection**: Subgroup MAE on top 10% of FRI values.

**Contingency**: Consider tiered weighting or hybrid v2/v3 approach for extreme values.

### R4 — Increased Low-Risk False Positives

**Description**: Tavg and RH_avg may inflate FRI values during dry periods, increasing the number of low-risk days classified as medium-risk.

**Assessment**: Medium likelihood. Tavg's influence increases from 10% to 25%, potentially adding noise during non-rainy periods.

**Detection**: Confusion matrix analysis; calculate false positive rate for Low→Medium transitions.

**Contingency**: If false positive rate increases >10%, consider temperature and humidity score capping.

### R5 — Rainfall Sensitivity Reduced

**Description**: By reducing combined rainfall weight (RR+Rain7) from 60% to 50%, the index may under-react to genuine heavy rainfall events. A day with extreme RR but moderate Rain7 may receive a lower FRI than physically justified.

**Assessment**: This is the strongest scientific argument against equal weighting. Rain7 is hydrologically the most important variable.

**Detection**: Manual review of FRI_v3 values on known heavy rainfall days.

**Contingency**: If 2+ known heavy rainfall days receive implausibly low FRI_v3, revert to v2 or propose constrained weights (e.g., RR+Rain7 ≥ 50%).

### R6 — Seasonality Becomes Implausible

**Description**: The seasonal pattern of FRI_v3 may not match the known wet season (October–March) and dry season (April–September) of Pekanbaru.

**Assessment**: Low likelihood. All four variables have some seasonal signal.

**Detection**: Monthly mean FRI plot against climatological expectation.

**Contingency**: Adjust weights or add seasonal calibration if patterns are inverted.

### R7 — Recommendation Quality Degrades

**Description**: Commodity recommendations derived from FRI_v3 may be less appropriate than those from FRI_v2, especially during high-risk periods.

**Assessment**: Medium likelihood. If FRI_v3 changes significantly, recommendations will change accordingly.

**Detection**: Compare recommended commodity lists for the same input conditions.

**Contingency**: If recommendations become clearly inappropriate, retain v2 for the recommendation engine while v3 predictions are further evaluated.

### R8 — Production Rollback Required

**Description**: After v3 deployment, issues are discovered that require rolling back to v2.

**Assessment**: Medium likelihood for any production change.

**Mitigation**: Production artifact (`random_forest_v2.pkl`) is preserved; rollback is a configuration change only.

### R9 — Implementation Exceeds Scope

**Description**: During the implementation sprint, unintended changes to scoring, features, or backend occur beyond the weight change.

**Assessment**: Low likelihood if sprint boundaries are clearly documented.

**Mitigation**: Implementation sprint must include a boundary enforcement checklist.

### R10 — Indistinguishable Results

**Description**: FRI_v3 and FRI_v2 distributions are so similar that the weight change has negligible practical effect.

**Assessment**: Low likelihood. A 25% change in three out of four weights should produce measurable differences.

**Detection**: Kolmogorov-Smirnov test between v2 and v3 distributions.

**Contingency**: If p > 0.05 (distributions not significantly different), document that equal weighting is effectively equivalent to v2 weighting for this dataset.

---

## Risk Matrix

```
Impact
  High    │ R1, R5
  Medium  │ R3, R4, R7
  Low     │ R2, R6, R8, R9, R10
          └────────────────────────
          Low    Medium    High
                  Likelihood
```

---

## Risk Acceptance

| Risk ID | Decision | Rationale |
|---------|----------|-----------|
| R1 | **Must test** | Non-inferiority is a hard gate |
| R2 | **Monitor** | Pre-training check is required |
| R3 | **Monitor** | Subgroup analysis is part of experiment plan |
| R4 | **Accept** | Acceptable if within threshold |
| R5 | **Must test** | Manual plausibility review required |
| R6 | **Accept** | Low likelihood; cosmetic concern |
| R7 | **Monitor** | Will be measured; actionable if negative |
| R8 | **Accept** | Rollback procedure is documented |
| R9 | **Accept** | Sprint boundary enforcement is routine |
| R10 | **Accept** | Even null result is informative |

---

## Go/No-Go Criteria for Production Deployment

**Go** (all must pass):
- Non-inferiority test: MAE_v3 ≤ 1.10 × MAE_v2
- Distribution check: σ_v3 ≥ 0.90 × σ_v2
- Hydrological plausibility: No known extreme-rainfall day receives implausibly low FRI_v3

**No-Go** (any single failure):
- MAE_v3 > 1.10 × MAE_v2
- FRI_v3 range < 50 (on 0–100 scale)
- Two or more known heavy rainfall days produce FRI_v3 < 30
