# Features

> Dokumentasi lengkap setiap fitur FloodRisk AI — tujuan, alur, sumber data, status, dan rencana pengembangan.

---

## 1. Dashboard — Decision Center

### Tujuan

Menjadi pusat pengambilan keputusan utama. Menampilkan semua informasi prediksi risiko banjir dalam satu tampilan premium yang mudah dipahami.

### Komponen

| Komponen | Deskripsi |
|---|---|
| **Hero Context Bar** | Baris konteks lokasi + tanggal + waktu update, satu baris di atas gauge |
| **Hero FRI Gauge** | Gauge arc SVG animasi dengan nilai FRI dan tingkat risiko |
| **Weather Cards (2×2)** | Curah hujan, kelembapan, suhu, flood risk — dengan progress bar animasi |
| **Radar Chart** | Visualisasi komposisi faktor risiko (Hujan, Kelembapan, Suhu, FRI) |
| **Bar Chart Top 5** | Horizontal bar chart ranking komoditas berdasarkan skor |
| **Recommendation Accordion** | Accordion per komoditas: alasan ✓, ringkasan, skor, keyakinan |
| **Mitigation Timeline** | Kartu tindakan mitigasi berurutan berdasarkan prioritas |
| **Quick Insights** | 3 insight otomatis berdasarkan kondisi cuaca aktual |

### Alur

```
useRealtimePrediction(wilayah) → TanStack Query
  → GET /api/prediksi/realtime?wilayah={wilayah}
  → Backend: Open-Meteo → Feature Eng → RF → DSS
  → PrediksiRealtimeResponse
  → DashboardPanel render semua section
```

### Sumber Data

- `PrediksiRealtimeResponse` dari backend (realtime via Open-Meteo)
- Cache TanStack Query: 5 menit

### Status

✅ **Selesai** — Production ready

### Future Improvement

- Tambah sparkline tren FRI 14 hari
- Komparasi multi-wilayah side-by-side

---

## 2. AI Decision Support

### Tujuan

Memungkinkan pengguna bertanya pertanyaan natural tentang hasil prediksi — FRI, komoditas, mitigasi — dan mendapatkan jawaban terstruktur dari LLM dalam Bahasa Indonesia.

### Fitur

| Fitur | Deskripsi |
|---|---|
| **Percakapan terstruktur** | Respon LLM dalam format: judul → penjelasan → bullets → ringkasan |
| **Region-based persistence** | Percakapan tersimpan per `{wilayah}_{forecast_date}` di localStorage |
| **Markdown rendering** | Headings, bold, italic, bullets, numbered list — tanpa raw `**` |
| **Evidence panel** | Panel lipat menampilkan data prediksi yang digunakan AI |
| **Quick suggestions** | 5 pertanyaan preset yang langsung terkirim saat diklik |
| **Regenerate** | Ulangi respon terakhir dengan konteks yang sama |
| **Copy** | Salin pesan ke clipboard |
| **Clear current** | Hapus percakapan wilayah aktif saja |

### Alur

```
Pengguna klik suggestion / ketik pertanyaan
  → useConversationStore: load conversation untuk wilayah aktif
  → chat(data, messages, userMessage) — services/llm.ts
  → buildMessages: SYSTEM_PROMPT + KNOWLEDGE + context prediksi + history
  → callGemini() / callOpenAI() / callAnthropic() / callGroq()
  → Response → MarkdownContent renderer
  → useConversationStore: simpan ke localStorage
```

### Persistence Key

```
{wilayah}_{forecast_date}
→ "Pekanbaru_2026-07-01"
→ "Kampar_2026-06-30"
```

### Provider yang Didukung

| Provider | Model Default | Env Variable |
|---|---|---|
| Gemini | gemini-2.0-flash | `NEXT_PUBLIC_LLM_PROVIDER=gemini` |
| OpenAI | gpt-4o-mini | `NEXT_PUBLIC_LLM_PROVIDER=openai` |
| Anthropic | claude-3-haiku | `NEXT_PUBLIC_LLM_PROVIDER=anthropic` |
| Groq | llama-3.1-8b-instant | `NEXT_PUBLIC_LLM_PROVIDER=groq` |

### Sumber Data

