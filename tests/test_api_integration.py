"""Integration tests for the Flood Risk DSS API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)

BASE_PAYLOAD = {
    "tanggal": "2026-01-15",
    "rr": 25.0,
    "rh_avg": 85.0,
    "tmax": 33.0,
    "tmin": 24.0,
}


class TestPredictionGateway:
    def test_gateway_direct(self):
        """Test gateway langsung tanpa HTTP."""
        from datetime import date as d
        from backend.providers.models import RawWeatherData
        from backend.services.prediction_gateway import predict_from_raw

        weather = RawWeatherData(
            tanggal=d(2026, 1, 15), rr=30.0, rh_avg=88.0,
            tmax=31.0, tmin=24.0, latitude=0.5, longitude=101.4, sumber="test",
        )
        result = predict_from_raw(weather, model="rf", top_n=3)
        assert "fri" in result
        assert "tingkat_risiko" in result
        assert "rekomendasi" in result
        assert "mitigasi" in result
        assert 0 <= result["fri"] <= 100

    def test_gateway_with_history(self):
        from datetime import date as d
        from backend.providers.models import RawWeatherData
        from backend.services.prediction_gateway import predict_from_raw

        weather = RawWeatherData(
            tanggal=d(2026, 1, 15), rr=40.0, rh_avg=90.0,
            tmax=30.0, tmin=25.0, latitude=0.5, longitude=101.4, sumber="test",
        )
        history = [{"rr": 10.0}, {"rr": 20.0}, {"rr": 15.0}]
        result = predict_from_raw(weather, history=history, model="rf", top_n=2)
        assert 0 <= result["fri"] <= 100


class TestHealthEndpoint:
    def test_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "sehat"


class TestValidPrediction:
    def test_valid_request(self):
        r = client.post("/api/prediksi/manual", json=BASE_PAYLOAD)
        assert r.status_code == 200
        data = r.json()
        assert "fri" in data
        assert "tingkat_risiko" in data
        assert "rekomendasi" in data
        assert "mitigasi" in data
        assert 0 <= data["fri"] <= 100

    def test_low_risk_scenario(self):
        payload = {**BASE_PAYLOAD, "rr": 0.0, "rh_avg": 65.0, "tmax": 35.0, "tmin": 23.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 200
        assert r.json()["tingkat_risiko"] == "Risiko Rendah"

    def test_medium_risk_scenario(self):
        payload = {**BASE_PAYLOAD, "rr": 25.0, "rh_avg": 85.0, "tmax": 30.0, "tmin": 24.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 200
        assert r.json()["tingkat_risiko"] in ("Risiko Sedang", "Risiko Tinggi")

    def test_high_risk_scenario(self):
        payload = {**BASE_PAYLOAD, "rr": 80.0, "rh_avg": 95.0, "tmax": 28.0, "tmin": 25.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 200
        assert r.json()["tingkat_risiko"] in ("Risiko Sedang", "Risiko Tinggi")


class TestValidationErrors:
    def test_negative_rainfall(self):
        payload = {**BASE_PAYLOAD, "rr": -5.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422
        assert r.json()["status"] == "error"
        assert r.json()["kode"] == 422

    def test_invalid_humidity_over_100(self):
        payload = {**BASE_PAYLOAD, "rh_avg": 110.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422

    def test_invalid_humidity_negative(self):
        payload = {**BASE_PAYLOAD, "rh_avg": -5.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422

    def test_tmax_lower_than_tmin(self):
        payload = {**BASE_PAYLOAD, "tmax": 20.0, "tmin": 30.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422
        assert "tmax" in r.json()["pesan"].lower() or "suhu" in r.json()["pesan"].lower()

    def test_future_date(self):
        payload = {**BASE_PAYLOAD, "tanggal": "2030-12-31"}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422
        assert "masa depan" in r.json()["pesan"].lower() or "future" in r.json()["pesan"].lower()

    def test_invalid_date_format(self):
        payload = {**BASE_PAYLOAD, "tanggal": "15-01-2026"}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422

    def test_missing_required_field(self):
        payload = {"tanggal": "2026-01-15", "rr": 10.0}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422
        assert r.json()["status"] == "error"

    def test_invalid_data_type(self):
        payload = {**BASE_PAYLOAD, "rr": "bukan_angka"}
        r = client.post("/api/prediksi/manual", json=payload)
        assert r.status_code == 422


class TestInfoEndpoints:
    def test_model_info(self):
        r = client.get("/api/info/model")
        assert r.status_code == 200
        data = r.json()
        assert data["jumlah_fitur"] == 9
        assert len(data["nama_fitur"]) == 9
        assert "status_artifact" in data

    def test_version_info(self):
        r = client.get("/api/info/version")
        assert r.status_code == 200
        data = r.json()
        assert "versi" in data
        assert "python_version" in data

    def test_health_detail(self):
        r = client.get("/api/health/detail")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "sehat"
        assert "komponen" in data
        assert data["komponen"]["random_forest"] == "sehat"


class TestCSVEndpoint:
    def test_valid_csv_single_prediction(self):
        csv = "tanggal,rr,rh_avg,tmax,tmin\n2026-01-01,5,75,33,24\n2026-01-02,10,80,32,24\n2026-01-03,30,88,30,25\n"
        r = client.post("/api/prediksi/csv", files={"file": ("t.csv", csv, "text/csv")})
        assert r.status_code == 200
        data = r.json()
        # Only predicts the latest date
        assert data["tanggal"] == "2026-01-03"
        assert "fri" in data
        assert "tingkat_risiko" in data
        assert "rekomendasi" in data
        assert "mitigasi" in data
        assert data["jumlah_baris_historis"] == 2

    def test_csv_single_row(self):
        csv = "tanggal,rr,rh_avg,tmax,tmin\n2026-01-01,15,82,31,24\n"
        r = client.post("/api/prediksi/csv", files={"file": ("t.csv", csv, "text/csv")})
        assert r.status_code == 200
        assert r.json()["jumlah_baris_historis"] == 0

    def test_csv_skips_invalid_rows(self):
        csv = "tanggal,rr,rh_avg,tmax,tmin\n2026-01-01,10,80,32,24\nbad,-1,110,20,30\n2026-01-03,20,85,31,25\n"
        r = client.post("/api/prediksi/csv", files={"file": ("t.csv", csv, "text/csv")})
        assert r.status_code == 200
        # Invalid row skipped; latest valid = 2026-01-03
        assert r.json()["tanggal"] == "2026-01-03"

    def test_non_csv_file(self):
        r = client.post("/api/prediksi/csv", files={"file": ("t.txt", "hello", "text/plain")})
        assert r.status_code == 422

    def test_missing_columns(self):
        csv = "tanggal,rr\n2026-01-01,5\n"
        r = client.post("/api/prediksi/csv", files={"file": ("t.csv", csv, "text/csv")})
        assert r.status_code == 422

    def test_csv_download(self):
        csv = "tanggal,rr,rh_avg,tmax,tmin\n2026-01-01,5,75,33,24\n2026-01-02,20,85,31,24\n"
        r = client.post("/api/prediksi/csv/download", files={"file": ("t.csv", csv, "text/csv")})
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        # Should contain header + 1 data row
        lines = r.text.strip().split("\n")
        assert len(lines) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
