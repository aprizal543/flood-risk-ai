# Realtime End-to-End Audit - FRI v2

## Objective

Strict read-only audit of the realtime prediction pipeline to verify whether `GET /api/prediksi/realtime` is connected end-to-end to the FRI v2 backend path.

No backend, frontend, model, configuration, authentication, security, router, service, or feature-engineering code was modified during this audit.

## Section 1 - Realtime Endpoint

| Item | Finding |
|------|---------|
| Endpoint | `GET /api/prediksi/realtime` |
| Router file | `backend/routers/realtime.py` |
| Handler function | `predict_realtime()` |
| Registered by | `backend/app.py`, `app.include_router(realtime_router)` |
| Provider dependency | Module-level `_provider = OpenMeteoProvider()` |
| Prediction service invoked | `backend.services.prediction_gateway.predict_from_raw()` |
| Authentication | `Depends(get_current_user)` from `backend.dependencies.auth` |
| Auth behavior | Missing/invalid Bearer token raises `401 Unauthorized` before route body execution |
| Rate limiting | `@limiter.limit(REALTIME_LIMIT)` from `backend.security.rate_limit`; `REALTIME_LIMIT = "60/minute"` |
| Query parameters | `wilayah`, `model`, `top_n` |

Relevant code locations:

| File | Lines |
|------|-------|
| `backend/routers/realtime.py` | 24-38 endpoint declaration, auth dependency, rate limit, query params |
| `backend/routers/realtime.py` | 41-55 provider call and gateway call |
| `backend/routers/realtime.py` | 65-88 response assembly |
| `backend/app.py` | 28 imports realtime router; 106 registers it |
| `backend/dependencies/auth.py` | 11-18 authentication dependency and 401 behavior |
| `backend/security/limits.py` | 20-21 prediction/realtime limits |

## Section 2 - Execution Flow

Exact realtime execution chain when authentication succeeds:

```text
HTTP GET /api/prediksi/realtime
  -> backend.app.app
  -> backend.middleware.LoggingMiddleware.dispatch()
  -> backend.middleware.SecurityHeadersMiddleware.dispatch()
  -> slowapi.middleware.SlowAPIMiddleware
  -> backend.routers.realtime.predict_realtime()
  -> backend.dependencies.auth.get_current_user()
  -> backend.services.auth_service.verify_access_token()
  -> backend.providers.openmeteo_provider.OpenMeteoProvider.get_weather_history(wilayah, days=14)
  -> backend.providers.geocoding.geocode(wilayah)
  -> requests.get(Open-Meteo forecast API)
  -> backend.providers.models.RawWeatherData rows
  -> latest row selected as weather
  -> preceding rows selected as weather_history
  -> backend.services.prediction_gateway.predict_from_raw(weather, weather_history=preceding, model=model, top_n=top_n)
  -> ml.feature_engineering.builder.build_features_v2(raw_data, history=effective_history)
  -> ml.feature_engineering.rainfall.compute_rain7(rr_series)
  -> pandas.DataFrame columns [RR, Rain7, RH_avg, Tavg]
  -> ml.service.predictor.prediksi(features, model="rf", top_n=top_n)
  -> ml.predict.preprocess.validate_input(row)
  -> ml.predict.preprocess.get_feature_list()
  -> pandas.DataFrame(rows)[features]
  -> ml.predict.random_forest.predict_rf(df.iloc[[-1]])
  -> ml.predict.random_forest._load_model()
  -> joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")
  -> RandomForestRegressor.predict(df)
  -> ml.predict.risk.classify_risk(fri)
  -> ml.recommendation.recommender.recommend(fri, top_n=top_n)
  -> ml.recommendation.explain.explain_recommendation(...)
  -> ml.recommendation.mitigation.get_mitigasi(risiko)
  -> backend.routers.realtime.predict_realtime() response dict
```

## Section 3 - Feature Verification

Runtime feature metadata file:

```text
ml/artifacts/feature_list.json
```

Current content:

```json
[
  "RR",
  "Rain7",
  "RH_avg",
  "Tavg"
]
```

Feature builder used by realtime gateway:

```text
backend.services.prediction_gateway.predict_from_raw()
  -> ml.feature_engineering.builder.build_features_v2()
```

`build_features_v2()` output order:

```text
RR, Rain7, RH_avg, Tavg
```

Dataframe captured at `predict_rf()` during a read-only runtime probe:

```text
columns: [RR, Rain7, RH_avg, Tavg]
dtypes:  [float64, float64, float64, float64]
row:     {RR: 10.0, Rain7: 37.0, RH_avg: 80.0, Tavg: 27.5}
```

Feature verification result:

| Check | Result |
|-------|--------|
| Feature names | PASS: `RR`, `Rain7`, `RH_avg`, `Tavg` |
| Feature order | PASS: exact expected order |
| Feature count | PASS: 4 |
| Data types at RF prediction | PASS: all `float64` |
| Legacy realtime features absent from RF dataframe | PASS: no `rr`, `rain3`, `rain14`, `temp_range`, `rainfall_anomaly`, `month`, or `day_of_year` |

No mismatch found.

## Section 4 - Model Verification

Actual RF loader:

```text
ml/predict/random_forest.py
  _load_model()
  joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")
```

Resolved artifact path from runtime probe:

```text
D:\flood-risk-ai\ml\artifacts\random_forest_v2.pkl
```

Model metadata verified at runtime:

