# 44 — Knowledge Base Audit

## Objective

Audit every commodity in the project's Knowledge Base against the lecturer recommendation document. The lecturer document is the single source of truth.

---

## Current Project Commodities (17 total)

| # | ID | Nama | Source File |
|---|-----|------|-------------|
| 1 | kangkung | Kangkung | commodity_profiles.json, commodity_knowledge.json |
| 2 | bayam | Bayam | commodity_profiles.json, commodity_knowledge.json |
| 3 | sawi | Sawi Hijau | commodity_profiles.json, commodity_knowledge.json |
| 4 | selada | Selada | commodity_profiles.json, commodity_knowledge.json |
| 5 | cabai_rawit | Cabai Rawit | commodity_profiles.json, commodity_knowledge.json |
| 6 | cabai_merah | Cabai Merah | commodity_profiles.json, commodity_knowledge.json |
| 7 | tomat | Tomat | commodity_profiles.json, commodity_knowledge.json |
| 8 | terong | Terong | commodity_profiles.json, commodity_knowledge.json |
| 9 | mentimun | Mentimun | commodity_profiles.json, commodity_knowledge.json |
| 10 | kacang_panjang | Kacang Panjang | commodity_profiles.json, commodity_knowledge.json |
| 11 | pare | Pare | commodity_profiles.json, commodity_knowledge.json |
| 12 | melon | Melon | commodity_profiles.json, commodity_knowledge.json |
| 13 | semangka | Semangka | commodity_profiles.json, commodity_knowledge.json |
| 14 | jagung_manis | Jagung Manis | commodity_profiles.json, commodity_knowledge.json |
| 15 | talas | Talas | commodity_profiles.json, commodity_knowledge.json |
| 16 | seledri | Seledri | commodity_profiles.json, commodity_knowledge.json |
| 17 | kemangi | Kemangi | commodity_profiles.json, commodity_knowledge.json |

---

## Lecturer Document Commodities (22 unique)

| # | Komoditas | Alias | Kelompok Kerentanan | Tingkat Kerentanan | Batas Toleransi |
|---|-----------|-------|---------------------|--------------------|-----------------|
| 1 | Cabai | - | Tinggi | Sangat Rentan (Highly Sensitive) | <24 jam |
| 2 | Tomat | - | Tinggi | Sangat Rentan (Highly Sensitive) | <24 jam |
| 3 | Bawang Merah | - | Tinggi | Sangat Rentan (Highly Sensitive) | <24 jam |
| 4 | Kentang | - | Tinggi | Sangat Rentan (Highly Sensitive) | <24 jam |
| 5 | Paprika | - | Tinggi | Sangat Rentan (Highly Sensitive) | <24 jam |
| 6 | Kubis | Kol | Tinggi, Sedang | Rentan / Rentan Sedang | 24-48 jam |
| 7 | Pakcoy | Sawi Daging | Tinggi, Sedang | Rentan / Rentan Sedang | 24-48 jam |
| 8 | Sawi Hijau | Caisim | Tinggi, Sedang | Rentan / Rentan Sedang | 24-48 jam |
| 9 | Terong | - | Tinggi, Sedang | Rentan / Rentan Sedang | 24-48 jam |
| 10 | Kacang Panjang | - | Tinggi, Sedang | Rentan / Rentan Sedang | 24-48 jam |
| 11 | Mentimun | - | Tinggi, Sedang | Rentan / Rentan Sedang | 24-48 jam |
| 12 | Wortel | - | Tinggi, Sedang | Agak Toleran / Toleran Sedang | 48-72 jam |
| 13 | Lobak | - | Tinggi, Sedang | Agak Toleran / Toleran Sedang | 48-72 jam |
| 14 | Labu Siam | Waluh | Tinggi, Sedang | Agak Toleran / Toleran Sedang | 48-72 jam |
| 15 | Buncis | - | Tinggi, Sedang | Agak Toleran / Toleran Sedang | 48-72 jam |
| 16 | Kangkung Air | - | Tinggi, Rendah | Toleran / Sangat Toleran | >72 jam / Permanen |
| 17 | Genjer | - | Tinggi, Rendah | Toleran / Sangat Toleran | >72 jam / Permanen |
| 18 | Selada Air | - | Tinggi, Rendah | Toleran / Toleran | >72 jam / >72 jam |
| 19 | Talas | Keladi | Tinggi, Rendah | Toleran / Toleran | >72 jam / >72 jam |
| 20 | Seledri | - | Sedang | Toleran Sedang | 48-72 jam |
| 21 | Pakis Sayur | Paku | Rendah | Toleran (Toleransi Tinggi) | >72 jam |
| 22 | Semanggi | - | Rendah | Sangat Toleran (Vegetasi Akuatik) | Permanen |

