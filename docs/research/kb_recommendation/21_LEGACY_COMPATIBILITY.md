# Legacy Compatibility Specification

## 1. Principle

DO NOT remove the legacy recommendation system (`ml/recommendation/`) during Sprint KB3. Both systems coexist. A feature flag selects which system is active.

## 2. Feature Flag

**Environment Variable**: `USE_KNOWLEDGE_RECOMMENDATION`

**Defined in**: `backend/config.py`

```python
USE_KNOWLEDGE_RECOMMENDATION: bool = os.getenv(
    "USE_KNOWLEDGE_RECOMMENDATION", "false"
).lower() in ("1", "true", "yes")
```

**Default**: `false` (legacy system active)

**Values**:
- `0`, `false`, `no` → Legacy recommendation (`ml/recommendation/`)
- `1`, `true`, `yes` → Knowledge-based recommendation (`backend/decision/`)

## 3. What Is Preserved

| Component | Status | Reason |
|-----------|--------|--------|
| `ml/recommendation/scorer.py` | Kept | Heuristic scoring engine |
| `ml/recommendation/recommender.py` | Kept | Top-N recommender |
| `ml/recommendation/mitigation.py` | Kept | Mitigation rules |
| `ml/recommendation/explain.py` | Kept | Explanation engine |
| `ml/service/predictor.py` | Kept | Full prediction pipeline |
| `backend/services/prediction_gateway.py` | Kept | Entry point for legacy flow |
| API response format | Unchanged | Frontend continues to work |

## 4. What Was Added (Additive)

| Component | Status | Description |
|-----------|--------|-------------|
| `backend/decision/` | New | KB-based decision engine |
| `app.state.decision_engine` | New | Engine instance |
| `app.state.recommendation_service` | New | Service instance |
| `/api/health` → `decision_engine` field | New | Additive health field |
| `/api/info/*` → decision engine details | New | Additive info field |

## 5. Migration Plan

### Sprint KB3 (current)
- Both systems coexist
- Feature flag defaults to `false` (legacy)
- New engine is fully tested but not active by default

### Sprint KB4
- Feature flag defaults to `true` (knowledge recommendation)
- Legacy system remains available as fallback
- Frontend and API responses are updated if needed

### Sprint KB5+
- Legacy `ml/recommendation/` can be archived
- All consumers use `backend/decision/`

## 6. Switching Between Systems

```python
from backend.config import USE_KNOWLEDGE_RECOMMENDATION
from backend.services.prediction_gateway import predict_from_raw
from backend.decision import KnowledgeRecommendationService

def get_recommendation(fri: float, request):
    if USE_KNOWLEDGE_RECOMMENDATION:
        service: KnowledgeRecommendationService = request.app.state.recommendation_service
        return service.recommend_as_dict(fri)
    else:
        return predict_from_raw(weather, ...)  # legacy
```

## 7. Testing

Both systems are tested independently:

```bash
# Legacy tests
python -m pytest tests/backend/knowledge/

# New KB tests
python -m pytest tests/backend/decision/

# Combined (no regressions)
python -m pytest tests/backend/knowledge/ tests/backend/decision/
```
