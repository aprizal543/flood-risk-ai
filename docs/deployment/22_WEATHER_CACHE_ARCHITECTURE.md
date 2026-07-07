# Weather Cache Architecture

## Overview

The weather caching layer sits between the request handler and external API calls (Open-Meteo Geocoding + Forecast). It intercepts duplicate requests within the TTL window to eliminate redundant HTTP calls.

## Architecture Diagram

```
Client
  │
  ▼
Backend API
  │
  ├── geocode("Pekanbaru")
  │     │
  │     ├── [Cache HIT]  ──► Return cached GeoLocation
  │     │
  │     └── [Cache MISS] ──► Open-Meteo Geocoding API
  │                            │
  │                            └── Store result ──► Return
  │
  └── get_current_weather("Pekanbaru")
        │
        ├── geocode("Pekanbaru")  ──► GeoLocation (cached)
        │
        ├── _fetch_forecast(lat, lon, days)
        │     │
        │     ├── [Cache HIT]  ──► Return cached JSON
        │     │
        │     └── [Cache MISS] ──► Open-Meteo Forecast API
        │                            │
        │                            └── Store raw JSON ──► Return
        │
        └── Build RawWeatherData ──► Feature Engineering ──► Prediction
```

## Module Structure

```
backend/
├── cache/                    # New package
│   ├── __init__.py           # Exports
│   ├── base.py               # ThreadSafeCache (generic TTLCache wrapper)
│   └── metrics.py            # CacheMetrics (hit/miss counters)
│
├── config.py                 # Cache TTLs (GEOCODING_CACHE_TTL, FORECAST_CACHE_TTL)
│
├── providers/
│   ├── geocoding.py          # geocoding_cache instance (module-level)
│   └── openmeteo_provider.py # forecast_cache instance (module-level)
│
└── routers/
    └── health.py             # /api/system/cache diagnostics endpoint
```

## Thread Safety

Both `ThreadSafeCache` and `CacheMetrics` use `threading.RLock` (reentrant lock) for safe concurrent access from multiple FastAPI request handlers running in threaded mode.

- `ThreadSafeCache.get(key)` — atomic read
- `ThreadSafeCache.set(key, value)` — atomic write
- `CacheMetrics.hit()` / `miss()` — atomic counter increment
- `CacheMetrics.snapshot()` — atomic read (internally calls `hit_rate` safely due to RLock)

## TTL Policy

| Cache        | Default TTL | Config Key               | Rationale                        |
|-------------|-------------|--------------------------|----------------------------------|
| Geocoding   | 86400s (24h)| `GEOCODING_CACHE_TTL`    | City → coords rarely change      |
| Forecast    | 600s (10m)  | `FORECAST_CACHE_TTL`     | Weather data refreshes hourly    |

## Memory Usage

- Geocoding: ~200 bytes per entry (string key + GeoLocation dataclass). Max 1000 entries ≈ 200 KB.
- Forecast: ~2–10 KB per entry (raw JSON response). Max 100 entries ≈ 200 KB–1 MB.

Total worst-case memory: ~1.2 MB — negligible for a production server.
