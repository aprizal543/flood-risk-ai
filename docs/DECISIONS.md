# Architecture Decision Log

> Catatan seluruh keputusan arsitektur dan desain penting yang dibuat selama pengembangan FloodRisk AI. Setiap keputusan disertai konteks dan alasan.

---

## DEC-001 — Analytics Dihapus dari Sidebar (MVP)

**Tanggal**: 1 Juli 2026
**Sprint**: UI-NAV-REFINE

**Keputusan**: Analytics tidak ditampilkan di sidebar dan tidak dirender di workspace.

**Alasan**:
- MVP harus sesederhana mungkin — satu Decision Center sudah cukup.
- Dashboard baru (dari layout Analytics) sudah mencakup semua visualisasi utama.
- Mengurangi cognitive load pengguna.

**Dampak**:
- `analytics-panel.tsx` dipertahankan utuh di source code.
- `"analytics"` dihapus dari `WorkspaceMenu` type.
- Dapat diaktifkan kembali di Sprint Analytics V2.

---

## DEC-002 — Visualisasi Analytics Dipindahkan ke Dashboard

**Tanggal**: 1 Juli 2026
**Sprint**: UI-DASHBOARD-FINAL

**Keputusan**: Layout premium Analytics (Hero Gauge, Radar Chart, Bar Chart) dijadikan tampilan utama Dashboard.

**Alasan**:
- Dashboard lama terlalu sederhana (teks + kartu saja).
- Visualisasi Analytics jauh lebih informatif dan professional.
- Penggabungan menghemat satu menu navigasi.
- Tambah Accordion Detail Rekomendasi yang tidak ada di keduanya.

**Dampak**:
- `dashboard-panel.tsx` ditulis ulang sepenuhnya.
- `analytics-panel.tsx` dipertahankan sebagai future module.

---

## DEC-003 — Realtime Endpoint Hanya Menyediakan Prediksi Hari Ini

**Tanggal**: 28 Juni 2026
**Sprint**: BIZ-5

**Keputusan**: `GET /api/prediksi/realtime` hanya mengembalikan prediksi untuk tanggal hari ini (hari terakhir dari 14-hari Open-Meteo history).

**Alasan**:
- Scope penelitian fokus pada keputusan hari ini, bukan multi-hari.
- Open-Meteo menyediakan data hingga hari ini, bukan forecast hari depan yang akurat.
- Menyederhanakan UI (satu kartu hasil, bukan timeline).

**Dampak**:
- Prediksi 7-hari ke depan masuk ke backlog (Sprint 7-Day Forecast).
- Frontend tidak perlu mengelola state timeline multi-hari.

---

## DEC-004 — AI Summary Dihapus dari PDF

**Tanggal**: 1 Juli 2026
**Sprint**: UI-AI-2

**Keputusan**: Dokumen cetak/PDF tidak menyertakan konten AI Decision Support.

**Alasan**:
- Percakapan AI bersifat exploratory dan tidak menjadi bagian dari output formal.
- Dokumen formal (skripsi, laporan pemerintah) tidak boleh mencantumkan output LLM tanpa verifikasi.
- AI tidak selalu digunakan — tidak semua pengguna membuka panel AI sebelum mencetak laporan.

**Dampak**:
- `PrintableReport.tsx` tidak menerima `aiSummary` prop.
- `ReportsPanel.tsx` tidak meneruskan data AI ke print window.
- PDF 3 halaman: Cover, Rekomendasi, Insights/Metadata.

---

## DEC-005 — Percakapan AI Dipisahkan Berdasarkan Wilayah + Tanggal

**Tanggal**: 1 Juli 2026
**Sprint**: UI-AI-2

**Keputusan**: Setiap percakapan AI di-key-kan dengan `{wilayah}_{forecast_date}`, bukan satu percakapan global.

**Alasan**:
- Mencampurkan percakapan Pekanbaru dan Kampar dalam satu thread membingungkan.
- Context LLM diinjeksi per prediksi — percakapan harus selaras dengan data prediksi yang benar.
- Pengguna dapat kembali ke wilayah sebelumnya dan melanjutkan percakapan yang sama.

**Implementasi**: `hooks/use-conversation-store.ts` dengan key `"Pekanbaru_2026-07-01"`.

---

## DEC-006 — Dark Theme sebagai Default

**Tanggal**: 28 Juni 2026
**Sprint**: UI-FREEZE-V2

**Keputusan**: Tema gelap (`dark`) adalah tema default aplikasi, bukan mengikuti preferensi sistem.

**Alasan**:
- Target audience (peneliti, dosen, stakeholder) lebih sering menggunakan aplikasi di dalam ruangan.
- Dark theme lebih cocok untuk aplikasi analitik premium (Vercel, Linear, Raycast).
- Background gelap `#07111F` menciptakan kontras yang lebih baik untuk visualisasi data.

