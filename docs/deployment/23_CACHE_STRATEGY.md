# Cache Strategy

## Caching Decisions

### Geocoding Cache

- **Key**: `geo:{city_name.lower().strip()}`
- **Value**: `GeoLocation(latitude, longitude, resolved_name)`
- **TTL**: 24 hours (configurable via `GEOCODING_CACHE_TTL`)
- **Storage**: `cachetools.TTLCache` with thread-safe wrapper
- **Why 24h?** City names and their coordinates do not change. 24h TTL is conservative and avoids stale data in the extremely unlikely event of a geocoding database update.

### Forecast Cache

- **Key**: `fcst:{lat}:{lon}:{days}`
- **Value**: Raw JSON response from Open-Meteo (unprocessed `dict`)
- **TTL**: 10 minutes (configurable via `FORECAST_CACHE_TTL`)
- **Storage**: `cachetools.TTLCache` with thread-safe wrapper
- **Why 10m?** Open-Meteo updates forecast data hourly. A 10-minute TTL provides significant latency reduction for repeated requests while ensuring data is never more than 10 minutes stale.

## Cache Invalidation Strategy

### Explicit Invalidation

- `ThreadSafeCache.clear()` — clears all entries immediately
- Used in tests to reset state between test cases

### Time-Based Expiration (TTL)

- Entries are automatically evicted when their TTL expires
- `cachetools.TTLCache` uses lazy expiration: expired entries are removed on next access or during cleanup on write

### Size-Based Eviction (LRU)

- When `maxsize` is exceeded, the least-recently-used entry is evicted
- Geocoding: max 1000 entries
- Forecast: max 100 entries

### No Manual Invalidation API

- No endpoint to purge individual cache entries (not needed for current requirements)
- Full cache can be cleared via server restart or `/api/system/cache` (future enhancement)

## Key Design Decisions

### Why store raw JSON for forecast?

Storing the raw JSON response (rather than processed `RawWeatherData`) ensures that:
1. The cache is format-agnostic — if `RawWeatherData` construction logic changes, cached data is still valid
2. Deserialization happens on every cache hit (rebuilding `RawWeatherData`), matching the code path of a cache miss exactly
3. Prediction outputs remain bit-for-bit identical regardless of cache state

### Why thread-safe wrapper?

FastAPI with uvicorn runs multiple workers/threads. Without thread safety, concurrent requests could:
- Read partially written cache entries
- Corrupt hit/miss counters
- Cause `TTLCache` internal state corruption

### Why not Redis?

Keeping caches in-process avoids:
- Network latency for cache lookups
- Redis deployment and maintenance overhead
- Serialization/deserialization cost
- Cache coherence complexity across workers

The trade-off is that cache is per-worker (each uvicorn worker has its own cache). For the current scale, this is acceptable.
