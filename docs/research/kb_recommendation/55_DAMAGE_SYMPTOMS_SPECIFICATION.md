# Sprint KB8.6 — Damage Symptoms Specification

**Date:** 2026-07-10
**Source:** Lecturer Recommendation Document (only valid source)

---

## Overview

All 22 commodities now carry `damage_symptoms` as an authoritative, structured field. Content is an exact copy of `gejala_kerusakan` from the lecturer document.

---

## Specification

```json
"damage_symptoms": [
  "<exact lecturer wording>",
  "<exact lecturer wording>"
]
```

### Requirements
- Array entries preserve lecturer wording verbatim
- No summaries or paraphrasing
- If multiple commodities share identical lecturer descriptions, wording is reused
- `damage_symptoms` is authoritative over legacy `catatan` / `recommendation_notes`
- Legacy `damage_symptoms` (deprecated) was fixed to match `gejala_kerusakan`

---

## Per-Commodity Symptoms

### Kelompok Kerentanan Tinggi — Sangat Rentan
Commodities: cabai, tomat, bawang_merah, kentang, paprika

```json
"damage_symptoms": [
  "Busuk akar akibat ketiadaan oksigen",
  "Daun menguning (klorosis)",
  "Layu mendadak (epinasti)",
  "Kematian total tanaman dalam hitungan hari"
]
```

### Kelompok Kerentanan Tinggi & Sedang — Rentan (24-48 jam)
Commodities: kubis, pakcoy, sawi, terong, mentimun, kacang_panjang

```json
"damage_symptoms": [
  "Pertumbuhan kerdil",
  "Bunga dan bakal buah rontok massal",
  "Serangan jamur patogen tanah (Phytophthora, Pythium)",
  "Stres perakaran",
  "Daun bagian bawah melungkur dan layu"
]
```

### Kelompok Kerentanan Tinggi & Sedang — Agak Toleran (48-72 jam)
Commodities: wortel, lobak

```json
"damage_symptoms": [
  "Umbi membusuk atau pecah di dalam tanah",
  "Daun bagian bawah rontok",
  "Kualitas umbi menurun drastis",
  "Busuk, pecah-pecah (cracking), bentuk abnormal"
]
```

### Kelompok Kerentanan Tinggi & Sedang — Agak Toleran (48-72 jam)
Commodities: labu_siam, buncis

```json
"damage_symptoms": [
  "Buah membusuk atau pecah",
  "Daun bagian bawah rontok",
  "Kualitas buah menurun drastis",
  "Busuk, pecah-pecah (cracking), bentuk abnormal"
]
```

### Kelompok Kerentanan Tinggi & Rendah — Akuatik (>72 jam)
Commodities: kangkung_air, genjer

```json
"damage_symptoms": [
  "Tidak menunjukkan gejala kerusakan berarti pada genangan",
  "Tumbuh optimal di lahan tergenang permanen"
]
```

### Kelompok Kerentanan Tinggi & Rendah — >72 jam (3-7 hari)
Commodities: selada_air, talas

```json
"damage_symptoms": [
  "Tidak menunjukkan gejala kerusakan berarti pada genangan hingga 3-7 hari",
  "Pucuk atau daun atas yang tenggelam sepenuhnya dapat menyebabkan kematian"
]
```

### Kelompok Kerentanan Sedang — Toleran Sedang (48-72 jam)
Commodity: seledri

```json
"damage_symptoms": [
  "Kualitas fisik menurun",
  "Busuk atau kerusakan jaringan pada genangan berkepanjangan"
]
```

### Kelompok Kerentanan Rendah — >72 jam (3-7 hari)
Commodity: pakis_sayur

```json
"damage_symptoms": [
  "Tidak menunjukkan gejala kerusakan berarti pada genangan hingga 3-7 hari",
  "Pucuk atau daun atas yang tenggelam sepenuhnya dapat menyebabkan kematian"
]
```

### Kelompok Kerentanan Rendah — Permanen (Akuatik)
Commodity: semanggi

```json
"damage_symptoms": [
  "Tidak menunjukkan gejala kerusakan pada genangan",
  "Membutuhkan genangan permanen untuk pertumbuhan maksimal"
]
```

---

## Validation Rules

- No null arrays
- No empty arrays
- No duplicated entries
- Wording must originate from lecturer document
- Every commodity must have at least 1 entry
