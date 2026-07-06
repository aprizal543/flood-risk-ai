# Flood Risk DSS Production Readiness Report

## Summary

Verdict: ❌ Not Ready for Production

Scope: Read-only production readiness audit for Azure App Service backend and Vercel frontend.

Overall score: 67/100

## Inspection Results

### 1. Repository Structure

- Backend layout exists under `backend/` with FastAPI app, routers, services, providers, security, schemas, and auth dependencies.
- Frontend layout exists under `apps/web/` with App Router pages, middleware, Supabase helpers, services, components, hooks, and public assets.
- ML layout exists under `ml/` with feature engineering, prediction, recommendation, artifacts, and knowledge base assets.
- Required production artifacts are present: `ml/artifacts/random_forest_v2.pkl` and `ml/artifacts/feature_list.json`.
- Static assets are present under `apps/web/public/`.

### 2. Environment Variables

- Backend runtime depends on Supabase and provider keys.
- Frontend runtime depends on public API and Supabase variables.
- Several documented `.env` values are not consumed by current code.
- Local `.env` files contain secret values and localhost defaults.

### 3. Backend Production Readiness

- FastAPI entrypoint exists in `backend/app.py`.
- Health endpoint exists at `/api/health`.
- ASGI app export is `app`.
- Azure compatibility is reasonable when the startup command explicitly binds the deployed port.

### 4. Frontend Production Readiness

- Next.js production scripts exist: `build` and `start`.
- Supabase SSR and auth callback wiring are present.
- API base URL defaults to localhost if `NEXT_PUBLIC_API_URL` is missing.
- No `next/image` usage or image optimization config was found.

### 5. ML Artifact Readiness

- `random_forest_v2.pkl` is loaded lazily from `ml/artifacts/`.
- `feature_list.json` exists and matches the v2 feature set.
- Cold start behavior is acceptable but includes model load overhead.

### 6. Open-Meteo Connectivity

- Production code uses Open-Meteo HTTPS endpoints directly.
- Timeouts are configured at 10 seconds in both weather and geocoding requests.
- No localhost assumption exists in the Open-Meteo path.

### 7. CORS, Auth, Security, Logging

- CORS allows localhost and two custom production origins.
- Supabase auth uses SSR cookies on the frontend and bearer-token verification on the backend.
- Logging is present and does not appear to emit secrets.
- Legacy localStorage session fallback still exists on the frontend.

### 8. Dependencies

- Python requirements are incomplete for the current codebase.
- Node dependencies are present and locked.

## Findings

| Severity | Finding | Evidence | Impact |
|---|---|---|---|
| High | `requirements.txt` does not declare `requests` or `httpx`, but backend code imports both. | `backend/providers/openmeteo_provider.py:6`, `backend/providers/geocoding.py:5`, `backend/services/auth_service.py:8`, `backend/services/llm_service.py:14`, `requirements.txt:5-47` | Backend deployment can fail or become environment-dependent. |
| High | CORS allow-list does not include the Vercel deployment origin unless it exactly matches one of the hardcoded domains. | `backend/app.py:45-54` | Browser API calls can fail in production. |
| High | Frontend falls back to localhost when `NEXT_PUBLIC_API_URL` is missing. | `apps/web/services/prediction.ts:5-7`, `apps/web/services/llm.ts:10-11`, `apps/web/services/auth-api.ts:3-6` | Production frontend can point at a local backend by mistake. |
| Medium | Several documented environment variables are unused by current runtime code. | `.env.example:4-27`, `backend/app.py:30-54`, `backend/providers/openmeteo_provider.py:13-45`, `apps/web/services/llm.ts:10-11` | Deployment docs drift from implementation. |
| Medium | Frontend session fallback still persists tokens in localStorage. | `apps/web/providers/session-provider.tsx:44-66`, `apps/web/lib/auth/storage.ts:24-39` | Increased XSS exposure compared with cookie-only storage. |
| Medium | Error handling can disclose internal file paths or provider messages. | `backend/app.py:99-104`, `backend/services/auth_service.py:81-89` | Minor information disclosure risk. |
| Low | Next.js image optimization is not configured and no `next/image` usage was found. | `apps/web/next.config.ts:1-18` | No functional blocker, but no optimization benefit. |
| Low | `LOG_LEVEL` is documented but not wired into logging configuration. | `backend/app.py:30-34`, `.env.example:21-22` | Logging cannot be tuned via env without code changes. |

## Recommendations

- Add the missing Python dependencies to the deployment environment before release.
- Confirm the final Vercel origin is explicitly allowed by backend CORS.
- Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_SITE_URL` in Vercel to the production domains.
- Keep Supabase auth settings aligned with deployed redirect URLs.
- Treat the current local `.env` files as non-deployable artifacts.

## Blocking Issues

- Missing direct Python dependencies for the backend runtime.
- CORS origin mismatch risk for a Vercel-hosted frontend.
- Production frontend can silently default to localhost if `NEXT_PUBLIC_API_URL` is not set.

## Non-Blocking Issues

- Unused or stale environment variables in docs.
- Legacy localStorage session fallback.
- Minor information-disclosure risk in error handling.
- No image optimization configuration.
- Logging level not externally configurable.

## Production Readiness Score

| Dimension | Score |
|---|---:|
| Architecture | 88 |
| Backend | 68 |
| Frontend | 82 |
| ML | 86 |
| Security | 62 |
| Performance | 80 |
| Deployment | 58 |
| Maintainability | 74 |
| Documentation | 70 |
| Overall | 67 |

## Final Verdict

❌ Not Ready for Production
