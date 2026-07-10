# Feature Flag Specification

## 1. Environment Variable

```
USE_KNOWLEDGE_RECOMMENDATION=false
```

**Defined in**: `backend/config.py` (loaded from `.env`)

**Default**: `false` (legacy recommendation active)

## 2. Valid Values

| Value | Behavior |
|-------|----------|
| `0`, `false`, `no`, (unset) | Legacy scoring engine |
| `1`, `true`, `yes` | Knowledge-Based Decision Engine |

## 3. Where the Flag is Used

| File | Usage |
|------|-------|
| `backend/config.py` | Loads and parses the flag |
| `backend/services/recommendation_gateway.py` | Routes to correct engine |
| `backend/routers/health.py` | Reports flag status in response |
| `backend/routers/info.py` | Reports flag status in response |
| `backend/schemas/response.py` | Schema includes `feature_flag_active` field |

## 4. Testing the Flag

```bash
# Legacy mode (default)
python -m pytest tests/backend/ -v

# KB mode (override for testing)
$env:USE_KNOWLEDGE_RECOMMENDATION="true"
python -m pytest tests/backend/test_recommendation_gateway.py -v
$env:USE_KNOWLEDGE_RECOMMENDATION="false"
```

## 5. Production Transition

```bash
# Step 1: Deploy with flag=false (legacy active, KB ready)
# Step 2: Test KB in staging
# Step 3: Set flag=true in .env and restart
USE_KNOWLEDGE_RECOMMENDATION=true
# Step 4: Monitor health endpoint for recommendation_engine
# Step 5: If issues, set back to false and restart
```

## 6. Health Check

The `/api/health` endpoint reports the active engine:

```json
{
  "recommendation_engine": {
    "active_engine": "knowledge_base",
    "feature_flag_active": true,
    "knowledge_engine_version": "1.0",
    "decision_engine_ready": true
  }
}
```

## 7. Rollback

To roll back:
```bash
# Set flag to false
USE_KNOWLEDGE_RECOMMENDATION=false
# Restart the application
```

No code changes or redeployment needed for rollback.
