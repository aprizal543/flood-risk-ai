"""Unit tests untuk Weather Provider layer dengan mock HTTP."""

import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.providers.geocoding import geocode, GeoLocation
from backend.providers.openmeteo_provider import OpenMeteoProvider
from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError, WeatherProviderError

client = TestClient(app)

MOCK_GEOCODING_RESPONSE = {
    "results": [{"latitude": 0.507, "longitude": 101.447, "name": "Pekanbaru"}]
}

YESTERDAY = (date.today() - timedelta(days=1)).isoformat()

MOCK_WEATHER_RESPONSE = {
    "daily": {
        "time": [YESTERDAY],
        "precipitation_sum": [12.5],
        "relative_humidity_2m_mean": [85.0],
        "temperature_2m_max": [33.0],
        "temperature_2m_min": [24.0],
    }
}


class TestGeocoding:
    @patch("backend.providers.geocoding.requests.get")
    def test_geocode_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_GEOCODING_RESPONSE)
        mock_get.return_value.raise_for_status = MagicMock()
        result = geocode("Pekanbaru")
        assert isinstance(result, GeoLocation)
        assert result.latitude == 0.507
        assert result.name == "Pekanbaru"

    @patch("backend.providers.geocoding.requests.get")
    def test_geocode_not_found(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"results": None})
        mock_get.return_value.raise_for_status = MagicMock()
        with pytest.raises(LocationNotFoundError):
            geocode("XyzNotExist")

    @patch("backend.providers.geocoding.requests.get")
    def test_geocode_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("timeout")
        with pytest.raises(ProviderConnectionError):
            geocode("Pekanbaru")


class TestOpenMeteoProvider:
    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_get_current_weather_success(self, mock_geocode, mock_get):
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        mock_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_WEATHER_RESPONSE)
        mock_get.return_value.raise_for_status = MagicMock()

        provider = OpenMeteoProvider()
        result = provider.get_current_weather("Pekanbaru")
        assert result.rr == 12.5
        assert result.rh_avg == 85.0
        assert result.tmax == 33.0
        assert result.tmin == 24.0
        assert result.sumber == "Open-Meteo"

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_get_weather_incomplete_data(self, mock_geocode, mock_get):
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        incomplete = {"daily": {"time": [YESTERDAY], "precipitation_sum": [None],
                      "relative_humidity_2m_mean": [85], "temperature_2m_max": [33], "temperature_2m_min": [24]}}
        mock_get.return_value = MagicMock(status_code=200, json=lambda: incomplete)
        mock_get.return_value.raise_for_status = MagicMock()

        provider = OpenMeteoProvider()
        with pytest.raises(WeatherProviderError, match="tidak lengkap"):
            provider.get_current_weather("Pekanbaru")

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_get_weather_connection_error(self, mock_geocode, mock_get):
        import requests
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        mock_get.side_effect = requests.ConnectionError("refused")

        provider = OpenMeteoProvider()
        with pytest.raises(ProviderConnectionError):
            provider.get_current_weather("Pekanbaru")


class TestProviderEndpoint:
    @patch("backend.routers.provider._provider")
    def test_endpoint_success(self, mock_provider):
        from backend.providers.models import RawWeatherData
        mock_provider.get_current_weather.return_value = RawWeatherData(
            tanggal=date.today() - timedelta(days=1),
            rr=10.0, rh_avg=82.0, tmax=32.0, tmin=23.0,
            latitude=0.507, longitude=101.447, sumber="Open-Meteo",
        )
        r = client.get("/api/provider/openmeteo", params={"wilayah": "Pekanbaru"})
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "berhasil"
        assert data["rr"] == 10.0
        assert data["sumber"] == "Open-Meteo"

    @patch("backend.routers.provider._provider")
    def test_endpoint_location_not_found(self, mock_provider):
        mock_provider.get_current_weather.side_effect = LocationNotFoundError("Tidak ditemukan")
        r = client.get("/api/provider/openmeteo", params={"wilayah": "XyzNotExist"})
        assert r.status_code == 404

    @patch("backend.routers.provider._provider")
    def test_endpoint_connection_error(self, mock_provider):
        mock_provider.get_current_weather.side_effect = ProviderConnectionError("Timeout")
        r = client.get("/api/provider/openmeteo", params={"wilayah": "Pekanbaru"})
        assert r.status_code == 502

    def test_endpoint_missing_param(self):
        r = client.get("/api/provider/openmeteo")
        assert r.status_code == 422


