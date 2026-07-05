# FRI v2 Migration Plan

## Objective

Define the future migration sequence from FRI v1 to FRI v2 without implementing any changes during this documentation sprint.

## Migration Principle

FRI v2 must be introduced through isolated, reviewable sprints. Each sprint must pass validation before the next sprint begins.

## Sequence

| Phase | Sprint | Purpose |
|-------|--------|---------|
| 1 | v2.1 Feature Engineering | Prepare retained feature derivation and removed-feature exclusion rules |
| 2 | v2.2 Scoring Engine | Implement four-feature FRI v2 scoring and weights |
| 3 | v2.3 Training | Retrain Random Forest with approved v2 feature set |
| 4 | v2.4 Backend Migration | Wire backend to v2 scoring/model artifacts |
| 5 | v2.5 Integration Testing | Validate API, model, scoring, and regression behavior |
| 6 | v2.6 Scientific Evaluation | Compare v1 and v2 with documented metrics and interpretation |
| 7 | v2.7 Production Deployment | Release v2 after acceptance gates pass |

## Gate Requirements

Each future sprint must confirm:

- Dataset remains unchanged.
- Cleaning scripts remain unchanged.
- Merge scripts remain unchanged.
- Frontend remains unchanged unless explicitly authorized in a later non-FRI sprint.
- Authentication and security remain unchanged.
- Supabase and infrastructure remain unchanged.
- Rollback path remains available.

## Migration Risks

| Risk | Mitigation |
|------|------------|
| Feature order mismatch | Document and test canonical feature order |
| Accidental dataset mutation | Use read-only validation and checksum comparison |
| Scientific regression | Require v1 vs v2 evaluation report |
| Backend/frontend contract drift | Preserve existing API schema unless separately approved |
| Deployment uncertainty | Keep v1 artifacts until v2 is accepted in production |

## Completion Criteria

Migration is complete only when production uses accepted FRI v2 artifacts, scientific evaluation is approved, rollback is documented, and no forbidden system areas were modified.
