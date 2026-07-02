# Flood Risk Index (FRI) – Technical Specification

## Version
1.2 (Sprint 2.6 – Scientific Validation)

## Objective

Develop a meteorology-based Flood Risk Index (FRI) for short-term agricultural flood risk assessment in horticultural areas of Pekanbaru, Riau Province, Indonesia.

The FRI quantifies daily flood risk on a 0–100 continuous scale using only publicly available BMKG climate observations. It is designed to serve as the analytical core of a Decision Support System (DSS) for horticultural commodity recommendation and flood mitigation planning.

---

## Layered Architecture

```
Layer 1: Raw Features (BMKG Observations)
    ↓
Layer 2: Feature Engineering (Derived Variables)
    ↓
Layer 3: Scientific Scoring (0–100 per variable)
    ↓
Layer 4: Weighted Aggregation
    ↓
Layer 5: Flood Risk Index (0–100)
    ↓
Layer 6: Risk Classification (Low / Medium / High)
```

Each layer is independently documented, testable, and modifiable. The architecture ensures full traceability from raw observation to final recommendation.

---

## Layer 1: Raw Features

**Source**: BMKG Stasiun Meteorologi Sultan Syarif Kasim II, Pekanbaru (WMO ID: 96109, coordinates 0.459°N, 101.447°E, elevation 39m).

| Variable | Unit | Description | Role |
|----------|------|-------------|------|
| RR | mm | Daily rainfall | Direct flood trigger |
| RH_AVG | % | Daily average relative humidity | Atmospheric moisture indicator |
| TN | °C | Daily minimum temperature | Component of TempRange |
| TX | °C | Daily maximum temperature | Component of TempRange |

**Data quality**: BMKG sentinel values (8888 = unmeasured, 9999 = no observation) are converted to NaN during the cleaning pipeline. No imputation is performed; missing values propagate to scoring with appropriate handling (see Layer 4).

---

## Layer 2: Feature Engineering

| Derived Variable | Formula | Purpose | FRI Role |
|-----------------|---------|---------|----------|
| Rain3 | Σ RR (t, t-1, t-2) | Short-term rainfall accumulation | Scored in FRI |
| Rain7 | Σ RR (t to t-6) | Medium-term rainfall accumulation | Scored in FRI |
| Rain14 | Σ RR (t to t-13) | Antecedent precipitation index | Scored in FRI |
| TempRange | TX - TN | Diurnal temperature range (storm proxy) | Scored in FRI |
| Month | month(tanggal) | Calendar month | **ML feature only – excluded from FRI** |

### Month Exclusion Rationale

Month is explicitly excluded from the FRI formula for three methodological reasons:

1. **Not a physical driver**: Month is a temporal index with no causal relationship to flooding. Including it would conflate correlation (wet season timing) with causation.
2. **Redundancy**: Seasonal rainfall patterns are already captured by the dynamic rainfall variables (RR, Rain3, Rain7, Rain14) which directly measure the physical conditions that cause flooding.
3. **Circular reasoning**: Including month would bias the FRI toward high values during wet-season dates regardless of actual meteorological observations, degrading discriminatory power for anomalous events (dry-season floods, dry spells during wet season).

Month is retained exclusively as a feature for machine learning classification models that may learn seasonal patterns independently of the deterministic FRI.

---

## Layer 3: Scientific Scoring

Each FRI input variable is transformed into a standardized risk score S_i ∈ [0, 100] using threshold functions appropriate to the variable's nature and data availability.

### Threshold Strategy

| Variable | Threshold Source | Method | Justification |
|----------|-----------------|--------|---------------|
| RR | BMKG rainfall intensity classification | Official categorical thresholds with linear interpolation | Nationally authoritative standard (see 07_THRESHOLD_JUSTIFICATION.md) |
| Rain3 | Pekanbaru dataset | Percentile-based (empirical CDF) | No official standard; local calibration required (see 07_THRESHOLD_JUSTIFICATION.md) |
| Rain7 | Pekanbaru dataset | Percentile-based (empirical CDF) | No official standard; local calibration required |
| Rain14 | Pekanbaru dataset | Percentile-based (empirical CDF) | No official standard; local calibration required |
| RH_avg | Pekanbaru dataset | Percentile-based (empirical CDF) | No official standard; indirect relationship |
| TempRange | Pekanbaru dataset | Percentile-based (inverse) | No official standard; inverse relationship |

