# Research Gap Analysis

## Objective

This document identifies the research gap addressed by the proposed Flood Risk Index-based Decision Support System (FRI-DSS). It compares existing flood prediction approaches with the proposed system to establish the novelty and contribution of this research.

---

## Existing Approaches to Flood Prediction

### Category 1: Hydrological Modeling

**Approach**: Physics-based simulation of rainfall-runoff processes, river routing, and inundation dynamics.

**Examples**: HEC-HMS, SWAT, MIKE-FLOOD, HEC-RAS

**Characteristics**:
- Requires extensive input data (DEM, soil maps, land use, river geometry, discharge measurements)
- Computationally intensive
- High spatial and temporal resolution possible
- Validated against observed discharge/water level records
- Requires hydrological expertise for setup and calibration

**Gap relative to this research**: Hydrological models are powerful but data-intensive and expert-dependent. They are not accessible to agricultural extension officers or local farmers, and are unavailable in regions lacking discharge gauging stations—including most of Pekanbaru's horticultural areas.

---

### Category 2: Machine Learning Flood Prediction

**Approach**: Data-driven models (Random Forest, SVM, Neural Networks, LSTM) trained on historical flood event data to predict flood occurrence or severity.

**Examples**: Various published studies using ML for flood susceptibility mapping and event prediction.

**Characteristics**:
- Requires labelled flood event data for training
- High predictive accuracy when training data is sufficient
- Black-box nature limits interpretability
- Cannot explain why a prediction is made
- Requires retraining when conditions change
- Performance degrades without ground truth validation data

**Gap relative to this research**: ML approaches require flood event labels (ground truth) that are unavailable for Pekanbaru's agricultural areas. Furthermore, ML models cannot provide the transparent, decomposable reasoning needed for agricultural decision support—a farmer needs to understand *why* risk is high, not just *that* it is high.

---

### Category 3: Remote Sensing-Based Flood Mapping

**Approach**: Satellite imagery (SAR, optical) used to detect inundated areas during or after flood events.

**Examples**: Sentinel-1 SAR flood mapping, MODIS near-real-time flood detection.

**Characteristics**:
- Spatial coverage is excellent
- Detects actual inundation (post-event or near-real-time)
- Cannot predict future flooding
- Cloud cover limits optical sensors in tropical regions
- Resolution may not match agricultural plot scale
- Retrospective (after flooding has occurred)

**Gap relative to this research**: Remote sensing maps floods that have already occurred. It does not provide *prospective* risk assessment for agricultural planning. Farmers need advance indication of risk conditions, not confirmation that flooding happened.

---

### Category 4: Composite Flood Risk Indices

**Approach**: Multi-variable indices combining environmental factors into a single risk score.

**Examples**: Various flood vulnerability indices, disaster risk indices (INFORM, WRI)

**Characteristics**:
- Integrates multiple data sources into interpretable output
- Typically applied at regional/national scale for policy
- Often uses static factors (elevation, proximity to rivers, land use)
- Rarely incorporates dynamic meteorological variables at daily timescale
- Weight assignment often subjective or expert-based

**Gap relative to this research**: Existing composite indices are predominantly static (long-term vulnerability assessment) rather than dynamic (daily operational risk). They operate at policy scale, not agricultural decision scale. The proposed FRI is unique in applying dynamic meteorological scoring at daily resolution for agricultural commodity planning.

---

## Identified Research Gaps

### Gap 1: No Dynamic Daily Flood Risk Index for Agricultural Decision Support

Existing flood risk tools are either:
- **Predictive but opaque** (ML models without interpretability)
- **Interpretable but static** (vulnerability indices with fixed factors)
- **Dynamic but inaccessible** (hydrological models requiring extensive infrastructure)

**No existing system** provides a transparent, daily-updated, meteorology-based flood risk assessment specifically designed for agricultural commodity recommendation in tropical lowland environments.

### Gap 2: No FRI-to-Commodity Decision Pipeline

Published flood research focuses on predicting flood occurrence or mapping flood extent. The translation of flood risk levels into specific horticultural commodity recommendations represents an unexplored decision support layer.

