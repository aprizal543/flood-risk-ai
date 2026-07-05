# Backend Prediction Pipeline Audit For FRI v2

## Status

Read-only audit completed.

## Scope

This report maps the current backend prediction pipeline before FRI v2 backend migration. No backend, frontend, model, dataset, source, configuration, or artifact file was modified by this audit.

## Executive Summary

Backend readiness: PARTIALLY READY

Readiness score: 62 / 100

Migration complexity: HIGH

Primary blocker: the runtime backend still uses the FRI v1 model path, v1 feature list, and v1 feature-engineering shape. The new `random_forest_v2.pkl` artifact exists and expects four features, but no backend runtime path currently loads or feeds it.

## Architecture Diagram

```text
HTTP Request
  |
  v
FastAPI Router
  |-- /api/prediksi/realtime
  |-- /api/prediksi/manual
  |-- /api/prediksi/engineered
  |-- /api/prediksi/csv
  |-- /api/prediksi/csv/download
  |
  v
Authentication + Rate Limiting
  |
  v
Raw Weather Provider / Request Body / CSV Parser
  |
  v
backend.services.prediction_gateway.predict_from_raw
  |
  v
ml.feature_engineering.builder.build_features
  |
  v
ml.service.predictor.prediksi
  |
  v
ml.predict.preprocess.get_feature_list
  |
  v
ml.predict.random_forest.predict_rf
  |
  v
joblib.load(ml/artifacts/random_forest.pkl)
  |
  v
model.predict([rr, rain3, rain7, rain14, rh_avg, temp_range, rainfall_anomaly, month, day_of_year])
  |
  v
Risk Classification -> Recommendations -> Mitigation -> API Response
```

## Section 1: Prediction Entry Points

| Endpoint | Method | File | Function | Request Schema | Response Schema | Authentication | Rate Limit | Service Called |
|----------|--------|------|----------|----------------|-----------------|----------------|------------|----------------|
| `/api/prediksi/realtime` | GET | `backend/routers/realtime.py:24-88` | `predict_realtime` | Query: `wilayah`, `model=rf|lstm`, `top_n` | Inline dict with status, weather metadata, FRI, risk, recommendations, mitigation | `Depends(get_current_user)` | `REALTIME_LIMIT = 60/minute` | `OpenMeteoProvider.get_weather_history`, then `predict_from_raw` |
| `/api/prediksi/manual` | POST | `backend/routers/prediction.py:21-55` | `predict_manual` | `PrediksiManualRequest` | `PrediksiResponse` | `Depends(get_current_user)` | `PREDICTION_LIMIT = 20/minute` | `predict_from_raw` |
| `/api/prediksi/engineered` | POST | `backend/routers/prediction.py:58-80` | `predict_engineered` | `PrediksiEngineeredRequest` | `PrediksiResponse` | `Depends(get_current_user)` | `PREDICTION_LIMIT = 20/minute` | `run_prediction` |
| `/api/prediksi/csv` | POST | `backend/routers/csv_prediction.py:94-132` | `predict_csv` | Multipart CSV upload with columns `tanggal`, `rr`, `rh_avg`, `tmax`, `tmin` | Inline dict with tanggal, historical row count, FRI, risk, recommendations, mitigation | `Depends(get_current_user)` | `PREDICTION_LIMIT = 20/minute` | `predict_from_raw` |
| `/api/prediksi/csv/download` | POST | `backend/routers/csv_prediction.py:135-177` | `predict_csv_download` | Multipart CSV upload with columns `tanggal`, `rr`, `rh_avg`, `tmax`, `tmin` | CSV stream with tanggal, FRI, risk, top commodity, confidence | `Depends(get_current_user)` | `PREDICTION_LIMIT = 20/minute` | `predict_from_raw` |
| `/api/provider/openmeteo` | GET | `backend/routers/provider.py:15-51` | `get_openmeteo_weather` | Query: `wilayah` | Inline current weather dict | `Depends(get_current_user)` | None on route | `OpenMeteoProvider.get_current_weather` |
| `/api/info/model` | GET | `backend/routers/info.py:10-16` | `model_info` | None | Model metadata dict | None | None | `get_model_info` |

