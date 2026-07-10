# Deployment Strategy

## 1. Phased Rollout

### Phase 1 — Deploy with Legacy Active (Sprint KB4)

```yaml
# .env
USE_KNOWLEDGE_RECOMMENDATION=false
```

- Deploy all Sprint KB4 code
- Decision Engine initializes on startup
- All endpoints serve legacy recommendations
- Health endpoint reports both engines
- Monitor for: startup time, memory usage, errors

### Phase 2 — Enable KB in Staging

```yaml
USE_KNOWLEDGE_RECOMMENDATION=true
```

- Test all endpoints against Knowledge-Based engine
- Verify response structure
- Verify frontend compatibility
- Run load tests

### Phase 3 — Production Cutover

```yaml
USE_KNOWLEDGE_RECOMMENDATION=true
```

- Monitor `/api/health` for `decision_engine.ready == true`
- Monitor `/api/health/detail` for `recommendation_engine == knowledge_base`
- Legacy engine still available as fallback

### Phase 4 — Archive Legacy (Sprint KB6+)

- Remove `ml/recommendation/` after confirming no consumers
- Remove legacy mapping code

## 2. Monitoring

### Health Endpoint

```
GET /api/health
```

Key fields to monitor:
- `decision_engine.decision_ready` — Engine healthy?
- `decision_engine.feature_flag_active` — KB mode active?
- `recommendation_engine.active_engine` — Which engine is live?
- `recommendation_engine.decision_engine_ready` — KB engine healthy?

### Logs

```
KB recommendation: FRI=45.0 Risiko Sedang | R=7 A=4 N=6 | 2.34ms
DecisionEngine initialized with 17 commodities, 15 rules
```

## 3. Rollback Procedure

```bash
# 1. Set feature flag to false
USE_KNOWLEDGE_RECOMMENDATION=false

# 2. Restart the application
# 3. Verify health endpoint
curl http://localhost:8000/api/health | jq .recommendation_engine
# → {"active_engine": "legacy_scoring", "feature_flag_active": false, ...}
```

No code changes needed. The legacy engine was never removed.

## 4. Startup Order

```
1. Load environment (config.py)
2. Load ML models (Random Forest, scaler, features)
3. Load legacy recommendation data (commodity_profiles.json)
4. Initialize Knowledge Base (commodity_knowledge.json)
5. Initialize Decision Engine (rules + KB validation)
6. Initialize Recommendation Gateway
7. Warm-up prediction
8. Application ready → port 8000
```

If step 4 or 5 fails, the application fails to start.
If step 6 fails, legacy mode is used.

## 5. Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_KNOWLEDGE_RECOMMENDATION` | `false` | Select recommendation engine |

## 6. Testing in Production

Before enabling the KB engine globally:
1. Set `USE_KNOWLEDGE_RECOMMENDATION=true` on one instance
2. Verify health endpoint shows `decision_engine_ready: true`
3. Send test requests with `curl`
4. Monitor response times
5. If stable, roll out to all instances
