# Open-Meteo Request Verification - FRI v2

## Audit Status

Strict read-only audit completed. No backend, frontend, prediction, model, API, configuration, or artifact file was modified. This document is the only intended output.

## Final Verdict

✅ Backend Open-Meteo request is scientifically correct

The backend realtime path uses Open-Meteo Forecast API daily `precipitation_sum` as the source of `RR`. The observed discrepancy is caused by comparing different Open-Meteo daily variables: backend uses `precipitation_sum`, while the manual value `Rain Sum = 3 mm` matches Open-Meteo `rain_sum` for the same backend coordinates, date range, timezone, and automatic weather model.

## 1. Complete Pipeline Diagram

```text
Dashboard
  -> apps/web/hooks/use-realtime-prediction.ts
  -> apps/web/services/prediction.ts
  -> GET /api/prediksi/realtime?wilayah=Pekanbaru&model=rf&top_n=5
  -> backend/routers/realtime.py::predict_realtime()
  -> _provider.get_weather_history(wilayah, days=14)
  -> backend/providers/openmeteo_provider.py::OpenMeteoProvider.get_weather_history()
  -> backend/providers/geocoding.py::geocode(wilayah)
  -> GET https://geocoding-api.open-meteo.com/v1/search?name=Pekanbaru&count=1
  -> GeoLocation(latitude=0.51667, longitude=101.44167, name=Pekanbaru)
  -> GET https://api.open-meteo.com/v1/forecast?...daily=precipitation_sum,...
  -> RawWeatherData[]
  -> weather = history_data[-1]
  -> weather.rr = daily.precipitation_sum[-1]
  -> prediction_gateway.predict_from_raw()
  -> build_features_v2()
  -> RF v2 prediction
  -> response.cuaca.rr
```

## 2. Open-Meteo Request Locations

Source search found only these backend Open-Meteo HTTP requests:

| API Family | Endpoint | File | Function | Used By Realtime Prediction? |
|---|---|---|---:|
| Geocoding API | `https://geocoding-api.open-meteo.com/v1/search` | `backend/providers/geocoding.py` | `geocode()` | Yes |
| Forecast API | `https://api.open-meteo.com/v1/forecast` | `backend/providers/openmeteo_provider.py` | `get_weather_history()` | Yes |
| Forecast API | `https://api.open-meteo.com/v1/forecast` | `backend/providers/openmeteo_provider.py` | `get_current_weather()` | No for `/api/prediksi/realtime`; used by provider endpoint |

No Archive API, Historical Weather API, Marine API, Hourly API request, or cache-backed request exists in the backend realtime prediction path.

## 3. Exact Backend Open-Meteo URL

Generated read-only on 2026-07-05 using the same backend geocoding and request construction logic.

### Geocoding URL

```text
https://geocoding-api.open-meteo.com/v1/search?name=Pekanbaru&count=1
```

Geocoding result used by backend:

| Field | Value |
|---|---:|
| Name | Pekanbaru |
| Latitude | `0.51667` |
| Longitude | `101.44167` |

### Forecast URL For Realtime Prediction

Directly executable in browser:

```text
https://api.open-meteo.com/v1/forecast?latitude=0.51667&longitude=101.44167&daily=precipitation_sum%2Crelative_humidity_2m_mean%2Ctemperature_2m_mean%2Ctemperature_2m_max%2Ctemperature_2m_min&start_date=2026-06-22&end_date=2026-07-05&timezone=Asia%2FJakarta
```

## 4. Complete Query Parameters

### Realtime Forecast Request

| Parameter | Backend Value |
|---|---|
| HTTP method | `GET` |
| Base URL | `https://api.open-meteo.com/v1/forecast` |
| `latitude` | `0.51667` |
| `longitude` | `101.44167` |
| `daily` | `precipitation_sum,relative_humidity_2m_mean,temperature_2m_mean,temperature_2m_max,temperature_2m_min` |
| `start_date` | `2026-06-22` |
| `end_date` | `2026-07-05` |
| `timezone` | `Asia/Jakarta` |
| `forecast_days` | Not sent |
| `past_days` | Not sent |
| `hourly` | Not sent |
| `models` / weather model | Not sent |

