# Design System

> Dokumentasi lengkap design system FloodRisk AI. Seluruh token, prinsip, dan pola komponen yang digunakan dalam aplikasi.

---

## Prinsip Desain

FloodRisk AI mengikuti prinsip **Premium Dark-First Workspace** — terinspirasi dari aplikasi analitik profesional seperti Linear, Vercel Dashboard, dan Raycast.

| Prinsip | Penjelasan |
|---|---|
| **Dark-first** | Tema gelap adalah default. Tema terang tersedia sebagai alternatif. |
| **Floating surfaces** | Sidebar dan peta mengambang di atas background, bukan terpaku ke tepi layar. |
| **Layered depth** | Kedalaman visual diciptakan melalui perbedaan warna background, bukan shadow tebal. |
| **Subtle borders** | Border menggunakan opacity sangat rendah (`rgba(255,255,255,0.06)`) agar tidak mengganggu. |
| **No decorations** | Tidak ada gradient dekoratif, tidak ada animasi berlebihan, tidak ada elemen estetis tanpa fungsi. |
| **Typography hierarchy** | Ukuran teks sangat kecil (8–13px) karena ruang terbatas, namun hierarchy tetap jelas. |

---

## Color Tokens

Seluruh warna didefinisikan sebagai CSS custom properties di `app/globals.css`.

### Dark Theme (Default — `:root`)

```css
/* Brand */
--brand-primary:       #3b82f6   /* Biru utama — aksen, tombol, link aktif */
--brand-primary-dark:  #2563eb   /* Biru gelap — hover state */
--brand-glow:          rgba(59, 130, 246, 0.3)  /* Glow effect pada elemen aktif */

/* Risk Colors */
--risk-rendah:   #22c55e   /* Hijau — FRI 0–33 */
--risk-sedang:   #f59e0b   /* Amber — FRI 34–66 */
--risk-tinggi:   #ef4444   /* Merah — FRI 67–100 */

/* Background Layers */
--bg-app:         #07111F   /* Background paling dalam (halaman) */
--bg-sidebar:     #0B1727   /* Background sidebar floating */
--bg-panel:       #0D1829   /* Background panel workspace */
--bg-card:        #101D31   /* Background kartu / komponen */
--bg-card-hover:  #152438   /* Hover state kartu */
--bg-input:       #0F1A2E   /* Background input, textarea */

/* Text */
--text-primary:    #f1f5f9   /* Teks utama */
--text-secondary:  #cbd5e1   /* Teks sekunder */
--text-muted:      #64748b   /* Teks hint, label, placeholder */

/* Borders */
--border:          rgba(255,255,255,0.06)   /* Border default */
--border-hover:    rgba(255,255,255,0.12)   /* Border on hover */
```

### Light Theme (`.light`)

```css
--bg-app:         #f4f6f9
--bg-sidebar:     #ffffff
--bg-panel:       #ffffff
--bg-card:        #f8fafc
--bg-card-hover:  #f1f5f9
--bg-input:       #f1f5f9

--text-primary:    #0f172a
--text-secondary:  #334155
--text-muted:      #64748b

--border:          rgba(0,0,0,0.06)
--border-hover:    rgba(0,0,0,0.12)

--shadow-float:    0 20px 60px rgba(0,0,0,0.08)
--shadow-card:     0 4px 20px rgba(0,0,0,0.06)
```

### Penggunaan Risk Color

```tsx
// Selalu gunakan map ini untuk konsistensi
const RISK_COLORS = {
  "Risiko Rendah": "#22c55e",
  "Risiko Sedang": "#f59e0b",
  "Risiko Tinggi": "#ef4444",
};

// Background badge
style={{ backgroundColor: `${color}18`, color }}
// → 18 = opacity 10% dalam hex (24/255 ≈ 0.094)
```

---

## Shadow Tokens

```css
--shadow-float:   0 20px 60px rgba(0,0,0,0.35)   /* Sidebar, panel floating */
--shadow-card:    0 4px 20px rgba(0,0,0,0.25)    /* Kartu dalam panel */
--shadow-popup:   0 12px 40px rgba(0,0,0,0.4)    /* Modal, popup, dialog */
```

---

## Border Radius Tokens

```css
--radius-sidebar:   28px   /* Sidebar floating */
--radius-map:       28px   /* Container peta */
--radius-card:      24px   /* Kartu besar (Hero Gauge, Report) */
--radius-weather:   22px   /* Kartu cuaca, item list */
--radius-popup:     20px   /* Popup, dropdown */
--radius-btn:       18px   /* Tombol */
--radius-search:  9999px   /* Search bar (pill) */
--radius-legend:    20px   /* Legenda peta */
--radius-status:    24px   /* Status bar */
```

---

## Typography

### Font Families

```css
--font-sans: "Inter", ui-sans-serif, system-ui, sans-serif
--font-mono: "JetBrains Mono", ui-monospace, monospace
```

### Scale Tipografi (dalam komponen)

| Token Tailwind | Ukuran | Penggunaan |
|---|---|---|
| `text-[8px]` | 8px | Disclaimer, badge kecil |
| `text-[9px]` | 9px | Label, hint, metadata kecil |
| `text-[10px]` | 10px | Body teks panel, deskripsi |
| `text-[11px]` | 11px | Teks utama komponen |
| `text-[12px]` | 12px | Judul sub-section |
| `text-sm` | 14px | Judul panel, heading wilayah |
| `text-xl` | 20px | Nilai metrik (suhu, RH) |
| `text-6xl` | 60px | Angka FRI pada Hero Gauge |

### Line Height

Semua teks menggunakan `leading-relaxed` (1.625) atau `leading-relaxed` (1.7 untuk AI markdown).

