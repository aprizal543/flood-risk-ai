# Threshold Justification

## Objective

This document provides a rigorous justification for every threshold decision in the Flood Risk Index scoring layer. Each variable's threshold source, selection rationale, and methodological basis are explained to support reproducibility and academic defensibility.

---

## Threshold Strategy Overview

The FRI employs two distinct threshold approaches, selected according to the availability of authoritative standards:

| Approach | Applied To | Rationale |
|----------|-----------|-----------|
| Official Standard | RR (Daily Rainfall) | Nationally recognized BMKG classification exists with defined boundaries |
| Empirical Percentile | Rain3, Rain7, Rain14, RH_avg, TempRange | No official standards exist; thresholds must be derived from local observations |

---

## 1. RR – BMKG Rainfall Intensity Classification

### Threshold Values

| Category | Range (mm/day) | Score Mapping |
|----------|---------------|---------------|
| Tidak hujan | 0 | 0 |
| Hujan ringan | >0 – 5 | 0 – 20 |
| Hujan sedang | >5 – 20 | 20 – 40 |
| Hujan lebat | >20 – 50 | 40 – 70 |
| Hujan sangat lebat | >50 – 100 | 70 – 90 |
| Hujan ekstrem | >100 | 90 – 100 |

### Justification

1. **Authoritative source**: The BMKG classification is the official Indonesian meteorological standard for categorising rainfall intensity. It is used operationally in weather warnings, climate reports, and disaster risk assessments nationwide.

2. **Physical basis**: Category boundaries correspond to observed relationships between rainfall intensity and hydrological response (infiltration exceedance, runoff generation) documented in tropical hydrology.

3. **Reproducibility**: Using a published, externally maintained standard eliminates researcher subjectivity in threshold selection for the primary flood variable.

4. **Consistency**: The same classification is used by BNPB (National Disaster Agency) in flood early warning protocols, ensuring alignment between the FRI and existing disaster management frameworks.

### Score Mapping Rationale

Linear interpolation within each category boundary ensures:
- Continuous, smooth scoring (no abrupt jumps)
- Monotonically increasing relationship between rainfall and risk score
- Full utilisation of the 0–100 scale

The non-uniform score increments (20, 20, 30, 20, 10) reflect the disproportionate increase in flood risk at higher rainfall intensities—heavy rainfall is not merely twice as risky as moderate rainfall.

---

## 2. Rain3, Rain7, Rain14 – Percentile-Based Thresholds

### Why Percentile-Based

The selection of percentile-based thresholds for multi-day rainfall accumulations is justified by the following factors:

**2.1 Absence of Official Standards**

No Indonesian government agency (BMKG, BNPB, PUPR) publishes standardised thresholds for 3-day, 7-day, or 14-day cumulative rainfall in the context of flood risk classification. Unlike daily rainfall intensity, multi-day accumulation does not have a nationally accepted categorisation system.

**2.2 Local Relevance**

Flood-triggering accumulation levels vary substantially between regions due to differences in:
- Soil infiltration capacity
- Terrain slope and drainage
- Urbanisation and land use
- Baseline climatological rainfall

A threshold appropriate for Java (steep terrain, volcanic soils) would not be appropriate for Pekanbaru (flat lowland, peat/alluvial soils). Percentiles computed from local observations inherently capture the station's specific climatological context.

**2.3 Statistical Robustness**

Percentile-based thresholds are:
- Distribution-free (no normality assumption required)
- Resistant to outliers
- Self-calibrating to the available record length
- Interpretable (e.g., "above the 75th percentile" = "among the wettest 25% of observations")

**2.4 Precedent in Hydrometeorology**

Percentile-based approaches are widely used in:
- Drought monitoring (SPI – Standardized Precipitation Index)
- Extreme event definition (ETCCDI climate indices)
- Flood frequency analysis (percentile of flow distribution)

### Threshold Structure

| Percentile | Risk Interpretation | Score Range |
|------------|-------------------|-------------|
| ≤ P25 | Below-normal accumulation; low risk | 0 – 25 |
| P25 – P50 | Normal accumulation; baseline risk | 25 – 50 |
| P50 – P75 | Above-normal accumulation; elevated risk | 50 – 75 |
| ≥ P75 | High accumulation; significant risk | 75 – 100 |

