# Realtime Data Pipeline Full Audit - FRI v2

## Audit Status

Strict read-only audit completed. No backend, frontend, prediction, model, API, or artifact source file was modified by this audit. This document is the only intended output.

## Final Verdict

⚠ Pipeline Correct with Minor Issues

The authenticated realtime RF path correctly acquires Open-Meteo daily data, builds the FRI v2 feature vector `RR`, `Rain7`, `RH_avg`, `Tavg`, passes that vector to `random_forest_v2.pkl`, classifies risk, and returns a stable prediction response. The main minor issue is response serialization: `Rain7` and `Tavg` are used by the model but are not included in `/api/prediksi/realtime`, so frontend UI elements for `Akumulasi Hujan 7 Hari` and `Suhu Rata-rata` display `—`.

## 1. Pipeline Diagram

```text
DashboardScreen
  -> useRealtimePrediction(wilayah)
  -> fetchRealtimePrediction(wilayah, model="rf", top_n=5)
  -> GET /api/prediksi/realtime?wilayah=...&model=rf&top_n=5
  -> FastAPI middleware and rate limiter
  -> get_current_user()
  -> backend.routers.realtime.predict_realtime()
  -> OpenMeteoProvider.get_weather_history(wilayah, days=14)
  -> geocode(wilayah)
  -> requests.get(Open-Meteo Geocoding API)
  -> requests.get(Open-Meteo Forecast API daily fields)
  -> RawWeatherData[]
  -> weather = latest row
  -> preceding = all rows before latest
  -> prediction_gateway.predict_from_raw(weather, weather_history=preceding)
  -> build_prediction_features_v2(weather, history=[{"rr": ...}])
  -> build_features_v2(raw_data, history)
  -> compute_rain7(pd.Series(history_rr + current_rr))
  -> prediksi(features, model="rf")
  -> validate_input(features)
  -> get_feature_list()
  -> pd.DataFrame([features])[["RR", "Rain7", "RH_avg", "Tavg"]]
  -> predict_rf(df.iloc[[-1]])
  -> _load_model() -> random_forest_v2.pkl
  -> model.predict(df)
  -> classify_risk(fri)
  -> recommend(fri)
  -> explain_recommendation(...)
  -> get_mitigasi(risiko)
  -> router response dict
  -> frontend React Query data
  -> DashboardPanel / MapContainer history popup / ReportsPanel / AISupportPanel
```

## 2. Realtime Sequence Diagram

```text
User
  |
  v
Dashboard search / default wilayah
  |
  v
useRealtimePrediction(queryKey=["prediksi-realtime", wilayah, model], staleTime=5min)
  |
  v
fetchRealtimePrediction()
  |
  |-- getAuthorizationHeaders() from Supabase browser session
  |-- axios GET /api/prediksi/realtime
  v
FastAPI app
  |
  |-- LoggingMiddleware.dispatch()
  |-- CORS middleware
  |-- SecurityHeadersMiddleware.dispatch()
  |-- SlowAPIMiddleware / @limiter.limit("60/minute")
  |-- get_current_user()
  v
predict_realtime()
  |
  |-- _provider.get_weather_history(wilayah, days=14)
  |-- weather = history_data[-1]
  |-- preceding = history_data[:-1]
  |-- predict_from_raw(weather, weather_history=preceding, model, top_n)
  |-- response serializer inline dict
  v
JSON response
  |
  v
React Query cache
  |
  |-- DashboardPanel(data)
  |-- AISupportPanel(data)
  |-- ReportsPanel(data)
  |-- useEffect upsert(history entry)
  v
MapContainer(history) -> RegionPopup(history entry)
```

## 3. Open-Meteo Data Flow

### Request Behavior

The backend requests Open-Meteo on every authenticated realtime request that reaches the router body.

Evidence:

