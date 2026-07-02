# Project Structure

> Panduan struktur folder proyek FloodRisk AI. Setiap folder memiliki tanggung jawab yang jelas dan terdefinisi.

---

## Struktur Root

```
flood-risk-ai/
├── apps/web/           → Frontend Next.js (SPA)
├── backend/            → REST API FastAPI
├── ml/                 → Machine Learning pipeline
├── scripts/            → ETL & utility scripts
├── data/               → Data artifacts (raw, processed, ML splits)
├── docs/               → Dokumentasi proyek
├── tests/              → Backend automated tests
├── outputs/            → Laporan dan output script
├── requirements.txt    → Python dependencies
├── .env.example        → Template environment variables
├── CHANGELOG.md        → Riwayat perubahan
└── README.md           → Overview proyek
```

---

## apps/web/ — Frontend

```
apps/web/
├── app/
│   ├── page.tsx                     → Entry point SPA, layout utama, state orchestration
│   ├── layout.tsx                   → Root HTML layout, metadata, providers
│   └── globals.css                  → CSS variables (design tokens), AI markdown styles
│
├── components/
│   ├── dashboard/
│   │   ├── dashboard-panel.tsx      → Decision Center (Hero Gauge, Charts, Accordion)
│   │   ├── ai-support-panel.tsx     → AI Decision Support dengan LLM
│   │   ├── reports-panel.tsx        → Preview laporan interaktif + tombol export
│   │   ├── workspace-panels.tsx     → Settings & About panels
│   │   └── analytics-panel.tsx      → [PRESERVED – future] Analytics V2
│   │
│   ├── layout/
│   │   ├── sidebar.tsx              → Floating sidebar navigasi (5 menu)
│   │   └── resizable-panel.tsx      → Panel kiri yang bisa di-resize
│   │
│   ├── map/
│   │   ├── map-container.tsx        → Komponen peta utama (MapLibre GL)
│   │   ├── map-overlays.tsx         → UI overlay di atas peta
│   │   ├── search-bar.tsx           → Search bar pencarian wilayah
│   │   ├── PolygonLayer.tsx         → Rendering polygon GeoJSON
│   │   ├── PolygonInteraction.ts    → Hover & click handler polygon
│   │   ├── RegionPopup.ts           → Popup detail wilayah
│   │   ├── FloodRiskLegend.tsx      → Legenda risiko banjir
│   │   └── ...                      → (komponen map lainnya)
│   │
│   ├── report/
│   │   ├── PrintableReport.tsx      → Dokumen A4 profesional (3 halaman)
│   │   ├── ReportPrintWindow.tsx    → Orchestrator print/PDF flow
│   │   └── print.css               → Stylesheet khusus cetak (sumber)
│   │
│   └── shared/
│       ├── index.tsx                → LoadingSkeleton, ErrorState
│       └── Toast.tsx                → Notifikasi toast
│
├── hooks/
│   ├── use-workspace-store.ts       → State menu aktif (WorkspaceMenu type)
│   ├── use-wilayah-sync.ts          → Sinkronisasi wilayah aktif ke localStorage
│   ├── use-realtime-prediction.ts   → TanStack Query wrapper prediksi realtime
│   ├── use-search-history.ts        → Riwayat pencarian multi-wilayah
│   ├── use-conversation-store.ts    → Percakapan AI per wilayah (region-based)
│   ├── use-daily-reset.ts           → Reset otomatis riwayat setiap hari baru
│   ├── use-local-storage.ts         → Generic localStorage hook
│   ├── use-geolocation.ts           → Geolokasi browser
│   └── use-debounce.ts              → Debounce input hook
│
├── services/
│   ├── llm.ts                       → LLM client (Gemini/OpenAI/Anthropic/Groq)
│   ├── prediction.ts                → API client untuk backend prediksi
│   └── geocoding.ts                 → Geocoding client
│
├── types/
│   ├── api.ts                       → Interface TypeScript response API (Cuaca, Rekomendasi, dll.)
│   └── index.ts                     → Type aliases (RiskLevel, Theme, Model)
│
├── lib/
│   ├── constants.ts                 → Konstanta (ukuran panel, STORAGE_KEYS)
│   └── utils.ts                     → cn() helper (clsx + twMerge)
│
├── providers/
│   ├── theme-provider.tsx           → Provider tema gelap/terang/system
│   └── query-provider.tsx           → TanStack Query client provider
│
├── public/
│   ├── print-report.css             → CSS cetak yang di-serve sebagai static file
│   └── geo/                         → GeoJSON batas wilayah Riau
│
├── package.json
├── tsconfig.json
├── next.config.ts
└── eslint.config.mjs
```

---

## backend/ — REST API

