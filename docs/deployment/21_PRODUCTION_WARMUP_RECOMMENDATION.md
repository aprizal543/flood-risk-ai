# 21 — Production Warm-Up Recommendations

> **This document proposes optimizations only. No implementation in this sprint.**

## Root Cause Summary

The 5-6 second first-request overhead is driven by three sequential phases:

| Phase | Duration | % of Overhead | Root Cause |
|-------|----------|---------------|------------|
| Azure container provisioning | 500-2000ms | ~25% | Platform cold start |
| Startup imports (pandas, joblib, requests) | 844ms | ~15% | Python module initialization |
| **sklearn lazy import via joblib.load()** | **~1184ms** | **~25%** | **Lazy scikit-learn import on first predict** |
| Pipeline execution | ~344ms | ~7% | Includes sklearn import above |
| Network calls (geocoding + forecast) | 340-1700ms | ~28% | Two serial HTTP requests |

## Recommended Optimizations

Ranked by Impact / Complexity / Risk:

### P0: Eager sklearn import at startup

| Property | Value |
|----------|-------|
| Impact | **~1184ms reduction** on first request |
| Complexity | Very Low (1 line) |
| Risk | Very Low (import only, no state change) |
| File | `ml/predict/random_forest.py` |

Add an eager import of the sklearn ensemble module at module load time. This moves the 1184ms import cost from first request to app startup (where it overlaps with other startup tasks):

```python
# At module level in random_forest.py — triggers eager sklearn import
import sklearn.ensemble._forest  # noqa: F401
```

**Trade-off**: Increases app startup time by ~1184ms but eliminates the first-request penalty entirely.

### P1: Preload model at startup

| Property | Value |
|----------|-------|
| Impact | **~40ms additional reduction** (pure deserialization) |
| Complexity | Low |
| Risk | Low |
| File | `ml/predict/random_forest.py` |

Call `_load_model()` during app initialization to eagerly deserialize the model:

```python
# At module level in random_forest.py
_model = joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")
```

Or via the existing `_load_model()` after the eager sklearn import:

```python
# At module level
import sklearn.ensemble._forest
_load_model()
```

**Trade-off**: Increases memory usage (model loaded even if never used). But since the realtime endpoint always uses RF, this is fine.

### P2: Eliminate duplicate commodity_profiles.json load

| Property | Value |
|----------|-------|
| Impact | ~0.3ms reduction (minor) |
| Complexity | Low |
| Risk | Very Low |
| Files | `ml/recommendation/scorer.py`, `ml/recommendation/explain.py` |

Both modules load the same file independently. Either:
- Share a single cache via a common module
- Have explain.py import the already-loaded data from scorer.py

**Trade-off**: Marginal latency benefit on first request, but reduces disk I/O.

### P3: Warm-up endpoint

| Property | Value |
|----------|-------|
| Impact | Eliminates ALL first-request overhead for real users |
| Complexity | Medium |
| Risk | Low |
| Files | `backend/app.py` (or new startup handler) |

Add a startup event or health-check handler that eagerly:
1. Imports all heavy modules
2. Calls `_load_model()` to deserialize the RF
3. Calls `get_feature_list()` to cache feature list
4. Calls `_load_profiles()` (both scorer and explain)
5. Calls `_load_rules()` to cache mitigation rules
6. Calls `_get_session()` (both geocoding and openmeteo) to warm connection pools
7. Performs a dummy prediction to warm numpy/scikit-learn thread pools

```python
@app.on_event("startup")
async def warmup():
    # Eager-load model and warm caches
    from ml.predict.random_forest import _load_model
    from ml.recommendation.scorer import _load_profiles
    from ml.recommendation.explain import _load_profiles as _explain_profiles
    from ml.recommendation.mitigation import _load_rules
    from ml.predict.preprocess import get_feature_list

    get_feature_list()
    _load_model()
    _load_profiles()
    _explain_profiles()
    _load_rules()

    # Warm numpy/scikit-learn thread pool with a dummy predict
    import pandas as pd
    model = _load_model()
    df = pd.DataFrame([[10.0, 37.0, 80.0, 27.5]], columns=["RR", "Rain7", "RH_avg", "Tavg"])
    model.predict(df)
```

**Trade-off**: Increases app startup time by ~1500ms but eliminates ALL first-request cold-start penalties.

### P4: Connection pool pre-warming

| Property | Value |
|----------|-------|
| Impact | Eliminates DNS + TCP + TLS from first network call |
| Complexity | Low |
| Risk | Low |
| Files | `backend/providers/geocoding.py`, `backend/providers/openmeteo_provider.py` |

Pre-establish connections during startup by calling `_get_session()` in both provider modules:

```python
# At module level in openmeteo_provider.py
_get_session()  # Warm connection pool to api.open-meteo.com
```

**Trade-off**: Creates connections that may timeout before first request (default keep-alive: ~60s). Mitigate with a lightweight health-check endpoint that users hit first.

## Comparison: No Optimization vs P0+P1+P3

| Metric | Current | After P0+P1+P3 | Improvement |
|--------|---------|----------------|-------------|
| First request (pipeline only) | 1528ms | ~50ms | **30x** |
| First request (no network) | ~1528ms | ~50ms | -1478ms |
| First request (with network) | ~3500ms | ~1600ms | -1900ms |
| App startup time | 844ms | ~2400ms | +1556ms (acceptable, happens before traffic) |
| Steady-state request | ~29ms | ~29ms | No change |

## Additional Low-Impact Recommendations

| Suggestion | Impact | Complexity | Risk |
|-----------|--------|-----------|------|
| Sort imports: `import pandas` before others | ~50ms overlap | Very Low | None |
| Use `importlib.import_module()` for cold-start overlap | Unknown | Medium | Low |
| Pin Azure App Service to "Always On" | Eliminates container provisioning entirely | Very Low | Low (cost implication) |
| Use Azure App Service warm-up slot | Eliminates container provisioning | Low | Low |

## Final Recommendation (Sprint Sequence)

| Sprint | Items | Expected First-Request Latency |
|--------|-------|-------------------------------|
| Current baseline | — | ~7400ms |
| Sprint 1 | P0 (eager sklearn import) | ~6200ms |
| Sprint 2 | P1 (preload model) | ~6100ms |
| Sprint 3 | P3 (warm-up endpoint) | ~1600ms |
| Sprint 4 | Always On + DNS pre-warm | ~900ms |

The **single highest-impact change** is **P0: eager sklearn import at startup**. This is a 1-line addition that moves 1184ms of latency from first-request critical path to app startup critical path (where it overlaps with other startup work).
