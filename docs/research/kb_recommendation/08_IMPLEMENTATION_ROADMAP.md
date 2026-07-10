# Implementation Roadmap — Knowledge-Based Recommendation System

## 1. Sprint Overview

```
Sprint KB2:    Knowledge Base Engine
Sprint KB3:    Rule Engine
Sprint KB4:    Backend Integration
Sprint KB5:    Frontend Migration
Sprint KB6:    Testing & Validation
```

Total estimated duration: **10 weeks** (2 weeks per sprint)

---

## 2. Sprint KB2 — Knowledge Base Engine

**Objective**: Implement the structured knowledge base with query interface.

**Duration**: 2 weeks

### 2.1 Tasks

| # | Task | Deliverable | Effort |
|---|------|-------------|--------|
| 2.1 | Define `CommodityRecord` dataclass matching specification | `ml/knowledge/knowledge_base.py` | 0.5 day |
| 2.2 | Implement `KnowledgeBase` class with lazy loading | `ml/knowledge/knowledge_base.py` | 1 day |
| 2.3 | Implement query interface methods | `ml/knowledge/knowledge_base.py` | 1 day |
| 2.4 | Implement record validation and schema enforcement | `ml/knowledge/knowledge_base.py` | 1 day |
| 2.5 | Write data migration script (JSON → dataclass) | `scripts/migrate_knowledge_base.py` | 0.5 day |
| 2.6 | Write unit tests for all query methods | `tests/ml/knowledge/test_knowledge_base.py` | 2 days |
| 2.7 | Performance benchmark (load time, query latency) | Benchmark report | 1 day |
| 2.8 | Documentation update | Inline docstrings + README | 0.5 day |

### 2.2 Acceptance Criteria

- [ ] All 17 commodity profiles load correctly with validated fields
- [ ] Query by tolerance level returns correct subset
- [ ] Query by category returns correct subset
- [ ] Query by commodity_id returns single record
- [ ] Invalid commodity_id raises clear error
- [ ] Missing required field raises validation error
- [ ] Load time < 100ms on first access
- [ ] Query latency < 5ms after load
- [ ] 100% test coverage on query interface

### 2.3 Files Created

```
ml/knowledge/__init__.py
ml/knowledge/knowledge_base.py
ml/knowledge/types.py              (shared dataclass definitions)
scripts/migrate_knowledge_base.py
tests/ml/knowledge/test_knowledge_base.py
```

### 2.4 Files Modified

```
ml/service/predictor.py             (import new module, no behaviour change)
```

---

## 3. Sprint KB3 — Rule Engine

**Objective**: Implement rule-based inference engine.

**Duration**: 2 weeks

### 3.1 Tasks

| # | Task | Deliverable | Effort |
|---|------|-------------|--------|
| 3.1 | Define `DecisionSet` and `ScoredRecommendation` dataclasses | `ml/recommendation/rule_engine.py` | 0.5 day |
| 3.2 | Implement `RiskClassifier` (wraps existing classify_risk) | `ml/recommendation/rule_engine.py` | 0.5 day |
| 3.3 | Implement selection rules (R_L1, R_M1, R_H1–H4) | `ml/recommendation/rule_engine.py` | 2 days |
| 3.4 | Implement exclusion rules (R_M2–M4) | `ml/recommendation/rule_engine.py` | 1 day |
| 3.5 | Implement priority/ranking rules (R_L2, R_M5, R_E) | `ml/recommendation/rule_engine.py` | 1 day |
| 3.6 | Implement alternative rule with precondition generation | `ml/recommendation/rule_engine.py` | 1 day |
| 3.7 | Implement rule chain logging for explainability | `ml/recommendation/rule_engine.py` | 1 day |
| 3.8 | Implement Explanation Engine v2 | `ml/recommendation/explain_v2.py` | 2 days |
| 3.9 | Implement mitigation coupling with decision set | `ml/recommendation/mitigation.py` | 1 day |
| 3.10 | Write unit tests | `tests/ml/recommendation/test_rule_engine.py` | 3 days |
| 3.11 | Write rule validation tests | `tests/ml/recommendation/test_rules.py` | 1 day |

### 3.2 Acceptance Criteria

