# Knowledge Base Data Dictionary

## 1. File Location

`backend/knowledge/data/commodity_knowledge.json`

## 2. Top-Level Structure

```json
[
  { /* CommodityKnowledge record */ },
  { /* CommodityKnowledge record */ },
  ...
]
```

The file is a JSON array of commodity records. Each record is validated against the `CommodityKnowledge` schema.

## 3. Field Reference

### `commodity_id` (string, required)
Unique slug identifier. Lowercase, hyphens allowed. Examples: `kangkung`, `jagung_manis`, `kacang_tanah`.

### `commodity_name` (string, required)
Common Indonesian name. Examples: `Kangkung`, `Jagung Manis`, `Kacang Tanah`.

### `commodity_category` (enum, required)
Agronomic classification:

| Value | Count |
|-------|-------|
| `sayuran_daun` | 5 (kangkung, bayam, sawi, selada, seledri) |
| `sayuran_buah` | 5 (cabai, tomat, terong, mentimun, pare) |
| `sayuran_serealia` | 1 (jagung manis) |
| `kacang_kacangan` | 1 (kacang tanah) |
| `umbi` | 2 (singkong, kentang) |
| `buah` | 1 (melon) |
| `tanaman_industri` | 1 (tebu) |
| `bumbu_dapur` | 1 (jahe) |

### `vulnerability_level` (enum, required)
Flood vulnerability classification (from very low to very high):

| Value | Meaning |
|-------|---------|
| `Sangat Rendah` | Severe damage or death under any inundation |
| `Rendah` | Poor flood tolerance, significant yield loss |
| `Sedang` | Moderate tolerance, some yield loss |
| `Tinggi` | Good tolerance, minimal yield loss |
| `Sangat Tinggi` | Thrives in flooded conditions |

### `flood_tolerance_category` (enum, required)
Ability to survive inundation:

| Value | Meaning |
|-------|---------|
| `Sangat Rendah` | Cannot survive inundation |
| `Rendah` | Survives <1 hour |
| `Sedang` | Survives <1 day |
| `Tinggi` | Survives 1-3 days |
| `Sangat Tinggi` | Survives >7 days |

### `maximum_inundation_duration` (string, required)
Human-readable maximum inundation duration. Examples: `>7 hari`, `2-3 hari`, `<6 jam`.

### `drainage_requirement` (enum, required)
Minimum drainage needed for healthy growth:

| Value | Meaning |
|-------|---------|
| `Minimal` | Thrives in standing water |
| `Rendah` | Tolerates poor drainage |
| `Sedang` | Needs moderate drainage |
| `Tinggi` | Needs good drainage |
| `Sangat Tinggi` | Requires excellent drainage |

### `growing_duration_days` (integer, required, 1–365)
Days from planting to harvest. Examples: `25` (kangkung), `365` (tebu).

### `optimal_risk_level` (enum, required)
Risk level at which the commodity performs best:

| Value | Meaning |
|-------|---------|
| `Sangat Rendah` | Only suitable in flood-free zones |
| `Rendah` | Best in low-risk areas |
| `Sedang` | Moderate risk tolerance |
| `Tinggi` | Performs well in high-risk areas |
| `Sangat Tinggi` | Ideal for flood-prone areas |

### `economic_priority` (enum, required)
Economic and cultural importance ranking:

| Value | Meaning |
|-------|---------|
| `Sangat Tinggi` | Staple / high economic impact |
| `Tinggi` | Major cash crop |
| `Sedang` | Moderate importance |
| `Rendah` | Niche / low economic impact |
| `Sangat Rendah` | Minimal economic role |

### `major_impacts` (array of strings, required, non-empty)
Physiological effects of flooding on the commodity.

### `damage_symptoms` (array of strings, required, non-empty)
Observable damage signs under flood stress.

### `recommendation_notes` (string, required)
Planting guidance for flood conditions. Human-readable advice.

### `scientific_reference` (string, required)
Citation or assumption marker. Format: `[Source type] — Title`. For assumed data: `[Assumption] — reason`.

### `version` (string, required)
Record version for change tracking. Format: `major.minor` (e.g., `1.0`).

### `last_updated` (string, required)
Last update date in ISO 8601 format (`YYYY-MM-DD`).

## 4. Commodity Inventory (17 entries)

| ID | Name | Category | Vulnerability |
|----|------|----------|---------------|
| kangkung | Kangkung | sayuran_daun | Sangat Tinggi |
| bayam | Bayam | sayuran_daun | Tinggi |
| sawi | Sawi | sayuran_daun | Tinggi |
| selada | Selada | sayuran_daun | Sedang |
| seledri | Seledri | sayuran_daun | Sedang |
| cabai | Cabai | sayuran_buah | Sangat Rendah |
| tomat | Tomat | sayuran_buah | Sangat Rendah |
| terong | Terong | sayuran_buah | Rendah |
| mentimun | Mentimun | sayuran_buah | Rendah |
| pare | Pare | sayuran_buah | Sedang |
| jagung_manis | Jagung Manis | sayuran_serealia | Rendah |
| kacang_tanah | Kacang Tanah | kacang_kacangan | Rendah |
| singkong | Singkong | umbi | Rendah |
| kentang | Kentang | umbi | Sangat Rendah |
| melon | Melon | buah | Sangat Rendah |
| tebu | Tebu | tanaman_industri | Rendah |
| jahe | Jahe | bumbu_dapur | Sedang |

## 5. Adding a New Commodity

1. Append a new JSON object to the `commodity_knowledge.json` array.
2. Ensure all required fields are present and valid enum values are used.
3. Assign a unique `commodity_id`.
4. Run the validation test suite:
   ```bash
   python -m pytest tests/backend/knowledge/ -v
   ```
5. Update the count assertion in `test_integration.py` if needed.

## 6. Schema Versioning

Current schema version: `1.0`. Bump the version when:
- A new required field is added.
- An enum value is added, removed, or renamed.
- The data format changes.