### Request Schema Details

`PrediksiManualRequest` in `backend/schemas/request.py:8-30` expects:

- `tanggal`
- `rr`
- `rh_avg`
- `tmax`
- `tmin`
- `model`
- `top_n`

`PrediksiEngineeredRequest` in `backend/schemas/request.py:33-45` expects v1 engineered features:

- `rr`
- `rain3`
- `rain7`
- `rain14`
- `rh_avg`
- `temp_range`
- `rainfall_anomaly`
- `month`
- `day_of_year`
- `model`
- `top_n`

`PrediksiResponse` in `backend/schemas/response.py:22-27` returns:

- `model`
- `fri`
- `tingkat_risiko`
- `rekomendasi`
- `mitigasi`

## Section 2: Prediction Flow

### Realtime Call Chain

```text
GET /api/prediksi/realtime
  -> backend.routers.realtime.predict_realtime
  -> OpenMeteoProvider.get_weather_history(wilayah, days=14)
  -> latest RawWeatherData = history_data[-1]
  -> preceding RawWeatherData list = history_data[:-1]
  -> prediction_gateway.predict_from_raw(weather, weather_history=preceding, model=model, top_n=top_n)
  -> convert weather_history to [{"rr": w.rr}]
  -> ml.feature_engineering.builder.build_features(raw_data, history=effective_history)
  -> ml.service.predictor.prediksi(features, model=model, top_n=top_n)
  -> ml.predict.preprocess.get_feature_list()
  -> pandas.DataFrame(rows)[feature_list]
  -> ml.predict.random_forest.predict_rf(df.iloc[[-1]]) for model="rf"
  -> joblib.load(ml/artifacts/random_forest.pkl), cached in module global _model
  -> model.predict(df)
  -> classify_risk(fri)
  -> recommend(fri)
  -> get_mitigasi(risiko)
  -> router response dict
```

### Manual Raw Call Chain

```text
POST /api/prediksi/manual
  -> backend.routers.prediction.predict_manual
  -> RawWeatherData(tanggal, rr, rh_avg, tmax, tmin)
  -> prediction_gateway.predict_from_raw(weather, history=None)
  -> build_features(raw_data, history=None)
  -> rain3 = rr, rain7 = rr, rain14 = rr
  -> prediksi -> predict_rf -> random_forest.pkl -> response
```

### Engineered Feature Call Chain

```text
POST /api/prediksi/engineered
  -> backend.routers.prediction.predict_engineered
  -> req.model_dump(exclude={"model", "top_n"})
  -> predictor_service.run_prediction(features)
  -> ml.service.predictor.prediksi(features)
  -> validate against feature_list.json
  -> predict_rf -> random_forest.pkl -> response
```

### CSV Call Chain

```text
POST /api/prediksi/csv or /api/prediksi/csv/download
  -> _parse_csv
  -> _validate_and_sort(sort ascending by tanggal)
  -> _build_weather_and_history
  -> predict_from_raw(weather, history=[{"rr": ...}])
  -> build_features -> prediksi -> predict_rf -> response
```

## Section 3: Feature Engineering Map

