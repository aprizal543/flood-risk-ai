# Spesifikasi Komponen – FloodRisk AI Dashboard

> Revisi 1.1 – Final Design Freeze

## Daftar Komponen

| # | Komponen | Lokasi | Prioritas |
|---|----------|--------|-----------|
| 1 | MapView | Map Area | P0 |
| 2 | MapToolbar | Map Area | P0 |
| 3 | FloatingLegend | Map Area | P1 |
| 4 | MapMarker | Map Area | P1 |
| 5 | FRICard | Panel | P0 |
| 6 | RiskBadge | Panel | P0 |
| 7 | WeatherCard | Panel | P1 |
| 8 | CommodityList | Panel | P0 |
| 9 | CommodityItem | Panel | P0 |
| 10 | MitigationList | Panel | P1 |
| 11 | MitigationItem | Panel | P1 |
| 12 | ResizableDivider | Layout | P0 |
| 13 | SidebarNav | Sidebar | P1 |
| 14 | SidebarToggle | Sidebar | P1 |
| 15 | StatusHeader | Panel | P1 |
| 16 | LoadingState | Global | P1 |
| 17 | ErrorState | Global | P1 |

---

## 1. MapView (PRIMARY FOCUS)

**Fungsi**: Peta interaktif sebagai fokus visual utama dashboard.

**Engine**: MapLibre GL JS

**Arsitektur**: Provider-agnostic — mendukung OpenStreetMap, MapTiler, Stadia Maps tanpa redesign.

**Props**:
- `center: [lat, lng]`
- `zoom: number`
- `markers: MapMarker[]`
- `style: string` (tile URL / style JSON)

**Default Config**:
- Center: [0.507, 101.447] (Pekanbaru)
- Zoom: 11
- Tiles: OpenStreetMap raster atau OSM vector

**Features**:
- Vector rendering
- Smooth zoom animation
- GeoJSON overlay (future: risk zones)
- Responsive resize (auto-fills remaining space)

**Future Features** (arsitektur harus mendukung tanpa redesign):
- Heatmap layer
- Marker clustering
- Multi-city markers
- Custom risk zone polygons

---

## 2. MapToolbar

**Fungsi**: Kontrol peta (floating, posisi kanan atas).

**Buttons**:
- Zoom In (+)
- Zoom Out (-)
- Locate (center ke lokasi prediksi)
- Layers (toggle tile layers — future)
- Fullscreen (expand map, collapse panel)

**Visual**:
- Floating card, vertikal stack
- Background: white, shadow-md
- Border-radius: radius-md
- Button size: 36×36px
- Gap: 4px

---

## 3. FloatingLegend

**Fungsi**: Tampilkan legenda risiko (floating, posisi kiri bawah peta).

**Visual**:
```
┌───────────────────┐
│ Legenda Risiko    │
│ ● Rendah (0-33)   │
│ ● Sedang (34-66)  │
│ ● Tinggi (67-100) │
└───────────────────┘
```

- Background: white/90% opacity
- Border-radius: radius-md
- Padding: space-3
- Font: text-sm
- Collapsible (klik header untuk toggle)

---

## 4. MapMarker

**Fungsi**: Marker lokasi prediksi pada peta.

**Props**:
- `position: [lat, lng]`
- `fri: number`
- `riskLevel: string`

**Visual**:
- Circle marker, warna sesuai risk level
- Ukuran: 16px radius
- Border: 2px white
- Popup on click: FRI value + risk level + tanggal
- Pulse animation jika risiko tinggi

---

## 5. FRICard

**Fungsi**: Menampilkan Flood Risk Index (compact card, bukan gauge besar).

**Props**:
- `value: number` (0–100)
- `riskLevel: "Rendah" | "Sedang" | "Tinggi"`

**Visual**:
- Card horizontal: angka besar (kiri) + progress bar + badge (kanan)
- Angka FRI: text-2xl bold (32px)
- Progress bar horizontal: lebar penuh, warna risk level
- RiskBadge di samping
- Background: risk-level-bg (subtle)

**Ukuran**: Full panel width, height ~80px

---

## 6. RiskBadge

**Props**:
- `level: "Rendah" | "Sedang" | "Tinggi"`

**Visual**:
- Pill shape
- Background: risk color 15% opacity
- Text: risk color 100%
- Padding: 4px 12px
- Font: text-sm semibold

