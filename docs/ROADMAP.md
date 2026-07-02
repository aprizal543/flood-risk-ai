# Roadmap

> Riwayat sprint yang telah selesai dan rencana pengembangan ke depan.

---

## Status Ringkasan

| Fase | Status |
|---|---|
| Backend & ML Pipeline | ✅ Selesai |
| REST API v1.0 | ✅ Selesai |
| Frontend MVP | ✅ Selesai |
| Dokumentasi | ✅ Selesai |
| Analytics V2 | 📋 Planned |
| 7-Day Forecast | 📋 Planned |
| Historical Prediction | 📋 Planned |
| Model Audit | 📋 Planned |
| Notification | 📋 Planned |

---

## ✅ Sprint yang Telah Selesai

### BIZ-1 — ETL Pipeline

**Tujuan**: Membangun pipeline data dari raw BMKG Excel ke dataset bersih.

- Merge 24 file Excel BMKG Pekanbaru (2018–2024) → 726 records
- Validasi dan cleaning dataset (hapus sentinel values, enforce types)
- Feature engineering: rolling rainfall, anomaly, temporal features
- Output: `data/interim/bmkg_clean.csv`, `data/processed/bmkg_features.csv`

---

### BIZ-2 — FRI Engine

**Tujuan**: Membangun mesin penghitung Flood Risk Index berbasis formula penelitian.

- Formula FRI berbasis bobot literatur (curah hujan dominan)
- Scoring engine dengan komponen terpisah
- Aggregasi ke skala 0–100
- Validasi output FRI
- Output: `data/processed/bmkg_fri_dataset.csv`

---

### BIZ-3 — Machine Learning

**Tujuan**: Melatih dan mengevaluasi model prediksi FRI.

- Random Forest Regressor (100 trees, 9 fitur)
- LSTM Sequential (7-step lookback)
- Train/test split dan preprocessing
- Model artifacts: `ml/artifacts/random_forest.pkl`, `best_lstm.keras`

---

### BIZ-4 — Decision Support System

**Tujuan**: Membangun engine rekomendasi dan mitigasi.

- Knowledge base 17 komoditas hortikultura (`commodity_profiles.json`)
- Commodity scoring engine berbasis FRI
- Explainability engine (alasan dalam Bahasa Indonesia)
- Mitigation engine (3 level prioritas)
- Unified prediction service `ml/service/predictor.py`

---

### BIZ-5 — REST API

**Tujuan**: Mengekspos seluruh pipeline sebagai REST API.

- FastAPI dengan 10 endpoint
- Pydantic validation
- Error handling & logging middleware
- Open-Meteo provider (current + 14-day history)
- Prediction gateway (unified entry point)
- Realtime prediction endpoint
- 38 automated tests (integration + unit)

---

### UI-FREEZE-V2 — Frontend Foundation

**Tujuan**: Membangun fondasi frontend Next.js 16 dengan design system premium.

- Setup Next.js 16 + React 19 + Tailwind CSS 4
- Design system (dark theme, CSS variables, radius tokens)
- Floating sidebar + resizable panel layout
- MapLibre GL integration dengan GeoJSON Riau
- TanStack Query untuk data fetching
- Theme provider (dark/light)

---

### UI-1 — Dashboard & Core Panels

**Tujuan**: Membangun panel-panel workspace utama.

- Dashboard panel (hero FRI card, weather cards, recommendation)
- AI Decision Support panel dengan LLM integration (4 provider)
- Reports panel dengan print/PDF flow
- Settings & About panels
- Search history multi-wilayah
- Daily reset otomatis

---

### UI-2 — Map & Search

**Tujuan**: Menyempurnakan fitur peta dan pencarian.

- Polygon layer dengan color mapping risiko
- Point-in-polygon untuk hover detection
- Region popup dengan "Lihat Detail"
- Search bar dengan index lokal
- Layer manager dan flood risk legend
- Spatial statistics

---

### UI-3 — Map Improvements

**Tujuan**: Meningkatkan interaktivitas dan performa peta.

- PolygonFilter berdasarkan FRI
- MapStatusBar
- Improved geocoding
- GeoJSON optimization

---

### UI-REPORT-PDF — Professional PDF Export

**Tujuan**: Mengganti print flow lama dengan dokumen A4 profesional.