| Feature | File | Function | Formula | Realtime Or Offline | Current Status |
|---------|------|----------|---------|---------------------|----------------|
| `rr` / `RR` | `ml/feature_engineering/builder.py:33-38` | `build_features` | `float(raw_data["rr"])` | Realtime, manual, CSV | Used by v1 runtime; needed by v2 |
| `rain3` | `ml/feature_engineering/rainfall.py:6-8` | `compute_rain3` | `rr_series.rolling(window=3, min_periods=1).sum()` | Realtime/CSV if history exists; manual fallback = `rr` | Used by v1 runtime; removed in v2 |
| `rain7` | `ml/feature_engineering/rainfall.py:11-13` | `compute_rain7` | `rr_series.rolling(window=7, min_periods=1).sum()` | Realtime/CSV if history exists; manual fallback = `rr` | Used by v1 runtime; retained in v2 |
| `rain14` | `ml/feature_engineering/rainfall.py:16-18` | `compute_rain14` | `rr_series.rolling(window=14, min_periods=1).sum()` | Realtime/CSV if history exists; manual fallback = `rr` | Used by v1 runtime; removed in v2 |
| `rh_avg` / `RH_avg` | `ml/feature_engineering/builder.py:33-38` | `build_features` | `float(raw_data["rh_avg"])` | Realtime, manual, CSV | Used by v1 runtime; needed by v2 |
| `temp_range` | `ml/feature_engineering/temperature.py:4-6` | `compute_temp_range` | `tmax - tmin` | Realtime, manual, CSV | Used by v1 runtime; removed in v2 |
| `rainfall_anomaly` | `ml/feature_engineering/anomaly.py:12-21` | `compute_rainfall_anomaly` | `np.interp(rr, _RR_PERCENTILES, _PCT_VALUES)` | Realtime, manual, CSV | Used by v1 runtime; removed in v2 |
| `month` | `ml/feature_engineering/calendar.py:6-8` | `compute_month` | `tanggal.month` | Realtime, manual, CSV | Used by v1 runtime; not part of v2 final features |
| `day_of_year` | `ml/feature_engineering/calendar.py:11-14` | `compute_day_of_year` | `tanggal.timetuple().tm_yday` | Realtime, manual, CSV | Used by v1 runtime; not part of v2 final features |
| `Tavg` | None in current backend runtime | None | Not computed; current runtime has `tmax`, `tmin`, and `temp_range` only | Not available in current backend runtime | Required by v2 but missing |

## Section 4: Realtime Pipeline

Open-Meteo request:

- File: `backend/providers/openmeteo_provider.py`
- URL: `https://api.open-meteo.com/v1/forecast`
- Daily fields: `precipitation_sum`, `relative_humidity_2m_mean`, `temperature_2m_max`, `temperature_2m_min`
- Timezone: `Asia/Jakarta`
- Current weather path requests yesterday through today in `get_current_weather`.
- Realtime prediction path requests `days=14` in `get_weather_history`.

Historical days downloaded:

- `backend/routers/realtime.py:39-41` calls `_provider.get_weather_history(wilayah, days=14)`.
- `OpenMeteoProvider.get_weather_history` uses `start_date = today - timedelta(days=days - 1)` and `end_date = today`, so it requests 14 calendar days including today.
- The latest day is prediction day; the preceding 13 days are passed to rolling features.

Realtime answers:

| Question | Answer |
|----------|--------|
| Where is `Rain7` calculated? | `ml/feature_engineering/builder.py:44-50` calls `compute_rain7`; formula in `ml/feature_engineering/rainfall.py:11-13` |
| Does `Rain3` exist? | Yes, `compute_rain3`; currently included in runtime feature vector |
| Does `Rain14` exist? | Yes, `compute_rain14`; currently included in runtime feature vector |
| Does anomaly exist? | Yes, `compute_rainfall_anomaly`; currently included in runtime feature vector |
| Does temperature range exist? | Yes, `compute_temp_range`; currently included in runtime feature vector |
| Does `Tavg` exist? | No backend runtime feature currently computes or passes `Tavg` |
| Does caching exist? | No weather or prediction cache found in realtime path; only model/feature/scaler module globals and config/Supabase `lru_cache` exist |
| Do rolling windows exist? | Yes, rainfall windows 3, 7, and 14 days use pandas rolling with `min_periods=1` |

## Section 5: Model Loading Map

