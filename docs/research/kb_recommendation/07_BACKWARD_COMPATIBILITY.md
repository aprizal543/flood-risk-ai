# Backward Compatibility Specification

## 1. Components Remaining Completely Unchanged

The following components shall not be modified in any sprint. Their interfaces, behaviour, and output remain identical to the current implementation.

### 1.1 ML Prediction Pipeline

| Component | File | Rationale |
|-----------|------|-----------|
| Random Forest Model | `ml/artifacts/random_forest_v2.pkl` | Trained model artefact; no retraining required |
| RF Predictor | `ml/predict/random_forest.py` | FRI prediction function remains identical |
| LSTM Model | `ml/artifacts/best_lstm.keras` | No changes to deep learning model |
| LSTM Predictor | `ml/predict/lstm.py` | FRI prediction via LSTM unchanged |
| Feature Engineering | `ml/feature_engineering/builder.py` | build_features_v2() output same 4 features |
| Risk Classifier | `ml/predict/risk.py` | classify_risk() thresholds unchanged (33/66) |
| Prediction Validation | `ml/predict/preprocess.py` | Input validation remains identical |
| Feature List | `ml/artifacts/feature_list.json` | Cached feature names (RR, Rain7, RH_avg, Tavg) |

### 1.2 Weather Data Providers

| Component | File | Rationale |
|-----------|------|-----------|
| Open-Meteo Provider | `backend/providers/openmeteo_provider.py` | Weather data fetching unchanged |
| Weather Provider Interface | `backend/providers/__init__.py` | Abstract base class unchanged |
| Provider Exceptions | `backend/providers/exceptions.py` | Error types unchanged |

### 1.3 Authentication and Security

| Component | File | Rationale |
|-----------|------|-----------|
| Auth Dependency | `backend/dependencies/auth.py` | Authentication flow unchanged |
| Rate Limiting | `backend/security/rate_limit.py` | Rate limit configuration unchanged |
| Rate Limit Constants | `backend/security/limits.py` | REALTIME_LIMIT unchanged |

### 1.4 Backend Infrastructure

| Component | File | Rationale |
|-----------|------|-----------|
| FastAPI App Instance | `backend/app.py` | Middleware, CORS, startup unchanged |
| Prediction Gateway | `backend/services/prediction_gateway.py` | Orchestration logic unchanged (internal wiring only) |
| Health Endpoint | `backend/routers/health.py` | No functionality change |
| Info Endpoint | `backend/routers/info.py` | Model version info unchanged |
| CSV Prediction | `backend/routers/csv_prediction.py` | Batch prediction unchanged |
| Manual Prediction | `backend/routers/prediction.py` | Manual input prediction unchanged |

### 1.5 Knowledge Source Files

| Component | File | Rationale |
|-----------|------|-----------|
| Commodity Profiles | `ml/knowledge/commodity_profiles.json` | Source data; schema unchanged during design freeze |
| Recommendation Rules | `ml/knowledge/recommendation_rules.json` | Reference for rule implementation |
| Mitigation Rules | `ml/knowledge/mitigation_rules.json` | Reference for mitigation generation |
| Scientific References | `ml/knowledge/references.md` | Literature documentation unchanged |

### 1.6 Frontend Infrastructure

| Component | File | Rationale |
|-----------|------|-----------|
| App Layout | `apps/web/app/layout.tsx` | No layout changes |
| Dashboard Page | `apps/web/app/dashboard/page.tsx` | Page routing unchanged |
| Shared Components | `apps/web/components/shared/*` | LoadingSkeleton, ErrorState unchanged |
| Service Layer | `apps/web/services/prediction.ts` | HTTP client unchanged (response handling enhanced) |
| Hooks | `apps/web/hooks/use-realtime-prediction.ts` | Data fetching hook unchanged |
| Map Components | `apps/web/components/map/*` | Map selection unchanged |
| AI Chat | `apps/web/components/dashboard/ai-support-panel.tsx` | LLM assistant unchanged |
| Utility Functions | `apps/web/lib/realtime-presentation.ts` | Display formatting unchanged |

### 1.7 Data and Configuration

| Component | File | Rationale |
|-----------|------|-----------|
| ML Datasets | `data/ml/*` | Training/validation splits unchanged |
| Raw Weather Data | `data/raw/*` | Historical weather data unchanged |
| Geo Boundaries | `data/geo/*` | Map boundary data unchanged |
| Environment Config | `.env` | Environment variables unchanged |
| Package Dependencies | `requirements.txt` | No new Python dependencies required |
| Frontend Dependencies | `apps/web/package.json` | No new NPM dependencies required |

## 2. Components Modified (Backward Compatible)

The following components receive additive changes. Existing behaviour is preserved.

### 2.1 API Response Schema

