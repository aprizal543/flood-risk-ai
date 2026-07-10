# Future Integration Roadmap

## 1. Sprint KB3 — Rule Engine (Next)

The Rule Engine will load rules from the Knowledge Base and apply them to input data:

```
Input → Rule Engine → Context → KnowledgeBase → Recommendation Engine → Output
                          ↑
                    KnowledgeBase (lookups)
```

### Integration Points
- Rule definitions stored as a new `rules/` collection in the KB data directory.
- `RuleEngine` class accepts a `KnowledgeBase` instance for commodity lookups.
- Rules reference commodities by `commodity_id` and use KB fields (vulnerability, tolerance, etc.) as conditions.

### Proposed Rule Format
```json
{
  "rule_id": "flood_high_recommend_kangkung",
  "condition": {
    "field": "flood_risk",
    "operator": ">=",
    "value": "Tinggi"
  },
  "actions": [
    {
      "type": "recommend_commodity",
      "commodity_id": "kangkung",
      "priority": 1
    }
  ]
}
```

### KB Dependencies
- `KnowledgeBase.get_by_id()` and `KnowledgeBase.query()` for rule matching.
- No changes to the core KB modules — the Rule Engine imports the facade.

## 2. Sprint KB4 — Recommendation Engine

The Recommendation Engine aggregates rule outputs and KB data to produce ranked recommendations:

### Inputs
- Rule evaluation results (list of matched rules with priorities).
- Knowledge Base commodity profiles (from the cache).
- Optional: user preferences (commodity categories, economic priority).

### Output
- Ranked list of `RecommendedCommodity` objects with scores and explanations.

### KB Dependencies
- Batch lookups via `KnowledgeBase.get_all()` for scoring all commodities.
- `KnowledgeBase.get_by_category()` for filtered recommendations.
- `KnowledgeBase.get_by_vulnerability()` for flood-based filtering.

## 3. Sprint KB5 — ML Integration

The ML subsystem (RF, LSTM, FRI) will remain separate but may consume KB data:

### Potential Integration
- ML models use KB fields as feature inputs (e.g., vulnerability_level ordinal, growing_duration_days).
- ML predictions feed into the Rule Engine as dynamic rule conditions.
- KB provides ground-truth labels for ML model validation.

### Isolation Guarantee
- The KB module imports **nothing** from the ML module.
- The ML module may optionally import from `backend.knowledge` but not vice versa.
- This prevents circular dependencies and allows independent testing.

## 4. Sprint KB6 — API & Frontend

### New API Endpoints
```
GET  /api/v1/knowledge/commodities          → list all commodities
GET  /api/v1/knowledge/commodities/{id}     → single commodity detail
GET  /api/v1/knowledge/categories           → list categories
GET  /api/v1/knowledge/vulnerability-levels  → list vulnerability levels
GET  /api/v1/recommendations                → recommendation endpoint
```

### Frontend Integration
- Commodity data cards rendered from KB fields.
- Filter UI driven by `list_categories()` and `list_vulnerability_levels()`.
- Recommendation results displayed with KB-sourced explanations.

## 5. Sprint KB7 — Enhanced Knowledge (Future)

Potential enhancements after the core system is stable:

- **Versioned snapshots**: Store historical versions of commodity profiles.
- **Regional variants**: Override KB values by geographic region.
- **Dynamic thresholds**: Allow configuration of vulnerability/drainage thresholds without code changes.
- **Approval workflow**: Staged updates for KB content changes.
- **Admin API**: CRUD endpoints for KB management.

## 6. Dependency Graph

```
         ┌──────────────────┐
         │  Knowledge Base  │  ← Sprint KB2 (complete)
         └────────┬─────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│ Rule    │ │ Recomnd. │ │ ML       │
│ Engine  │ │ Engine   │ │ Subsystem│
└─────────┘ └──────────┘ └──────────┘
Sprint KB3   Sprint KB4   Sprint KB5
```

Arrows indicate "depends on" or "imports from". No arrows point into the KB — it is a dependency leaf.