### Computation Methodology

Percentile values (P25, P50, P75) are computed from the complete cleaned dataset (`data/interim/bmkg_clean.csv`) using:
- All valid (non-NaN) observations
- Standard linear interpolation between data points
- One-time computation stored as configuration parameters

### Limitations

- Two years of data may not fully represent the climatological distribution
- Extreme percentiles (P95, P99) are less reliable with limited record length
- Thresholds should be recomputed if the dataset is extended significantly

---

## 3. RH_avg – Percentile-Based Thresholds

### Why Percentile-Based

**3.1 No Standardised Flood-Risk Humidity Threshold**

While agricultural guidelines reference humidity thresholds for disease risk (e.g., >85% for fungal growth), no established standard links specific humidity values to flood risk in horticultural contexts.

**3.2 Indirect Contribution**

Humidity contributes to flood risk through evapotranspiration suppression rather than as a direct water input. The relationship is continuous and gradual, making percentile-based scoring (which captures relative magnitude within the local climate) more appropriate than arbitrary absolute thresholds.

**3.3 Local Climate Dependency**

Pekanbaru's equatorial climate has characteristically high baseline humidity (typically 75–90%). Absolute thresholds from temperate or semi-arid regions would be inappropriate. Percentile scoring automatically adapts to the local humidity distribution.

### Threshold Structure

Same quartile-based structure as rainfall accumulation variables:
- ≤ P25 → Score 0–25 (relatively dry for this location)
- P25–P50 → Score 25–50
- P50–P75 → Score 50–75
- ≥ P75 → Score 75–100 (exceptionally humid even for Pekanbaru)

---

## 4. TempRange – Inverse Percentile-Based Thresholds

### Why Percentile-Based (Inverse)

**4.1 No Standard DTR-Flood Threshold**

Diurnal temperature range is not conventionally used as a flood risk variable. No published standard defines DTR thresholds for flood risk assessment. The variable is included as a meteorological proxy for storm/overcast conditions.

**4.2 Inverse Relationship Justification**

Unlike other variables where higher values indicate higher risk, TempRange has an inverse relationship:
- **Large DTR** → Clear skies, strong solar heating → Low flood risk
- **Small DTR** → Overcast, cloud-insulated → Active weather systems → Higher flood risk

This inverse relationship is physically grounded: persistent cloud cover simultaneously suppresses daytime maxima and elevates nighttime minima.

**4.3 Scoring**

```
Score = 100 - percentile_rank(TempRange) × 100
```

This ensures a day with TempRange at the 10th percentile (unusually compressed, very overcast) receives a score of 90, while a day at the 90th percentile (large range, clear skies) receives a score of 10.

### Threshold Structure (Inverted)

| Percentile of TempRange | Condition | Score Range |
|------------------------|-----------|-------------|
| ≥ P75 | Large range; clear skies | 0 – 25 |
| P50 – P75 | Normal range | 25 – 50 |
| P25 – P50 | Below-normal range | 50 – 75 |
| ≤ P25 | Compressed range; overcast/storm | 75 – 100 |

---

## Summary of Threshold Decisions

| Variable | Approach | Source | Justification |
|----------|----------|--------|---------------|
| RR | BMKG Categories | Official government standard | Authoritative, validated, operationally consistent |
| Rain3 | Percentile (P25/P50/P75) | Pekanbaru dataset | No standard exists; local calibration required |
| Rain7 | Percentile (P25/P50/P75) | Pekanbaru dataset | No standard exists; local calibration required |
| Rain14 | Percentile (P25/P50/P75) | Pekanbaru dataset | No standard exists; local calibration required |
| RH_avg | Percentile (P25/P50/P75) | Pekanbaru dataset | No standard exists; indirect relationship |
| TempRange | Percentile (inverse) | Pekanbaru dataset | No standard exists; proxy variable with inverse relationship |

---

## Methodological Integrity

1. **No arbitrary thresholds**: Every threshold is either sourced from an official standard or derived systematically from data.
2. **Transparent methodology**: The percentile computation is fully reproducible given the same input dataset.
3. **Conservative approach**: Quartile-based division (4 segments) avoids overfitting that finer divisions might introduce with limited data.
4. **Documented limitations**: The reliance on ~2 years of data for percentile estimation is acknowledged as a constraint.
