# Sprint KB8.6 — API Mapping Changes

**Date:** 2026-07-10

---

## Changes to `recommendation_mapper.py`

### Before (Sprint KB8.5)

```python
def item(c) -> dict:
    return {
        "komoditas": c.commodity_name,
        "komoditas_id": c.commodity_id,
        "vulnerability": c.vulnerability_level,
        "max_inundation": c.maximum_inundation_duration,
        "impacts": list(c.major_impacts),       # deprecated field
        "symptoms": list(c.damage_symptoms),     # was deprecated
        "reason": c.recommendation_reason,
        "source": c.knowledge_reference,
    }
```

### After (Sprint KB8.6)

```python
def item(c) -> dict:
    return {
        "komoditas": c.commodity_name,
        "komoditas_id": c.commodity_id,
        "vulnerability": c.vulnerability_level,
        "max_inundation": c.maximum_inundation_duration,
        "maximum_inundation_duration": c.maximum_inundation_duration,  # NEW
        "main_impacts": list(c.main_impacts),                          # NEW authoritative
        "damage_symptoms": list(c.damage_symptoms),                    # NEW authoritative
        "impacts": list(c.major_impacts),      # kept for backward compat
        "symptoms": list(c.damage_symptoms),   # kept for backward compat
        "reason": c.recommendation_reason,
        "source": c.knowledge_reference,
    }
```

## Additive Only

Existing fields are NOT removed. Only new fields are added:

| Field | Source | Status |
|-------|--------|--------|
| `max_inundation` | `maximum_inundation_duration` | Kept |
| `maximum_inundation_duration` | `maximum_inundation_duration` | **New** |
| `impacts` | `major_impacts` (deprecated) | Kept |
| `main_impacts` | `main_impacts` (authoritative) | **New** |
| `symptoms` | `damage_symptoms` | Kept |
| `damage_symptoms` | `damage_symptoms` (authoritative) | **New** |

## Example API Response Fragment

```json
{
  "recommended": [
    {
      "komoditas": "Kangkung Air",
      "komoditas_id": "kangkung_air",
      "vulnerability": "Sangat Tinggi",
      "max_inundation": "Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
      "maximum_inundation_duration": "Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
      "main_impacts": [
        "Tanaman tetap tumbuh optimal karena memiliki struktur anatomi khusus seperti jaringan aerenkim (rongga udara) yang mampu menyalurkan oksigen dari daun langsung ke akar",
        "Kelompok ini justru membutuhkan kondisi tanah yang jenuh air atau tergenang permanen untuk mencapai pertumbuhan maksimal",
        "Genangan air tinggi tidak dianggap sebagai cekaman, melainkan lingkungan tumbuh ideal",
        "Akar sangat efektif mengambil oksigen yang terlarut di dalam air"
      ],
      "damage_symptoms": [
        "Tidak menunjukkan gejala kerusakan berarti pada genangan",
        "Tumbuh optimal di lahan tergenang permanen"
      ],
      "impacts": ["..."],
      "symptoms": ["..."],
      "reason": "Kangkung Air direkomendasikan ...",
      "source": "Lecturer recommendation document ..."
    }
  ]
}
```
