# 09 — Realtime Performance Audit

## TASK 1 — Request Flow Mapping

```
Client (Browser / Mobile)
  │
  │  GET /api/prediksi/realtime?wilayah=Pekanbaru
  ▼
┌──────────────────────┐
│  Frontend (React)    │     No backend network call
└────────┬─────────────┘
         │  HTTP GET (with Authorization: Bearer <token>)
         ▼
┌──────────────────────────────────────┐
│  Backend Auth Middleware             │
│  → verify_access_token()             │
│  → httpx.Client(timeout=15.0)       │  NETWORK CALL #1
│  → GET {SUPABASE_URL}/auth/v1/user   │  External: Supabase Auth
└────────┬─────────────────────────────┘
         │  Auth passes (503 occurs AFTER auth)
         ▼
┌──────────────────────────────────────┐
│  Realtime Router                     │
│  → _provider.get_weather_history()   │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  OpenMeteoProvider                   │
│  → geocode(wilayah)                  │  NETWORK CALL #2
│  → requests.get(timeout=10)          │  External: geocoding-api.open-meteo.com
│  → GET /v1/search?name=...&count=1   │
└────────┬─────────────────────────────┘
         │  Returns GeoLocation(lat, lon)
         ▼
┌──────────────────────────────────────┐
│  OpenMeteoProvider                   │
│  → get_weather_history()             │  NETWORK CALL #3
│  → requests.get(timeout=10)          │  External: api.open-meteo.com
│  → GET /v1/forecast?latitude=...     │
│    &longitude=...&daily=...          │
│    &start_date=...&end_date=...      │
└────────┬─────────────────────────────┘
         │  Returns RawWeatherData[14]
         ▼
┌──────────────────────────────────────┐
│  Prediction Gateway                  │   No network calls
│  → build_prediction_features_v2()    │   Pure Python + pandas
│  → build_features_v2()               │
│  → compute_rain7() (rolling sum)     │
└────────┬─────────────────────────────┘
         │  Feature dict {RR, Rain7, RH_avg, Tavg}
         ▼
┌──────────────────────────────────────┐
│  ML Predictor                        │   Local file read (joblib)
│  → prediksi()                        │   Reads random_forest_v2.pkl
│  → predict_rf()                      │   from disk (lazy-loaded, cached)
│  → joblib.load()                     │   No network call
└────────┬─────────────────────────────┘
         │  FRI value
         ▼
┌──────────────────────────────────────┐
│  Recommendation Engine               │   No network calls
│  → score_commodities(fri)            │   Pure Python
│  → recommend(top_n)                  │
│  → explain_recommendation()          │
│  → get_mitigasi()                    │
└────────┬─────────────────────────────┘
         │  Complete response
         ▼
┌──────────────────────────────────────┐
│  Response Serialization + Return     │
└──────────────────────────────────────┘
```

### Network Calls per Request: 3

| # | Service | URL | Library | Timeout |
|---|---------|-----|---------|---------|
| 1 | Supabase Auth | `{SUPABASE_URL}/auth/v1/user` | httpx | 15s |
| 2 | Open-Meteo Geocoding | `https://geocoding-api.open-meteo.com/v1/search` | requests | 10s |
| 3 | Open-Meteo Forecast | `https://api.open-meteo.com/v1/forecast` | requests | 10s |

All three are serial — each must complete before the next starts.

---

## TASK 2 — Timeout Audit

### Inventory of every HTTP call

#### 1. `backend/services/auth_service.py:78` — Supabase Auth
```python
with httpx.Client(timeout=15.0) as client:
    response = client.request(method, url, headers=headers, json=json_body)
```
- **Library**: httpx
- **Timeout**: 15.0 seconds (hardcoded, not configurable via env)
- **Retry policy**: None
- **Connection reuse**: New `httpx.Client()` created on every call (no session reuse)
- **Backoff**: None
- **Circuit breaker**: None

#### 2. `backend/providers/geocoding.py:34` — Open-Meteo Geocoding
```python
resp = requests.get(GEOCODING_URL, params={"name": wilayah, "count": 1}, timeout=10)
```
- **Library**: requests
- **Timeout**: 10 seconds (hardcoded)
- **Retry policy**: None
- **Connection reuse**: Raw `requests.get()` — no Session, no connection pooling
- **Backoff**: None
- **Circuit breaker**: None

