# Changelog

Semua perubahan signifikan proyek FloodRisk AI dicatat di sini.

---

## [1.1.0] — 2026-07-01

### UI Sprints (Frontend)

#### Sprint UI-REPORT-PDF — Professional PDF Export
- Komponen `PrintableReport.tsx` terpisah dari dashboard (dokumen A4 independen)
- Stylesheet cetak khusus `print.css` (A4, page breaks, typography profesional)
- `ReportPrintWindow.tsx` — orchestrator print flow via new window
- 3 halaman: Cover + Cuaca | Rekomendasi + Mitigasi | Insights + Metadata

#### Sprint UI-REPORT-PDF-FIX-1 — Header & Footer
- Header: terpusat, "FloodRisk AI — Forecast Report | {Wilayah}"
- Footer: tanggal/waktu (kiri) + "Halaman X / Y" (kanan)

#### Sprint UI-NAV-REFINE — Simplifikasi Navigasi
- Analytics dihapus dari sidebar (source code dipertahankan)
- Navigasi: Dashboard, AI Assistant, Laporan, Pengaturan, Tentang

#### Sprint UI-DASHBOARD-FINAL — Dashboard sebagai Decision Center
- Layout premium Analytics dijadikan tampilan utama Dashboard
- Tambah seksi **Recommendation Detail Accordion**
- Hero Context Bar: lokasi + tanggal + waktu update

#### Sprint UI-AI-2 — Premium AI Decision Support
- Region-based conversation persistence (localStorage)
- Markdown rendering (heading, bold, bullet, numbered list)
- System prompt diperbarui: format terstruktur wajib (max 350 kata)
- AI section dihapus dari PDF
- Clear hanya menghapus percakapan wilayah aktif

#### Sprint DOCS-FOUNDATION — Project Knowledge Base
- 10 dokumen baru di `docs/`
- Update `CHANGELOG.md` dan `README.md`

---

## [1.0.0-rc] — 2026-06-28

### Backend Release Candidate

#### ETL Pipeline
- Merge 24 file Excel BMKG Pekanbaru (2018–2024) → 726 records
- Dataset validation, cleaning (sentinel removal, type enforcement)
- Feature engineering (rolling, temporal, anomaly)
- FRI generation engine (scoring + aggregation)
- ML dataset preparation (train/test split)

#### Machine Learning
- Random Forest Regressor (100 trees, 9 fitur)
- LSTM Sequential (7-step lookback, Keras)
- Prediction pipeline dengan lazy model loading

#### Decision Support System
- Knowledge base 17 komoditas hortikultura
- Dynamic commodity scoring engine
- Explainability engine (Bahasa Indonesia)
- Mitigation engine (3-level actions)
- Unified prediction service

#### REST API (FastAPI)
- 10 endpoint (health, info, prediksi manual/CSV/realtime, provider)
- Open-Meteo provider (current + 14-day history)
- Prediction gateway (unified entry point)
- 38 automated tests

### UI Sprints

#### Sprint UI-FREEZE-V2 — Frontend Foundation
- Next.js 16 + React 19 + Tailwind CSS 4
- Design system (dark theme, CSS variables, radius tokens)
- Floating sidebar + resizable panel layout
- MapLibre GL integration dengan GeoJSON Riau
- TanStack Query untuk data fetching

#### Sprint UI-1 — Core Panels
- Dashboard, AI Support, Reports, Settings, About panels
- LLM integration (Gemini, OpenAI, Anthropic, Groq)
- Print/PDF flow (versi lama)
- Search history multi-wilayah + daily reset

#### Sprint UI-2 & UI-3 — Map & Search
- Polygon layer dengan color mapping risiko
- Point-in-polygon, region popup
- Search bar dengan index lokal
- Layer manager, flood risk legend, spatial statistics
