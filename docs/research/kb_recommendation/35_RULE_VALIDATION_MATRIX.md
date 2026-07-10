# Rule Validation Matrix

## Sprint KB6

### Decision Table: Vulnerability Level × Risk Category

| Vulnerability | Rendah | Sedang | Tinggi |
|---------------|--------|--------|--------|
| **Sangat Tinggi** | RECOMMENDED | RECOMMENDED | RECOMMENDED |
| **Tinggi** | RECOMMENDED | RECOMMENDED | ALTERNATIVE |
| **Sedang** | RECOMMENDED | ALTERNATIVE | NOT_RECOMMENDED |
| **Rendah** | ALTERNATIVE | NOT_RECOMMENDED | NOT_RECOMMENDED |
| **Sangat Rendah** | NOT_RECOMMENDED | NOT_RECOMMENDED | NOT_RECOMMENDED |

### Detailed Rule Validation (15/15 Rules)

| # | Vulnerability | Risk | Expected Status | Actual Status | Result |
|---|---------------|------|-----------------|---------------|--------|
| 1 | Sangat Tinggi | Rendah | recommended | recommended | PASS |
| 2 | Sangat Tinggi | Sedang | recommended | recommended | PASS |
| 3 | Sangat Tinggi | Tinggi | recommended | recommended | PASS |
| 4 | Tinggi | Rendah | recommended | recommended | PASS |
| 5 | Tinggi | Sedang | recommended | recommended | PASS |
| 6 | Tinggi | Tinggi | alternative | alternative | PASS |
| 7 | Sedang | Rendah | recommended | recommended | PASS |
| 8 | Sedang | Sedang | alternative | alternative | PASS |
| 9 | Sedang | Tinggi | not_recommended | not_recommended | PASS |
| 10 | Rendah | Rendah | alternative | alternative | PASS |
| 11 | Rendah | Sedang | not_recommended | not_recommended | PASS |
| 12 | Rendah | Tinggi | not_recommended | not_recommended | PASS |
| 13 | Sangat Rendah | Rendah | not_recommended | not_recommended | PASS |
| 14 | Sangat Rendah | Sedang | not_recommended | not_recommended | PASS |
| 15 | Sangat Rendah | Tinggi | not_recommended | not_recommended | PASS |

### Rule Coverage: 100.0%

### Key Observations

1. **Sangat Tinggi** vulnerability (Kangkung, Talas) — Always recommended regardless of risk level
2. **Sangat Rendah** vulnerability (Melon, Semangka) — Never recommended at any risk level
3. **Tinggi** vulnerability — Recommended at Rendah/Sedang, Alternative at Tinggi
4. **Sedang** vulnerability — Recommended at Rendah, Alternative at Sedang, Not recommended at Tinggi
5. **Rendah** vulnerability — Alternative at Rendah, Not recommended at Sedang/Tinggi

### Validation Method

Rules validated programmatically using `InferenceRuleEngine` from `backend/decision/rules.py`. All 15 combinations exhaustively tested against the hardcoded `DECISION_TABLE`.
