# FRI v2 Decision Log

## Version

2.0.1 — Documentation Completion

## Objective

Maintain a chronological record of every scientific and technical decision related to FRI v2. This document extends the design freeze recorded in `01_SPECIFICATION.md`, `02_ADR.md`, and `07_IMPLEMENTATION_RULES.md` without introducing new methodology.

## Decision Records

| Version | Date | Decision | Reason | Evidence | Impact | Status | Approved By |
|---------|------|----------|--------|----------|--------|--------|-------------|
| 2.0 | 2026-07-05 | Keep existing BMKG dataset at 726 records | Preserve scientific comparability with FRI v1 and avoid uncontrolled dataset drift | `01_SPECIFICATION.md` Dataset Specification; `07_IMPLEMENTATION_RULES.md` Rule 1 | Future v2 work must use the frozen dataset only | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | No dataset expansion | Avoid changing the empirical basis during methodology revision | `01_SPECIFICATION.md`; `04_BOUNDARY.md` | No additional historical data may be added | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Remove `Rain3` from FRI v2 scoring | Simplify the feature set and focus on weekly antecedent rainfall | `01_SPECIFICATION.md` Removed Features | `Rain3` must not contribute to deterministic FRI v2 score | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Remove `Rain14` from FRI v2 scoring | Simplify the feature set and avoid longer-window overlap with `Rain7` | `01_SPECIFICATION.md` Removed Features | `Rain14` must not contribute to deterministic FRI v2 score | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Replace `TempRange` with `Tavg` | Use average temperature as the approved supporting thermal condition signal | `01_SPECIFICATION.md` Retained and Removed Features | `TempRange` is excluded; `Tavg` is retained | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Remove `RainfallAnomaly` from FRI v2 scoring | Keep v2 scoring limited to the four approved hydrometeorological features | `01_SPECIFICATION.md` Removed Features | `RainfallAnomaly` must not contribute to deterministic FRI v2 score | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Feature set equals `RR`, `Rain7`, `RH_avg`, `Tavg` | Establish a closed, interpretable feature set for v2 | `01_SPECIFICATION.md` Feature Set; `07_IMPLEMENTATION_RULES.md` Rule 2 | Future feature engineering, scoring, training, and inference must use this canonical set | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Weights equal 10 / 50 / 30 / 10 | Prioritize seven-day rainfall accumulation while retaining daily rainfall, humidity, and temperature context | `01_SPECIFICATION.md` Weighting Formula; `07_IMPLEMENTATION_RULES.md` Rule 4 | FRI v2 aggregation must use `RR` 10%, `Rain7` 50%, `RH_avg` 30%, `Tavg` 10% | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Keep Random Forest | Preserve the approved machine learning algorithm and avoid algorithmic confounding | `01_SPECIFICATION.md` Algorithm; `07_IMPLEMENTATION_RULES.md` Rule 5 | Future training may retrain Random Forest only; no model-family replacement | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Backend architecture unchanged until backend migration sprint | Protect stable production behavior and API compatibility | `03_MIGRATION_PLAN.md`; `07_IMPLEMENTATION_RULES.md` Rule 7 | Backend changes are forbidden until Sprint v2.4 and must preserve API compatibility | Accepted | FRI v2 Design Freeze |
| 2.0 | 2026-07-05 | Security architecture unchanged | Keep audited security posture outside FRI methodology scope | `04_BOUNDARY.md`; `07_IMPLEMENTATION_RULES.md` Rule 6 | Authentication, authorization, security controls, and security files remain forbidden areas | Accepted | FRI v2 Design Freeze |

## Change Control

Future decisions that alter features, weights, thresholds, classification rules, algorithm, dataset, backend contract, or security posture require a new ADR before implementation.

## Documentation-Only Statement

This decision log records approved decisions only. It does not implement code, retrain models, modify datasets, or change runtime behavior.
