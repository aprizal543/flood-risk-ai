# Rule Implementation

## 1. Decision Table

All inference rules are defined in `InferenceRuleEngine.DECISION_TABLE` as a 5×3 matrix mapping `(vulnerability_level, risk_category)` → `RecommendationStatus`.

### Table

| Vulnerability Level | Rendah (FRI 0–33) | Sedang (FRI 34–66) | Tinggi (FRI 67–100) |
|---------------------|:-----------------:|:------------------:|:-------------------:|
| **Sangat Tinggi**   | ✅ Recommended    | ✅ Recommended     | ✅ Recommended      |
| **Tinggi**          | ✅ Recommended    | ✅ Recommended     | ⚠️ Alternative     |
| **Sedang**          | ✅ Recommended    | ⚠️ Alternative    | ❌ Not Recommended  |
| **Rendah**          | ⚠️ Alternative   | ❌ Not Recommended | ❌ Not Recommended  |
| **Sangat Rendah**   | ❌ Not Recommended| ❌ Not Recommended | ❌ Not Recommended  |

### Rule Count: 15 (5 vulnerability levels × 3 risk categories)

## 2. Rule Evaluation

```python
def evaluate(vulnerability_level: str, risk_category: str) -> RecommendationStatus:
    row = DECISION_TABLE[vulnerability_level]
    return row[risk_category]
```

Each commodity is evaluated independently. The result is deterministic — same input always produces the same output.

## 3. Key Principles

- **No heuristic scoring**: Rules produce a status, not a score.
- **No weights**: All rules have equal priority (sorted by vulnerability after evaluation).
- **No AI/ML**: Rules are hand-defined based on domain knowledge.
- **100% coverage**: Every vulnerability × risk combination has a defined outcome.
- **Deterministic**: Same FRI always produces the same grouping.

## 4. Group Assignment

After evaluation, commodities are assigned to exactly one of three groups:

| Group | Status | Criteria |
|-------|--------|----------|
| **Recommended** | `recommended` | Vulnerability ≥ 2 levels above risk |
| **Alternative** | `alternative` | Vulnerability ≈ 1 level above / at risk |
| **Not Recommended** | `not_recommended` | Vulnerability below risk level |

Commodities within each group are sorted by vulnerability level descending (highest tolerance first).

## 5. Rule Templates

Each status has a Bahasa Indonesia explanation template:

- **Recommended**: `"{name} direkomendasikan untuk ditanam pada kondisi Risiko {risk} karena memiliki toleransi banjir {vuln} yang sangat sesuai."`
- **Alternative**: `"{name} dapat dipertimbangkan sebagai alternatif pada kondisi Risiko {risk} meskipun toleransi banjirnya {vuln} — perlu pengelolaan drainase yang baik."`
- **Not Recommended**: `"{name} tidak direkomendasikan pada kondisi Risiko {risk} karena toleransi banjirnya {vuln} dan tidak sesuai dengan tingkat risiko saat ini."`

## 6. Validation

On initialization, `InferenceRuleEngine._validate_table()` checks:
- All 5 vulnerability levels have rows
- All 3 risk categories have columns per row
- All 15 cells contain valid `RecommendationStatus` values

If validation fails, the application startup fails (fail-fast).
