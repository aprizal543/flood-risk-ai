# FRI v2 Known Limitations

## 1. Legacy pytest drift

The full `python -m pytest tests` run currently fails because older integration tests still expect pre-auth or pre-v2 behavior.

Observed examples:

- Protected prediction/provider endpoints return `401` without auth.
- `tests/test_api_integration.py::TestInfoEndpoints::test_model_info` still expects the old feature count.

## 2. Pytest asyncio warning

`pytest_asyncio` emits a deprecation warning about `asyncio_default_fixture_loop_scope` being unset.

## 3. Sklearn artifact warning

Loading `random_forest_v2.pkl` emits `InconsistentVersionWarning` because the artifact was serialized under scikit-learn `1.6.1` and loaded under `1.8.0`.

## 4. Next.js workspace warnings

Frontend build emits existing warnings about:

- Multiple lockfiles and workspace-root inference
- Deprecated `middleware` convention in favor of `proxy`

## 5. Open-Meteo latency variability

Open-Meteo is an external dependency. Live latency varies and the service can change weather values between requests.

## 6. Cold-start cost

The first manual prediction call includes model loading overhead. Warm predictions are significantly faster.

## 7. Documentation drift

Some frozen-state and earlier audit documents do not fully reflect the latest runtime snapshot. This is documentation debt, not a runtime blocker.

## 8. Future improvements

- Refresh legacy tests to the current authenticated API contract.
- Reconcile frozen-state documents with the final release candidate state.
- Capture artifact provenance and environment versions alongside the model artifact.
- Add explicit pytest asyncio configuration in a future maintenance sprint.

## Non-actions

These issues were intentionally left unchanged in this QA sprint.
