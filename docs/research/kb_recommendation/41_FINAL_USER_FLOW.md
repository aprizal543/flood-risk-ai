# Final User Flow

## Knowledge-Based Decision Support System

### Flow 1: Manual Prediction

```
User enters weather data
        │
        ▼
POST /api/prediksi/manual
        │
        ├── Feature Engineering (build_features_v2)
        ├── Random Forest Prediction
        ├── Risk Classification (FRI → Rendah/Sedang/Tinggi)
        ├── Legacy Recommendation (always runs)
        ├── [if KB flag ON] Knowledge Recommendation
        │       ├── DecisionEngine.decide(FRI)
        │       ├── Rule Engine evaluates 15 rules
        │       ├── Groups: Recommended / Alternative / Not Recommended
        │       └── Response includes knowledge_recommendation + knowledge_source
        └── Response: FRI + Risk + Legacy rekomendasi + Mitigation + [KB data]
                │
                ▼
        Frontend Dashboard
        ├── Prediction Summary (FRI gauge, risk badge)
        ├── Recommendation Groups (3 sections)
        │       ├── Direkomendasikan (Recommended)
        │       ├── Alternatif (Alternative)
        │       └── Tidak Direkomendasikan (Not Recommended)
        └── Each commodity card shows:
                ├── Commodity name & vulnerability level
                ├── Inundation tolerance
                ├── Impacts & damage symptoms
                └── Recommendation reason
```

### Flow 2: Realtime Prediction

```
User selects city (e.g., Pekanbaru)
        │
        ▼
GET /api/prediksi/realtime?wilayah=Pekanbaru
        │
        ├── Open-Meteo fetches 14-day weather history
        ├── Feature Engineering with historical rolling features
        ├── (same as Flow 1 from here)
        └── Response includes city metadata + KB recommendation
```

### Flow 3: CSV Prediction

```
User uploads CSV file
        │
        ▼
POST /api/prediksi/csv
        │
        ├── Parse CSV → validate → sort by date
        ├── Latest row = prediction target
        ├── Preceding rows = history for rolling features
        ├── (same prediction pipeline)
        └── Response includes CSV metadata + KB recommendation
```

### Flow 4: User Interface States

```
┌─────────────────┐
│  Loading State   │  RecommendationSkeleton component
│  (Skeleton UI)   │  Animated pulse placeholders
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  Empty State     │  RecommendationEmptyState component
│  (No Data)       │  "Belum ada data prediksi" message
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  Success State   │  RecommendationSection renders 3 groups
│  (Data Loaded)   │  Each RecommendationGroup contains
│                  │  CommodityCard items with expandable details
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  Error State     │  HTTP error handling (401, 422, 500)
│  (API Error)     │  Indonesian error messages
└─────────────────┘
```

### Flow 5: Feature Flag Switching

```
USE_KNOWLEDGE_RECOMMENDATION=false
        │
        ▼
┌──────────────────────────────────┐
│  Legacy Mode                     │
│  Response:                       │
│  {                                │
│    fri, tingkat_risiko,          │
│    rekomendasi (legacy list),    │
│    mitigasi                      │
│    ← NO knowledge_recommendation │
│    ← NO knowledge_source         │
│  }                                │
└──────────────────────────────────┘

USE_KNOWLEDGE_RECOMMENDATION=true
        │
        ▼
┌──────────────────────────────────┐
│  Knowledge Mode                  │
│  Response:                       │
│  {                                │
│    fri, tingkat_risiko,          │
│    rekomendasi (legacy-compat),  │
│    mitigasi,                     │
│    knowledge_recommendation: {   │
│      recommended: [...],         │
│      alternative: [...],         │
│      not_recommended: [...]      │
│    },                             │
│    knowledge_source: {           │
│      version, engine, duration   │
│    }                              │
│  }                                │
└──────────────────────────────────┘
```

### Switching Requirements

- **No restart required** if the flag is read from environment at startup (current implementation requires restart)
- Future enhancement: dynamic flag toggle via admin endpoint
