# Implementation Roadmap — FRI Version 3

## Objective

Define the phased implementation sequence for FRI v3 from design freeze through production deployment. Each phase is a separate sprint or work package with defined inputs, outputs, and acceptance criteria.

---

## Phase Overview

```
Phase 1: FRI v3 Target Generation
    ↓
Phase 2: Dataset_v3 Construction
    ↓
Phase 3: Exploratory Data Analysis
    ↓
Phase 4: Distribution Analysis
    ↓
Phase 5: Model Training (RandomForest_v3)
    ↓
Phase 6: Model Evaluation
    ↓
Phase 7: Model Versioning & Artifact Management
    ↓
Phase 8: Production Deployment
```

---

## Phase 1: FRI v3 Target Generation

**Objective**: Generate the FRI_v3 target values using the approved equal-weight formula.

**Input**: `data/processed/bmkg_clean.csv` (existing BMKG dataset)

**Process**:
1. Load individual variable scores (RR, Rain7, RH_avg, Tavg) — identical scoring functions to v2
2. Apply weight configuration:
   ```
   FRI_v3 = 0.25 × Score(RR) + 0.25 × Score(Rain7) + 0.25 × Score(RH_avg) + 0.25 × Score(Tavg)
   ```
3. Validate weight sum = 1.0
4. Validate FRI_v3 ∈ [0, 100] for all records
5. Compute confidence scores

**Output**: FRI_v3 column appended to the clean dataset.

**Acceptance Criteria**:
- All 726 records have valid FRI_v3 values (no NaN)
- Weight sum = 1.0 (floating-point tolerance: ±1e-10)
- FRI_v3 ∈ [0, 100] for all records
- FRI_v3 ≠ FRI_v2 for at least some records (confirms weight change took effect)

---

## Phase 2: Dataset_v3 Construction

**Objective**: Create the formal Dataset_v3 CSV file with features and FRI_v3 target.

**Input**: Phase 1 output (clean dataset with FRI_v3 column)

**Process**:
1. Select feature columns: RR, Rain7, RH_avg, Tavg
2. Select target column: FRI_v3
3. Create `data/processed/bmkg_fri_v3.csv`
4. Add metadata header or sidecar file with weight configuration
5. Verify column structure matches FEATURE_ORDER_V2

**Output**: `data/processed/bmkg_fri_v3.csv`

**Acceptance Criteria**:
- File has exactly 726 rows
- Columns: [tanggal, RR, Rain7, RH_avg, Tavg, FRI_v3]
- FRI_v3 matches Phase 1 computation
- SHA-256 checksum recorded

---

## Phase 3: Exploratory Data Analysis

**Objective**: Understand the statistical properties of Dataset_v3 before training.

**Input**: Dataset_v3

**Tasks**:
1. Summary statistics (mean, median, σ, skewness, kurtosis, min, max)
2. Pairplot of features vs. FRI_v3 target
3. Correlation matrix (features and target)
4. Missing value check
5. Temporal pattern inspection (monthly means)
6. Comparison with Dataset_v2 summary

**Output**: EDA report with figures

**Acceptance Criteria**:
- Distribution is not degenerate (σ > 10)
- Feature-target correlations are physically plausible
- Temporal patterns match seasonal expectation

---

## Phase 4: Distribution Analysis

**Objective**: Formally compare FRI_v2 and FRI_v3 distributions.

**Input**: Dataset_v2, Dataset_v3

**Tasks**:
1. Overlay histogram (see Experiment Plan §A1)
2. Boxplot comparison (§A2)
3. Risk class distribution comparison (§A3)
4. Binned distribution table (§A4)
5. CDF comparison (§A5)
6. Kolmogorov-Smirnov test

**Output**: Distribution comparison report with figures

**Acceptance Criteria**:
- Distribution differences quantified and documented
- Visual inspection confirms no implausible patterns
- KS test results recorded (no pass/fail; descriptive only)

---

## Phase 5: Model Training

**Objective**: Train RandomForest_v3 on Dataset_v3.

**Input**: Dataset_v3 (train split, 80% chronological)

**Process**:
1. Apply chronological 80/20 split (identical to v2 split)
2. Train RandomForestRegressor with identical hyperparameters to v2:
   - n_estimators: 100
   - max_depth: None
   - min_samples_split: 2
   - min_samples_leaf: 1
   - random_state: 42
3. No feature scaling required (Random Forest is scale-invariant)
4. Save model to `ml/artifacts/random_forest_v3.pkl`
5. Record metadata (see Versioning Plan)

