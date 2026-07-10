# Decision Engine — Knowledge-Based Recommendation

The Decision Engine replaces the legacy heuristic scoring approach with a deterministic, rule-based system driven entirely by the Knowledge Base.

## Architecture

```
FRI → KnowledgeRecommendationService
         │
         └──→ DecisionEngine.decide(fri)
                 │
                 ├──→ RiskMapper (FRI → RiskCategory)
                 ├──→ KnowledgeBase.get_all()
                 ├──→ InferenceRuleEngine.evaluate(vuln, risk)
                 ├──→ ExplainabilityEngine.generate_reason()
                 ├──→ Group by RecommendationStatus
                 └──→ DecisionResult
```

## Key Principles

- **No scoring**: Recommendations are rule-based, not score-based.
- **Deterministic**: Same input always produces the same output.
- **Knowledge-driven**: All explanations generated from KB fields.
- **No ML dependency**: The Decision Engine imports nothing from `ml/`.

## Usage

```python
from backend.decision import DecisionEngine, KnowledgeRecommendationService
from backend.knowledge import KnowledgeBase

kb = KnowledgeBase()
kb.initialize()

engine = DecisionEngine(knowledge_base=kb)
engine.initialize()

service = KnowledgeRecommendationService(engine)
result = service.recommend(fri=45.0)

print(result.recommended)       # list of CommodityRecommendation
print(result.alternative)       # list of CommodityRecommendation
print(result.not_recommended)   # list of CommodityRecommendation
```

## Modules

| Module | Description |
|--------|-------------|
| `models.py` | Strongly-typed Pydantic models |
| `exceptions.py` | Exception hierarchy |
| `mapper.py` | FRI → risk category mapping |
| `rules.py` | Deterministic decision table |
| `engine.py` | Core orchestration engine |
| `validator.py` | Result validation and reporting |
| `explainability.py` | KB-driven human-readable explanations |
| `recommendation_service.py` | Top-level service orchestrator |