class TestRealtimeEndpoint:
    @patch("backend.routers.realtime._provider")
    def test_realtime_success(self, mock_provider):
        from backend.providers.models import RawWeatherData
        # Build 14 days of history
        history = [
            RawWeatherData(
                tanggal=date.today() - timedelta(days=14 - i),
                rr=float(5 + i * 2), rh_avg=80.0, tmax=32.0, tmin=24.0,
                latitude=0.507, longitude=101.447, sumber="Open-Meteo",
            )
            for i in range(14)
        ]
        mock_provider.get_weather_history.return_value = history
        r = client.get("/api/prediksi/realtime", params={"wilayah": "Pekanbaru"})
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "berhasil"
        assert data["wilayah"] == "Pekanbaru"
        assert "fri" in data
        assert "tingkat_risiko" in data
        assert "rekomendasi" in data
        assert "mitigasi" in data
        assert "cuaca" in data
        assert data["sumber_data"] == "Open-Meteo"
        assert data["hari_historis"] == 13

    @patch("backend.routers.realtime._provider")
    def test_realtime_location_not_found(self, mock_provider):
        mock_provider.get_weather_history.side_effect = LocationNotFoundError("Tidak ditemukan")
        r = client.get("/api/prediksi/realtime", params={"wilayah": "XyzNotExist"})
        assert r.status_code == 404

    @patch("backend.routers.realtime._provider")
    def test_realtime_provider_unavailable(self, mock_provider):
        mock_provider.get_weather_history.side_effect = ProviderConnectionError("Timeout")
        r = client.get("/api/prediksi/realtime", params={"wilayah": "Pekanbaru"})
        assert r.status_code == 503

    def test_realtime_missing_wilayah(self):
        r = client.get("/api/prediksi/realtime")
        assert r.status_code == 422


class TestHistoricalFeatures:
    """Verify rolling features are computed correctly from history."""

    def test_rolling_rain3(self):
        """rain3 should sum last 3 days including current."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from ml.feature_engineering.builder import build_features

        raw = {"tanggal": "2026-01-15", "rr": 10.0, "rh_avg": 80.0, "tmax": 32.0, "tmin": 24.0}
        history = [{"rr": 5.0}, {"rr": 8.0}, {"rr": 12.0}]  # 3 preceding days
        df = build_features(raw, history=history)
        # rain3 = sum of last 3 in [5, 8, 12, 10] = 12 + 10 + 8... wait:
        # Series: [5, 8, 12, 10], rolling(3).sum() on last = 8+12+10 = 30
        # Actually rolling(3, min_periods=1) on index 3 = index[1]+[2]+[3] = 8+12+10
        assert df["rain3"].iloc[0] == 30.0

    def test_rolling_rain7(self):
        """rain7 should sum last 7 days including current."""
        from ml.feature_engineering.builder import build_features

        raw = {"tanggal": "2026-01-15", "rr": 10.0, "rh_avg": 80.0, "tmax": 32.0, "tmin": 24.0}
        history = [{"rr": 1.0}, {"rr": 2.0}, {"rr": 3.0}, {"rr": 4.0},
                   {"rr": 5.0}, {"rr": 6.0}, {"rr": 7.0}]  # 7 preceding days
        df = build_features(raw, history=history)
        # Series: [1,2,3,4,5,6,7,10], rolling(7) on last = 2+3+4+5+6+7+10 = 37
        assert df["rain7"].iloc[0] == 37.0

    def test_rolling_rain14(self):
        """rain14 should sum last 14 days including current."""
        from ml.feature_engineering.builder import build_features

        raw = {"tanggal": "2026-01-15", "rr": 10.0, "rh_avg": 80.0, "tmax": 32.0, "tmin": 24.0}
        history = [{"rr": float(i)} for i in range(1, 14)]  # 13 preceding days: 1..13
        df = build_features(raw, history=history)
        # Series: [1,2,...,13,10], rolling(14) = sum of all 14 = (1+2+...+13)+10 = 91+10 = 101
        expected = sum(range(1, 14)) + 10.0
        assert df["rain14"].iloc[0] == expected

    def test_no_history_uses_rr(self):
        """Without history, rain3/7/14 should equal rr."""
        from ml.feature_engineering.builder import build_features

        raw = {"tanggal": "2026-01-15", "rr": 25.0, "rh_avg": 80.0, "tmax": 32.0, "tmin": 24.0}
        df = build_features(raw, history=None)
        assert df["rain3"].iloc[0] == 25.0
        assert df["rain7"].iloc[0] == 25.0
        assert df["rain14"].iloc[0] == 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
