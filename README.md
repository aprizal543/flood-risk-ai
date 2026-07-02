# FloodRisk AI

**Sistem Pendukung Keputusan Risiko Banjir untuk Hortikultura Pekanbaru**

Prediksi Flood Risk Index (FRI) menggunakan Random Forest dan LSTM, rekomendasi komoditas hortikultura, dan tindakan mitigasi — berbasis data cuaca realtime Open-Meteo.

---

## Fitur Utama

- **Dashboard Decision Center** — Hero Gauge FRI, visualisasi cuaca, radar chart, bar chart rekomendasi, accordion detail komoditas, timeline mitigasi
- **Peta Interaktif** — MapLibre GL dengan polygon wilayah Riau, pencarian, popup risiko
- **AI Decision Support** — LLM (Gemini/OpenAI/Groq) dengan percakapan per wilayah, markdown rendering, persistensi localStorage
- **Laporan PDF Profesional** — Dokumen A4 3 halaman siap cetak (Cover, Rekomendasi, Metadata)
- **Prediksi Realtime** — Data cuaca Open-Meteo 14-hari tanpa input manual
- **Tema Gelap / Terang**

---

## Quick Start

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan API server
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Jalankan tests
pytest tests/ -v
```

### Frontend

```bash
cd apps/web

# Install dependencies
npm install

# Konfigurasi environment
cp .env.example .env
# Edit .env dan isi NEXT_PUBLIC_LLM_API_KEY

# Development
npm run dev

# Production build
npm run build
npm start
```

---

## Environment Variables

### Backend (`.env`)

```env
HOST=0.0.0.0
PORT=8000
MODEL_DEFAULT=rf
TOP_N_DEFAULT=5
```

### Frontend (`apps/web/.env`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_LLM_PROVIDER=gemini        # gemini | openai | anthropic | groq
NEXT_PUBLIC_LLM_API_KEY=your_api_key
```

---

## API Endpoints

| Method | Path | Deskripsi |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/health/detail` | Status komponen |
| GET | `/api/info/model` | Metadata model |
| GET | `/api/info/version` | Versi aplikasi |
| POST | `/api/prediksi/manual` | Prediksi dari input BMKG manual |
| POST | `/api/prediksi/engineered` | Prediksi dari fitur yang dihitung |
| POST | `/api/prediksi/csv` | Prediksi dari upload CSV |
| POST | `/api/prediksi/csv/download` | Download hasil prediksi CSV |
| GET | `/api/prediksi/realtime` | Prediksi realtime via Open-Meteo |
| GET | `/api/provider/openmeteo` | Data cuaca raw Open-Meteo |

---

## Arsitektur

```
┌────────────────────────────────────────────────┐
│             Frontend (Next.js 16)               │
│  Dashboard  │  AI Support  │  Laporan  │  Peta  │
└─────────────────────┬──────────────────────────┘
                      │ REST API
┌─────────────────────▼──────────────────────────┐
│               Backend (FastAPI)                  │
│      Prediction Gateway → RF/LSTM → DSS          │
└──────────────────────────────────────────────────┘
         │                          │
┌────────▼──────┐          ┌────────▼──────┐
│  Open-Meteo   │          │  LLM Provider  │
│  (cuaca +     │          │  (client-side) │
│   geocoding)  │          └───────────────┘
└───────────────┘
```

Dokumentasi arsitektur lengkap: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Model Machine Learning

| Model | Tipe | Fitur | Target |
|---|---|---|---|
| Random Forest | Regressor (100 trees) | 9 | FRI (0–100) |
| LSTM | Sequential (7-step lookback) | 9 | FRI (0–100) |

**9 Fitur**: `rr`, `rain3`, `rain7`, `rain14`, `rh_avg`, `temp_range`, `rainfall_anomaly`, `month`, `day_of_year`

---

## Klasifikasi Risiko

| FRI | Tingkat | Rekomendasi |
|---|---|---|
| 0 – 33 | Risiko Rendah | Tanam normal |
| 34 – 66 | Risiko Sedang | Tanam dengan pencegahan |
| 67 – 100 | Risiko Tinggi | Tunda atau lindungi tanaman |

---

## Dokumentasi

| Dokumen | Isi |
|---|---|
| [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) | Tujuan, scope, fitur, alur penggunaan |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arsitektur sistem + diagram |
| [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) | Panduan struktur folder |
| [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) | Design tokens, komponen, animasi |
| [`docs/FEATURES.md`](docs/FEATURES.md) | Dokumentasi setiap fitur |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Sprint selesai dan rencana |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Log keputusan arsitektur |
| [`docs/AI_AGENT_GUIDE.md`](docs/AI_AGENT_GUIDE.md) | Panduan untuk AI Agent baru |
| [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | Referensi endpoint API |
| [`docs/DATA_FLOW.md`](docs/DATA_FLOW.md) | Alur data end-to-end |

---

## Roadmap

- ✅ Backend ML Pipeline (ETL, FRI Engine, RF, LSTM, DSS, REST API)
- ✅ Frontend MVP (Dashboard, AI Support, Laporan, Peta)
- ✅ Dokumentasi lengkap
- 📋 Analytics V2 (source code sudah tersedia)
- 📋 7-Day Forecast
- 📋 Historical Prediction
- 📋 Model Audit

---

## Requirements

- Python 3.12+
- Node.js 20+
- FastAPI, scikit-learn, pandas, numpy, joblib, uvicorn
- Next.js 16, React 19, Tailwind CSS 4

---

## Lisensi

Research Project — Universitas Islam Negeri Sultan Syarif Kasim Riau.
Non-commercial. Peneliti: Aprizal, Program Studi Teknik Informatika.