#### 3. `backend/providers/openmeteo_provider.py:45` — Open-Meteo Forecast (get_current_weather)
```python
resp = requests.get(WEATHER_URL, params=params, timeout=10)
```
- **Library**: requests
- **Timeout**: 10 seconds (hardcoded)
- **Retry policy**: None
- **Connection reuse**: Raw `requests.get()` — no Session, no connection pooling
- **Backoff**: None
- **Circuit breaker**: None

#### 4. `backend/providers/openmeteo_provider.py:116` — Open-Meteo Forecast (get_weather_history)
```python
resp = requests.get(WEATHER_URL, params=params, timeout=10)
```
- Same as #3 above. Identical pattern.

### Missing retries — complete inventory

| Call | Retries | Backoff | Circuit Breaker |
|------|---------|---------|-----------------|
| Supabase Auth | ❌ | ❌ | ❌ |
| Open-Meteo Geocoding | ❌ | ❌ | ❌ |
| Open-Meteo Forecast | ❌ | ❌ | ❌ |

### Connection reuse — audit

Every external HTTP call creates a **brand new TCP connection**:

- `backend/services/auth_service.py:78`: `with httpx.Client(timeout=15.0) as client:` — context manager creates/destroys client per call
- `backend/providers/geocoding.py:34`: `requests.get(...)` — no Session
- `backend/providers/openmeteo_provider.py:45,116`: `requests.get(...)` — no Session

Under concurrent load, this causes:
- TCP handshake overhead per request (SYN, SYN-ACK, ACK = ~1 RTT each)
- TLS negotiation overhead per request (~2-3 RTTs each)
- Ephemeral port exhaustion under high concurrency
- No keep-alive reuse

### Timeout Configuration Gaps

| Gap | Detail |
|-----|--------|
| No connect timeout separation | Single `timeout=10` covers both connect + read. A connect timeout should be shorter (e.g. 3-5s) to fail fast on network issues. |
| No read timeout separation | Unable to distinguish "cannot connect" from "slow response". |
| No total request timeout | No upper bound on total pipeline time. If auth takes 14s, geocoding takes 9s, forecast takes 9s, the total is 32s before the user sees an error. |
| Hardcoded values | All timeouts are hardcoded literals. Not configurable via environment variables. |

### Critical Finding

The realtime endpoint's `get_weather_history` (openmeteo_provider.py:116) calls the **forecast** endpoint with `start_date` = (today - 13 days) and `end_date` = today. This is a single request returning 14 days of data. The timeout of 10 seconds is reasonable for this call, but:

- **No retry on transient failure**: A single DNS hiccup or TCP drop causes `ProviderConnectionError` → HTTP 503.
- **No fallback**: If this call fails, the entire prediction fails. There is no degraded mode using cached data or partial data.

---

## TASK 5 — Logging Audit

### Current Logging Points

| File | Line | What is logged |
|------|------|----------------|
| `backend/middleware.py:16` | Request path + method | After auth, before route handler |
| `backend/middleware.py:19` | Status code + elapsed ms | After response |
| `backend/routers/realtime.py:59` | Wilayah, FRI, risk level, history count | On success only |

### What is NOT logged

| Gap | Impact |
|-----|--------|
| Provider exceptions are NOT logged before re-raise | The `except ProviderConnectionError` in `realtime.py:44` re-raises as HTTPException(503) with NO `logger.exception()` or `logger.error()` call. The original exception message (which may contain timeout reason) is lost. |
| Stack traces are NOT preserved | All `except` blocks in `realtime.py` (lines 42-47) use `raise HTTPException(...)` without `logger.exception()`. The traceback is suppressed. |
| Timeout reason is invisible | The `requests.RequestException` caught in `openmeteo_provider.py:47` and `geocoding.py:36` is converted to `ProviderConnectionError` with a generic message. Whether it was a timeout, connection refused, or DNS failure is indistinguishable. |
| No per-call latency tracking | Auth latency, geocoding latency, Open-Meteo latency are not measured individually. Only total request time is available (from middleware). |
| No failure counters | No metric for how often geocoding vs. forecast fails. |
| No slow-call warnings | No logging when a single provider call exceeds a threshold (e.g. >3s). |
| Feature engineering / ML latency not tracked | No timing around `build_features_v2`, `prediksi`, or `predict_rf`. |
| No structured logging | All logging is plain text. No JSON-structured logs for log aggregation. |