| Layer | File | Function | Finding |
|---|---|---|---|
| Router | `backend/routers/realtime.py:39-41` | `predict_realtime()` | Calls `_provider.get_weather_history(wilayah, days=14)` inside every request. |
| Provider | `backend/providers/openmeteo_provider.py:91-151` | `get_weather_history()` | Calls `geocode(wilayah)`, then `requests.get(WEATHER_URL, ...)`. |
| Geocoding | `backend/providers/geocoding.py:20-49` | `geocode()` | Calls `requests.get(GEOCODING_URL, ...)`. |

### Requested Daily Fields

`OpenMeteoProvider.get_weather_history()` requests:

```text
precipitation_sum,
relative_humidity_2m_mean,
temperature_2m_mean,
temperature_2m_max,
temperature_2m_min
```

It sends:

| Parameter | Value |
|---|---|
| `latitude` | From Open-Meteo geocoding result |
| `longitude` | From Open-Meteo geocoding result |
| `start_date` | `today - timedelta(days=days - 1)` |
| `end_date` | `today` |
| `timezone` | `Asia/Jakarta` |

For realtime, `days=14`, so 14 calendar dates are requested inclusive of today.

### Cache Analysis

No realtime weather cache exists.

| Cache Type | Exists? | Details |
|---|---:|---|
| Open-Meteo forecast response cache | No | No cache object, TTL, or persisted weather store was found. |
| Geocoding cache | No | `geocode()` calls `requests.get()` every time. |
| Prediction result cache | No | `predict_realtime()` calls provider and prediction gateway per request. |
| Frontend query cache | Yes | React Query uses `staleTime: 5 * 60 * 1000` in `useRealtimePrediction()`. This caches browser-side query data for UI refetch behavior only; it is not a backend cache. |
| RF model cache | Yes | Module global `_model` in `ml/predict/random_forest.py`; no TTL; lazy singleton until process restart. |
| Feature list cache | Yes | Module global `_feature_list` in `ml/predict/preprocess.py`; no TTL; lazy singleton until process restart. |
| Supabase/config cache | Yes | `lru_cache` in unrelated config/Supabase helper paths; not realtime weather caching. |

Cache TTL/location/key/invalidation for backend weather data: not applicable because no backend weather cache exists.

## 4. Feature Flow

| Field | Source | Transformation | Exists Before Prediction? | Passed To RF? | Included In API Response? | Frontend Destination |
|---|---|---|---:|---:|---:|---|
| `RR` | Open-Meteo `daily.precipitation_sum[-1]` -> `RawWeatherData.rr` | `build_features_v2()` casts to float and emits `RR` | Yes | Yes | As `cuaca.rr`, not as `RR` | Curah Hujan cards, report, popup history |
| `Rain7` | Current `RR` plus historical `rr` from preceding records | `compute_rain7(pd.Series(history_rr + [RR])).iloc[-1]`; rolling sum window 7, `min_periods=1` | Yes, in feature builder output | Yes | No | UI attempts lookup, receives `null`, displays `—` |
| `RH_avg` | Open-Meteo `daily.relative_humidity_2m_mean[-1]` -> `RawWeatherData.rh_avg` | `build_features_v2()` casts to float and emits `RH_avg` | Yes | Yes | As `cuaca.rh_avg`, not as `RH_avg` | Kelembapan cards, report, popup history |
| `Tavg` | Open-Meteo `daily.temperature_2m_mean[-1]` -> `RawWeatherData.tavg` | `_resolve_tavg()` uses `raw_data["tavg"]` when present; fallback `(tmax+tmin)/2` only if missing | Yes | Yes | No | UI attempts lookup, receives `null`, displays `—` |
| `FRI` | RF v2 model prediction | `RandomForestRegressor.predict(df)[0]`, then rounded to 2 decimals in `prediksi()` | After model prediction | Output, not input | Yes as `fri` | Gauge, cards, reports, popup, AI evidence |
| `Risk` | `classify_risk(fri)` | Thresholds: `<=33 Rendah`, `<=66 Sedang`, else `Tinggi`; serialized as `Risiko <level>` | After FRI | Output, not input | Yes as `tingkat_risiko` | Gauge, cards, reports, popup, AI evidence |

## 5. Prediction Flow

### Backend Function Chain

