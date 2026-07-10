# Sprint KB1 — Design Freeze Report

## Knowledge-Based Decision Support System (KB-DSS) Architecture Design

---

## 1. Sprint Summary

| Attribute | Detail |
|-----------|--------|
| Sprint ID | KB1 |
| Title | Knowledge-Based Recommendation System Design Freeze |
| Duration | Design Only (no implementation) |
| Status | ✅ **FROZEN** |
| Date | 2026-07-08 |
| Author | System Architecture Team |

---

## 2. What Was Produced

This design freeze produced the following documents in `docs/research/kb_recommendation/`:

| # | Document | Description |
|---|----------|-------------|
| 1 | `01_KNOWLEDGE_BASE_SPECIFICATION.md` | Complete schema definition for the knowledge base including 17 commodity records with scientific justification, enum definitions, query interface design, and versioning strategy |
| 2 | `02_RULE_ENGINE_SPECIFICATION.md` | Deterministic inference rules mapping FRI → Risk Category → Commodity Decisions, with 14 formal rules (R1–R_MIT), scientific reasoning, priority order, and conflict resolution |
| 3 | `03_RECOMMENDATION_ARCHITECTURE.md` | Full architecture diagram showing component interactions, sequence diagrams for the complete prediction-to-recommendation flow, module boundary map, and error handling strategy |
| 4 | `04_API_RESPONSE_DESIGN.md` | Future API response design with 5 new sections (ringkasan, alternatif, tidak_direkomendasikan, sumber_pengetahuan, enhanced mitigasi), backward-compatible additive schema, and example responses for all 3 risk levels |
| 5 | `05_UI_DESIGN_SPECIFICATION.md` | Redesigned frontend UI flow with Decision Banner, Recommendation Category Tabs, Commodity Cards with vulnerability bars and badges, Commodity Detail Modal, Knowledge Source Footer, responsive breakpoints, and accessibility requirements |
| 6 | `06_MIGRATION_PLAN.md` | Phased migration strategy (Parallel Run → API Enrichment → Frontend Migration → Legacy Removal) with file-level change tracking, dependency graph, and rollback strategy for each phase |
| 7 | `07_BACKWARD_COMPATIBILITY.md` | Comprehensive compatibility analysis: 30+ components identified as completely unchanged, all API changes verified as additive, deprecation timeline, and potential breaking changes mitigated |
| 8 | `08_IMPLEMENTATION_ROADMAP.md` | 5-sprint implementation plan (KB2–KB6) with 40+ tasks, effort estimates (50 person-days total), acceptance criteria for each sprint, resource allocation, and dependency management |
| 9 | `09_RISK_ASSESSMENT.md` | 12 identified risks across 4 categories (Technical, Research, Migration, Rollback) with probability/impact assessment, mitigation strategies, rollback procedures, monitoring plan, and go/no-go decision points |

---

## 3. Architecture Decisions

### 3.1 Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Knowledge Base as dataclass module, not JSON** | Type safety, validation, query interface, and immutability enforce data integrity at runtime. JSON is used only as source data. |
| **Rule Engine replaces weighted scoring entirely** | Weighted heuristic (0.35/0.25/0.20/0.10/0.10) has no scientific basis. Rules are transparent, testable, and justifiable. |
| **Categorical recommendation (recommended / alternative / not_recommended) replaces ranked list** | Farmers need decision categories, not ordinal ranks. "Should I plant this?" is a categorical question, not a ranking question. |
| **Additive API changes only** | Zero breaking changes to existing consumers. Old fields preserved exactly. New fields add value without disruption. |
| **Decision Banner + Tabs + Cards replaces Accordion** | Information architecture improves: farmers see the decision first, then explore by category, then drill into details. |
| **Research Assumptions explicitly flagged** | All knowledge entries marked as `is_assumption: true` until validated by field studies. Users are informed of confidence level. |

### 3.2 Decisions Deliberately Out of Scope

| Decision | Reason |
|----------|--------|
| ML model retraining or re-evaluation | Random Forest and LSTM are explicitly out of scope; only the recommendation engine is redesigned |
| Database integration | Knowledge base stays in application memory; no PostgreSQL/vector DB required for 17 records |
| User feedback loop | Not included in initial design; can be added as post-migration enhancement |
| Multi-language support | Documentation and system use Bahasa Indonesia only; internationalisation deferred |
| Real-time weather API changes | Open-Meteo provider unchanged; future weather provider migration is separate |

---

## 4. Scientific Justification Summary

Every design decision in this freeze is grounded in the repository's knowledge source (`commodity_profiles.json`). Key scientific mappings:

| FRI Range | Agricultural Interpretation | Rule Basis |
|-----------|---------------------------|------------|
| 0–33 | Normal soil moisture; all crops viable | No physiological stress; standard agronomy |
| 33–66 | Sustained elevated moisture; root zone stress begins | Species with < "Sedang" tolerance suffer root hypoxia within hours |
| 66–100 | Soil saturation / inundation; anaerobic conditions | Only semi-aquatic species survive prolonged root submersion |