### Recommended Observability Additions

1. `logger.exception()` in every `except` block in `realtime.py` before raising HTTPException
2. Per-provider latency instrumentation (timing before/after each external call)
3. Separate timeout reason logging (connect vs. read)
4. Warning log when a provider call exceeds a warning threshold (e.g. 3s)
5. Failure counter metrics for each provider (geocoding, forecast, auth)
6. Structured JSON logging for machine parsing

---

## TASK 6 — Performance Audit

### Latency Budget Table

| Component | Type | Expected Latency | Worst Case | Network? |
|-----------|------|-----------------|------------|----------|
| Auth (Supabase token verify) | External HTTP | ~200-400ms | 15,000ms (timeout) | Yes — 1 call |
| Geocoding | External HTTP | ~200-500ms | 10,000ms (timeout) | Yes — 1 call |
| Open-Meteo Forecast (14d) | External HTTP | ~500-1,500ms | 10,000ms (timeout) | Yes — 1 call |
| Feature Engineering (v2) | Local CPU | ~10-50ms | 100ms | No |
| Random Forest Prediction | Local CPU + disk I/O | ~5-20ms | 100ms | No (cached model) |
| Recommendation Engine | Local CPU | ~15-50ms | 100ms | No |
| Response Serialization | Local CPU | ~1-5ms | 10ms | No |
| **Total (success)** | | **~1.0-2.5s** | **~35s (if all timeout)** | **3 calls** |
| **Observed success** | | **1.5-2.0s** | | |
| **Observed failure** | | **10-11s** | | |

### Analysis

- **Success** (1.5-2.0s): Auth ~200ms + Geocoding ~300ms + Forecast ~800ms + ML ~100ms = ~1.4s. Matches observation.
- **Failure** (10-11s): Auth passes quickly (~200ms) + Geocoding or Forecast hits timeout (~10s). Matches observation exactly.

The 10-11s failure time strongly suggests **one of the Open-Meteo calls is timing out** at its 10-second limit. The auth call has a 15s timeout but completes quickly (otherwise we'd see 401, not 503).

---

## TASK 7 — Reliability Audit

### Current State

| Reliability Feature | Status | Details |
|--------------------|--------|---------|
| Retry support | ❌ | No retries on any external call |
| Connection pooling | ❌ | Every call creates new TCP + TLS connection |
| Session reuse | ❌ | No `requests.Session` or reusable `httpx.Client` |
| Cache support | ❌ | Geocoding results are NOT cached. Called every request. |
| Graceful degradation | ❌ | Any provider failure = whole request fails |
| Failure recovery | ❌ | No degraded mode, no fallback data |
| Circuit breaker | ❌ | No protection against cascading failures |
| Bulkhead isolation | ❌ | Auth, geocoding, and forecast share same thread pool |

### Production Risks

| Risk | Likelihood | Impact | Description |
|------|-----------|--------|-------------|
| Open-Meteo API rate limiting | Medium | High | No retry with backoff. A 429 from Open-Meteo causes a 503 to user. |
| DNS instability from Azure | Low | High | DNS resolution for open-meteo.com may be slow on cold start. Raw `requests.get()` doesn't reuse DNS cache of a Session. |
| Ephemeral port exhaustion | Medium (high concurrency) | High | No connection pooling means each request uses a new port. Under load, ports can be exhausted. |
| Supabase Auth regional latency | Low | Medium | Single 15s timeout. No fallback auth mechanism. |
| Geocoding API slowdown | Medium | High | Every request depends on geocoding. A 5s geocode delay adds 5s to every prediction. |
| Cascade failure | Medium | Critical | If Open-Meteo is slow, ALL requests queue up and timeout, making the entire endpoint unavailable. |
