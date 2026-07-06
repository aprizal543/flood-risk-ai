# Flood Risk DSS Deployment Checklist

## Summary

Use this checklist after the deployment blockers in `01_PRODUCTION_READINESS_REPORT.md` are addressed.

All three production blocking issues identified in the audit have been resolved in Sprint 1.5.

## Inspection Results

### Azure Backend Checklist

- [x] All backend runtime dependencies are declared in `requirements.txt` (including `httpx`, `requests`, `keras`).
- [x] `runtime.txt` created — Python 3.12 pinned.
- [x] `startup.sh` created — binds to `$PORT` using `uvicorn backend.app:app`.
- [x] Health endpoint `/api/health` verified — returns `{"status":"sehat","versi":"1.0.0"}`.
- [x] Model info endpoint `/api/info/model` verified — `random_forest_v2.pkl` reports `tersedia`.
- [x] CORS configured via `FRONTEND_URL` env var (no wildcard).
- [x] Open-Meteo uses public HTTPS endpoints (no localhost, no API key).
- [x] Logging at INFO level — no secrets in logs.
- [ ] **Manual step:** Set `SUPABASE_URL` in Azure App Service.
- [ ] **Manual step:** Set `SUPABASE_SERVICE_ROLE_KEY` in Azure App Service.
- [ ] **Manual step:** Set `SUPABASE_ANON_KEY` in Azure App Service.
- [ ] **Manual step:** Set `FRONTEND_URL` in Azure App Service.
- [ ] **Manual step:** Set LLM provider API keys if AI Chat is enabled.
- [ ] **Manual step:** Deploy code via git push, zip deploy, or GitHub Actions.

### Vercel Frontend Checklist

- [ ] Set `NEXT_PUBLIC_API_URL` to the Azure backend URL (required; build will fail if missing in production).
- [ ] Set `NEXT_PUBLIC_SITE_URL` to the final Vercel production URL.
- [ ] Set `NEXT_PUBLIC_SUPABASE_URL`.
- [ ] Set `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- [ ] Confirm Supabase OAuth redirect URLs include `/auth/callback` on the production domain.
- [ ] Confirm production pages load without any localhost fallback.
- [ ] Run `npm run build` in `apps/web` and confirm success.
- [ ] Verify auth routes and dashboard routes still work after deployment.
- [ ] Verify static assets in `public/` load correctly.

### Post-Deployment Checklist

- [ ] Open `/api/health` and `/api/health/detail`.
- [ ] Run one authenticated manual prediction.
- [ ] Run one authenticated realtime prediction.
- [ ] Confirm Open-Meteo weather values appear in the response.
- [ ] Confirm frontend can call the backend from the deployed origin.
- [ ] Confirm Supabase login and logout still work.
- [ ] Confirm no secret values appear in logs or browser console.

### Rollback Checklist

- [ ] Keep the last accepted backend deployment artifact available.
- [ ] Keep the current frontend release tag or deployment version available.
- [ ] Record the rollback command or deployment swap procedure.
- [ ] Confirm the previous known-good backend URL remains reachable.
- [ ] Confirm the previous known-good frontend deployment can be restored quickly.

## Findings

- The backend is structurally deployable — dependency and CORS issues are resolved.
- The frontend is structurally deployable, but production env vars must be set explicitly or it will fail with a clear configuration error.
- The ML artifact path is present and valid.

## Recommendations

- Do not promote to production until the Azure and Vercel checklist items marked unchecked are completed.
- Keep smoke tests short and focused on auth, prediction, and Open-Meteo connectivity.
- Validate rollback before the first public release.

## Blocking Issues (Resolved)

- [x] Missing backend runtime dependencies — `httpx`, `requests`, and `keras` added to `requirements.txt`.
- [x] Potential frontend/backend origin mismatch — CORS now uses `FRONTEND_URL` env var.
- [x] Missing production env var injection for the frontend — `NEXT_PUBLIC_API_URL` is now required in production; missing it throws a clear configuration error.

## Non-Blocking Issues

- No image optimization config.
- Legacy session fallback remains in the frontend.
- Logging is not env-driven.
