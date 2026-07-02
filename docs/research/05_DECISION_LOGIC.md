# Decision Logic

## Objective

Define the decision architecture that translates Flood Risk Index (FRI) outputs into actionable agricultural recommendations. This document describes the logical flow only—no implementation.

---

## Decision Pipeline

```
Flood Risk Index (0–100)
    ↓
Risk Level Classification
    ↓
Commodity Suitability Assessment
    ↓
Mitigation Recommendation
    ↓
Reasoning / Explanation
```

---

## Stage 1: Risk Level Classification

### Input
FRI value (continuous, 0–100)

### Output
Risk category (categorical)

### Logic

| FRI Range | Risk Level | Agricultural Interpretation |
|-----------|------------|---------------------------|
| 0–33 | Low | Normal conditions; standard agricultural operations |
| 34–66 | Medium | Elevated moisture; planning adjustments advised |
| 67–100 | High | Significant flood risk; protective measures required |

---

## Stage 2: Commodity Suitability Assessment

### Input
Risk level + temporal context (month, season)

### Output
List of suitable horticultural commodities with suitability score

### Logic Architecture

```
IF risk_level = "Low":
    → All commodities suitable
    → Prioritize high-value, water-sensitive crops

IF risk_level = "Medium":
    → Filter to moderate flood-tolerant commodities
    → Exclude highly water-sensitive species

IF risk_level = "High":
    → Restrict to flood-tolerant commodities only
    → Recommend postponement of planting for sensitive crops
```

### Commodity Classification Framework

Commodities are classified by flood tolerance:

| Tolerance Level | Characteristics | Example Categories |
|----------------|-----------------|-------------------|
| High | Survives waterlogging >3 days; shallow root system acceptable | Leafy vegetables, kangkung, water spinach |
| Medium | Tolerates brief waterlogging (<2 days); requires drainage | Chili, tomato (with raised beds), eggplant |
| Low | No waterlogging tolerance; root rot within hours | Melon, strawberry, lettuce (ground-planted) |

Specific commodity lists are determined by:
1. Local horticultural practices in Pekanbaru
2. Agricultural extension office recommendations
3. Crop-specific waterlogging tolerance literature

---

## Stage 3: Mitigation Recommendation

### Input
Risk level + commodity selection + FRI component scores

### Output
Prioritized list of mitigation actions

### Logic Architecture

```
IF risk_level = "Low":
    → Routine maintenance
    → Standard drainage inspection

IF risk_level = "Medium":
    → Ensure drainage channels are clear
    → Consider raised bed preparation
    → Mulching for erosion prevention
    → Monitor weather forecast for escalation

IF risk_level = "High":
    → Activate flood protection (raised beds, barriers)
    → Harvest mature crops early if possible
    → Delay new planting
    → Ensure drainage infrastructure at full capacity
    → Prepare post-flood recovery materials
```

### Component-Specific Recommendations

The FRI decomposition (individual score contributions) enables targeted recommendations:

| Dominant Risk Factor | Specific Mitigation |
|---------------------|-------------------|
| High RR score | Short-term drainage; cover crops |
| High Rain7/Rain14 score | Long-term drainage; water table management |
| High RH_avg score | Ventilation; fungicide preparation (secondary effect) |
| Low TempRange score | Monitor for continued storm activity |

---

## Stage 4: Reasoning / Explanation

### Input
FRI value + component scores + risk level + recommendations

### Output
Human-readable explanation of why the recommendation was made

### Logic Architecture

The reasoning layer produces an explanation structured as:

```
1. Current Conditions:
   "FRI is [value] ([category]) because [dominant contributors]."

2. Primary Risk Drivers:
   "The main risk factors are [top 2-3 contributors by w_i × S_i]."

3. Recommendation Rationale:
   "[Commodity X] is recommended because [flood tolerance] aligns with [risk level]."
   "[Mitigation Y] is advised because [specific risk driver] is elevated."

4. Confidence:
   "This assessment is based on [confidence]% of available indicators."
```

---

## Decision Rules Summary

| Risk Level | Planting Decision | Crop Selection | Mitigation Urgency |
|------------|------------------|----------------|-------------------|
| Low | Proceed normally | Full range available | Routine |
| Medium | Proceed with precautions | Moderate+ tolerance | Preventive |
| High | Postpone or protect | High tolerance only | Immediate |

---

## Constraints

1. **No implementation in this document**: This describes architecture only.
2. **Commodity lists are configurable**: Not hardcoded; loaded from reference data.
3. **Recommendations are advisory**: The system does not make autonomous decisions.
4. **Transparency required**: Every recommendation must be traceable to specific FRI components.
5. **Graceful degradation**: If FRI confidence is low (missing data), recommendations are flagged as uncertain.

---

## Integration Points

| System Component | Consumes | Produces |
|-----------------|----------|----------|
| FRI Generator (Sprint 4) | Cleaned features | FRI values + scores |
| Decision Engine (Future) | FRI + component scores | Recommendations |
| User Interface (Future) | Recommendations + reasoning | Display to farmer/extension officer |
