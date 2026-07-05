# Sprint v2.4 — Backend Migration

## Objective

Migrate backend prediction flow to consume accepted FRI v2 scoring and model artifacts while preserving existing API behavior.

## Background

Backend migration must occur only after feature engineering, scoring, and training are accepted. The existing production backend is stable and must not be disrupted prematurely.

## Scope

- Wire backend to accepted v2 feature/scoring/model path.
- Preserve API response schema.
- Validate realtime and batch prediction behavior where applicable.
- Keep rollback to v1 available.

## Out of Scope

- Frontend changes.
- Authentication changes.
- Security changes.
- Supabase changes.
- Infrastructure changes.
- Dataset changes.

## Scientific Constraints

- Backend must use the exact v2 feature order.
- Backend must not reintroduce removed features into FRI v2 scoring.
- Random Forest remains the algorithm.

## Technical Constraints

- Preserve request and response contracts.
- Keep timezone and metadata behavior unchanged unless separately approved.
- Avoid broad refactors unrelated to v2 migration.

## Files Allowed To Modify

- Future-approved backend prediction files.
- Future-approved backend tests.
- Future-approved model configuration references.
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

- Identify backend model and scoring loading path.
- Point backend to accepted v2 artifacts.
- Validate API schema compatibility.
- Add or update backend tests if approved.
- Document rollback switch to v1.

## Validation Checklist

- API contract remains stable.
- Backend loads v2 artifact successfully.
- FRI score remains 0-100.
- Removed features do not affect backend output.
- No forbidden files changed.

## Acceptance Criteria

- Backend can serve predictions using accepted v2 artifacts.
- Existing clients remain compatible.
- Rollback to v1 is documented and tested.

## Deliverables

- Backend migration notes.
- API validation evidence.
- Changed-file review.

## Rollback Plan

Restore backend references to v1 scoring and model artifacts. Re-run API validation against v1 expected behavior.
