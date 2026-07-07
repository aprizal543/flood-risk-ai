# 12 — Production Hotfix Plan

> **This document proposes fixes only. No implementation until approved.**

## Ranking Matrix

| Priority | Fix | Impact | Complexity | Risk | Latency Improvement | Reliability Improvement |
|----------|-----|--------|-----------|------|--------------------|------------------------|
| P0 | Add `requests.Session` with connection pooling | High | Low | Low | ~200-500ms reduction | High — reduces SNAT port exhaustion |
| P0 | Implement `@lru_cache` on `geocode()` | High | Low | Low | ~200-500ms reduction per repeated city | Medium — removes 1 of 3 external calls |
| P0 | Add retry with exponential backoff to Open-Meteo calls | High | Low | Low | None on success | High — eliminates transient failure 503s |
| P1 | Separate connect timeout (3s) from read timeout (10s) | Medium | Low | Low | Faster failure on network issues | Medium — fails fast for connectivity problems |
| P1 | Add `logger.exception()` in all `except` blocks | Medium | Very Low | Low | None | High — enables debugging of timeout causes |
| P1 | Add per-provider latency logging | Medium | Low | Low | None | Medium — enables monitoring of provider health |
| P2 | Configure timeouts via environment variables | Low | Low | Low | None | Medium — allows tuning without code deploy |
| P2 | Add circuit breaker pattern | Medium | Medium | Medium | None | High — prevents cascade failures |
| P2 | Add degraded mode (use last known data on failure) | High | Medium | Medium | None | High — eliminates 503s entirely |
| P3 | Implement async HTTP with `httpx.AsyncClient` | Low | High | High | ~100-200ms via concurrent calls | Low | |
| P3 | Add provider health check endpoint | Low | Low | Low | None | Medium — proactive monitoring | |

---

## P0 — Critical (Hotfix)

### P0.1: Add `requests.Session` with connection pooling

**Files**: `backend/providers/openmeteo_provider.py`, `backend/providers/geocoding.py`

**Changes**:
- Create a module-level `requests.Session()` instance in both `openmeteo_provider.py` and `geocoding.py`
- Configure `Retry` adapter with backoff
- Replace raw `requests.get(...)` with `session.get(...)`
- Set pool size via `HTTPAdapter(pool_connections=10, pool_maxsize=20)`

**Benefit**:
- TCP connection reuse eliminates TLS handshake overhead (~100-300ms per call)
- DNS cache reuse
- HTTP keep-alive reduces latency
- Reduces SNAT port consumption in Azure

**Risk**: Very low. `requests.Session` is a drop-in replacement for `requests.get()`.

**Expected latency improvement**: 200-500ms per request (from reused connections)

---

### P0.2: Cache geocoding results

**File**: `backend/providers/geocoding.py`

**Changes**:
- Add `@functools.lru_cache(maxsize=128)` to the `geocode()` function
- Or implement a TTL-based cache with `cachetools.TTLCache`

**Benefit**:
- Eliminates geocoding API call for repeated cities
- Cities don't change coordinates — cache is safe indefinitely
- Removes 1 of 3 external network calls from the critical path

**Risk**: Very low. Deterministic function — same input always returns same output.

**Expected latency improvement**: 200-500ms per request (eliminated entirely for cached cities)

---

### P0.3: Add retry with exponential backoff

**Files**: `backend/providers/openmeteo_provider.py`, `backend/providers/geocoding.py`

**Changes**:
- Use `requests.adapters.HTTPAdapter(max_retries=retry_strategy)` with:
  ```python
  from urllib3.util.retry import Retry
  retry_strategy = Retry(
      total=2,
      backoff_factor=0.5,
      status_forcelist=[429, 500, 502, 503, 504],
      allowed_methods=["GET"],
  )
  ```
- Attach to the `requests.Session` instance

**Benefit**:
- Transient failures (network hiccup, DNS flake, API 503) are automatically retried
- Backoff prevents thundering herd
- 2 retries with 0.5s backoff = ~1.5s added latency on failure, vs. 10s timeout → 503

**Risk**: Low. Adds at most ~3s to worst-case latency instead of returning 503.

**Expected reliability improvement**: High — most intermittent failures will auto-recover on retry

---

## P1 — High Priority

### P1.1: Separate connect / read timeouts

**Files**: `backend/providers/openmeteo_provider.py`, `backend/providers/geocoding.py`

