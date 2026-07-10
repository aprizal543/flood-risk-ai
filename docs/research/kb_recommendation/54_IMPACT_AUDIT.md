# Sprint KB8.6 — Impact & Damage Symptoms Audit

**Audit Date:** 2026-07-10
**Scope:** Comprehensive audit of `dampak_utama`, `gejala_kerusakan`, `major_impacts`, `damage_symptoms` fields across both datasets.

---

## Dataset 1: `commodity_knowledge.json` (KB-DSS)

| # | commodity_id | dampak_utama | major_impacts | Match? | gejala_kerusakan | damage_symptoms | Match? |
|---|---|---|---|---|---|---|---|
| 1 | cabai | 4 | 4 | YES | 4 | 4 | YES |
| 2 | tomat | 4 | 4 | YES | 4 | 4 | YES |
| 3 | bawang_merah | 4 | 4 | YES | 4 | 4 | YES |
| 4 | kentang | 4 | 4 | YES | 4 | 4 | YES |
| 5 | paprika | 4 | 4 | YES | 4 | 4 | YES |
| 6 | kubis | 5 | 5 | YES | 5 | 5 | YES |
| 7 | pakcoy | 5 | 5 | YES | 5 | 5 | YES |
| 8 | sawi | 5 | 5 | YES | 5 | 5 | YES |
| 9 | terong | 5 | 5 | YES | 5 | 5 | YES |
| 10 | mentimun | 5 | 5 | YES | 5 | 5 | YES |
| 11 | kacang_panjang | 5 | 5 | YES | 5 | 5 | YES |
| 12 | wortel | 5 | **3** | **NO** — 2 items missing | 4 | **3** | **NO** — 1 item missing |
| 13 | lobak | 5 | **3** | **NO** — 2 items missing | 4 | **3** | **NO** — 1 item missing |
| 14 | labu_siam | 5 | **3** | **NO** — 2 items missing | 4 | **3** | **NO** — 1 item missing |
| 15 | buncis | 5 | **3** | **NO** — 2 items missing | 4 | **3** | **NO** — 1 item missing |
| 16 | kangkung_air | 4 | **2** | **NO** — 2 items missing | 2 | 2 | YES |
| 17 | genjer | 4 | **2** | **NO** — 2 items missing | 2 | 2 | YES |
| 18 | selada_air | 3 | **2** | **NO** — 1 item missing + truncation | 2 | 2 | YES |
| 19 | talas | 3 | 3 | **NO** — completely different content | 2 | 2 | **NO** — completely different |
| 20 | seledri | 2 | 2 | YES | 2 | 2 | YES |
| 21 | pakis_sayur | 2 | 2 | **NO** — truncated wording | 2 | 2 | YES |
| 22 | semanggi | 3 | 3 | **NO** — slightly reworded | 2 | 2 | YES |

**Summary:**
- `dampak_utama` == `major_impacts`: **11 YES / 11 NO**
- `gejala_kerusakan` == `damage_symptoms`: **18 YES / 4 NO**
- `main_impacts` field: **0/22** (doesn't exist yet)
- Primary cause of mismatches: truncated arrays, lost items, completely different content

---

## Dataset 2: `commodity_profiles.json` (ML Legacy)

| Field | Present? |
|-------|----------|
| `catatan` | 22/22 (100%) |
| `main_impacts` | 0/22 |
| `damage_symptoms` | 0/22 |
| `dampak_utama` | 0/22 |
| `gejala_kerusakan` | 0/22 |

**Summary:** ML profiles have no structured impact/symptom data — only free-text `catatan`.

---

## Key Findings

1. **11 commodities** have `major_impacts` truncated vs `dampak_utama` (lost 1-2 items each)
2. **4 commodities** have `damage_symptoms` truncated vs `gejala_kerusakan`
3. **Talas** has completely different impact/symptom content between Indonesian/English fields
4. **ML profiles** lack any structured impact/symptom fields
5. **`main_impacts` field does not exist** in either dataset — must be added
6. `catatan`/`recommendation_notes` exists but is free-text, not structured