- [ ] All 3 risk levels produce correct categorisation (Rendah/Sedang/Tinggi)
- [ ] Low risk: all 17 commodities in recommended, 0 in alternative, 0 in not_recommended
- [ ] Medium risk: correct exclusion of low/very-low tolerance commodities
- [ ] High risk: only kangkung + talas in recommended; bayam + sawi in alternative
- [ ] Alternative commodities include precondition strings
- [ ] Rule chain is recorded for every recommendation
- [ ] Explanations reference rule IDs correctly
- [ ] Mitigation actions include per-commodity context
- [ ] No hardcoded commodity IDs — all data from Knowledge Base

### 3.3 Files Created

```
ml/recommendation/rule_engine.py
ml/recommendation/explain_v2.py
tests/ml/recommendation/test_rule_engine.py
tests/ml/recommendation/test_rules.py
```

### 3.4 Files Modified

```
ml/recommendation/mitigation.py     (enhanced with decision set context)
ml/service/predictor.py             (import new engine, no behaviour change)
```

---

## 4. Sprint KB4 — Backend Integration

**Objective**: Wire KB engine into API with backward-compatible response.

**Duration**: 2 weeks

### 4.1 Tasks

| # | Task | Deliverable | Effort |
|---|------|-------------|--------|
| 4.1 | Add new Pydantic response models | `backend/schemas/response.py` | 1 day |
| 4.2 | Implement `kb_recommend()` in predictor service | `ml/service/predictor.py` | 2 days |
| 4.3 | Parallel run: both engines execute; KB output stored | `ml/service/predictor.py` | 1 day |
| 4.4 | Wire new response sections into realtime endpoint | `backend/routers/realtime.py` | 1 day |
| 4.5 | Add API version header (`X-API-Version`) | `backend/app.py` | 0.5 day |
| 4.6 | Mark old PenjelasanResponse as deprecated | `backend/schemas/response.py` | 0.5 day |
| 4.7 | Comprehensive integration tests | `tests/backend/test_kb_realtime.py` | 3 days |
| 4.8 | Output comparison: heuristic vs KB on historical data | Comparison report | 2 days |

### 4.2 Acceptance Criteria

- [ ] API response includes all new sections (ringkasan, alternatif, tidak_direkomendasikan, sumber_pengetahuan)
- [ ] Old API fields remain present and functional
- [ ] Old `rekomendasi` key returns enriched `RekomendasiDetail[]` (backward compatible with skor/kategorisasi)
- [ ] No regression in existing tests
- [ ] KB output does not contradict heuristic output on top-5 commodities
- [ ] Response time increase < 20ms (KB query overhead)
- [ ] All acceptance criteria from KB2 and KB3 still satisfied

### 4.3 Files Modified

```
backend/schemas/response.py
backend/routers/realtime.py
ml/service/predictor.py
ml/recommendation/mitigation.py
```

### 4.4 Files Created

```
tests/backend/test_kb_realtime.py
```

---

## 5. Sprint KB5 — Frontend Migration

**Objective**: Replace existing recommendation UI with KB-DSS components.

**Duration**: 2 weeks

### 5.1 Tasks

| # | Task | Deliverable | Effort |
|---|------|-------------|--------|
| 5.1 | Update TypeScript API types | `apps/web/types/api.ts` | 0.5 day |
| 5.2 | Implement RecommendationBadge component | NEW file | 0.5 day |
| 5.3 | Implement VulnerabilityBars component | NEW file | 0.5 day |
| 5.4 | Implement CommodityCard component | NEW file | 1.5 days |
| 5.5 | Implement DecisionBanner component | NEW file | 0.5 day |
| 5.6 | Implement RecommendationTabs component | NEW file | 1 day |
| 5.7 | Implement CommodityDetailModal component | NEW file | 1.5 days |
| 5.8 | Implement KnowledgeSourceFooter component | NEW file | 0.5 day |
| 5.9 | Implement KBRecommendationSection (orchestrator) | NEW file | 1.5 days |
| 5.10 | Replace RecommendationAccordion in dashboard-panel | Modify file | 1 day |
| 5.11 | Delete old recommendation-card.tsx | Delete | 0.5 day |
| 5.12 | Storybook stories for new components | Story files | 1 day |
| 5.13 | Responsive testing (mobile, tablet, desktop) | Test report | 1 day |
| 5.14 | Accessibility audit | Audit report | 1 day |

### 5.2 Acceptance Criteria

