# Explainability Engine Specification

## 1. Purpose

The Explainability Engine generates human-readable Bahasa Indonesia explanations for every commodity recommendation. Explanations are derived entirely from Knowledge Base fields — never hardcoded in API endpoints.

## 2. Architecture

```
CommodityKnowledge
  ├── vulnerability_level        → _VULN_DESCRIPTIONS
  ├── flood_tolerance_category   → _FLOOD_TOL_DESCRIPTIONS
  ├── optimal_risk_level         → _RISK_MATCH_DESCRIPTIONS
  ├── maximum_inundation_duration
  ├── major_impacts
  ├── damage_symptoms
  ├── growing_duration_days
  └── scientific_reference
          │
          ▼
    ExplainabilityEngine.generate_reason()
          │
          ▼
    Human-readable explanation string (Bahasa Indonesia)
```

## 3. Explanation Templates

### Recommended
```
{Kangkung} direkomendasikan karena {sangat toleran terhadap genangan}
({dapat bertahan lebih dari 7 hari dalam genangan}) sehingga
{sangat sesuai untuk ditanam pada berbagai kondisi risiko banjir}
pada kondisi Risiko {Tinggi} saat ini.
```

### Alternative
```
{Bayam} dapat dipertimbangkan sebagai alternatif pada kondisi
Risiko {Tinggi} karena {cukup toleran terhadap genangan}
({dapat bertahan 2-3 hari dalam genangan}), namun perlu
pengelolaan drainase yang baik dan perlindungan tambahan.
```

### Not Recommended
```
{Melon} tidak direkomendasikan pada kondisi Risiko {Tinggi}
karena {sangat rentan terhadap genangan}
({tidak dapat bertahan dalam genangan}; genangan maksimal
{<6 jam}) sehingga {tidak sesuai dan sangat berisiko
mengalami kerusakan}.
```

## 4. Key Translations

| KB Field Value | Indonesian Description |
|---------------|------------------------|
| Sangat Tinggi | sangat toleran terhadap genangan |
| Tinggi | cukup toleran terhadap genangan |
| Sedang | memiliki toleransi sedang terhadap genangan |
| Rendah | kurang toleran terhadap genangan |
| Sangat Rendah | sangat rentan terhadap genangan |

## 5. Detailed Explanation

`generate_detailed_explanation()` returns a structured dict:

```json
{
  "ringkasan": "Kangkung direkomendasikan...",
  "faktor_utama": [
    "Tingkat toleransi banjir: Sangat Tinggi",
    "Durasi genangan maksimal: >7 hari",
    "Kebutuhan drainase: Minimal"
  ],
  "dampak_utama": ["Pertumbuhan subur di kondisi tergenang"],
  "gejala_kerusakan": ["Tidak ada gejala kerusakan berarti"],
  "durasi_tanam_hari": 25,
  "referensi": "FAO aquatic vegetable cultivation guides [Pending]"
}
```

## 6. Design Principles

- **KB-driven**: All text is generated from commodity attributes, not API code.
- **Deterministic**: Same KB + same status → same explanation.
- **No ML**: No language models, no templates with AI.
- **Complete coverage**: Every commodity has an explanation (validated by `DecisionValidator`).