---

## Layout Sistem

### Struktur Halaman

```
┌─────────────────────────────────────────────────────────────────┐
│ p-2 gap-2 (padding 8px, gap 8px)                                │
│                                                                   │
│ ┌──────┐  ┌────────────────┐  ┌────────────────────────────┐    │
│ │Sidebar│  │  ResizablePanel│  │    MapContainer            │    │
│ │ 72px  │  │  min:320 def:380 max:720px │  (flex-1)        │    │
│ │fixed  │  │                │  │                            │    │
│ └──────┘  └────────────────┘  └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Sidebar Floating

- Lebar tetap: `72px`
- Posisi: `fixed inset-y-0 left-0 z-30`
- Radius: `28px` dengan margin `mx-2 my-2`
- Background: `var(--bg-sidebar)` + `border border-[var(--border)]`
- Shadow: `shadow-[var(--shadow-float)]`
- **Tidak dapat di-collapse** — desain keputusan sadar (lihat DECISIONS.md)

### Panel Kiri (ResizablePanel)

- Default width: `380px`
- Min width: `320px`
- Max width: `720px`
- Dapat di-resize dengan drag handle

### Peta (MapContainer)

- `flex-1` — mengisi sisa ruang
- Rounded: `28px`
- Selalu aktif, tidak bisa disembunyikan

---

## Komponen Reusable

### Kartu Dasar (Pattern)

```tsx
<div className="bg-[var(--bg-card)] rounded-[var(--radius-card)] border border-[var(--border)] p-4">
  {/* konten */}
</div>
```

### Kartu Weather (Lebih kecil)

```tsx
<div className="bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] p-3.5 hover:border-[var(--border-hover)] hover:translate-y-[-2px] transition-all">
  {/* konten */}
</div>
```

### Badge Risiko

```tsx
<span
  className="px-3 py-1 rounded-full text-[10px] font-semibold"
  style={{ backgroundColor: `${color}18`, color }}
>
  {tingkatRisiko}
</span>
```

### Tombol Primer

```tsx
<button className="px-4 py-2 text-[11px] font-medium rounded-[var(--radius-btn)] bg-[var(--brand-primary)] text-white hover:opacity-90 transition-opacity">
  Label
</button>
```

### Tombol Sekunder (Outline)

```tsx
<button className="px-3 py-1.5 text-[10px] font-medium rounded-[var(--radius-btn)] border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
  Label
</button>
```

### Section Header (Dashboard)

```tsx
<div className="mb-3">
  <h3 className="text-[11px] font-semibold text-[var(--text-primary)]">{title}</h3>
  <p className="text-[9px] text-[var(--text-muted)] mt-0.5">{subtitle}</p>
</div>
```

---

## Animasi

Seluruh animasi menggunakan **Framer Motion**.

### Pattern Stagger (Cascading entrance)

```tsx
const stagger = { animate: { transition: { staggerChildren: 0.08 } } };
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } };

<motion.div {...stagger}>
  <motion.div {...fadeUp}>Item 1</motion.div>
  <motion.div {...fadeUp}>Item 2</motion.div>
</motion.div>
```

### Panel Transition (Workspace switching)

```tsx
<motion.div
  key={activeMenu}
  initial={{ opacity: 0, x: -8 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: 8 }}
  transition={{ duration: 0.15 }}
>
```

### Accordion (Rekomendasi Detail)

```tsx
<motion.div
  initial={{ height: 0, opacity: 0 }}
  animate={{ height: "auto", opacity: 1 }}
  exit={{ height: 0, opacity: 0 }}
  transition={{ duration: 0.25, ease: "easeInOut" }}
>
```

### Progress Bar Animasi

```tsx
<motion.div
  style={{ backgroundColor: color }}
  initial={{ width: 0 }}
  animate={{ width: `${pct * 100}%` }}
  transition={{ duration: 0.8, ease: "easeOut" }}
/>
```

### Aksesibilitas

```css
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0ms !important; animation: none !important; }
}
```

---

## Glassmorphism & Floating

Efek floating dicapai melalui kombinasi:

1. **Background layer berbeda** (`--bg-app` < `--bg-panel` < `--bg-card`)
2. **Border transparan** (`rgba(255,255,255,0.06)`)
3. **Shadow besar** (`0 20px 60px rgba(0,0,0,0.35)`)
4. **Border radius besar** (`24px–28px`)
5. **Padding dalam** (`p-4` hingga `p-6`)

Tidak menggunakan `backdrop-filter: blur` pada komponen utama (performa).

---

## Print / PDF Design

Dokumen cetak menggunakan stylesheet terpisah (`public/print-report.css`).

| Properti | Nilai |
|---|---|
| Ukuran halaman | A4 Portrait (`210mm × 297mm`) |
| Margin | `18mm` semua sisi |
| Font | Inter, 10pt base |
| Line height | 1.6 |
| Warna | Dicetak penuh (`print-color-adjust: exact`) |
| Header | Teks terpusat: "FloodRisk AI — Forecast Report | {Wilayah}" |
| Footer | Kiri: tanggal + waktu. Kanan: "Halaman X / Y" |

---

## Scrollbar Custom

```css
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
```

---

## Cara Menggunakan Design Tokens

```tsx
// ✅ BENAR — gunakan CSS variable
className="bg-[var(--bg-card)] text-[var(--text-primary)]"

// ✅ BENAR — inline style untuk warna dinamis
style={{ color: riskColor, backgroundColor: `${riskColor}18` }}

// ❌ SALAH — hardcode warna
className="bg-[#101D31]"

// ❌ SALAH — gunakan warna Tailwind default untuk background utama
className="bg-slate-900"
```