### RR Scoring – BMKG Rainfall Intensity Categories

The daily rainfall score applies the official BMKG classification system with piecewise linear interpolation:

| BMKG Category | Rainfall (mm/day) | Risk Score |
|---------------|-------------------|------------|
| Tidak hujan | 0 | 0 |
| Hujan ringan | >0 – 5 | 0 – 20 |
| Hujan sedang | >5 – 20 | 20 – 40 |
| Hujan lebat | >20 – 50 | 40 – 70 |
| Hujan sangat lebat | >50 – 100 | 70 – 90 |
| Hujan ekstrem | >100 | 90 – 100 |

**Source authority**: BMKG is the Indonesian national meteorological agency. These categories are used operationally in weather warnings and by BNPB for disaster risk assessment.

### Percentile-Based Scoring (Rain3, Rain7, Rain14, RH_avg)

For variables without official threshold standards, scoring maps observed values to their position within the empirical cumulative distribution of the Pekanbaru cleaned dataset:

| Percentile Range | Risk Interpretation | Score Range |
|-----------------|-------------------|-------------|
| ≤ P25 | Below-normal; low risk | 0 – 25 |
| P25 – P50 | Normal; baseline risk | 25 – 50 |
| P50 – P75 | Above-normal; elevated risk | 50 – 75 |
| ≥ P75 | High; significant risk | 75 – 100 |

Percentile anchors (P25, P50, P75) are computed from all valid observations in `data/interim/bmkg_clean.csv` during the EDA phase.

**Why percentiles**: See 07_THRESHOLD_JUSTIFICATION.md for complete rationale including absence of standards, local relevance, statistical robustness, and precedent in hydrometeorology.

### TempRange Scoring (Inverse Percentile)

TempRange uses inverse scoring because lower diurnal temperature range indicates overcast/storm conditions associated with higher flood risk:

| TempRange Percentile | Condition | Score Range |
|---------------------|-----------|-------------|
| ≥ P75 | Large range; clear skies | 0 – 25 |
| P50 – P75 | Normal range | 25 – 50 |
| P25 – P50 | Below-normal range | 50 – 75 |
| ≤ P25 | Compressed range; overcast/storm | 75 – 100 |

---

## Layer 4: Weighted Aggregation

### Formula

```
FRI = Σ (w_i × S_i)    for i ∈ {RR, Rain3, Rain7, Rain14, RH_avg, TempRange}
```

Where:
- S_i = scientific score for variable i (0–100)
- w_i = weight for variable i
- Σ w_i = 1.0

### Weight Status

All weights are **TBD** pending completion of literature review and Exploratory Data Analysis.

| Variable | Weight | Status |
|----------|--------|--------|
| RR | TBD | Pending Phase 1–3 (see 08_WEIGHT_SELECTION.md) |
| Rain3 | TBD | Pending Phase 1–3 |
| Rain7 | TBD | Pending Phase 1–3 |
| Rain14 | TBD | Pending Phase 1–3 |
| RH_avg | TBD | Pending Phase 1–3 |
| TempRange | TBD | Pending Phase 1–3 |

### Weight Determination Methodology

Weights will be assigned through a structured three-phase process:
1. **Literature-informed ranking** – Establish relative importance from hydrometeorological literature
2. **EDA-based refinement** – Use correlation, variance, and sensitivity analysis on the Pekanbaru dataset
3. **Integration and validation** – Select the configuration producing the most physically interpretable FRI distribution

Full methodology documented in 08_WEIGHT_SELECTION.md.

### Design Constraints

| Constraint | Specification | Rationale |
|-----------|---------------|-----------|
| Sum to unity | Σ w_i = 1.0 | Maintains 0–100 scale |
| All positive | w_i > 0 ∀ i | All variables contribute positively |
| Rainfall dominance | w_RR + w_Rain3 + w_Rain7 + w_Rain14 ≥ 0.60 | Precipitation is the established dominant tropical flood driver |
| No single dominance | No w_i > 0.35 | Prevents single-variable control of the index |
| Secondary cap | w_RH_avg + w_TempRange ≤ 0.25 | Indirect indicators should not overwhelm primary drivers |

### Missing Value Handling

When one or more input scores are unavailable (NaN due to missing observations):

```
FRI = Σ (w_i × S_i) / Σ w_i    for all i where S_i is not NaN
```

