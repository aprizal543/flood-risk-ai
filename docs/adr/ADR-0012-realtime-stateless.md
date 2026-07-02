# ADR-0012: Realtime Prediction is Stateless

## Status

Accepted — Design Freeze

## Date

2026-06-29

## Decision

All realtime predictions in FloodRisk AI are stateless. Predictions are computed on-demand from the latest Open-Meteo forecast and are never stored permanently on the backend.

## Motivation

1. **Data freshness**: Open-Meteo updates forecasts multiple times daily. Stored predictions become stale within hours.
2. **Correctness**: Displaying yesterday's FRI when today's weather has changed is misleading for agricultural decision-making.
3. **Simplicity**: No database, no cache invalidation, no stale data bugs.
4. **Privacy**: No permanent record of user queries.

## Architecture

```
User Request
    ↓
GET /api/prediksi/realtime?wilayah=X
    ↓
Open-Meteo API (14-day history + today forecast)
    ↓
Feature Engineering (rolling features)
    ↓
Random Forest Prediction
    ↓
Recommendation Engine
    ↓
JSON Response (not stored)
```

### Backend

- `GET /api/prediksi/realtime` performs the full pipeline on every request
- No database writes, no file writes, no caching
- Response includes `forecast_date` (today WIB) and `updated_at` (current timestamp WIB)
- Timezone: always `Asia/Jakarta`

### Frontend

- Prediction history is **session state only** (localStorage, cleared daily)
- History stores: location name, coordinates, FRI, risk level, timestamp
- All values are transient — cleared automatically at midnight WIB
- Clicking a history item triggers a **new prediction request** (never reuses old data)

## Daily Reset

At `00:00 Asia/Jakarta`, the frontend clears:

- Prediction history
- Map markers
- Marker popups
- Polygon states
- Spatial statistics
- Legend counts

Preserved across reset:

- Theme preference
- Sidebar state
- Panel width
- Layer visibility
- Map base layer
- Filter preferences

### Mechanism

- `lastResetDate` stored in localStorage
- Checked on: page load, `visibilitychange`, `window.focus`
- If `today (WIB) !== lastResetDate`: execute reset, show toast notification

## Future Considerations

- **Caching**: If needed for performance, implement short-lived HTTP cache (max 5 minutes) at the API gateway level, never in application code.
- **Multi-province**: Adding new provinces requires only GeoJSON + polygon registry. No architecture change.
- **Offline mode**: If offline support is needed, use Service Worker with explicit TTL, not permanent storage.

## Frozen Architecture

The following components are design-frozen after this ADR:

- Open-Meteo Integration
- Smart Geocoding (Indonesia/Riau prioritization)
- Point-In-Polygon (ray-casting)
- Dynamic Polygon Visibility
- Marker Interaction
- Dashboard Realtime
- Forecast Metadata (`forecast_date` + `updated_at`)
- Timezone Handling (`Asia/Jakarta`)
- Stateless Prediction
