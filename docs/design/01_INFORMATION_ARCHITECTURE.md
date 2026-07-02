# Arsitektur Informasi – FloodRisk AI Dashboard

> Revisi 1.1 – Final Design Freeze

## Identitas Produk

**FloodRisk AI** adalah Geo Intelligence Platform untuk prediksi risiko banjir dan rekomendasi komoditas hortikultura di Pekanbaru.

## Prinsip Desain

| # | Prinsip | Deskripsi |
|---|---------|-----------|
| 1 | **Map First, Decision Second** | Peta interaktif adalah fokus visual utama; informasi keputusan mendukung peta |
| 2 | **Dashboard = Realtime** | Dashboard selalu menampilkan prediksi terkini |
| 3 | **Data Before Decoration** | Prioritaskan kejelasan data di atas estetika |
| 4 | **One Source of Truth** | Backend API adalah satu-satunya sumber data |
| 5 | **Bahasa Indonesia First** | Seluruh antarmuka pengguna dalam Bahasa Indonesia |
| 6 | **Responsive by Default** | Semua layout bekerja di desktop, tablet, dan mobile |
| 7 | **Consistency Over Complexity** | Gunakan pattern yang konsisten, hindari variasi tanpa alasan |
| 8 | **Minimal Navigation** | Sidebar icon-only; kurangi klik untuk sampai ke informasi |
| 9 | **Resizable Workspace** | Pengguna mengontrol proporsi panel dan peta |
| 10 | **Professional Geo Intelligence Experience** | Tampilan setara dengan tool GIS profesional |

---

## Hierarki Visual (Direvisi)

### Primary Focus: Peta Interaktif

Peta MapLibre GL JS menempati **area terbesar** dan menjadi anchor visual. Pengguna pertama kali melihat konteks spasial, lalu membaca detail di panel.

### Secondary Focus: Flood Risk Index Card

FRI ditampilkan sebagai compact card (bukan gauge besar) di bagian atas panel informasi. Angka besar + progress bar + badge risiko.

### Supporting Information

Data cuaca, rekomendasi komoditas, dan tindakan mitigasi tersusun vertikal di panel scrollable.

| Prioritas | Elemen | Lokasi | Rasional |
|-----------|--------|--------|----------|
| P0 | Peta Interaktif | Map area (fill) | Geo Intelligence — konteks spasial utama |
| P0 | FRI Card | Panel (top) | Angka keputusan utama |
| P1 | Rekomendasi Komoditas | Panel (middle) | Aksi utama petani |
| P1 | Tindakan Mitigasi | Panel (bottom) | Langkah protektif |
| P2 | Data Cuaca | Panel (supporting) | Konteks pendukung |
| P2 | Map Marker + Popup | Map overlay | Detail spasial on-demand |

---

## Hierarki Informasi

```
FloodRisk AI Dashboard
│
├── Sidebar (80px, icon-only)
│   ├── Logo Ikon
│   ├── Navigation Icons (tooltip on hover)
│   │   ├── Dashboard
│   │   ├── Prediksi Manual
│   │   ├── Upload CSV
│   │   └── Tentang
│   ├── Toggle (collapse/expand)
│   └── Status Indicator
│
├── Panel Informasi (380px, resizable 320–720px)
│   ├── Status Header (tanggal, sumber, waktu)
│   ├── FRI Card (value + progress + badge)
│   ├── Data Cuaca (grid cards)
│   ├── Rekomendasi Komoditas (expandable list)
│   └── Tindakan Mitigasi (timeline)
│
├── ResizableDivider (4px, drag handle)
│
└── Peta Interaktif (MapLibre GL JS, fill)
    ├── MapToolbar (zoom, locate, layers, fullscreen)
    ├── MapMarker (lokasi prediksi)
    ├── FloatingLegend (risiko)
    └── Popup (on marker click)
```

---

## Alur Pengguna Utama

```
1. Buka Dashboard
   ↓
2. Peta langsung terlihat (map-first) + prediksi otomatis dimuat
   ↓
3. Panel menampilkan FRI + rekomendasi + mitigasi
   ↓
4. (Opsional) Resize panel untuk memperluas peta
   ↓
5. (Opsional) Klik komoditas → detail alasan
   ↓
6. (Opsional) Ganti wilayah → refresh prediksi
   ↓
7. (Opsional) Navigasi ke halaman lain via sidebar
```

---

## Persona Target

| Persona | Kebutuhan | Fitur Utama |
|---------|-----------|-------------|
| Petani | Cepat: risiko hari ini + komoditas aman | FRI card + top recommendation |
| Penyuluh | Detail + penjelasan untuk edukasi | Expandable reasons + mitigation timeline |
| Peneliti | Data + metodologi + konteks spasial | Peta + data cuaca + halaman tentang |

---

## Responsivitas

| Breakpoint | Layout | Map Position |
|------------|--------|--------------|
| ≥1280px (Desktop) | Sidebar(80) + Panel(resizable) + Map(fill) | Kanan, dominant |
| 768–1279px (Tablet) | Sidebar(48) + Panel(340) + Map(fill) | Kanan |
| <768px (Mobile) | Topbar + Map(60vh) + Panel(scroll) | **Atas** (map-first) |

---

## Persistent User Preferences

Preferensi pengguna disimpan di `localStorage` dan di-restore otomatis saat aplikasi dibuka:

| Preferensi | Key | Default |
|-----------|-----|---------|
| Sidebar collapsed | `floodrisk_sidebar_collapsed` | `false` |
| Panel width | `floodrisk_panel_width` | `380` |
| Theme | `floodrisk_theme` | `"light"` |
| Map layer | `floodrisk_map_layer` | `"osm"` |

---

## Teknologi Peta

| Aspek | Keputusan |
|-------|-----------|
| Engine | **MapLibre GL JS** (bukan Leaflet) |
| Rendering | Vector tiles (GPU-accelerated) |
| Default tiles | OpenStreetMap |
| Arsitektur | Provider-agnostic (MapTiler, Stadia, custom) |
| Future | Heatmap, clustering, risk zone polygons |
