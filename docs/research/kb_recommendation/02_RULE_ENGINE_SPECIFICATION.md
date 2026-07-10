# Recommendation Rule Engine Specification

## 1. Purpose

The Rule Engine replaces the current weighted-scoring approach with a deterministic, knowledge-driven inference system. It maps FRI → Risk Category → Commodity Decisions using explicit rules derived from the knowledge base and agronomic principles.

## 2. Architecture Overview

```
FRI (float 0–100)
     │
     ▼
┌─────────────────┐
│  Risk Classifier │  classify_risk(fri) → "Rendah" | "Sedang" | "Tinggi"
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Inference Rule Engine      │  Matches risk level to rule set
│   ┌──────────────────────┐   │
│   │  Selection Rules     │   │  Which commodities survive at this risk?
│   │  Exclusion Rules     │   │  Which commodities should be avoided?
│   │  Alternative Rules   │   │  What substitutions make sense?
│   │  Priority Rules      │   │  How to rank within each category?
│   └──────────────────────┘   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Decision Output                  │
│  ┌──────────────────────────┐    │
│  │  recommended:    []      │    │
│  │  alternative:    []      │    │
│  │  not_recommended: []     │    │
│  └──────────────────────────┘    │
└──────────────────────────────────┘
```

## 3. Risk Classification Rule

### 3.1 Threshold Definition

| Risk Level | FRI Range | Scientific Basis |
|------------|-----------|------------------|
| Rendah | 0.0 – 33.0 | Tercile 1 of the 0–100 FRI scale. Normal weather conditions. |
| Sedang | 33.1 – 66.0 | Tercile 2. Elevated moisture conditions requiring precaution. |
| Tinggi | 66.1 – 100.0 | Tercile 3. Flood-level conditions requiring maximum protection. |

**Rule R1**: `classify_risk(fri)`:
```
if fri <= 33.0 → "Rendah"
if fri <= 66.0 → "Sedang"
otherwise       → "Tinggi"
```

**Justification**: Tercile split on the 0–100 index is consistent with the existing FRI specification (`ml/predict/risk.py:17-29`). This is a methodological choice documented in `01_FRI_SPECIFICATION.md`.

## 4. Commodity Classification Rules

Each commodity has a `flood_tolerance` attribute. The rule engine uses this as the primary classification axis.

**Rule R2 — Tolerance-Based Grouping**:
```
flood_tolerance == "Sangat Tinggi" → Group A (Survivor)
flood_tolerance == "Tinggi"       → Group B (Tolerant)
flood_tolerance == "Sedang"       → Group C (Moderate)
flood_tolerance == "Rendah"       → Group D (Sensitive)
flood_tolerance == "Sangat Rendah" → Group E (Intolerant)
```

**Scientific basis**: Flood tolerance classification follows the commodity vulnerability hierarchy validated in the knowledge source (`commodity_profiles.json`). The ordinal mapping reflects known physiological thresholds for oxygen deprivation in root zones.

## 5. Inference Rules by Risk Level

### 5.1 Low Risk (FRI ≤ 33.0)

| Rule ID | Rule | Logic | Scientific Justification |
|---------|------|-------|-------------------------|
| R_L1 | All commodities are available for selection | Groups A, B, C, D, E ⊆ available | At low FRI, soil conditions approximate normal. No stress factors limit any crop's physiological function. Standard agronomic principle. |
| R_L2 | Rank by economic priority descending | sort(available, by=economic_priority, reverse=True) | When no environmental constraint exists, economic return maximisation is the rational decision criterion. General agronomic principle. |
| R_L3 | Include drainage requirement as secondary sort | then sort(available, by=drainage_requirement) | Even at low risk, efficient water management reduces production costs. |

**Decision Output for Low Risk**:
- `recommended`: All 17 commodities sorted by economic priority
- `alternative`: Empty (no alternatives needed when all are available)
- `not_recommended`: Empty

### 5.2 Medium Risk (33.0 < FRI ≤ 66.0)

| Rule ID | Rule | Logic | Scientific Justification |
|---------|------|-------|-------------------------|
| R_M1 | Exclude Groups D and E (sensitive and intolerant) | available = Groups A ∪ B ∪ C | Species with low or very low flood tolerance (tomat, jagung_manis, melon, semangka) suffer irreversible root damage within hours of waterlogging. Even moderate FRI indicates sustained soil moisture that exceeds their physiological tolerance. [Pending] — Crop waterlogging tolerance thresholds. |
| R_M2 | Within Group C, prefer short-duration varieties | sort(available_C, by=growing_duration_days) | Shorter growing cycles reduce cumulative exposure to flood risk. At medium risk, the probability of a flood event during the growing period is non-trivial. |
| R_M3 | Prefer climbing/vining habits within C | prefer {kacang_panjang, pare} | Climbing varieties keep reproductive organs above the water surface, reducing direct flood damage. |
| R_M4 | Apply drainage requirement filter | exclude if drainage_requirement ∈ {Tinggi, Sangat Tinggi} | Commodities requiring excellent drainage (cabai_rawit, cabai_merah) are elevated risk at medium FRI. Raised beds become a prerequisite. |
| R_M5 | Rank recommended: A > B > C (tolerance primary) | sort(available, by=(flood_tolerance, economic_priority)) | Tolerance to prevailing conditions is the primary survival factor. Within same tolerance band, economic priority breaks ties. |