---

## Audit Findings

### 1. Commodities to Remove (not in lecturer document)

| Commodity | Reason |
|-----------|--------|
| Bayam | Not listed in lecturer document |
| Pare | Not listed in lecturer document |
| Melon | Not listed in lecturer document |
| Semangka | Not listed in lecturer document |
| Jagung Manis | Not listed in lecturer document |
| Kemangi | Not listed in lecturer document |

### 2. Commodities to Add (in lecturer document, not in KB)

| Commodity | Internal ID |
|-----------|-------------|
| Bawang Merah | bawang_merah |
| Kentang | kentang |
| Paprika | paprika |
| Kubis | kubis |
| Pakcoy | pakcoy |
| Wortel | wortel |
| Lobak | lobak |
| Labu Siam | labu_siam |
| Buncis | buncis |
| Genjer | genjer |
| Pakis Sayur | pakis_sayur |
| Semanggi | semanggi |

### 3. Naming Inconsistencies

| Current Name | Lecturer Name | Action |
|--------------|---------------|--------|
| Kangkung | Kangkung Air | Rename |
| Selada | Selada Air | Rename |
| Cabai Rawit | Cabai | Merge (single "Cabai" entry) |
| Cabai Merah | Cabai | Merge (single "Cabai" entry) |

### 4. Attribute Inconsistencies

| Commodity | Current KB Field | Current Value | Lecturer Value | Action |
|-----------|-----------------|---------------|----------------|--------|
| Sawi Hijau | vulnerability_level | Tinggi | Rentan (→ Rendah) | Update |
| Sawi Hijau | flood_tolerance_category | Tinggi | Rentan / Rentan Sedang | Update |
| Sawi Hijau | maximum_inundation_duration | 2-3 hari | 24-48 jam | Update |
| Terong | vulnerability_level | Sedang | Rentan (→ Rendah) | Update |
| Terong | maximum_inundation_duration | 24 jam | 24-48 jam | Update |
| Kacang Panjang | vulnerability_level | Sedang | Rentan (→ Rendah) | Update |
| Kacang Panjang | maximum_inundation_duration | 24 jam | 24-48 jam | Update |
| Mentimun | vulnerability_level | Sedang | Rentan (→ Rendah) | Update |
| Mentimun | maximum_inundation_duration | 12-24 jam | 24-48 jam | Update |
| Tomat | vulnerability_level | Rendah | Sangat Rentan (→ Sangat Rendah) | Update |
| Tomat | maximum_inundation_duration | <6 jam | <24 jam | Update |
| Kangkung | vulnerability_level | Sangat Tinggi | Toleran / Sangat Toleran | Update |
| Talas | vulnerability_level | Sangat Tinggi | Toleran (→ Tinggi) | Update |
| Talas | maximum_inundation_duration | >7 hari | >72 jam / 3-7 hari | Update |
| Seledri | vulnerability_level | Sedang | Toleran Sedang (→ Sedang) | Keep (matches) |
| Seledri | maximum_inundation_duration | 12-24 jam | 48-72 jam | Update |

### 5. Missing Attributes (Lecturer has, KB doesn't)

- Aliases for commodities that have them (e.g., Kubis = Kol, Pakcoy = Sawi Daging)
- Multiple vulnerability profiles per commodity (some appear in 2+ Kelompok Kerentanan)
- Lecturer-specific Dampak Utama & Gejala Kerusakan text

### 6. Extra Attributes (KB has, lecturer doesn't)

- drainage_requirement (kebutuhan_drainase)
- growing_duration_days (durasi_tanam_hari)
- optimal_risk_level (risiko_optimal)
- economic_priority (prioritas ekonomi)
- scientific_reference
- version / last_updated
- commodity_category (tipe_komoditas)
- nama_ilmiah (scientific name)

---

## Summary

| Metric | Count |
|--------|-------|
| Current commodities | 17 |
| Lecturer commodities | 22 |
| Commodities to KEEP | 7 (sawi, tomat, terong, mentimun, kacang_panjang, talas, seledri) |
| Commodities to RENAME | 2 (kangkung→kangkung_air, selada→selada_air) |
| Commodities to MERGE | 2→1 (cabai_rawit+cabai_merah→cabai) |
| Commodities to REMOVE | 6 (bayam, pare, melon, semangka, jagung_manis, kemangi) |
| Commodities to ADD | 12 (bawang_merah, kentang, paprika, kubis, pakcoy, wortel, lobak, labu_siam, buncis, genjer, pakis_sayur, semanggi) |
| Final total | 22 |

---

## Validation Status

**AUDIT COMPLETE** — All findings documented. Proceed to Phase 2 (Commodity Synchronization).
