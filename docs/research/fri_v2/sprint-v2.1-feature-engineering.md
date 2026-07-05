# Sprint v2.1 — Feature Engineering

## Objective

Prepare FRI v2 feature engineering so only `RR`, `Rain7`, `RH_avg`, and `Tavg` are produced or selected for the v2 scoring and training path.

## Background

FRI v2 keeps the dataset unchanged and simplifies the feature set. This sprint is the first future implementation sprint and must not alter raw, interim, or processed dataset records.

## Scope

- Identify existing feature engineering entry points.
- Add or adjust v2 feature-selection logic only where explicitly approved.
- Ensure canonical feature order: `RR`, `Rain7`, `RH_avg`, `Tavg`.
- Document mapping from existing columns to v2 features.

## Out of Scope

- Model retraining.
- Scoring engine changes.
- Backend API migration.
- Frontend changes.
- Dataset cleaning or merging.

## Scientific Constraints

- Dataset remains the existing 726-record BMKG dataset.
- No new historical data may be added.
- `Rain3`, `Rain14`, `TempRange`, and `RainfallAnomaly` must not be selected for FRI v2 scoring or training.

## Technical Constraints

- Preserve existing v1 behavior unless a separate v2 path is explicitly introduced.
- Do not mutate source dataset files.
- Keep feature names stable and traceable.

## Files Allowed To Modify

- Future-approved feature engineering files only.
- Future-approved tests for feature selection only.
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

- Locate feature engineering code paths.
- Define v2 feature selection using the approved four features.
- Validate feature order and absence of removed features.
- Add feature-selection tests if test files are approved.
- Update documentation with exact feature mapping.

## Validation Checklist

- Dataset checksum or file diff confirms no dataset change.
- Feature output contains `RR`, `Rain7`, `RH_avg`, `Tavg`.
- Feature output excludes `Rain3`, `Rain14`, `TempRange`, `RainfallAnomaly`.
- Existing v1 path remains recoverable.

## Acceptance Criteria

- Four-feature v2 feature engineering path is ready.
- No forbidden files are modified.
- No model is retrained.
- No backend or frontend behavior changes.

## Deliverables

- Feature mapping notes.
- Validation evidence.
- Changed-file review.

## Rollback Plan

Revert only v2 feature-selection changes and keep v1 feature engineering active. Confirm dataset and pipeline files remain unchanged.
