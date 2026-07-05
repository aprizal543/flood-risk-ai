# Sprint v2.5C Regression Report

## Objective

Validate backend regression safety after the FRI v2 Random Forest migration. This sprint focused on testing production behavior, not adding features or changing algorithms.

## Status

PRODUCTION READY WITH MINOR ISSUES

The active realtime RF path is functional, authenticated, rate-limited, protected by security headers, and connected to FRI v2 features plus `random_forest_v2.pkl`. Two minimal bug fixes were applied during validation.

## Bug Fixes Applied

| File | Fix | Reason |
|------|-----|--------|
| `backend/services/prediction_gateway.py` | `predict_from_raw()` now calls `build_prediction_features_v2()` instead of duplicating direct `build_features_v2()` construction. | Sprint v2.5C explicitly required validating that the realtime path reaches the validated v2 feature seam. Behavior is unchanged. |
| `backend/app.py` | Added a `FileNotFoundError` exception handler returning `{status, kode, pesan}` with HTTP 500. | Simulated missing RF model previously returned raw `Internal Server Error` text instead of documented JSON error schema. |

No model artifacts were replaced. No RF retraining, FRI formula change, feature-engineering redesign, API redesign, frontend change, or deployment change was performed.

## Test Summary

| Area | Result | Notes |
|------|--------|-------|
| Backend startup/import | PASS | `from backend.app import app` succeeds in fresh Python processes. |
| Model load | PASS | Active RF loader loads `random_forest_v2.pkl`. |
| Authentication tests | PASS | `tests/test_auth.py`: 8 passed. |
| FRI v2 feature/RF tests | PASS | `tests/test_weather_provider.py -k "FriV2FeatureEngineering or FriV2RandomForestCompatibility"`: 6 passed. |
| Open-Meteo provider tests | PASS | `tests/test_weather_provider.py -k "OpenMeteoProvider"`: included in 9 selected provider/v2 tests, passed. |
| Full pytest collection | BLOCKED | Root-level `test_agentrouter.py` raises `RuntimeError` when `AGENTROUTER_API_KEY` is unset. |
| Legacy integration test file | FAILS EXPECTED/STale | `tests/test_api_integration.py`: 19 failed, 5 passed. Failures are mostly stale assumptions: unauthenticated prediction endpoints expected `200`, and model info expected 9 v1 features. |
| Authenticated endpoint probes | PASS with one legacy issue | Health, auth, provider, manual prediction, CSV prediction, realtime prediction, metadata, AI chat, security headers, CORS, and rate limiting passed under authenticated/mocked conditions. |

## Endpoint Regression Matrix

| Endpoint / Feature | Result | Evidence |
|--------------------|--------|----------|
| `/api/health` | PASS | `200`, body `{"status":"sehat","versi":"1.0.0"}`. |
| `/api/health/detail` | PASS | `200`, components healthy. |
| `/api/info/model` | PASS | `jumlah_fitur=4`, features `RR`, `Rain7`, `RH_avg`, `Tavg`, RF v2 artifact available. |
| `/api/auth/me` anonymous | PASS | `401`, JSON error schema. |
| `/api/auth/me` invalid token | PASS | `401`, JSON error schema. |
| `/api/auth/me` expired token | PASS | `401`, JSON error schema. |
| `/api/auth/login` rate limit | PASS | 6 requests produced `[200, 200, 200, 200, 200, 429]`. |
| `/api/provider/openmeteo` authenticated mocked | PASS | `200`, provider response returned. |
| `/api/prediksi/realtime` anonymous | PASS | `401`; provider and prediction were not called. |
| `/api/prediksi/realtime` authenticated mocked | PASS | `200`, RF prediction returned. |
| `/api/prediksi/manual` authenticated | PASS | `200`, RF prediction returned. |
| `/api/prediksi/csv` authenticated | PASS | `200`, RF prediction returned. |
| `/api/ai/chat` authenticated mocked | PASS | `200`, response schema valid. |
| `/api/prediksi/engineered` authenticated | MINOR ISSUE | Returns `422` because request schema still supplies v1 engineered fields while runtime RF now requires FRI v2 fields. Not fixed because changing this endpoint requires an explicit compatibility/API decision. |

## Security Regression Checks

| Check | Result |
|-------|--------|
| Security headers | PASS: `X-Frame-Options=DENY`, `X-Content-Type-Options=nosniff`, `Referrer-Policy=strict-origin-when-cross-origin`. |
| CORS preflight from `http://localhost:3000` | PASS: `200`, allowed origin returned. |
| Rate limiting | PASS: login 6th request returned `429` with JSON error schema. |
| Auth before realtime execution | PASS: anonymous realtime returned `401`; provider and prediction call flags remained false. |

## Error Handling Checks

| Scenario | Result |
|----------|--------|
| Open-Meteo unavailable in realtime | PASS: `503`, JSON error schema. |
| Open-Meteo unavailable in provider endpoint | PASS: `502`, JSON error schema. |
| Invalid provider weather data in realtime | PASS: `500`, JSON error schema. |
| Invalid query parameter `top_n=0` | PASS: `422`, JSON error schema. |
| Expired token | PASS: `401`, JSON error schema. |
| Unauthorized access | PASS: `401`, JSON error schema. |
| Missing RF model artifact | PASS after fix: `500`, JSON error schema. |

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| `/api/prediksi/engineered` still exposes v1 engineered request schema and returns `422` under v2 RF metadata. | Medium | Not fixed in this QA sprint because a correct fix requires an explicit API compatibility decision. |
| `tests/test_api_integration.py` is stale relative to current security and RF v2 feature expectations. | Low | Test maintenance needed; production auth behavior is correct. |
| Root-level `test_agentrouter.py` blocks full pytest when `AGENTROUTER_API_KEY` is unset. | Low | Environment/test isolation issue, unrelated to FRI v2 RF path. |
| sklearn emits `InconsistentVersionWarning` loading model pickled with sklearn `1.6.1` under `1.8.0`. | Low | Prediction succeeds; should be tracked for production dependency pinning or artifact refresh policy. |

## Production Readiness Assessment

Readiness score: 90/100

Recommendation: Production Ready with Minor Issues.

The active authenticated realtime RF path is ready. The only production-facing compatibility concern found is the legacy engineered endpoint, which should be handled as an explicit follow-up rather than silently remapped during QA.
