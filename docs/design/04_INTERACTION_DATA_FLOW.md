# Interaksi & Alur Data – FloodRisk AI Dashboard

> Revisi 1.1 – Final Design Freeze

## API Integration

### Endpoints yang Digunakan

| Aksi UI | Endpoint | Method | Trigger |
|---------|----------|--------|---------|
| Load dashboard | `/api/prediksi/realtime?wilayah=Pekanbaru` | GET | Mount / wilayah change |
| Ganti wilayah | `/api/prediksi/realtime?wilayah={x}` | GET | Dropdown change |
| Prediksi manual | `/api/prediksi/manual` | POST | Form submit |
| Upload CSV | `/api/prediksi/csv` | POST | File upload |
| Download hasil | `/api/prediksi/csv/download` | POST | Button click |
| Health check | `/api/health/detail` | GET | Interval (60s) |
| Info model | `/api/info/model` | GET | Halaman "Tentang" |
| Data cuaca mentah | `/api/provider/openmeteo` | GET | Debug / info |

---

## Alur Data: Dashboard Realtime

```
┌─────────────┐     GET /prediksi/realtime
│  Dashboard  │ ──────────────────────────────► Backend
│  Mount      │                                    │
└─────────────┘                                    │
       ▲                                           ▼
       │                              ┌─────────────────────┐
       │                              │ OpenMeteoProvider    │
       │                              │ (14 hari historis)   │
       │                              └──────────┬──────────┘
       │                                         │
       │                              ┌──────────▼──────────┐
       │                              │ PredictionGateway    │
       │                              │ Feature Engineering  │
       │                              │ → RF/LSTM Prediction │
       │                              │ → Recommendation     │
       │                              │ → Mitigation         │
       │                              └──────────┬──────────┘
       │                                         │
       │              JSON Response              │
       └─────────────────────────────────────────┘
```

---

## State Management

### Global State

```
AppState {
  // User preferences (persisted in localStorage)
  preferences: {
    sidebarCollapsed: boolean     // default: false
    panelWidth: number            // default: 380
    theme: "light" | "dark"      // default: "light"
    mapLayer: string             // default: "osm"
  }

  // Runtime state
  wilayah: string                // "Pekanbaru"
  model: "rf" | "lstm"          // "rf"

  prediction: {
    loading: boolean
    error: string | null
    data: PrediksiResponse | null
  }

  health: {
    status: string
    lastCheck: Date
  }
}
```

### localStorage Keys

| Key | Type | Default | Restore On |
|-----|------|---------|-----------|
| `floodrisk_sidebar_collapsed` | boolean | false | App mount |
| `floodrisk_panel_width` | number | 380 | App mount |
| `floodrisk_theme` | string | "light" | App mount |
| `floodrisk_map_layer` | string | "osm" | App mount |

---

## Interaksi: Panel Resize

### ResizableDivider Interactions

| Aksi Pengguna | Hasil | Animasi |
|---------------|-------|---------|
| Hover divider | Divider highlight (brand-primary), cursor `col-resize` | Instant |
| Drag ke kanan | Panel melebar, peta menyusut (real-time) | None (langsung ikuti mouse) |
| Drag ke kiri | Panel menyempit, peta melebar (real-time) | None |
| Drag melewati min (320px) | Snap: panel collapse ke 0px | 250ms ease-in-out |
| Double-click divider | Reset panel ke default 380px | 200ms ease-in-out |
| Release drag | Simpan lebar ke localStorage | — |

### Collapse/Expand Panel

| State | Panel | Peta | Divider |
|-------|-------|------|---------|
| Normal | 380px (atau custom) | Fill sisa | Visible, draggable |
| Collapsed | 0px | Fill (sidebar + map) | Show expand button |
| Expanding | Animate ke saved width | Animate shrink | Appear |

### Map Auto-Resize

Saat panel di-resize atau collapse/expand:
- MapLibre GL JS `map.resize()` dipanggil otomatis
- Map smooth-fills ruang yang tersedia
- Tidak ada layout jump

