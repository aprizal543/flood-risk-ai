# FRI v2 Dependency Map

## Version

2.0.1 — Documentation Completion

## Objective

Document dependencies between datasets, feature engineering, scoring, aggregation, labels, Random Forest training, model artifacts, backend inference, realtime prediction, deployment, and dashboard consumption.

## Architecture Diagram

```text
Dataset
  |
  v
Feature Engineering
  |
  v
Scoring
  |
  v
Aggregation
  |
  v
FRI Label
  |
  v
Random Forest Training
  |
  v
Model Artifact
  |
  v
Backend Inference
  |
  v
Realtime Prediction
  |
  v
Dashboard
```

## Dependency Table

| Layer | Inputs | Outputs | Dependencies | Downstream Impact |
|-------|--------|---------|--------------|-------------------|
| Dataset | Existing BMKG Clean Dataset, 726 records | Frozen observation table | Source BMKG records, existing cleaning and merge outputs | Any dataset mutation invalidates feature engineering, scoring, training, evaluation, and scientific comparability |
| Feature Engineering | Dataset columns required to derive or select `RR`, `Rain7`, `RH_avg`, `Tavg` | Canonical FRI v2 feature matrix | Frozen dataset, approved feature list in `01_SPECIFICATION.md` | Changes require regenerating FRI values, retraining Random Forest, replacing model artifact, and updating realtime inference |
| Scoring | `RR`, `Rain7`, `RH_avg`, `Tavg` feature values | Normalized feature scores | Feature engineering output, approved scoring rules, fixed feature names | Score changes affect aggregation, labels, model targets, evaluation, backend inference, and dashboard values |
| Aggregation | Normalized feature scores and weights 10 / 50 / 30 / 10 | Continuous FRI v2 score | Scoring output, approved weights in `01_SPECIFICATION.md` | Weight changes alter FRI labels, model training target, evaluation metrics, and production predictions |
| FRI Label | Continuous FRI v2 score and existing risk-class semantics | Risk class label | Aggregated FRI score, preserved classification policy | Label changes affect Random Forest training, metrics, API outputs, and dashboard risk display |
| Random Forest Training | Feature matrix and FRI v2 label | Trained Random Forest model | Frozen dataset, feature engineering, scoring, aggregation, labels | Training changes produce new model artifacts and require backend validation before production use |
| Model Artifact | Trained Random Forest output and metadata | Versioned model file with feature order and checksum | Training configuration, feature order, artifact serialization | Artifact replacement affects backend inference and rollback readiness |
| Backend Inference | Model artifact, realtime feature inputs, scoring path | Prediction API response | Accepted model artifact, backend loading logic, API contract | Backend changes affect realtime prediction, clients, integration tests, and production stability |
| Realtime Prediction | Backend inference result and realtime weather-derived features | Current prediction for requested location/date | Backend inference, realtime data provider, feature ordering | Realtime changes affect dashboard values and user-facing decision support |
| Dashboard | Realtime prediction API response | User-facing FRI, risk level, and decision support display | Stable API response contract | API contract drift can break frontend display; frontend UI changes are outside FRI v2 scope |

## Critical Dependency Rule

Changing Feature Engineering requires:

- Regenerate FRI values.
- Retrain Random Forest.
- Replace model artifact.
- Update realtime inference.
- Re-run integration tests.
- Re-run scientific evaluation.
- Reconfirm rollback readiness.

## Protected Dependencies

FRI v2 must not alter the frozen dataset, cleaning scripts, merge scripts, frontend UI, authentication, security, Supabase, or infrastructure unless a separate approved sprint explicitly changes the boundary in `04_BOUNDARY.md`.

## Cross-References

- `01_SPECIFICATION.md` defines the approved feature set, weights, and algorithm.
- `03_MIGRATION_PLAN.md` defines the future migration sequence.
- `07_IMPLEMENTATION_RULES.md` defines mandatory implementation constraints.
- `12_VALIDATION_DATASET.md` freezes the validation dataset specification.
