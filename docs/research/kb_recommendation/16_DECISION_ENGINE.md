# Decision Engine Specification

## 1. Overview

The Decision Engine is the core component of the KB-DSS recommendation system. It replaces the legacy heuristic scoring approach with a deterministic, rule-based engine driven entirely by the Knowledge Base.

## 2. Architecture

```
┌──────────────────────────────────────────────────────────┐
│              KnowledgeRecommendationService              │
│  (high-level orchestrator — entry point for the system)  │
├──────────────────────────────────────────────────────────┤
│                      DecisionEngine                      │
│  ┌─────────┐  ┌──────────┐  ┌───────────────┐           │
│  │  Rules  │  │   KB     │  │ Explainability │           │
│  │ Engine  │  │  Query   │  │   Engine       │           │
│  └────┬────┘  └────┬─────┘  └───────┬───────┘           │
│       │            │                │                    │
│       └────────────┼────────────────┘                    │
│                    │                                     │
│              ┌─────▼──────┐                              │
│              │  Mapper    │                              │
│              │ (FRI→Risk) │                              │
│              └────────────┘                              │
└──────────────────────────────────────────────────────────┘
         │
         ▼
   DecisionResult
   ┌─────────────────────┐
   │  DecisionContext    │  FRI, RiskCategory, timestamp
   │  RecommendationGroup│  recommended (list)
   │  RecommendationGroup│  alternative (list)
   │  RecommendationGroup│  not_recommended (list)
   │  DecisionMetadata   │  execution stats, version
   │  DecisionReport     │  coverage, integrity
   └─────────────────────┘
```

## 3. Decision Flow

```
Input: FRI (float 0–100)
  │
  1. Mapper: FRI → RiskCategory (Rendah/Sedang/Tinggi)
  │
  2. KnowledgeBase.get_all() → 17 CommodityKnowledge
  │
  3. For each commodity:
     ├── Rule Engine: evaluate(vulnerability_level, risk_category)
     ├── Status: recommended | alternative | not_recommended
     ├── Explainability: generate_reason(commodity, status, risk)
     └── CommodityRecommendation built
  │
  4. Group by status → 3 RecommendationGroups
  │
  5. Sort each group by vulnerability (highest first)
  │
  6. Assemble DecisionResult with context + metadata + report
  │
  Output: DecisionResult
```

## 4. File Layout

```
backend/decision/
├── __init__.py                — Package exports
├── models.py                  — Strongly-typed Pydantic models
├── exceptions.py              — Exception hierarchy
├── mapper.py                  — FRI→RiskCategory mapping
├── rules.py                   — InferenceRuleEngine (decision table)
├── engine.py                  — DecisionEngine (core orchestrator)
├── validator.py               — DecisionValidator (integrity checks)
├── explainability.py          — ExplainabilityEngine (KB-driven text)
├── recommendation_service.py  — KnowledgeRecommendationService
└── README.md                  — Usage guide
```

## 5. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Frozen models** | Immutability prevents accidental mutation of results |
| **Decision table** | All 15 (5×3) rules defined explicitly — easy to audit |
| **Separate service layer** | `KnowledgeRecommendationService` handles orchestration; `DecisionEngine` is the pure logic |
| **No scoring** | Rules produce status directly — no weights, no ranking |
| **Fail-fast startup** | Engine validates rules + KB during `initialize()` |
| **Additive health** | Health endpoint extended with `decision_engine` field |

## 6. Dependencies

- **Internal**: `backend.knowledge.*` (Knowledge Base)
- **External**: None (pure Python + Pydantic)
- **ML**: None — decision engine is completely independent
