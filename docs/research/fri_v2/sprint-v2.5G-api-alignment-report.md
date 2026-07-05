# Sprint v2.5G API Alignment Report

## Summary

Sprint v2.5G completed the final synchronization between the authenticated realtime RF v2 backend response and the frontend dashboard. The realtime API now exposes `RR`, `Rain7`, `RH_avg`, and `Tavg` from the same feature dictionary already passed into Random Forest v2. The frontend consumes those response fields through the shared display mapper and shows the approved terminology across popup, left panel, analytics, printable report, and AI evidence.

Final recommendation:

```text
✅ FRI v2 Fully Synchronized
```

## Files Modified

- `backend/services/prediction_gateway.py`
- `backend/routers/realtime.py`
- `tests/test_weather_provider.py`
- `apps/web/types/api.ts`
- `apps/web/lib/realtime-presentation.ts`
- `apps/web/components/map/RegionPopup.ts`
- `apps/web/components/map/SpatialStatistics.tsx`
- `apps/web/components/map/PolygonInteraction.ts`
- `apps/web/components/dashboard/dashboard-panel.tsx`
- `apps/web/components/dashboard/analytics-panel.tsx`
- `apps/web/components/dashboard/ai-support-panel.tsx`
- `apps/web/components/dashboard/reports-panel.tsx`
- `apps/web/components/dashboard/trend-chart.tsx`
- `apps/web/components/dashboard/hero-fri-card.tsx`
- `apps/web/components/report/PrintableReport.tsx`
- `apps/web/services/llm.ts`
- `apps/web/mocks/data.ts`

## Files Created

- `docs/research/fri_v2/sprint-v2.5G-api-alignment-report.md`

## Response Schema Changes

`GET /api/prediksi/realtime` now includes these top-level fields:

| Field | Type | Source | Notes |
|---|---|---|---|
| `RR` | number | `result["_features"]["RR"]` | Exact value passed to RF v2. |
| `Rain7` | number | `result["_features"]["Rain7"]` | Exact value passed to RF v2. |
| `RH_avg` | number | `result["_features"]["RH_avg"]` | Exact value passed to RF v2. |
| `Tavg` | number | `result["_features"]["Tavg"]` | Exact value passed to RF v2. |

The realtime response continues to expose:

- `fri`
- `tingkat_risiko`
- `waktu_prediksi`
- `sumber_data`
- `forecast_date`
- `cuaca`
- `rekomendasi`
- `mitigasi`

No feature engineering, Random Forest artifact, Open-Meteo provider, `precipitation_sum` mapping, Rain7 calculation, Tavg sourcing, authentication, middleware, database, or deployment code was changed.

## Backend Implementation Notes

- `predict_from_raw()` now supports `include_features=False` by default.
- Only the realtime router calls `predict_from_raw(..., include_features=True)`.
- The feature dict is built once, passed to `prediksi()`, and then attached internally as `_features` when requested.
- The realtime router serializes `RR`, `Rain7`, `RH_avg`, and `Tavg` from `_features`.
- Other prediction endpoints do not expose `_features` by default.

## Frontend Components Updated

| Area | File | Update |
|---|---|---|
| Shared labels and mapper | `apps/web/lib/realtime-presentation.ts` | Added frozen label constants and direct response mapping from `RR`, `Rain7`, `RH_avg`, `Tavg`. |
| Types | `apps/web/types/api.ts` | Made top-level `RR`, `Rain7`, `RH_avg`, `Tavg` required realtime response fields. |
| Popup | `apps/web/components/map/RegionPopup.ts` | Uses approved labels and values from history derived from one realtime response. |
| Left panel | `apps/web/components/dashboard/dashboard-panel.tsx` | Uses approved labels and response-backed display values. |
| Analytics | `apps/web/components/dashboard/analytics-panel.tsx` | Uses approved labels and response-backed display values. |
| Reports | `apps/web/components/dashboard/reports-panel.tsx` | Uses approved labels in summary and weather cards. |
| Printable report | `apps/web/components/report/PrintableReport.tsx` | Uses approved labels and v2 feature wording. |
| AI evidence | `apps/web/components/dashboard/ai-support-panel.tsx` | Uses approved labels. |
| AI context | `apps/web/services/llm.ts` | Uses response-backed FRI v2 values instead of legacy Tmax/Tmin wording. |