```text
n_features_in_: 4
feature_names_in_: [RR, Rain7, RH_avg, Tavg]
```

Model verification result:

| Check | Result |
|-------|--------|
| Active RF artifact | PASS: `random_forest_v2.pkl` |
| Legacy RF artifact loaded by realtime RF path | PASS: no evidence of `random_forest.pkl` load in active RF path |
| Model feature count | PASS: 4 |
| Model feature names match runtime feature list | PASS |

## Section 5 - Prediction Validation

`predict()` receives the output of `build_features_v2()`, not legacy `build_features()`.

Evidence:

| Layer | Evidence |
|-------|----------|
| Gateway import | `backend/services/prediction_gateway.py` imports `build_features_v2` from `ml.feature_engineering.builder` |
| Gateway call | `predict_from_raw()` calls `df = build_features_v2(raw_data, history=effective_history)` |
| Prediction service | `prediksi()` validates against `feature_list.json`, builds `pd.DataFrame(rows)[features]`, and passes the last row to `predict_rf()` |
| RF call | `predict_rf()` calls `model.predict(df)` |
| Captured RF dataframe | `[RR, Rain7, RH_avg, Tavg]`, all `float64` |

Conclusion: realtime RF prediction is connected to `build_features_v2()`.

## Section 6 - Authentication Boundary

Authentication dependency:

```text
backend.dependencies.auth.get_current_user()
```

Behavior:

```text
credentials is None -> HTTPException(401, "Unauthorized")
invalid/expired token -> HTTPException(401, "Invalid or expired token")
```

Read-only runtime probe without `Authorization` header:

```text
GET /api/prediksi/realtime?wilayah=Pekanbaru
status: 401
provider called: False
prediction called: False
```

Authentication boundary result:

| Check | Result |
|-------|--------|
| `401 Unauthorized` occurs before provider execution | PASS |
| `401 Unauthorized` occurs before prediction execution | PASS |
| Prediction code reachable without auth | PASS: not reachable |

## Section 7 - End-to-End Readiness

Readiness verdict:

```text
READY
```

The audited realtime RF path is connected:

```text
Router
  -> Gateway
  -> build_features_v2()
  -> random_forest_v2.pkl
  -> predict()
  -> Response
```

Readiness score:

```text
95/100
```

Rationale for not assigning 100:

| Residual item | Impact |
|---------------|--------|
| `model` query still allows `lstm` | Realtime RF v2 path is ready, but selecting `model=lstm` follows a legacy/non-v2 path and is outside this RF v2 audit. |
| Response field `versi_model` remains `1.0` | Does not block execution, but metadata naming is not aligned with RF v2. |
| sklearn warning | `random_forest_v2.pkl` was serialized with sklearn `1.6.1` and loaded under sklearn `1.8.0`; prediction still executed successfully. |

## Section 8 - Remaining Work

No missing integration points were found for the realtime RF v2 path.

If the product requires `model=lstm` to remain supported on the realtime endpoint after RF v2 migration, that is a separate non-RF integration decision. It is not required for the audited path:

```text
Router -> Gateway -> build_features_v2() -> random_forest_v2.pkl -> predict() -> Response
```

## Section 9 - Risk Assessment

Remaining migration work classification:

```text
Low
```

Estimated backend files still requiring modification for realtime RF v2 integration:

```text
0
```

Migration complexity:

```text
Low
```

## Verification Commands

Runtime model and feature metadata probe:

```text
python -c "import joblib; from ml.predict.preprocess import ARTIFACTS_DIR, get_feature_list; p=ARTIFACTS_DIR / 'random_forest_v2.pkl'; m=joblib.load(p); print(p); print(get_feature_list()); print(getattr(m, 'n_features_in_', None)); print(list(getattr(m, 'feature_names_in_', [])))"
```

Observed output:

```text
D:\flood-risk-ai\ml\artifacts\random_forest_v2.pkl
['RR', 'Rain7', 'RH_avg', 'Tavg']
4
['RR', 'Rain7', 'RH_avg', 'Tavg']
```

Runtime dataframe capture at RF prediction boundary:

```text
columns: [RR, Rain7, RH_avg, Tavg]
dtypes:  [float64, float64, float64, float64]
row:     {RR: 10.0, Rain7: 37.0, RH_avg: 80.0, Tavg: 27.5}
result:  rf 42.8 Risiko Sedang
```

Unauthenticated boundary probe:

```text
GET /api/prediksi/realtime?wilayah=Pekanbaru
status: 401
provider called: False
prediction called: False
```

## Files Inspected

```text
backend/app.py
backend/middleware.py
backend/routers/realtime.py
backend/dependencies/auth.py
backend/security/limits.py
backend/security/rate_limit.py
backend/providers/openmeteo_provider.py
backend/providers/models.py
backend/services/prediction_gateway.py
ml/feature_engineering/builder.py
ml/feature_engineering/rainfall.py
ml/service/predictor.py
ml/predict/preprocess.py
ml/predict/random_forest.py
ml/artifacts/feature_list.json
ml/artifacts/random_forest_v2.pkl
```

## Files Created

```text
docs/research/fri_v2/realtime_end_to_end_audit.md
```

## Files Modified

```text
None, except this audit report file.
```

## Final Recommendation

Sprint FRI v2.5C may safely begin.

The realtime RF path is already connected end-to-end to FRI v2 feature engineering and the RF v2 model artifact. No backend integration changes are required for the audited RF realtime pipeline before starting the next sprint.
