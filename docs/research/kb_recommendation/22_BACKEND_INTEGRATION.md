# Backend Integration Architecture

## 1. Integration Points

The Decision Engine integrates into 4 API layers:

```
FastAPI Endpoints
    │
    ├── /api/prediksi/manual        → predict_from_raw() → augment_with_knowledge()
    ├── /api/prediksi/engineered     → run_prediction()   → augment_with_knowledge()
    ├── /api/prediksi/realtime       → predict_from_raw() → augment_with_knowledge()
    ├── /api/prediksi/csv            → predict_from_raw() → augment_with_knowledge()
    │
    ├── /api/health                  → decision_engine + recommendation_engine fields
    └── /api/health/detail           → recommendation_engine + feature flag info
```

## 2. Data Flow

```
Weather Data → Feature Engineering → RF Model → FRI
                                                    │
                                                    ▼
                                          Recommendation Gateway
                                          ┌──────────────────┐
                                          │ Check Feature    │
                                          │ Flag             │
                                          └────┬──────┬──────┘
                                               │      │
                                          False│      │True
                                               │      │
                                               ▼      ▼
                                      ┌──────────┐ ┌──────────────┐
                                      │ Legacy   │ │ Decision     │
                                      │ Scoring  │ │ Engine (KB)  │
                                      └──────────┘ └──────┬───────┘
                                                          │
                                                          ▼
                                                 ┌────────────────┐
                                                 │ Recommendation │
                                                 │ Mapper         │
                                                 └────────────────┘
                                                          │
                                                          ▼
                                            ┌─────────────────────┐
                                            │ Unified Response    │
                                            │ + knowledge fields  │
                                            └─────────────────────┘
```

## 3. How Augmentation Works

The `augment_with_knowledge()` function is the single seam for all recommendation switching:

1. **Receives** the base prediction result dict (from ML pipeline)
2. **Checks** `USE_KNOWLEDGE_RECOMMENDATION` flag
3. If **legacy mode**: returns base result unchanged
4. If **KB mode**: calls `KnowledgeRecommendationService`, maps output to legacy-compatible format, adds `knowledge_recommendation` and `knowledge_source` fields

## 4. Files Changed

| File | Change |
|------|--------|
| `backend/services/recommendation_gateway.py` | **New** — unified gateway |
| `backend/services/recommendation_mapper.py` | **New** — response format mapper |
| `backend/schemas/response.py` | Extended — additive KB fields |
| `backend/routers/prediction.py` | Updated — uses gateway |
| `backend/routers/realtime.py` | Updated — uses gateway |
| `backend/routers/csv_prediction.py` | Updated — uses gateway |
| `backend/routers/health.py` | Extended — additive fields |
| `backend/routers/info.py` | Extended — additive fields |
| `backend/config.py` | Already had `USE_KNOWLEDGE_RECOMMENDATION` |

## 5. Design Principles

- **Additive only**: New fields are optional and default to None.
- **No breaking changes**: Legacy clients never see knowledge fields.
- **No ML changes**: RF, FRI, and weather provider are untouched.
- **No frontend changes**: All existing API consumers work without updates.
- **Graceful fallback**: If KB engine fails, legacy response is returned.
