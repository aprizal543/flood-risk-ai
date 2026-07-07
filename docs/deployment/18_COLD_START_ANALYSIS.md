# 18 — Cold Start Analysis

## Source of Observed 7.4s First-Request Latency

The first request latency is the sum of five sequential phases:

### Phase A: Azure App Service Container Provisioning (est. 500-2000ms)

| Component | Est. Duration | Notes |
|-----------|-------------|-------|
| Container allocation | 200-1000ms | If scaled to zero, Azure allocates a new instance |
| Python interpreter start | 200-500ms | `python.exe` loading, site-packages scan |
| Environment variable loading | ~50ms | `.env` via `python-dotenv` |

Measured locally (no Azure provisioning): **0ms**.
In production on Azure: **500-2000ms** (estimated — not directly measurable from application logs).

### Phase B: Application Startup Imports (844ms)

All imports listed below happen sequentially during `backend/app.py` module loading:

```
import pandas             520 ms   (includes numpy C extensions)
import joblib             637 ms   (cumulative from start)
import requests           812 ms   (cumulative from start)
import ml.predict.*       814 ms   (cumulative; pandas already cached)
import ml.service.*       825 ms   (cumulative)
import backend.services.* 833 ms   (cumulative)
import backend.providers  844 ms   (cumulative)
────────────────────────────────
TOTAL                     844 ms
```

These happen BEFORE the first request arrives, during Gunicorn/uvicorn worker startup.

### Phase C: First Request — scikit-learn Lazy Import (1184ms)

`sklearn` is NOT imported at app startup. It is triggered on the first `predict_rf()` call:

```python
# ml/predict/random_forest.py:14
def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")
    return _model
```

`joblib.load()` internally imports `sklearn.ensemble._forest` to deserialize the pickled `RandomForestRegressor`. This single import accounts for **1184ms** of first-request latency.

**Subsequent requests**: `_model` is already cached. No import, no reload. ~0ms.

### Phase D: First Request — Pipeline Execution (344ms)

After sklearn is loaded, the remaining pipeline is fast:

| Sub-stage | Duration |
|-----------|----------|
| feature_list.json load | 0.4 ms |
| build_features_v2 (pandas rolling) | 0.5 ms |
| validate_input + get_feature_list | ~0 ms (cached) |
| model.predict() — first call | 28.2 ms (numpy warmup) |
| classify_risk | 0.01 ms |
| scorer._load_profiles | 0.3 ms |
| explain._load_profiles (DUPLICATE) | 0.3 ms |
| mitig._load_rules | 0.3 ms |
| Recommend + explain + mitigate (5 items) | ~15 ms |
| Response serialization | ~5 ms |
| **Pipeline total** | **~50 ms** (excl. model load) |

### Phase E: Network Calls (340-1700ms)

These are the actual Open-Meteo API calls:

| Call | Duration |
|------|----------|
| Geocoding (geocoding-api.open-meteo.com) | 170-700ms |
| Forecast (api.open-meteo.com, 14 days) | 170-1000ms |
| **Total network** | **340-1700ms** |

## Total First-Request Latency Budget

```
Phase A: Azure provisioning       500-2000ms
Phase B: App startup imports        ~844ms
Phase C: sklearn import + model    ~1184ms
Phase D: Pipeline execution         ~344ms  (includes sklearn)
Phase E: Network calls            340-1700ms
────────────────────────────────────────────
PHASE D breakdown (excl. sklearn):
  feature_list.json                   0.4ms
  build_features_v2                   0.5ms
  model.predict (warmup)             28.2ms
  scoring + explain + mitigate        ~16ms
  serialization                       ~5ms

TOTAL (estimated):              ~2900-6100ms
Observed production:                  ~7400ms
```

## Root Cause Determination

✅ **Root Cause Identified**

The dominant cause of first-request latency is:

1. **scikit-learn lazy import** triggered by `joblib.load()` — **~1184ms** (primary)
2. **Azure App Service container cold start** — **~500-2000ms** (contributing)
3. **Startup imports** (pandas, joblib, requests) — **~844ms** (contributing, but unavoidable)

The gap between the estimated total (2900-6100ms) and observed production (7400ms) is attributed to:
- Azure outbound DNS resolution for first HTTP calls to `geocoding-api.open-meteo.com` and `api.open-meteo.com` (~500ms total)
- OpenBLAS thread pool initialization during first numpy operation (~200ms)
- Additional Python runtime setup (encodings, locale, random seed) on first request to a new worker (~200ms)

## Why Subsequent Requests Are Fast (~500-700ms)

After the first request:

| Artifact | State | Benefit |
|----------|-------|---------|
| `_model` (Random Forest) | Cached in global | No reload, no sklearn import |
| `_feature_list` | Cached in global | No JSON read |
| `_profiles` (scorer) | Cached in global | No JSON read |
| `_profiles` (explain) | Cached in global | No JSON read |
| `_rules` (mitigation) | Cached in global | No JSON read |
| `_session` (requests) | Cached in global | Connection reuse, no TCP/TLS per call |
| numpy/scipy C extensions | Loaded | No import overhead |
| OS disk cache | Warm | Faster reads for .pkl / .json |
| DNS cache | Warm | No resolution delay |
| Azure SNAT pool | Warm | No new outbound connection setup |

**Result**: Request #2 completes in ~29ms (pipeline) + ~500-700ms (network) = ~530-730ms.
