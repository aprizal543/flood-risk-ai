# Realtime Prediction Test

## Test Date: 2026-06-28
## Endpoint: GET /api/prediksi/realtime

## Test Scenarios

### Scenario 1: Pekanbaru (Primary Target City)
```
GET /api/prediksi/realtime?wilayah=Pekanbaru
```
- [x] Geocoding resolves to ~0.507°N, 101.447°E
- [x] Weather data retrieved from Open-Meteo
- [x] Feature engineering applied (temp_range, rainfall_anomaly, calendar features)
- [x] RF prediction returns FRI [0-100]
- [x] Risk classification applied (Rendah/Sedang/Tinggi)
- [x] Recommendations generated
- [x] Mitigation actions returned

### Scenario 2: Multiple Indonesian Cities (Verified via mocked tests)
| City | Expected Behavior |
|------|------------------|
| Pekanbaru | Geocoding success, prediction complete |
| Jakarta | Geocoding success, prediction complete |
| Surabaya | Geocoding success, prediction complete |
| Medan | Geocoding success, prediction complete |

### Scenario 3: Error Handling
| Input | Expected |
|-------|----------|
| wilayah=XyzNotExist | 404 - Lokasi tidak ditemukan |
| (no wilayah param) | 422 - Parameter wajib |
| Provider timeout | 503 - Service unavailable |

## Automated Test Coverage
- test_realtime_success: Mocked provider, full pipeline verified
- test_realtime_location_not_found: 404 response
- test_realtime_provider_unavailable: 503 response
- test_realtime_missing_wilayah: 422 response

## Result: PASS
