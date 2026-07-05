# Sprint v2.5C End-to-End Validation

## Objective

Validate the complete authenticated realtime RF v2 path after migration:

```text
HTTP request -> auth -> router -> provider -> gateway -> build_prediction_features_v2() -> build_features_v2() -> prediksi() -> random_forest_v2.pkl -> predict() -> response
```

## Backend Startup

| Check | Result |
|-------|--------|
| FastAPI app import | PASS |
| App title available | PASS: `Flood Risk DSS API` |
| No import errors in startup probe | PASS |
| RF model load | PASS |
| Runtime RF prediction | PASS |

## Authentication Validation

| Scenario | Result |
|----------|--------|
| Anonymous realtime request | PASS: `401 Unauthorized`; provider and prediction were not called. |
| Valid authenticated request | PASS: `200 OK` using dependency override with `AuthUser`. |
| Invalid JWT | PASS: `401`, JSON error schema. |
| Expired JWT | PASS: `401`, JSON error schema. |

## Realtime Prediction Validation

Authenticated mocked realtime request result:

```text
status: 200
model: rf
fri: 55.37
tingkat_risiko: Risiko Sedang
hari_historis: 13
```

Feature seam call counts after the minimal fix:

```text
build_prediction_features_v2: 1
build_features_v2: 1
```

FRI v2 feature vector reaching RF prediction:

```text
RR, Rain7, RH_avg, Tavg
```

Data types:

```text
float64, float64, float64, float64
```

Runtime artifact loaded:

```text
random_forest_v2.pkl
```

## Prediction Response Validation

| Check | Result |
|-------|--------|
| Prediction returned | PASS |
| Risk category returned | PASS |
| Recommendation confidence fields returned | PASS: `tingkat_keyakinan` in recommendation objects. |
| JSON serialization | PASS |
| Required realtime keys present | PASS |
| No `None` values | PASS |
| No `NaN` values | PASS |
| Data types | PASS: `fri=float`, `tingkat_risiko=str`, `rekomendasi=list`, `mitigasi=list`. |

Realtime response keys:

```text
cuaca, forecast_date, fri, hari_historis, mitigasi, model, rekomendasi, status, sumber_data, tingkat_risiko, updated_at, versi_model, waktu_prediksi, wilayah
```

## Production Safety Validation

| Check | Result |
|-------|--------|
| Active RF loader uses `random_forest_v2.pkl` | PASS |
| Runtime feature list is v2 | PASS: `RR`, `Rain7`, `RH_avg`, `Tavg`. |
| `random_forest.pkl` loaded by active RF path | PASS: not loaded. |
| Legacy v1 feature vector used by active realtime RF path | PASS: not used. |
| `Rain3` in active realtime RF dataframe | PASS: absent. |
| `Rain14` in active realtime RF dataframe | PASS: absent. |
| `TempRange` in active realtime RF dataframe | PASS: absent. |
| `RainfallAnomaly` in active realtime RF dataframe | PASS: absent. |

Static grep found only legacy compatibility definitions/status metadata, not active realtime RF usage:

| Finding | Interpretation |
|---------|----------------|
| `random_forest_legacy` in metadata | Legacy artifact visibility only. |
| v1 engineered fields in `PrediksiEngineeredRequest` | Legacy engineered endpoint compatibility issue. |
| `build_features()` definition in `ml/feature_engineering/builder.py` | Deprecated legacy builder retained; not called by active realtime RF path. |

## Regression Findings

| Finding | Severity | Decision |
|---------|----------|----------|
| `build_prediction_features_v2()` was not directly invoked by realtime before this sprint. | Low | Fixed by routing `predict_from_raw()` through the existing seam. |
| Missing RF model returned raw `Internal Server Error` text. | Medium | Fixed with `FileNotFoundError` JSON handler. |
| `/api/prediksi/engineered` still accepts v1 engineered features and returns `422` under v2 RF metadata. | Medium | Not fixed in this sprint; requires explicit API compatibility decision. |
| Existing `tests/test_api_integration.py` expects unauthenticated prediction/CSV access and 9 features. | Low | Test suite is stale relative to current security and FRI v2 state. |

## Final Readiness

Production readiness score: 90/100

Final recommendation:

```text
Production Ready with Minor Issues
```

The authenticated realtime RF v2 flow is end-to-end valid. Sprint follow-up should decide whether to remove, migrate, or explicitly deprecate the legacy engineered endpoint.
