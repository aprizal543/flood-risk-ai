# Knowledge Base Specification

## 1. Purpose

The Knowledge Base is the central repository of structured agricultural domain knowledge that drives all commodity recommendations in the KB-DSS. It replaces the heuristic scoring approach with a queryable, scientifically grounded knowledge store.

## 2. Design Principles

| Principle | Rationale |
|-----------|-----------|
| **Single source of truth** | All commodity attributes, thresholds, and relationships reside in one place. No duplication across modules. |
| **Explicit semantics** | Every field has a defined interpretation. No ordinal mappings hidden in code. |
| **Extensibility** | New commodities, attributes, or rules can be added without modifying system logic. |
| **Traceability** | Every entry links to a scientific reference or documented research assumption. |
| **Version-controlled** | Schema and content versioned alongside code. All changes reviewed. |

## 3. Schema Specification

### 3.1 Commodity Definition Record

Each commodity in the knowledge base is represented by the following schema:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `commodity_id` | string (slug) | Yes | Unique identifier | `kangkung` |
| `commodity_name` | string | Yes | Common Indonesian name | `Kangkung` |
| `scientific_name` | string | Yes | Latin binomial | `Ipomoea aquatica` |
| `commodity_category` | enum | Yes | Agronomic category | `sayuran_daun` |
| `vulnerability_level` | enum | Yes | Flood vulnerability classification | `Sangat Tinggi` |
| `flood_tolerance` | enum | Yes | Ability to survive inundation | `Sangat Tinggi` |
| `maximum_inundation_duration` | string | Yes | Maximum survivable flood duration | `>7 hari` |
| `drainage_requirement` | enum | Yes | Minimum drainage needed | `Minimal` |
| `growing_duration_days` | integer | Yes | Days from planting to harvest | `25` |
| `optimal_risk_level` | enum | Yes | Risk level at which commodity performs best | `Tinggi` |
| `economic_priority` | enum | Yes | Economic/cultural importance ranking | `Sangat Tinggi` |
| `major_impacts` | array[string] | Yes | Physiological effects of flooding | `["Pertumbuhan subur di genangan"]` |
| `damage_symptoms` | array[string] | Yes | Observable damage signs under flood stress | `["Tidak ada gejala kerusakan berarti"]` |
| `recommendation_notes` | string | Yes | Planting guidance for flood conditions | `Semi-aquatic; tumbuh subur di kondisi tergenang.` |
| `scientific_reference` | string | Yes | Citation or assumption marker | `[FAO aquatic vegetable cultivation guides]` |
| `is_assumption` | boolean | Yes | True if scientific reference is pending | `true` |

### 3.2 Enum Definitions

#### `commodity_category`

| Value | Description |
|-------|-------------|
| `sayuran_daun` | Leaf vegetables (kangkung, bayam, sawi, selada, seledri) |
| `sayuran_buah` | Fruit vegetables (cabai, tomat, terong, mentimun, pare) |
| `sayuran_serealia` | Cereal vegetables (jagung manis) |
| `kacang-kacangan` | Legumes (kacang panjang) |
| `umbi` | Tubers (talas) |
| `buah` | Fruits (melon, semangka) |
| `herba` | Herbs (kemangi) |

#### `vulnerability_level` / `flood_tolerance`

| Value | Ordinal | Interpretation |
|-------|---------|----------------|
| `Sangat Tinggi` | 5 | Thrives in flooded conditions |
| `Tinggi` | 4 | Survives brief to moderate inundation |
| `Sedang` | 3 | Tolerates short-duration waterlogging |
| `Rendah` | 2 | Damaged by even short inundation |
| `Sangat Rendah` | 1 | Crop failure under any inundation |

#### `drainage_requirement`

| Value | Ordinal | Meaning |
|-------|---------|---------|
| `Minimal` | 1 | Thrives in saturated soil |
| `Rendah` | 2 | Prefers moist soil, tolerates some wetness |
| `Sedang` | 3 | Requires balanced moisture |
| `Tinggi` | 4 | Needs well-drained soil |
| `Sangat Tinggi` | 5 | Intolerant of any waterlogging |

### 3.3 Risk Level Enum

| Value | FRI Range | Description |
|-------|-----------|-------------|
| `Rendah` | 0–33 | Normal conditions; full crop range available |
| `Sedang` | 34–66 | Elevated risk; select tolerant commodities |
| `Tinggi` | 67–100 | Significant flood risk; only flood-adapted species |

## 4. Complete Knowledge Base Records

The knowledge base shall contain exactly 17 records derived from `commodity_profiles.json` in the repository. Below is the enumerated content with scientific justification.

### 4.1 Very High Flood Tolerance

