# FRI Weight Revision Specification — Version 3

## Version

3.0 — Design Freeze (Sprint 4.0)

## Status

Design Freeze — Documentation Only. No implementation authorized.

---

## Objective

Define a revised weighting scheme for the Flood Risk Index (FRI) Version 3. The revision changes only the weight allocation across the four existing features. No features are added or removed. No scoring functions change. Only the aggregation weights are updated.

---

## Current Production System (FRI v2)

| Property | Value |
|----------|-------|
| Model | RandomForest_v2.pkl |
| Features | RR, Rain7, RH_avg, Tavg |
| Weights | RR: 10%, Rain7: 50%, RH_avg: 30%, Tavg: 10% |
| Feature Order | ["RR", "Rain7", "RH_avg", "Tavg"] |
| Prediction Type | Regression (continuous FRI ∈ [0, 100]) |
| Risk Classification | Low [0–33], Medium [34–66], High [67–100] |

---

## Proposed Weight Configuration (FRI v3)

| Feature | Weight | Change from v2 |
|---------|--------|----------------|
| RR | 25% | +15% |
| Rain7 | 25% | -25% |
| RH_avg | 25% | -5% |
| Tavg | 25% | +15% |
| **Total** | **100%** | — |

### Weight Constraints

| Constraint | FRI v2 | FRI v3 | Status |
|------------|--------|--------|--------|
| Σ w_i = 1.0 | 1.0 | 1.0 | Preserved |
| w_i > 0 ∀ i | All > 0 | All > 0 | Preserved |
| No single w_i > 0.35 | Rain7 = 0.50 ❌ | All = 0.25 ✅ | **Violation fixed** |
| Rainfall dominance (RR+Rain7) ≥ 0.60 | 0.60 ✅ | 0.50 ❌ | **Constraint relaxed** |
| Secondary cap (RH_avg+Tavg) ≤ 0.25 | 0.40 ❌ | 0.50 ❌ | **Constraint relaxed** |

Note: The rainfall dominance constraint (≥60%) and the secondary cap (≤25%) from the original FRI v1 specification (`docs/research/08_WEIGHT_SELECTION.md`) are deliberately relaxed in this proposal. The equal-weight hypothesis asserts that these constraints, while physically motivated, may not be optimal for machine learning target construction. Whether relaxation improves or degrades the target is an empirical question to be resolved by the experiment plan.

---

## What Changes

| Component | FRI v2 | FRI v3 |
|-----------|--------|--------|
| Feature set | RR, Rain7, RH_avg, Tavg | Unchanged |
| Scoring functions | Per v2 specification | Unchanged |
| Weights | 10/50/30/10 | 25/25/25/25 |
| Aggregation formula | Σ (w_i × S_i) | Unchanged |
| Risk classification thresholds | 33/66 | Unchanged |
| ML algorithm | Random Forest | Unchanged |
| Model artifact | RandomForest_v2.pkl | RandomForest_v3.pkl (new) |

---

## What Does Not Change

- Raw BMKG dataset (remains at 726 records)
- Feature engineering pipeline
- Feature order (remains ["RR", "Rain7", "RH_avg", "Tavg"])
- Scoring functions and threshold methodology
- Risk classification boundaries
- Random Forest algorithm
- Backend API contract
- Frontend display semantics

---

## Motivation Summary

1. **Rain7 dominance**: Rain7 at 50% alone controls half the index. Combined rainfall (RR + Rain7 = 60%) may over-emphasize precipitation signals at the expense of humidity and temperature contributions.

2. **Single-variable dominance**: Rain7 at 50% violates the original design principle that no single w_i should exceed 0.35 (see `docs/research/08_WEIGHT_SELECTION.md`).

3. **Target distribution compression**: If rainfall dominance produces a narrow target distribution, Random Forest may exhibit regression-to-the-mean behaviour, concentrating predictions around medium-risk values.

4. **Information redundancy**: RR and Rain7 are not independent; Rain7 is a cumulative function of RR. Combined weight of 60% may double-count the same precipitation signal.

5. **Equal-weight precedent**: Equal weighting is a well-established method in composite index construction and provides a natural baseline for comparison.

---

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Weight definition only | Source code modifications |
| Scientific justification | Model retraining |
| Hypothesis documentation | Dataset changes |
| Experiment plan | Scoring function changes |
| Model versioning plan | Feature engineering changes |
| Risk assessment | Backend/frontend changes |
| Implementation roadmap | Deployment changes |
| | Azure/Vercel configuration |

---

## Frozen Specification

The following is frozen as of Sprint 4.0 Design Freeze:

```
FRI_v3 = 0.25 × Score(RR)
       + 0.25 × Score(Rain7)
       + 0.25 × Score(RH_avg)
       + 0.25 × Score(Tavg)
```

Any future change to this formula requires a new design freeze sprint and a new version number.

---

## References

- `docs/research/fri_v2/01_SPECIFICATION.md` — FRI v2 Design Freeze
- `docs/research/fri_v2/02_ADR.md` — FRI v2 ADR
- `docs/research/fri_v2/09_DECISION_LOG.md` — FRI v2 Decision Log
- `docs/research/08_WEIGHT_SELECTION.md` — Original weight methodology (v1 era)
- `docs/research/04_FRI_FORMULA.md` — FRI mathematical formulation
- `docs/research/10_TARGET_VARIABLE_SPECIFICATION.md` — Target variable definition
