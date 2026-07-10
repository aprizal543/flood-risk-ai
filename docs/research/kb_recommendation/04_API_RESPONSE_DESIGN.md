# Backend API Response Design

## 1. Design Principles

1. **Backward wire-compatible**: The existing `GET /api/prediksi/realtime` endpoint retains its URL, method, parameters, and authentication contract. No breaking changes to the request interface.
2. **Additive enrichment**: New fields are added alongside existing fields. No existing fields are removed or renamed.
3. **Progressive enhancement**: Frontend can adopt new fields incrementally. Old frontend versions continue to work.
4. **Self-documenting**: Response includes `knowledge_source` section clarifying provenance of each recommendation.

## 2. Current Response (Baseline)

```json
{
  "status": "berhasil",
  "wilayah": "Pekanbaru",
  "sumber_data": "Open-Meteo",
  "forecast_date": "2026-07-08",
  "updated_at": "2026-07-08T15:30:00+07:00",
  "waktu_prediksi": "2026-07-08T15:30:00+07:00",
  "model": "rf",
  "versi_model": "1.0",
  "RR": 12.5,
  "Rain7": 85.3,
  "RH_avg": 82.0,
  "Tavg": 28.5,
  "cuaca": { ... },
  "hari_historis": 13,
  "fri": 45.2,
  "tingkat_risiko": "Risiko Sedang",
  "rekomendasi": [...],
  "mitigasi": [...]
}
```

## 3. Future Response Design

### 3.1 New Top-Level Sections

| Section | Type | Required | Description |
|---------|------|----------|-------------|
| `ringkasan` | object | Yes | Executive summary of the recommendation |
| `rekomendasi` | array | Yes | Recommended commodities (category-aware) |
| `alternatif` | array | Yes | Alternative commodities with preconditions |
| `tidak_direkomendasikan` | array | Yes | Commodities to avoid |
| `mitigasi` | array | Yes | Mitigation actions (unchanged structure) |
| `sumber_pengetahuan` | object | Yes | Knowledge provenance information |

### 3.2 Complete Response Schema

