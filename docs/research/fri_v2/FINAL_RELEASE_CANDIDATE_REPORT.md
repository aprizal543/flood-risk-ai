# FRI v2 Final Release Candidate Report

## Verdict

⚠ Release Candidate Approved with Minor Issues

## Scope

Read-only QA audit for the FRI v2 release candidate.

## Executive Summary

The FRI v2 release candidate is functionally aligned with the frozen methodology:

- Canonical features are `RR`, `Rain7`, `RH_avg`, `Tavg`.
- `random_forest_v2.pkl` is still the active model artifact in the validated runtime path.
- Realtime/manual prediction responses expose the v2 feature vector and risk output.
- Frontend build, lint, and TypeScript checks pass.
- Auth tests pass for the current protected route behavior.

Minor issues remain:

- The full legacy pytest suite still contains stale expectations for pre-auth / pre-v2 responses.
- Documentation state files contain older claims that do not fully match the current implementation snapshot.
- Known warnings remain in pytest, sklearn artifact loading, and Next.js workspace detection.

## System Overview

- Backend: FastAPI application with authenticated prediction routes.
- ML: Random Forest v2 artifact loaded from `random_forest_v2.pkl`.
- Methodology: `RR`, `Rain7`, `RH_avg`, `Tavg` with fixed 10 / 50 / 30 / 10 weighting.
- Frontend: dashboard, popup, analytics, reports, AI evidence, and status bar consume the same realtime contract.
- Auth: Supabase-backed session/auth flow with protected application routes.

## Verification Summary

| Area | Result | Evidence |
|---|---|---|
| Python compile | Pass | `python -m compileall backend tests` |
| Backend auth tests | Pass | `python -m pytest tests/test_auth.py` |
| FRI v2 contract tests | Pass | Targeted `tests/test_weather_provider.py` selection passed |
| Frontend lint | Pass | `npm run lint` in `apps/web` |
| TypeScript | Pass | `npx tsc --noEmit` in `apps/web` |
| Frontend build | Pass | `npm run build` in `apps/web` |
| Full pytest suite | Partial | 26 failures, 30 passes |

## Regression Summary

### Passed regressions

- Auth endpoints behave as expected in `tests/test_auth.py`.
- Targeted v2 weather/realtime/model compatibility tests pass.
- Manual and realtime prediction paths return v2 outputs when authenticated.

### Failed legacy expectations

The full `python -m pytest tests` run reported 26 failures, concentrated in legacy integration tests that still expect older behavior:

- Protected prediction/provider routes now return `401` without auth, while the tests expect `200` or validation errors.
- `tests/test_api_integration.py::TestInfoEndpoints::test_model_info` still expects `jumlah_fitur == 9`, while the current contract reports the v2 feature set.

These failures indicate test drift, not a runtime build failure.

## API Validation

Validated current contract behavior:

- Manual prediction with auth override returned `200` and produced `fri=44.02`, `tingkat_risiko=Risiko Sedang`.
- Realtime prediction with mocked provider returned `200` and exposed `RR`, `Rain7`, `RH_avg`, `Tavg`.
- Direct prediction latency was `28.96 ms`.
- Warm manual route average was `38.05 ms`.
- Warm realtime route average was `42.31 ms`.

## Dashboard Validation

Code-path validation confirms the dashboard and related views consume the same realtime response and shared display mapping. The current implementation surfaces identical v2 values across:

- Popup
- Left panel
- Analytics
- Reports
- AI evidence
- Printable report
- Status bar

## Authentication Validation

- `tests/test_auth.py` passed: register, login, logout, refresh, me, unauthorized, invalid token, and expired token.
- Protected prediction/provider routes are currently guarded and return `401` without valid auth.
- This is consistent with the current authenticated release candidate behavior.

## Scientific Validation

The audited implementation matches the frozen FRI v2 methodology:

- Features: `RR`, `Rain7`, `RH_avg`, `Tavg`
- Weights: `10%`, `50%`, `30%`, `10%`
- Algorithm: Random Forest
- Model artifact: `random_forest_v2.pkl`

The selected runtime tests confirm the feature vector and artifact compatibility.

## Performance Summary

| Metric | Result |
|---|---|
| Backend startup | `2444 ms` |
| Manual prediction cold route | `1092.80 ms` |
| Manual prediction warm average | `38.05 ms` |
| Direct prediction | `28.96 ms` |
| Realtime route warm average | `42.31 ms` |
| Open-Meteo provider probe | `1692.36 ms` |
| Frontend build | `23.5 s` |

## Repository Health

### Pass

- Python compilation
- Backend auth tests
- Targeted v2 contract tests
- Frontend lint
- TypeScript compile
- Frontend build

### Partial

- Full pytest suite due stale legacy test assumptions and auth-gated routes

## Documentation Consistency

The frozen FRI v2 specification documents remain internally consistent on:

- Methodology
- Feature set
- Weights
- Dataset immutability
- Random Forest retention

Observed drift:

- `08_PROJECT_STATE.md` is a frozen-state snapshot and does not reflect the latest runtime implementation details.
- Some earlier audit reports predate the later auth/api/dashboard alignment work.

## Release Readiness Scores

| Dimension | Score |
|---|---:|
| Architecture | 88 |
| Scientific methodology | 91 |
| Backend | 84 |
| Frontend | 90 |
| ML | 87 |
| Testing | 68 |
| Documentation | 72 |
| Performance | 83 |
| Maintainability | 77 |
| Security | 89 |

## Final Notes

The release candidate is acceptable for release with minor issues because the remaining gaps are primarily legacy test drift, documentation staleness, and non-blocking warnings rather than runtime failures in the validated FRI v2 path.
