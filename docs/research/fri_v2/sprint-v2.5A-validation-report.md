# Sprint v2.5A Validation Report

## Objective

Migrate backend realtime feature engineering toward the frozen FRI v2 feature specification without replacing the model artifact, changing prediction output schema, modifying frontend, changing authentication/security, or altering deployment.

## Status

PASS WITH KNOWN COMPATIBILITY LIMITATION

The backend now has a validated FRI v2 feature-generation path that outputs exactly `RR`, `Rain7`, `RH_avg`, `Tavg`. It is intentionally not connected to `model.predict()` in this sprint because model migration is reserved for Sprint v2.5B.

## Files Modified

| File | Purpose |
|------|---------|
| `backend/providers/models.py` | Added optional `tavg` to `RawWeatherData` so provider-supplied daily mean temperature can flow through the backend. |
| `backend/providers/openmeteo_provider.py` | Requested and extracted Open-Meteo `temperature_2m_mean`; mapped it to `RawWeatherData.tavg`. |
| `ml/feature_engineering/builder.py` | Added `FEATURE_ORDER_V2` and `build_features_v2`; marked legacy v1 builder as deprecated for FRI v2 feature construction. |
| `backend/services/prediction_gateway.py` | Added `build_prediction_features_v2` to build the v2 feature vector without invoking prediction. Existing prediction path remains unchanged. |
| `backend/services/metadata_service.py` | Added FRI v2 feature-engineering metadata without changing model artifact metadata. |
| `tests/test_weather_provider.py` | Added validation tests for Open-Meteo mean temperature extraction and FRI v2 feature-vector construction. |

## Functions Modified Or Added

| Function / Class | File | Change |
|------------------|------|--------|
| `RawWeatherData` | `backend/providers/models.py` | Added optional `tavg` field. |
| `OpenMeteoProvider.get_current_weather` | `backend/providers/openmeteo_provider.py` | Requests `temperature_2m_mean` and stores it as `tavg`. |
| `OpenMeteoProvider.get_weather_history` | `backend/providers/openmeteo_provider.py` | Requests `temperature_2m_mean` for historical rows and stores it as `tavg`. |
| `build_features` | `ml/feature_engineering/builder.py` | Retained for v1 compatibility and marked deprecated for FRI v2 construction. |
| `build_features_v2` | `ml/feature_engineering/builder.py` | Added v2 builder producing exactly `RR`, `Rain7`, `RH_avg`, `Tavg`. |
| `_resolve_tavg` | `ml/feature_engineering/builder.py` | Added resolver that uses provider `tavg` when available and falls back to `(tmax + tmin) / 2` only for legacy non-provider inputs. |
| `predict_from_raw` | `backend/services/prediction_gateway.py` | Existing prediction flow remains v1-compatible; raw data now carries `tavg` but still calls legacy builder until v2.5B. |
| `build_prediction_features_v2` | `backend/services/prediction_gateway.py` | Added v2 feature construction seam without calling `prediksi` or `model.predict()`. |
| `get_model_info` | `backend/services/metadata_service.py` | Added `fri_v2_feature_engineering` metadata describing the v2 feature order and noting model artifact is not migrated in v2.5A. |

## Old Feature List

Current legacy v1 feature list retained for compatibility with `random_forest.pkl`:

```text
rr, rain3, rain7, rain14, rh_avg, temp_range, rainfall_anomaly, month, day_of_year
```

Legacy features are still present in compatibility code but are deprecated for FRI v2 feature-vector construction.

## New Feature List

FRI v2 feature vector:

```text
RR, Rain7, RH_avg, Tavg
```

Feature order is exactly:

```text
[
  RR,
  Rain7,
  RH_avg,
  Tavg
]
```

## Feature Engineering Flow

```text
Open-Meteo response
  |
  |-- precipitation_sum -> RawWeatherData.rr -> RR
  |-- relative_humidity_2m_mean -> RawWeatherData.rh_avg -> RH_avg
  |-- temperature_2m_mean -> RawWeatherData.tavg -> Tavg
  |
  v
RawWeatherData + historical rr values
  |
  v
backend.services.prediction_gateway.build_prediction_features_v2
  |
  v
ml.feature_engineering.builder.build_features_v2
  |
  v
[RR, Rain7, RH_avg, Tavg]
```

## Open-Meteo Mapping