```json
{
  "status": "berhasil",
  "wilayah": "Pekanbaru",
  "sumber_data": "Open-Meteo",
  "forecast_date": "2026-07-08",
  "updated_at": "2026-07-08T15:30:00+07:00",
  "waktu_prediksi": "2026-07-08T15:30:00+07:00",
  "model": "rf",
  "versi_model": "1.0",
  "RR": 12.5,
  "Rain7": 85.3,
  "RH_avg": 82.0,
  "Tavg": 28.5,
  "cuaca": { ... },
  "hari_historis": 13,
  "fri": 45.2,
  "tingkat_risiko": "Risiko Sedang",

  "ringkasan": {
    "keputusan_tanam": "tanam_dengan_pencegahan",
    "deskripsi": "Risiko meningkat. Pilih komoditas dengan toleransi banjir sedang hingga tinggi.",
    "jumlah_direkomendasikan": 7,
    "jumlah_alternatif": 2,
    "jumlah_tidak_direkomendasikan": 6,
    "peringatan": [
      "Hindari penanaman melon, semangka, tomat, dan jagung manis pada kondisi ini.",
      "Cabai rawit dan cabai merah hanya disarankan dengan bedengan tinggi."
    ]
  },

  "rekomendasi": [
    {
      "komoditas": "Kangkung",
      "komoditas_id": "kangkung",
      "kategori_rekomendasi": "direkomendasikan",
      "skor": 92.5,
      "tingkat_keyakinan": 0.95,
      "tingkat_risiko": "Risiko Sedang",
      "alasan": [
        "Memiliki toleransi banjir sangat tinggi — cocok untuk kondisi Risiko Sedang",
        "Masa panen singkat (25 hari) — mengurangi paparan risiko",
        "Tidak memerlukan drainase khusus"
      ],
      "ringkasan": "Kangkung sangat direkomendasikan karena memiliki toleransi banjir sangat tinggi dan sesuai dengan kondisi Risiko Sedang saat ini (FRI: 45).",
      "detail_komoditas": {
        "nama_ilmiah": "Ipomoea aquatica",
        "kategori": "sayuran_daun",
        "tingkat_kerentanan": "Sangat Tinggi",
        "toleransi_banjir": "Sangat Tinggi",
        "durasi_genangan_maksimal": ">7 hari",
        "kebutuhan_drainase": "Minimal",
        "durasi_tanam_hari": 25,
        "dampak_utama": [
          "Pertumbuhan subur di genangan",
          "Adaptasi semi-aquatic"
        ],
        "gejala_kerusakan": [
          "Tidak ada gejala kerusakan berarti"
        ],
        "prioritas_ekonomi": "Sangat Tinggi"
      },
      "rekomendasi_badge": {
        "label": "Sangat Direkomendasikan",
        "warna": "#22c55e",
        "icon": "check_circle"
      },
      "aturan_yang_diterapkan": [
        "R_M1: Kelompok toleransi A (Sangat Tinggi) lolos seleksi",
        "R_M5: Prioritas berdasarkan toleransi kemudian ekonomi"
      ]
    }
  ],

  "alternatif": [
    {
      "komoditas": "Cabai Rawit",
      "komoditas_id": "cabai_rawit",
      "kategori_rekomendasi": "alternatif",
      "skor": 62.0,
      "tingkat_keyakinan": 0.65,
      "tingkat_risiko": "Risiko Sedang",
      "alasan": [
        "Memiliki toleransi banjir sedang",
        "Nilai ekonomi tinggi",
        "Memerlukan drainase baik — perlu bedengan tinggi"
      ],
      "ringkasan": "Cabai rawit dapat dipertimbangkan dengan syarat menggunakan bedengan tinggi dan drainase yang baik.",
      "detail_komoditas": { ... },
      "rekomendasi_badge": {
        "label": "Alternatif (Dengan Syarat)",
        "warna": "#f59e0b",
        "icon": "warning"
      },
      "prasyarat": [
        "Gunakan bedengan setinggi minimal 30 cm",
        "Pastikan saluran drainase berfungsi baik",
        "Siapkan perlindungan mulsa plastik"
      ],
      "aturan_yang_diterapkan": [
        "R_M4: Kebutuhan drainase Tinggi — prasyarat bedengan diterapkan",
        "R_E1: Prioritas ekonomi tinggi mendorong ke kategori alternatif"
      ]
    }
  ],

  "tidak_direkomendasikan": [
    {
      "komoditas": "Melon",
      "komoditas_id": "melon",
      "kategori_rekomendasi": "tidak_direkomendasikan",
      "alasan_penolakan": [
        "Toleransi banjir sangat rendah — tidak cocok untuk Risiko Sedang",
        "Buah menyentuh tanah sangat rentan busuk pada kondisi lembab",
        "Memerlukan drainase sangat baik yang tidak terjamin"
      ],
      "detail_komoditas": { ... },
      "rekomendasi_badge": {
        "label": "Tidak Direkomendasikan",
        "warna": "#ef4444",
        "icon": "cancel"
      },
      "aturan_yang_diterapkan": [
        "R_M1: Kelompok toleransi E (Sangat Rendah) dieksklusi"
      ]
    }
  ],

  "mitigasi": [
    {
      "prioritas": 1,
      "kategori": "Drainase",
      "tindakan": "Pastikan semua saluran drainase bersih dari penyumbatan",
      "rekomendasi_spesifik": [
        "Kangkung: tidak perlu drainase khusus",
        "Cabai rawit: prioritas utama drainase"
      ]
    }
  ],

  "sumber_pengetahuan": {
    "versi_pengetahuan": "1.0",
    "versi_aturan": "1.0",
    "jumlah_komoditas": 17,
    "sumber_ilmiah": [
      {
        "komoditas": "Kangkung",
        "referensi": "FAO aquatic vegetable cultivation guides",
        "status": "Asumsi Penelitian"
      },
      {
        "komoditas": "Talas",
        "referensi": "Taro cultivation in Pacific/SE Asian wetlands",
        "status": "Asumsi Penelitian"
      }
    ],
    "keterangan": "Semua referensi ilmiah saat ini berstatus [Pending] dan akan diperbarui saat literatur telah direview."
  }
}
```

## 4. Pydantic Schema Changes

### 4.1 New Schemas to Add (no existing schema modified)

```python
class RekomendasiBadge(BaseModel):
    label: str
    warna: str
    icon: str

class DetailKomoditas(BaseModel):
    nama_ilmiah: str
    kategori: str
    tingkat_kerentanan: str
    toleransi_banjir: str
    durasi_genangan_maksimal: str
    kebutuhan_drainase: str
    durasi_tanam_hari: int
    dampak_utama: list[str]
    gejala_kerusakan: list[str]
    prioritas_ekonomi: str

class RekomendasiDetail(BaseModel):
    komoditas: str
    komoditas_id: str
    kategori_rekomendasi: str  # "direkomendasikan" | "alternatif" | "tidak_direkomendasikan"
    skor: float
    tingkat_keyakinan: float
    tingkat_risiko: str
    alasan: list[str]
    ringkasan: str
    detail_komoditas: DetailKomoditas
    rekomendasi_badge: RekomendasiBadge
    prasyarat: list[str] = []
    aturan_yang_diterapkan: list[str] = []

class RingkasanResponse(BaseModel):
    keputusan_tanam: str
    deskripsi: str
    jumlah_direkomendasikan: int
    jumlah_alternatif: int
    jumlah_tidak_direkomendasikan: int
    peringatan: list[str]

class SumberPengetahuan(BaseModel):
    versi_pengetahuan: str
    versi_aturan: str
    jumlah_komoditas: int
    sumber_ilmiah: list[dict]
    keterangan: str

class PrediksiResponseV2(BaseModel):
    # Inherits all existing fields from PrediksiResponseV1
    # Plus new sections:
    ringkasan: RingkasanResponse
    rekomendasi: list[RekomendasiDetail]  # Replaces PenjelasanResponse
    alternatif: list[RekomendasiDetail]
    tidak_direkomendasikan: list[RekomendasiDetail]
    mitigasi: list[TindakanMitigasiResponse]
    sumber_pengetahuan: SumberPengetahuan
```