**Output**: `random_forest_v3.pkl`, `model_metadata_v3.json`

**Acceptance Criteria**:
- Model loads successfully
- Feature order matches FEATURE_ORDER_V2
- Training completes without error
- Artifact checksum recorded

---

## Phase 6: Model Evaluation

**Objective**: Compare RandomForest_v2 and RandomForest_v3 performance.

**Input**: RandomForest_v2 (trained on Dataset_v2), RandomForest_v3 (trained on Dataset_v3), test split

**Tasks** (per Experiment Plan §C):
1. Compute regression metrics (MAE, RMSE, R², MAPE)
2. Residual analysis
3. Feature importance comparison
4. Prediction distribution comparison
5. Regression-to-the-mean analysis (β₁ slope)
6. Classification agreement analysis
7. Extreme-value subgroup analysis

**Output**: Experiment Report with all metrics and figures

**Acceptance Criteria** (go/no-go):
- MAE_v3 ≤ 1.10 × MAE_v2
- R²_v3 ≥ R²_v2 − 0.05
- σ(pred_v3) > σ(pred_v2)
- FRI_v3 range ≥ 0.80 × FRI_v2 range

---

## Phase 7: Model Versioning & Artifact Management

**Objective**: Formalise all artifacts with versioning and documentation.

**Input**: All Phase 5 and Phase 6 outputs

**Process**:
1. Update `feature_list.json` (confirm it remains ["RR", "Rain7", "RH_avg", "Tavg"])
2. Record `random_forest_v3.pkl` SHA-256 checksum
3. Create model metadata JSON
4. Archive Dataset_v3 with checksum
5. Document evaluation results in release notes

**Output**: Versioned and documented artifacts

**Acceptance Criteria**:
- All artifacts have checksums
- Metadata is complete per schema
- v2 artifacts are preserved intact

---

## Phase 8: Production Deployment

**Objective**: Deploy RandomForest_v3 to production environment.

**Input**: Approved and validated RandomForest_v3

**Sub-phases**:

### 8.1 Backend Update
- Update model loader to support v3
- Add `model_version` parameter to API (default: v2)
- Preserve v2 model loading path

### 8.2 Staging Deployment
- Deploy v3 to staging environment
- Run integration tests against staging API
- Validate end-to-end prediction flow

### 8.3 Shadow Mode (Recommended)
- Run v2 and v3 in parallel
- Compare predictions on live data for N days
- Document any discrepancies

### 8.4 Production Switch
- Change default model to v3
- Monitor error rates, latency, and prediction distribution
- Prepare rollback procedure

### 8.5 Post-Deployment Monitoring
- Monitor prediction distribution for drift
- Compare with expected distribution from training
- Document any anomalies

**Output**: Production deployment with v3 model active

**Acceptance Criteria**:
- API returns correct predictions for v2 and v3
- Backward compatibility with existing API consumers
- No regression in API latency (>10% increase triggers review)
- Successful rollback tested

---

## Dependencies

| Phase | Depends On | External Dependencies |
|-------|-----------|----------------------|
| 1 | Design freeze acceptance | BMKG clean dataset |
| 2 | Phase 1 | — |
| 3 | Phase 2 | — |
| 4 | Phase 2, Dataset_v2 | — |
| 5 | Phase 2 | scikit-learn (existing) |
| 6 | Phase 5, v2 model | — |
| 7 | Phases 5, 6 | — |
| 8 | Phase 7 | Azure App Service, Vercel |

---

## Notional Timeline

| Phase | Estimated Effort | Priority |
|-------|-----------------|----------|
| 1: FRI v3 Generation | 1 day | Critical path |
| 2: Dataset_v3 | 0.5 day | Critical path |
| 3: EDA | 1 day | Parallel to 4 |
| 4: Distribution Analysis | 1 day | Parallel to 3 |
| 5: Training | 0.5 day | After 2 |
| 6: Evaluation | 1.5 days | After 5 |
| 7: Versioning | 0.5 day | After 6 |
| 8: Deployment | 2 days | After 7 |

---

## Out of Scope per Phase

Throughout all phases:

| Forbidden | Rationale |
|-----------|-----------|
| Modifying scoring functions | Would confound weight change effect |
| Adding/removing features | Weight-only revision |
| Changing Random Forest algorithm | Algorithm isolation |
| Changing dataset records | Dataset isolation |
| Modifying risk thresholds | Not part of this revision |
| Modifying frontend | Out of scope |
| Modifying Azure/Vercel | Deployment infrastructure unchanged |
