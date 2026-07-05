# Sprint v2.5B Validation Report

## Objective

Migrate the active backend Random Forest prediction path from the legacy v1 artifact and nine-feature vector to the FRI v2 artifact and frozen four-feature vector, while preserving API response schemas and leaving frontend, authentication, security, deployment, and legacy rollback artifact unchanged.

## Status

PASS WITH KNOWN NON-RF LIMITATIONS

The active RF prediction path now loads `random_forest_v2.pkl`, reads runtime features from the v2 `feature_list.json`, and receives features from `build_features_v2` through `predict_from_raw`.

## Files Modified

| File | Purpose |
|------|---------|
| `ml/predict/random_forest.py` | Changed lazy RF loader from `random_forest.pkl` to `random_forest_v2.pkl`. |
| `ml/artifacts/feature_list.json` | Replaced legacy nine-feature order with frozen FRI v2 feature order. |
| `backend/services/prediction_gateway.py` | Connected raw-weather prediction to `build_features_v2` before calling `prediksi`. |
| `backend/services/metadata_service.py` | Updated model metadata and health artifact path to the active RF v2 artifact while retaining legacy artifact status visibility. |
| `tests/test_weather_provider.py` | Added RF v2 artifact, feature-order, loader-path, and smoke-prediction compatibility checks. |

## Active Feature List

```text
RR, Rain7, RH_avg, Tavg
```

Runtime feature order is exactly:

```json
[
  "RR",
  "Rain7",
  "RH_avg",
  "Tavg"
]
```

## Model Artifact Mapping

| Artifact | Status |
|----------|--------|
| `ml/artifacts/random_forest_v2.pkl` | Active RF prediction artifact. |
| `ml/artifacts/random_forest.pkl` | Preserved as legacy rollback artifact. |

## Prediction Flow

```text
RawWeatherData + rainfall history
  -> backend.services.prediction_gateway.predict_from_raw
  -> ml.feature_engineering.builder.build_features_v2
  -> {RR, Rain7, RH_avg, Tavg}
  -> ml.service.predictor.prediksi
  -> ml.predict.random_forest.predict_rf
  -> ml/artifacts/random_forest_v2.pkl
```

## Compatibility Checks

| Check | Result |
|-------|--------|
| RF loader points to `random_forest_v2.pkl` | PASS |
| Runtime feature list exactly `RR`, `Rain7`, `RH_avg`, `Tavg` | PASS |
| Runtime feature count is `4` | PASS |
| `random_forest_v2.pkl.feature_names_in_` matches runtime feature list | PASS |
| `random_forest_v2.pkl.n_features_in_` is `4` | PASS |
| Gateway raw-weather path builds v2 features before prediction | PASS |
| Smoke RF prediction executes without sklearn shape/name mismatch | PASS |
| Legacy `random_forest.pkl` remains present | PASS |
| Prediction response schema unchanged | PASS |
| Frontend/auth/security/deployment/router files unchanged by this sprint | PASS |

## Validation Commands

```text
python -m py_compile backend/providers/models.py backend/providers/openmeteo_provider.py backend/services/prediction_gateway.py backend/services/metadata_service.py ml/feature_engineering/builder.py ml/predict/random_forest.py ml/predict/preprocess.py ml/service/predictor.py tests/test_weather_provider.py
```

Result: PASS

```text
pytest tests/test_weather_provider.py -k "FriV2FeatureEngineering or FriV2RandomForestCompatibility"
```

Result: 6 passed, 18 deselected

```text
python -c "from datetime import date; from backend.providers.models import RawWeatherData; from backend.services.prediction_gateway import predict_from_raw; w=RawWeatherData(tanggal=date(2026,1,15), rr=10.0, rh_avg=80.0, tavg=27.5, tmax=32.0, tmin=24.0, latitude=0.5, longitude=101.4, sumber='test'); h=[{'rr': float(i)} for i in range(1,8)]; r=predict_from_raw(w, history=h, model='rf', top_n=1); print(r['model'], r['fri'], r['tingkat_risiko'])"
```

Result:

```text
rf 42.8 Risiko Sedang
```

```text
python -c "from backend.app import app; print(app.title)"
```

Result:

```text
Flood Risk DSS API
```

## Observed Warnings And Non-RF Limitations

| Item | Status |
|------|--------|
| `pytest tests/test_weather_provider.py -k "FriV2FeatureEngineering or FriV2RandomForestCompatibility or realtime_success"` | The existing realtime endpoint test returned `401 Unauthorized` before reaching prediction. Authentication was intentionally not modified in this sprint. Direct gateway validation passed. |
| sklearn model load warning | `random_forest_v2.pkl` was serialized with sklearn `1.6.1` and validated here under sklearn `1.8.0`, producing `InconsistentVersionWarning`. Prediction still executed successfully. |
| LSTM path | `feature_list.json` is now v2 for RF migration. LSTM remains legacy/v1-feature based and was not migrated in this sprint. |

## Migration Summary

Sprint v2.5B completed the active RF backend migration to FRI v2. The runtime RF path now uses the four frozen FRI v2 features and the v2 model artifact without changing public prediction response shape or removing the legacy RF artifact.
