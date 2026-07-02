# OpenAPI / Swagger Documentation Test

## Test Date: 2026-06-28
## URL: http://localhost:8000/docs

## Audit Checklist

### Application Metadata
- [x] Title: "Flood Risk DSS API"
- [x] Description includes system purpose
- [x] Version: 1.0.0

### Endpoint Documentation
| Endpoint | Summary | Description | Tags |
|----------|---------|-------------|------|
| GET /api/health | ✅ | ✅ | Health |
| GET /api/health/detail | ✅ | ✅ | Info & Monitoring |
| GET /api/info/model | ✅ | ✅ | Info & Monitoring |
| GET /api/info/version | ✅ | ✅ | Info & Monitoring |
| POST /api/prediksi/manual | ✅ | ✅ | Prediksi |
| POST /api/prediksi/engineered | ✅ | ✅ | Prediksi |
| POST /api/prediksi/csv | ✅ | ✅ | Prediksi CSV |
| POST /api/prediksi/csv/download | ✅ | ✅ | Prediksi CSV |
| GET /api/prediksi/realtime | ✅ | ✅ | Prediksi Realtime |
| GET /api/provider/openmeteo | ✅ | ✅ | Provider Cuaca |

### Request Schema Documentation
- [x] PrediksiManualRequest: All fields have descriptions and examples
- [x] PrediksiEngineeredRequest: All fields have descriptions
- [x] Validation constraints visible (ge, le, pattern)

### Response Schema Documentation
- [x] PrediksiResponse defined
- [x] HealthResponse defined
- [x] ErrorResponse defined (status, kode, pesan)

### Error Responses
- [x] 422 responses documented on prediction endpoints
- [x] 501 documented (removed - CSV now implemented)
- [x] Error format consistent: `{"status":"error","kode":...,"pesan":"..."}`

## Result: PASS