## UI Terminology Verification

Approved labels are centralized in `REALTIME_LABELS`:

- `Flood Risk Index`
- `Risiko`
- `Curah Hujan Hari Ini`
- `Akumulasi Curah Hujan 7 Hari ke Belakang`
- `Kelembapan`
- `Suhu Rata-rata`
- `Prediksi`

Verified updated areas:

- Realtime popup
- Left information panel
- Analytics panel
- Printable report
- AI evidence panel
- Report summary/weather cards

## Single Source Of Truth

All displayed realtime weather/model values originate from one backend response returned by `GET /api/prediksi/realtime`.

- No additional API call was added for `RR`, `Rain7`, `RH_avg`, or `Tavg`.
- Frontend does not calculate `Rain7`, `Tavg`, FRI, or risk.
- Popup values are still derived from the current response snapshot stored in search history.

## Regression Validation

Prediction regression probe:

```json
{
  "base_fri": 42.8,
  "aligned_fri": 42.8,
  "base_risk": "Risiko Sedang",
  "aligned_risk": "Risiko Sedang",
  "features": {"RR": 10.0, "Rain7": 37.0, "RH_avg": 80.0, "Tavg": 27.5},
  "prediction_unchanged": true
}
```

Result:

- Realtime prediction unchanged.
- FRI unchanged.
- Risk unchanged.
- Backend prediction path unchanged except response feature carry-through.

## Performance Verification

Warm latency comparison:

```json
{
  "warm_base_ms": 28.914,
  "warm_aligned_ms": 28.536,
  "delta_ms": -0.379,
  "prediction_unchanged": true
}
```

Result: no measurable latency regression.

## Validation Commands

Backend:

```text
python -m py_compile "backend/services/prediction_gateway.py" "backend/routers/realtime.py" "tests/test_weather_provider.py"
```

Result: PASS

```text
pytest tests/test_weather_provider.py -k "realtime_success or FriV2FeatureEngineering or FriV2RandomForestCompatibility"
```

Result: `7 passed, 17 deselected`

Frontend:

```text
npm run lint
npx tsc --noEmit
npm run build
```

Result: PASS

Build warnings unchanged from prior frontend validation:

- Next.js inferred workspace root because multiple lockfiles exist.
- Next.js reports the `middleware` convention is deprecated in favor of `proxy`.

Known backend test warnings unchanged:

- sklearn `InconsistentVersionWarning` because `random_forest_v2.pkl` was serialized with sklearn `1.6.1` and loaded under sklearn `1.8.0`.
- pytest-asyncio loop-scope deprecation warning.

## Acceptance Checklist

| Criterion | Result |
|---|---|
| Backend still uses `precipitation_sum` | PASS |
| Backend still computes Rain7 in existing feature builder | PASS |
| Backend still sources Tavg from existing provider/builder path | PASS |
| Random Forest unchanged | PASS |
| Feature engineering unchanged | PASS |
| Response exposes `RR` | PASS |
| Response exposes `Rain7` | PASS |
| Response exposes `RH_avg` | PASS |
| Response exposes `Tavg` | PASS |
| Popup displays approved labels | PASS |
| Left panel displays approved labels | PASS |
| Analytics displays approved labels | PASS |
| Printable report displays approved labels | PASS |
| AI evidence displays approved labels | PASS |
| No frontend Rain7/Tavg calculation | PASS |
| No duplicated backend Rain7/Tavg calculation | PASS |
| No prediction differences | PASS |

## Final Recommendation

```text
✅ FRI v2 Fully Synchronized
```
