# Migration Plan — Heuristic Scoring to Knowledge-Based Recommendation

## 1. Overview

This document defines the migration strategy for transitioning from the current heuristic commodity scoring engine to the new Knowledge-Based Decision Support System (KB-DSS) recommendation pipeline. The migration is phased to ensure zero downtime and continuous operation.

## 2. Modules to Deprecate

### 2.1 Direct Deprecation

The following modules will be removed entirely and replaced with new implementations:

| Module | File | Current Function | Deprecation Reason |
|--------|------|------------------|-------------------|
| **Commodity Scorer** | `ml/recommendation/scorer.py` | Computes weighted heuristic scores (toleransi 0.35, risiko 0.25, drainase 0.20, durasi 0.10, prioritas 0.10) | Heuristic weights are arbitrary, not scientifically derived. The weighted sum approach lacks rule transparency and does not model conditional logic (e.g., "if FRI > 66, exclude all medium-tolerance crops"). |
| **Commodity Ranking** | `ml/recommendation/recommender.py` | Sorts scored commodities descending, takes top N | Simple ranking loses the distinction between "recommended", "alternative", and "not recommended". Every commodity is ranked, even unsuitable ones. |
| **Explanation Engine v1** | `ml/recommendation/explain.py` | Generates explanations from score components | Explanations reference score sub-components (skor_toleransi, skor_drainase) that will no longer exist. New explanations must reference rule chain. |

### 2.2 Internal Deprecation (within modified files)

| Code Section | Location | Current Behaviour | Deprecation Reason |
|-------------|----------|-------------------|-------------------|
| `recommend()` call | `ml/service/predictor.py:72` | Calls `recommend(fri, top_n)` | Will be replaced by `kb_recommend(fri, risk_level)` |
| `explain_recommendation()` call | `ml/service/predictor.py:75` | Calls `explain_recommendation(id, fri, skor, confidence)` | Will be replaced by rule-chain-based explanation |
| `PenjelasanResponse` | `backend/schemas/response.py:12` | Flat recommendation response | Will be replaced by `RekomendasiDetail` with category, badge, preconditions |

## 3. Modules to Create (Replacements)

| Module | Path | Replaces | Description |
|--------|------|----------|-------------|
| **Knowledge Base Engine** | `ml/knowledge/knowledge_base.py` | `scorer.py` profiles loading | Structured commodity record management with query interface and validation |
| **Rule Engine** | `ml/recommendation/rule_engine.py` | `scorer.py` + `recommender.py` | Rule-based inference producing categorised recommendation sets |
| **Explanation Engine v2** | `ml/recommendation/explain_v2.py` | `explain.py` | Rule-chain-based explanation generator |

## 4. Modules to Modify

| Module | Change Type | Description |
|---------|-------------|-------------|
| `ml/recommendation/mitigation.py` | Enhancement | Add per-commodity mitigation coupling; accept decision set as input |
| `ml/service/predictor.py` | Internal refactor | Replace `recommend()` → `kb_recommend()`; enrich output structure |
| `backend/schemas/response.py` | Addition | Add new response models alongside existing; no field removal |
| `backend/routers/realtime.py` | Wiring | Enrich response with new sections |
| `apps/web/types/api.ts` | Type addition | Add TypeScript interfaces for new response sections |
| `apps/web/components/dashboard/dashboard-panel.tsx` | UI replacement | Replace `RecommendationAccordion` with `KBRecommendationSection` |
| `apps/web/components/dashboard/recommendation-card.tsx` | Replacement | Replace with new CommodityCard set |

## 5. Migration Phases

### 5.1 Phase 0: Parallel Run (Sprint KB4)

**Objective**: New KB engine runs alongside existing engine. No user-facing changes.

```
┌─────────────────────────────────┐
│  prediksi()                     │
│  ├── recommend()    ──► OLD     │  → still populates rekomendasi[]
│  └── kb_recommend() ──► NEW    │  → populates new fields (hidden)
└─────────────────────────────────┘
```

| Action | Detail |
|--------|--------|
| Implement Knowledge Base Engine | `ml/knowledge/knowledge_base.py` |
| Implement Rule Engine | `ml/recommendation/rule_engine.py` |
| Implement Explanation v2 | `ml/recommendation/explain_v2.py` |
| Add `kb_recommend()` to predictor | Runs both engines; stores KB output internally |
| Add new API response schemas | Not returned yet; stored for logging/comparison |
| Validation | Compare KB output vs. heuristic output on 100+ historical predictions |

**Files changed**: `ml/knowledge/knowledge_base.py` (NEW), `ml/recommendation/rule_engine.py` (NEW), `ml/recommendation/explain_v2.py` (NEW)

### 5.2 Phase 1: API Enrichment (Sprint KB4)

**Objective**: New fields added to API response. Legacy fields retained.

