# Sprint 1.5 — Production Blocking Fixes Report

## Summary

Resolved all three production blocking issues identified in the Production Readiness Audit (`01_PRODUCTION_READINESS_REPORT.md`).

## Files Modified

| File | Change |
|---|---|
| `requirements.txt` | Added `httpx>=0.27.0`, `requests>=2.31.0`, `keras>=3.0.0` |
| `backend/app.py` | CORS now reads `FRONTEND_URL` env var instead of hardcoded production origins; keeps localhost for development |
| `apps/web/lib/api-url.ts` | **NEW** — shared `getApiBaseUrl()` helper; throws in production if `NEXT_PUBLIC_API_URL` is missing |
| `apps/web/services/prediction.ts` | Uses `getApiBaseUrl()` instead of `?? "http://localhost:8000"` |
| `apps/web/services/llm.ts` | Uses `getApiBaseUrl()` instead of `?? "http://localhost:8000"` |
| `apps/web/services/auth-api.ts` | Uses `getApiBaseUrl()` instead of `?? "http://localhost:8000"` |
| `docs/deployment/02_DEPLOYMENT_CHECKLIST.md` | Updated checklist to reflect resolved blockers; added `FRONTEND_URL` |
| `docs/deployment/03_ENVIRONMENT_VARIABLES.md` | Documented `FRONTEND_URL`, `NEXT_PUBLIC_API_URL` production requirement, Azure/Vercel sections |
| `docs/deployment/04_DEPLOYMENT_RISKS.md` | Updated risk table to mark high-risk items as resolved |

## Blocking Issue Resolution

### Blocker 1 — Missing Backend Dependencies

**Problem:** `requirements.txt` did not include `httpx` and `requests`, which are directly imported by:
- `backend/services/auth_service.py` (httpx)
- `backend/services/llm_service.py` (httpx)
- `backend/providers/openmeteo_provider.py` (requests)
- `backend/providers/geocoding.py` (requests)

Also added `keras` for the LSTM module (`ml/predict/lstm.py`), which is a runtime dependency of the backend.

**Resolution:** Added three dependencies to `requirements.txt`:
- `httpx>=0.27.0`
- `requests>=2.31.0`
- `keras>=3.0.0`

### Blocker 2 — Production CORS

**Problem:** CORS configuration hardcoded `https://floodrisk.ai` and `https://www.floodrisk.ai` as allowed origins. The final Vercel deployment domain may differ.

**Resolution:**
- Removed hardcoded production origins
- Kept `http://localhost:3000` and `http://127.0.0.1:3000` for local development
- Added `FRONTEND_URL` environment variable for the production origin
- No wildcard (`*`) CORS used

### Blocker 3 — Frontend Localhost Fallback

**Problem:** Three frontend API client files silently fell back to `http://localhost:8000` when `NEXT_PUBLIC_API_URL` was not set.

**Resolution:**
- Created `apps/web/lib/api-url.ts` with `getApiBaseUrl()` helper
- All three services (`prediction.ts`, `llm.ts`, `auth-api.ts`) now use this helper
- In development: falls back to `http://localhost:8000` (unchanged behavior)
- In production: throws a clear configuration error if `NEXT_PUBLIC_API_URL` is missing

## Regression Results

| Check | Result |
|---|---|
| Backend Python compile (`py_compile`) | All 32 files pass |
| Frontend TypeScript (`tsc --noEmit`) | Pass — zero errors |
| Frontend ESLint (`npm run lint`) | Pass — zero errors |
| Frontend build (`npm run build`) | Pass — successful compiled output |

**Verification that unmodified code is unchanged:**
- Prediction logic — untouched
- FRI methodology — untouched
- Random Forest — untouched
- Feature engineering — untouched
- Authentication logic — untouched
- Database/Supabase — untouched
- Dashboard UI — untouched
- Model artifacts — untouched

## Deployment Readiness Update

- **Backend:** Ready for deployment. Install dependencies with `pip install -r requirements.txt`, set env vars (including `FRONTEND_URL` in Azure), start with `uvicorn backend.app:app`.
- **Frontend:** Ready for deployment. Requires `NEXT_PUBLIC_API_URL` in Vercel production environment. Missing it will fail at runtime with a clear configuration error instead of silently using localhost.

## Final Verdict

✅ **All Production Blockers Resolved**
