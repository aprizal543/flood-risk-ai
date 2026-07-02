# Feature Justification

## Objective

Provide scientific justification for each feature selected for the Flood Risk Index (FRI) system. Each section explains the physical mechanism by which the variable contributes to flood risk in a tropical lowland agricultural context.

---

## 1. RR – Daily Rainfall (mm)

### Role in FRI
Primary flood trigger variable.

### Scientific Justification

Rainfall intensity is the most direct determinant of flood occurrence in tropical regions. When rainfall rate exceeds soil infiltration capacity, surface runoff is generated. In lowland areas like Pekanbaru (elevation ~39m), flat terrain limits drainage velocity, making high-intensity rainfall events the primary initiator of agricultural flooding.

### Physical Mechanism

```
High-intensity rainfall → Infiltration exceedance → Surface runoff → Water accumulation → Flooding
```

### Threshold Basis

BMKG official rainfall intensity classification provides nationally standardized categories that are operationally meaningful and scientifically peer-accepted across Indonesian meteorological applications.

---

## 2. Rain3 – 3-Day Cumulative Rainfall (mm)

### Role in FRI
Short-term soil saturation indicator.

### Scientific Justification

Single-day rainfall alone does not capture the antecedent moisture condition. Consecutive days of moderate rainfall can saturate soil just as effectively as a single extreme event. A 3-day window captures the immediate pre-event moisture buildup that determines whether additional rainfall generates runoff or infiltrates.

### Physical Mechanism

```
Day 1–2 rainfall → Soil moisture increase → Reduced infiltration capacity
Day 3 rainfall → Already saturated soil → Immediate runoff generation
```

### Why 3 Days

Three days represents the typical short-term memory of tropical soils before partial drainage/evaporation occurs. This timeframe captures back-to-back rain events within a single synoptic weather system.

---

## 3. Rain7 – 7-Day Cumulative Rainfall (mm)

### Role in FRI
Medium-term saturation and water table indicator.

### Scientific Justification

A 7-day accumulation window captures the effects of sustained wet periods that raise the water table. In tropical lowland environments, one week of above-average rainfall is sufficient to bring shallow water tables to surface level, eliminating infiltration entirely and creating waterlogged conditions.

### Physical Mechanism

```
Sustained weekly rainfall → Water table rise → Zero infiltration capacity → Widespread surface saturation
```

### Why 7 Days

Seven days aligns with typical synoptic-scale weather patterns (passage of ITCZ, monsoon surges) and represents the time horizon over which shallow groundwater responds to sustained precipitation input.

---

## 4. Rain14 – 14-Day Cumulative Rainfall (mm)

### Role in FRI
Extended antecedent moisture condition.

### Scientific Justification

The 14-day window captures prolonged wet spells characteristic of active monsoon phases. Two weeks of elevated rainfall fundamentally alters the catchment's hydrological state: soil column is fully saturated, drainage channels are at capacity, and any additional rainfall—even moderate—results in flooding.

### Physical Mechanism

```
2-week wet spell → Complete soil saturation → Drainage infrastructure at capacity → Minimal additional rainfall triggers flooding
```

### Why 14 Days

Fourteen days represents approximately one phase of the Madden-Julian Oscillation (MJO) active cycle, which modulates extended wet periods in the Maritime Continent. This timescale captures the transition from normal to flood-prone catchment state.

---

## 5. RH_avg – Average Relative Humidity (%)

### Role in FRI
Atmospheric moisture and evapotranspiration deficit indicator.

### Scientific Justification

High relative humidity (>85%) indicates:
1. Reduced evapotranspiration, meaning wet surfaces remain wet longer.
2. Near-saturated atmospheric conditions associated with persistent cloud cover and continued rainfall probability.
3. Reduced soil drying between rain events.

In tropical agricultural contexts, sustained high humidity accelerates waterlogging because the evapotranspiration pathway for removing surface water is suppressed.

### Physical Mechanism

```
High RH → Low evapotranspiration → Surface water persists → Waterlogging duration extended
High RH → Continued rainfall probability → Compound risk
```

---

## 6. TempRange – Diurnal Temperature Range (TX - TN, °C)

### Role in FRI
Cloud cover and storm condition proxy.

### Scientific Justification

Diurnal temperature range (DTR) is inversely correlated with cloud cover and precipitation in tropical environments:

- **Large DTR** (clear skies): Strong daytime solar heating, strong nighttime radiative cooling → Fair weather, low flood risk.
- **Small DTR** (overcast): Cloud cover suppresses daytime heating and insulates nighttime cooling → Associated with active precipitation systems.

A compressed DTR signals the presence of weather systems capable of producing sustained or heavy rainfall.

### Physical Mechanism

```
Low TempRange → Persistent cloud cover → Active precipitation system → Elevated flood risk
High TempRange → Clear skies → Low precipitation probability → Reduced flood risk
```

### Inverse Scoring

Unlike other variables, TempRange uses inverse scoring: lower values produce higher risk scores.

---

## 7. Month – Calendar Month

### Role
**ML classification feature only. Excluded from FRI.**

### Scientific Justification for Inclusion as ML Feature

Pekanbaru's climate exhibits seasonal precipitation patterns driven by the ITCZ migration and monsoon systems. The wet season (approximately October–March) has climatologically higher rainfall frequency and intensity. Month encodes this seasonal context for machine learning models.

### Justification for Exclusion from FRI

1. **Not a physical driver**: Month is a temporal index, not a physical quantity that causes flooding.
2. **Redundancy**: Seasonal rainfall patterns are already captured by RR, Rain3, Rain7, and Rain14 during wet months.
3. **Circular reasoning**: Including month would bias the index toward wet-season dates regardless of actual observations, reducing the index's discriminatory power for unusual dry-season floods or dry spells during wet season.

---

## Summary Table

| Feature | Physical Mechanism | Direction | Threshold Approach |
|---------|-------------------|-----------|-------------------|
| RR | Infiltration exceedance | Higher → More risk | BMKG categories |
| Rain3 | Short-term saturation | Higher → More risk | Percentile |
| Rain7 | Water table response | Higher → More risk | Percentile |
| Rain14 | Catchment state change | Higher → More risk | Percentile |
| RH_avg | Evapotranspiration suppression | Higher → More risk | Percentile |
| TempRange | Storm/cloud proxy | **Lower → More risk** | Percentile (inverse) |
| Month | Seasonal context | N/A | Not scored |
