# Spesifikasi Layout – FloodRisk AI Dashboard

> Revisi 1.1 – Final Design Freeze

## Prinsip Layout

**Map First, Decision Second** — Peta interaktif adalah fokus visual utama. Panel informasi mendukung keputusan. Sidebar hanya navigasi.

## Grid Utama (Desktop ≥1280px)

```
┌────────┬─────────────────────────┬─┬────────────────────────────────────────┐
│        │                         │▐│                                        │
│SIDEBAR │   PANEL INFORMASI       │▐│         PETA INTERAKTIF                │
│  80px  │   380px (resizable)     │▐│         fill (sisa ruang)              │
│        │                         │▐│                                        │
│ icon   │   scrollable            │▐│         MapLibre GL JS                 │
│ only   │                         │▐│                                        │
│        │                         │▐│                                        │
│ fixed  │   min:320 / max:720     │▐│         selalu mengisi sisa            │
│        │                         │▐│                                        │
└────────┴─────────────────────────┴─┴────────────────────────────────────────┘
                                    ↑
                           ResizableDivider
```

## Dimensi

| Area | Lebar | Tinggi | Behavior |
|------|-------|--------|----------|
| Sidebar | 80px fixed | 100vh | Sticky, icon-only, collapsible to 0px (hidden icons remain at 48px) |
| Panel Informasi | 380px default | 100vh | Resizable: min 320px, max 720px, collapsible |
| ResizableDivider | 4px | 100vh | Drag handle, visual indicator on hover |
| Peta | `calc(100vw - sidebar - panel - divider)` | 100vh | Selalu fill sisa ruang |

## Sidebar (80px – Icon Only)

```
┌──────────┐
│  🌊      │  ← Logo ikon (40×40px)
│          │
├──────────┤
│  🏠      │  ← Dashboard (active)
│  ✏️      │  ← Prediksi Manual
│  📤      │  ← Upload CSV
│  ℹ️      │  ← Tentang
│          │
│          │
│          │
├──────────┤
│  ◀      │  ← SidebarToggle (collapse/expand)
├──────────┤
│  ●      │  ← Status indicator (sehat/degraded)
└──────────┘
```

**Tooltip**: Hover pada ikon menampilkan label (delay 300ms).

**Collapse**: Toggle button menciutkan sidebar ke 48px (ikon tetap terlihat tapi lebih kecil). Sidebar **tidak pernah hilang sepenuhnya**.

**State disimpan di localStorage**: `floodrisk_sidebar_collapsed`

**Referensi gaya**: VS Code Activity Bar, Linear sidebar, Vercel navigation.

---

## Panel Informasi (Resizable)

### Resize Behavior

| Aksi | Hasil |
|------|-------|
| Drag divider ke kanan | Panel melebar (max 720px), peta menyusut |
| Drag divider ke kiri | Panel menyempit (min 320px), peta melebar |
| Double-click divider | Reset ke default 380px |
| Klik collapse button | Panel collapse ke 0px, peta full width |
| Klik expand button | Panel restore ke lebar terakhir |

**State disimpan di localStorage**: `floodrisk_panel_width`

### Konten Panel (Scrollable)

```
┌────────────────────────────┐
│ 📅 27 Juni 2026            │  ← Status header
│ Sumber: Open-Meteo         │
│ Update: 09:00 WIB          │
├────────────────────────────┤
│                            │
│  ┌──────────────────────┐  │
│  │   FRI: 67.3          │  │  ← FRI Card (compact)
│  │   ████████████░░░░░  │  │
│  │   Risiko Tinggi      │  │
│  └──────────────────────┘  │
│                            │
├────────────────────────────┤
│ DATA CUACA                 │
│ ┌──────┬──────┬──────┐    │
│ │🌧️45mm│💧92% │🌡️31/24│    │
│ └──────┴──────┴──────┘    │
├────────────────────────────┤
│ REKOMENDASI KOMODITAS      │
│                            │
│ 1. Kangkung        91.8   │
│    ████████████████████░   │
│    [Detail ▼]             │
│                            │
│ 2. Talas            82.6   │
│ 3. Bayam            76.3   │
│ 4. Sawi Hijau       72.5   │
│ 5. Kacang Panjang   59.1   │
├────────────────────────────┤
│ TINDAKAN MITIGASI          │
│ Urgensi: 🔴 Segera         │
│                            │
│ 1. Aktifkan drainase       │
│ 2. Panen darurat           │
│ 3. Pasang penghalang       │
│ ...                        │
└────────────────────────────┘
```

