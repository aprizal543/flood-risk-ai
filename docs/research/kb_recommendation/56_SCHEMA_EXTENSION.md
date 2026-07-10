# Sprint KB8.6 — Schema Extension

**Date:** 2026-07-10
**Schema Version:** 2.1 (bumped from 2.0)

---

## Changes

### 1. New Authoritative Fields

Added two new authoritative fields to `CommodityKnowledge` model:

```python
main_impacts: list[str]  # Exact lecturer wording for main impacts
damage_symptoms: list[str]  # Exact lecturer wording for damage symptoms
```

Both fields:
- `min_length=1` — must contain at least 1 item
- `frozen=True` — immutable after construction
- `extra="forbid"` — unknown fields rejected

### 2. Field Hierarchy

```
Authoritative (new):
  main_impacts  ─── reads from ─── dampak_utama (lecturer)
  damage_symptoms ─── reads from ─── gejala_kerusakan (lecturer)

Deprecated (kept for backward compat):
  major_impacts ─── maps from dampak_utama
  recommendation_notes (catatan) ─── legacy only

Unchanged (lecturer-derived, kept):
  dampak_utama ─── Indonesian lecturer impacts
  gejala_kerusakan ─── Indonesian lecturer symptoms
```

### 3. Backward Compatibility

All deprecated fields remain:
- `commodity_category`
- `vulnerability_level`
- `flood_tolerance_category`
- `drainage_requirement`
- `growing_duration_days`
- `optimal_risk_level`
- `economic_priority`
- `major_impacts`
- `recommendation_notes` (catatan)
- `scientific_reference`
- `version`
- `last_updated`

### 4. Changed Files

| File | Change |
|------|--------|
| `backend/knowledge/models.py` | Added `main_impacts`, `damage_symptoms` fields; updated docstrings |
| `backend/knowledge/data/commodity_knowledge.json` | Added `main_impacts` (×22), fixed `damage_symptoms` (×5), fixed `major_impacts` (×10), bumped version to 2.1 |
| `ml/knowledge/commodity_profiles.json` | Added `main_impacts` (×22), `damage_symptoms` (×22) |
| `backend/knowledge/validator.py` | Added `main_impacts`/`damage_symptoms` to lecturer fields and list field validation |
| `backend/services/recommendation_mapper.py` | Exposes `main_impacts`, `damage_symptoms`, `maximum_inundation_duration` in API response |
| `apps/web/types/api.ts` | Added `main_impacts`, `damage_symptoms`, `maximum_inundation_duration` to TypeScript types |
| `apps/web/components/recommendation/CommodityCard.tsx` | Reads from `maximum_inundation_duration`, `main_impacts`, `damage_symptoms` instead of legacy fields |

### 5. Data Fixes Applied

| Issue | Commodities | Fix |
|-------|-------------|-----|
| Truncated `major_impacts` (5→3) | wortel, lobak, labu_siam, buncis | Restored to full 5 items |
| Truncated `major_impacts` (4→2) | kangkung_air, genjer, selada_air | Restored to full count |
| Truncated `damage_symptoms` (4→3) | wortel, lobak, labu_siam, buncis | Restored to full 4 items |
| Wrong content in all fields | talas | Replaced with correct lecturer content |
| Missing `main_impacts` | All 22 | Added (copy of `dampak_utama`) |
| Missing structured fields in ML | All 22 | Added `main_impacts` + `damage_symptoms` |
