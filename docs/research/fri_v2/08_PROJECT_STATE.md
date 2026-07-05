# FRI v2 Project State At Design Freeze

## Date

2026-07-05

## State Summary

FloodRisk AI is stable on FRI v1. FRI v2 is approved as a future scientific revision but is not implemented in this sprint.

## Current Stable System

| Area | State |
|------|-------|
| FRI v1 | Stable and production-ready |
| Security | Audited and frozen for this sprint |
| Backend | Must remain unchanged |
| Frontend | Must remain unchanged |
| Dataset | Existing BMKG dataset, 726 records |
| Model | Existing production model remains active |

## Approved FRI v2 Target

| Area | Target |
|------|--------|
| Dataset | Same 726-record BMKG dataset |
| Algorithm | Random Forest |
| Features | `RR`, `Rain7`, `RH_avg`, `Tavg` |
| Weights | 10%, 50%, 30%, 10% |
| Removed from FRI scoring | `Rain3`, `Rain14`, `TempRange`, `RainfallAnomaly` |

## Current Sprint Output

The current sprint creates documentation only under `docs/research/fri_v2/`. It does not change runtime behavior.

## Next State

The next authorized implementation step is Sprint v2.1 Feature Engineering, but only after this documentation set is reviewed and accepted.