| Open-Meteo Field | Backend Field | FRI v2 Feature | Notes |
|------------------|---------------|----------------|-------|
| `precipitation_sum` | `rr` | `RR` | Daily rainfall. |
| `precipitation_sum` history | historical `rr` series | `Rain7` | Rolling sum over latest 7 observations including current day. |
| `relative_humidity_2m_mean` | `rh_avg` | `RH_avg` | Daily average relative humidity. |
| `temperature_2m_mean` | `tavg` | `Tavg` | Daily mean temperature from Open-Meteo, not derived from max/min when available. |
| `temperature_2m_max` | `tmax` | None | Retained only for legacy compatibility. |
| `temperature_2m_min` | `tmin` | None | Retained only for legacy compatibility. |

## Rain7 Validation

Methodology:

```text
pd.Series(history_rr + [current_rr]).rolling(window=7, min_periods=1).sum().iloc[-1]
```

Validation example:

```text
history = [1, 2, 3, 4, 5, 6, 7]
current RR = 10
Rain7 = 2 + 3 + 4 + 5 + 6 + 7 + 10 = 37
```

This matches the training feature-engineering methodology: rolling window size 7, `min_periods=1`, current observation included.

## Validation Checklist

| Check | Result |
|-------|--------|
| Backend computes v2 feature vector with only `RR`, `Rain7`, `RH_avg`, `Tavg` | PASS |
| Feature order exactly `RR`, `Rain7`, `RH_avg`, `Tavg` | PASS |
| Rain7 rolling window = 7 | PASS |
| Rain7 uses `min_periods=1` methodology via existing `compute_rain7` | PASS |
| `Rain3` absent from v2 feature vector | PASS |
| `Rain14` absent from v2 feature vector | PASS |
| `TempRange` absent from v2 feature vector | PASS |
| `RainfallAnomaly` absent from v2 feature vector | PASS |
| `Month` absent from v2 feature vector | PASS |
| `DayOfYear` absent from v2 feature vector | PASS |
| Open-Meteo daily mean temperature extracted as `Tavg` | PASS |
| `random_forest.pkl` unchanged | PASS |
| `random_forest_v2.pkl` not used | PASS |
| Existing prediction service path not migrated to v2 model | PASS |
| Routers unchanged | PASS |
| API response schema unchanged | PASS |
| Authentication/security/rate limiting unchanged | PASS |

## Validation Commands

```text
python -m py_compile backend/providers/models.py backend/providers/openmeteo_provider.py backend/services/prediction_gateway.py backend/services/metadata_service.py ml/feature_engineering/builder.py tests/test_weather_provider.py
```

Result: PASS

```text
pytest tests/test_weather_provider.py -k "FriV2FeatureEngineering or get_current_weather_success or get_weather_incomplete_data"
```

Result: 5 passed

```text
python -c "from backend.app import app; print(app.title); from ml.feature_engineering.builder import build_features_v2; print(build_features_v2({'tanggal':'2026-01-15','rr':10,'rh_avg':80,'tavg':27.5,'tmax':32,'tmin':24}, history=[{'rr':i} for i in [1,2,3,4,5,6,7]]).to_dict('records')[0])"
```

Result:

```text
Flood Risk DSS API
{'RR': 10.0, 'Rain7': 37.0, 'RH_avg': 80.0, 'Tavg': 27.5}
```

## Migration Summary

Sprint v2.5A creates a safe feature-engineering migration seam. The backend can now construct the exact FRI v2 feature vector independently of model prediction. Legacy v1 feature generation remains available only because the current production model still requires it until Sprint v2.5B.

## Known Limitations

- The active prediction path still uses legacy `build_features` and `random_forest.pkl` until Sprint v2.5B.
- `random_forest_v2.pkl` is not loaded or used in this sprint.
- `ml/artifacts/feature_list.json` remains v1 because changing it before model migration would break current prediction.
- Manual and CSV inputs do not currently provide `Tavg`; `build_features_v2` falls back to `(tmax + tmin) / 2` for those legacy non-provider paths until their API contracts are explicitly migrated.
- LSTM remains v1-feature-based and is not part of this sprint.

## Compatibility Statement

This sprint intentionally does not connect v2 feature vectors to `model.predict()`. Sprint v2.5B may safely begin model migration using `build_prediction_features_v2` as the validated feature source.
