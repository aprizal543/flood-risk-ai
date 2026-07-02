# API Acceptance Test

## Test Date: 2026-06-28
## Version: 1.0.0-rc

## Endpoints Tested

### GET /api/health
- [x] Returns 200
- [x] Response: `{"status": "sehat", "versi": "1.0.0"}`

### GET /api/health/detail
- [x] Returns 200
- [x] All components "sehat"
- [x] Returns uptime_detik

### GET /api/info/model
- [x] Returns 200
- [x] jumlah_fitur = 9
- [x] All artifact status "tersedia"

### GET /api/info/version
- [x] Returns 200
- [x] Contains python_version, fastapi_version

### POST /api/prediksi/manual
- [x] Valid request returns 200
- [x] Response contains fri, tingkat_risiko, rekomendasi, mitigasi
- [x] FRI bounded [0, 100]
- [x] Invalid tanggal returns 422
- [x] Future date returns 422
- [x] Negative rr returns 422
- [x] rh_avg > 100 returns 422
- [x] tmax < tmin returns 422
- [x] Missing field returns 422

### POST /api/prediksi/engineered
- [x] Valid request returns 200
- [x] Response matches PrediksiResponse schema

### POST /api/prediksi/csv
- [x] Valid CSV returns single prediction for latest date
- [x] History used for rolling features
- [x] Invalid rows silently skipped
- [x] Non-CSV file returns 422
- [x] Missing columns returns 422

### POST /api/prediksi/csv/download
- [x] Returns text/csv content-type
- [x] Contains exactly 1 data row

### GET /api/prediksi/realtime
- [x] Valid wilayah returns 200 (mocked)
- [x] Unknown wilayah returns 404
- [x] Provider timeout returns 503
- [x] Missing wilayah returns 422

### GET /api/provider/openmeteo
- [x] Valid wilayah returns weather data (mocked)
- [x] Unknown wilayah returns 404
- [x] Connection error returns 502

## Result: PASS (38/38 automated tests)