| Change | Nature | Backward Compatible? |
|--------|--------|---------------------|
| New `RekomendasiDetail` model | Additive | Yes — existing `PenjelasanResponse` retained |
| New `RingkasanResponse` | Additive | Yes — new section, not replacing anything |
| New `SumberPengetahuan` | Additive | Yes — new section |
| New `alternatif` field | Additive | Yes |
| New `tidak_direkomendasikan` field | Additive | Yes |

**Contract**: All existing clients consuming `rekomendasi[]` as `PenjelasanResponse[]` continue to work without any changes.

### 2.2 ML Predictor Service

| Change | Nature | Backward Compatible? |
|--------|--------|---------------------|
| `kb_recommend()` added alongside `recommend()` | Additive parallel run | Yes — old path remains operational |
| Enriched output dict | Additive fields | Yes — old keys unchanged |

### 2.3 Mitigation Engine

| Change | Nature | Backward Compatible? |
|--------|--------|---------------------|
| Per-commodity mitigation coupling | Enhanced behaviour | Yes — old `get_mitigasi(risk)` signature unchanged |
| Optional decision set parameter | New overload | Yes — backward-compatible default |

## 3. API Contract Guarantees

### 3.1 Request Contract (No Changes)

| Parameter | Type | Status |
|-----------|------|--------|
| `wilayah` | string (required) | Unchanged |
| `model` | "rf" \| "lstm" | Unchanged |
| `top_n` | int (1–17) | Unchanged |

### 3.2 Response Contract (Additive Only)

```json
// Old fields — all present:
{ "status", "wilayah", "sumber_data", "forecast_date", "updated_at",
  "waktu_prediksi", "model", "versi_model", "RR", "Rain7", "RH_avg",
  "Tavg", "cuaca", "hari_historis", "fri", "tingkat_risiko",
  "rekomendasi": [PenjelasanResponse], "mitigasi": [TindakanMitigasiResponse] }

// New fields — added:
{ "ringkasan": RingkasanResponse,
  "rekomendasi": [RekomendasiDetail],  ← Note: same key, enriched type
  "alternatif": [RekomendasiDetail],
  "tidak_direkomendasikan": [RekomendasiDetail],
  "sumber_pengetahuan": SumberPengetahuan }
```

**Important**: The `rekomendasi` key is reused. During migration, it contains the enriched `RekomendasiDetail[]`. Old clients using `rekomendasi[].komoditas` and `rekomendasi[].skor` will still work since these fields exist in both schemas. However, `rekomendasi[].tingkat_keyakinan` as a float changes semantics. See Section 4.

### 3.3 Deprecation Timeline

| Sprint | Change | Deprecation Notice |
|--------|--------|-------------------|
| KB Sprint 4 | New fields added; old `PenjelasanResponse` deprecated in OpenAPI | `deprecated: true` in schema |
| KB Sprint 5 | Frontend migrates to new response format | N/A |
| KB Sprint 6 | Old fields removed | Breaking change announced 1 sprint in advance |

## 4. Potential Breaking Changes (Mitigated)

### 4.1 `tingkat_keyakinan` Semantic Change

| Aspect | Current | Future |
|--------|---------|--------|
| Calculation | `skor / max_score` (relative ranking) | Rule confidence (absolute, based on rule strength) |
| Range | 0–1 (relative) | 0–1 (absolute) |
| Impact | Values may differ slightly | Frontend should treat as approximate confidence, not exact ranking |

**Mitigation**: In Phase 1, both values are returned. Frontend is updated to use the new semantic in Phase 2.

### 4.2 `skor` Value Changes

**Impact**: Scores computed by rule engine will differ from heuristic scores. A commodity scoring 85 in the old system may score 78 in the new system.

**Mitigation**: The `rekomendasi_badge.label` field provides a categorical label ("Sangat Direkomendasikan", "Direkomendasikan", etc.) so frontend can display category-based UI instead of score-based UI. This decouples the UI from exact score values.

## 5. Testing Compatibility

| Test Type | Method | Success Criterion |
|-----------|--------|-------------------|
| Integration | Run old API call, verify old fields present | All old fields return valid values |
| Integration | Run new API call, verify new fields present | All new fields return valid values |
| Integration | Compare heuristic vs. KB output | No contradiction in top-5 commodities |
| Regression | Run existing test suite | All existing tests pass without modification |
| Visual | Screenshot comparison of old vs. new UI | No visual regression in unchanged components |

## 6. Configuration Backward Compatibility

```yaml
# No new configuration keys required
# Existing .env variables all retained
# No new environment variables
# No new service dependencies
```

## 7. Commitment

The KB-DSS migration introduces zero breaking changes to:
- API request contracts
- Core ML prediction pipeline
- Weather data providers
- Authentication and security
- Frontend routing and page structure
- Database schemas (if any)
- Deployment configuration
- Monitoring and logging