```
backend/
├── app.py                    → FastAPI instance, middleware, router registration
├── middleware.py             → Logging request/response
│
├── routers/
│   ├── health.py             → GET /api/health, /api/health/detail
│   ├── prediction.py         → POST /api/prediksi/manual, /api/prediksi/engineered
│   ├── csv_prediction.py     → POST /api/prediksi/csv, /api/prediksi/csv/download
│   ├── realtime.py           → GET /api/prediksi/realtime
│   ├── info.py               → GET /api/info/model, /api/info/version
│   └── provider.py           → GET /api/provider/openmeteo
│
├── services/
│   ├── prediction_gateway.py → Unified entry point: feature eng → predict → DSS
│   ├── predictor_service.py  → Delegasi ke ml.service.predictor
│   └── metadata_service.py   → Model info dan health status
│
├── providers/
│   ├── openmeteo_provider.py → Implementasi Open-Meteo (current + history)
│   ├── weather_provider.py   → Abstract base class WeatherProvider
│   ├── geocoding.py          → Geocoding via Open-Meteo API
│   ├── models.py             → RawWeatherData dataclass
│   └── exceptions.py         → Custom exceptions
│
└── schemas/
    ├── request.py            → Pydantic request models
    └── response.py           → Pydantic response models
```

---

## ml/ — Machine Learning

```
ml/
├── artifacts/
│   ├── random_forest.pkl     → Model RF terlatih (~5 MB)
│   ├── best_lstm.keras       → Model LSTM terlatih (~400 KB)
│   ├── scaler_lstm.pkl       → StandardScaler untuk LSTM
│   └── feature_list.json     → Daftar 9 fitur resmi
│
├── predict/
│   ├── predict.py            → Entry predict(data, model)
│   ├── random_forest.py      → predict_rf(df) → float
│   ├── lstm.py               → predict_lstm(df) → float
│   ├── risk.py               → classify_risk(fri) → str
│   └── preprocess.py         → prepare_dataframe, validate_input
│
├── feature_engineering/
│   ├── builder.py            → FeatureBuilder orchestrator
│   ├── rainfall.py           → rain3, rain7, rain14 rolling
│   ├── anomaly.py            → rainfall_anomaly
│   ├── temperature.py        → temp_range
│   └── calendar.py           → month, day_of_year
│
├── recommendation/
│   ├── recommender.py        → Top-N recommendation engine
│   ├── scorer.py             → Commodity scoring (FRI-based)
│   ├── explain.py            → Explainability (Bahasa Indonesia)
│   └── mitigation.py         → Mitigation action generator
│
├── knowledge/
│   ├── commodity_profiles.json   → Profil 17 komoditas
│   ├── recommendation_rules.json → Aturan scoring
│   ├── mitigation_rules.json     → Aturan mitigasi per level
│   └── references.md             → Referensi ilmiah
│
└── service/
    └── predictor.py          → prediksi() — unified prediction function
```

---

## docs/ — Dokumentasi

```
docs/
├── PROJECT_CONTEXT.md    → Konteks proyek, tujuan, fitur, alur penggunaan
├── ARCHITECTURE.md       → Arsitektur sistem lengkap + Mermaid diagrams
├── PROJECT_STRUCTURE.md  → Panduan struktur folder (file ini)
├── DESIGN_SYSTEM.md      → Design tokens, tema, komponen, prinsip desain
├── FEATURES.md           → Dokumentasi lengkap setiap fitur
├── ROADMAP.md            → Sprint selesai dan rencana ke depan
├── DECISIONS.md          → Log keputusan arsitektur
├── AI_AGENT_GUIDE.md     → Panduan khusus untuk AI Agent baru
├── API_REFERENCE.md      → Referensi semua endpoint API
├── DATA_FLOW.md          → Diagram alur data end-to-end
├── adr/                  → Architecture Decision Records
├── design/               → Spesifikasi desain detail
├── knowledge/            → FAQ dan knowledge base domain
├── research/             → 12 dokumen metodologi penelitian
└── testing/              → Dokumentasi pengujian
```

---

## Konvensi Penamaan

| Tipe | Konvensi | Contoh |
|---|---|---|
| Komponen React | PascalCase | `DashboardPanel`, `MapContainer` |
| Hook | camelCase + `use` prefix | `useWorkspaceStore`, `useConversationStore` |
| Service/utility | camelCase | `fetchRealtimePrediction`, `buildKey` |
| File CSS | kebab-case | `print.css`, `globals.css` |
| File Python | snake_case | `openmeteo_provider.py`, `prediction_gateway.py` |
| CSS Variables | `--kebab-case` | `--brand-primary`, `--bg-card` |
| TypeScript Interface | PascalCase | `PrediksiRealtimeResponse`, `ChatMessage` |
| Konstanta | SCREAMING_SNAKE | `STORAGE_KEY`, `RISK_COLORS` |