| Artifact | Current Path | Loader | Singleton Or Per Request | Current Backend Use | Notes |
|----------|--------------|--------|--------------------------|---------------------|-------|
| Random Forest v1 | `ml/artifacts/random_forest.pkl` | `joblib.load` in `ml/predict/random_forest.py:14-19` | Lazy singleton via module global `_model` | Active for `model="rf"` | Expects 9 v1 features |
| Random Forest v2 | `ml/artifacts/random_forest_v2.pkl` | Not used by backend | Not loaded | Not active | Exists; expects 4 v2 features |
| LSTM | `ml/artifacts/best_lstm.keras` | `keras.models.load_model` in `ml/predict/lstm.py:15-21` | Lazy singleton via `_model` | Active for `model="lstm"` if requested and enough rows | Depends on v1 feature list and scaler |
| LSTM scaler | `ml/artifacts/scaler_lstm.pkl` | `joblib.load` in `ml/predict/preprocess.py:26-31` | Lazy singleton via `_scaler` | Active for LSTM only | Scales v1 feature sequence |
| Feature list | `ml/artifacts/feature_list.json` | JSON read in `ml/predict/preprocess.py:17-23` | Lazy singleton via `_feature_list` | Active for all model paths | Contains 9 v1 features |

Artifact inspection found:

- `random_forest.pkl`: `RandomForestRegressor`, `n_features_in_ = 9`, `feature_names_in_ = ['rr', 'rain3', 'rain7', 'rain14', 'rh_avg', 'temp_range', 'rainfall_anomaly', 'month', 'day_of_year']`
- `random_forest_v2.pkl`: `RandomForestRegressor`, `n_features_in_ = 4`, `feature_names_in_ = ['RR', 'Rain7', 'RH_avg', 'Tavg']`

## Section 6: Exact Prediction Features Sent Into `model.predict()`

Current RF path:

```python
features = get_feature_list()
df = pd.DataFrame(rows)[features]
fri = predict_rf(df.iloc[[-1]])
prediction = model.predict(df)[0]
```

Exact current feature vector order from `ml/artifacts/feature_list.json`:

```text
[
  rr,
  rain3,
  rain7,
  rain14,
  rh_avg,
  temp_range,
  rainfall_anomaly,
  month,
  day_of_year
]
```

This is a v1 feature vector. It is incompatible with `random_forest_v2.pkl`, whose model metadata expects:

```text
[
  RR,
  Rain7,
  RH_avg,
  Tavg
]
```

## Section 7: Unused Legacy Code Assessment

| Code / Feature | Location | Still Used Or Dead Code | Reason |
|----------------|----------|-------------------------|--------|
| `rain3` | `ml/feature_engineering/rainfall.py`, `builder.py`, `feature_list.json`, request schema | Still used | Required by current v1 RF feature list and engineered endpoint |
| `rain14` | `ml/feature_engineering/rainfall.py`, `builder.py`, `feature_list.json`, request schema | Still used | Required by current v1 RF feature list and engineered endpoint |
| `temp_range` | `ml/feature_engineering/temperature.py`, `builder.py`, `feature_list.json`, request schema | Still used | Required by current v1 RF feature list and engineered endpoint |
| `rainfall_anomaly` | `ml/feature_engineering/anomaly.py`, `builder.py`, `feature_list.json`, request schema | Still used | Required by current v1 RF feature list and engineered endpoint |
| `month` | `calendar.py`, `builder.py`, `feature_list.json`, request schema | Still used | Required by current v1 RF feature list but not FRI v2 |
| `day_of_year` | `calendar.py`, `builder.py`, `feature_list.json`, request schema | Still used | Required by current v1 RF feature list but not FRI v2 |

Conclusion: legacy code is not dead yet. It is active in the production backend pipeline and must be migrated carefully rather than deleted blindly.

## Section 8: Backend File Impact Matrix

