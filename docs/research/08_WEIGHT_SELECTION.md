# Weight Selection Methodology

## Objective

This document describes the methodology that will be used to determine the weights for the Flood Risk Index (FRI) weighted aggregation layer. No numerical weights are assigned at this stage. All weights remain TBD until the completion of the literature review and Exploratory Data Analysis (EDA).

---

## Current Status

| Variable | Weight | Status |
|----------|--------|--------|
| RR | TBD | Pending literature review + EDA |
| Rain3 | TBD | Pending literature review + EDA |
| Rain7 | TBD | Pending literature review + EDA |
| Rain14 | TBD | Pending literature review + EDA |
| RH_avg | TBD | Pending literature review + EDA |
| TempRange | TBD | Pending literature review + EDA |

---

## Methodological Framework

Weight determination will follow a structured three-phase approach, combining theoretical justification with empirical evidence.

### Phase 1: Literature-Informed Initial Ranking

**Objective**: Establish the relative ordering of variable importance based on hydrological and meteorological literature.

**Method**:
1. Review published studies on tropical flood drivers to identify consensus on relative importance of precipitation intensity, antecedent moisture, humidity, and temperature signals.
2. Examine existing flood indices and composite risk scores for weight allocation precedents.
3. Identify the dominant driver hierarchy (expected: direct rainfall > accumulated rainfall > atmospheric moisture indicators).

**Expected Output**: A qualitative ranking of variables by contribution magnitude (e.g., "rainfall variables collectively dominate; humidity and temperature are secondary contributors").

**Constraint**: Rainfall-related variables (RR + Rain3 + Rain7 + Rain14) shall collectively receive the dominant share of total weight (≥ 60%), reflecting the established primacy of precipitation in tropical flood causation.

---

### Phase 2: Exploratory Data Analysis (EDA)

**Objective**: Use empirical analysis of the Pekanbaru dataset to inform weight proportions within the literature-established ranking.

**Methods**:

#### 2.1 Correlation Analysis
- Compute pairwise correlations between individual variable scores and composite indicators of extreme conditions.
- Assess collinearity between rainfall accumulation windows (Rain3, Rain7, Rain14) to determine how to distribute weight among correlated variables.

#### 2.2 Variance Contribution
- Analyse the variance of each scored variable to understand its discriminatory power.
- Variables with higher variance in their scores contribute more information to the composite index.

#### 2.3 Temporal Co-occurrence
- Examine how frequently high scores in different variables co-occur versus occur independently.
- Variables that independently signal risk (low redundancy) may warrant higher weight.

#### 2.4 Sensitivity Analysis
- Systematically vary weight configurations within feasible ranges.
- Evaluate resulting FRI distributions for:
  - Reasonable discrimination between high-risk and low-risk periods
  - Plausible seasonal patterns
  - Absence of floor/ceiling effects (avoiding compressed distributions)

**Expected Output**: Quantitative evidence supporting specific weight ranges for each variable.

---

### Phase 3: Integration and Validation

**Objective**: Synthesize literature ranking with EDA evidence to assign final weights.

**Method**:
1. Propose candidate weight sets consistent with both literature hierarchy and EDA findings.
2. Apply each candidate to the full dataset and evaluate:
   - Distribution properties (mean, spread, skewness)
   - Temporal patterns (does FRI track known wet/dry seasons?)
   - Extreme event identification (do FRI peaks align with intense rainfall events?)
3. Select the weight set that produces the most physically interpretable and well-distributed FRI.

**Validation Criteria**:
- FRI should not be dominated by a single variable (no w_i > 0.35)
- FRI should show seasonal variation consistent with Pekanbaru's climate
- High FRI days should correspond to days with objectively severe meteorological conditions
- The distribution should utilise a reasonable range of the 0–100 scale

---

## Design Constraints

The following constraints are imposed on any weight configuration:

| Constraint | Rationale |
|-----------|-----------|
| Σ w_i = 1.0 | Ensures FRI remains on the 0–100 scale |
| w_i > 0 ∀ i | All selected variables must contribute positively |
| w_RR + w_Rain3 + w_Rain7 + w_Rain14 ≥ 0.60 | Precipitation dominance in tropical flooding |
| No single w_i > 0.35 | Prevents single-variable dominance |
| w_RH_avg + w_TempRange ≤ 0.25 | Secondary indicators should not overwhelm primary drivers |

---

## Why Weights Are Not Yet Assigned

1. **Scientific integrity**: Assigning weights without completing the literature review would be methodologically unsound and constitute arbitrary parameter selection.

2. **Empirical grounding**: Without EDA results, it is impossible to assess collinearity between rainfall windows or the discriminatory power of each variable in the Pekanbaru context.

3. **Reproducibility**: The weight selection methodology must be documented before values are assigned, allowing reviewers to assess whether the process was rigorous.

4. **Academic standard**: For thesis purposes (Chapter III), the methodology must be established independently of its results—avoiding the appearance of post-hoc rationalisation.

---

## Timeline

| Phase | Dependency | Sprint |
|-------|-----------|--------|
| Phase 1: Literature Review | Independent | Sprint 3 (concurrent with feature engineering) |
| Phase 2: EDA | Requires Sprint 3 output (engineered features) | Sprint 3.5 |
| Phase 3: Integration | Requires Phase 1 + Phase 2 completion | Sprint 4 (FRI generation) |

---

## Alternative Approaches Considered

| Approach | Decision | Rationale |
|----------|----------|-----------|
| Equal weights | Rejected | Ignores established dominance of precipitation; physically unrealistic |
| AHP (Analytic Hierarchy Process) | Deferred | Requires expert panel; may be explored if literature is insufficient |
| PCA-derived weights | Deferred | Data-driven but lacks physical interpretability; may be used for validation |
| Machine learning optimisation | Rejected for FRI | Sacrifices transparency; may be used in separate ML model |

---

## Relationship to Thesis

This methodology supports Chapter III (Research Methodology) by:
1. Demonstrating a systematic, transparent approach to parameter selection
2. Establishing criteria before results are known (avoiding confirmation bias)
3. Providing a clear audit trail from literature → data → weight assignment
4. Acknowledging the preliminary nature of choices made with limited data
