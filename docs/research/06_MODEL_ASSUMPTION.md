# Model Assumptions

## Objective

Explicitly document what the Flood Risk Index (FRI) model predicts, what it does not predict, its research scope, limitations, and directions for future work. This document supports transparency and reproducibility as required for academic documentation (Chapter III/IV).

---

## What the Model Predicts

1. **Daily flood risk level** for horticultural areas in Pekanbaru, expressed as a continuous index (0–100) and categorical classification (Low/Medium/High).

2. **Relative risk ranking** between days—identifying which days have higher or lower meteorological flood indicators compared to the local climatological baseline.

3. **Dominant risk contributors** for each day, decomposed from the FRI formula to identify whether rainfall intensity, accumulated precipitation, humidity, or temperature anomaly is the primary driver.

4. **Commodity suitability recommendations** based on the current risk level and crop-specific flood tolerance characteristics.

---

## What the Model Does NOT Predict

1. **Actual flood occurrence**: The FRI quantifies meteorological conditions associated with flood risk. It does not model whether flooding will actually occur at a specific location.

2. **Flood depth, extent, or duration**: No hydrological or hydraulic modeling is performed.

3. **River discharge or overflow**: The model has no river level, flow rate, or catchment hydrology inputs.

4. **Spatial distribution**: The FRI produces a single value for the area represented by the BMKG station, not a spatial map.

5. **Economic loss or crop damage**: The model does not quantify agricultural damage in monetary or yield terms.

6. **Long-term climate trends**: The model operates on daily timescales; it does not predict seasonal or climate-change-driven flood trends.

7. **Flash flood timing**: Sub-daily temporal resolution is not available from BMKG daily observations.

---

## Research Scope

### Geographic Scope
- **Area**: Pekanbaru, Riau Province, Indonesia
- **Station**: BMKG Stasiun Meteorologi Sultan Syarif Kasim II (WMO ID: 96109)
- **Coordinates**: 0.459°N, 101.447°E, elevation 39m

### Temporal Scope
- **Period**: July 2024 – June 2026 (~2 years of daily observations)
- **Resolution**: Daily

### Thematic Scope
- **Domain**: Agricultural meteorology for horticultural flood risk
- **Target users**: Farmers, agricultural extension officers, local planning agencies
- **Application**: Retrospective risk analysis and commodity planning support

### Methodological Scope
- **Approach**: Index-based (deterministic scoring + weighted aggregation)
- **Data source**: Single meteorological station (BMKG)
- **Validation approach**: Internal consistency checks; external validation against flood events pending

---

## Core Assumptions

### A1: Single-Station Representativeness
The meteorological observations from one BMKG station adequately represent conditions across the broader Pekanbaru horticultural area.

**Implication**: Microclimatic variations, urban heat effects, and local orographic rainfall are not captured.

### A2: Meteorological Sufficiency
Flood risk can be meaningfully estimated from atmospheric variables (rainfall, humidity, temperature) without hydrological state variables (soil moisture, groundwater level, river stage).

**Implication**: The model may underestimate risk when catchment is pre-saturated from upstream rainfall not captured by the local station, or overestimate risk when efficient drainage infrastructure mitigates meteorological conditions.

### A3: Linear Aggregation
A weighted linear combination of individual risk scores adequately represents the combined flood risk, without requiring nonlinear interaction terms.

**Implication**: Synergistic effects (e.g., high rainfall × high antecedent moisture being disproportionately worse than either alone) are not explicitly modeled.

### A4: Stationarity
The statistical properties of Pekanbaru's climate (percentile distributions) remain stable within the observation period and into the near-term future.

**Implication**: If climate shifts significantly (due to El Niño/La Niña, urbanization, or climate change), percentile thresholds may need recalibration.

### A5: Percentile Robustness
Percentiles computed from ~2 years of data reasonably approximate the true climatological distribution for threshold-setting purposes.

**Implication**: Extreme values (P99, P1) may not be reliably estimated from this sample size. Multi-decade records would be preferable.

### A6: BMKG Data Quality
BMKG observations, after sentinel value removal, represent reliable measurements of actual atmospheric conditions.

**Implication**: Instrument errors, station relocations, or observer biases are not accounted for beyond the sentinel value system.

### A7: Flood Tolerance Classification
Horticultural commodities can be meaningfully classified into discrete flood tolerance categories that remain stable across reasonable environmental variation.

**Implication**: Actual crop response depends on growth stage, cultivar, soil type, and management practices not captured in the model.

---

## Limitations

### Data Limitations
1. **Short record length**: ~2 years insufficient for robust extreme value analysis or return period estimation.
2. **Missing data**: Sentinel values (8888/9999) converted to NaN reduce effective sample size for affected periods.
3. **Single source**: No cross-validation with neighboring stations or satellite precipitation products.
4. **No flood ground truth**: Absence of verified flood event records prevents empirical calibration of the index.

### Methodological Limitations
1. **No physical model**: FRI is statistical/empirical, not physically based. It does not simulate water balance or hydraulic processes.
2. **No spatial dimension**: Point-based assessment only.
3. **No uncertainty quantification**: The FRI produces deterministic values without confidence intervals or probabilistic output.
4. **Equal-interval classification**: The Low/Medium/High tercile split is geometrically convenient but not validated against impact thresholds.
5. **Weight subjectivity**: Until validated against flood events, weight allocation contains subjective judgment.

### Scope Limitations
1. **Not a warning system**: The FRI is a retrospective analytical tool, not an operational real-time flood early warning system.
2. **Not generalizable without recalibration**: Percentile thresholds are location-specific; applying to other regions requires recomputation.
3. **No economic model**: Does not translate risk into financial terms.

---

## Future Work

### Short-Term (Within Thesis Scope)
1. Complete literature review for weight determination.
2. Perform EDA to extract percentile thresholds from cleaned dataset.
3. Implement FRI computation and validate distribution properties.
4. Cross-reference FRI peaks with reported flood/waterlogging events (if records obtainable from BPBD Pekanbaru).

### Medium-Term (Post-Thesis Extensions)
1. Incorporate satellite precipitation data (GPM/CHIRPS) for spatial coverage.
2. Add soil moisture data (SMAP, ERA5-Land) for improved antecedent condition modeling.
3. Integrate river level data from BBWS for hydrological validation.
4. Develop nonlinear scoring using machine learning (replacing piecewise linear functions).
5. Extend temporal record using BMKG historical data (pre-2024).

### Long-Term (Research Direction)
1. Multi-station network for spatial flood risk mapping.
2. Real-time operational deployment with automated BMKG data ingestion.
3. Ensemble approach combining meteorological FRI with hydrological models.
4. Economic loss modeling coupled with FRI for insurance/planning applications.
5. Climate change scenario analysis using CMIP6 projections.

---

## Relationship to Thesis Structure

| Document Section | Thesis Chapter | Purpose |
|-----------------|----------------|---------|
| Research Scope | Chapter I (Introduction) | Problem definition, objectives |
| Assumptions | Chapter III (Methodology) | Methodological framework justification |
| Limitations | Chapter III / Chapter V | Scope boundaries, discussion |
| What Model Predicts/Does Not | Chapter IV (Results) | Interpretation guidelines |
| Future Work | Chapter V (Conclusion) | Recommendations |
