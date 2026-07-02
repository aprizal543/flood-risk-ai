# AI Agent Guide

> Panduan khusus untuk AI Agent atau developer baru yang akan bekerja pada proyek FloodRisk AI. Baca dokumen ini sebelum menyentuh kode apapun.

---

## Project Overview (1 menit)

- **Nama**: FloodRisk AI — DSS Risiko Banjir untuk Hortikultura Pekanbaru
- **Frontend**: Next.js 16, React 19, Tailwind CSS 4, Framer Motion, Recharts, MapLibre GL
- **Backend**: FastAPI (Python 3.12), Random Forest + LSTM, Open-Meteo API
- **LLM**: Gemini / OpenAI / Anthropic / Groq (via env variable)
- **Entry point frontend**: `apps/web/app/page.tsx`
- **Entry point backend**: `backend/app.py`
- **Tipe data utama**: `PrediksiRealtimeResponse` di `apps/web/types/api.ts`

Baca berurutan: `PROJECT_CONTEXT.md` → `ARCHITECTURE.md` → `FEATURES.md` → file ini.

---

## Aturan Umum

### ✅ DO

- Baca source code yang relevan sebelum menulis kode baru
- Ikuti konvensi penamaan yang sudah ada (lihat `PROJECT_STRUCTURE.md`)
- Gunakan CSS variables untuk semua warna (`var(--bg-card)`, bukan `#101D31`)
- Gunakan komponen `cn()` dari `lib/utils.ts` untuk conditional classnames
- Jalankan `npx tsc --noEmit` sebelum selesai
- Jalankan `npx eslint` sebelum selesai
- Jalankan `npx next build` untuk verifikasi akhir
- Pertahankan file `analytics-panel.tsx` — jangan hapus
- Tulis komentar untuk logika non-obvious

### ❌ DON'T

- Jangan hardcode warna (`#3b82f6`) — gunakan `var(--brand-primary)`
- Jangan tambah library baru tanpa alasan yang kuat
- Jangan modifikasi `backend/`, `ml/`, atau model artifacts saat sprint UI
- Jangan print dashboard ke PDF — gunakan `PrintableReport`
- Jangan gunakan `useEffect` untuk set state dari prop yang berubah (React 19 strict)
- Jangan akses `ref.current` saat render (React 19 ESLint error)
- Jangan commit `.env` atau API key
- Jangan ubah `WorkspaceMenu` type tanpa update sidebar dan page.tsx sekaligus

---

## Arsitektur Frontend

```
app/page.tsx                 ← satu-satunya halaman (SPA)
  ├── Sidebar                ← navigasi, 5 menu
  ├── ResizablePanel         ← panel kiri aktif
  │     └── [ActivePanel]    ← switch berdasarkan useWorkspaceStore
  └── MapContainer           ← peta, selalu aktif
```

**State utama** — semua lewat hooks, tidak ada global store:

| Hook | Fungsi |
|---|---|
| `useWorkspaceStore` | Menu aktif saat ini |
| `useWilayahSync` | Wilayah aktif (localStorage) |
| `useRealtimePrediction` | Data prediksi (TanStack Query) |
| `useSearchHistory` | Riwayat multi-wilayah |
| `useConversationStore` | Percakapan AI per wilayah |

---

## Aturan Desain

### Warna

```tsx
// ✅ Benar
className="bg-[var(--bg-card)] text-[var(--text-primary)]"
style={{ color: riskColor, backgroundColor: `${riskColor}18` }}

// ❌ Salah
className="bg-slate-900 text-white"
```

### Risk Color Pattern

```tsx
const RISK_COLORS = {
  "Risiko Rendah": "#22c55e",
  "Risiko Sedang": "#f59e0b",
  "Risiko Tinggi": "#ef4444",
};
const color = RISK_COLORS[data.tingkat_risiko] ?? "#64748b";
```

### Ukuran teks

Panel workspace sangat kompak. Gunakan skala ini:
- Label/hint: `text-[9px]`
- Body teks: `text-[11px]`
- Judul section: `text-[12px]` atau `text-sm`
- Nilai metrik besar: `text-xl` atau lebih

### Animasi

Selalu gunakan Framer Motion, bukan CSS animation untuk entrance:

```tsx
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } };
const stagger = { animate: { transition: { staggerChildren: 0.08 } } };
```

### Radius

