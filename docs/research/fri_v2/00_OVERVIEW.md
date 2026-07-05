# FRI v2 Documentation Overview

## Status

Design Freeze — Documentation Only

## Objective

Freeze the approved Flood Risk Index v2 methodology before implementation begins. This documentation package defines the scientific scope, technical boundaries, migration sequence, acceptance criteria, rollback strategy, and future sprint rules for FRI v2.

## Background

FRI v1 is stable, security audited, and production-ready. FRI v2 is a scientific revision that simplifies the deterministic flood-risk feature set while preserving the existing dataset, Random Forest algorithm, production architecture, and operational safety posture.

## Frozen Decisions

| Area | Decision |
|------|----------|
| Dataset | Keep existing BMKG dataset unchanged at 726 records |
| Historical data | Do not add additional historical data |
| Data pipeline | Do not modify cleaning or merge pipeline |
| Algorithm | Keep Random Forest unchanged |
| Retained FRI features | `RR`, `Rain7`, `RH_avg`, `Tavg` |
| Removed FRI features | `Rain3`, `Rain14`, `TempRange`, `RainfallAnomaly` |
| Feature weights | `RR` 10%, `Rain7` 50%, `RH_avg` 30%, `Tavg` 10% |

## Documentation Map

| Document | Purpose |
|----------|---------|
| `01_SPECIFICATION.md` | Scientific and technical specification for FRI v2 |
| `02_ADR.md` | Architecture decision record for the v2 methodology |
| `03_MIGRATION_PLAN.md` | Sequenced future migration plan without current implementation |
| `04_BOUNDARY.md` | Explicit allowed and forbidden boundaries |
| `05_ACCEPTANCE_CRITERIA.md` | Design-freeze and future sprint acceptance gates |
| `06_ROLLBACK_PLAN.md` | Strategy for reverting future v2 implementation to v1 |
| `07_IMPLEMENTATION_RULES.md` | Rules future implementers must follow |
| `08_PROJECT_STATE.md` | Current project state at documentation freeze |

## Sprint Map

| Sprint | Purpose |
|--------|---------|
| `sprint-v2.1-feature-engineering.md` | Prepare feature engineering changes |
| `sprint-v2.2-scoring-engine.md` | Update deterministic FRI scoring and weighting |
| `sprint-v2.3-training.md` | Retrain and evaluate Random Forest only when approved |
| `sprint-v2.4-backend-migration.md` | Migrate backend consumption of v2 artifacts |
| `sprint-v2.5-integration-testing.md` | Validate end-to-end compatibility |
| `sprint-v2.6-scientific-evaluation.md` | Perform scientific comparison and reporting |
| `sprint-v2.7-production-deployment.md` | Deploy v2 only after all gates pass |

## Non-Implementation Statement

This package does not implement FRI v2. It does not modify source code, backend behavior, frontend behavior, datasets, trained model artifacts, authentication, security, Supabase, or infrastructure.