| Step | File | Function | Role |
|---:|---|---|---|
| 1 | `backend/routers/realtime.py` | `predict_realtime()` | HTTP endpoint, auth-protected, rate-limited. |
| 2 | `backend/providers/openmeteo_provider.py` | `OpenMeteoProvider.get_weather_history()` | Gets geocoded coordinates and daily Open-Meteo weather. |
| 3 | `backend/providers/geocoding.py` | `geocode()` | Resolves `wilayah` to latitude/longitude. |
| 4 | `backend/providers/models.py` | `RawWeatherData` | Data carrier for daily weather values. |
| 5 | `backend/services/prediction_gateway.py` | `predict_from_raw()` | Converts `weather_history` to rainfall history and invokes v2 feature seam. |
| 6 | `backend/services/prediction_gateway.py` | `build_prediction_features_v2()` | Builds raw dict with `rr`, `rh_avg`, `tavg`, `tmax`, `tmin`. |
| 7 | `ml/feature_engineering/builder.py` | `build_features_v2()` | Emits exact FRI v2 features `RR`, `Rain7`, `RH_avg`, `Tavg`. |
| 8 | `ml/feature_engineering/rainfall.py` | `compute_rain7()` | Calculates rolling 7-day rainfall sum. |
| 9 | `ml/service/predictor.py` | `prediksi()` | Validates, orders dataframe, predicts FRI, creates recommendations and mitigation. |
| 10 | `ml/predict/preprocess.py` | `validate_input()` | Verifies features from `feature_list.json` exist. |
| 11 | `ml/predict/preprocess.py` | `get_feature_list()` | Loads cached `ml/artifacts/feature_list.json`. |
| 12 | `ml/predict/random_forest.py` | `predict_rf()` | Calls active RF model. |
| 13 | `ml/predict/random_forest.py` | `_load_model()` | Lazy-loads `ml/artifacts/random_forest_v2.pkl`. |
| 14 | `ml/predict/risk.py` | `classify_risk()` | Converts FRI to risk class. |
| 15 | `ml/recommendation/recommender.py` | `recommend()` | Creates ranked commodity recommendations. |
| 16 | `ml/recommendation/explain.py` | `explain_recommendation()` | Serializes recommendation explanation fields. |
| 17 | `ml/recommendation/mitigation.py` | `get_mitigasi()` | Serializes mitigation actions. |
| 18 | `backend/routers/realtime.py` | inline return dict | Response serializer. |

### Scientific Validation Evidence

RF v2 receives exactly `RR`, `Rain7`, `RH_avg`, `Tavg` during realtime prediction.

Evidence:

| Evidence | Location / Probe |
|---|---|
| Gateway imports v2 builder | `backend/services/prediction_gateway.py:12` imports `build_features_v2`. |
| Realtime raw path calls v2 seam | `predict_from_raw()` calls `build_prediction_features_v2()` at `backend/services/prediction_gateway.py:41`. |
| V2 builder output order | `FEATURE_ORDER_V2 = ["RR", "Rain7", "RH_avg", "Tavg"]` in `ml/feature_engineering/builder.py:24`. |
| Runtime feature list | `ml/artifacts/feature_list.json` is consumed by `get_feature_list()` and expected to contain the v2 feature list. |
| Predictor dataframe ordering | `pd.DataFrame(rows)[features]` in `ml/service/predictor.py:56-57`. |
| Active RF artifact | `_load_model()` loads `random_forest_v2.pkl` in `ml/predict/random_forest.py:18`. |
| Read-only timing probe feature row | `{"RR": 15.9, "Rain7": 69.6, "RH_avg": 90.0, "Tavg": 27.0}`. |

## 6. Rain7 Investigation