Agricultural extension services lack a quantitative, systematic framework for advising farmers on crop selection based on current meteorological flood risk conditions.

### Gap 3: No BMKG-Based Flood Risk Scoring for Pekanbaru Horticulture

Despite BMKG providing comprehensive daily climate data for Pekanbaru, no published study has:
1. Developed a flood risk scoring system using BMKG data for this location
2. Applied percentile-based thresholds from local climate observations
3. Connected meteorological indicators to horticultural decision-making in Riau Province

### Gap 4: Lack of Transparent, Decomposable Risk Communication

Existing tools produce either:
- A single opaque prediction (flood: yes/no)
- A complex model output requiring expert interpretation

Neither approach supports the communication needs of agricultural stakeholders who require:
- Understanding of *which factors* drive the current risk level
- Actionable guidance tied to specific risk contributors
- Confidence assessment based on data availability

---

## Novelty of This Research

### Primary Contribution

Development of a **meteorology-based Flood Risk Index (FRI)** with the following novel characteristics:

| Aspect | Novelty |
|--------|---------|
| **Domain** | Flood risk assessment specifically for horticultural commodity planning |
| **Temporal resolution** | Daily operational risk (not static vulnerability) |
| **Data source** | Exclusively BMKG public observations (no special instrumentation required) |
| **Threshold methodology** | Hybrid approach: official standards (BMKG) where available, empirical percentiles where not |
| **Transparency** | Fully decomposable—each day's FRI can be traced to individual variable contributions |
| **Decision integration** | Explicit pipeline from meteorological risk → commodity suitability → mitigation advice |
| **Geographic specificity** | Calibrated to Pekanbaru's equatorial lowland climate using local percentile distributions |
| **Accessibility** | Designed for non-expert users (farmers, extension officers) without hydrological expertise |

### Secondary Contributions

1. **Methodological framework** for constructing location-specific meteorological flood risk indices that can be replicated for other Indonesian stations.
2. **Threshold justification protocol** demonstrating transparent threshold selection combining official standards with dataset-derived percentiles.
3. **Weight selection methodology** establishing a rigorous, pre-registered approach to parameter determination.

---

## Positioning Within Literature

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Flood Risk Assessment Landscape                    │
├──────────────────┬──────────────────┬───────────────────────────────┤
│   Hydrological   │  Machine Learning │  Composite Indices            │
│   Models         │  Prediction       │                               │
│                  │                   │                               │
│  • Physics-based │  • Black-box      │  • Static vulnerability       │
│  • Data-heavy    │  • Requires labels│  • Policy scale               │
│  • Expert-only   │  • Not decomposable│  • Not agricultural          │
├──────────────────┴──────────────────┴───────────────────────────────┤
│                                                                       │
│   ★ THIS RESEARCH: FRI-Based Decision Support System                 │
│                                                                       │
│   • Transparent & decomposable                                        │
│   • Daily dynamic resolution                                          │
│   • BMKG data only (accessible)                                       │
│   • Agricultural commodity output                                     │
│   • Locally calibrated (Pekanbaru percentiles)                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Research Questions Addressed

| # | Research Question | How FRI-DSS Addresses It |
|---|-----------------|--------------------------|
| 1 | How can publicly available meteorological data be transformed into an operational flood risk indicator for agriculture? | FRI scoring layer converts BMKG observations into 0–100 risk scores using justified thresholds |
| 2 | What methodology produces transparent, locally-relevant flood risk thresholds without requiring historical flood event data? | Hybrid BMKG-standard + empirical-percentile approach documented in 07_THRESHOLD_JUSTIFICATION.md |
| 3 | How can flood risk information be translated into actionable horticultural recommendations? | Decision logic pipeline (05_DECISION_LOGIC.md) connecting FRI levels to commodity suitability |

---

## Relationship to Thesis

This gap analysis directly supports:
- **Chapter I**: Problem statement and research justification (why this research is needed)
- **Chapter II**: Literature review positioning (how this work relates to existing studies)
- **Chapter III**: Methodological novelty claims (what distinguishes this approach)
- **Chapter V**: Contribution statement (what the research adds to knowledge)
