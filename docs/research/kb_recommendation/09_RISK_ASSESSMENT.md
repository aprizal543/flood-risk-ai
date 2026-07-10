# Risk Assessment — Knowledge-Based Recommendation Migration

## 1. Risk Matrix

| ID | Risk Category | Risk Description | Probability | Impact | Severity | Mitigation |
|----|--------------|------------------|-------------|--------|----------|------------|
| R1 | Technical | Knowledge Base Engine performance degrades under concurrent load | Low | Medium | Medium | Lazy-loading with TTL cache; benchmark before deployment |
| R2 | Technical | Rule Engine produces incorrect recommendations due to logic error | Low | High | High | Comprehensive unit tests; validation matrix covering all 17 × 3 combinations |
| R3 | Technical | Schema mismatch between knowledge base specification and implementation | Medium | Medium | Medium | Strict dataclass validation at load time; schema tests |
| R4 | Research | Commodity flood tolerance classifications are inaccurate for Pekanbaru microclimate | Medium | High | High | Flag all entries as [Research Assumption]; plan field validation study |
| R5 | Research | Maximum inundation duration estimates are incorrect for local varieties | Medium | High | High | Document as assumption; design rule override mechanism for local calibration |
| R6 | Research | Economic priority rankings do not reflect actual market conditions | Medium | Medium | Medium | Make priority configurable; recommend market survey |
| R7 | Migration | Parallel run reveals contradictions between heuristic and KB output | Low | Medium | Medium | Document contradictions; escalate to domain expert for resolution |
| R8 | Migration | API consumers break due to unnoticed response format changes | Low | High | High | Strict additive-only policy in Phase 1; full regression test suite |
| R9 | Migration | Frontend migration incomplete before KB backend goes live | Low | Medium | Medium | Feature flag: new UI only visible when `?kb_ui=true` parameter present |
| R10 | Rollback | Unable to roll back due to database schema migration | None | N/A | N/A | No database changes in scope; rollback is git revert |
| R11 | Rollback | New frontend components cannot be reverted atomically | Low | Low | Low | Component-level feature flags; old components retained during transition |
| R12 | Technical | Explanation Engine v2 produces confusing or incorrect explanations | Medium | Medium | Medium | Iterative review with domain expert; A/B test explanation clarity |

## 2. Technical Risks

### 2.1 R1 — Knowledge Base Performance Under Load

**Description**: The Knowledge Base Engine loads and validates 17 commodity records at startup. Under concurrent request load, query performance may degrade if the module is not properly cached.

**Assessment**: The data volume is extremely small (17 records, <10KB). Lazy-loading with a simple `@lru_cache` or module-level singleton ensures microsecond query times.

**Mitigation**:
- Implement singleton pattern for KnowledgeBase class
- Use `functools.lru_cache` on query methods
- Benchmark: target <5ms per query after initial load
- Fallback: static fallback list if load fails

**Contingency**: If benchmark shows >20ms overhead, implement eager loading at application startup instead of lazy loading.

### 2.2 R2 — Rule Engine Logic Error

**Description**: Incorrect rule implementation could produce dangerous recommendations (e.g., recommending tomat at high risk).

**Assessment**: The rule set is deterministic and testable. Each rule maps to a specific code path.

**Mitigation**:
- Complete test matrix: all 17 commodities × 3 risk levels = 51 test cases
- Property-based testing: for any valid FRI, recommended commodities must have tolerance ≥ threshold
- Code review of rule implementation against specification

**Contingency**: Add a "safety layer" that cross-references KB output against a hardcoded safety matrix as a circuit breaker during early deployment.

### 2.3 R3 — Schema Mismatch

**Description**: The specification schema (this document) may not match the implementation schema exactly.

**Mitigation**:
- Schema validation test: load specification and verify all fields exist in implementation
- Round-trip test: serialize → deserialize → compare
- Explicit `__post_init__` validation in dataclass

## 3. Research Risks

### 3.1 R4 — Inaccurate Flood Tolerance Classification

**Description**: The flood tolerance levels assigned to commodities are based on general botanical knowledge and pending literature review. They may not reflect actual field performance in Pekanbaru's specific climate and soil conditions.

**Assessment**: 
- High impact: incorrect tolerance leads to wrong recommendations
- Medium probability: general botanical knowledge is usually reliable at the ordinal level

**Mitigation**:
- All tolerance classifications clearly marked as `[Research Assumption]`
- The `is_assumption` field enables users to assess confidence
- A field validation study is recommended before operational deployment
- Local agricultural extension experts should review classifications

**Contingency**: Design a "calibration override" mechanism that allows adjusting tolerance levels without code changes (e.g., via config file or admin interface).

### 3.2 R5 — Incorrect Maximum Inundation Duration

**Description**: Estimated durations for how long each commodity can survive inundation may be inaccurate.

**Assessment**: Similar to R4 — duration estimates are educated guesses based on related literature.

**Mitigation**:
- Durations expressed as ranges not exact values
- Marked as research assumptions
- Conservative estimates used (shorter durations for flood-intolerant species)

### 3.3 R6 — Economic Priority Mismatch

**Description**: Economic priority rankings prioritize commodities that may not have strong market demand in Riau province.

**Mitigation**:
- Priority is the lowest-weight factor in current engine (0.10)
- In the new KB engine, priority affects ranking within same tolerance band only
- Configurable priority list can be adjusted for local markets

## 4. Migration Risks

### 4.1 R7 — Heuristic vs KB Contradiction

**Description**: The parallel run (Phase 0) may reveal cases where the KB engine recommends different commodities than the heuristic engine.

