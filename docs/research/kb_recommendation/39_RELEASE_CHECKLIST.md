# Production Release Checklist

## Sprint KB6 — KB-DSS Release

### Pre-Released Checks

- [x] Knowledge Base loaded successfully (17 commodities)
- [x] All 246 tests passing
- [x] Health endpoint ready (all subsystems healthy)
- [x] No TODO comments in backend code
- [x] No FIXME comments in backend or frontend code
- [x] No debug logging in production code
- [x] No dead code identified
- [x] No duplicated commodities
- [x] No duplicated rules
- [x] No frontend build warnings
- [x] No backend compilation warnings
- [x] All environment variables documented in .env.example
- [x] Knowledge validation (444 checks, 0 failures)
- [x] Rule validation (15/15 rules, 100% coverage)
- [x] API schema compatibility verified
- [x] Feature flag verified (legacy + KB mode)

### Rollback Procedure

1. **Disable Knowledge Engine:** Set `USE_KNOWLEDGE_RECOMMENDATION=false` in `.env`
2. **Restart application:** `uvicorn backend.app:app --host 0.0.0.0 --port 8000`
3. **Verify rollback:** Check `GET /api/health` → `active_engine: legacy_scoring`
4. **No database changes needed** — KB is purely in-memory
5. **No data loss** — KB-DSS is additive only

### Activation Procedure

1. [ ] Set `USE_KNOWLEDGE_RECOMMENDATION=true` in `.env`
2. [ ] Restart the application
3. [ ] Verify `GET /api/health` shows `active_engine: knowledge_base`
4. [ ] Run manual prediction test
5. [ ] Verify frontend shows knowledge-based recommendations
6. [ ] Monitor error logs for 24 hours

### Post-Activation Monitoring

- [ ] Monitor /api/health endpoint every 5 minutes
- [ ] Track decision engine latency (should be <1ms)
- [ ] Verify no increase in API error rates
- [ ] Verify frontend renders correctly with KB data
- [ ] Check that `knowledge_recommendation` field appears in responses

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| USE_KNOWLEDGE_RECOMMENDATION | Enable KB recommendation engine | No | false |
| LOG_LEVEL | Logging level | No | INFO |
| OPENMETEO_WEATHER_URL | Open-Meteo API URL | No | https://api.open-meteo.com/v1/forecast |
| SUPABASE_URL | Supabase project URL | Yes | — |
| SUPABASE_SERVICE_ROLE_KEY | Supabase service role | Yes | — |

### Security Checklist

- [x] API keys stored only in .env (not in code)
- [x] Rate limiting active on prediction endpoints
- [x] Authentication required for all prediction routes
- [x] No secrets in logs
- [x] CORS configured for production frontend URL

### Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | — | 2026-07-08 | — |
| Reviewer | — | — | — |
| Product Owner | — | — | — |
