# 17 — First-Request Profiling Results

## Overview

Measured every stage of the realtime prediction pipeline using `time.perf_counter()` across fresh subprocesses to simulate true cold starts. All network calls are excluded from pipeline timings (mocked) to isolate application-layer latency.

## Profiling Method

| Phase | Method | What It Measures |
|-------|--------|-----------------|
| Phase 1 | Fresh subprocess | Module import time (app startup) |
| Phase 2 | Fresh subprocess | Artifact loading (model, JSON, session) |
| Phase 3 | Fresh subprocess | First `predict_from_raw()` call after imports |
| Phase 4 | In-process (10 iterations) | Warm-up curve showing request #1 through #10 |
| Phase 5 | In-process | Per-component warmup audit |

## Raw Results

### Phase 1 — Module Import Timing

```
Component                             Duration
import pandas                         519.9 ms
import joblib                         637.0 ms
import requests                       811.6 ms
import json                           811.6 ms
import ml.predict.random_forest       814.5 ms
import ml.service.predictor           825.5 ms
import ml.feature_engineering.builder 828.4 ms
import prediction_gateway             832.9 ms
import openmeteo_provider             843.5 ms
import geocoding                      843.5 ms
─────────────────────────────────────────────
TOTAL                                 843.5 ms
```

Note: Cumulative timings overlap because `pandas` transitively imports `numpy` during its own init. The TOTAL (843ms) is less than the sum of individual imports.

### Phase 2 — Cold Artifact Loading

```
Component                                     Duration
feature_list.json (44 B)                          0.4 ms
commodity_profiles.json (6.6 KB)                  0.3 ms
mitigation_rules.json (3.5 KB)                    0.3 ms
random_forest_v2.pkl (5.3 MB) [includes sklearn]  1183.7 ms  ← DOMINANT
requests.Session() + HTTPAdapter                   0.1 ms
```

The 5.3 MB `random_forest_v2.pkl` load triggers `sklearn.ensemble._forest` import (scikit-learn C extensions), which accounts for ~1180ms of the total. The pure deserialization is ~40ms.

### Phase 3 — First Prediction (Fresh Subprocess)

```
Component                                     Duration
First predict_from_raw() call (cold)          1528.5 ms
```

This is the time from entering `predict_from_raw()` to receiving the result dict, in a process where pandas/joblib/requests are already imported but sklearn has NOT yet been loaded.

### Phase 4 — Warm-Up Curve

```
Request #1:  1459.8 ms   FRI=66.89
Request #2:    29.4 ms   FRI=66.89
Request #3:    32.7 ms   FRI=66.89
Request #4:    28.1 ms   FRI=66.89
Request #5:    30.6 ms   FRI=66.89
Request #6:    28.5 ms   FRI=66.89
Request #7:    30.5 ms   FRI=66.89
Request #8:    31.7 ms   FRI=66.89
Request #9:    33.2 ms   FRI=66.89
Request #10:   27.5 ms   FRI=66.89
─────────────────────────────────────────────
Cold-start overhead:  1432.3 ms
Warm-up ratio:        53.1x
Steady state:         27.5 ms (no network)
```

### Phase 5 — Component Warmup

```
Component                                 Cold       Hot
get_feature_list()                         0.4 ms    ~0 ms
_load_model() [includes sklearn import]  ~1184 ms    ~0 ms
scorer._load_profiles()                    0.3 ms    ~0 ms
explain._load_profiles() (DUPLICATE)        0.3 ms    ~0 ms
mitig._load_rules()                        0.3 ms    ~0 ms
predict_rf()                               28.2 ms   28.2 ms
```

Note: `commodity_profiles.json` is loaded TWICE — once by `scorer.py:_load_profiles()` and again by `explain.py:_load_profiles()` — because they maintain separate module-level caches.

## Execution Timeline

```
Time    Event
────    ─────
+0 ms    Python process start
+200    Azure container provisioning (est.)
+500    Python interpreter init, encodings, site-packages scan
+1344   import pandas (520ms)
+1460   import joblib (637ms cumulative)
+1630   import requests (812ms cumulative)
+1644   All startup imports complete (844ms total)
        ── request arrives ──
+1644   get_feature_list() → reads feature_list.json (0.4ms)
+1644   build_features_v2() → pandas rolling operations (0.5ms)
+1645   prediksi() → validate_input → get_feature_list (cached)
+1645   predict_rf() → _load_model()
+1645   → joblib.load("random_forest_v2.pkl")
+1645   → sklearn.ensemble._forest imported (~1180ms)
+2825   → RandomForestRegressor deserialized
+2825   model.predict(df) → first predict (28ms)
+2853   classify_risk(fri) (0.01ms)
+2853   recommend() → scorer._load_profiles() → commodity_profiles.json (0.3ms)
+2853   → explain._load_profiles() → commodity_profiles.json AGAIN (0.3ms)
+2853   → mitigation._load_rules() → mitigation_rules.json (0.3ms)
+2853   Response serialization + return
+3140   ── prediction returned (1528ms pipeline time) ──
+3140   Total: ~2.4s (no network), ~4-7s (with network + Azure cold start)
```

## Conclusion

The cold-start latency is dominated by **one cause**: `sklearn` (scikit-learn) is imported lazily on the first `joblib.load()` call, when the Random Forest model artifact is deserialized. This accounts for **~1184ms** of the first-request overhead.

All subsequent requests see ~29ms pipeline time because every lazy-loaded artifact is cached in module-level globals.