**Assessment**: Some contradiction is expected and healthy — it indicates the KB engine is making different (hopefully better) trade-offs.

**Mitigation**:
- Define acceptable contradiction threshold: top-5 overlap ≥ 3 commodities
- Escalate contradictions to domain expert
- Document all contradictions with explanation of which engine is correct
- No user-facing impact during parallel run

### 4.2 R8 — API Consumer Breakage

**Description**: External consumers (mobile apps, third-party integrations) relying on the old API format may break.

**Mitigation**:
- Strict additive-only policy for KB Sprint 4
- Old `PenjelasanResponse` fields preserved exactly
- Deprecation notice sent via API version header and OpenAPI schema
- Old fields removed only after announcement in Sprint KB6

### 4.3 R9 — Incomplete Frontend Migration

**Description**: If frontend migration (KB Sprint 5) is incomplete before KB Sprint 4 backend goes live, users see partial or broken UI.

**Mitigation**:
- Feature flag: `?kb_ui=true` enables new components
- Backend returns both old and new fields
- Frontend falls back to old UI if feature flag is off
- Staged rollout: 10% → 50% → 100% of users

## 5. Rollback Strategy

### 5.1 Rollback Triggers

| Trigger | Action |
|---------|--------|
| KB engine produces obviously wrong recommendations | Disable KB engine; fall back to heuristic |
| API response time increases >100ms | Roll back schema changes; keep old response format |
| Frontend crash rate increases >1% | Disable feature flag; restore old components |
| Domain expert rejects recommendation quality | Revert to heuristic; revise KB before re-release |

### 5.2 Rollback Procedure

**Sprint KB2/KB3 (Engine Phase)**
```
git revert <merge-commit>  # Revert the sprint merge
# No data migration to reverse
# No user impact (not yet deployed)
```

**Sprint KB4 (Backend Phase)**
```
1. git revert the schema/routing changes
2. Re-deploy previous API version
3. Verify old endpoint returns correct old-format response
4. (No cache invalidation needed — old fields never removed)
```

**Sprint KB5 (Frontend Phase)**
```
1. Set feature flag kb_ui_enabled = false
2. old components still in codebase (not yet deleted)
3. Verify old UI renders correctly
4. Remove new components in next patch (optional)
```

**Sprint KB6 (Cleanup Phase)**
```
1. git revert the deletion commits
2. Restore scorer.py, recommender.py, explain.py
3. Restore old API response schemas
4. Redeploy with heuristic engine active
```

### 5.3 Rollback Time Estimates

| Phase | Detection Time | Decision Time | Execution Time | Total Downtime |
|-------|---------------|---------------|----------------|----------------|
| Engine | Immediate (test fails) | 1 hour | 1 hour | ~2 hours |
| Backend | < 5 minutes (monitoring) | 1 hour | 30 minutes | ~1.5 hours |
| Frontend | < 5 minutes (error tracking) | 30 minutes | 15 minutes | ~1 hour |

## 6. Technical Debt Considerations

| Area | Debt | Repayment |
|------|------|-----------|
| Parallel run code | Two engines running simultaneously adds complexity | Remove old engine in Sprint KB6 |
| Additive API fields | Temporarily duplicated response data | Remove old fields in Sprint KB6 |
| Feature flags | Temporary conditional logic in frontend | Remove feature flag after full rollout |
| Research assumptions | All knowledge currently assumed | Resolve through literature review and field studies |

## 7. Monitoring Plan

| Metric | Tool | Threshold | Alert |
|--------|------|-----------|-------|
| KB engine load time | Application logging | >100ms | Warning |
| KB query latency | Application logging | >20ms | Warning |
| API response time | API monitoring | >2× baseline | Critical |
| Recommendation consistency | A/B comparison | <3/5 overlap heuristic vs KB | Warning |
| Frontend error rate | Error tracking | >0.5% | Critical |
| Feature flag adoption | Analytics | <50% after 2 weeks | Information |

## 8. Risk Ownership

| Risk | Owner | Review Schedule |
|------|-------|-----------------|
| R1 (Performance) | Backend Developer | Sprint KB4 code review |
| R2 (Rule Logic) | ML Engineer | Sprint KB3 code review |
| R3 (Schema) | Tech Lead | Sprint KB2 code review |
| R4 (Tolerance Accuracy) | Domain Expert | Sprint KB6 validation |
| R5 (Duration Accuracy) | Domain Expert | Sprint KB6 validation |
| R6 (Economic Priority) | Product Owner | Sprint KB6 validation |
| R7 (Contradiction) | Tech Lead | Sprint KB4 review |
| R8 (API Breakage) | Backend Developer | Sprint KB4 code review |
| R9 (Frontend) | Frontend Developer | Sprint KB5 code review |
| R10–R11 (Rollback) | DevOps | Ongoing |

## 9. Go/No-Go Decision Points

| Checkpoint | Criteria | Decision Makers |
|------------|----------|-----------------|
| Before Sprint KB3 | All KB2 acceptance criteria met | Tech Lead + ML Engineer |
| Before Sprint KB4 | All KB3 acceptance criteria met; rule validation matrix complete | Tech Lead + Domain Expert |
| Before Sprint KB5 | Backend integration tests pass; no regression | Tech Lead + QA |
| Before Sprint KB6 | Frontend acceptance criteria met; accessibility audit passes | Tech Lead + Frontend Lead |
| Go-Live | All Sprint KB6 acceptance criteria met; expert validation complete | Tech Lead + Product Owner |
