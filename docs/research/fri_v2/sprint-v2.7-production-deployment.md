# Sprint v2.7 — Production Deployment

## Objective

Deploy accepted FRI v2 artifacts to production after all prior sprint gates pass.

## Background

Production deployment is the final step. It must occur only after successful feature engineering, scoring, training, backend migration, integration testing, and scientific evaluation.

## Scope

- Promote accepted FRI v2 artifacts to production configuration.
- Run production smoke tests.
- Confirm rollback readiness.
- Document deployment evidence.

## Out of Scope

- Methodology changes.
- New model training.
- Frontend redesign.
- Dataset edits.
- Infrastructure redesign.

## Scientific Constraints

- Deploy only the artifact accepted in scientific evaluation.
- Do not change features, weights, thresholds, or model algorithm during deployment.
- Keep v1 rollback available until production acceptance is complete.

## Technical Constraints

- Deployment must be traceable to exact artifact checksums.
- API contract must remain compatible.
- Monitoring and rollback instructions must be documented.

## Files Allowed To Modify

- Future-approved production model configuration references.
- Future-approved deployment documentation.
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

- Verify all prior acceptance gates.
- Promote accepted v2 artifact references.
- Run smoke tests.
- Verify rollback procedure.
- Record deployment decision.

## Validation Checklist

- Accepted artifact checksum matches evaluation report.
- Production smoke tests pass.
- API response schema remains compatible.
- Rollback path is ready.
- No forbidden files changed.

## Acceptance Criteria

- FRI v2 is active in production only after all gates pass.
- Deployment evidence is recorded.
- Rollback to v1 remains available.

## Deliverables

- Deployment report.
- Smoke test results.
- Artifact checksum confirmation.
- Rollback readiness confirmation.

## Rollback Plan

Restore production references to the last accepted FRI v1 artifacts and re-run smoke tests. Keep FRI v2 deployment evidence for postmortem and corrective action.
