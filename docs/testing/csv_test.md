# CSV Prediction Test

## Test Date: 2026-06-28
## Endpoints: POST /api/prediksi/csv, POST /api/prediksi/csv/download

## Design

CSV endpoint predicts **only the latest date**. Historical rows provide context for rolling feature computation (rain3, rain7, rain14).

## Test Scenarios

### Scenario 1: Multi-row CSV (3 days history)
```csv
tanggal,rr,rh_avg,tmax,tmin
2026-01-01,5,75,33,24
2026-01-02,10,80,32,24
2026-01-03,30,88,30,25
```
- [x] Prediction for 2026-01-03 only
- [x] jumlah_baris_historis = 2
- [x] Rolling features computed from all 3 rows
- [x] Single FRI value returned

### Scenario 2: Single-row CSV
```csv
tanggal,rr,rh_avg,tmax,tmin
2026-01-01,15,82,31,24
```
- [x] Prediction for 2026-01-01
- [x] jumlah_baris_historis = 0
- [x] rain3 = rain7 = rain14 = rr (no history)

### Scenario 3: CSV with invalid rows
```csv
tanggal,rr,rh_avg,tmax,tmin
2026-01-01,10,80,32,24
bad,-1,110,20,30
2026-01-03,20,85,31,25
```
- [x] Invalid row silently skipped
- [x] Latest valid date (2026-01-03) predicted
- [x] Valid row used in history

### Scenario 4: CSV Download
- [x] Content-Type: text/csv
- [x] Header row + 1 data row
- [x] Columns: tanggal, fri, tingkat_risiko, komoditas_terbaik, tingkat_keyakinan

### Scenario 5: Error Cases
| Case | Expected |
|------|----------|
| Non-.csv file | 422 |
| Missing columns | 422 |
| All rows invalid | 422 |
| Empty file | 422 |

## Result: PASS
