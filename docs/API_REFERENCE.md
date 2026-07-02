# API Reference

> Referensi lengkap semua endpoint REST API FloodRisk AI.
> Base URL: `http://localhost:8000`

---

## Health

### `GET /api/health`

Health check sederhana.

**Response**
```json
{ "status": "ok" }
```

---

### `GET /api/health/detail`

Status komponen secara detail.

**Response**
```json
{
  "status": "ok",
  "components": {
    "random_forest": "ok",
    "lstm": "ok",
    "scaler": "ok",
    "feature_list": "ok"
  }
}
```

---

## Info

### `GET /api/info/model`

Metadata model prediksi.

**Response**
```json
{
  "model": "RandomForestRegressor",
  "version": "1.0",
  "features": ["rr","rain3","rain7","rain14","rh_avg","temp_range","rainfall_anomaly","month","day_of_year"],
  "target": "FRI (0-100)"
}
```

---

### `GET /api/info/version`

Versi aplikasi.

**Response**
```json
{ "version": "1.0.0", "api": "FastAPI" }
```

---

## Prediksi

### `POST /api/prediksi/manual`

Prediksi dari input BMKG manual (satu hari, tanpa rolling features).

**Request Body**
```json
{
  "tanggal": "2026-06-27",
  "rr": 45.0,
  "rh_avg": 92.0,
  "tmax": 31.0,
  "tmin": 24.0
}
```

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `tanggal` | string (YYYY-MM-DD) | ✅ | Tanggal observasi |
| `rr` | float ≥ 0 | ✅ | Curah hujan (mm) |
| `rh_avg` | float 0–100 | ✅ | Kelembapan relatif (%) |
| `tmax` | float | ✅ | Suhu maksimum (°C) |
| `tmin` | float | ✅ | Suhu minimum (°C) |
| `model` | string | ❌ | "rf" (default) atau "lstm" |
| `top_n` | int 1–17 | ❌ | Jumlah rekomendasi (default: 5) |

**Response** → lihat [Response Schema](#response-schema)

---

### `POST /api/prediksi/engineered`

Prediksi dari fitur yang sudah dihitung sebelumnya.

**Request Body**
```json
{
  "rr": 45.0,
  "rain3": 120.0,
  "rain7": 210.0,
  "rain14": 380.0,
  "rh_avg": 92.0,
  "temp_range": 7.0,
  "rainfall_anomaly": 1.35,
  "month": 6,
  "day_of_year": 178
}
```

**Response** → lihat [Response Schema](#response-schema)

---

### `POST /api/prediksi/csv`

Prediksi dari upload file CSV. Prediksi menggunakan baris terakhir sebagai data hari ini, baris sebelumnya sebagai history rolling.

**Request**: `multipart/form-data`, field `file` berisi CSV.

**Format CSV yang diharapkan**:
```
tanggal,rr,rh_avg,tmax,tmin
2026-06-14,5.2,75.0,33.1,24.0
2026-06-15,12.4,80.0,32.5,23.8
...
2026-06-27,45.0,92.0,31.0,24.0
```

**Response** → lihat [Response Schema](#response-schema)

---

### `POST /api/prediksi/csv/download`

Sama seperti `/csv` tapi mengembalikan file CSV hasil prediksi.

**Response**: `text/csv` file attachment.

---

### `GET /api/prediksi/realtime`

**Endpoint utama** — prediksi realtime dari Open-Meteo. Ini yang digunakan frontend.

**Query Parameters**

| Parameter | Tipe | Default | Keterangan |
|---|---|---|---|
| `wilayah` | string | — (wajib) | Nama kota/wilayah |
| `model` | string | `rf` | "rf" atau "lstm" |
| `top_n` | int | `5` | Jumlah rekomendasi (1–17) |

**Contoh Request**
```bash
curl "http://localhost:8000/api/prediksi/realtime?wilayah=Pekanbaru"
```

**Response**
```json
{
  "status": "berhasil",
  "wilayah": "Pekanbaru",
  "sumber_data": "Open-Meteo",
  "forecast_date": "2026-07-01",
  "updated_at": "2026-07-01T08:30:00+07:00",
  "waktu_prediksi": "2026-07-01T08:30:00+07:00",
  "model": "rf",
  "versi_model": "1.0",
  "cuaca": {
    "tanggal": "2026-07-01",
    "rr": 12.4,
    "rh_avg": 78.0,
    "tmax": 33.0,
    "tmin": 24.0,
    "latitude": 0.5071,
    "longitude": 101.4478
  },
  "hari_historis": 13,
  "fri": 45.2,
  "tingkat_risiko": "Risiko Sedang",
  "rekomendasi": [...],
  "mitigasi": [...]
}
```

**Error Responses**

| Kode | Kondisi |
|---|---|
| 404 | Wilayah tidak ditemukan |
| 503 | Tidak dapat terhubung ke Open-Meteo |
| 422 | Parameter tidak valid |

---

## Provider

### `GET /api/provider/openmeteo`

Data cuaca raw dari Open-Meteo tanpa prediksi.

**Query Parameters**: `wilayah` (string, wajib)

**Response**: Data cuaca JSON langsung dari Open-Meteo.

---

## Response Schema

### Objek `rekomendasi[]`

```json
{
  "komoditas": "Bayam",
  "komoditas_id": "bayam",
  "skor": 82.5,
  "tingkat_keyakinan": 0.943,
  "tingkat_risiko": "Risiko Sedang",
  "alasan": [
    "Toleransi terhadap genangan moderat",
    "Siklus panen pendek (25-30 hari)",
    "Sesuai dengan kelembapan tinggi"
  ],
  "ringkasan": "Bayam memiliki kesesuaian tinggi untuk kondisi saat ini..."
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `komoditas` | string | Nama komoditas |
| `komoditas_id` | string | ID lowercase (untuk key) |
| `skor` | float 0–100 | Skor kesesuaian |
| `tingkat_keyakinan` | float 0–1 | Rasio skor terhadap skor tertinggi |
| `tingkat_risiko` | string | "Risiko Rendah/Sedang/Tinggi" |
| `alasan` | string[] | Daftar alasan (Bahasa Indonesia) |
| `ringkasan` | string | Ringkasan satu paragraf |

---

### Objek `mitigasi[]`

```json
{
  "prioritas": 1,
  "kategori": "Drainase",
  "tindakan": "Bersihkan saluran drainase dan pastikan air tidak menggenang"
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `prioritas` | int 1–3 | 1=segera, 2=preventif, 3=jangka menengah |
| `kategori` | string | Kategori tindakan |
| `tindakan` | string | Deskripsi tindakan |

---

### Klasifikasi FRI

| FRI | Tingkat Risiko | Rekomendasi Umum |
|---|---|---|
| 0 – 33 | Risiko Rendah | Tanam normal |
| 34 – 66 | Risiko Sedang | Tanam dengan pencegahan |
| 67 – 100 | Risiko Tinggi | Tunda atau lindungi tanaman |

---

## LLM (Client-side)

LLM tidak dipanggil melalui backend — dipanggil langsung dari browser via `services/llm.ts`.

**Konfigurasi** (environment variables frontend):
```
NEXT_PUBLIC_LLM_PROVIDER=gemini    # gemini|openai|anthropic|groq
NEXT_PUBLIC_LLM_API_KEY=your_key
```

**Provider endpoints**:

| Provider | URL |
|---|---|
| Gemini | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent` |
| OpenAI | `https://api.openai.com/v1/chat/completions` |
| Anthropic | `https://api.anthropic.com/v1/messages` |
| Groq | `https://api.groq.com/openai/v1/chat/completions` |
