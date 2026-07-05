# ADR: Adopt FRI v2 Simplified Feature Methodology

## Status

Accepted — Design Freeze

## Date

2026-07-05

## Context

FloodRisk AI currently operates with stable FRI v1 methodology and production-ready implementation. A scientific revision has been approved to simplify the Flood Risk Index by reducing feature count and emphasizing weekly rainfall accumulation and humidity.

## Decision

Adopt FRI v2 as the next methodology target with the following frozen decisions:

- Keep the existing BMKG dataset unchanged at 726 records.
- Do not add historical observations.
- Do not modify cleaning or merge scripts.
- Retain only `RR`, `Rain7`, `RH_avg`, and `Tavg` for FRI v2 scoring.
- Remove `Rain3`, `Rain14`, `TempRange`, and `RainfallAnomaly` from FRI v2 scoring.
- Use weights: `RR` 10%, `Rain7` 50%, `RH_avg` 30%, `Tavg` 10%.
- Keep Random Forest as the algorithm.

## Rationale

The revised methodology improves interpretability by focusing on four hydrometeorological signals. Weekly accumulated rainfall is treated as the dominant risk driver, while humidity and temperature provide supporting environmental context. The decision avoids dataset expansion so scientific comparisons remain controlled against FRI v1.

## Consequences

Future implementation must update feature engineering, scoring, training, backend consumption, integration tests, scientific evaluation, and deployment documentation in separate controlled sprints. This ADR does not modify production behavior.

## Non-Decisions

This ADR does not decide to:

- Change risk thresholds.
- Replace Random Forest.
- Change frontend design.
- Change authentication, authorization, or security controls.
- Change Supabase, hosting, or infrastructure.
- Modify raw, interim, or processed datasets.

## Compliance Requirement

Any future sprint that implements FRI v2 must reference this ADR and prove that forbidden areas remain unchanged.
