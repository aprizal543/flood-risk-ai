# Project Context

> Dokumen ini menjelaskan konteks menyeluruh proyek FloodRisk AI — tujuan, ruang lingkup, status pengembangan, dan alur penggunaan. Baca dokumen ini terlebih dahulu sebelum memahami bagian teknis lainnya.

---

## Nama Proyek

**FloodRisk AI — Sistem Pendukung Keputusan Risiko Banjir untuk Hortikultura**

---

## Tujuan Proyek

Membangun sistem berbasis Machine Learning yang dapat:

1. Memprediksi **Flood Risk Index (FRI)** — indeks risiko banjir skala 0–100 — berdasarkan data cuaca harian.
2. Memberikan **rekomendasi komoditas hortikultura** yang paling sesuai untuk kondisi cuaca saat ini.
3. Menghasilkan **tindakan mitigasi** terprioritas agar petani dapat mengambil langkah preventif.
4. Menyediakan **AI Decision Support** berbasis LLM untuk menjawab pertanyaan petani dalam Bahasa Indonesia.
5. Menghasilkan **laporan profesional** yang dapat dicetak atau diekspor sebagai PDF.

---

## Latar Belakang

Pekanbaru dan wilayah sekitar Riau memiliki karakteristik curah hujan tinggi dan rentan banjir. Petani hortikultura di wilayah ini kesulitan dalam:

- Menentukan waktu tanam yang tepat berdasarkan risiko banjir.
- Memilih komoditas yang sesuai dengan kondisi iklim aktual.
- Mengambil tindakan mitigasi yang terukur dan terprioritas.

Proyek ini adalah bagian dari penelitian skripsi di **Program Studi Teknik Informatika, Universitas Islam Negeri Sultan Syarif Kasim Riau**, yang mengembangkan Decision Support System (DSS) berbasis ML untuk membantu pengambilan keputusan budidaya.

---

## Target Pengguna

| Pengguna | Kebutuhan |
|---|---|
| Petani hortikultura | Keputusan tanam dan mitigasi sederhana |
| Penyuluh pertanian | Analisis kondisi wilayah secara visual |
| Peneliti / akademisi | Validasi model, ekspor laporan |
| Stakeholder pemerintah | Ringkasan risiko berbasis wilayah |

---

## MVP Scope

MVP (Minimum Viable Product) v1.0 mencakup:

- ✅ Prediksi FRI berbasis data cuaca Open-Meteo (realtime, tanpa input manual)
- ✅ Rekomendasi 5 komoditas hortikultura teratas
- ✅ Tindakan mitigasi 3 prioritas
- ✅ Peta interaktif berbasis MapLibre
- ✅ AI Decision Support berbasis LLM (Gemini / OpenAI / Groq / Anthropic)
- ✅ Laporan PDF profesional (A4, 3 halaman)
- ✅ Riwayat pencarian multi-wilayah
- ✅ Tema gelap dan terang

---

## Fitur yang Sudah Selesai

### Backend & ML

| Komponen | Status |
|---|---|
| ETL Pipeline (merge, clean, feature engineering) | ✅ Selesai |
| FRI Engine (scoring + aggregation) | ✅ Selesai |
| Random Forest Regressor (100 trees, 9 fitur) | ✅ Selesai |
| LSTM (7-step lookback) | ✅ Selesai |
| Commodity Scoring Engine (17 komoditas) | ✅ Selesai |
| Explainability Engine (Bahasa Indonesia) | ✅ Selesai |
| Mitigation Engine (3-level) | ✅ Selesai |
| Unified Prediction Service | ✅ Selesai |
| REST API FastAPI (10 endpoint) | ✅ Selesai |
| Open-Meteo Provider (14-day history) | ✅ Selesai |
| Realtime Prediction Endpoint | ✅ Selesai |
| 38 Automated Tests | ✅ Selesai |

### Frontend

| Komponen | Status |
|---|---|
| Dashboard — Decision Center (Hero Gauge, Weather, Radar, Bar Chart, Accordion) | ✅ Selesai |
| Peta Interaktif MapLibre (search, polygon, popup) | ✅ Selesai |
| AI Decision Support (LLM, region-based persistence, markdown render) | ✅ Selesai |
| Laporan Interaktif (preview workspace) | ✅ Selesai |
| Export PDF Profesional (3 halaman A4) | ✅ Selesai |
| Tema Gelap / Terang | ✅ Selesai |
| Riwayat Pencarian Multi-Wilayah | ✅ Selesai |
| Sidebar Floating Premium | ✅ Selesai |
| Daily Reset (riwayat direset tiap hari) | ✅ Selesai |