- [ ] Decision banner correctly reflects risk level and planting decision
- [ ] Tabs filter commodity list by recommendation category
- [ ] Each commodity card shows badge, vulnerability bars, impacts
- [ ] Tapping card opens detail modal with full commodity info
- [ ] Knowledge source footer visible at bottom of section
- [ ] All components responsive down to 360px width
- [ ] WCAG AA contrast ratios met
- [ ] Keyboard navigation works correctly
- [ ] No visual regression in other dashboard sections

### 5.3 Files Created

```
apps/web/components/dashboard/kb-recommendation-section.tsx
apps/web/components/dashboard/commodity-card.tsx
apps/web/components/dashboard/commodity-detail-modal.tsx
apps/web/components/dashboard/decision-banner.tsx
apps/web/components/dashboard/recommendation-tabs.tsx
apps/web/components/dashboard/knowledge-source-footer.tsx
```

### 5.4 Files Modified

```
apps/web/types/api.ts
apps/web/components/dashboard/dashboard-panel.tsx
apps/web/components/dashboard/dashboard-screen.tsx  (if wiring needed)
```

### 5.5 Files Deleted

```
apps/web/components/dashboard/recommendation-card.tsx
```

---

## 6. Sprint KB6 — Testing & Validation

**Objective**: Comprehensive testing, validation, and legacy cleanup.

**Duration**: 2 weeks

### 6.1 Tasks

| # | Task | Deliverable | Effort |
|---|------|-------------|--------|
| 6.1 | End-to-end test: full pipeline (weather → FRI → KB → UI) | Test script | 2 days |
| 6.2 | Regression test: all existing prediction scenarios | Test suite | 1 day |
| 6.3 | Rule engine validation: verify all 17 commodities at 3 risk levels | Validation matrix | 1 day |
| 6.4 | Edge case testing: FRI=0, FRI=33, FRI=66, FRI=100 | Test report | 1 day |
| 6.5 | Performance test: KB load time under concurrent requests | Benchmark report | 1 day |
| 6.6 | Compare KB recommendations with domain expert evaluation | Expert review | 2 days |
| 6.7 | Remove legacy code (scorer.py, recommender.py, explain.py) | Clean PR | 0.5 day |
| 6.8 | Remove deprecated API response fields | `backend/schemas/response.py` | 0.5 day |
| 6.9 | Update developer documentation | README, CONTRIBUTING | 1 day |
| 6.10 | Final architecture review | Review meeting | 0.5 day |

### 6.2 Acceptance Criteria

- [ ] All 17 commodities correctly classified at all 3 risk levels
- [ ] Heuristic engine code fully removed
- [ ] Deprecated API fields removed (breaking change announced)
- [ ] All tests pass (unit, integration, e2e)
- [ ] Performance within 1.2x of old system
- [ ] Domain expert validates recommendation quality
- [ ] Documentation reflects final architecture

### 6.3 Files Modified

```
backend/schemas/response.py         (final cleanup)
ml/service/predictor.py             (remove parallel run code)
```

### 6.4 Files Deleted

```
ml/recommendation/scorer.py
ml/recommendation/recommender.py
ml/recommendation/explain.py
```

---

## 7. Resource Estimates

| Sprint | Dev Days | QA Days | Total Days |
|--------|----------|---------|------------|
| KB2 | 5 | 3 | 8 |
| KB3 | 8 | 4 | 12 |
| KB4 | 6 | 4 | 10 |
| KB5 | 8 | 3 | 11 |
| KB6 | 4 | 5 | 9 |
| **Total** | **31** | **19** | **50** |

---

## 8. Dependencies

| Sprint | Depends On | External Dependencies |
|--------|------------|----------------------|
| KB2 | KB1 (this document) | None |
| KB3 | KB2 | None |
| KB4 | KB2, KB3 | None |
| KB5 | KB4 | None |
| KB6 | KB2–KB5 | Domain expert availability |

No external service dependencies are introduced.

---

## 9. Success Criteria

The implementation is considered successful when:

1. All acceptance criteria for all 5 sprints are met
2. The KB-DSS produces scientifically grounded recommendations that match or exceed heuristic quality
3. Zero regressions in existing functionality
4. All legacy code is removed
5. Response time increase is within acceptable bounds (<20ms)
6. Domain experts validate recommendation quality
