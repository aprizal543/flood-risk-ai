# Flood Risk Index (FRI)

FRI adalah indeks risiko banjir untuk lahan hortikultura dengan skala 0–100.

## Klasifikasi

| FRI | Level | Tindakan |
|-----|-------|----------|
| 0–33 | Rendah | Tanam normal tanpa pencegahan khusus |
| 34–66 | Sedang | Tanam dengan pencegahan (drainase, mulsa) |
| 67–100 | Tinggi | Tunda penanaman atau lindungi tanaman |

## Faktor Penentu

- **Curah hujan (rr)**: Faktor dominan. >50mm/hari = risiko tinggi.
- **Akumulasi hujan 3/7/14 hari**: Mendeteksi saturasi tanah.
- **Kelembapan (rh_avg)**: >90% meningkatkan kerentanan.
- **Rentang suhu (temp_range)**: Indikator stabilitas cuaca.
- **Anomali curah hujan**: Deviasi dari rata-rata musiman.

## Model

Random Forest Regressor dengan 100 decision trees, 9 fitur input.