---

## Fitur yang Belum Dibuat (Future)

| Fitur | Keterangan |
|---|---|
| Analytics Panel V2 | Panel visualisasi lanjutan (source code sudah tersedia di `analytics-panel.tsx`) |
| 7-Day Forecast | Prakiraan 7 hari ke depan |
| Historical Prediction | Riwayat prediksi per wilayah (time series) |
| Model Audit | Evaluasi performa Random Forest secara berkala |
| Notifikasi | Alert kondisi risiko tinggi |
| Autentikasi | Login/logout pengguna |
| Multi-Language | Dukungan Bahasa Inggris |
| Mobile Responsive | Adaptasi tampilan untuk perangkat mobile |

---

## Ruang Lingkup Penelitian

- **Domain**: Pertanian hortikultura dataran rendah, wilayah Pekanbaru dan sekitarnya.
- **Data Training**: Dataset BMKG Pekanbaru 2018–2024 (726 records setelah preprocessing).
- **Model**: Random Forest Regressor (model utama) + LSTM (model sekunder).
- **Target Variabel**: Flood Risk Index (FRI) 0–100, dihitung dari formula berbasis literatur.
- **Fitur Model**: `rr`, `rain3`, `rain7`, `rain14`, `rh_avg`, `temp_range`, `rainfall_anomaly`, `month`, `day_of_year`.
- **Sumber Data Realtime**: Open-Meteo API (gratis, tidak memerlukan API key).
- **Batasan**: Prediksi bersifat estimasi. Keputusan budidaya tetap pada pengguna.

---

## Alur Penggunaan Aplikasi

```
1. Pengguna membuka aplikasi
   └── Peta Pekanbaru ditampilkan otomatis

2. Pengguna mengetik nama wilayah di search bar peta
   └── Geocoding via Open-Meteo
   └── Prediksi realtime dijalankan otomatis
   └── Data cuaca 14 hari diambil dari Open-Meteo

3. Hasil prediksi muncul di Dashboard
   └── Hero Gauge: FRI + Tingkat Risiko
   └── Weather Cards: Curah hujan, Kelembapan, Suhu
   └── Radar Chart: Komposisi faktor risiko
   └── Bar Chart: Top 5 Rekomendasi
   └── Accordion: Detail rekomendasi komoditas
   └── Mitigation Timeline: Tindakan prioritas
   └── Quick Insights: Analisis otomatis

4. Pengguna dapat bertanya ke AI Decision Support
   └── Pertanyaan tentang FRI, komoditas, mitigasi
   └── Percakapan tersimpan per wilayah + tanggal
   └── Tersedia di semua sesi selama aplikasi aktif

5. Pengguna membuka menu Laporan
   └── Preview interaktif tersedia
   └── Export PDF / Print Report

6. Pengguna dapat mencari wilayah lain
   └── Prediksi baru dijalankan
   └── Percakapan AI beralih ke wilayah baru
   └── Kembali ke wilayah sebelumnya memulihkan percakapan
```

---

## Teknologi Utama

| Layer | Teknologi |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, Framer Motion, Recharts, MapLibre GL |
| Backend | Python 3.12, FastAPI, Uvicorn |
| ML | scikit-learn (Random Forest), TensorFlow/Keras (LSTM) |
| Data | pandas, numpy, joblib |
| LLM | Gemini 2.0 Flash / GPT-4o-mini / Claude Haiku / LLaMA 3.1 |
| Maps | MapLibre GL JS, Open-Meteo Geocoding API |
| Weather | Open-Meteo API |
| Storage | localStorage (frontend), file-based (model artifacts) |

---

## Informasi Proyek

| Atribut | Nilai |
|---|---|
| Institusi | Universitas Islam Negeri Sultan Syarif Kasim Riau |
| Program Studi | Teknik Informatika |
| Peneliti | Aprizal |
| Jenis | Penelitian Skripsi |
| Lisensi | Research Project — Non-commercial |
| Versi | 1.0.0 |
