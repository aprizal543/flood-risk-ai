# Sprint v2.5 — Integration Testing

## Objective

Validate the integrated FRI v2 pipeline across feature engineering, scoring, model loading, and backend prediction paths.

## Background

After backend migration, FRI v2 must be tested end-to-end before scientific evaluation and production deployment.

## Scope

- Run integration tests for FRI v2 prediction flow.
- Validate API compatibility.
- Validate deterministic scoring consistency.
- Validate model artifact loading.
- Validate rollback path.

## Out of Scope

- New feature development.
- Frontend redesign.
- Dataset modification.
- Infrastructure deployment.
- Algorithm changes.

## Scientific Constraints

- Test inputs must use approved v2 features.
- Removed features must not influence FRI v2 outputs.
- Tests must not alter the dataset.

## Technical Constraints

- Tests must be repeatable.
- Test artifacts must not replace production artifacts.
- API response shape must remain compatible.

## Files Allowed To Modify

- Future-approved integration tests.
- Future-approved test fixtures that do not modify source datasets.
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

- Define end-to-end test cases.
- Run feature-to-score validation.
- Run score-to-model/backend validation.
- Validate rollback behavior.
- Record all failures and fixes.

## Validation Checklist

- Integration tests pass.
- API contract remains stable.
- Dataset diff is empty.
- Rollback path succeeds.
- No forbidden files changed.

## Acceptance Criteria

- Integrated FRI v2 pipeline passes agreed tests.
- No unresolved critical defects remain.
- Rollback evidence is documented.

## Deliverables

- Integration test report.
- API compatibility evidence.
- Rollback validation evidence.

## Rollback Plan

If integration fails, keep production on FRI v1 and revert only v2 integration changes. Preserve failure evidence for the next corrective sprint.