### Provider Current Weather Request

This request exists but is not used by `/api/prediksi/realtime`.

| Parameter | Backend Value |
|---|---|
| HTTP method | `GET` |
| Base URL | `https://api.open-meteo.com/v1/forecast` |
| `latitude` | Geocoded latitude |
| `longitude` | Geocoded longitude |
| `daily` | `precipitation_sum,relative_humidity_2m_mean,temperature_2m_mean,temperature_2m_max,temperature_2m_min` |
| `start_date` | `today - 1 day` |
| `end_date` | `today` |
| `timezone` | `Asia/Jakarta` |
| `forecast_days` | Not sent |
| `past_days` | Not sent |
| `hourly` | Not sent |
| `models` / weather model | Not sent |

### Geocoding Request

| Parameter | Backend Value |
|---|---|
| HTTP method | `GET` |
| Base URL | `https://geocoding-api.open-meteo.com/v1/search` |
| `name` | Requested `wilayah`, e.g. `Pekanbaru` |
| `count` | `1` |

## 5. Variable Mapping

| FRI v2 Variable | Open-Meteo Source | Backend Field | Transformation | Final Destination |
|---|---|---|---|---|
| `RR` | `daily.precipitation_sum` latest date | `RawWeatherData.rr` | `float(rr)` | `build_features_v2()` emits `RR`; response serializes as `cuaca.rr` |
| `RH_avg` | `daily.relative_humidity_2m_mean` latest date | `RawWeatherData.rh_avg` | `float(rh)` | `build_features_v2()` emits `RH_avg`; response serializes as `cuaca.rh_avg` |
| `Tavg` | `daily.temperature_2m_mean` latest date | `RawWeatherData.tavg` | `float(tavg)` | `build_features_v2()` emits `Tavg`; not serialized in realtime response |
| `Rain7` | `daily.precipitation_sum` history plus latest `RR` | Historical `RawWeatherData.rr` + current `rr` | Rolling 7-day sum with `min_periods=1` | `build_features_v2()` emits `Rain7`; not serialized in realtime response |

## 6. Rainfall Investigation

`RR` comes from Open-Meteo `daily.precipitation_sum`, not `daily.rain_sum`, not `hourly.precipitation`, not `hourly.rain`, not manual aggregation, and not a cached value.

Evidence:

| Evidence | Location |
|---|---|
| Backend daily variables include `precipitation_sum` | `backend/providers/openmeteo_provider.py:106-113` |
| Backend reads rainfall from `daily["precipitation_sum"][i]` | `backend/providers/openmeteo_provider.py:127-129` |
| Backend serializes current rainfall as `cuaca.rr` | `backend/routers/realtime.py:74-77` |
| No hourly request exists | No backend `hourly` parameter found in Open-Meteo provider |
| No weather cache exists | No cache/TTL/storage code in provider/router path |

Read-only reproduction for same backend request returned latest date `2026-07-05`:

```json
{
  "precipitation_sum": 15.9,
  "relative_humidity_2m_mean": 90,
  "temperature_2m_mean": 27.0,
  "temperature_2m_max": 31.0,
  "temperature_2m_min": 25.1
}
```

Backend displays this rounded as approximately `16 mm`.

## 7. Historical Window