**Dampak**:
- CSS variables default di `:root` adalah dark theme.
- Light theme tersedia di class `.light`.
- `useLocalStorage(STORAGE_KEYS.theme, "light")` — ada inkonsistensi kecil di settings (default "light" di selector, tapi tema default actual adalah dark). Ini dapat diperbaiki di masa depan.

---

## DEC-007 — Peta Selalu Aktif, Tidak Dapat Disembunyikan

**Tanggal**: 28 Juni 2026
**Sprint**: UI-FREEZE-V2

**Keputusan**: `MapContainer` selalu dirender di semua menu, tidak di-unmount saat berpindah panel.

**Alasan**:
- MapLibre memerlukan waktu inisialisasi yang signifikan — unmount/remount mahal secara performa.
- Peta adalah elemen identitas utama aplikasi (Sistem Pendukung Keputusan berbasis wilayah).
- Pengguna diharapkan selalu memiliki konteks geografis.

**Dampak**:
- Peta tidak hilang saat berpindah ke AI Support, Reports, Settings, atau About.
- ResizablePanel kiri tetap terisi konten aktif, peta di kanan tetap ada.

---

## DEC-008 — Sidebar Tidak Dapat Di-collapse

**Tanggal**: 28 Juni 2026
**Sprint**: UI-FREEZE-V2

**Keputusan**: Sidebar memiliki lebar tetap `72px` dan tidak dapat di-collapse menjadi lebih kecil.

**Alasan**:
- Layar target adalah desktop/laptop dengan resolusi ≥ 1280px.
- Icon-only sidebar (72px) sudah sangat kompak.
- Implementasi collapse menambah kompleksitas state yang tidak sepadan untuk MVP.

**Dampak**:
- `SIDEBAR_WIDTH = 80` dan `SIDEBAR_COLLAPSED_WIDTH = 48` ada di `constants.ts` sebagai persiapan, tapi belum diimplementasikan.

---

## DEC-009 — Tidak Menggunakan State Management Library Eksternal

**Tanggal**: 28 Juni 2026
**Sprint**: UI-FREEZE-V2

**Keputusan**: Tidak menggunakan Redux, Zustand, Jotai, atau sejenisnya. State dikelola dengan `useState`, `localStorage`, dan TanStack Query.

**Alasan**:
- Aplikasi SPA dengan satu halaman dan state relatif sederhana.
- TanStack Query menangani semua server state (fetching, caching, revalidation).
- `localStorage` menangani semua persistent client state.
- `useState` lokal cukup untuk UI state per komponen.

**Dampak**:
- Tidak ada store global yang perlu dipelajari developer baru.
- Semua state dapat ditelusuri langsung dari hooks.

---

## DEC-010 — LLM Dikonfigurasi via Environment Variable, Bukan UI

**Tanggal**: 29 Juni 2026
**Sprint**: UI-1

**Keputusan**: Provider LLM dan API key dikonfigurasi melalui `NEXT_PUBLIC_LLM_PROVIDER` dan `NEXT_PUBLIC_LLM_API_KEY`, bukan dari settings UI.

**Alasan**:
- Menyederhanakan UI (tidak perlu form API key di settings).
- Lebih aman untuk deployment (key tidak disimpan di localStorage).
- Untuk penelitian, provider dipilih sekali saat deployment.

**Catatan Keamanan**: `NEXT_PUBLIC_*` terekspos ke browser. Untuk produksi, LLM harus dipanggil dari backend proxy.

---

## DEC-011 — Print CSS Disimpan di `public/` sebagai Static File

**Tanggal**: 1 Juli 2026
**Sprint**: UI-REPORT-PDF

**Keputusan**: `print.css` di-serve dari `public/print-report.css` (static), bukan di-bundle ke JavaScript.

**Alasan**:
- Print window dibuka sebagai jendela browser terpisah — tidak memiliki akses ke bundle JS aplikasi.
- CSS harus dimuat via `<link rel="stylesheet">` di HTML skeleton print window.
- Tidak ada mekanisme native Next.js untuk mengekspos CSS module sebagai string ke client component (tidak ada `?raw` import).

**Dampak**:
- Setiap kali `components/report/print.css` diubah, file harus di-copy ke `public/print-report.css` secara manual.

---

## DEC-012 — Random Forest sebagai Model Default

**Tanggal**: 27 Juni 2026
**Sprint**: BIZ-3

**Keputusan**: Random Forest (`rf`) adalah model default, LSTM (`lstm`) tersedia sebagai alternatif via parameter.

**Alasan**:
- Random Forest lebih stabil untuk prediksi single-step tanpa window panjang.
- LSTM memerlukan minimal 7 data historis berurutan — bisa gagal jika history tidak tersedia.
- Random Forest inference lebih cepat (~milidetik vs LSTM yang memerlukan TensorFlow runtime).

**Dampak**:
- `model=rf` adalah default di semua endpoint.
- LSTM tersedia via `?model=lstm` untuk pengujian dan penelitian.
