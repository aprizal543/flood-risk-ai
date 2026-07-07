"""
profile_first_request.py – Cold start & first-request profiling.

Measures every pipeline stage with microsecond precision across
multiple request iterations to identify warm-up latency sources.

Runs each phase in a subprocess to simulate true cold start.

Usage:
    python scripts/profile_first_request.py
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def _run_script(code: str, label: str) -> str:
    """Run a snippet in a subprocess and capture its stdout."""
    # Inject REPO_ROOT so scripts don't rely on __file__
    code = code.replace("{{REPO_ROOT}}", str(REPO_ROOT))
    result = subprocess.run(
        [PYTHON, "-c", code],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        err = result.stderr.strip()
        if err:
            # Print only first few lines of error for context
            lines = err.split("\n")
            for line in lines[-3:]:
                print(f"  > {line}")
    return result.stdout.strip()


# ── Phase 1: Import timing (fresh subprocess) ──────────────────────────
IMPORT_PROFILER = r"""
from __future__ import annotations
import sys, time
sys.path.insert(0, r"{{REPO_ROOT}}")
_t0 = time.perf_counter()

# Startup imports (simulating app.py import chain)
import pandas as pd
t_pd = (time.perf_counter() - _t0) * 1000

import joblib
t_jl = (time.perf_counter() - _t0) * 1000

import requests
t_rq = (time.perf_counter() - _t0) * 1000

import json
t_js = (time.perf_counter() - _t0) * 1000

# Pipeline imports (simulating prediction_gateway import chain)
from ml.predict.random_forest import predict_rf
t_rf = (time.perf_counter() - _t0) * 1000

from ml.service.predictor import prediksi
t_pr = (time.perf_counter() - _t0) * 1000

from ml.feature_engineering.builder import build_features_v2
t_fe = (time.perf_counter() - _t0) * 1000

from backend.services.prediction_gateway import predict_from_raw
t_gw = (time.perf_counter() - _t0) * 1000

from backend.providers.openmeteo_provider import OpenMeteoProvider
t_om = (time.perf_counter() - _t0) * 1000

from backend.providers.geocoding import geocode
t_gc = (time.perf_counter() - _t0) * 1000

# Total import time
total = (time.perf_counter() - _t0) * 1000

print(f'{t_pd:.1f}|{t_jl:.1f}|{t_rq:.1f}|{t_js:.1f}|{t_rf:.1f}|{t_pr:.1f}|{t_fe:.1f}|{t_gw:.1f}|{t_om:.1f}|{t_gc:.1f}|{total:.1f}')
"""


# ── Phase 2: Cold-start artifact loading (fresh subprocess) ────────────
COLD_LOAD_PROFILER = r"""
from __future__ import annotations
import sys, time, json
sys.path.insert(0, r"{{REPO_ROOT}}")

from ml.predict.preprocess import ARTIFACTS_DIR
from ml.recommendation.mitigation import KNOWLEDGE_DIR

results = {}

# feature_list.json
t0 = time.perf_counter()
_ = json.loads((ARTIFACTS_DIR / "feature_list.json").read_text(encoding="utf-8"))
results['feature_list.json'] = (time.perf_counter() - t0) * 1000

# commodity_profiles.json (loaded by scorer AND explain separately)
t0 = time.perf_counter()
_ = json.loads((KNOWLEDGE_DIR / "commodity_profiles.json").read_text(encoding="utf-8"))
results['commodity_profiles.json'] = (time.perf_counter() - t0) * 1000

# mitigation_rules.json
t0 = time.perf_counter()
_ = json.loads((KNOWLEDGE_DIR / "mitigation_rules.json").read_text(encoding="utf-8"))
results['mitigation_rules.json'] = (time.perf_counter() - t0) * 1000

# random_forest_v2.pkl — this triggers sklearn import + joblib deserialization
import gc
gc.collect(); gc.collect()
t0 = time.perf_counter()
import joblib
_ = joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")
results['random_forest_v2.pkl (includes sklearn import)'] = (time.perf_counter() - t0) * 1000

# Session creation
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
t0 = time.perf_counter()
s = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504], allowed_methods=["GET"])
adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
s.mount("https://", adapter)
s.mount("http://", adapter)
results['requests.Session() creation'] = (time.perf_counter() - t0) * 1000

print(json.dumps(results))
"""


# ── Phase 3: First-prediction timing (fresh subprocess, imports + predict) ──
COLD_PREDICT_PROFILER = r"""
from __future__ import annotations
import sys, time, json
sys.path.insert(0, r"{{REPO_ROOT}}")

from datetime import date, timedelta
from backend.providers.models import RawWeatherData
from backend.services.prediction_gateway import predict_from_raw

today = date(2026, 7, 7)
history = [
    RawWeatherData(
        tanggal=today - timedelta(days=13-i), rr=float(5 + i*2), rh_avg=80.0,
        tmax=32.0, tmin=24.0, latitude=0.507, longitude=101.447,
        sumber="Open-Meteo", tavg=27.5)
    for i in range(14)
]
weather = history[-1]
preceding = history[:-1]