| Field | Kangkung | Talas |
|-------|----------|-------|
| commodity_id | `kangkung` | `talas` |
| commodity_name | Kangkung | Talas |
| scientific_name | *Ipomoea aquatica* | *Colocasia esculenta* |
| commodity_category | sayuran_daun | umbi |
| vulnerability_level | Sangat Tinggi | Sangat Tinggi |
| flood_tolerance | Sangat Tinggi | Sangat Tinggi |
| maximum_inundation_duration | >7 hari | >7 hari |
| drainage_requirement | Minimal | Minimal |
| growing_duration_days | 25 | 180 |
| optimal_risk_level | Tinggi | Tinggi |
| economic_priority | Sangat Tinggi | Sangat Tinggi |
| major_impacts | Pertumbuhan subur di genangan; adaptasi semi-aquatic | Adaptif terhadap tanah jenuh air; spesies lahan basah |
| damage_symptoms | Tidak ada gejala kerusakan berarti | Tidak ada gejala kerusakan berarti |
| recommendation_notes | Semi-aquatic; tumbuh subur di kondisi tergenang. Ideal untuk area rawan banjir. | Spesies lahan basah yang adaptif terhadap tanah jenuh air. Cocok untuk zona banjir. |
| scientific_reference | [Pending] — FAO aquatic vegetable cultivation guides | [Pending] — Taro cultivation in Pacific/SE Asian wetlands |
| is_assumption | true | true |

### 4.2 High Flood Tolerance

| Field | Bayam | Sawi Hijau |
|-------|-------|------------|
| commodity_id | `bayam` | `sawi` |
| commodity_name | Bayam | Sawi Hijau |
| scientific_name | *Amaranthus tricolor* | *Brassica juncea* |
| commodity_category | sayuran_daun | sayuran_daun |
| vulnerability_level | Tinggi | Tinggi |
| flood_tolerance | Tinggi | Tinggi |
| maximum_inundation_duration | 2–3 hari | 2–3 hari |
| drainage_requirement | Rendah | Rendah |
| growing_duration_days | 30 | 35 |
| optimal_risk_level | Sedang | Sedang |
| economic_priority | Sangat Tinggi | Tinggi |
| major_impacts | Toleransi genangan singkat; siklus cepat mengurangi paparan risiko | Toleran kondisi lembab; siklus pendek cocok untuk periode basah |
| damage_symptoms | Daun menguning jika genangan >3 hari; pertumbuhan terhambat | Layu sementara pada genangan ekstrem; pemulihan cepat setelah drainase |
| recommendation_notes | Toleran genangan singkat. Siklus panen cepat mengurangi paparan risiko. | Toleran kondisi lembab. Siklus pendek cocok untuk periode basah. |
| scientific_reference | [Pending] — Tropical leafy vegetable production manuals | [Pending] — Brassica cultivation in tropical lowlands |
| is_assumption | true | true |

### 4.3 Medium Flood Tolerance

| Field | Selada | Cabai Rawit | Cabai Merah | Tomat | Terong | Mentimun | Kacang Panjang | Pare | Seledri | Kemangi |
|-------|--------|-------------|-------------|-------|--------|----------|----------------|------|---------|---------|
| commodity_id | `selada` | `cabai_rawit` | `cabai_merah` | `tomat` | `terong` | `mentimun` | `kacang_panjang` | `pare` | `seledri` | `kemangi` |
| commodity_name | Selada | Cabai Rawit | Cabai Merah | Tomat | Terong | Mentimun | Kacang Panjang | Pare | Seledri | Kemangi |
| flood_tolerance | Sedang | Sedang | Sedang | Rendah | Sedang | Sedang | Sedang | Sedang | Sedang | Sedang |
| maximum_inundation_duration | 12–24 jam | 24 jam | <24 jam | <6 jam | 24 jam | 12–24 jam | 24 jam | 24 jam | 12–24 jam | 12–24 jam |
| drainage_requirement | Sedang | Tinggi | Tinggi | Tinggi | Sedang | Sedang | Sedang | Sedang | Sedang | Sedang |
| growing_duration_days | 40 | 90 | 100 | 80 | 70 | 45 | 55 | 50 | 60 | 35 |
| optimal_risk_level | Rendah | Rendah | Rendah | Rendah | Sedang | Rendah | Sedang | Sedang | Rendah | Rendah |
| economic_priority | Sedang | Tinggi | Tinggi | Sedang | Sedang | Sedang | Tinggi | Sedang | Sedang | Sedang |
| recommendation_notes | Memerlukan tanah berdrainase baik. Rentan busuk akar saat tergenang lama. | Nilai ekonomi tinggi. Perlu bedengan tinggi di area rawan banjir. | Penting secara ekonomi. Risiko penyakit akar meningkat saat genangan >24 jam. | Sangat sensitif terhadap genangan. Kekurangan oksigen akar dalam hitungan jam. | Toleransi banjir sedang. Dapat bertahan genangan singkat dengan pemulihan drainase. | Siklus pendek mengurangi paparan banjir. Perlu drainase tapi toleran kelembaban. | Tipe merambat menjaga polong di atas air. Toleransi sedang terhadap tanah basah. | Tanaman merambat; buah di atas permukaan tanah. | Suka tanah lembab tapi tidak tergenang. | Herba cepat tumbuh. Toleran kelembaban tapi perlu drainase. |
| scientific_reference | [Pending] | [Pending] — Capsicum disease management | [Pending] — Capsicum disease management | [Pending] — Tomato waterlogging physiology | [Pending] — Eggplant water stress | [Pending] — Cucurbit production | [Pending] — Legume waterlogging studies | [Pending] — Bitter gourd cultivation | [Pending] | [Pending] |
| is_assumption | true | true | true | true | true | true | true | true | true | true |

