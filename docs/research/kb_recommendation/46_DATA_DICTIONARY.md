# 46 — Data Dictionary

## Objective

Document every field in the Knowledge Base, identifying its origin (lecturer document vs. backward compatibility) and usage.

---

## Lecturer-Derived Fields (Source of Truth)

These fields come directly from the lecturer recommendation document.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `commodity_id` | string | Unique URL-safe identifier | `kangkung_air` |
| `commodity_name` | string | Common Indonesian name from lecturer | `Kangkung Air` |
| `aliases` | list[string] | Alternative names (Alias column) | `["Caisim"]` |
| `kelompok_kerentanan` | list[string] | Vulnerability groups from lecturer | `["Tinggi", "Rendah"]` |
| `tingkat_kerentanan` | string | Vulnerability level name (exact copy) | `Sangat Rentan (Highly Sensitive)` |
| `batas_toleransi_genangan` | string | Maximum inundation tolerance (exact copy) | `Kurang dari 24 jam` |
| `dampak_utama` | list[string] | Main physiological impacts (exact copy) | `["Akar langsung membusuk akibat ketiadaan oksigen"]` |
| `gejala_kerusakan` | list[string] | Observable damage symptoms (derived) | `["Daun menguning (klorosis)"]` |

### Valid Values for `kelompok_kerentanan`

| Value | Meaning |
|-------|---------|
| `Tinggi` | Highly vulnerable to water |
| `Sedang` | Moderately vulnerable to water |
| `Rendah` | Low vulnerability to water |

---

## Deprecated Fields (Backward Compatibility)

These fields are kept for backward compatibility with the existing API, frontend, decision engine, and legacy ML system.

| Field | Type | Deprecation Reason | Replacement |
|-------|------|--------------------|-------------|
| `commodity_category` | string | Not from lecturer doc. Used by Decision Engine and health endpoint. | N/A (kept) |
| `vulnerability_level` | string | Lecturer uses different classification. Used by Decision Engine rules. | Derived from `tingkat_kerentanan` |
| `flood_tolerance_category` | string | Not from lecturer doc. Used by Explainability Engine. | N/A (kept) |
| `maximum_inundation_duration` | string | Duplicates `batas_toleransi_genangan`. Used by API/frontend. | `batas_toleransi_genangan` |
| `drainage_requirement` | string | Not from lecturer doc. Used by legacy scorer and Explainability Engine. | N/A (kept) |
| `growing_duration_days` | integer | Not from lecturer doc. Used by legacy scorer and Explainability Engine. | N/A (kept) |
| `optimal_risk_level` | string | Not from lecturer doc. Used by legacy scorer. | N/A (kept) |
| `economic_priority` | string | Not from lecturer doc. Used by legacy scorer. | N/A (kept) |
| `major_impacts` | list[string] | Duplicates `dampak_utama`. Used by API/frontend. | `dampak_utama` |
| `damage_symptoms` | list[string] | Duplicates `gejala_kerusakan`. Used by API/frontend. | `gejala_kerusakan` |
| `recommendation_notes` | string | Not from lecturer doc. Used by validation/reporting. | N/A (kept) |
| `scientific_reference` | string | Not from lecturer doc. Used by API as `source` field. | Lecturer document attribution |
| `version` | string | Schema version tracking. | `2.0` |
| `last_updated` | string | Date tracking. | ISO date string |

### Valid Values for `commodity_category`

| Value | Description |
|-------|-------------|
| `sayuran_daun` | Leaf vegetable |
| `sayuran_buah` | Fruit vegetable |
| `sayuran_umbi` | Tuber/root vegetable |
| `kacang-kacangan` | Legume |
| `umbi` | Tuber (legacy) |
| `sayuran_serealia` | Cereal vegetable |
| `buah` | Fruit |
| `herba` | Herb |

### Valid Values for `vulnerability_level`

| Value | Ordinal | Meaning |
|-------|---------|---------|
| `Sangat Tinggi` | 5 | Very high flood tolerance |
| `Tinggi` | 4 | High flood tolerance |
| `Sedang` | 3 | Moderate flood tolerance |
| `Rendah` | 2 | Low flood tolerance |
| `Sangat Rendah` | 1 | Very low flood tolerance |

---

## Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `CommodityCategory` | sayuran_daun, sayuran_buah, sayuran_serealia, kacang-kacangan, umbi, buah, herba, sayuran_umbi | Agronomic categorization (DEPRECATED) |
| `FloodToleranceLevel` | Sangat Tinggi, Tinggi, Sedang, Rendah, Sangat Rendah | Flood tolerance ordinal |
| `DrainageRequirement` | Minimal, Rendah, Sedang, Tinggi, Sangat Tinggi | Drainage needs (DEPRECATED) |
| `RiskLevel` | Rendah, Sedang, Tinggi | FRI-based risk categories |
| `EconomicPriority` | Sangat Tinggi, Tinggi, Sedang, Rendah | Economic importance (DEPRECATED) |

---

## Decision Engine Fields (CommodityRecommendation)

| Field | Source | API Exposure |
|-------|--------|--------------|
| `commodity_id` | CommodityKnowledge | `komoditas_id` |
| `commodity_name` | CommodityKnowledge | `komoditas` |
| `recommendation_status` | Decision Rules | Group (recommended/alternative/not_recommended) |
| `vulnerability_level` | CommodityKnowledge (deprecated) | `vulnerability` |
| `maximum_inundation_duration` | CommodityKnowledge (deprecated) | `max_inundation` |
| `major_impacts` | CommodityKnowledge (deprecated) | `impacts` |
| `damage_symptoms` | CommodityKnowledge (deprecated) | `symptoms` |
| `recommendation_reason` | Explainability Engine | `reason` |
| `knowledge_reference` | CommodityKnowledge (deprecated) | `source` |

---

## Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-08 | Initial KB-DSS schema |
| 2.0 | 2026-07-10 | Lecturer doc synchronization: added lecturer-derived fields, deprecated non-lecturer fields |