**Decision Output for Medium Risk**:
- `recommended`: kangkung, talas, bayam, sawi, kacang_panjang, pare, terong, mentimun, kemangi (sorted by tolerance then priority)
- `alternative`: cabai_rawit, cabai_merah (with raised bed precondition)
- `not_recommended`: tomat, jagung_manis, melon, semangka, selada, seledri

### 5.3 High Risk (FRI > 66.0)

| Rule ID | Rule | Logic | Scientific Justification |
|---------|------|-------|-------------------------|
| R_H1 | Only Group A (survivor) commodities | available = Group A | During active flood conditions (FRI > 66), soil saturation is prolonged. Only species adapted to aquatic or semi-aquatic environments (kangkung — *Ipomoea aquatica*; talas — *Colocasia esculenta*) can survive without total crop loss. |
| R_H2 | Include Group B only with protective measures | alternative = Group B + precondition("raised_beds") | Bayam and sawi can survive if root zones are elevated. This is a conditional recommendation. |
| R_H3 | Exclude Groups C, D, E entirely | not_recommended = Groups C ∪ D ∪ E | At high FRI, any commodity with less than "Tinggi" tolerance faces near-certain crop failure. Planting represents wasted seed, labour, and resources. |
| R_H4 | Prioritise shortest-duration within Group A | sort(A, by=growing_duration_days) | Even survivor species benefit from shorter cycles at high risk, as prolonged inundation eventually exceeds all tolerance thresholds. |

**Decision Output for High Risk**:
- `recommended`: kangkung (25 days), talas (180 days — note: long duration but flood-adapted)
- `alternative`: bayam, sawi (with raised bed precondition)
- `not_recommended`: All other 13 commodities

## 6. Supplementary Inference Rules

### 6.1 Duration Risk Adjustment Rule

**Rule R_D**: Adjust recommendation confidence based on growing duration vs. forecast window.
```
if growing_duration_days > forecast_reliable_window:
    confidence *= 0.8  # Penalise long-duration crops in uncertain conditions
```

**Justification**: Weather forecasts beyond 7–14 days have diminishing reliability. Long-duration crops (e.g., talas at 180 days; cabai_merah at 100 days) carry higher exposure risk that is not captured by current-day FRI alone.

### 6.2 Economic Weighting Rule

**Rule R_E**: Apply economic modifier within same tolerance band.
```
within same tolerance_group:
    rank = f(economic_priority, market_demand, input_cost)
```

**Justification**: When multiple commodities have equal flood tolerance, economic considerations become the differentiating factor. This follows standard agricultural extension decision frameworks.

### 6.3 Mitigation Coupling Rule

**Rule R_MIT**: Each recommendation category carries implied mitigation actions.

| Decision Category | Implied Mitigation |
|-------------------|-------------------|
| recommended | Standard care per risk level |
| alternative | Additional protective measure required (specified in precondition) |
| not_recommended | Do not plant; implement loss-prevention measures |

## 7. Rule Priority and Conflict Resolution

When multiple rules apply, the following priority order resolves conflicts:

1. **Safety-first principle**: Flood tolerance rules override economic priority rules
2. **Specificity principle**: More specific rules override general rules
3. **Recency principle**: Where two rules have equal specificity, the one derived from more recent data takes precedence

**Example conflict**: A commodity with high economic value but low flood tolerance at medium risk.
- Economic rule says: recommend (high value)
- Tolerance rule says: exclude (sensitive)
- Resolution: tolerance rule wins (safety-first)

## 8. Rule Engine Interface (Future — KB Sprint 3)

The Rule Engine will expose the following interface:

```
class RecommendationInferenceEngine:
    def infer(risk_level: str, fri: float) -> RecommendationSet
    def get_recommended(risk_level: str) -> list[CommodityRecord]
    def get_alternative(risk_level: str) -> list[AlternativeRecord]
    def get_not_recommended(risk_level: str) -> list[CommodityRecord]
    def get_mitigation_actions(risk_level: str) -> list[MitigationAction]
```

Where `RecommendationSet` contains:
```
@dataclass
class RecommendationSet:
    risk_level: str
    fri: float
    recommended: list[ScoredRecommendation]
    alternative: list[ScoredRecommendation]
    not_recommended: list[CommodityReference]
    reasoning: list[str]  # Chain of rules applied
```

## 9. Rule Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | Sprint KB3 | Initial rule set from this specification |

Rules are versioned independently of the knowledge base. A rule version change indicates altered inference logic, while a knowledge base version change indicates altered commodity data.
