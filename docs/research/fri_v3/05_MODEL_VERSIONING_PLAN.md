# Model Versioning Plan — FRI v3

## Objective

Define the versioning strategy for model artifacts, datasets, and metadata associated with FRI v3 implementation. This plan ensures traceability, reproducibility, and safe rollback without overwriting production artifacts.

---

## Artifact Naming Convention

### Model Artifacts

| Version | File Name | Status |
|---------|-----------|--------|
| FRI v1 | `random_forest.pkl` | Legacy (retained for rollback) |
| FRI v2 | `random_forest_v2.pkl` | Current production |
| FRI v3 | `random_forest_v3.pkl` | Target (to be created) |

### Dataset Artifacts

| Version | File Name | Status |
|---------|-----------|--------|
| FRI v2 target | `bmkg_fri_v2.csv` | Existing |
| FRI v3 target | `bmkg_fri_v3.csv` | To be created |

### Scaler Artifacts

The scaler (`scaler_lstm.pkl`) is unchanged between v2 and v3. No new scaler artifact is required for the Random Forest model.

---

## File Locations

| Artifact Type | v2 Location | v3 Location |
|---------------|-------------|-------------|
| Model | `ml/artifacts/random_forest_v2.pkl` | `ml/artifacts/random_forest_v3.pkl` |
| Dataset | `data/processed/bmkg_fri_v2.csv` | `data/processed/bmkg_fri_v3.csv` |
| Feature list | `ml/artifacts/feature_list.json` | Unchanged (same 4 features) |
| Scaler | `ml/artifacts/scaler_lstm.pkl` | Unchanged |
| Model metadata | `docs/research/fri_v2/` | `docs/research/fri_v3/` |

---

## Model Metadata Structure

Each model artifact must be accompanied by a metadata JSON file with the following schema:

```json
{
  "model_version": "3.0",
  "training_date": "YYYY-MM-DD",
  "dataset": {
    "version": "v3",
    "source": "bmkg_fri_v3.csv",
    "record_count": 726,
    "feature_count": 4,
    "features": ["RR", "Rain7", "RH_avg", "Tavg"],
    "target": "FRI_v3",
    "weight_configuration": {
      "RR": 0.25,
      "Rain7": 0.25,
      "RH_avg": 0.25,
      "Tavg": 0.25
    },
    "frozen_since": "2026-07-07"
  },
  "training_parameters": {
    "algorithm": "RandomForestRegressor",
    "n_estimators": 100,
    "max_depth": null,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42
  },
  "splits": {
    "method": "chronological",
    "train_start": "YYYY-MM-DD",
    "train_end": "YYYY-MM-DD",
    "test_start": "YYYY-MM-DD",
    "test_end": "YYYY-MM-DD",
    "train_size": 580,
    "test_size": 146
  },
  "evaluation": {
    "MAE": null,
    "RMSE": null,
    "R2": null,
    "test_records": 146
  },
  "artifact": {
    "path": "ml/artifacts/random_forest_v3.pkl",
    "checksum_sha256": null,
    "file_size_bytes": null
  }
}
```

---

## Versioning Rules

### Rule 1: Never Overwrite Production Artifacts
- `random_forest_v2.pkl` must never be deleted or overwritten.
- `random_forest_v2.pkl` remains the production artifact until an approved deployment process replaces it.
- `random_forest_v3.pkl` is a candidate artifact until formally accepted.

### Rule 2: Sequential Versioning
- FRI versions follow a strict monotonic integer sequence: v1 → v2 → v3 → ...
- No version number reuse.
- If v3 is rejected, the next attempt is v4 (not v3 rev2).

### Rule 3: Dataset Version Matches FRI Version
- Dataset_v3 uses FRI_v3 target.
- Dataset_v3 column naming must include `FRI_v3` to distinguish from `FRI_v2`.
- Historical datasets (Dataset_v1, Dataset_v2) are retained indefinitely.

### Rule 4: Metadata Is Mandatory
- Every model artifact must have a corresponding metadata record.
- Metadata must be committed alongside the artifact in the same deployment.
- Checksums must be computed immediately after training.

### Rule 5: Backward-Compatible Feature Order
- The feature order for v3 is identical to v2: ["RR", "Rain7", "RH_avg", "Tavg"].
- `feature_list.json` remains unchanged.
- This ensures the v3 model is a drop-in replacement for the v2 backend without API changes.

---

## Model Loading Strategy

The backend must support loading both v2 and v3 models. Implementation approach:

### Option A: Model Name Parameter (Recommended)
- API request includes `model_version` parameter ("v2" or "v3")
- Backend loads the corresponding artifact
- Default: "v2" (until v3 is validated for production)

### Option B: Gradual Rollout
- Deploy v3 alongside v2 in a shadow mode
- Both models run in parallel for a validation period
- Compare real-time outputs before switching

---

## Rollback Procedure

If v3 deployment requires rollback:

1. Revert API configuration to load `random_forest_v2.pkl`
2. No code changes required (v2 artifact was never overwritten)
3. Retain `random_forest_v3.pkl` for post-mortem analysis
4. Document rollback reason in decision log

---

## Deployment Phasing

| Phase | Action | Artifact |
|-------|--------|----------|
| 0 | Current production | random_forest_v2.pkl |
| 1 | Train v3 in offline environment | random_forest_v3_candidate.pkl |
| 2 | Validate v3 against test set | Evaluation report |
| 3 | Deploy v3 to staging | random_forest_v3_staging.pkl |
| 4 | A/B test v3 vs. v2 | Both models in shadow mode |
| 5 | Approve v3 for production | random_forest_v3.pkl promoted |
| 6 | Production switch | Model loader points to v3 |
| 7 | Post-deployment monitoring | Both artifacts retained |
