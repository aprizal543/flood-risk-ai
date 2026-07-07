# 19 — Model Loading Audit

## Artifact Inventory

| Artifact | Size | Format | Load Point | Trigger | Cache |
|----------|------|--------|------------|---------|-------|
| `random_forest_v2.pkl` | 5.3 MB | joblib/pickle | First `predict_rf()` call | `_load_model()` | Module global `_model` |
| `feature_list.json` | 44 B | JSON | First `get_feature_list()` call | Any feature validation | Module global `_feature_list` |
| `commodity_profiles.json` | 6.6 KB | JSON | First `score_commodities()` call | `scorer._load_profiles()` | Module global `_profiles` |
| `commodity_profiles.json` | 6.6 KB | JSON | First `explain_recommendation()` call | `explain._load_profiles()` | Module global `_profiles` (DUPLICATE) |
| `mitigation_rules.json` | 3.5 KB | JSON | First `get_mitigasi()` call | `mitigation._load_rules()` | Module global `_rules` |
| `scaler_lstm.pkl` | 1.4 KB | joblib | First LSTM prediction | `preprocess.get_scaler()` | Module global `_scaler` |

## Model Loading Behavior

### random_forest_v2.pkl

**File**: `ml/predict/random_forest.py`

```python
_model: Any = None  # module-level cache

def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")
    return _model
```

| Property | Value |
|----------|-------|
| Load point | First call to `predict_rf()` — happens during first request |
| Load mechanism | `joblib.load()` — pickled scikit-learn `RandomForestRegressor` |
| Side effects | Imports `sklearn.ensemble._forest` and all dependencies |
| File size | 5,307,665 bytes (5.3 MB) |
| Cold load time (incl. sklearn import) | **1183.7 ms** |
| Pure deserialization time | ~40 ms (measured after sklearn cached) |
| Hot load time | ~0 ms (cached in `_model`) |
| Memory after load | ~30-50 MB (Random Forest with ~100 trees × 4 features) |

### feature_list.json

**File**: `ml/predict/preprocess.py`

```python
_feature_list: list[str] | None = None

def get_feature_list() -> list[str]:
    global _feature_list
    if _feature_list is None:
        path = ARTIFACTS_DIR / "feature_list.json"
        _feature_list = json.loads(path.read_text(encoding="utf-8"))
    return _feature_list
```

| Property | Value |
|----------|-------|
| Load point | First call to `get_feature_list()` — first `predict_rf()` via `validate_input()` |
| Cold load time | **0.4 ms** |
| Content | `["RR", "Rain7", "RH_avg", "Tavg"]` |

### commodity_profiles.json (DUPLICATE LOAD)

**File 1**: `ml/recommendation/scorer.py` — `_load_profiles()`
**File 2**: `ml/recommendation/explain.py` — `_load_profiles()`

Each maintains an independent module-level cache:

```python
# scorer.py
_profiles: list[dict] | None = None
def _load_profiles() -> list[dict]:
    global _profiles
    if _profiles is None:
        _profiles = json.loads(path.read_text(encoding="utf-8"))
    return _profiles

# explain.py
_profiles: dict[str, dict] | None = None
def _load_profiles() -> dict[str, dict]:
    global _profiles
    if _profiles is None:
        data = json.loads(path.read_text(encoding="utf-8"))
        _profiles = {p["id"]: p for p in data}
    return _profiles
```

| Property | Value |
|----------|-------|
| Cold load time (each) | **0.3 ms** |
| Total cold load time | **0.6 ms** (two reads of the same file) |

### mitigation_rules.json

**File**: `ml/recommendation/mitigation.py`

| Property | Value |
|----------|-------|
| Cold load time | **0.3 ms** |

## Total Cold-Start Artifact Loading

| Artifact | Duration | % of First-Request Overhead |
|----------|----------|-----------------------------|
| random_forest_v2.pkl (incl. sklearn import) | 1183.7 ms | 99.9% |
| commodity_profiles.json (scorer) | 0.3 ms | <0.1% |
| commodity_profiles.json (explain) | 0.3 ms | <0.1% |
| mitigation_rules.json | 0.3 ms | <0.1% |
| feature_list.json | 0.4 ms | <0.1% |
| requests.Session() | 0.1 ms | <0.1% |
| **Total** | **~1185 ms** | **100%** |

## Loading Lifecycle Summary

| Request # | Model Loaded? | Profiles Loaded? | Session Created? | Pipeline Time |
|-----------|--------------|-----------------|-----------------|--------------|
| 1 | Yes (1184ms) | Yes (0.6ms) | Yes (0.1ms) | ~1528ms |
| 2 | No (cached) | No (cached) | No (cached) | ~29ms |
| 3 | No | No | No | ~33ms |
| 10 | No | No | No | ~28ms |

## Key Finding

The **entire** 1430ms first-request pipeline overhead is driven by a single cause: **lazy import of scikit-learn via `joblib.load()`**. All other artifact loads (JSON files, Session creation) sum to less than 2ms combined.
