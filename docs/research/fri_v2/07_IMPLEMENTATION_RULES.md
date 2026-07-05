# FRI v2 Implementation Rules

## Objective

Define mandatory rules for future implementation sprints. These rules do not authorize implementation during the current documentation sprint.

## Rule 1: Dataset Is Immutable

The existing BMKG dataset must remain unchanged at 726 records. Do not add, delete, edit, re-clean, or re-merge records for FRI v2.

## Rule 2: Feature Set Is Closed

FRI v2 may use only:

- `RR`
- `Rain7`
- `RH_avg`
- `Tavg`

No other feature may contribute to deterministic FRI v2 scoring.

## Rule 3: Removed Features Stay Removed From Scoring

The following features must not contribute to FRI v2 scoring:

- `Rain3`
- `Rain14`
- `TempRange`
- `RainfallAnomaly`

## Rule 4: Weights Are Fixed

Weights must be exactly:

- `RR`: 10%
- `Rain7`: 50%
- `RH_avg`: 30%
- `Tavg`: 10%

The total must equal 100%.

## Rule 5: Random Forest Remains The Algorithm

Do not replace Random Forest with another algorithm in FRI v2 implementation sprints.

## Rule 6: Forbidden Areas Are Protected

Do not modify dataset files, merge scripts, cleaning scripts, frontend, authentication, security, Supabase, or infrastructure unless a separate approved sprint explicitly authorizes it.

## Rule 7: Preserve API Compatibility

Future backend migration must preserve existing API response shape unless a separate API migration document is approved.

## Rule 8: Prove Changes With Validation

Every future implementation sprint must include validation evidence, changed-file review, and rollback notes.

## Rule 9: No Silent Scientific Changes

Any change to thresholds, classification rules, feature transforms, or evaluation criteria requires a new ADR before implementation.
