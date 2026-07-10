# API Migration Guide

## 1. Current API (Legacy)

```json
{
  "model": "rf",
  "fri": 45.0,
  "tingkat_risiko": "Risiko Sedang",
  "rekomendasi": [
    {
      "komoditas": "Kangkung",
      "komoditas_id": "kangkung",
      "skor": 85.5,
      "tingkat_keyakinan": 95.0,
      "tingkat_risiko": "Risiko Sedang",
      "alasan": ["..."],
      "ringkasan": "..."
    }
  ],
  "mitigasi": [
    {
      "prioritas": 1,
      "kategori": "Drainase",
      "tindakan": "..."
    }
  ]
}
```

## 2. New API (Knowledge Mode, additive)

All legacy fields remain. Two additive fields appear when feature flag is ON:

```json
{
  "model": "rf",
  "fri": 45.0,
  "tingkat_risiko": "Risiko Sedang",
  "rekomendasi": [
    {
      "komoditas": "Kangkung",
      "komoditas_id": "kangkung",
      "skor": 100.0,
      "tingkat_keyakinan": 100.0,
      "tingkat_risiko": "Risiko Sedang",
      "alasan": ["Kangkung direkomendasikan..."],
      "ringkasan": "Kangkung direkomendasikan..."
    }
  ],
  "mitigasi": [
    {...}
  ],
  "knowledge_recommendation": {
    "recommended": [
      {
        "commodity_id": "kangkung",
        "commodity_name": "Kangkung",
        "vulnerability_level": "Sangat Tinggi",
        "maximum_inundation_duration": ">7 hari",
        "recommendation_reason": "Kangkung direkomendasikan...",
        "knowledge_reference": "FAO aquatic vegetable cultivation guides [Pending]"
      }
    ],
    "alternative": [...],
    "not_recommended": [...]
  },
  "knowledge_source": {
    "version": "1.0",
    "engine": "KB-DSS",
    "execution_duration_ms": 2.34
  }
}
```

## 3. Backward Compatibility

| Scenario | Legacy Fields | KB Fields | Works? |
|----------|---------------|-----------|--------|
| Old client, flag OFF | Present | Absent | ✅ |
| Old client, flag ON | Present | Present (ignored) | ✅ |
| New client, flag OFF | Present | Absent | ✅ |
| New client, flag ON | Present | Present | ✅ |

## 4. Migration Steps

### Sprint KB4 (current)
- Both systems coexist
- Feature flag defaults to `false`
- Additive fields available but not active

### Sprint KB5
- Set `USE_KNOWLEDGE_RECOMMENDATION=true` in production
- Monitor for issues
- Legacy system remains as fallback

### Sprint KB6+
- Frontend can optionally consume `knowledge_recommendation` and `knowledge_source`
- Legacy `ml/recommendation/` can be archived

## 5. No Breaking Changes

The following are guaranteed:
- All existing response fields are preserved
- No field renamed or removed
- Response schema validates without KB fields
- Frontend renders correctly regardless of flag state