| File | Impact | Why Impacted |
|------|--------|--------------|
| `ml/predict/random_forest.py` | HIGH | Loads `random_forest.pkl`; must load v2 artifact or support selectable artifact path |
| `ml/artifacts/feature_list.json` | HIGH | Current cached feature list is v1; backend uses it for validation/order |
| `ml/feature_engineering/builder.py` | HIGH | Produces v1 features and does not compute `Tavg`; gateway depends on it |
| `backend/services/prediction_gateway.py` | HIGH | Converts raw weather into feature vector via v1 builder; realtime/manual/CSV all pass through it |
| `backend/schemas/request.py` | HIGH | Engineered request schema requires v1 feature payload; v2 requires 4-feature payload if endpoint remains |
| `backend/routers/realtime.py` | MEDIUM | Response model version and realtime history assumptions may need v2 alignment; currently uses 14 days despite v2 only needing 7-day accumulation |
| `backend/routers/prediction.py` | MEDIUM | Manual/engineered endpoint descriptions and schema wiring must align with v2 |
| `backend/routers/csv_prediction.py` | MEDIUM | CSV feature history can remain, but v2 builder output and response assumptions must align |
| `backend/services/metadata_service.py` | MEDIUM | Health/model info still points to `random_forest.pkl` and reports v1 feature list |
| `ml/predict/preprocess.py` | MEDIUM | Central feature list loader/validator caches v1 artifact; v2 may need separate feature-list strategy |
| `ml/service/predictor.py` | MEDIUM | Uses `get_feature_list()` and `predict_rf`; output pipeline can stay but input assumptions must change |
| `backend/providers/openmeteo_provider.py` | LOW/MEDIUM | Provides `tmax`/`tmin` but not `Tavg`; may need daily mean temperature from provider or derived average |
| `ml/predict/lstm.py` | LOW unless LSTM retained | LSTM is v1-feature-based and may be out of scope if v2 production uses RF only |
| `ml/predict/risk.py` | LOW | Classification thresholds are stable unless scientific evaluation changes them |
| Recommendation modules | LOW | Consume final FRI only; likely unchanged |

## Section 9: Risk Assessment

| File | Why It Must Change | Why It Should Not Change Too Much | Migration Risk | Rollback Difficulty |
|------|--------------------|-----------------------------------|----------------|---------------------|
| `ml/predict/random_forest.py` | Must load `random_forest_v2.pkl` for v2 RF inference | Broad changes risk breaking lazy singleton loading | HIGH | MEDIUM |
| `ml/artifacts/feature_list.json` | Must align feature order with v2 if reused | Overwriting v1 list breaks LSTM and rollback | HIGH | HIGH |
| `ml/feature_engineering/builder.py` | Must output `RR`, `Rain7`, `RH_avg`, `Tavg` for v2 | Removing v1 builder directly breaks existing endpoints/tests | HIGH | HIGH |
| `backend/services/prediction_gateway.py` | Central raw-weather gateway must route to v2 features | It is shared by realtime, manual, and CSV | HIGH | MEDIUM |
| `backend/schemas/request.py` | Engineered schema must accept v2 feature shape | Changing schema breaks clients using v1 engineered endpoint | HIGH | MEDIUM |
| `backend/routers/realtime.py` | Must report correct model/version and pass correct history | Realtime endpoint is user-facing and should preserve response contract | MEDIUM | MEDIUM |
| `backend/routers/csv_prediction.py` | Must ensure CSV history can produce v2 `Rain7` and `Tavg` | CSV parsing/sorting should remain stable | MEDIUM | LOW |
| `backend/services/metadata_service.py` | Must report v2 model path/features | Health endpoints support observability; inaccurate metadata is risky | MEDIUM | LOW |
| `backend/providers/openmeteo_provider.py` | May need mean temperature source or derived `Tavg` rule | Provider changes can break realtime API integration | MEDIUM | MEDIUM |
| `ml/service/predictor.py` | Must validate/order v2 features before prediction | Recommendation/mitigation orchestration is stable and should remain | MEDIUM | LOW |

## Section 10: Migration Readiness

Readiness: PARTIALLY READY

Reasons ready:

- `random_forest_v2.pkl` exists and has expected 4-feature metadata.
- Realtime already fetches enough rainfall history for `Rain7`.
- Central gateway architecture gives a single common path for realtime/manual/CSV raw-weather predictions.
- Recommendation and mitigation layers consume only final FRI and likely do not require migration.

Reasons not fully ready:

