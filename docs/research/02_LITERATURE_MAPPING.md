# Literature Mapping

## Objective

This document provides a systematic mapping between each variable in the Flood Risk Index (FRI) and its scientific foundation. The mapping serves as a traceability matrix connecting methodological choices to their evidence base, supporting the research methodology (Chapter III) and discussion (Chapter IV).

---

## Literature Mapping Table

| Feature | Scientific Rationale | Threshold Source | Evidence Level | Citation Status |
|---------|---------------------|-----------------|----------------|-----------------|
| RR (Daily Rainfall) | Rainfall intensity is the primary determinant of surface runoff generation in tropical lowland environments. When precipitation rate exceeds infiltration capacity, ponding and subsequent flooding occur. | BMKG Official Classification – Categorization of rainfall intensity into six levels (tidak hujan, ringan, sedang, lebat, sangat lebat, ekstrem) with defined mm/day boundaries. | **Strong** – Government meteorological standard applied nationally; operationally validated across Indonesian stations. | BMKG operational standard; publicly documented in BMKG technical guidelines. |
| Rain3 (3-day cumulative rainfall) | Consecutive-day rainfall saturates the soil profile, reducing infiltration capacity progressively. Short-term accumulation captures antecedent moisture effects not visible in single-day observations. | Empirical percentile distribution computed from Pekanbaru station data (2024–2026). No official multi-day accumulation standard exists for Indonesia. | **Moderate** – Physical mechanism well-established in hydrology literature; specific percentile thresholds are dataset-dependent. | Pending – Antecedent Precipitation Index (API) literature review required. |
| Rain7 (7-day cumulative rainfall) | Sustained weekly precipitation raises the water table in shallow lowland aquifers, reducing or eliminating available soil storage. Seven days represents the timescale of synoptic weather system influence. | Empirical percentile distribution computed from Pekanbaru station data. | **Moderate** – Consistent with API methodology used in flood forecasting; threshold values require local calibration. | Pending – Southeast Asian flood forecasting studies using 7-day accumulation. |
| Rain14 (14-day cumulative rainfall) | Extended wet periods fundamentally alter catchment hydrological state. After two weeks of elevated precipitation, soil storage is exhausted and drainage infrastructure operates at capacity, making the system vulnerable to even moderate additional rainfall. | Empirical percentile distribution computed from Pekanbaru station data. | **Moderate** – Aligns with extended API windows used in monsoon flood analysis; local validation pending. | Pending – Monsoon flood studies in Maritime Continent region. |
| RH_avg (Average Relative Humidity) | High atmospheric humidity suppresses evapotranspiration, prolonging surface water persistence. Additionally, sustained high humidity correlates with continued cloud cover and precipitation probability. | Empirical percentile distribution computed from Pekanbaru station data. No standardized humidity threshold for flood risk exists. | **Moderate-Low** – Indirect relationship; humidity is a contributing factor rather than a direct flood driver. Physical mechanism established but contribution magnitude uncertain. | Pending – Evapotranspiration-waterlogging relationship studies in tropical agriculture. |
| TempRange (Diurnal Temperature Range) | Compressed diurnal temperature range indicates persistent cloud cover associated with active precipitation systems. Low DTR serves as a meteorological proxy for storm conditions. Inverse relationship: lower DTR corresponds to higher flood risk. | Empirical percentile distribution (inverse scoring) computed from Pekanbaru station data. | **Moderate-Low** – DTR-cloud cover relationship documented in climate science; use as flood proxy is indirect and novel. | Pending – DTR as weather/climate signal in tropical regions. |
| Month (Calendar Month) | Encodes seasonal precipitation climatology (ITCZ migration, monsoon phasing). Pekanbaru wet season (Oct–Mar) has higher baseline rainfall frequency. | Not applicable – excluded from FRI scoring. | **N/A** – Used only as ML classification feature. | Not required for FRI methodology. |

---

## Evidence Level Definitions

| Level | Definition | Implication for FRI |
|-------|-----------|-------------------|
| **Strong** | Established standard or extensively validated methodology from authoritative source. | Directly adopted without modification. |
| **Moderate** | Physical mechanism well-understood; application methodology accepted in literature; local parameterization required. | Adopted with dataset-specific calibration (percentile computation). |
| **Moderate-Low** | Physical relationship established but indirect; contribution magnitude not well-quantified for this specific application. | Included with lower weight allocation; requires sensitivity analysis. |
| **N/A** | Not used in the index calculation. | Excluded from FRI; retained for other purposes. |

---

## Citation Status Summary

| Status | Count | Description |
|--------|-------|-------------|
| Confirmed | 1 | BMKG rainfall classification (official operational standard) |
| Pending | 5 | Literature review in progress; physical rationale established but specific citations not yet identified |
| Not Required | 1 | Month (excluded from FRI) |

---

## Methodological Notes

1. **No fabricated citations**: All entries marked "Pending" represent genuine gaps requiring formal literature review. No placeholder references with invented authors, titles, or DOIs are included.

2. **Evidence hierarchy**: The evidence level assessment follows a conservative approach—variables are classified at their lowest defensible level until supporting literature is formally reviewed and documented.

3. **Threshold source transparency**: The distinction between official standards (BMKG) and dataset-derived thresholds (percentiles) is explicitly maintained to allow reviewers to assess the robustness of each scoring function independently.

4. **Living document**: Citation status will be updated as literature review progresses. Each update will note the date and nature of the change.
