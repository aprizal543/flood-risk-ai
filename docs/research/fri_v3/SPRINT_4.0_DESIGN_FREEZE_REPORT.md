# Sprint 4.0 — FRI Weight Revision Design Freeze Report

## Version

4.0 — Design Freeze

## Date

2026-07-07

---

## Executive Summary

This sprint freezes the scientific design for Flood Risk Index (FRI) Version 3. The revision changes only the weighting of the four existing features from the v2 configuration (RR=10%, Rain7=50%, RH_avg=30%, Tavg=10%) to equal weights (25% each). No features are added or removed. No scoring functions are modified. No source code changes are authorized.

The design freeze produces seven specification documents and this final report. Implementation is deferred to a future sprint.

---

## Motivation

The current FRI v2 weighting heavily emphasises Rain7 (50%). Combined rainfall contribution (RR + Rain7) is 60%, which may cause:

- **Rainfall dominance**: The index tracks a single variable (Rain7) more than any other
- **Reduced influence of RH_avg and Tavg**: Secondary variables contribute only 40% collectively
- **Narrower target distribution**: Limited multi-dimensional mixing
- **Random Forest regression-to-the-mean**: Predictions concentrate around medium-risk values when the target distribution is compressed

The equal-weight hypothesis proposes that a more balanced allocation may produce a better ML target while preserving overall index quality.

---

## Old vs. New Weights

| Feature | FRI v2 | FRI v3 | Delta |
|---------|--------|--------|-------|
| RR | 10% | 25% | +15% |
| Rain7 | 50% | 25% | −25% |
| RH_avg | 30% | 25% | −5% |
| Tavg | 10% | 25% | +15% |
| **Total** | **100%** | **100%** | — |

### Constraint Changes

| Constraint | v2 Status | v3 Status |
|------------|-----------|-----------|
| Σ w_i = 1.0 | ✅ | ✅ |
| w_i > 0 ∀ i | ✅ | ✅ |
| No single w_i > 0.35 | ❌ (Rain7=0.50) | ✅ |
| Rainfall dominance ≥ 60% | ✅ (60%) | ❌ (50%) |
| Secondary cap ≤ 25% | ❌ (40%) | ❌ (50%) |

Two original constraints (rainfall dominance ≥60%, secondary cap ≤25%) are deliberately relaxed for v3 as part of the experimental hypothesis.

---

## Scientific Basis

A literature review (`02_LITERATURE_REVIEW_EQUAL_WEIGHTING.md`) establishes:

1. **Composite index methodology**: Equal weighting is a standard, widely used method in composite index construction (OECD, 2008; Decancq & Lugo, 2013)
2. **Information redundancy**: RR and Rain7 are correlated; their combined 60% weight may double-count precipitation signal
3. **Multi-dimensional flood risk**: Flooding involves multiple processes (infiltration exceedance, saturation excess, evapotranspiration, atmospheric capacity), none of which is categorically dominant
4. **Agricultural pathways**: RR, Rain7, RH_avg, and Tavg affect crops through distinct mechanisms; balanced representation may improve recommendation robustness
5. **Random Forest behaviour**: Ensemble averaging tends toward regression-to-the-mean; a wider target distribution may improve prediction diversity

All claims of improvement are labelled as **research hypotheses**, not established findings.

---

## Research Hypotheses

| ID | Hypothesis | Domain | Criterion |
|----|-----------|--------|-----------|
| H₁ₐ | FRI_v3 has wider spread than FRI_v2 | Distribution | σ(v3) > σ(v2) |
| H₁_b | FRI_v3 skewness differs from v2 | Distribution | Measured (no prediction) |
| H₂ₐ | FRI_v3 ML performance is non-inferior to v2 | ML | MAE ≤ 1.10×, R² ≥ −0.05 |
| H₂_b | FRI_v3 improves extreme-value predictions | ML | MAE(top 10%) improved |
| H₃ₐ | FRI_v3 reduces regression-to-the-mean | ML | σ(pred_v3) > σ(pred_v2) |
| H₃_b | FRI_v3 prediction range is larger | ML | Range_v3 > Range_v2 |
| H₄ₐ | FRI_v3 class proportions shift | Classification | Measured (no prediction) |
| H₄_b | FRI_v3 increases extreme bin counts | Classification | Count(0–20, 80–100) increased |
| H₅ₐ | FRI_v3 recommendations are more diverse | Downstream | Recommendation variance |
| H₆ₐ | **Negative**: FRI_v3 accuracy may degrade | ML | MAE ratio test |
| H₆_b | **Negative**: FRI_v3 may increase false positives | ML | Confusion matrix analysis |

---

## Implementation Plan

### Phased Approach

| Phase | Description | Output |
|-------|-------------|--------|
| 1 | Generate FRI_v3 target values | FRI_v3 column |
| 2 | Construct Dataset_v3 | `bmkg_fri_v3.csv` |
| 3 | Exploratory Data Analysis | EDA report |
| 4 | Distribution Analysis (v2 vs. v3) | Distribution report |
| 5 | Train RandomForest_v3 | `random_forest_v3.pkl` |
| 6 | Evaluate v2 vs. v3 | Experiment report |
| 7 | Model versioning & artifacts | Metadata, checksums |
| 8 | Production deployment | Live v3 model |

