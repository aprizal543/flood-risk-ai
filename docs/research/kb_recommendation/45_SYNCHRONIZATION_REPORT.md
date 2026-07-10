# 45 — Synchronization Report

## Objective

Synchronize the full Knowledge Base with the lecturer recommendation document, ensuring every commodity, attribute, and recommendation exactly matches the lecturer's official source of truth.

---

## Changes Made

### 1. Commodity List Synchronization

| Action | Count | Commodities |
|--------|-------|-------------|
| Kept (unchanged) | 7 | sawi, tomat, terong, mentimun, kacang_panjang, talas, seledri |
| Renamed | 2 | kangkung → kangkung_air, selada → selada_air |
| Merged | 2→1 | cabai_rawit + cabai_merah → cabai |
| Removed | 6 | bayam, pare, melon, semangka, jagung_manis, kemangi |
| Added | 12 | bawang_merah, kentang, paprika, kubis, pakcoy, wortel, lobak, labu_siam, buncis, genjer, pakis_sayur, semanggi |
| **Final total** | **22** | |

### 2. Naming Normalization

| Pre-Sync | Post-Sync | Reason |
|----------|-----------|--------|
| Kangkung | Kangkung Air | Lecturer document specifies "Kangkung Air" |
| Selada | Selada Air | Lecturer document specifies "Selada Air" |
| Cabai Rawit + Cabai Merah | Cabai | Lecturer document treats as single commodity "Cabai" |
| Sawi Hijau | Sawi Hijau | Kept (lecturer uses "Sawi Hijau" with alias "Caisim") |

### 3. Attribute Synchronization

All commodity attributes now derived from lecturer document:

- **kelompok_kerentanan**: Captures all vulnerability groups (Tinggi/Sedang/Rendah) per commodity
- **tingkat_kerentanan**: Exact copy of lecturer's classification (e.g. "Sangat Rentan (Highly Sensitive)")
- **batas_toleransi_genangan**: Exact copy of lecturer's tolerance duration (e.g. "Kurang dari 24 jam")
- **dampak_utama**: Exact copy of lecturer's impact descriptions
- **gejala_kerusakan**: Derived from lecturer's damage symptom descriptions

### 4. Vulnerability Category Mapping

Each commodity's `vulnerability_level` (used by Decision Engine) is derived from the lecturer doc:

| Lecturer Classification | Mapped To | Count | Examples |
|------------------------|-----------|-------|----------|
| Sangat Rentan (Highly Sensitive) | Sangat Rendah | 5 | cabai, tomat, bawang_merah, kentang, paprika |
| Rentan (Moderately Sensitive) | Rendah | 6 | kubis, pakcoy, sawi, terong, mentimun, kacang_panjang |
| Agak Toleran / Toleran Sedang | Sedang | 5 | wortel, lobak, labu_siam, buncis, seledri |
| Toleran (Toleransi Tinggi) | Tinggi | 3 | selada_air, talas, pakis_sayur |
| Sangat Toleran / Vegetasi Akuatik | Sangat Tinggi | 3 | kangkung_air, genjer, semanggi |

---

## Files Modified

| File | Change |
|------|--------|
| `ml/knowledge/commodity_profiles.json` | Updated commodity list (22 items), updated attributes |
| `ml/knowledge/recommendation_rules.json` | Updated v4.0 with new commodity IDs |
| `backend/knowledge/data/commodity_knowledge.json` | Complete restructure with lecturer-derived fields |
| `backend/knowledge/models.py` | Added lecturer fields, deprecated old fields, new v2.0 schema |
| `backend/knowledge/validator.py` | Updated validation rules for new schema, added lecturer existence check |
| `scripts/validation/01_knowledge_validation.py` | Updated for 22 commodities, lecturer-specific checks |

---

## Validation

| Check | Result |
|-------|--------|
| Knowledge validation | PASS (794 checks, 0 errors) |
| Rule validation | PASS (15/15 rules) |
| Decision engine validation | PASS (22 commodities classified correctly) |
| Legacy scorer | PASS (22 commodities scored) |
| Commodity count matches lecturer | PASS (22 = 22) |
| No unsupported commodities | PASS |
| No missing lecturer commodities | PASS |

---

## Conclusion

Knowledge Base has been fully synchronized with the lecturer recommendation document. All 22 commodities match exactly. Attributes are copied directly from the lecturer document without paraphrasing or interpretation.