| Question | Finding |
|---|---|
| Where is Rain7 computed? | `ml/feature_engineering/builder.py:93-97` calls `compute_rain7()` on `history_rr + current_rr`. |
| When is Rain7 computed? | During `build_features_v2()` before `prediksi()` and before RF prediction. |
| Does Rain7 exist before prediction? | Yes. It exists in the feature dict returned by `build_prediction_features_v2()`. |
| Does Rain7 exist after prediction? | Internally, yes only as pre-prediction input; `prediksi()` result does not include input features. |
| Is Rain7 included in API response? | No. The realtime router response does not serialize `Rain7`, `rain7`, `features`, or `fitur`. |
| Why not? | `backend/routers/realtime.py:65-88` manually constructs the response and includes only `cuaca.rr`, `cuaca.rh_avg`, `cuaca.tmax`, `cuaca.tmin`, coordinates, prediction output, recommendations, and mitigation. It discards the v2 feature dict returned to the model. |

Current Rain7 methodology:

```text
rr_values = [float(h["rr"]) for h in history] + [rr]
rain7 = compute_rain7(pd.Series(rr_values)).iloc[-1]
```

With 13 preceding records, the final rolling value uses only D-6 through D0. D-13 through D-7 are downloaded and processed but do not affect final `Rain7`.

## 7. Tavg Investigation

| Question | Finding |
|---|---|
| Where does Tavg originate? | Open-Meteo daily field `temperature_2m_mean`. |
| Open-Meteo daily or hourly? | Daily. No hourly request exists in the realtime path. |
| Is Tavg calculated? | For Open-Meteo realtime, no; it is read from `temperature_2m_mean`. `_resolve_tavg()` falls back to `(tmax+tmin)/2` only when `tavg` is missing. |
| Is Tavg passed to RF? | Yes. It is emitted as `Tavg` by `build_features_v2()` and ordered into the RF dataframe. |
| Is Tavg returned to frontend? | No. `RawWeatherData.tavg` is not included in the realtime router's `cuaca` object or top-level response. |
| Why missing from UI? | Backend serializer omission. Frontend mapping checks `tavg`/`Tavg`, but the actual response contains neither. |

## 8. API Response Schema

The exact successful `/api/prediksi/realtime` response is an inline dict from `backend/routers/realtime.py:65-88`.

| Field | Type | Description | Origin | Used By Frontend? | Used By Model? |
|---|---|---|---|---:|---:|
| `status` | string | Fixed success status, currently `berhasil`. | Router serializer | Not materially rendered | No |
| `wilayah` | string | Requested region name. | Query param | Yes, header/history/report/AI | No |
| `sumber_data` | string | Weather source, typically `Open-Meteo`. | `weather.sumber` | Yes, report/AI evidence text | No |
| `forecast_date` | string date | Latest weather record date. | `weather.tanggal.isoformat()` | Yes, panel/report/AI | No |
| `updated_at` | string datetime | Backend response timestamp. | `datetime.now(WIB).isoformat()` | Yes, panel context | No |
| `waktu_prediksi` | string datetime | Backend prediction timestamp. | Same `now.isoformat()` | Yes, history timestamp/popup | No |
| `model` | string | Selected model, usually `rf`. | `result["model"]` | Yes, report | Controls model branch before response |
| `versi_model` | string | Static string currently `1.0`. | Router literal | Yes, report | No |
| `cuaca` | object | Current/latest weather object. | Router serializer from `weather` | Yes | Partial source fields were model inputs before serialization |
| `cuaca.tanggal` | string date | Weather record date. | `weather.tanggal.isoformat()` | Fallback date | No |
| `cuaca.rr` | number | Daily rainfall. | `weather.rr` from Open-Meteo `precipitation_sum` | Yes | Source for `RR` |
| `cuaca.rh_avg` | number | Daily average humidity. | `weather.rh_avg` from Open-Meteo `relative_humidity_2m_mean` | Yes | Source for `RH_avg` |
| `cuaca.tmax` | number | Daily max temperature. | `weather.tmax` from Open-Meteo `temperature_2m_max` | Mostly ignored after UI alignment; AI prompt still uses it | No for RF v2 realtime if `tavg` exists |
| `cuaca.tmin` | number | Daily min temperature. | `weather.tmin` from Open-Meteo `temperature_2m_min` | Mostly ignored after UI alignment; AI prompt still uses it | No for RF v2 realtime if `tavg` exists |
| `cuaca.latitude` | number | Latitude. | Geocoding result | Yes, map marker | No |
| `cuaca.longitude` | number | Longitude. | Geocoding result | Yes, map marker | No |
| `hari_historis` | number | Count of preceding records. | `len(preceding)` | Typed but not prominently rendered | No |
| `fri` | number | Predicted FRI rounded to 2 decimals. | `prediksi()` result | Yes, all major views | No, output |
| `tingkat_risiko` | string | Risk label prefixed with `Risiko`. | `classify_risk()` via `prediksi()` | Yes, all major views | No, output |
| `rekomendasi` | array | Commodity recommendations with explanations. | `recommend()` + `explain_recommendation()` | Yes, panel/report/AI context | No |
| `rekomendasi[].komoditas` | string | Commodity display name. | Commodity profile | Yes | No |
| `rekomendasi[].komoditas_id` | string | Commodity identifier. | Commodity profile | Yes, accordion key | No |
| `rekomendasi[].skor` | number | Recommendation score. | Recommendation scorer | Yes | No |
| `rekomendasi[].tingkat_keyakinan` | number | Confidence-like value, rounded in explanation layer. | `explain_recommendation()` | Yes | No |
| `rekomendasi[].tingkat_risiko` | string | Risk context for recommendation. | `explain_recommendation()` | Yes | No |
| `rekomendasi[].alasan` | string[] | Explanation reasons. | `explain_recommendation()` | Yes | No |
| `rekomendasi[].ringkasan` | string | Summary explanation. | `explain_recommendation()` | Yes | No |
| `mitigasi` | array | Mitigation actions. | `get_mitigasi()` | Yes | No |
| `mitigasi[].prioritas` | number | Action priority. | Mitigation rules | Yes | No |
| `mitigasi[].kategori` | string | Action category. | Mitigation rule mapping | Yes | No |
| `mitigasi[].tindakan` | string | Action description. | Mitigation rules | Yes | No |

