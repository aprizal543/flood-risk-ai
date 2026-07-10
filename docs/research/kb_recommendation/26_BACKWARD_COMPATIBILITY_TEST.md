# Backward Compatibility Test Plan

## 1. Compatibility Matrix

| Test | Legacy Mode | KB Mode | Method |
|------|-------------|---------|--------|
| Manual prediction endpoint | ✅ | ✅ | POST /api/prediksi/manual |
| Engineered prediction endpoint | ✅ | ✅ | POST /api/prediksi/engineered |
| Realtime prediction endpoint | ✅ | ✅ | GET /api/prediksi/realtime |
| CSV prediction endpoint | ✅ | ✅ | POST /api/prediksi/csv |
| Health endpoint | ✅ | ✅ | GET /api/health |
| Info/Detail endpoint | ✅ | ✅ | GET /api/health/detail |
| Authentication | ✅ | ✅ | All endpoints |
| Rate limiting | ✅ | ✅ | All endpoints |

## 2. Schema Tests

### PrediksiResponse Schema

| Test | Expected |
|------|----------|
| Construct without knowledge fields | Succeeds |
| `model` field present | Always |
| `fri` field present | Always |
| `rekomendasi` field present | Always |
| `mitigasi` field present | Always |
| `knowledge_recommendation` is None in legacy mode | True |
| `knowledge_source` is None in legacy mode | True |

### HealthResponse Schema

| Test | Expected |
|------|----------|
| Construct without knowledge/decision_engine | Succeeds |
| `recommendation_engine` field present | Always |
| `decision_engine` field present | Always |
| `knowledge` field present | Always |

## 3. Response Structure Tests

### Legacy Mode (flag OFF)

```
GET /api/health
  → Contains: status, versi, ready, decision_engine, recommendation_engine, knowledge
  → Does NOT contain: knowledge_recommendation, knowledge_source

POST /api/prediksi/manual
  → Contains: model, fri, tingkat_risiko, rekomendasi, mitigasi
  → knowledge_recommendation is null or absent
  → knowledge_source is null or absent
```

### KB Mode (flag ON)

```
POST /api/prediksi/manual
  → Contains: all legacy fields + knowledge_recommendation + knowledge_source
  → rekomendasi still present (mapped from KB)
  → knowledge_recommendation.recommended is populated
  → knowledge_recommendation.alternative is populated
  → knowledge_recommendation.not_recommended is populated
```

## 4. Behavioral Tests

| Scenario | Expected Behavior |
|----------|------------------|
| KB engine available, flag ON | KB recommendations served |
| KB engine error, flag ON | Graceful fallback to legacy |
| KB engine not initialized, flag ON | Graceful fallback to legacy |
| Flag OFF, KB healthy | Legacy recommendations served |
| Flag changes without restart | Read from env on next request |

## 5. Running Compatibility Tests

```bash
# All tests (legacy mode default)
python -m pytest tests/backend/ -v

# Specific integration tests
python -m pytest tests/backend/test_recommendation_gateway.py -v
python -m pytest tests/backend/test_api_integration.py -v

# KB mode tests
$env:USE_KNOWLEDGE_RECOMMENDATION="true"
python -m pytest tests/backend/test_recommendation_gateway.py -v
$env:USE_KNOWLEDGE_RECOMMENDATION="false"
```
