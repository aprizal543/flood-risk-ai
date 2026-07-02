# Design Tokens & Style Guide – FloodRisk AI

> Revisi 1.1 – Final Design Freeze

## Palet Warna

### Brand

| Token | Hex | Penggunaan |
|-------|-----|-----------|
| `brand-primary` | `#2563eb` | Aksen utama, link, tombol primer, divider active |
| `brand-primary-dark` | `#1d4ed8` | Hover tombol primer |
| `brand-secondary` | `#0f172a` | Sidebar background |

### Risk Level

| Token | Hex | Penggunaan |
|-------|-----|-----------|
| `risk-rendah` | `#22c55e` | FRI rendah, marker rendah |
| `risk-rendah-bg` | `#f0fdf4` | Background FRI card rendah |
| `risk-sedang` | `#f59e0b` | FRI sedang, marker sedang |
| `risk-sedang-bg` | `#fffbeb` | Background FRI card sedang |
| `risk-tinggi` | `#ef4444` | FRI tinggi, marker tinggi |
| `risk-tinggi-bg` | `#fef2f2` | Background FRI card tinggi |

### Neutral

| Token | Hex | Penggunaan |
|-------|-----|-----------|
| `neutral-50` | `#f8fafc` | Background panel |
| `neutral-100` | `#f1f5f9` | Background kartu, hover sidebar |
| `neutral-200` | `#e2e8f0` | Border, divider default |
| `neutral-300` | `#cbd5e1` | Border hover |
| `neutral-500` | `#64748b` | Text muted, ikon inactive |
| `neutral-700` | `#334155` | Text secondary |
| `neutral-900` | `#0f172a` | Text primary |

### Kategori Mitigasi

| Token | Hex | Kategori |
|-------|-----|----------|
| `cat-drainase` | `#3b82f6` | Drainase |
| `cat-monitoring` | `#8b5cf6` | Monitoring |
| `cat-lahan` | `#10b981` | Persiapan Lahan |
| `cat-panen` | `#f59e0b` | Panen |
| `cat-lindung` | `#ef4444` | Perlindungan |
| `cat-tanam` | `#6366f1` | Penanaman |
| `cat-pulih` | `#14b8a6` | Pemulihan |
| `cat-dokumen` | `#6b7280` | Dokumentasi |

---

## Tipografi

### Font Family

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Scale

| Token | Size | Weight | Line Height | Penggunaan |
|-------|------|--------|-------------|-----------|
| `text-xs` | 11px | 400 | 1.4 | Caption, tooltip, status |
| `text-sm` | 13px | 400 | 1.5 | Label, helper, metadata |
| `text-base` | 14px | 400 | 1.6 | Body text |
| `text-md` | 16px | 500 | 1.5 | Card title, list item |
| `text-lg` | 18px | 600 | 1.4 | Section header |
| `text-xl` | 24px | 700 | 1.3 | Page title |
| `text-2xl` | 32px | 700 | 1.2 | FRI value (compact card) |

---

## Spacing

| Token | Nilai |
|-------|-------|
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-5` | 20px |
| `space-6` | 24px |
| `space-8` | 32px |
| `space-10` | 40px |

---

## Border Radius

| Token | Nilai | Penggunaan |
|-------|-------|-----------|
| `radius-sm` | 4px | Badges, tags, tooltip |
| `radius-md` | 8px | Cards, inputs, toolbar |
| `radius-lg` | 12px | Panels, modals |
| `radius-full` | 9999px | Pills, circles, markers |

---

## Shadow

| Token | Nilai | Penggunaan |
|-------|-------|-----------|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle elevation |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Cards, toolbar |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Panel, dropdown |
| `shadow-glow` | `0 0 0 2px rgba(37,99,235,0.3)` | Divider active state |

---

## Motion & Animasi

### Durasi

| Token | Nilai | Penggunaan |
|-------|-------|-----------|
| `duration-instant` | 0ms | Divider drag (real-time follow) |
| `duration-fast` | 150ms | Hover, focus ring |
| `duration-normal` | 200ms | Panel resize (animated), sidebar toggle |
| `duration-medium` | 250ms | Collapse/expand, card expand |
| `duration-slow` | 400ms | Page transitions |

### Easing

| Token | Nilai | Penggunaan |
|-------|-------|-----------|
| `ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard transitions |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.6, 1)` | Resize, collapse, expand |
| `ease-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful (marker pulse) |