Fields not in the actual backend response despite frontend optional typings:

```text
RR, Rain7, rain7, RH_avg, Tavg, tavg, features, fitur, cuaca.RR, cuaca.Rain7, cuaca.rain7, cuaca.RH_avg, cuaca.Tavg, cuaca.tavg
```

## 9. Frontend Mapping

### Request Layer

| File | Function | Behavior |
|---|---|---|
| `apps/web/hooks/use-realtime-prediction.ts` | `useRealtimePrediction()` | React Query key `['prediksi-realtime', wilayah, model]`, calls `fetchRealtimePrediction()`, `staleTime` 5 minutes, `retry: 1`. |
| `apps/web/services/prediction.ts` | `fetchRealtimePrediction()` | Sends `GET /api/prediksi/realtime` with query params and Authorization header. |
| `apps/web/services/authenticated-fetch.ts` | `getAuthorizationHeaders()` | Reads Supabase browser session and attaches `Authorization: Bearer <token>` if available. |

### Display Mapper

`apps/web/lib/realtime-presentation.ts` maps values by scanning top-level response, `cuaca`, `features`, and `fitur`:

| Display Value | Lookup Keys | Actual Backend Match | UI Result |
|---|---|---|---|
| `rainfall` | `rr`, `RR` | `cuaca.rr` | Numeric value |
| `rain7` | `rain7`, `Rain7` | None | `null` -> `—` |
| `humidity` | `rh_avg`, `RH_avg` | `cuaca.rh_avg` | Numeric value |
| `tavg` | `tavg`, `Tavg` | None | `null` -> `—` |

### Consumed Response Fields