| Item | Count | Explanation |
|---|---:|---|
| Requested days | 14 | `predict_realtime()` calls `get_weather_history(wilayah, days=14)`. |
| Date range in probe | 2026-06-22 through 2026-07-05 | Inclusive `start_date=today-13`, `end_date=today`. |
| Latest/current record | 1 | `history_data[-1]`, date `2026-07-05`. |
| Preceding records | 13 | `history_data[:-1]`; used as history input. |
| Records passed into Rain7 series | 14 | 13 preceding rainfall values plus current rainfall. |
| Records actually used by final Rain7 | 7 | Rolling window uses the last 6 preceding records plus current date. |
| Ignored by final Rain7 | 7 | D-13 through D-7 are over-fetched for FRI v2. |

Returned backend precipitation series:

| Date | `precipitation_sum` mm |
|---|---:|
| 2026-06-22 | 9.4 |
| 2026-06-23 | 4.6 |
| 2026-06-24 | 27.7 |
| 2026-06-25 | 6.4 |
| 2026-06-26 | 0.8 |
| 2026-06-27 | 0.0 |
| 2026-06-28 | 5.1 |
| 2026-06-29 | 37.8 |
| 2026-06-30 | 1.9 |
| 2026-07-01 | 8.7 |
| 2026-07-02 | 1.7 |
| 2026-07-03 | 0.9 |
| 2026-07-04 | 2.7 |
| 2026-07-05 | 15.9 |

Final `Rain7` from the backend series:

```text
37.8 + 1.9 + 8.7 + 1.7 + 0.9 + 2.7 + 15.9 = 69.6 mm
```

## 8. Weather Model Used

The backend does not send a `models` query parameter.

Therefore, Open-Meteo uses its default automatic weather model selection for the requested coordinate and variables.

| Model Parameter | Backend Value |
|---|---|
| `models` | Not sent |
| Effective Open-Meteo behavior | Automatic/default model selection |
| Explicit ECMWF | No |
| Explicit ICON | No |
| Explicit GFS | No |
| Explicit JMA | No |

Weather model can influence rainfall values in general. However, the observed `3 mm` vs `16 mm` mismatch is not explained by model selection here because both reproduced requests omit `models` and therefore use the same Open-Meteo automatic/default behavior.

## 9. Coordinate Verification

### Backend Request Coordinates

| Source | Latitude | Longitude |
|---|---:|---:|
| Open-Meteo geocoding result for `Pekanbaru` | `0.51667` | `101.44167` |
| Forecast response grid metadata | `0.52724075` | `101.41738` |

The forecast response metadata differs slightly because Open-Meteo maps requested coordinates to an internal forecast grid point.

### Can Coordinates Explain The Difference?

For the observed mismatch, no.

Evidence: using the same backend coordinates, same date range, same endpoint, same timezone, and same automatic model, changing only the daily variable from `precipitation_sum` to `rain_sum` returns `3.0 mm`. That matches the manual observation.

## 10. Manual Reproduction URLs

### Exact Backend URL

```text
https://api.open-meteo.com/v1/forecast?latitude=0.51667&longitude=101.44167&daily=precipitation_sum%2Crelative_humidity_2m_mean%2Ctemperature_2m_mean%2Ctemperature_2m_max%2Ctemperature_2m_min&start_date=2026-06-22&end_date=2026-07-05&timezone=Asia%2FJakarta
```

Latest returned `RR` source:

```text
daily.precipitation_sum[2026-07-05] = 15.9 mm
```

### Same Request But With `rain_sum`

This reproduces the manual `Rain Sum = 3 mm` observation:

```text
https://api.open-meteo.com/v1/forecast?latitude=0.51667&longitude=101.44167&daily=rain_sum&start_date=2026-06-22&end_date=2026-07-05&timezone=Asia%2FJakarta
```

Latest returned manual-like value:

```text
daily.rain_sum[2026-07-05] = 3.0 mm
```

## 11. Manual vs Backend Comparison

The exact manual URL was not provided in the task. The table below compares the backend request with the reproduced manual-equivalent request that returns the reported `3 mm` value.