### 4.4 Low to Very Low Flood Tolerance

| Field | Tomat | Jagung Manis | Melon | Semangka |
|-------|-------|--------------|-------|----------|
| commodity_id | `tomat` | `jagung_manis` | `melon` | `semangka` |
| commodity_name | Tomat | Jagung Manis | Melon | Semangka |
| flood_tolerance | Rendah | Rendah | Sangat Rendah | Sangat Rendah |
| maximum_inundation_duration | <6 jam | <12 jam | <6 jam | <6 jam |
| drainage_requirement | Tinggi | Tinggi | Sangat Tinggi | Sangat Tinggi |
| optimal_risk_level | Rendah | Rendah | Rendah | Rendah |
| economic_priority | Sedang | Rendah | Rendah | Rendah |
| recommendation_notes | Sangat sensitif terhadap genangan. Kekurangan oksigen akar dalam hitungan jam. | Sistem akar sensitif kondisi anaerob. Hindari penanaman saat risiko tinggi. | Sangat sensitif genangan. Hanya cocok saat risiko rendah dengan drainase sempurna. | Buah menyentuh tanah sangat rentan busuk. Memerlukan kondisi kering. |
| scientific_reference | [Pending] — Tomato waterlogging physiology and disease | [Pending] — Maize flooding response literature | [Pending] — Melon production and water management | [Pending] — Watermelon cultivation best practices |
| is_assumption | true | true | true | true |

## 5. Reference Mapping Table

| commodity_id | scientific_reference_key | Status |
|-------------|------------------------|--------|
| kangkung | FAO aquatic vegetable cultivation guides | Assumption |
| talas | Taro cultivation in Pacific/SE Asian wetlands | Assumption |
| bayam | Tropical leafy vegetable production manuals | Assumption |
| sawi | Brassica cultivation in tropical lowlands | Assumption |
| selada | General agronomic principle | Assumption |
| cabai_rawit | Capsicum disease management; soil-borne pathogen studies | Assumption |
| cabai_merah | Capsicum disease management; soil-borne pathogen studies | Assumption |
| tomat | Tomato waterlogging physiology and disease | Assumption |
| terong | Eggplant water stress physiology | Assumption |
| mentimun | Cucurbit production in humid tropics | Assumption |
| kacang_panjang | Legume waterlogging tolerance studies | Assumption |
| pare | Bitter gourd cultivation practices | Assumption |
| melon | Melon production and water management | Assumption |
| semangka | Watermelon cultivation best practices | Assumption |
| jagung_manis | Maize flooding response literature | Assumption |
| talas | Taro cultivation in Pacific/SE Asian wetlands | Assumption |
| seledri | General agronomic principle | Assumption |
| kemangi | General agronomic principle | Assumption |

## 6. Research Assumptions

The following assumptions are made where scientific references are marked [Pending]:

1. **Flood tolerance levels** are derived from known botanical characteristics of each species as documented in tropical horticulture extension materials. These are considered reliable for decision-support purposes but have not been validated through local field trials in Pekanbaru.
2. **Maximum inundation durations** are estimates based on published waterlogging tolerance ranges for related species. Actual durations may vary with temperature, soil type, and growth stage.
3. **Economic priority rankings** reflect general market demand in Riau province and should be calibrated against local market data.
4. **Damage symptoms** are extrapolated from known pathophysiology of waterlogging stress (reduced root respiration, ethylene accumulation, nutrient uptake inhibition). Local observation studies are recommended for validation.

## 7. Knowledge Base Storage Design (Future — KB Sprint 2)

The knowledge base will be implemented as a structured data module (not JSON flat file) with the following characteristics:

- **Data class definitions** mirroring the schema above with type validation
- **Immutable record set** loaded at application startup from a versioned source
- **Query interface** providing:
  - `get_commodity(commodity_id) -> CommodityRecord`
  - `get_commodities_by_tolerance(level) -> list[CommodityRecord]`
  - `get_commodities_by_category(category) -> list[CommodityRecord]`
  - `get_commodities_by_risk_level(risk) -> list[CommodityRecord]`
  - `get_all_commodities() -> list[CommodityRecord]`
- **Validation layer** ensuring all records conform to schema before use
- **Caching layer** for runtime performance

## 8. Versioning Strategy

| Version | Date | Change |
|---------|------|--------|
| 1.0 | Sprint KB2 | Initial implementation from this specification |

Schema versioning follows semantic versioning: MAJOR for breaking schema changes, MINOR for additive changes, PATCH for corrections.