### 4.2 Backward Compatibility Strategy

To ensure backward compatibility during migration:

1. **Phase 1 (KB Sprint 4)**: Add new fields; keep old fields populated
   - `rekomendasi` still contains `PenjelasanResponse[]` for backward compat
   - New `ringkasan`, `alternatif`, `tidak_direkomendasikan`, `sumber_pengetahuan` added alongside
   - Frontend can choose which fields to consume

2. **Phase 2 (KB Sprint 5)**: After frontend migration, deprecate old fields
   - Mark old `PenjelasanResponse` structure as deprecated in API docs
   - Old fields still returned but flagged

3. **Phase 3 (KB Sprint 6)**: Remove deprecated fields
   - Only `RekomendasiDetail` format remains

## 5. Response Field Mapping

| Current Field | New Field | Relationship |
|---------------|-----------|--------------|
| `rekomendasi[].komoditas` | `rekomendasi[].komoditas` | Same |
| `rekomendasi[].skor` | `rekomendasi[].skor` | Same |
| `rekomendasi[].tingkat_keyakinan` | `rekomendasi[].tingkat_keyakinan` | Same |
| `rekomendasi[].alasan` | `rekomendasi[].alasan` | Enhanced (rule-based) |
| `rekomendasi[].ringkasan` | `rekomendasi[].ringkasan` | Enhanced (contextual) |
| (not present) | `rekomendasi[].kategori_rekomendasi` | New — recommendation category |
| (not present) | `rekomendasi[].detail_komoditas` | New — full commodity detail |
| (not present) | `rekomendasi[].rekomendasi_badge` | New — UI badge instructions |
| (not present) | `rekomendasi[].prasyarat` | New — preconditions for alternative |
| (not present) | `rekomendasi[].aturan_yang_diterapkan` | New — rule traceability |
| (not present) | `ringkasan` | New — executive summary |
| (not present) | `alternatif` | New — alternative category |
| (not present) | `tidak_direkomendasikan` | New — explicit exclusions |
| (not present) | `sumber_pengetahuan` | New — knowledge provenance |

## 6. Example Scenarios

### 6.1 Low Risk Response

```json
{
  "ringkasan": {
    "keputusan_tanam": "tanam_normal",
    "deskripsi": "Kondisi normal. Semua komoditas tersedia.",
    "jumlah_direkomendasikan": 17,
    "jumlah_alternatif": 0,
    "jumlah_tidak_direkomendasikan": 0,
    "peringatan": []
  },
  "rekomendasi": [
    {
      "komoditas": "Kangkung",
      "kategori_rekomendasi": "direkomendasikan",
      "skor": 95.0,
      "rekomendasi_badge": { "label": "Sangat Direkomendasikan", "warna": "#22c55e", "icon": "check_circle" }
    }
  ],
  "alternatif": [],
  "tidak_direkomendasikan": [],
  "sumber_pengetahuan": { ... }
}
```

### 6.2 High Risk Response

```json
{
  "ringkasan": {
    "keputusan_tanam": "tunda_atau_lindungi",
    "deskripsi": "Risiko banjir signifikan. Hanya komoditas tahan banjir yang direkomendasikan.",
    "jumlah_direkomendasikan": 2,
    "jumlah_alternatif": 2,
    "jumlah_tidak_direkomendasikan": 13,
    "peringatan": [
      "Tunda penanaman baru sampai risiko banjir menurun.",
      "Jika terpaksa tanam, pilih kangkung atau talas.",
      "Bayam dan sawi hanya dengan bedengan tinggi dan drainase darurat."
    ]
  },
  "rekomendasi": [
    {
      "komoditas": "Kangkung",
      "kategori_rekomendasi": "direkomendasikan",
      "skor": 98.0,
      "rekomendasi_badge": { "label": "Sangat Direkomendasikan", "warna": "#22c55e", "icon": "check_circle" }
    },
    {
      "komoditas": "Talas",
      "kategori_rekomendasi": "direkomendasikan",
      "skor": 95.0,
      "rekomendasi_badge": { "label": "Direkomendasikan", "warna": "#22c55e", "icon": "check_circle" }
    }
  ],
  "alternatif": [
    {
      "komoditas": "Bayam",
      "kategori_rekomendasi": "alternatif",
      "skor": 65.0,
      "prasyarat": ["Bedengan tinggi minimal 30 cm", "Drainase darurat siap"]
    },
    {
      "komoditas": "Sawi Hijau",
      "kategori_rekomendasi": "alternatif",
      "skor": 60.0,
      "prasyarat": ["Bedengan tinggi minimal 30 cm", "Drainase darurat siap"]
    }
  ],
  "tidak_direkomendasikan": [
    { "komoditas": "Melon", "alasan_penolakan": ["Toleransi banjir sangat rendah"] },
    { "komoditas": "Semangka", "alasan_penolakan": ["Toleransi banjir sangat rendah"] }
  ]
}
```
