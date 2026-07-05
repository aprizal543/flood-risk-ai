# Sprint v2.6 — Scientific Evaluation

## Objective

Evaluate FRI v2 scientifically against FRI v1 and document whether v2 is acceptable for production deployment.

## Background

FRI v2 changes the explanatory feature set and weights. Scientific evaluation must demonstrate that the simplified methodology is valid, interpretable, and suitable for FloodRisk AI use cases.

## Scope

- Compare FRI v1 and FRI v2 outputs.
- Evaluate model metrics.
- Analyze feature contribution and interpretability.
- Document limitations.
- Recommend accept, revise, or reject.

## Out of Scope

- Production deployment.
- Backend migration changes.
- Frontend changes.
- Dataset expansion.
- Algorithm replacement.

## Scientific Constraints

- Use the unchanged 726-record BMKG dataset.
- Use approved v2 features and weights.
- Clearly state uncertainty and limitations.
- Do not tune methodology silently during evaluation.

## Technical Constraints

- Evaluation must be reproducible.
- Metrics and plots must reference exact artifact versions.
- Any proposed change requires a new ADR before implementation.

## Files Allowed To Modify

- Future-approved evaluation notebooks or reports.
- Future-approved generated evaluation outputs.
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

- Define evaluation metrics.
- Compare FRI v1 and v2 distributions.
- Compare classification outcomes.
- Assess model performance.
- Write scientific evaluation report.

## Validation Checklist

- Evaluation uses approved v2 artifact.
- Dataset remains unchanged.
- v1 baseline is documented.
- Limitations are explicit.
- Recommendation is clear.

## Acceptance Criteria

- Scientific report recommends accept, revise, or reject.
- Metrics and interpretation are complete.
- No forbidden files are modified.

## Deliverables

- Scientific evaluation report.
- Metric tables.
- v1 vs v2 comparison summary.
- Recommendation for production readiness.

## Rollback Plan

If v2 is rejected or requires revision, keep production on FRI v1 and open a new methodology revision sprint before further implementation.
