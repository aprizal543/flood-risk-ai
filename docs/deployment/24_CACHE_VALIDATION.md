# Cache Validation

## Acceptance Criteria

### 1. Repeated Requests Use Cache (No HTTP)

**Test**: `TestGeocodingCache::test_first_request_is_miss_second_is_hit`
**Test**: `TestForecastCache::test_first_request_is_miss_second_is_hit`

```
First  request → Cache MISS → HTTP call → Store → Return
Second request → Cache HIT  → Return cached → No HTTP
```

**Validation**: `mock_get.call_count == 1` after two calls to `geocode("Pekanbaru")`.

### 2. Different Cities Create Separate Entries

**Test**: `TestGeocodingCache::test_different_cities_create_separate_entries`
**Test**: `TestForecastCache::test_different_cities_cached_separately`

```
geocode("Pekanbaru") → HTTP (MISS) → store "geo:pekanbaru"
geocode("Dumai")     → HTTP (MISS) → store "geo:dumai"
geocode("Pekanbaru") → Cache HIT (no HTTP)
geocode("Dumai")     → Cache HIT (no HTTP)
```

**Validation**: Two HTTP calls total, both return correct locations.

### 3. Case-Insensitive Cache Key

**Test**: `TestGeocodingCache::test_case_insensitive_cache_key`

```
geocode("  Pekanbaru  ") → HTTP (MISS) → store "geo:pekanbaru"
geocode("pekanbaru")     → Cache HIT
geocode("PEKANBARU")     → Cache HIT
```

**Validation**: One HTTP call total.

### 4. Cache Metrics Are Accurate

**Test**: `TestGeocodingCache::test_cache_metrics_updated`
**Test**: `TestForecastCache::test_forecast_cache_metrics`

```
First  request → geocoding_metrics.misses += 1
Second request → geocoding_metrics.hits += 1
```

**Validation**: `geocoding_metrics.hits == 1`, `geocoding_metrics.misses == 1`.

### 5. TTL Expiration Works

**Test**: `TestThreadSafeCache::test_ttl_expiry`
**Test**: `TestForecastCache::test_forecast_cache_ttl`

```
cache.set("k", "v") with TTL=1s
sleep(1.1)
cache.get("k") → None (expired)
```

**Validation**: After TTL expiry, entry returns `None`.

### 6. Prediction Equality (Bit-for-Bit Identical)

**Test**: `TestPredictionEquality::test_prediction_identical_with_cache`

```
weather1 = provider.get_current_weather("Pekanbaru")  # cache MISS
pred1 = predict_from_raw(weather1, ...)

weather2 = provider.get_current_weather("Pekanbaru")  # cache HIT
pred2 = predict_from_raw(weather2, ...)

assert weather1 == weather2
assert pred1["fri"] == pred2["fri"]
assert pred1["rekomendasi"] == pred2["rekomendasi"]
assert pred1["mitigasi"] == pred2["mitigasi"]
```

**Validation**: All prediction fields identical.

### 7. Diagnostics Endpoint

**Test**: `TestCacheDiagnostics::test_cache_endpoint_returns_expected_structure`

```json
GET /api/system/cache

{
  "geocoding": {
    "hits": 0,
    "misses": 1,
    "hit_rate": 0.0,
    "entries": 1,
    "maxsize": 1000,
    "ttl_seconds": 86400
  },
  "forecast": {
    "hits": 2,
    "misses": 1,
    "hit_rate": 0.6667,
    "entries": 1,
    "maxsize": 100,
    "ttl_seconds": 600
  }
}
```

## Regression Test Suite

```bash
python -m pytest tests/test_cache.py -v
```