- Active RF loader still points to `random_forest.pkl`.
- Active feature list remains v1 with 9 features.
- Active feature builder emits v1 features and lacks `Tavg`.
- Engineered request schema is v1-only.
- Metadata service reports v1 artifact and v1 feature list.
- LSTM option is still exposed in API query/schema but v2 methodology states Random Forest remains the algorithm; LSTM path is not aligned with v2.
- Realtime response hardcodes `versi_model = "1.0"`.

## Files That MUST Change For FRI v2 Backend Migration

- `ml/predict/random_forest.py`
- `ml/artifacts/feature_list.json` or a new v2-specific feature list artifact/path
- `ml/feature_engineering/builder.py` or a new v2 builder module
- `backend/services/prediction_gateway.py`
- `backend/schemas/request.py`
- `backend/services/metadata_service.py`
- `backend/routers/realtime.py`
- `backend/routers/prediction.py`
- `backend/routers/csv_prediction.py`

## Files That MUST NOT Change Unless Explicitly Approved

- Dataset files under `data/interim` and prior processed source datasets
- Cleaning scripts
- Merge scripts
- Frontend files under `apps/web`
- Authentication files and Supabase auth logic
- Security middleware and rate-limit policy, unless required only for versioned endpoint metadata
- Deployment configuration
- Existing model artifact `ml/artifacts/random_forest.pkl` if rollback must be preserved
- Existing `ml/artifacts/scaler_lstm.pkl` and `best_lstm.keras` unless LSTM deprecation is explicitly approved

## Safe Migration Order

1. Add a v2 feature-order strategy without deleting v1 feature list.
2. Add a v2 raw-weather feature builder that outputs exactly `RR`, `Rain7`, `RH_avg`, `Tavg`.
3. Decide and document `Tavg` realtime formula/source before implementation. Current provider supplies max/min but not mean temperature.
4. Add v2 RF loader path for `random_forest_v2.pkl` while preserving rollback to `random_forest.pkl`.
5. Wire `prediction_gateway` to v2 builder and v2 model path behind a narrow switch or direct v2 migration, depending on sprint scope.
6. Update request schema for engineered v2 predictions or deprecate engineered v1 endpoint explicitly.
7. Update realtime/manual/CSV route descriptions, model version fields, and validation expectations.
8. Update metadata/health reporting to include v2 artifact and v2 feature order.
9. Run integration tests for realtime/manual/CSV prediction paths.
10. Verify rollback by restoring v1 model/feature path without altering source datasets.

## Migration Recommendations

- Prefer adding v2-specific builder and artifact constants first, rather than mutating v1 builder and feature list in place.
- Keep `random_forest.pkl` and v1 feature list available until v2 production deployment is accepted.
- Treat LSTM exposure as a product decision: either keep v1 LSTM as legacy only or remove the `lstm` option in a separate approved API migration.
- Do not change authentication, rate limits, CORS, or security middleware during FRI v2 backend migration.
- Add explicit tests that capture the exact `model.predict()` DataFrame columns for v2.
- Confirm provider-derived `Tavg` scientifically before implementation. If using `(tmax + tmin) / 2`, document it because training used `Tavg` from BMKG clean data.

## Final Readiness Score

| Category | Score | Notes |
|----------|-------|-------|
| Artifact availability | 80 | v2 RF artifact exists and has expected feature metadata |
| Feature engineering readiness | 45 | Rain7 exists; Tavg missing; v1 removed features still active |
| Model loading readiness | 50 | Lazy loader is good but points to v1 artifact |
| API compatibility readiness | 55 | Response contract can likely stay; engineered schema is v1-only |
| Realtime readiness | 65 | Open-Meteo history is sufficient for Rain7; Tavg unresolved |
| Rollback readiness | 75 | v1 artifact and current path still intact |

Overall readiness score: 62 / 100

Overall readiness: PARTIALLY READY

Estimated Sprint v2.5 impact: HIGH

Recommendation: Sprint FRI v2.5 may begin only as a controlled backend migration sprint with explicit tests and rollback preservation. It should not include frontend, security, authentication, deployment, or model retraining work.
