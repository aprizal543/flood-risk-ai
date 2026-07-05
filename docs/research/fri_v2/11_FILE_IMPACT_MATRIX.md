# FRI v2 File Impact Matrix

## Version

2.0.1 — Documentation Completion

## Objective

Map future FRI v2 implementation sprints to expected project file categories and impact areas. This document is planning-only and does not authorize source code changes during the current documentation sprint.

## Risk Levels

| Risk Level | Meaning |
|------------|---------|
| LOW | Documentation or isolated tests with no runtime effect |
| MEDIUM | Limited implementation change with contained runtime effect |
| HIGH | Model, backend, or inference behavior change requiring validation |
| CRITICAL | Dataset, security, authentication, infrastructure, or deployment configuration impact; forbidden for FRI v2 unless separately approved |

## Impact Matrix

| Sprint | File | Purpose | Risk Level | Allowed Modification | Rollback Needed | Dependency | Impact |
|--------|------|---------|------------|----------------------|-----------------|------------|--------|
| v2.1 Feature Engineering | Future-approved feature engineering files | Select or derive `RR`, `Rain7`, `RH_avg`, `Tavg` for v2 path | HIGH | Yes, only if approved in sprint v2.1 | Yes | Frozen dataset, `01_SPECIFICATION.md` | Affects scoring, training, realtime inference |
| v2.1 Feature Engineering | Future-approved feature selection tests | Validate canonical four-feature output | MEDIUM | Yes, only if approved in sprint v2.1 | No, unless tests alter fixtures | Feature engineering | Prevents removed-feature leakage |
| v2.1 Feature Engineering | `docs/research/fri_v2/` | Record feature mapping and validation evidence | LOW | Yes | No | Design-freeze docs | Improves traceability |
| v2.2 Scoring Engine | Future-approved scoring engine files | Apply FRI v2 feature scores and weights | HIGH | Yes, only if approved in sprint v2.2 | Yes | Feature engineering output, fixed weights | Affects FRI score, labels, training target, backend outputs |
| v2.2 Scoring Engine | Future-approved scoring tests | Validate weights, bounds, and removed-feature exclusion | MEDIUM | Yes, only if approved in sprint v2.2 | No | Scoring engine | Reduces formula regression risk |
| v2.2 Scoring Engine | `docs/research/fri_v2/` | Record formula validation evidence | LOW | Yes | No | `01_SPECIFICATION.md` | Preserves scientific audit trail |
| v2.3 Training | Future-approved training scripts or configuration | Train Random Forest with v2 feature set | HIGH | Yes, only if approved in sprint v2.3 | Yes | Feature engineering, scoring, labels | Produces new model artifact |
| v2.3 Training | Future-approved model artifact path | Store versioned Random Forest v2 artifact | HIGH | Yes, only if approved in sprint v2.3 | Yes | Training output | Affects backend inference after migration |
| v2.3 Training | Future-approved evaluation reports | Record model metrics and artifact checksum | LOW | Yes | No | Training output | Supports scientific review |
| v2.4 Backend Migration | Future-approved backend prediction files | Load and use accepted v2 model/scoring path | HIGH | Yes, only if approved in sprint v2.4 | Yes | Model artifact, scoring engine | Affects API predictions and realtime flow |
| v2.4 Backend Migration | Future-approved backend tests | Validate API compatibility and model loading | MEDIUM | Yes, only if approved in sprint v2.4 | No | Backend migration | Protects production contract |
| v2.4 Backend Migration | `docs/research/fri_v2/` | Record backend migration and rollback evidence | LOW | Yes | No | Migration plan | Supports operational audit |
| v2.5 Integration Testing | Future-approved integration tests | Validate end-to-end v2 pipeline | MEDIUM | Yes, only if approved in sprint v2.5 | No | Feature, scoring, model, backend | Confirms pipeline compatibility |
| v2.5 Integration Testing | Future-approved test fixtures | Provide non-dataset fixtures for tests | MEDIUM | Yes, only if fixtures do not modify source datasets | Yes, if fixtures affect test behavior | Integration tests | Supports repeatable validation |
| v2.5 Integration Testing | `docs/research/fri_v2/` | Record integration test report | LOW | Yes | No | Integration testing | Provides acceptance evidence |
| v2.6 Scientific Evaluation | Future-approved evaluation notebooks or reports | Compare FRI v1 and FRI v2 scientifically | MEDIUM | Yes, only if approved in sprint v2.6 | No | Accepted v2 artifact, v1 baseline | Determines production readiness |
| v2.6 Scientific Evaluation | Future-approved generated evaluation outputs | Store metrics, plots, and comparison summaries | LOW | Yes | No | Evaluation process | Supports accept, revise, or reject decision |
| v2.6 Scientific Evaluation | `docs/research/fri_v2/` | Record scientific recommendation | LOW | Yes | No | Evaluation outputs | Freezes deployment recommendation |
| v2.7 Production Deployment | Future-approved production model references | Point runtime to accepted v2 artifact | HIGH | Yes, only if approved in sprint v2.7 | Yes | Scientific acceptance, artifact checksum | Activates v2 in production |
| v2.7 Production Deployment | Future-approved deployment documentation | Record smoke tests and rollback readiness | LOW | Yes | No | Deployment process | Supports operational traceability |
| v2.7 Production Deployment | Deployment configuration | Runtime deployment settings | CRITICAL | No, unless separately approved outside FRI v2 | Yes | Infrastructure | Forbidden by current FRI v2 boundary |

## Files NEVER Allowed To Change During FRI v2

The following areas are never allowed to change during FRI v2 implementation unless a separate approved non-FRI sprint explicitly changes the boundary:

- Dataset.
- Cleaning.
- Merge.
- Frontend UI.
- Authentication.
- Security.
- Supabase.
- Deployment configuration.

## Enforcement

Every implementation sprint must perform a final changed-file review. Any changed file outside the sprint's allowed list fails acceptance unless the governing documentation is updated and approved before implementation.