- `PrediksiRealtimeResponse` (diinjeksi ke system prompt sebagai context)
- `NEXT_PUBLIC_LLM_API_KEY` (wajib dikonfigurasi)

### Status

✅ **Selesai** — Production ready

### Future Improvement

- Streaming response (token by token)
- Ekspor percakapan sebagai PDF
- Riwayat percakapan antar sesi (tanggal berbeda)

---

## 3. Laporan (Reports)

### Tujuan

Menghasilkan dokumen laporan profesional yang dapat dicetak atau diekspor sebagai PDF — cocok untuk lampiran skripsi, submisi ke dosen, atau dokumentasi stakeholder.

### Fitur

| Fitur | Deskripsi |
|---|---|
| **Preview interaktif** | Preview laporan di workspace (scrollable) |
| **Export PDF** | Buka jendela baru → render PrintableReport → cetak/save PDF |
| **Print Report** | Sama dengan Export PDF, dialog cetak browser |
| **A4 Layout** | 3 halaman A4 portrait, margin 18mm |
| **Header konsisten** | "FloodRisk AI — Forecast Report | {Wilayah}" terpusat di setiap halaman |
| **Footer informatif** | Kiri: tanggal/waktu. Kanan: "Halaman X / Y" |

### Struktur Dokumen PDF

```
Halaman 1:
  - Cover (FloodRisk AI, judul, metadata, risk badge)
  - Ringkasan Eksekutif
  - Kondisi Cuaca (tabel)
  - Analisis Risiko Banjir (gauge bar)

Halaman 2:
  - Rekomendasi Komoditas (tabel profesional)
  - Tindakan Mitigasi (tabel prioritas)

Halaman 3:
  - Ringkasan Cepat (insights grid 2×2)
  - Metadata Teknis (tabel)
  - Disclaimer
  - Informasi Penelitian (institusi, peneliti, lisensi)
```

### Alur Export PDF

```
Klik "Export PDF"
  → openPrintWindow({ data })
  → window.open() buka jendela baru
  → Write HTML: Inter font + /print-report.css
  → createRoot().render(<PrintableReport data={data} />)
  → Tunggu: stylesheet load + fonts.ready
  → window.print() → Dialog browser
```

### Sumber Data

- `PrediksiRealtimeResponse` (direuse tanpa request baru)

### Status

✅ **Selesai** — Production ready

### Future Improvement

- Server-side PDF generation (Puppeteer/wkhtmltopdf)
- Template laporan alternatif
- Watermark institusi

---

## 4. Peta Interaktif (Map)

### Tujuan

Visualisasi geografis risiko banjir per wilayah di Riau — memungkinkan pengguna mencari wilayah dan melihat hasil prediksi langsung di peta.

### Fitur

| Fitur | Deskripsi |
|---|---|
| **Search bar** | Pencarian wilayah dengan debounce + index lokal |
| **Polygon GeoJSON** | Batas wilayah Riau ditampilkan sebagai polygon berwarna |
| **Color mapping** | Warna polygon sesuai tingkat risiko (hijau/kuning/merah) |
| **Hover popup** | Popup detail wilayah saat mouse hover |
| **Click popup** | Popup dengan tombol "Lihat Detail" → switch ke Dashboard |
| **Marker** | Marker di titik koordinat wilayah aktif |
| **Riwayat pencarian** | Multi-wilayah dapat disimpan, semua ditampilkan di peta |
| **Layer Manager** | Kontrol layer polygon dan marker |
| **Legend** | Legenda risiko banjir (Rendah/Sedang/Tinggi) |
| **Status bar** | Status koneksi dan koordinat kursor |

### Alur Pencarian

```
Pengguna ketik "Pekanbaru" di search bar
  → LocalSearch mencari di SearchIndex (JSON lokal)
  → setWilayah("Pekanbaru")
  → useWilayahSync menyimpan ke localStorage
  → useRealtimePrediction trigger query baru
  → Peta fly-to ke koordinat hasil prediksi
  → Marker ditampilkan di koordinat lat/lon
```

### Sumber Data

- GeoJSON: `/geo/riau-simplified.geojson` (static file)
- Koordinat: dari `PrediksiRealtimeResponse.cuaca.latitude/longitude`

### Status