- `PrintableReport.tsx` — komponen dokumen independen (bukan dashboard)
- `print.css` — stylesheet khusus cetak (A4, page breaks, professional typography)
- `ReportPrintWindow.tsx` — orchestrator print flow via new window
- 3 halaman: Cover + Cuaca + Rekomendasi + Mitigasi + Metadata
- Tidak menggunakan komponen dashboard (sepenuhnya terpisah)

---

### UI-REPORT-PDF-FIX-1 — Header & Footer Refinement

**Tujuan**: Menyempurnakan header dan footer dokumen cetak.

- Header: terpusat, "FloodRisk AI — Forecast Report | {Wilayah}"
- Footer: kiri tanggal/waktu, kanan "Halaman X / Y"
- Hapus metadata berlebihan dari header/footer

---

### UI-NAV-REFINE — Simplifikasi Navigasi MVP

**Tujuan**: Menyederhanakan navigasi untuk MVP.

- Hapus Analytics dari sidebar (source code dipertahankan)
- Navigasi akhir: Dashboard, AI Assistant, Laporan, Pengaturan, Tentang
- Hapus `"analytics"` dari `WorkspaceMenu` type

---

### UI-DASHBOARD-FINAL — Dashboard sebagai Decision Center

**Tujuan**: Mengganti Dashboard lama dengan layout premium Analytics.

- Hero Gauge + Weather Cards + Radar Chart + Bar Chart dari Analytics
- Tambah seksi baru: **Recommendation Detail Accordion**
- Accordion per komoditas: alasan dengan checkmark, ringkasan, skor, keyakinan
- Hero Context Bar: lokasi + tanggal + update time

---

### UI-AI-2 — Premium AI Decision Support

**Tujuan**: Transformasi AI dari chatbot generic ke decision assistant profesional.

- Region-based conversation persistence (localStorage, key: `{wilayah}_{date}`)
- Markdown rendering (headings, bold, bullets, code)
- System prompt diperbarui: format terstruktur wajib (max 350 kata)
- AI section dihapus dari PDF/laporan
- Clear hanya menghapus percakapan wilayah aktif

---

### DOCS-FOUNDATION — Project Knowledge Base

**Tujuan**: Membuat dokumentasi lengkap agar developer atau AI Agent baru dapat langsung memahami proyek.

- 10 dokumen baru di `docs/`
- Update `CHANGELOG.md` dan `README.md`
- Cakupan: konteks, arsitektur, struktur, design system, fitur, roadmap, keputusan, panduan AI Agent, API reference, data flow

---

## 📋 Sprint yang Direncanakan

### MODEL-AUDIT-1

**Prioritas**: Tinggi (penelitian)

- Evaluasi ulang performa Random Forest dengan data terbaru
- Analisis feature importance
- Bandingkan RF vs LSTM secara kuantitatif
- Dokumentasi hasil dalam laporan penelitian

---

### Analytics V2

**Prioritas**: Sedang

- Aktifkan kembali `analytics-panel.tsx` (source code sudah tersedia)
- Tambahkan ke sidebar sebagai menu terpisah
- Tambahkan fitur: tren FRI historis, perbandingan multi-wilayah
- Visualisasi lanjutan (waterfall chart, heatmap kalender)

---

### Historical Prediction

**Prioritas**: Sedang

- Endpoint baru: `GET /api/prediksi/history?wilayah=X&days=30`
- Simpan hasil prediksi per wilayah ke database lokal (SQLite)
- Frontend: grafik tren FRI 30/60/90 hari

---

### 7-Day Forecast

**Prioritas**: Sedang

- Manfaatkan kemampuan forecast Open-Meteo (hingga 16 hari ke depan)
- Endpoint: `GET /api/prediksi/forecast?wilayah=X&days=7`
- Frontend: timeline 7 hari dengan FRI dan risiko per hari

---

### Notification System

**Prioritas**: Rendah

- Alert browser (`Notification API`) untuk kondisi risiko tinggi
- Threshold konfigurasi di Settings (misal: alert jika FRI > 70)
- Daily digest prakiraan risiko

---

### Mobile Responsive

**Prioritas**: Rendah

- Adaptasi layout untuk layar < 768px
- Peta collapsible pada mobile
- Panel bottom sheet menggantikan sidebar panel

---

### Autentikasi

**Prioritas**: Sangat Rendah (opsional untuk penelitian)

- Login sederhana (email + password)
- Menyimpan preferensi dan riwayat per akun
- Berbagi laporan via link publik