A `confidence` metric accompanies each FRI value:
```
confidence = Σ w_i (available) / Σ w_i (all)
```

Records with confidence below 0.5 are flagged as unreliable.

---

## Layer 5: Flood Risk Index

**Output**: A continuous value FRI ∈ [0, 100].

**Properties**:
- FRI = 0: No flood risk indicators active
- FRI = 100: All indicators at maximum risk
- Monotonically increasing with respect to each component score
- Fully decomposable: individual contributions (w_i × S_i) can be reported

---

## Layer 6: Risk Classification

| FRI Range | Category | Agricultural Interpretation |
|-----------|----------|---------------------------|
| 0–33 | **Low** | Normal agricultural operations; full commodity range available |
| 34–66 | **Medium** | Elevated risk; precautionary measures advised; moderate-tolerance crops preferred |
| 67–100 | **High** | Significant flood risk; protective action required; flood-tolerant crops only |

**Note**: The tercile-based classification (33/66) is preliminary. These thresholds are subject to validation against observed flood events if ground-truth data becomes available. See 05_DECISION_LOGIC.md for the downstream decision architecture.

---

## Assumptions

| # | Assumption | Implication |
|---|-----------|-------------|
| A1 | **Single-station representativeness**: Observations from BMKG Sultan Syarif Kasim II represent conditions across Pekanbaru's horticultural areas. | Microclimatic variation and localised rainfall not captured. |
| A2 | **Meteorological sufficiency**: Flood risk can be meaningfully estimated from atmospheric variables alone, without hydrological state variables (soil moisture, river stage, groundwater level). | May underestimate risk from upstream contributions; may overestimate when drainage infrastructure is effective. |
| A3 | **Stationarity**: Climate statistical properties remain stable within the observation period (2024–2026). | Index requires recalibration if climate regime shifts significantly. |
| A4 | **Linear aggregation**: Weighted linear combination adequately represents combined flood risk without requiring nonlinear interaction terms. | Synergistic effects (e.g., high rainfall × saturated soil) not explicitly modeled. |
| A5 | **Percentile stability**: Percentiles from ~2 years of data reasonably approximate climatological norms for threshold-setting purposes. | Extreme percentiles (P95+) less reliable; multi-decade records preferred. |
| A6 | **BMKG data quality**: After sentinel removal, observations represent reliable measurements of actual atmospheric conditions. | Instrument errors or observer biases not accounted for. |

Full assumption documentation: 06_MODEL_ASSUMPTION.md.

---

## Limitations

1. **No hydrological model**: Does not simulate runoff, infiltration, or river discharge.
2. **No spatial resolution**: Single-point observation; no spatial interpolation or mapping.
3. **Limited temporal coverage**: ~2 years insufficient for extreme value analysis or return period estimation.
4. **No flood event validation**: Cannot be empirically calibrated against actual flooding without ground-truth records.
5. **Sentinel data gaps**: NaN periods reduce effective sample size and scoring continuity.
6. **No real-time capability**: Retrospective analytical tool, not an operational early warning system.
7. **Weight subjectivity**: Until validated against flood events, weight allocation retains elements of informed judgment.

---

## Design Principles

1. **Transparency**: Every threshold is sourced from an official standard (BMKG) or derived systematically from data with documented methodology.
2. **Reproducibility**: No arbitrary constants; all values computable from data or literature with defined procedures.
3. **Modularity**: Each layer is independently testable, modifiable, and documentable.
4. **Conservative approach**: Weights remain TBD until supported by converging evidence from literature and data analysis.
5. **Academic rigour**: Methodology established before results; no post-hoc rationalisation.

---

## Cross-References

| Document | Content |
|----------|---------|
| 02_LITERATURE_MAPPING.md | Evidence base for each variable |
| 03_FEATURE_JUSTIFICATION.md | Physical mechanism justification per feature |
| 04_FRI_FORMULA.md | Mathematical formulation details |
| 05_DECISION_LOGIC.md | Downstream decision architecture (FRI → commodity → mitigation) |
| 06_MODEL_ASSUMPTION.md | Complete assumptions, scope, and limitations |
| 07_THRESHOLD_JUSTIFICATION.md | Threshold selection methodology and rationale |
| 08_WEIGHT_SELECTION.md | Weight determination methodology (TBD values) |
| 09_RESEARCH_GAP.md | Positioning against existing approaches; novelty |