---

## Interaksi: Sidebar

### SidebarToggle

| Aksi | Dari | Ke | Animasi |
|------|------|-----|---------|
| Klik ◀ | Expanded (80px) | Collapsed (48px) | 200ms ease-in-out |
| Klik ▶ | Collapsed (48px) | Expanded (80px) | 200ms ease-in-out |

**Persistence**: State disimpan di `floodrisk_sidebar_collapsed`.

**Sidebar tidak pernah hilang sepenuhnya** — minimal 48px dengan ikon visible.

---

## Interaksi: Map

### MapToolbar Actions

| Button | Aksi |
|--------|------|
| + (Zoom In) | `map.zoomIn()` |
| - (Zoom Out) | `map.zoomOut()` |
| ⊕ (Locate) | `map.flyTo(predictionCenter)` |
| ▢ (Fullscreen) | Collapse panel + expand map full width |

### MapMarker Popup

| Trigger | Aksi |
|---------|------|
| Klik marker | Show popup: FRI, risk level, tanggal |
| Klik di luar | Close popup |

---

## Interaksi: Komoditas Detail

| Step | Aksi | UI Change |
|------|------|-----------|
| 1 | Klik commodity card | Expand: show alasan + ringkasan |
| 2 | Klik lagi | Collapse back |

**Animasi**: height transition 250ms ease-in-out.
**Tidak memerlukan API call** — data sudah di response.

---

## Interaksi: Prediksi Manual

| Step | Aksi |
|------|------|
| 1 | User isi form (tanggal, rr, rh_avg, tmax, tmin) |
| 2 | Client-side validation (same rules: date not future, rr≥0, rh_avg 0-100, tmax≥tmin) |
| 3 | POST /api/prediksi/manual |
| 4 | Tampilkan hasil (FRICard + rekomendasi + mitigasi) |

---

## Interaksi: Upload CSV

| Step | Aksi |
|------|------|
| 1 | Drag-drop atau klik file picker |
| 2 | Validate: .csv extension |
| 3 | Show file preview (nama, ukuran) |
| 4 | POST /api/prediksi/csv |
| 5 | Tampilkan hasil tanggal terakhir |
| 6 | "Download Hasil" → POST /csv/download → browser download |

---

## Error Handling

| Error | HTTP | UI |
|-------|------|-----|
| Network error | — | ErrorState: "Tidak dapat terhubung ke server" |
| Location not found | 404 | ErrorState: "Wilayah tidak ditemukan" |
| Provider unavailable | 503 | ErrorState: "Layanan cuaca sedang tidak tersedia. Coba lagi nanti." |
| Validation error | 422 | Inline field errors (merah, di bawah input) |
| Server error | 500 | ErrorState: "Terjadi kesalahan sistem" |

---

## Refresh Strategy

| Data | Strategy | Interval |
|------|----------|----------|
| Realtime prediction | On-demand (wilayah change / manual refresh) | Tombol refresh |
| Health status | Background polling | 60 detik |
| User preferences | localStorage (no network) | Instant |

---

## Loading States

| Trigger | Komponen | Behavior |
|---------|----------|----------|
| Initial load | Full layout | Map skeleton + panel skeleton |
| Wilayah change | Panel only | Panel skeleton; map tetap visible |
| Manual prediction | Form area | Disable form + spinner on button |
| CSV upload | Result area | Progress bar |
| Panel resize | — | No loading (instant) |

---

## Accessibility

| Requirement | Implementation |
|-------------|---------------|
| Keyboard nav | Tab: sidebar → panel → map toolbar |
| Screen reader | ARIA labels: FRI value, risk level, recommendations |
| Color contrast | WCAG AA (4.5:1 text, 3:1 graphics) |
| Focus ring | Visible on all interactive elements |
| Resize | Keyboard: arrow keys on divider (±10px per press) |
| Motion | Respect `prefers-reduced-motion`: disable animations |
| Map | ARIA: `role="application"`, keyboard zoom (±) |
