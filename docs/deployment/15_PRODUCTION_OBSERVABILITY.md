# 15 — Production Observability Implementation

## Overview

Added structured logging, request context propagation, request ID tracking, and enhanced exception logging across the provider stack.

## Changes

### 1. `backend/logging.py` (new)

Provides request context propagation via Python `contextvars`:

```python
_request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

def generate_request_id() -> str:
    return uuid.uuid4().hex[:8]

def set_request_id(rid: str) -> None:
    _request_id_var.set(rid)

def get_request_id() -> str:
    return _request_id_var.get()
```

The context variable is automatically propagated to any threads or async tasks spawned during request processing (Python 3.7+ `contextvars` + `anyio`).

### 2. `backend/middleware.py` — RequestID tracking

```python
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = generate_request_id()
        set_request_id(request_id)
        # ...log request with [request_id]...
        response = await call_next(request)
        # ...log response with [request_id]...
```

### 3. Provider-level timing and structured error logging

#### Geocoding (`geocoding.py`)

**Success log:**
```
2026-07-07 12:00:00 [INFO] backend.providers.geocoding: [a1b2c3d4] Geocoding 'Pekanbaru'=342ms
```

**Failure log:**
```
2026-07-07 12:00:00 [ERROR] backend.providers.geocoding: [a1b2c3d4] Geocoding 'Pekanbaru' FAILED category=TIMEOUT status=None elapsed=10042ms: Connection timeout
Traceback (most recent call last):
  ...
```

#### Open-Meteo Forecast (`openmeteo_provider.py`)

**Success log:**
```
2026-07-07 12:00:00 [INFO] backend.providers.openmeteo: [a1b2c3d4] Forecast(14d) 'Pekanbaru'=811ms
```

**Failure log:**
```
2026-07-07 12:00:00 [ERROR] backend.providers.openmeteo: [a1b2c3d4] Forecast(14d) 'Pekanbaru' FAILED category=HTTP_ERROR (503) status=503 elapsed=3050ms: Server Error
Traceback (most recent call last):
  ...
```

### 4. Error categorization

The `_categorise_error()` function classifies failures into:

| Category | Meaning | Example Root Cause |
|----------|---------|-------------------|
| `TIMEOUT` | Request exceeded timeout | Open-Meteo slow response, network congestion |
| `CONNECTION_ERROR (NameResolutionError)` | DNS failure | DNS server unavailable |
| `CONNECTION_ERROR (ConnectionRefusedError)` | Port closed / service down | Open-Meteo down |
| `CONNECTION_ERROR (SSLError)` | TLS negotiation failed | Certificate issue |
| `HTTP_ERROR (5xx)` | Server error | Open-Meteo 503 |
| `HTTP_ERROR (429)` | Rate limited | Too many requests |
| `REQUEST_ERROR` | Other request failure | — |

### 5. Enhanced exception context

`ProviderConnectionError` now carries structured metadata:

```python
class ProviderConnectionError(WeatherProviderError):
    def __init__(self, message, *, url=None, elapsed_ms=None, status_code=None, original_exception=None):
        ...
    def to_log_dict(self) -> dict:
        return {
            "message": str(self),
            "url": self.url,
            "elapsed_ms": self.elapsed_ms,
            "status_code": self.status_code,
            "original_exception": repr(self.original_exception) if self.original_exception else None,
        }
```

## Sample Log Output (end-to-end request)

```
2026-07-07 12:00:00 [INFO] backend: [a1b2c3d4] Request: GET /api/prediksi/realtime?wilayah=Pekanbaru
2026-07-07 12:00:00 [INFO] backend.providers.geocoding: [a1b2c3d4] Geocoding 'Pekanbaru'=342ms
2026-07-07 12:00:01 [INFO] backend.providers.openmeteo: [a1b2c3d4] Forecast(14d) 'Pekanbaru'=811ms
2026-07-07 12:00:01 [INFO] backend.realtime: Realtime: Pekanbaru FRI=42.50 Risiko Sedang (13 hari historis)
2026-07-07 12:00:01 [INFO] backend: [a1b2c3d4] Response: 200 (1852ms)
```

## Sample Log Output (failure with retry exhaustion)

```
2026-07-07 12:00:00 [INFO] backend: [b2c3d4e5] Request: GET /api/prediksi/realtime?wilayah=Pekanbaru
2026-07-07 12:00:00 [INFO] backend.providers.geocoding: [b2c3d4e5] Geocoding 'Pekanbaru'=298ms
2026-07-07 12:00:10 [ERROR] backend.providers.openmeteo: [b2c3d4e5] Forecast(14d) 'Pekanbaru' FAILED category=TIMEOUT status=None elapsed=10042ms: Connection timeout
Traceback (most recent call last):
  File "backend/providers/openmeteo_provider.py", line 85, in _fetch_forecast
    resp = _http_get(WEATHER_URL, params=params, timeout=WEATHER_TIMEOUT)
  File "backend/providers/openmeteo_provider.py", line 69, in _http_get
    return _get_session().get(url, **kwargs)
  ... (urllib3 retry details) ...
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='api.open-meteo.com', port=443): Max retries exceeded
  (Caused by ReadTimeoutError(...))
2026-07-07 12:00:10 [INFO] backend: [b2c3d4e5] Response: 503 (10243ms)
```

## Files Modified

| File | Change |
|------|--------|
| `backend/logging.py` | New — request context propagation utilities |
| `backend/middleware.py` | RequestID generation + log enrichment |
| `backend/providers/geocoding.py` | Per-call latency logging, structured error logging |
| `backend/providers/openmeteo_provider.py` | Per-call latency logging, structured error logging |
| `backend/providers/exceptions.py` | Structured exception metadata |
