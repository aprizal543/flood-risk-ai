# Sprint v2.3 — Training

## Objective

Retrain the Random Forest model with the approved FRI v2 feature set after feature engineering and scoring are accepted.

## Background

FRI v2 keeps Random Forest as the algorithm but changes the feature set. Training must occur only in this dedicated sprint and must be reproducible.

## Scope

- Train Random Forest using `RR`, `Rain7`, `RH_avg`, and `Tavg`.
- Record feature order and training configuration.
- Generate evaluation metrics.
- Preserve v1 model artifacts for rollback.

## Out of Scope

- Algorithm replacement.
- Dataset expansion.
- Cleaning or merge changes.
- Backend deployment.
- Frontend changes.

## Scientific Constraints

- Use only the existing 726-record BMKG dataset.
- Use only approved v2 features.
- Do not include removed features in training.
- Compare results against v1 baseline.

## Technical Constraints

- Training must be reproducible.
- Model artifact metadata must include feature order.
- Do not overwrite v1 artifact without an approved rollback copy.

## Files Allowed To Modify

- Future-approved training scripts or configuration.
- Future-approved model artifact output location.
- Future-approved evaluation reports.
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

- Confirm v2 feature matrix.
- Train Random Forest with fixed configuration.
- Save artifact with versioned naming.
- Record metrics, feature order, and artifact checksum.
- Compare v2 model against v1 baseline.

## Validation Checklist

- Training input has exactly four approved features.
- Removed features are absent.
- Dataset record count remains 726.
- Artifact loads successfully.
- Metrics are documented.

## Acceptance Criteria

- Reproducible Random Forest v2 artifact exists.
- Evaluation report is complete.
- v1 rollback artifact remains available.
- No forbidden files are modified.

## Deliverables

- Versioned model artifact.
- Training metadata.
- Evaluation metrics.
- Artifact checksum.

## Rollback Plan

Restore the last accepted v1 model artifact and remove v2 artifact references from future runtime configuration if validation fails.