### Aturan Motion per Komponen

| Komponen | Aksi | Durasi | Easing |
|----------|------|--------|--------|
| ResizableDivider | Drag | Instant (0ms) | — (follow mouse) |
| ResizableDivider | Double-click reset | 200ms | ease-in-out |
| Panel | Collapse | 250ms | ease-in-out |
| Panel | Expand | 250ms | ease-in-out |
| Sidebar | Toggle | 200ms | ease-in-out |
| CommodityItem | Expand/collapse | 250ms | ease-default |
| MapLibre | `map.resize()` | Automatic (internal) | — |
| MapMarker | Pulse (risiko tinggi) | 1500ms loop | ease-in-out |
| Tooltip | Appear | 150ms | ease-default |
| Tooltip | Delay | 300ms | — |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0ms !important; animation: none !important; }
}
```

---

## Map Configuration (MapLibre GL JS)

### Default Style

```javascript
{
  container: 'map',
  style: 'https://demotiles.maplibre.org/style.json', // atau OSM raster
  center: [101.447, 0.507],  // Pekanbaru [lng, lat]
  zoom: 11,
  attributionControl: true
}
```

### Provider-Agnostic Architecture

| Provider | Status | Catatan |
|----------|--------|---------|
| OpenStreetMap (raster) | Default | Gratis, tanpa API key |
| MapTiler (vector) | Future | Perlu API key, visual lebih baik |
| Stadia Maps | Future | Alternatif vector tiles |
| Custom | Future | Self-hosted tiles |

Style JSON dapat diganti tanpa perubahan kode komponen.

---

## Komponen Primitif

### Button

| Variant | Background | Text | Border |
|---------|-----------|------|--------|
| Primary | `brand-primary` | white | none |
| Secondary | transparent | `neutral-700` | `neutral-200` |
| Ghost | transparent | `neutral-500` | none |
| Icon | transparent | `neutral-500` | none |

Ukuran: `sm` (28px), `md` (36px), `lg` (44px)

### Input

- Height: 36px
- Border: `neutral-200`
- Focus: `brand-primary` ring 2px
- Error: `risk-tinggi` border
- Border-radius: `radius-md`

### Card

- Background: white
- Border: `neutral-200`
- Border-radius: `radius-md`
- Padding: `space-4`
- Shadow: `shadow-sm`
- Hover (jika clickable): `shadow-md`, transition `duration-fast`

---

## Dark Mode (Future)

Arsitektur token menggunakan CSS variables untuk mendukung dark mode:

```css
:root { --bg-panel: #f8fafc; --text-primary: #0f172a; --bg-sidebar: #0f172a; }
.dark { --bg-panel: #1e293b; --text-primary: #f1f5f9; --bg-sidebar: #0f172a; }
```

Map: MapLibre mendukung dark style JSON (swap style URL).

Implementasi dark mode dijadwalkan setelah MVP.

---

## Icon Set

**Lucide Icons** (MIT license):

| Konteks | Icon |
|---------|------|
| Dashboard | `home` |
| Prediksi Manual | `pencil` |
| Upload CSV | `upload` |
| Tentang | `info` |
| Curah Hujan | `cloud-rain` |
| Kelembaban | `droplets` |
| Suhu | `thermometer` |
| Refresh | `refresh-cw` |
| Error | `alert-triangle` |
| Success | `check-circle` |
| Expand | `chevron-down` |
| Collapse | `chevron-up` |
| Sidebar Collapse | `chevron-left` |
| Sidebar Expand | `chevron-right` |
| Zoom In | `plus` |
| Zoom Out | `minus` |
| Locate | `crosshair` |
| Fullscreen | `maximize-2` |
| Layers | `layers` |