| Field | Consumed By | UI Element |
|---|---|---|
| `wilayah` | `DashboardScreen`, `DashboardPanel`, `ReportsPanel`, `AISupportPanel` | Panel header, report, AI context, history key |
| `forecast_date` / `cuaca.tanggal` | `DashboardPanel`, `ReportsPanel`, `AISupportPanel` | Forecast date labels |
| `updated_at` | `DashboardPanel`, `AnalyticsPanel` | Update time |
| `waktu_prediksi` | `DashboardScreen` -> history | Popup prediction timestamp |
| `fri` | Dashboard/analytics/report/popup/AI | Gauge, risk card, report, popup |
| `tingkat_risiko` | Dashboard/analytics/report/popup/AI | Risk badge and text |
| `cuaca.rr` | Display mapper | Curah Hujan |
| `cuaca.rh_avg` | Display mapper | Kelembapan |
| `cuaca.latitude` / `cuaca.longitude` | `DashboardScreen`, `MapContainer`, reports | Marker position, coordinates |
| `cuaca.tmax` / `cuaca.tmin` | `llm.ts` AI prompt context only | AI prompt still says `Suhu tmin-tmax`; not used by visual FRI v2 display mapper |
| `rekomendasi` | Dashboard/report/AI | Recommendation chart, accordion, report, AI context |
| `mitigasi` | Dashboard/report/AI | Mitigation timeline/report/AI context |
| `model`, `versi_model` | Reports | Report metadata |
| `sumber_data` | Reports/API evidence | Source label |

### Ignored Or Mostly Unused Fields

| Field | Status |
|---|---|
| `status` | Typed but not materially displayed. |
| `hari_historis` | Typed but not prominently displayed in current dashboard components. |
| Optional `features` / `fitur` | Frontend mapper supports them, but backend does not return them. |
| Optional `Rain7` / `Tavg` keys | Frontend mapper supports them, but backend does not return them. |

## 10. Single Source Of Truth

The current prediction result is fetched once by `useRealtimePrediction(wilayah)` and propagated through `DashboardScreen`.

| UI Area | Data Origin | Multiple Backend Requests? |
|---|---|---:|
| Left panel / gauge | Direct `data` from React Query | No |
| Reports panel | Same `data` prop | No |
| AI evidence panel | Same `data` prop | No |
| AI chat backend request | Sends separate `/api/ai/chat`, but prediction context is derived from same frontend `data` object | Not a prediction request |
| Popup | `DashboardScreen` stores derived `HistoryEntry` from same `data`, then `MapContainer` renders history | No new prediction request |
| Map marker | Same history entry and current `data` coordinates | No |

Conclusion: one realtime backend response is the source for current panel, gauge, report, AI evidence, and popup history. Popup values are a persisted derived snapshot, not a separate realtime fetch.

## 11. Realtime Consistency

| Value | Panel | Gauge | Popup | Report | AI Evidence | Consistency |
|---|---:|---:|---:|---:|---:|---|
| FRI | `data.fri.toFixed(1)` | `data.fri.toFixed(1)` | history `fri` from `data.fri` | `data.fri.toFixed(1)` | `data.fri.toFixed(1)` | Consistent except formatting precision is one decimal in UI vs two decimals in raw JSON. |
| Risk | `data.tingkat_risiko` | `data.tingkat_risiko` | history `tingkatRisiko` from `data.tingkat_risiko` | `data.tingkat_risiko` | `data.tingkat_risiko` | Consistent. |
| Curah Hujan | mapper from `cuaca.rr` | mapper from `cuaca.rr` | history `rr` from mapper | mapper from `cuaca.rr` | mapper from `cuaca.rr` | Consistent. |
| Kelembapan | mapper from `cuaca.rh_avg` | mapper from `cuaca.rh_avg` | history `rh_avg` from mapper | mapper from `cuaca.rh_avg` | mapper from `cuaca.rh_avg` | Consistent. |
| Akumulasi Hujan 7 Hari | `—` if missing | `—` if missing | `—` because history lacks value | `—` if missing | `—` if missing | Consistent, but missing. |
| Suhu Rata-rata | `—` if missing | `—` if missing | `—` because history lacks value | `—` if missing | `—` if missing | Consistent, but missing. |

## 12. Missing Field Analysis

### Why `Akumulasi Hujan 7 Hari` Shows `—`

Root cause: backend response serialization omission.

Detailed chain:

```text
Open-Meteo precipitation_sum history exists
  -> RawWeatherData.rr history exists
  -> build_features_v2 computes Rain7
  -> RF v2 receives Rain7
  -> prediksi() returns only model/fri/risk/rekomendasi/mitigasi
  -> realtime router manually serializes response
  -> response contains cuaca.rr and cuaca.rh_avg but not Rain7
  -> frontend mapper cannot find rain7/Rain7 in root, cuaca, features, or fitur
  -> formatMm(null) returns "—"
```

Potential causes assessed:

| Possible Cause | Result |
|---|---|
| Backend not computing Rain7 | False. It is computed before RF. |
| Serializer not returning Rain7 | True. Router return dict omits it. |
| DTO/response model filtering | Not applicable. Endpoint returns inline dict, not a Pydantic response model. |
| Naming mismatch | Secondary. Frontend supports `rain7` and `Rain7`, but backend returns neither. |
| Frontend mapping bug | False for current contract; mapper cannot display a field that is absent. |

### Why `Suhu Rata-rata` Shows `—`

Root cause: backend response serialization omission.

Detailed chain:

```text
Open-Meteo temperature_2m_mean exists
  -> RawWeatherData.tavg exists
  -> build_prediction_features_v2 includes raw_data["tavg"]
  -> build_features_v2 emits Tavg
  -> RF v2 receives Tavg
  -> realtime router serializes tmax/tmin but not tavg
  -> frontend mapper cannot find tavg/Tavg
  -> formatCelsius(null) returns "—"
```

Potential causes assessed:

| Possible Cause | Result |
|---|---|
| Open-Meteo hourly vs daily mismatch | False. Backend requests daily `temperature_2m_mean`. |
| Backend not obtaining Tavg | False. Provider maps `temperature_2m_mean` to `RawWeatherData.tavg`. |
| RF not receiving Tavg | False. V2 feature row includes `Tavg`. |
| API response omits Tavg | True. `cuaca` includes only `tmax` and `tmin`. |
| Frontend naming mismatch | Secondary. Frontend supports `tavg` and `Tavg`, but backend returns neither. |

## 13. Prediction Stability Analysis

FRI, humidity, and temperature may change within minutes for the following reasons:

| Cause | Applies? | Explanation |
|---|---:|---|
| Backend weather cache absent | Yes | Every backend realtime request that bypasses frontend cache calls geocoding and Open-Meteo again. If Open-Meteo changes data, backend uses new values. |
| Open-Meteo forecast refresh | Yes | The endpoint uses `/v1/forecast` daily aggregates, including today. Today's `precipitation_sum`, `relative_humidity_2m_mean`, and `temperature_2m_mean` can be forecast/nowcast values that Open-Meteo updates. |
| Daily aggregation for today | Yes | The current day aggregate can change during the day as forecast data is refreshed. |
| Hourly model | No evidence | The backend does not request hourly fields in realtime prediction. |
| RF stochasticity | No | RF prediction is deterministic for the same input and loaded artifact. |
| Feature engineering randomness | No | `build_features_v2()` is deterministic. |
| Frontend React Query cache | Partially | Browser-side `staleTime=5min` can prevent a refetch within 5 minutes for the same query key, but manual refetch or cache invalidation can still request again. Different browser sessions/users bypass this cache. |
| Geocoding variation | Possible but less likely | No backend geocoding cache; repeated geocoding could theoretically return changed coordinates if provider data changes. |

Conclusion: short-interval changes are most likely caused by live Open-Meteo forecast/daily aggregate refreshes combined with no backend weather cache. They are not caused by RF randomness.

## 14. Performance

Read-only timing probe was run directly against current code for `Pekanbaru`.

### Measured Results

| Stage | Measurement | Notes |
|---|---:|---|
| Open-Meteo provider total | `1581.57 ms` | Includes geocoding and forecast requests through `get_weather_history('Pekanbaru', days=14)`. |
| Returned history records | `14` | Latest row used as current weather; 13 rows used as preceding history. |
| Feature engineering cold probe | `14.9009 ms` | `build_prediction_features_v2()` including pandas object creation. |
| Feature engineering warm probe | `1.5054 ms` | Same process after warm-up. |
| Prediction total cold probe | `2012.7004 ms` | Includes feature build, RF artifact lazy load, sklearn unpickle, recommendation profile/rule lazy loads. |
| Prediction total warm probe | `26.3067 ms` | Same process after RF and knowledge files are loaded. |
| JSON serialization | `0.0853 ms` | `json.dumps()` of router-equivalent response, payload `3328` bytes. |

