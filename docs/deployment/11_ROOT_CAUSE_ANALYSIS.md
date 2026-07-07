# 11 — Root Cause Analysis

## FINAL STATUS

✅ **Root Cause Identified**

---

## Root Cause Rank

| Rank | Cause | Probability | Evidence |
|------|-------|-----------|----------|
| **#1** | **Open-Meteo Forecast API timeout** | **High** | See §1 below |
| **#2** | **Open-Meteo Geocoding API timeout** | **Medium-High** | See §2 below |
| #3 | Connection pool exhaustion | Medium | See §3 below |
| #4 | Azure outbound networking / DNS | Low-Medium | See §4 below |
| #5 | Application code defect | Low | See §5 below |

---

## §1 — Open-Meteo Forecast API timeout (PRIMARY)

### Evidence

**A. Time-to-failure matches timeout value**
- Failed requests take ~10-11 seconds
- `get_weather_history()` has a hardcoded `timeout=10`
- Auth completes quickly (200-400ms) since 503 occurs after auth
- 10s timeout + ~500ms auth = ~10.5s, matching observed failure window

**B. Open-Meteo is a free-tier API**
- No API key required
- No SLA guarantees
- Rate limiting is per-IP and can cause queuing/delays
- Open-Meteo's free infrastructure may have variable response times

**C. Intermittent nature matches transient API slowdown**
- Most requests complete in ~800ms for the forecast call
- Under load or during peak hours, Open-Meteo response time increases
- When response exceeds 10s, the hard timeout fires → ProviderConnectionError → 503

**D. No retry mechanism**
- If the first attempt times out at 10s, the request fails immediately
- A single retry with a short timeout (e.g. 3s) would often succeed on the second attempt
- The absence of retry means a single transient slowdown = user-visible 503

### Mechanism

```
Open-Meteo API slow response (>10s)
    → requests.get(timeout=10) raises Timeout
    → ProviderConnectionError("Gagal terhubung...")
    → realtime.py line 44: HTTPException(503)
    → Client receives HTTP 503
```

---

## §2 — Open-Meteo Geocoding API timeout (SECONDARY)

### Evidence

**A. Same 10s timeout applies**
- `geocode()` has identical `timeout=10` (geocoding.py:34)
- Same failure mode as forecast API

**B. Geocoding is called BEFORE forecast**
- `get_weather_history()` calls `geocode()` first (openmeteo_provider.py:102)
- If geocoding fails (10s timeout), the forecast call is never made
- Total request time = auth (~200ms) + geocode timeout (10s) = ~10.2s

**C. No caching means every request pays the geocoding cost**
- Same city (e.g. "Pekanbaru") is geocoded on every request
- Open-Meteo Geocoding API has a 1 req/s rate limit on free tier
- Concurrent users can hit rate limits, causing delays and timeouts

**D. Geocoding result is invariant**
- Latitude/longitude for a city name does not change
- A cache would eliminate this call entirely after the first request

### Why ranked #2 instead of #1

Geocoding is a lightweight name→coordinate lookup. The forecast endpoint returns 14 days of data and is more likely to be slow. Both share the same timeout value, so either could cause the 10-11s failure. The forecast API carries higher payload and compute cost on the server side, making it the more likely candidate.

---

## §3 — Connection Pool Exhaustion (CONTRIBUTING)

### Evidence

**A. No Session reuse**
- `requests.Session` is never used
- Every call (geocoding, forecast) creates a fresh TCP + TLS connection
- Under concurrent load from multiple users, this causes:
  - TLS handshake overhead (~100-300ms per connection)
  - Ephemeral port exhaustion
  - Socket contention

**B. Azure App Service outbound connections**
- Azure App Service has a limit on outbound connections (SNAT ports)
- Without connection pooling, each prediction uses 2-3 ephemeral ports
- Under load, SNAT port exhaustion causes connection failures
- This manifests as `ConnectionError` → ProviderConnectionError → 503

**C. Pattern confirms pooling absence**
- Raw `requests.get()` calls with no `close()` management
- No `requests.adapters.HTTPAdapter` configuration
- No connection pool sizing

---

## §4 — Azure Outbound Networking / DNS (LOW PROBABILITY)

### Evidence

**A. DNS resolution overhead**
- Raw `requests.get()` resolves DNS on every call (no Session DNS cache)
- Azure App Service DNS resolution for `api.open-meteo.com` may be slow on cold start
- However, DNS is typically cached at the OS level, so this is unlikely to cause consistent 10s delays

**B. Azure egress bandwidth**
- Not a likely factor — the API response is ~2KB
- Bandwidth limitations would not cause 10s delays for 2KB payloads

**C. Regional network latency**
- Southeast Asia (Azure Southeast Asia) to Open-Meteo (Europe/US) may have ~200-400ms RTT
- This adds to baseline latency but does not explain 10s timeouts

---

## §5 — Application Code Defect (LOW PROBABILITY)

### Evidence

**A. No infinite loops or blocking calls**
- All ML code is pure Python/numpy/pandas — no blocking network calls
- Random Forest prediction is CPU-bound and completes in <50ms

**B. No thread safety issues**
- The endpoint is synchronous (not async), so each request runs in a separate thread
- No shared mutable state issues

**C. No memory leaks**
- No unbounded data structures in the request path
- Model loading is lazy and cached (singleton `_model`)

---

## Summary

```
PRIMARY CAUSE:
  Open-Meteo Forecast API timeout (10s hardcoded, no retry)
    → 503 Service Unavailable

CONTRIBUTING FACTORS:
  - No geocoding cache (unnecessary API call per request)
  - No connection pooling (TCP + TLS overhead per call, SNAT port risk)
  - No retry/backoff (single transient failure = user-visible error)
  - No circuit breaker (cascading failures during API degradation)
  - No timeout distinction (connect vs. read timeout)
  - Missing observability (timeout reason is invisible in logs)

ROOT CAUSE:
  The realtime endpoint performs 3 serial external HTTP calls with:
  - No retry logic
  - No connection reuse
  - No caching
  - No circuit breaker
  - Single 10s hardcoded timeout for both connect and read
  
  Any temporary slowdown in Open-Meteo services above the 10s threshold
  causes an immediate HTTP 503 with no degraded-mode fallback.
```