---

## 7. WeatherCard

**Props**:
- `rr: number`
- `rh_avg: number`
- `tmax: number`
- `tmin: number`

**Layout**: Grid 3 kolom (atau 2×2 jika panel sempit)

**Per Item**:
- Ikon (Lucide)
- Nilai + satuan (text-md bold)
- Label (text-xs muted)

---

## 8. CommodityList

**Props**:
- `items: CommodityRecommendation[]`
- `maxDisplay: number` (default 5)

**Behavior**:
- Tampilkan top-N items
- "Lihat semua" toggle jika ada lebih

---

## 9. CommodityItem

**Props**:
- `peringkat: number`
- `komoditas: string`
- `skor: number`
- `tingkat_keyakinan: number`
- `alasan: string[]`
- `ringkasan: string`

**Visual**:
- Compact card, border-left warna berdasarkan skor
- Peringkat: circle badge (20px)
- Nama: text-md semibold
- Progress bar skor (thin, 4px height)
- Expandable: klik untuk alasan + ringkasan

**States**:
- Collapsed: nama + skor bar (height ~48px)
- Expanded: + alasan + ringkasan (animasi 250ms)

---

## 10. MitigationList

**Props**:
- `items: TindakanMitigasi[]`
- `urgensi: string`

**Visual**: Timeline/stepper layout vertikal

---

## 11. MitigationItem

**Props**:
- `prioritas: number`
- `kategori: string`
- `tindakan: string`

**Visual**:
- Timeline dot (warna kategori)
- Kategori tag (pill)
- Teks tindakan

---

## 12. ResizableDivider ⭐ NEW

**Fungsi**: Handle untuk resize panel informasi.

**Behavior**:
| Aksi | Hasil |
|------|-------|
| Drag horizontal | Resize panel (320px–720px) |
| Double-click | Reset ke default 380px |
| Drag ke minimum | Collapse panel (0px) |

**Visual**:
- Width: 4px (hit area: 12px transparent)
- Default: `neutral-200` (subtle line)
- Hover: `brand-primary` + cursor `col-resize`
- Active/dragging: `brand-primary` + width 2px glow

**Props**:
- `minWidth: number` (320)
- `maxWidth: number` (720)
- `defaultWidth: number` (380)
- `onResize: (width: number) => void`
- `onCollapse: () => void`
- `onExpand: () => void`

---

## 13. SidebarNav

**Fungsi**: Navigasi icon-only (80px width).

**Items**:
| Icon | Label (tooltip) | Route |
|------|----------------|-------|
| `home` | Dashboard | / |
| `pencil` | Prediksi Manual | /manual |
| `upload` | Upload CSV | /csv |
| `info` | Tentang | /tentang |

**Visual**:
- Icon size: 24px
- Item padding: 16px vertikal
- Active: background `brand-primary/10%` + icon `brand-primary`
- Hover: background `neutral-100`
- Tooltip: muncul setelah 300ms hover, posisi kanan

**Referensi**: VS Code Activity Bar, Linear, Vercel

---

## 14. SidebarToggle ⭐ NEW

**Fungsi**: Tombol collapse/expand sidebar.

**Visual**:
- Posisi: bottom sidebar, sebelum status indicator
- Icon: `chevron-left` (collapse) / `chevron-right` (expand)
- Size: 24×24px
- Background on hover

**Behavior**:
- Collapse: sidebar → 48px (ikon tetap visible, lebih kecil)
- Expand: sidebar → 80px
- State disimpan di localStorage

---

## 15. StatusHeader

**Props**:
- `tanggal: string`
- `sumber: string`
- `waktu: string`

**Visual**:
- Compact single row
- Font: text-xs muted
- Icons: calendar, database, clock

---

## 16. LoadingState

**Variants**:
- MapSkeleton: grey rectangle dengan pulse
- FRICardSkeleton: rectangle pulse
- CommodityListSkeleton: 5 bar placeholders
- FullPageLoader: Map + panel skeletons

---

## 17. ErrorState

**Props**:
- `pesan: string`
- `onRetry?: () => void`

**Visual**:
- Icon `alert-triangle` (amber)
- Pesan Bahasa Indonesia
- Tombol "Coba Lagi" (jika onRetry)
