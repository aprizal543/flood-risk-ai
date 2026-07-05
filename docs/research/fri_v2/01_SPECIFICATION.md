# FRI v2 Technical Specification

## Version

2.0 — Design Freeze

## Objective

Define the approved FRI v2 methodology for future implementation while keeping the current production system unchanged during this documentation sprint.

## Dataset Specification

FRI v2 must use the existing BMKG dataset exactly as it exists at design freeze.

| Constraint | Requirement |
|------------|-------------|
| Dataset size | 726 records |
| Data source | Existing BMKG dataset only |
| Additional historical data | Forbidden |
| Dataset edits | Forbidden |
| Cleaning pipeline changes | Forbidden |
| Merge pipeline changes | Forbidden |

## Feature Set

### Retained Features

| Feature | Meaning | FRI v2 Role |
|---------|---------|-------------|
| `RR` | Daily rainfall | Direct daily rainfall trigger |
| `Rain7` | Seven-day accumulated rainfall | Dominant antecedent rainfall signal |
| `RH_avg` | Average relative humidity | Atmospheric moisture persistence signal |
| `Tavg` | Average temperature | Supporting thermal condition signal |

### Removed Features

| Feature | v2 Decision |
|---------|-------------|
| `Rain3` | Removed from FRI v2 scoring and weighting |
| `Rain14` | Removed from FRI v2 scoring and weighting |
| `TempRange` | Removed from FRI v2 scoring and weighting |
| `RainfallAnomaly` | Removed from FRI v2 scoring and weighting |

Removal means the feature must not contribute to the deterministic FRI v2 score. It does not authorize deletion of historical documentation, datasets, or unrelated production code during this documentation sprint.

## Weighting Formula

FRI v2 uses four normalized feature scores with fixed weights:

```text
FRI_v2 = 0.10 * Score(RR)
       + 0.50 * Score(Rain7)
       + 0.30 * Score(RH_avg)
       + 0.10 * Score(Tavg)
```

| Feature | Weight |
|---------|--------|
| `RR` | 10% |
| `Rain7` | 50% |
| `RH_avg` | 30% |
| `Tavg` | 10% |
| Total | 100% |

## Algorithm

Random Forest remains the approved machine learning algorithm. Future implementation may retrain model artifacts only in the dedicated training sprint and only after feature engineering and scoring documents are accepted.

## Scientific Rationale

FRI v2 prioritizes a simpler hydrometeorological explanation:

- `Rain7` receives the largest weight because antecedent weekly rainfall is the primary saturation and flood-risk accumulation signal.
- `RH_avg` receives the second-largest weight because persistent humidity indicates atmospheric moisture conditions that can sustain rainfall and reduce evaporation.
- `RR` remains a direct trigger but receives lower weight because single-day rainfall without antecedent accumulation is insufficient to explain all flood-risk states.
- `Tavg` is retained as a supporting environmental variable with limited direct contribution.

## Classification Policy

FRI v2 must preserve the existing risk-class semantics unless a future approved scientific evaluation explicitly changes thresholds. No threshold change is authorized by this documentation sprint.

## Traceability Requirements

Future implementation must document:

- Source column mapping for each retained feature.
- Scoring function used for each retained feature.
- Weight application and sum validation.
- Model feature order.
- Evaluation metrics compared against FRI v1.
- Any generated model artifact checksum.

## Frozen Scope

This specification freezes design only. It does not authorize code edits, backend edits, frontend edits, dataset edits, model retraining, or production deployment.
