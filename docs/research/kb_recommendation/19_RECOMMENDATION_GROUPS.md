# Recommendation Groups

## 1. Overview

Every commodity belongs to exactly one of three recommendation groups. Groups are mutually exclusive — no commodity appears in more than one group.

## 2. Group Definitions

### ✅ Recommended (`recommended`)

Commodities that are suitable for planting at the current risk level with minimal additional management.

**Label**: `Direkomendasikan`

**Criteria**: Vulnerability level significantly exceeds the current risk level.

**Example** (Risiko Tinggi): Kangkung, Talas

### ⚠️ Alternative (`alternative`)

Commodities that can be planted with additional management measures (improved drainage, raised beds, protective structures).

**Label**: `Alternatif`

**Criteria**: Vulnerability level is close to or slightly below the current risk level.

**Example** (Risiko Tinggi): Bayam, Sawi (Tinggi vulnerability at Tinggi risk)

### ❌ Not Recommended (`not_recommended`)

Commodities that are unsuitable at the current risk level. Planting would likely result in significant crop damage or loss.

**Label**: `Tidak Direkomendasikan`

**Criteria**: Vulnerability level is below the current risk level.

**Example** (Risiko Tinggi): Melon, Semangka, Tomat, Jagung Manis

## 3. Sorting Within Groups

Commodities within each group are sorted by vulnerability level descending (highest flood tolerance first):

1. Sangat Tinggi
2. Tinggi
3. Sedang
4. Rendah
5. Sangat Rendah

## 4. Integrity Rules

| Rule | Enforcement |
|------|-------------|
| No commodity appears twice | `DecisionValidator` checks for duplicate IDs |
| All 17 commodities classified | Count must equal 17 |
| No empty groups | Each group must have ≥ 1 commodity |
| One group per commodity | Exclusive assignment enforced by logic |

## 5. Example Output (FRI=45 — Risiko Sedang)

**Recommended** (7 commodities):
Kangkung (Sangat Tinggi), Talas (Sangat Tinggi), Bayam (Tinggi), Sawi (Tinggi), Selada (Sedang), Cabai Rawit (Sedang), Cabai Merah (Sedang)

**Alternative** (4 commodities):
Terong (Sedang), Mentimun (Sedang), Kacang Panjang (Sedang), Pare (Sedang)

**Not Recommended** (6 commodities):
Tomat (Rendah), Jagung Manis (Rendah), Seledri (Sedang), Kemangi (Sedang), Melon (Sangat Rendah), Semangka (Sangat Rendah)

## 6. API Response Integration

The recommendation groups are returned as structured data through `KnowledgeRecommendationService.recommend_as_dict()`:

```json
{
  "status": "berhasil",
  "fri": 45.0,
  "tingkat_risiko": "Risiko Sedang",
  "recommended": [
    {
      "commodity_id": "kangkung",
      "commodity_name": "Kangkung",
      "vulnerability_level": "Sangat Tinggi",
      "recommendation_reason": "..."
    }
  ],
  "alternative": [...],
  "not_recommended": [...],
  "metadata": {
    "execution_duration_ms": 2.34,
    "total_commodities": 17
  }
}
```
