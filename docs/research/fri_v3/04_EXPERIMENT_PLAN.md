# Experiment Plan — FRI v2 vs. FRI v3 Comparison

## Objective

Define the experimental protocol for comparing FRI v2 and FRI v3 across distributional, predictive, and decision-level outcomes.

---

## Design

### Type
Controlled experiment with a single intervention: weight reconfiguration.

### Independent Variable
Weight configuration:
- Control: FRI v2 (RR=10%, Rain7=50%, RH_avg=30%, Tavg=10%)
- Treatment: FRI v3 (RR=25%, Rain7=25%, RH_avg=25%, Tavg=25%)

### Controlled Variables
- Dataset: BMKG 726 records, unchanged
- Feature engineering: Identical for both versions
- Scoring functions: Identical for both versions
- ML algorithm: Random Forest (identical hyperparameters)
- Train/test split: Chronological 80/20, same split for both
- Evaluation metrics: Identical calculation

### Dependent Variables
See measurement protocol below.

---

## Dataset

| Property | Value |
|----------|-------|
| Source | BMKG Sultan Syarif Kasim II, Pekanbaru |
| Records | 726 |
| Features | RR, Rain7, RH_avg, Tavg |
| Target (Control) | FRI_v2 = 0.10×Score(RR) + 0.50×Score(Rain7) + 0.30×Score(RH_avg) + 0.10×Score(Tavg) |
| Target (Treatment) | FRI_v3 = 0.25×Score(RR) + 0.25×Score(Rain7) + 0.25×Score(RH_avg) + 0.25×Score(Tavg) |
| Split | Chronological (80% train, 20% test), shuffle=False |

---

## Measurement Protocol

### Phase A: Distribution Analysis (Pre-Training)

Compare the statistical properties of FRI_v2 vs. FRI_v3 across the full dataset.

#### A1. Distribution Histogram
- Overlay histogram of FRI_v2 and FRI_v3 on the same axis
- Bin width: 5 FRI units
- Report: Mean, median, standard deviation, skewness, kurtosis for each

#### A2. Boxplot Comparison
- Side-by-side boxplot of FRI_v2 and FRI_v3
- Report: Min, Q1, median, Q3, max, IQR, outlier count

#### A3. Risk Class Distribution
- Compute Low (0–33), Medium (34–66), High (67–100) proportions for each version
- Contingency table of class transitions (v2 → v3)
- Report: Number and percentage of records changing class

#### A4. Binned Distribution Table
- Binned counts for bins: 0–10, 10–20, 20–30, ..., 90–100
- Identify bins with largest absolute change between versions

#### A5. Cumulative Distribution Function (CDF)
- Plot CDF of both versions
- Identify quantile shifts (e.g., P50, P75, P90, P95)

### Phase B: Training

#### B1. Dataset Preparation
- Generate Dataset_v2 (features + FRI_v2 target)
- Generate Dataset_v3 (features + FRI_v3 target)

#### B2. Model Training
- Train RandomForest_v2 on Dataset_v2
- Train RandomForest_v3 on Dataset_v3
- Hyperparameters: identical to current production RandomForest_v2.pkl
- Fixed seed for reproducibility

#### B3. Model Metadata
Record for each model:
- Training date and time
- Dataset version
- FRI version
- Feature order
- Weight configuration
- Hyperparameter configuration
- Training record count
- Checksum (SHA-256) of artifact

### Phase C: Evaluation

#### C1. Regression Metrics
Compute on held-out test set:

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| MAE | (1/n) Σ \|y_i − ŷ_i\| | Mean absolute prediction error |
| RMSE | √[(1/n) Σ (y_i − ŷ_i)²] | Root mean squared error (penalises large errors) |
| R² | 1 − (SS_res / SS_tot) | Proportion of variance explained |
| MAPE | (100/n) Σ \|(y_i − ŷ_i) / y_i\| | Mean absolute percentage error |

#### C2. Residual Analysis
- Residual plot: ŷ vs. (y − ŷ)
- Residual histogram with normal overlay
- Q-Q plot of residuals
- Report: residual mean, residual standard deviation, Durbin-Watson statistic

#### C3. Feature Importance
- Compare feature importance (Gini importance) between v2 and v3 models
- Identify whether importance ranking changes

#### C4. Prediction Distribution
- Histogram of predicted FRI values (v2 and v3)
- Overlay with actual target distribution
- Report: σ(pred), min(pred), max(pred), range(pred)

#### C5. Regression-to-the-Mean Analysis
- Scatter plot: actual FRI vs. predicted FRI
- Fit linear regression: y_pred = β₀ + β₁ × y_actual
- For a perfect predictor: β₀ = 0, β₁ = 1
- Regression-to-the-mean indicated by β₁ < 1
- Compare β₁ between v2 and v3 predictions

#### C6. Classification Agreement
- Confusion matrix: v2 predicted class vs. v3 predicted class
- Confusion matrix: v3 predicted class vs. v3 actual class
- Report: classification accuracy, precision, recall per class

#### C7. Extreme Value Analysis
- Subset test records where FRI > 80 (if any)
- Report MAE and RMSE on this subset separately
- Note: small sample sizes expected; interpret with caution

### Phase D: Sensitivity Analysis

#### D1. Weight Sweep
- Systematically vary weights around the equal-weight configuration
- Evaluate distribution metrics for each variation
- Candidates to test:
  - RR=20%, Rain7=30%, RH_avg=25%, Tavg=25%
  - RR=30%, Rain7=20%, RH_avg=25%, Tavg=25%
  - RR=25%, Rain7=30%, RH_avg=25%, Tavg=20%
  - RR=25%, Rain7=20%, RH_avg=30%, Tavg=25%

#### D2. Stability Analysis
- Bootstrap resampling (1000 iterations) of the FRI computation
- Compute 95% confidence intervals for mean, median, and skewness for both v2 and v3

---

## Acceptance Criteria

The FRI v3 configuration is considered acceptable for production deployment if:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| MAE non-inferiority | MAE_v3 ≤ 1.10 × MAE_v2 | Prevents significant accuracy loss |
| R² non-inferiority | R²_v3 ≥ R²_v2 − 0.05 | Prevents significant variance loss |
| Prediction diversity improvement | σ(pred_v3) > σ(pred_v2) | Confirms regression-to-the-mean reduction |
| No critical distribution collapse | FRI_v3 range ≥ 0.80 × FRI_v2 range | Prevents target compression |
| Visual inspection | No implausible seasonal patterns | Expert review required |

---

## Deliverables

| Deliverable | Format | Content |
|-------------|--------|---------|
| Experiment Report | Markdown | Full results with tables and figures |
| Distribution Comparison | PNG | Histogram, boxplot, CDF overlay |
| Residual Plots | PNG | Residual scatter, histogram, Q-Q |
| Feature Importance | PNG | Bar chart comparing v2 vs. v3 |
| Prediction Scatter | PNG | Actual vs. predicted for both versions |
| Metrics Table | CSV | All numerical results |
| Dataset_v3 | CSV | 726 records with FRI_v3 target |
| RandomForest_v3 | PKL | Trained model artifact (not for sprint) |
| Model Metadata | JSON | Training configuration and checksum |

---

## Validation Rules

1. All experiments must use the same 80/20 chronological split.
2. The test set must not be used for any training decisions.
3. Random Forest hyperparameters must be identical between v2 and v3 training.
4. All random seeds must be fixed and documented.
5. Any data transformation must be identically applied to both versions.
6. Results must be independently reproducible.
