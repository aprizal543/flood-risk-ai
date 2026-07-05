# FRI v2 Acceptance Criteria

## Documentation Sprint Acceptance Criteria

This sprint is accepted only if:

- `docs/research/fri_v2/` exists.
- All required design-freeze documents exist.
- All required sprint documents exist.
- The sprint produces documentation only.
- No source code is modified.
- No model is retrained.
- No backend implementation is changed.
- No frontend implementation is changed.
- No dataset is changed.

## Required Design-Freeze Documents

- `00_OVERVIEW.md`
- `01_SPECIFICATION.md`
- `02_ADR.md`
- `03_MIGRATION_PLAN.md`
- `04_BOUNDARY.md`
- `05_ACCEPTANCE_CRITERIA.md`
- `06_ROLLBACK_PLAN.md`
- `07_IMPLEMENTATION_RULES.md`
- `08_PROJECT_STATE.md`

## Required Sprint Documents

- `sprint-v2.1-feature-engineering.md`
- `sprint-v2.2-scoring-engine.md`
- `sprint-v2.3-training.md`
- `sprint-v2.4-backend-migration.md`
- `sprint-v2.5-integration-testing.md`
- `sprint-v2.6-scientific-evaluation.md`
- `sprint-v2.7-production-deployment.md`

## Future FRI v2 Implementation Acceptance Criteria

Future implementation is accepted only if:

- The feature set is exactly `RR`, `Rain7`, `RH_avg`, `Tavg`.
- Weights are exactly 10%, 50%, 30%, and 10% respectively.
- Removed features do not contribute to FRI v2 scoring.
- Random Forest remains the algorithm.
- Existing dataset remains unchanged at 726 records.
- Cleaning and merge pipelines remain unchanged.
- Evaluation compares FRI v2 against FRI v1.
- Rollback to FRI v1 is documented and tested.

## Failure Criteria

The sprint fails if any forbidden file category is modified or if implementation work occurs during this documentation-only sprint.