Commodity tolerance assignments follow:
- **Very High/High**: Botanical adaptations (aerenchyma, adventitious roots) in kangkung (*Ipomoea aquatica*) and talas (*Colocasia esculenta*)
- **Medium**: Generalist species with moderate flood avoidance (climbing habit in kacang panjang and pare; short cycles in bayam and sawi)
- **Low/Very Low**: Species lacking flood-adaptation mechanisms (fleshy fruit rot in melon/semangka; *Phytophthora* susceptibility in tomat/cabai)

---

## 5. Verification Against Constraints

| Constraint | Status | Evidence |
|------------|--------|----------|
| No backend code modified | ✅ | All specifications are documentation only |
| No frontend code modified | ✅ | 05_UI_DESIGN_SPECIFICATION.md specifies wireframes, not code |
| No API implementation modified | ✅ | 04_API_RESPONSE_DESIGN.md specifies future design, not current |
| No ML model modified | ✅ | Random Forest and LSTM explicitly listed as unchanged in 07 |
| No RF modified | ✅ | Specified in backward compatibility matrix |
| No recommendation code modified | ✅ | scorer.py, recommender.py, explain.py untouched |
| No datasets modified | ✅ | commodity_profiles.json, mitigation_rules.json, etc. untouched |
| No JSON files modified | ✅ | All knowledge files remain as-is |
| No deployment configuration modified | ✅ | No docker/CI/CD files referenced |
| No implementation code created | ✅ | All deliverables are .md documentation files only |

---

## 6. Readiness for KB Sprint 2

### 6.1 All Implementation Decisions Documented

| Decision Area | Documentation Location | Ready |
|--------------|----------------------|-------|
| Knowledge base schema | `01_KNOWLEDGE_BASE_SPECIFICATION.md` Section 3 | ✅ |
| Commodity records (all 17) | `01_KNOWLEDGE_BASE_SPECIFICATION.md` Section 4 | ✅ |
| Enum definitions | `01_KNOWLEDGE_BASE_SPECIFICATION.md` Section 3.2 | ✅ |
| Query interface design | `01_KNOWLEDGE_BASE_SPECIFICATION.md` Section 7 | ✅ |
| Risk classification thresholds | `02_RULE_ENGINE_SPECIFICATION.md` Section 3 | ✅ |
| Inference rules (all 14) | `02_RULE_ENGINE_SPECIFICATION.md` Sections 5–6 | ✅ |
| Rule priority and conflict resolution | `02_RULE_ENGINE_SPECIFICATION.md` Section 7 | ✅ |
| Module architecture and interactions | `03_RECOMMENDATION_ARCHITECTURE.md` Sections 2–4 | ✅ |
| Sequence diagram | `03_RECOMMENDATION_ARCHITECTURE.md` Section 3 | ✅ |
| API response JSON structure | `04_API_RESPONSE_DESIGN.md` Section 3 | ✅ |
| Pydantic schema design | `04_API_RESPONSE_DESIGN.md` Section 4 | ✅ |
| UI component tree and layout | `05_UI_DESIGN_SPECIFICATION.md` Sections 3–9 | ✅ |
| Wireframes for all card states | `05_UI_DESIGN_SPECIFICATION.md` Section 3.2 | ✅ |
| Accessibility requirements | `05_UI_DESIGN_SPECIFICATION.md` Section 12 | ✅ |
| File change inventory | `06_MIGRATION_PLAN.md` Section 8 | ✅ |
| Backward compatibility matrix | `07_BACKWARD_COMPATIBILITY.md` Section 1 | ✅ |
| Sprint task breakdown | `08_IMPLEMENTATION_ROADMAP.md` Sections 2–6 | ✅ |
| Acceptance criteria per sprint | `08_IMPLEMENTATION_ROADMAP.md` Sections 2.2–6.2 | ✅ |
| Risk matrix and mitigation | `09_RISK_ASSESSMENT.md` Section 1 | ✅ |
| Rollback strategy | `09_RISK_ASSESSMENT.md` Section 5 | ✅ |

### 6.2 Immediate Next Steps

The architecture team recommends the following order for KB Sprint 2:

1. **Day 1–2**: Set up `ml/knowledge/` package structure with `types.py` and `knowledge_base.py`
2. **Day 3**: Implement `CommodityRecord` dataclass and validation
3. **Day 4–5**: Implement `KnowledgeBase` class with query interface
4. **Day 6–7**: Write comprehensive unit tests
5. **Day 8**: Code review and documentation update
6. **Day 9–10**: Buffer for issues identified during implementation

---

## 7. Sign-Off

This design freeze is considered complete and ready for Sprint KB2 implementation.

| Role | Status |
|------|--------|
| Architecture Design | ✅ Complete |
| Scientific Justification | ✅ Documented |
| Backward Compatibility | ✅ Verified |
| Migration Planning | ✅ Complete |
| Risk Assessment | ✅ Reviewed |
| Implementation Specification | ✅ All decisions documented |

**Sprint KB1 Design Freeze — FROZEN**

*No further design changes will be accepted for this sprint. Implementation decisions are captured in full above.*
