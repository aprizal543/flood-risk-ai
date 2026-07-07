# 13 — Open-Meteo Retry Implementation

## Overview

Added exponential-backoff retry to both Open-Meteo provider calls (geocoding and forecast) using urllib3's built-in `Retry` mechanism attached to `requests.Session` via `HTTPAdapter`.

## Retry Configuration

### Parameters (from `backend/config.py`)

| Parameter | Env Variable | Default | Description |
|-----------|-------------|---------|-------------|
| `RETRY_TOTAL` | `HTTP_RETRY_TOTAL` | `3` | Maximum total retries across all error types |
| `RETRY_BACKOFF_FACTOR` | `HTTP_RETRY_BACKOFF_FACTOR` | `1.0` | Exponential backoff base (seconds) |

### Retry Triggers

| Error Type | Retry? | Notes |
|-----------|--------|-------|
| `requests.Timeout` | Yes | Read timeout / connect timeout |
| `requests.ConnectionError` | Yes | DNS failure, connection refused, SSL error |
| HTTP 429 (Too Many Requests) | Yes | Open-Meteo rate limiting |
| HTTP 500, 502, 503, 504 | Yes | Server-side errors |
| HTTP 400, 404 | **No** | Client errors — returned immediately |
| Invalid location (empty results) | **No** | Business logic error, never reaches HTTP layer |

### Backoff Sequence

With `backoff_factor=1.0` and `total=3`:

| Attempt | Delay Before | Cumulative Wait |
|---------|-------------|-----------------|
| 1st | 0s | 0s |
| 2nd (retry 1) | 1s | 1s |
| 3rd (retry 2) | 2s | 3s |
| 4th (retry 3) | 4s | 7s |

Formula: `delay = backoff_factor * (2 ** (retry_number - 1))`

### Worst-Case Timeouts

#### Geocoding (connect=3s, read=5s)

| Stage | Wall Clock |
|-------|-----------|
| Attempt 1: connect timeout | 3s |
| Backoff 1s + Attempt 2: connect timeout | 4s |
| Backoff 2s + Attempt 3: read timeout | 7s |
| Backoff 4s + Attempt 4: read timeout | 9s |
| **Total** | **23s** |

#### Forecast (connect=3s, read=10s)

| Stage | Wall Clock |
|-------|-----------|
| Attempt 1: read timeout | 10s |
| Backoff 1s + Attempt 2: read timeout | 11s |
| Backoff 2s + Attempt 3: read timeout | 12s |
| Backoff 4s + Attempt 4: read timeout | 14s |
| **Total** | **47s** |

> **Note**: The worst case only applies when Open-Meteo is completely unavailable for an extended period. For transient blips (the primary target), retry 1 or 2 succeeds quickly, and the user sees no error.

## Implementation Location

### `backend/providers/geocoding.py`

```python
retry_strategy = Retry(
    total=3,
    backoff_factor=1.0,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,
    pool_maxsize=20,
)
```

### `backend/providers/openmeteo_provider.py`

Same configuration — retry strategy is identical.

## Safety

- **Idempotent GETs**: Both geocoding and forecast use HTTP GET with no side effects. Retries are safe.
- **No duplicate predictions**: The forecast call returns weather data only. A retry means re-fetching the same data, not re-running the ML pipeline.
- **No duplicate logging**: Each HTTP attempt is transparent to the application — urllib3 handles retries internally. The application only sees success (if any retry succeeded) or failure (if all retries exhausted).

## Test Coverage

All existing mock-based tests pass with the retry mechanism:
- `test_geocode_success` ✅
- `test_geocode_connection_error` ✅
- `test_get_current_weather_success` ✅
- `test_get_weather_connection_error` ✅
- `test_get_weather_incomplete_data` ✅
