# 20 — First Request Timeline

## Complete Execution Flow

```
Time (ms)  Phase
──────────  ────────────────────────────────────────────────────────────────
     0      Azure receives request → App Service cold start triggered
   200      Container provisioned, Python interpreter starts
   325      site-packages scan, .pth files processed
   500      backend/app.py starts executing
   510      sys.path configured
   520      load_backend_environment() → .env parsed (cached by lru_cache)
────────────────────────────────────────────────────────────────────────
 APP STARTUP IMPORTS BEGIN
────────────────────────────────────────────────────────────────────────
   520     from backend.config import load_backend_environment
   520     from fastapi import FastAPI
   521     from fastapi.middleware.cors import CORSMiddleware
   522     from backend.middleware import LoggingMiddleware
  ↑523     from backend.routers.health import router
  ↑524     from backend.routers.prediction import router
            → from backend.services.prediction_gateway import predict_from_raw
              → from ml.service.predictor import prediksi
                → import pandas as pd                         ← 520ms
                → from ml.predict.random_forest import predict_rf
                  → import joblib                              ← 637ms
                  → import pandas (no-op, cached)
                → from ml.predict.risk import classify_risk
                → from ml.recommendation.recommender import recommend
                → from ml.recommendation.explain import ...
                → from ml.recommendation.mitigation import ...
   525     from backend.routers.ai_chat import router
   810     from backend.routers.auth import router
   811     from backend.routers.csv_prediction import router
   812     from backend.routers.info import router
   813     from backend.routers.provider import router
   814     from backend.routers.realtime import router
            → from backend.providers.openmeteo_provider import OpenMeteoProvider
              → import requests                               ← 812ms (cumulative)
              → from urllib3.util.retry import Retry
              → from backend.providers.geocoding import geocode
  1344     app startup complete (844ms total)
  1344     uvicorn/Gunicorn starts listening
────────────────────────────────────────────────────────────────────────
 FIRST REQUEST ARRIVES
────────────────────────────────────────────────────────────────────────
  1344     LoggingMiddleware.dispatch() — RequestID generated
  1344     Auth verify_access_token() → httpx GET to Supabase (~300ms)
  1644     Auth OK → predict_realtime() called
────────────────────────────────────────────────────────────────────────
 PROVIDER LAYER
────────────────────────────────────────────────────────────────────────
  1644     OpenMeteoProvider.get_weather_history("Pekanbaru")
  1644     → geocode("Pekanbaru")
  1644     → _get_session() → requests.Session() + HTTPAdapter  ← 0.1ms
  1644     → _http_get(GEOCODING_URL) → session.get()
  1644     → TCP + TLS to geocoding-api.open-meteo.com
  ~1900    → Response received (geocoding ~256ms)
  ~1900    → _build_daily_params() → params dict
  ~1900    → _http_get(WEATHER_URL) → session.get()
  ~1900    → TCP + TLS to api.open-meteo.com
  ~2700    → Response received (forecast ~800ms)
────────────────────────────────────────────────────────────────────────
 FEATURE ENGINEERING
────────────────────────────────────────────────────────────────────────
  2700     predict_from_raw() → build_prediction_features_v2()
  2700     → build_features_v2()
  2700     → compute_rain7() → pd.Series().rolling(7).sum()
  ↓2701    → Return 4-feature dict → DataFrame
────────────────────────────────────────────────────────────────────────
 ML PREDICTION
────────────────────────────────────────────────────────────────────────
  2701     prediksi() → validate_input()
  2701     → get_feature_list() → feature_list.json (0.4ms)
  2701     → predict_rf(df)
  2701     → _load_model()
              *** LAZY IMPORT TRIGGERED ***
  2701     → import sklearn.ensemble._forest             ← STARTS
  2885     → sklearn imports complete (~1184ms)
  2885     → joblib.load("random_forest_v2.pkl")         ← ~40ms
  2925     → RandomForestRegressor deserialized, cached in _model
  2925     → model.predict(df) — first prediction       ← 28ms (numpy warmup)
  2953     ← FRI = 66.89
────────────────────────────────────────────────────────────────────────
 RECOMMENDATION ENGINE
────────────────────────────────────────────────────────────────────────
  2953     classify_risk(fri) → "Sedang"
  2953     recommend(fri, top_n=5)
  2953     → score_commodities()
  2953     → _load_profiles() → commodity_profiles.json (0.3ms)
  2953     → Score 17 commodities → sort → top 5
  2954     explain_recommendation() (×5)
  2954     → _load_profiles() → commodity_profiles.json AGAIN (0.3ms)
  2955     → Generate alasan + ringkasan for each
  2956     get_mitigasi("Sedang")
  2956     → _load_rules() → mitigation_rules.json (0.3ms)
  2957     → Sort + return mitigation actions
────────────────────────────────────────────────────────────────────────
 RESPONSE
────────────────────────────────────────────────────────────────────────
  2957     HasilPrediksi.to_dict() → dict
  2957     Serialize to JSON → return HTTP 200
  2958     LoggingMiddleware logs "Response: 200 (Xms)"
  2958     ── RESPONSE SENT ──
────────────────────────────────────────────────────────────────────────
 TOTAL:  2958ms (no Azure provisioning)
       ~7400ms (with Azure provisioning + cold start)
```

## Network Call Sequence

```
Call #1: GET https://geocoding-api.open-meteo.com/v1/search?name=Pekanbaru&count=1
         → DNS resolve (if not cached) ~50-200ms
         → TCP connect ~50-100ms
         → TLS handshake ~100-250ms
         → HTTP request/response ~20-150ms
         = Total: ~220-700ms

Call #2: GET https://api.open-meteo.com/v1/forecast?latitude=...&longitude=...
         → DNS resolve (different hostname, ~50-200ms)
         → TCP connect ~50-100ms
         → TLS handshake ~100-250ms
         → HTTP request/response (14-day payload) ~50-450ms
         = Total: ~250-1000ms
```

## Key Observations

1. **sklearn import dominates**: The 1184ms sklearn import is the single largest contributor after network.

2. **Network calls are serial**: Geocoding must complete before the forecast call starts because geocoding provides lat/lon parameters.

3. **commodity_profiles.json is loaded twice**: Same 6.6 KB file read on disk twice from separate module-level caches.

4. **Feature engineering is negligible**: ~1ms total for all pandas operations.

5. **Recommendation engine is fast**: ~4ms for 5 recommendations with explanations and mitigation.

6. **Model prediction is fast after warm-up**: 28ms per predict once sklearn is loaded.