Gunakan token radius, bukan nilai arbitrary:
```tsx
rounded-[var(--radius-card)]    // kartu besar
rounded-[var(--radius-weather)] // kartu kecil
rounded-[var(--radius-btn)]     // tombol
rounded-full                    // pill/badge
```

---

## Aturan Komponen

### Panel Baru

Setiap panel workspace harus:
1. Export named function (bukan default export)
2. Menerima `data: PrediksiRealtimeResponse | undefined`
3. Menangani state `!data` dengan empty state yang informatif
4. Menggunakan `overflow-y-auto h-full` pada wrapper utama
5. **Tidak** mengimpor komponen dashboard lain (self-contained)

### Komponen Report

`PrintableReport` adalah dokumen cetak independen:
- Tidak menggunakan Tailwind classes
- Menggunakan class CSS murni dari `print.css`
- Tidak ada Framer Motion
- Tidak ada shadow/rounded-corner

Setiap kali `print.css` diubah → copy manual ke `public/print-report.css`.

### Komponen Map

Map components menggunakan MapLibre GL JS API secara langsung. Tidak ada abstraksi layer React untuk MapLibre — gunakan `map.addLayer()`, `map.addSource()` dll. langsung via `useRef`.

---

## TypeScript Rules

```typescript
// ✅ Selalu type props secara eksplisit
interface Props {
  data: PrediksiRealtimeResponse | undefined;
}

// ✅ Gunakan type dari types/api.ts, jangan redefinisi
import type { PrediksiRealtimeResponse, Rekomendasi } from "@/types/api";

// ✅ WorkspaceMenu type di hooks/use-workspace-store.ts
// Update type ini saat menambah/hapus menu di sidebar

// ❌ Jangan gunakan `any`
// ❌ Jangan skip type checking dengan `as unknown as X`
```

---

## Aturan Backend

- Semua prediksi masuk melalui `backend/services/prediction_gateway.py`
- Jangan memanggil `ml/service/predictor.py` langsung dari router
- Error response selalu dalam format: `{"status": "error", "kode": N, "pesan": "..."}`
- Semua endpoint prefix dengan `/api/`
- Gunakan Pydantic untuk validasi input/output

---

## Build & Lint

```bash
# Wajib dijalankan sebelum selesai sprint
cd apps/web
npx tsc --noEmit          # TypeScript check
npx eslint .              # ESLint check
npx next build            # Production build

# Backend
cd ../..
pytest tests/ -v          # 38 tests harus pass
```

---

## Prompt Rules untuk AI Agent

Saat menerima task sprint, ikuti urutan ini:

1. **Baca dulu** — baca file yang relevan sebelum menulis kode
2. **Buat task list** — gunakan todo_list sebelum mulai
3. **Jangan ubah** yang tidak diminta (backend, model, dll.)
4. **Reuse** komponen dan data yang sudah ada
5. **Verify** — jalankan tsc + eslint + build sebelum selesai
6. **Jangan asumsi** — kalau tidak yakin, baca source code

### Sprint dengan Instruksi "JANGAN UBAH X"

Ikuti secara ketat. Jika sprint UI mengatakan "jangan ubah backend", maka:
- Tidak boleh menyentuh file di `backend/`, `ml/`, `tests/`
- Tidak boleh mengubah response format API
- Tidak boleh mengubah model artifacts

### Saat Build Gagal

1. Baca error dengan teliti — jangan patch secara buta
2. Jika sama error 2x → analisis root cause, coba pendekatan berbeda
3. React 19 ESLint rules ketat: tidak boleh setState di effect, tidak boleh akses ref saat render

---

## Lokasi File Kritis

| File | Fungsi |
|---|---|
| `apps/web/app/page.tsx` | Orchestrator utama SPA |
| `apps/web/app/globals.css` | Design tokens (CSS variables) |
| `apps/web/types/api.ts` | Type definitions response API |
| `apps/web/hooks/use-workspace-store.ts` | WorkspaceMenu type + state |
| `apps/web/services/llm.ts` | LLM client + system prompt |
| `apps/web/components/report/PrintableReport.tsx` | Dokumen PDF A4 |
| `apps/web/public/print-report.css` | CSS cetak (static) |
| `backend/services/prediction_gateway.py` | Entry point semua prediksi |
| `ml/artifacts/` | Model files (jangan diubah) |
| `ml/knowledge/commodity_profiles.json` | Knowledge base 17 komoditas |