Measured feature row:

```json
{"RR": 15.9, "Rain7": 69.6, "RH_avg": 90.0, "Tavg": 27.0}
```

Measured prediction output:

```text
fri = 61.25
tingkat_risiko = Risiko Sedang
```

### Frontend Render Timing

No browser instrumentation was added because this audit is read-only and source modification was forbidden. Static trace shows frontend rendering is client-side React rendering from a single React Query result. Accurate render timing would require browser performance instrumentation or automated browser profiling, which was outside the no-code-modification constraint.

## 15. Code Modification Check

Audit rule verification:

| Area | Modified? | Evidence |
|---|---:|---|
| Backend source | No | Only read via file inspection and read-only timing probes. |
| Frontend source | No | Only read via file inspection. |
| Prediction source | No | Only imported and executed for read-only timing probes. |
| Random Forest artifact | No | Only loaded for prediction timing; no write operation. |
| API | No | No router/schema/service edits. |
| Generated output | Yes | This audit report only: `docs/research/fri_v2/realtime_data_pipeline_full_audit.md`. |

## 16. Root Cause Analysis

### Primary Root Cause

`Rain7` and `Tavg` are internal model inputs but not public realtime response fields.

The response serializer in `backend/routers/realtime.py` returns this `cuaca` object:

```json
{
  "tanggal": "...",
  "rr": 0,
  "rh_avg": 0,
  "tmax": 0,
  "tmin": 0,
  "latitude": 0,
  "longitude": 0
}
```

It does not include:

```text
Rain7, rain7, Tavg, tavg, features, fitur
```

### Secondary Root Causes

| Issue | Impact |
|---|---|
| Response schema still exposes legacy `tmax`/`tmin` but not FRI v2 `Tavg` | Frontend cannot display average temperature despite RF using it. |
| `hari_historis=13` remains from v1 14-day window | Scientifically harmless but over-fetches data for FRI v2. |
| `versi_model` remains static `1.0` | Metadata does not clearly communicate RF v2 state. |
| AI prompt knowledge still mentions 3/7/14-day accumulation and uses `tmin-tmax` context | Visual UI is aligned, but LLM context text is not fully FRI v2-aligned. |
| `model=lstm` remains accepted by query parameter | Non-RF path is outside RF v2 readiness and may not be compatible with v2 feature list. |

## 17. Recommendations

No changes were made during this audit. Recommended follow-up actions:

1. Add `Rain7` and `Tavg` to the realtime API response in a dedicated backend/API sprint, preferably under a clear `features` or `cuaca` extension contract.
2. Keep frontend display labels public-facing and avoid exposing internal names directly.
3. Decide whether to reduce realtime `days=14` to `days=7` or keep it as operational buffer; FRI v2 only needs 6 preceding rainfall records plus current day.
4. Consider a short backend weather cache if minute-to-minute visual stability is preferred over immediate Open-Meteo refreshes. Define TTL, cache key `(wilayah, date/window)`, and invalidation explicitly.
5. Align `versi_model` metadata with RF v2 in a backend metadata/API sprint.
6. Review or constrain `model=lstm` on realtime endpoint if LSTM is not migrated to the v2 feature contract.
7. Update AI prompt context to use FRI v2 terminology once backend response includes `Rain7` and `Tavg`.

## 18. Conclusion

The realtime RF v2 prediction pipeline is scientifically and technically connected end-to-end for model inference. Open-Meteo daily fields are acquired, `Rain7` and `Tavg` are constructed or sourced before prediction, and RF v2 receives the correct four-feature vector. The observed UI `—` values are not a model or feature-engineering failure; they are caused by missing response fields in the realtime API serializer.