| Attribute | Manual Request Equivalent | Backend Request |
|---|---|---|
| Endpoint | Forecast API | Forecast API |
| Base URL | `https://api.open-meteo.com/v1/forecast` | `https://api.open-meteo.com/v1/forecast` |
| Latitude | `0.51667` | `0.51667` |
| Longitude | `101.44167` | `101.44167` |
| Forecast response grid | `0.52724075, 101.41738` | `0.52724075, 101.41738` |
| Timezone | `Asia/Jakarta` | `Asia/Jakarta` |
| Weather model | Automatic/default, no `models` param | Automatic/default, no `models` param |
| Daily variables | `rain_sum` | `precipitation_sum,relative_humidity_2m_mean,temperature_2m_mean,temperature_2m_max,temperature_2m_min` |
| Hourly variables | None | None |
| Forecast days | Not sent | Not sent |
| Past days | Not sent | Not sent |
| Start date | `2026-06-22` | `2026-06-22` |
| End date | `2026-07-05` | `2026-07-05` |
| Returned latest rainfall | `rain_sum = 3.0 mm` | `precipitation_sum = 15.9 mm` |
| Backend `RR`? | No | Yes |

## 12. Difference Analysis

Actual cause: Different Open-Meteo daily variable.

| Candidate Cause | Result | Evidence |
|---|---|---|
| Different endpoint | No | Both reproduced values come from `/v1/forecast`. |
| Different variable | Yes | `precipitation_sum` returns `15.9`; `rain_sum` returns `3.0`. |
| Different weather model | No | Both requests omit `models`, using automatic/default behavior. |
| Different date | No | Both compared on `2026-07-05`. |
| Different coordinates | No | Same requested coordinates reproduce both values. |
| Historical vs forecast | No | Both use Forecast API and same date range. |
| Hourly aggregation | No | Backend sends no hourly variables and performs no hourly aggregation. |
| Caching | No | No backend weather cache exists. |
| Other | No | Not needed to explain the observed numbers. |

Conclusion:

```text
Manual Rain Sum = 3 mm because manual request uses daily.rain_sum.
Backend RR = 16 mm because backend uses daily.precipitation_sum = 15.9 mm.
```

## 13. Scientific Compliance With FRI v2

FRI v2 specification states `RR` is daily rainfall. The backend maps `RR` from Open-Meteo `daily.precipitation_sum`, which is a daily precipitation total and is scientifically acceptable for daily rainfall/flood-risk triggering.

| Check | Result |
|---|---|
| `RR` originates from daily Open-Meteo precipitation total | PASS |
| `Rain7` uses accumulated daily precipitation history including current day | PASS |
| `RH_avg` originates from daily mean relative humidity | PASS |
| `Tavg` originates from daily mean temperature | PASS |
| Backend uses hourly precipitation/rain aggregation | PASS: no hourly path exists |
| Backend uses cached or stale rainfall | PASS: no backend weather cache exists |

No deviation from FRI v2 was found in the backend Open-Meteo request. The discrepancy is an interpretation/comparison mismatch between Open-Meteo `rain_sum` and backend `precipitation_sum`.

## 14. Code Modification Check

| Area | Modified? |
|---|---:|
| Backend | NONE |
| Frontend | NONE |
| Prediction | NONE |
| Random Forest | NONE |
| Configuration | NONE |
| Model artifacts | NONE |
| Audit report | Created `docs/research/fri_v2/openmeteo_request_verification.md` |

## 15. Recommendation

1. Keep backend `RR` mapped to `daily.precipitation_sum` unless the scientific definition is explicitly changed.
2. When manually validating backend rainfall, compare against Open-Meteo `precipitation_sum`, not `rain_sum`.
3. Document in user-facing/debug docs that backend `Curah Hujan (RR)` means Open-Meteo daily `precipitation_sum`.
4. If product semantics require rain-only values, schedule a separate scientific/API decision sprint because switching from `precipitation_sum` to `rain_sum` would change model input semantics and FRI behavior.