---

## Peta Interaktif (Fill – MapLibre GL JS)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│    ┌─────────────┐                                  │
│    │ MapToolbar  │                                  │
│    │ [+][-][⊕][▢]│                                  │
│    └─────────────┘                                  │
│                                                     │
│                                                     │
│                   ● Pekanbaru                       │
│                   (FRI: 67.3 – Tinggi)              │
│                                                     │
│                                                     │
│                                                     │
│                                                     │
│  ┌───────────────────┐                              │
│  │ FloatingLegend    │                              │
│  │ ● Rendah (0-33)  │                              │
│  │ ● Sedang (34-66) │                              │
│  │ ● Tinggi (67-100)│                              │
│  └───────────────────┘                              │
└─────────────────────────────────────────────────────┘
```

### Map Engine: MapLibre GL JS

| Aspek | Spesifikasi |
|-------|-------------|
| Engine | MapLibre GL JS (open-source, vector tiles) |
| Default tiles | OpenStreetMap (raster) atau OSM vector via MapTiler free tier |
| Arsitektur | Provider-agnostic — MapTiler, Stadia Maps, atau custom dapat diadopsi tanpa redesign |
| Fitur wajib | Vector rendering, smooth zoom, GeoJSON overlay |
| Fitur future | Heatmap layer, clustering, multi-marker |

---

## Responsif: Tablet (768–1279px)

```
┌──┬──────────────────────────┬─┬─────────────────────────────────┐
│▐ │   PANEL INFORMASI        │▐│       PETA INTERAKTIF           │
│48│     340px (resizable)     │ │       fill                      │
│px│                           │ │                                 │
└──┴──────────────────────────┴─┴─────────────────────────────────┘
```

- Sidebar collapse otomatis ke 48px
- Panel default 340px (masih resizable)

## Responsif: Mobile (<768px)

```
┌─────────────────────────┐
│ ≡  FloodRisk AI    🔔   │  ← Topbar (48px, sidebar = drawer)
├─────────────────────────┤
│                         │
│    PETA (60vh)          │  ← Peta PERTAMA (map-first)
│                         │
├─────────────────────────┤
│                         │
│    PANEL (scroll)       │  ← Panel di bawah
│    FRI + Cuaca          │
│    Rekomendasi          │
│    Mitigasi             │
└─────────────────────────┘
```

**Mobile**: Peta ditampilkan PERTAMA (map-first), panel informasi di bawah. Sidebar menjadi drawer (slide from left).

---

## Spacing System

| Token | Nilai | Penggunaan |
|-------|-------|-----------|
| space-1 | 4px | Padding internal elemen kecil |
| space-2 | 8px | Gap antar elemen terkait |
| space-3 | 12px | Padding kartu internal |
| space-4 | 16px | Padding section |
| space-6 | 24px | Gap antar section |
| space-8 | 32px | Margin besar / padding panel |

## Z-Index

| Layer | Z-Index | Elemen |
|-------|---------|--------|
| Map | 0 | MapLibre canvas |
| MapToolbar | 5 | Kontrol peta |
| FloatingLegend | 5 | Legend overlay |
| Panel | 10 | Panel informasi |
| Divider | 15 | Resize handle |
| Sidebar | 20 | Sidebar navigasi |
| Overlay | 30 | Modal / Drawer |
| Toast | 40 | Notifikasi |