**Changes**:
- Replace `timeout=10` with `timeout=(3, 10)` in all `requests.get()` calls
- First value: connect timeout (3s) — fail fast if host unreachable
- Second value: read timeout (10s) — allow slow responses but not indefinite

**Benefit**:
- Network partition or DNS failure detected in 3s instead of 10s
- Faster failure allows quicker retry

### P1.2: Add exception logging

**Files**: `backend/routers/realtime.py`, `backend/providers/openmeteo_provider.py`, `backend/providers/geocoding.py`

**Changes**:
- Add `logger.exception("Open-Meteo forecast failed: %s", e)` before every `raise ProviderConnectionError`
- Add `logger.exception("Geocoding failed: %s", e)` before every `raise ProviderConnectionError`
- In `realtime.py`, add `logger.warning()` before each `HTTPException` raise

**Benefit**: Stack traces and error context visible in Azure App Service log stream.

### P1.3: Add per-provider latency instrumentation

**Files**: `backend/providers/openmeteo_provider.py`, `backend/providers/geocoding.py`

**Changes**:
- Wrap each HTTP call with `time.perf_counter()` timing
- Log at INFO level: `"Geocoding took 342ms"`, `"Forecast took 812ms"`
- Log WARNING when any call exceeds a threshold (e.g. 3s)

**Benefit**: Enables monitoring dashboard to identify which provider is slow.

---

## P2 — Medium Priority

### P2.1: Externalize timeout configuration

**Files**: `backend/config.py`, `backend/providers/openmeteo_provider.py`, `backend/providers/geocoding.py`

**Changes**:
- Read timeout values from environment variables:
  - `OPENMETEO_CONNECT_TIMEOUT` (default: 3)
  - `OPENMETEO_READ_TIMEOUT` (default: 10)
  - `GEOCODING_CONNECT_TIMEOUT` (default: 3)
  - `GEOCODING_READ_TIMEOUT` (default: 5)
  - `AUTH_TIMEOUT` (default: 10)

**Benefit**: Tune timeouts per environment without code changes.

### P2.2: Add circuit breaker

**File**: `backend/providers/openmeteo_provider.py` (or a new wrapper)

**Changes**:
- Wrap provider calls with a circuit breaker (e.g. `pybreaker` or `circuitbreaker` library)
- After 5 consecutive failures, open the circuit for 30s
- During open circuit, fail fast without making the HTTP call

**Benefit**: Prevents cascading timeout pile-ups when Open-Meteo is degraded.

### P2.3: Degraded mode with cached/last-known data

**File**: `backend/routers/realtime.py`

**Changes**:
- Store last successful weather data per city in a cache (Redis or in-memory)
- On provider failure, return a prediction based on cached data with `"data_source": "cached"` in the response
- Log the degraded state prominently

**Benefit**: Users never see 503 — they get a prediction based on recent data with a caveat.

---

## P3 — Future

### P3.1: Async HTTP with concurrent calls

**Changes**:
- Use `httpx.AsyncClient` instead of `requests`
- Auth verification, geocoding, and Open-Meteo forecast can run in parallel (auth is independent of geocoding)
- Reduces total wall-clock time by running external calls concurrently

**Benefit**: ~1.5s total instead of ~2.5s wall-clock for 3 serial calls.

**Risk**: High — requires refactoring synchronous route handler to async.

---

## Implementation Order

```
Sprint 1 (Hotfix — this sprint):
  Wait — audit only, no implementation.

Sprint 2 (Immediate):
  P0.1: requests.Session + connection pooling
  P0.2: @lru_cache on geocode()
  P0.3: Retry with exponential backoff
  P1.2: Exception logging

Sprint 3 (Short-term):
  P1.1: Separate connect/read timeouts
  P1.3: Per-provider latency logging
  P2.1: Externalize timeout configuration

Sprint 4 (Medium-term):
  P2.3: Degraded mode with cached fallback
  P2.2: Circuit breaker

Sprint 5 (Long-term):
  P3.1: Async HTTP with concurrent calls
```

---

## Expected Outcome After Sprint 2

| Metric | Before | After (est.) |
|--------|--------|-------------|
| Success latency | 1.5-2.0s | 1.0-1.5s |
| Failure rate (503) | ~5-15% | <0.5% |
| Failure mode | Hard 503 | Transient → auto-retry; persistent → 503 with logged cause |
| Observability | No provider timing | Per-call latency logged |
| Connection behavior | New TCP per call | Persistent connection pool |
| Geocoding overhead | 3rd call every request | Cached after first use |