✅ **Selesai** — Production ready

### Future Improvement

- Choropleth map (warna polygon berdasarkan FRI realtime semua wilayah)
- Heatmap mode
- Animasi FRI 7 hari berurutan

---

## 5. Prediksi Realtime

### Tujuan

Mengambil data cuaca 14 hari terakhir secara otomatis dari Open-Meteo dan menjalankan pipeline prediksi lengkap tanpa input manual.

### Alur Teknis

```
GET /api/prediksi/realtime?wilayah=Pekanbaru
  → OpenMeteoProvider.get_weather_history(wilayah, days=14)
  → Geocoding: nama → lat/lon
  → Open-Meteo Forecast API: 14 hari data harian
  → weather[-1] = hari terbaru (hari ini)
  → predict_from_raw(weather, history=preceding_13_days)
  → FeatureBuilder: rain3, rain7, rain14, anomaly, temp_range, month, doy
  → predict_rf(df) atau predict_lstm(df)
  → classify_risk(fri)
  → recommend(fri, top_n=5)
  → get_mitigasi(risiko)
  → Return JSON response
```

### Output

```json
{
  "status": "berhasil",
  "wilayah": "Pekanbaru",
  "fri": 45.2,
  "tingkat_risiko": "Risiko Sedang",
  "cuaca": { "rr": 12.4, "rh_avg": 78.0, "tmax": 33.0, "tmin": 24.0, ... },
  "rekomendasi": [{ "komoditas": "Bayam", "skor": 82.0, "alasan": [...] }, ...],
  "mitigasi": [{ "prioritas": 1, "kategori": "Drainase", "tindakan": "..." }, ...]
}
```

### Status

✅ **Selesai** — Production ready

### Future Improvement

- Endpoint multi-wilayah batch
- 7-day forecast (multi-hari ke depan)
- LSTM sebagai model default (setelah validasi lebih lanjut)

---

## 6. Tema (Theme)

### Tujuan

Mendukung preferensi visual pengguna dengan tema gelap (default) dan terang.

### Implementasi

- **Storage**: `localStorage` key `floodrisk_theme`
- **Provider**: `providers/theme-provider.tsx`
- **Switching**: Settings panel → select tema
- **Default**: Dark theme

### Status

✅ **Selesai**

### Future Improvement

- Deteksi otomatis sistem operasi (`prefers-color-scheme`)
- Tema "System" yang mengikuti OS

---

## 7. Riwayat Pencarian

### Tujuan

Menyimpan wilayah yang pernah dicari agar pengguna dapat berpindah antar wilayah dengan cepat.

### Implementasi

- **Hook**: `useSearchHistory`
- **Storage**: `localStorage` key `floodrisk_search_history`
- **Reset**: Otomatis direset setiap hari baru (via `useDailyReset`)
- **Multi-wilayah**: Semua wilayah dalam riwayat ditampilkan sebagai marker di peta

### Status

✅ **Selesai**

---

## 8. Pengaturan (Settings)

### Fitur

| Pengaturan | Keterangan |
|---|---|
| Tema | Pilih Light / Dark |
| Model Default | Informasi (Random Forest) |
| Sumber Data | Informasi (Open-Meteo) |
| LLM Provider | Informasi dari env variable |
| Timezone | Informasi (Asia/Jakarta WIB) |
| Hapus Riwayat | Hapus riwayat prediksi aktif |
| Hapus Percakapan AI | Hapus semua percakapan AI |
| Reset Workspace | Hapus semua data lokal |

### Status

✅ **Selesai**

---

## 9. Tentang (About)

### Isi

- Nama dan versi aplikasi
- Tanggal rilis
- Institusi dan program studi
- Deskripsi penelitian
- Technology stack
- Spesifikasi model
- Sumber data
- Lisensi dan author

### Status

✅ **Selesai**

---

## Fitur Tersimpan (Tidak Dirender)

### Analytics Panel V2

- **File**: `components/dashboard/analytics-panel.tsx`
- **Status**: Source code dipertahankan, tidak dirender
- **Alasan**: Dihapus dari MVP untuk menyederhanakan navigasi
- **Rencana**: Akan diaktifkan kembali sebagai fitur terpisah di Sprint Analytics V2
