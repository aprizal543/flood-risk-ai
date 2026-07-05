# Sprint v2.5C Performance Report

## Objective

Measure backend startup, Open-Meteo provider latency, model inference latency, gateway prediction latency, and end-to-end realtime request latency after the FRI v2 migration.

## Environment

| Item | Value |
|------|-------|
| Platform | Windows / PowerShell environment |
| App execution | FastAPI `TestClient` and direct service probes |
| Date | 2026-07-05 |
| Active RF artifact | `ml/artifacts/random_forest_v2.pkl` |
| Active RF features | `RR`, `Rain7`, `RH_avg`, `Tavg` |

## Metrics

| Metric | Runs | Average | Minimum | Maximum | Notes |
|--------|------|---------|---------|---------|-------|
| Backend startup/import | 3 | 1719.97 ms | 1695.46 ms | 1750.05 ms | Fresh Python process importing `backend.app`. |
| Real Open-Meteo history request | 3 | 1591.58 ms | 1545.68 ms | 1626.38 ms | `OpenMeteoProvider.get_weather_history("Pekanbaru", days=14)`; all 3 returned 14 rows. |
| Warm RF model inference | 10 | 26.24 ms | 24.06 ms | 35.21 ms | Direct `predict_rf()` with v2 dataframe. |
| Gateway prediction | 10 | 27.11 ms | 25.83 ms | 28.72 ms | `predict_from_raw()` with mocked weather/history, RF model warm. |
| Mocked realtime endpoint | 10 | 42.56 ms | 35.79 ms | 53.41 ms | Authenticated `GET /api/prediksi/realtime` with mocked provider, RF model warm. |

## Open-Meteo Validation

Result:

```text
[('ok', 14), ('ok', 14), ('ok', 14)]
```

All measured Open-Meteo calls succeeded and returned the expected 14-row history.

## Realtime Endpoint Validation

Mocked realtime endpoint status codes:

```text
[200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
```

## Observations

| Observation | Impact |
|-------------|--------|
| RF inference is stable under warm model cache. | Low latency and suitable for realtime endpoint use. |
| Open-Meteo dominates real end-to-end latency. | External network latency is the main runtime cost. |
| First model load emits sklearn version warnings. | No measured prediction failure, but warning should be tracked for production reproducibility. |

## Performance Assessment

Performance status: PASS

The backend meets expected latency for local/TestClient validation. Production latency will primarily depend on Open-Meteo and geocoding network calls.