```
Response now includes:
┌── rekomendasi[] - OLD format (PenjelasanResponse) ← backward compat
├── ringkasan - NEW (executive summary)
├── rekomendasi - NEW format (RekomendasiDetail[])
├── alternatif - NEW
├── tidak_direkomendasikan - NEW
├── sumber_pengetahuan - NEW
└── mitigasi[] - ENHANCED
```

| Action | Detail |
|--------|--------|
| Add new Pydantic models | `backend/schemas/response.py` — additive only |
| Wire new fields into realtime endpoint | `backend/routers/realtime.py` |
| API version header | Add `X-API-Version: 2.0` header |
| Deprecation notice | Mark old `PenjelasanResponse` as deprecated in OpenAPI schema |

**Files changed**: `backend/schemas/response.py`, `backend/routers/realtime.py`, `ml/service/predictor.py`

### 5.3 Phase 2: Frontend Migration (Sprint KB5)

**Objective**: Frontend adopts new response structure. Old UI components replaced.

```
Before → After
RecommendationAccordion → KBRecommendationSection
RecommendationAccordion → DecisionBanner + RecommendationTabs + CommodityCardList
recommendation-card.tsx → commodity-card.tsx + commodity-detail-modal.tsx
```

| Action | Detail |
|--------|--------|
| New TypeScript interfaces | `apps/web/types/api.ts` — additive |
| KBRecommendationSection component | New component consuming new API sections |
| CommodityCard component | Card with badge, vulnerability bars, detail |
| CommodityDetailModal | Modal with full commodity info |
| DecisionBanner component | Risk-level-based banner |
| RecommendationTabs component | Tab filtering by category |
| KnowledgeSourceFooter component | Provenance display |
| Delete old components | `recommendation-card.tsx`, old accordion code |

**Files changed**: Multiple frontend files (see Section 8)

### 5.4 Phase 3: Legacy Removal (Sprint KB6)

**Objective**: Old code and fields removed.

| Action | Detail |
|--------|--------|
| Remove old `rekomendasi` field | API returns only new format |
| Delete `scorer.py` | No longer used |
| Delete `recommender.py` | No longer used |
| Delete `explain.py` | No longer used |
| Clean up predictor | Remove parallel run code |
| Remove deprecated TypeScript types | Clean frontend types |

## 6. Dependency Graph

```
Sprint KB2: Knowledge Base Engine
  └── No dependencies (new module)

Sprint KB3: Rule Engine
  └── Depends on: Knowledge Base Engine (KB Sprint 2)

Sprint KB4: Backend Integration
  ├── Depends on: Rule Engine (KB Sprint 3)
  ├── Depends on: Knowledge Base Engine (KB Sprint 2)
  └── Depends on: Explanation Engine v2 (KB Sprint 3)

Sprint KB5: Frontend Migration
  └── Depends on: Backend Integration (KB Sprint 4)

Sprint KB6: Testing
  └── Depends on: All previous sprints
```

## 7. Rollback Strategy

| Phase | Rollback Action | Impact |
|-------|-----------------|--------|
| Phase 0 | Remove KB code; fall back to existing engine | No user impact (KB not user-facing) |
| Phase 1 | Revert `response.py` and `realtime.py` changes | Old API format restored |
| Phase 2 | Revert frontend changes; restore old components | Old UI restored |
| Phase 3 | Restore deleted files from git | Full rollback to heuristic engine |

## 8. File Change Summary

### Files to Create
```
ml/knowledge/__init__.py
ml/knowledge/knowledge_base.py
ml/recommendation/rule_engine.py
ml/recommendation/explain_v2.py
apps/web/components/dashboard/kb-recommendation-section.tsx
apps/web/components/dashboard/commodity-card.tsx
apps/web/components/dashboard/commodity-detail-modal.tsx
apps/web/components/dashboard/decision-banner.tsx
apps/web/components/dashboard/recommendation-tabs.tsx
apps/web/components/dashboard/knowledge-source-footer.tsx
```

### Files to Delete
```
ml/recommendation/scorer.py
ml/recommendation/recommender.py
ml/recommendation/explain.py
```

### Files to Modify
```
ml/service/predictor.py
ml/recommendation/mitigation.py
backend/schemas/response.py
backend/routers/realtime.py
apps/web/types/api.ts
apps/web/components/dashboard/dashboard-panel.tsx
apps/web/components/dashboard/dashboard-screen.tsx
```

### Files with No Changes
```
ml/predict/random_forest.py
ml/predict/lstm.py
ml/predict/risk.py
ml/predict/preprocess.py
ml/feature_engineering/builder.py
ml/artifacts/*
backend/providers/*
backend/dependencies/*
backend/security/*
backend/services/prediction_gateway.py
apps/web/hooks/*
apps/web/services/*
apps/web/app/*
data/*
```
