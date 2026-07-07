# 10 — Open-Meteo Reliability Audit

## TASK 3 — Geocoding Audit

### Source File
`backend/providers/geocoding.py` (49 lines)

### Is geocoding executed on every request?
**YES.** The `geocode()` function is called at the top of both `get_current_weather()` (openmeteo_provider.py:32) and `get_weather_history()` (openmeteo_provider.py:102). Every realtime prediction request calls `get_weather_history()`, which calls `geocode()` unconditionally.

```
realtime.py → get_weather_history(wilayah) → geocode(wilayah)
```

### Is caching implemented?
**NO.** There is no in-memory cache, no LRU cache, no database cache, and no distributed cache for geocoding results. Every request that includes the same city (e.g. "Pekanbaru") makes a fresh HTTP call to the Open-Meteo Geocoding API.

The `geocode()` function is a plain function with no `@lru_cache` decorator:
```python
def geocode(wilayah: str) -> GeoLocation:
    resp = requests.get(GEOCODING_URL, params={"name": wilayah, "count": 1}, timeout=10)
```

### Is geocoding an external network dependency?
**YES.** The geocoding API is a fully external HTTP dependency:

- **URL**: `https://geocoding-api.open-meteo.com/v1/search`
- **DNS resolution**: Required every call (no Session reuse means no DNS cache benefit)
- **TLS handshake**: Required every call (no connection reuse)
- **Rate limit**: Open-Meteo Geocoding API has a published rate limit of 1 request/second for the free tier (no API key required). Under concurrent user load, this can be exceeded.
- **Availability**: Depends entirely on Open-Meteo infrastructure. No SLA guarantees.

### Average expected latency

| Condition | Expected Latency | Source |
|-----------|-----------------|--------|
| Normal | 200-500ms | General API latency from Southeast Asia |
| Slow | 1-3s | Regional network congestion |
| Timeout | 10,000ms | Hardcoded timeout in code |
| DNS failure | ~2-5s | DNS timeout before TCP connection attempt |

### Impact

Each realtime prediction includes a mandatory serial geocoding call that adds **200ms-500ms** to success latency and up to **10s** to failure latency. Caching this result would eliminate the call entirely for repeated cities — and many users query the same cities repeatedly (e.g. "Pekanbaru").

### Recommendation (audit-only)

Add `@functools.lru_cache(maxsize=128)` to `geocode()` or implement a TTL-based cache. A city's latitude/longitude does not change.

---

## TASK 4 — Open-Meteo Audit

### Source File
`backend/providers/openmeteo_provider.py` (151 lines)

### Number of requests per prediction
**1** (for the realtime endpoint). Despite the name `get_weather_history`, the function makes a **single** HTTP GET request to the Open-Meteo forecast API with a date range covering 14 days.

The `get_current_weather` method is NOT called by the realtime endpoint — only `get_weather_history` is called (realtime.py:41).

### Forecast endpoint usage

**Endpoint**: `https://api.open-meteo.com/v1/forecast`
**Called by**: `get_weather_history()` (line 116) and `get_current_weather()` (line 45)

The realtime endpoint only calls `get_weather_history()`.

### Historical endpoint usage
**None.** There is no call to the Open-Meteo historical/archive API (``https://archive-api.open-meteo.com/v1/archive``). The application uses the **forecast** endpoint with a `start_date` in the past to retrieve recent data. This works because Open-Meteo's forecast API retains recent observed data for the past few days, but it is **not** the archive API.

This means:
- History beyond ~5 days may be forecast data, not observed data
- If Open-Meteo changes its data retention policy, history length could be affected

### Request parameters

#### `get_weather_history(wilayah, days=14)`
```python
params = {
    "latitude": location.latitude,
    "longitude": location.longitude,
    "daily": "precipitation_sum,relative_humidity_2m_mean,temperature_2m_mean,temperature_2m_max,temperature_2m_min",
    "start_date": (today - timedelta(days=days-1)).isoformat(),  # 13 days ago
    "end_date": today.isoformat(),
    "timezone": "Asia/Jakarta",
}
```

#### `get_current_weather(wilayah)`
```python
params = {
    "latitude": location.latitude,
    "longitude": location.longitude,
    "daily": "precipitation_sum,relative_humidity_2m_mean,temperature_2m_mean,temperature_2m_max,temperature_2m_min",
    "start_date": (today - timedelta(days=1)).isoformat(),
    "end_date": today.isoformat(),
    "timezone": "Asia/Jakarta",
}
```

#### Key observations

1. **Both methods request the same 5 daily variables**: precipitation_sum, relative_humidity_2m_mean, temperature_2m_mean, temperature_2m_max, temperature_2m_min
2. **Timezone is hardcoded** to `Asia/Jakarta` (WIB)
3. **No hourly data requested** — only daily aggregates
4. **No `past_days` parameter** — uses explicit date range instead
5. **No `forecast_days` parameter** — defaults to Open-Meteo's default (7 days), but the date range overrides this

### Timeout configuration

```python
resp = requests.get(WEATHER_URL, params=params, timeout=10)
```

- **Hardcoded 10 seconds**
- **Single value** — applies to both connect and read timeouts. If the connection is established but the response stream is slow, the entire 10 seconds is consumed on reading.
- **No retry** on timeout

### Failure handling

```python
try:
    resp = requests.get(WEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()
except requests.RequestException as e:
    raise ProviderConnectionError(f"Gagal terhubung ke Open-Meteo Weather API: {e}")
```

The exception handler:
- Catches ALL `requests.RequestException` subclasses (timeout, connection error, HTTP error)
- Wraps in a generic `ProviderConnectionError`
- Does NOT log the original exception
- Does NOT distinguish between timeout, connection refused, DNS failure, or HTTP 4xx/5xx

### Does a single provider timeout directly cause a 503?

**YES. Directly.** The exception propagation chain is:

1. `requests.get()` raises `requests.Timeout` or `requests.ConnectionError`
2. Caught by `except requests.RequestException` → raised as `ProviderConnectionError`
3. Propagated up to `realtime.py:44`:
   ```python
   except ProviderConnectionError as e:
       raise HTTPException(status_code=503, detail=str(e))
   ```
4. FastAPI returns HTTP 503 with the exception message

There is **no intermediary layer** that could catch this and:
- Retry the call
- Return stale/cached data
- Fall back to an alternative provider
- Return a partial response

The 503 is a direct consequence of any Open-Meteo API failure.

### Additional findings

#### 1. `requests.Session` not used
Neither `get_current_weather` nor `get_weather_history` uses `requests.Session`. This means:
- No TCP connection reuse between calls
- No DNS cache reuse between calls
- No HTTP keep-alive
- No adapter-level timeout configuration

#### 2. No HTTP error code handling
`resp.raise_for_status()` treats any 4xx/5xx response as an exception. The Open-Meteo API may return:
- **429 Too Many Requests** — rate limited
- **503 Service Unavailable** — temporary overload
- **400 Bad Request** — invalid parameters

All are treated identically as `ProviderConnectionError` → HTTP 503.

#### 3. No response size limits
The response is read entirely into memory with `resp.json()`. For 14 days of data, this is small (~2KB), but there is no safeguard against unexpectedly large responses.

#### 4. No data freshness check
The function trusts the API's time series. If Open-Meteo returns stale data for yesterday (e.g. forecast instead of observation), the application uses it without validation.
