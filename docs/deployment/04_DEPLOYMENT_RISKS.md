# Flood Risk DSS Deployment Risks

## Summary

The system is close to deployable. The three high-risk blocking issues identified in the audit have been resolved in Sprint 1.5.

## Inspection Results

### High Risk (Resolved)

| Risk | Resolution |
|---|---|
| Missing direct backend dependencies | `httpx>=0.27.0`, `requests>=2.31.0`, and `keras>=3.0.0` added to `requirements.txt`. |
| CORS origin mismatch for Vercel | Hardcoded production origins removed. CORS now uses `FRONTEND_URL` env var plus localhost for development. |
| Localhost fallback in frontend API clients | Production now throws a clear configuration error if `NEXT_PUBLIC_API_URL` is missing, instead of silently using localhost. |

### Medium Risk

| Risk | Evidence | Why it matters |
|---|---|---|
| Auth session fallback still uses localStorage | `apps/web/providers/session-provider.tsx:44-66`, `apps/web/lib/auth/storage.ts:24-39` | Higher exposure to XSS than a cookie-only strategy. |
| Error handling may reveal internals | `backend/app.py:99-104`, `backend/services/auth_service.py:81-89` | Internal paths or provider messages can leak to clients. |
| Docs and runtime env vars are out of sync | `.env.example:4-27`, `README.md:57-74`, `backend/app.py:30-54` | Operational mistakes become more likely during deployment. |
| Logging level is not env-driven | `backend/app.py:30-34`, `.env.example:21-22` | Production log tuning is limited without code changes. |
| Next.js middleware deprecation warning exists in project notes | `KNOWN_LIMITATIONS.md:20-26` | Not a launch blocker, but it is maintenance debt. |
| scikit-learn artifact version mismatch warning exists | `KNOWN_LIMITATIONS.md:16-19` | Model loads, but warnings should be expected at cold start. |

### Low Risk

| Risk | Evidence | Why it matters |
|---|---|---|
| No image optimization config | `apps/web/next.config.ts:1-18` | Performance optimization is limited, but functionality is unaffected. |
| Frontend UI displays a default provider label that differs from the chat service default | `apps/web/components/dashboard/workspace-panels.tsx:40-43`, `apps/web/services/llm.ts:10-11` | Minor consistency issue only. |
| Open-Meteo URLs are hardcoded rather than env-driven | `backend/providers/openmeteo_provider.py:13-45`, `backend/providers/geocoding.py:9-35` | Works in production, but reduces configurability. |

## Findings

- Blockers are operational, not architectural.
- The validated FRI v2 artifact path exists and is wired correctly.
- Open-Meteo connectivity has explicit timeout handling and no localhost dependence.
- Auth is production-capable, but the frontend still preserves a legacy localStorage path.

## Recommendations

- Fix the missing Python dependency declarations before deployment.
- Add the final frontend origin to backend CORS before launch.
- Set production env vars explicitly in Azure and Vercel.
- Recheck browser auth flows after deployment, especially OAuth callback and session refresh.

## Blocking Issues

- Missing direct backend dependencies.
- CORS allow-list not confirmed for the final Vercel origin.
- Frontend localhost fallback if `NEXT_PUBLIC_API_URL` is not set.

## Non-Blocking Issues

- localStorage auth fallback.
- Minor error disclosure risk.
- Documentation drift.
- Logging level not externally configurable.
- Known Next.js and scikit-learn warnings.