### Go/No-Go Criteria

**Go** (all must pass):
- MAE_v3 ≤ 1.10 × MAE_v2
- R²_v3 ≥ R²_v2 − 0.05
- σ(pred_v3) > σ(pred_v2)
- FRI_v3 range ≥ 0.80 × FRI_v2 range
- No implausible FRI_v3 values on known heavy-rainfall days

**No-Go** (any single failure triggers revision or rejection).

### Versioning

- New model: `random_forest_v3.pkl` (production artifact `random_forest_v2.pkl` preserved)
- New dataset: `bmkg_fri_v3.csv`
- Feature order unchanged: ["RR", "Rain7", "RH_avg", "Tavg"]
- Model metadata standardised with training date, weight config, checksum

---

## Risk Assessment

| Severity | Risks |
|----------|-------|
| **High** | Accuracy degradation (R1), Reduced rainfall sensitivity (R5) |
| **Medium** | Extreme-value prediction weakness (R3), False positives (R4), Recommendation quality (R7) |
| **Low** | Distribution collapse (R2), Seasonality issues (R6), Rollback required (R8), Scope overrun (R9), Null result (R10) |

All high-severity risks have defined detection criteria and mitigation plans. Rollback to v2 is a configuration change only (v2 artifact preserved).

---

## Files Created

| # | File | Description |
|---|------|-------------|
| 1 | `01_FRI_WEIGHT_REVISION_SPECIFICATION.md` | Weight change specification with frozen formula |
| 2 | `02_LITERATURE_REVIEW_EQUAL_WEIGHTING.md` | Literature-based justification distinguishing evidence from hypothesis |
| 3 | `03_RESEARCH_HYPOTHESIS.md` | 11 formally documented hypotheses (H₁–H₆) |
| 4 | `04_EXPERIMENT_PLAN.md` | Controlled experiment protocol with 4 phases (A–D) and acceptance criteria |
| 5 | `05_MODEL_VERSIONING_PLAN.md` | Artifact naming, metadata schema, rollback procedure, deployment phasing |
| 6 | `06_RISK_ASSESSMENT.md` | 10-risk register, risk matrix, go/no-go criteria |
| 7 | `07_IMPLEMENTATION_ROADMAP.md` | 8-phase implementation sequence with dependencies and timeline |
| 8 | `SPRINT_4.0_DESIGN_FREEZE_REPORT.md` | **This document** — final summary and readiness assessment |

---

## Implementation Readiness

| Criterion | Status | Notes |
|-----------|--------|-------|
| Weight configuration frozen | ✅ | 25/25/25/25 |
| Scientific justification documented | ✅ | 10 topics in literature review |
| Research hypotheses formalised | ✅ | 11 hypotheses across 6 categories |
| Experiment protocol defined | ✅ | 4 measurement phases with 18 sub-analyses |
| Model versioning planned | ✅ | Sequential naming, metadata schema, rollback |
| Risks assessed | ✅ | 10 risks with mitigation plans |
| Implementation phases defined | ✅ | 8 phases with acceptance criteria |
| Go/no-go criteria established | ✅ | 5 quantitative criteria |
| No source code modified | ✅ | Documentation-only sprint |
| No artifacts modified | ✅ | Read-only sprint |
| No datasets modified | ✅ | Read-only sprint |

---

## Design Freeze Status

### ✅ Design Freeze Approved

The FRI Weight Revision (Version 3) design is frozen at this specification.

**Frozen Formula**:
```
FRI_v3 = 0.25 × Score(RR) + 0.25 × Score(Rain7) + 0.25 × Score(RH_avg) + 0.25 × Score(Tavg)
```

**Next Action**: Implementation Sprint (Phase 1 — FRI v3 Target Generation) may proceed when authorised.

---

## Approval

| Role | Date | Status |
|------|------|--------|
| Design Freeze | 2026-07-07 | ✅ Approved |

---

## References

- `docs/research/fri_v2/01_SPECIFICATION.md` — FRI v2 design freeze
- `docs/research/fri_v2/02_ADR.md` — Architecture Decision Record for v2
- `docs/research/fri_v2/09_DECISION_LOG.md` — v2 decision log
- `docs/research/fri_v3/01_FRI_WEIGHT_REVISION_SPECIFICATION.md` — This revision
- `docs/research/fri_v3/02_LITERATURE_REVIEW_EQUAL_WEIGHTING.md` — Literature review
- `docs/research/fri_v3/03_RESEARCH_HYPOTHESIS.md` — Research hypotheses
- `docs/research/fri_v3/04_EXPERIMENT_PLAN.md` — Experiment protocol
- `docs/research/fri_v3/05_MODEL_VERSIONING_PLAN.md` — Versioning strategy
- `docs/research/fri_v3/06_RISK_ASSESSMENT.md` — Risk assessment
- `docs/research/fri_v3/07_IMPLEMENTATION_ROADMAP.md` — Implementation roadmap