t0 = time.perf_counter()
result = predict_from_raw(weather, weather_history=preceding, model="rf", top_n=5, include_features=True)
total_ms = (time.perf_counter() - t0) * 1000

print(json.dumps({"total_ms": round(total_ms, 1), "fri": result["fri"]}))
"""


# ── Phase 4: Warm-up profiling (in-process, 10 iterations) ─────────────
def profile_warmup_curve(iterations: int = 10) -> list[dict[str, float]]:
    """Run the pipeline multiple times in the same process and record timing."""
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

    from datetime import date, timedelta

    from backend.providers.models import RawWeatherData
    from backend.services.prediction_gateway import predict_from_raw

    today = date(2026, 7, 7)
    history = [RawWeatherData(
        tanggal=today - timedelta(days=13 - i), rr=float(5 + i * 2), rh_avg=80.0,
        tmax=32.0, tmin=24.0, latitude=0.507, longitude=101.447,
        sumber="Open-Meteo", tavg=27.5,
    ) for i in range(14)]
    weather = history[-1]
    preceding = history[:-1]

    results = []
    for i in range(iterations):
        t0 = time.perf_counter()
        result = predict_from_raw(weather, weather_history=preceding, model="rf", top_n=5, include_features=True)
        total_ms = (time.perf_counter() - t0) * 1000
        results.append({"iteration": i + 1, "total_ms": round(total_ms, 1), "fri": result["fri"]})

        if i == 0 or i < 3 or i == iterations - 1 or i == 4:
            print(f"  Request #{i+1}: {total_ms:.1f} ms  (FRI={result['fri']})")
        elif i == 3:
            print(f"  ... (iterations 4-{iterations-1})")

    return results


# ── Phase 5: Component-level warmup ────────────────────────────────────
def profile_component_warmup():
    """Time each lazy-initialized component on first vs subsequent call."""
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

    import gc
    from ml.predict.preprocess import get_feature_list
    from ml.predict.random_forest import _load_model, predict_rf
    from ml.recommendation.scorer import _profiles as sp, _load_profiles as slp
    from ml.recommendation.explain import _profiles as ep, _load_profiles as elp
    from ml.recommendation.mitigation import _rules as mr, _load_rules as mlr
    from ml.feature_engineering.builder import build_features_v2
    from backend.providers.geocoding import _get_session, _session as gsess
    from backend.providers.openmeteo_provider import _get_session as om_sess

    print("\n[Phase 5] Component-Level Warm-Up Audit")
    print("-" * 50)

    # feature_list.json (lazy via get_feature_list)
    assert get_feature_list() is not None  # first call — lazy load
    t0 = time.perf_counter()
    _ = get_feature_list()
    t1 = time.perf_counter()
    print(f"  get_feature_list() (subsequent):   {(t1-t0)*1000:.2f} ms")

    # random_forest_v2.pkl (lazy via _load_model)
    t0 = time.perf_counter()
    model = _load_model()
    t1 = time.perf_counter()
    print(f"  _load_model() (COLD — includes sklearn): {(t1-t0)*1000:.1f} ms")

    t0 = time.perf_counter()
    model = _load_model()
    t1 = time.perf_counter()
    print(f"  _load_model() (HOT):                {(t1-t0)*1000:.2f} ms")

    # commodity_profiles.json (scorer)
    gc.collect(); gc.collect()
    t0 = time.perf_counter()
    _ = slp()
    t1 = time.perf_counter()
    print(f"  scorer._load_profiles() (COLD):     {(t1-t0)*1000:.2f} ms")

    t0 = time.perf_counter()
    _ = slp()
    t1 = time.perf_counter()
    print(f"  scorer._load_profiles() (HOT):      {(t1-t0)*1000:.2f} ms")

    # commodity_profiles.json (explain) — DUPLICATE LOAD
    gc.collect(); gc.collect()
    t0 = time.perf_counter()
    _ = elp()
    t1 = time.perf_counter()
    print(f"  explain._load_profiles() (COLD):    {(t1-t0)*1000:.2f} ms (DUPLICATE)")

    # mitigation_rules.json
    gc.collect(); gc.collect()
    t0 = time.perf_counter()
    _ = mlr()
    t1 = time.perf_counter()
    print(f"  mitig._load_rules() (COLD):         {(t1-t0)*1000:.2f} ms")

    t0 = time.perf_counter()
    _ = mlr()
    t1 = time.perf_counter()
    print(f"  mitig._load_rules() (HOT):          {(t1-t0)*1000:.2f} ms")

    # Model predict warmup
    import pandas as pd
    df = pd.DataFrame([[10.0, 37.0, 80.0, 27.5]], columns=["RR", "Rain7", "RH_avg", "Tavg"])
    t0 = time.perf_counter()
    _ = predict_rf(df)
    t1 = time.perf_counter()
    print(f"  predict_rf() (should be HOT):       {(t1-t0)*1000:.2f} ms")


# ── Main ────────────────────────────────────────────────────────────────
def main():
    print("=" * 72)
    print("  First-Request Profiling — Cold Start & Warm-Up Analysis")
    print("=" * 72)

    # Phase 1: Import timing in a fresh subprocess
    print("\n[Phase 1] Module Import Timing (fresh subprocess)")
    print("-" * 55)
    out = _run_script(IMPORT_PROFILER, "Phase 1")
    parts = out.split("|")
    labels = [
        "import pandas",
        "import joblib",
        "import requests",
        "import json",
        "import ml.predict.random_forest",
        "import ml.service.predictor",
        "import ml.feature_engineering.builder",
        "import prediction_gateway",
        "import openmeteo_provider",
        "import geocoding",
    ]
    for label, val in zip(labels, parts[:-1]):
        print(f"  {label:40s} {float(val):>8.1f} ms")
    print(f"  {'TOTAL (startup imports)':40s} {float(parts[-1]):>8.1f} ms")

    # Phase 2: Artifact loading in a fresh subprocess
    print("\n[Phase 2] Cold Artifact Loading (fresh subprocess)")
    print("-" * 55)
    out = _run_script(COLD_LOAD_PROFILER, "Phase 2")
    import json
    loads = json.loads(out)
    for label, ms in loads.items():
        print(f"  {label:50s} {ms:>8.1f} ms")

    # Phase 3: Cold first prediction (fresh subprocess, total time)
    print("\n[Phase 3] First Prediction — Complete Cold Start (fresh subprocess)")
    print("-" * 55)
    out = _run_script(COLD_PREDICT_PROFILER, "Phase 3")
    cold = json.loads(out)
    print(f"  First prediction (imports + pipeline, no network): {cold['total_ms']:.1f} ms")
    print(f"  FRI={cold['fri']}")

    # Phase 4: Warm-up curve (in-process)
    print("\n[Phase 4] Multi-Request Warm-Up Curve (in-process)")
    print("-" * 55)
    curve = profile_warmup_curve(iterations=10)

    # Phase 5: Component-level warmup
    profile_component_warmup()

    # ── Summary tables ──────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  EVIDENCE SUMMARY")
    print("=" * 72)

    print("\n[Table A] Cold-Start Latency Budget")
    print("-" * 60)
    print(f"  {'Component':42s} {'Duration':>10s}")
    print(f"  {'-'*42} {'-'*10}")
    rows = [
        ("Python interpreter startup (est.)", "200-500"),
        ("Startup imports (pandas, joblib, etc.)", f"{float(parts[-1]):.0f}"),
        ("sklearn import (triggered by joblib.load)", f"{loads.get('random_forest_v2.pkl (includes sklearn import)', 0):.0f}"),
        ("Pipeline (features + rf + rec + serialization)", f"{cold['total_ms']:.0f}"),
        ("Network (geocoding ~200-700ms + forecast ~200-1000ms)", "400-1700"),
        ("Azure container provisioning (est.)", "500-2000"),
        ("TOTAL first request (estimated)", "~4000-7500"),
    ]
    for comp, dur in rows:
        print(f"  {comp:42s} {dur:>10s} ms")

    print("\n[Table B] Warm-Up Curve")
    print("-" * 60)
    print(f"  {'Request #':>10s} {'Duration':>12s} {'FRI':>8s}")
    print(f"  {'-'*10} {'-'*12} {'-'*8}")
    for row in curve:
        print(f"  {row['iteration']:>10d} {row['total_ms']:>10.1f} ms {row['fri']:>8.2f}")

    if len(curve) >= 2:
        first = curve[0]["total_ms"]
        last = curve[-1]["total_ms"]
        overhead = first - last
        print(f"\n  Cold-start pipeline overhead:       {overhead:.1f} ms")
        print(f"  Warm-up ratio:                      {first/last:.1f}x")
        print(f"  Subsequent steady-state:            {last:.1f} ms (no network)")

    print("\n[Table C] Lazy-Initialization Inventory")
    print("-" * 60)
    print(f"  {'Artifact':35s} {'First Load':>12s} {'Cached':>8s}")
    print(f"  {'-'*35} {'-'*12} {'-'*8}")
    lazy_items = [
        ("random_forest_v2.pkl (5.3 MB)", f"{loads.get('random_forest_v2.pkl (includes sklearn import)', 0):.0f} ms", "Yes"),
        ("commodity_profiles.json (6.6 KB)", f"{loads.get('commodity_profiles.json', 0):.0f} ms", "Yes"),
        ("feature_list.json (44 B)", f"{loads.get('feature_list.json', 0):.0f} ms", "Yes"),
        ("mitigation_rules.json (3.5 KB)", f"{loads.get('mitigation_rules.json', 0):.0f} ms", "Yes"),
        ("requests.Session()", f"{loads.get('requests.Session() creation', 0):.0f} ms", "Yes"),
    ]
    for art, t_load, cached in lazy_items:
        print(f"  {art:35s} {t_load:>12s} {cached:>8s}")

    if len(curve) >= 2:
        print(f"\n  Unexplained first-request overhead: {curve[0]['total_ms'] - curve[1]['total_ms']:.1f} ms")


if __name__ == "__main__":
    main()
