# Recommendation Gateway Specification

## 1. Purpose

The Recommendation Gateway is a thin service layer that routes recommendation requests to the appropriate engine based on the `USE_KNOWLEDGE_RECOMMENDATION` feature flag. Endpoints must never know which engine is active.

## 2. File Location

`backend/services/recommendation_gateway.py`

## 3. Key Functions

### `augment_with_knowledge(fri, risk_label, top_n, base_result, request)`

The central routing function. Called from every prediction endpoint after FRI calculation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `fri` | float | Flood Risk Index (0–100) |
| `risk_label` | str | Risk level string (e.g., "Risiko Sedang") |
| `top_n` | int | Number of recommendations |
| `base_result` | dict | Result from ML prediction pipeline |
| `request` | Request | FastAPI request (for app state access) |

**Returns**: Augmented response dict.

### `get_active_engine() -> str`

Returns `"knowledge_base"` or `"legacy_scoring"` based on feature flag.

### `is_knowledge_active() -> bool`

Returns the current state of `USE_KNOWLEDGE_RECOMMENDATION`.

## 4. Behavior Matrix

| Flag | KB Ready | KB Result | Response |
|------|----------|-----------|----------|
| OFF | — | — | Legacy only |
| ON | Yes | Success | Legacy + KB additive fields |
| ON | Yes | Error | Legacy (fallback, logged) |
| ON | No | — | Legacy (fallback, logged) |

## 5. Fallback Behavior

If the Knowledge-Based Decision Engine is unavailable or raises an error, the gateway:
1. Logs the error
2. Returns the legacy result unchanged
3. Never fails the request

This ensures the API is always available.

## 6. Logger Output

In KB mode, the gateway logs:

```
KB recommendation: FRI=45.0 Risiko Sedang | R=7 A=4 N=6 | 2.34ms
```
