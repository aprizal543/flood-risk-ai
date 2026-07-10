# 48 — Migration Summary

## Objective

Document the migration from the old Knowledge Base (17 commodities, schema v1.0) to the new lecturer-synchronized Knowledge Base (22 commodities, schema v2.0).

---

## What Changed

### Commodity Data

| Metric | Pre-Migration | Post-Migration |
|--------|---------------|----------------|
| Total commodities | 17 | 22 |
| Source of truth | FAO + general agronomy | Lecturer recommendation document |
| Schema version | 1.0 | 2.0 |

### Data Fields Added

| Field | Type | Source |
|-------|------|--------|
| `aliases` | list[string] | Lecturer document (Alias column) |
| `kelompok_kerentanan` | list[string] | Lecturer document |
| `tingkat_kerentanan` | string | Lecturer document |
| `batas_toleransi_genangan` | string | Lecturer document |
| `dampak_utama` | list[string] | Lecturer document |
| `gejala_kerusakan` | list[string] | Lecturer document |

### Commodity Changes

**Removed (6):**
- Bayam, Pare, Melon, Semangka, Jagung Manis, Kemangi

**Renamed (2):**
- Kangkung → Kangkung Air
- Selada → Selada Air

**Merged (2→1):**
- Cabai Rawit + Cabai Merah → Cabai

**Added (12):**
- Bawang Merah, Kentang, Paprika, Kubis, Pakcoy, Wortel, Lobak, Labu Siam, Buncis, Genjer, Pakis Sayur, Semanggi

**Kept (7):**
- Sawi Hijau, Tomat, Terong, Mentimun, Kacang Panjang, Talas, Seledri

---

## Files Changed

| File | Change Type |
|------|-------------|
| `ml/knowledge/commodity_profiles.json` | Updated |
| `ml/knowledge/recommendation_rules.json` | Updated (v4.0) |
| `backend/knowledge/data/commodity_knowledge.json` | Replaced |
| `backend/knowledge/models.py` | Updated (v2.0) |
| `backend/knowledge/validator.py` | Updated |
| `scripts/validation/01_knowledge_validation.py` | Updated |
| `scripts/validation/03_engine_validation.py` | Updated |
| `scripts/validation/06_e2e_consistency.py` | Updated |
| `backend/decision/validator.py` | Updated |

---

## Backward Compatibility

All deprecated fields from schema v1.0 are retained for backward compatibility:

- `commodity_category`
- `vulnerability_level`
- `flood_tolerance_category`
- `drainage_requirement`
- `growing_duration_days`
- `optimal_risk_level`
- `economic_priority`
- `major_impacts`
- `damage_symptoms`
- `recommendation_notes`
- `scientific_reference`
- `version`
- `last_updated`

These fields are marked as DEPRECATED in the Pydantic model docstrings.

---

## API Compatibility

| Endpoint | Expected Behavior | Compatible? |
|----------|-------------------|-------------|
| `POST /api/prediksi/manual` | Returns legacy `rekomendasi` + `knowledge_recommendation` | ✓ |
| `POST /api/prediksi/engineered` | Same augmentation pattern | ✓ |
| `GET /api/prediksi/realtime` | Returns `knowledge_recommendation` | ✓ |
| `GET /api/health` | Returns KB/Decision Engine status | ✓ |
| `GET /api/health/detail` | Returns knowledge_base_detail | ✓ |

---

## Deployment Notes

1. The Knowledge Base data file is read at startup. No hot-reload is required.
2. The legacy ML system (`scorer.py`, `explain.py`) loads `commodity_profiles.json` independently and will automatically use the new data.
3. The KB-DSS system (`loader.py`, `cache.py`, `query.py`) loads `commodity_knowledge.json` and will validate on startup.
4. If validation fails, the application will not start. See `47_VALIDATION_REPORT.md` for validation criteria.

---

## Rollback Plan

To revert to the previous Knowledge Base:

1. Restore `ml/knowledge/commodity_profiles.json` from backup
2. Restore `backend/knowledge/data/commodity_knowledge.json` from backup
3. Restore `backend/knowledge/models.py` from backup
4. Restore `backend/knowledge/validator.py` from backup
5. Restart the application
