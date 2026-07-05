# Sprint v2.2 — Scoring Engine

## Objective

Implement the deterministic FRI v2 scoring formula using the approved four features and fixed weights.

## Background

FRI v2 changes the deterministic feature contribution but keeps the scientific pipeline controlled. This sprint depends on accepted v2.1 feature engineering output.

## Scope

- Implement FRI v2 weighted aggregation.
- Validate weights sum to 100%.
- Ensure removed features have zero contribution.
- Preserve output scale 0-100.

## Out of Scope

- Dataset modification.
- Model retraining.
- Backend API migration.
- Frontend changes.
- Risk-threshold changes unless separately approved.

## Scientific Constraints

- Formula must use `RR` 10%, `Rain7` 50%, `RH_avg` 30%, `Tavg` 10%.
- Random Forest remains unchanged in this sprint.
- Existing risk-class semantics must remain unless separately approved.

## Technical Constraints

- Keep implementation minimal and testable.
- Preserve v1 rollback path.
- Do not change API contracts in this sprint.

## Files Allowed To Modify

- Future-approved scoring engine files.
- Future-approved scoring tests.
- Documentation under `docs/research/fri_v2/`.

## Files Forbidden To Modify

- Dataset.
- Merge scripts.
- Cleaning scripts.
- Frontend.
- Authentication.
- Security.
- Supabase.
- Infrastructure.

## Tasks

- Locate deterministic FRI scoring code.
- Add v2 formula with approved weights.
- Add validation for weight total.
- Test boundary values and missing-value behavior.
- Confirm removed features do not affect output.

## Validation Checklist

- Weight sum equals 1.0 or 100%.
- Output remains bounded to 0-100.
- Removed feature changes do not change FRI v2 score.
- Dataset files are unchanged.

## Acceptance Criteria

- FRI v2 scoring produces deterministic results from the four approved features.
- Tests or validation evidence cover formula correctness.
- No forbidden files are modified.

## Deliverables

- Scoring formula implementation notes.
- Test or validation output.
- Rollback notes.

## Rollback Plan

Disable or revert v2 scoring changes and restore v1 deterministic scoring. Confirm backend still points to accepted production scoring until migration is approved.
