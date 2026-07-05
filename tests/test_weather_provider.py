"""Unit tests untuk Weather Provider layer dengan mock HTTP."""

import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.dependencies.auth import get_current_user
from backend.providers.geocoding import geocode, GeoLocation
from backend.providers.openmeteo_provider import OpenMeteoProvider
from backend.providers.exceptions import LocationNotFoundError, ProviderConnectionError, WeatherProviderError
from backend.services.auth_service import AuthUser

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
        "temperature_2m_mean": [28.5],
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
        assert result.tavg == 28.5
        assert result.tmax == 33.0
        assert result.tmin == 24.0
        assert result.sumber == "Open-Meteo"

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_get_weather_incomplete_data(self, mock_geocode, mock_get):
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        incomplete = {"daily": {"time": [YESTERDAY], "precipitation_sum": [None],
                      "relative_humidity_2m_mean": [85], "temperature_2m_mean": [28],
                      "temperature_2m_max": [33], "temperature_2m_min": [24]}}
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
                latitude=0.507, longitude=101.447, sumber="Open-Meteo", tavg=27.5,
            )
            for i in range(14)
        ]
        mock_provider.get_weather_history.return_value = history
        app.dependency_overrides[get_current_user] = lambda: AuthUser(id="test-user", email="test@example.com")
        try:
            r = client.get("/api/prediksi/realtime", params={"wilayah": "Pekanbaru"})
        finally:
            app.dependency_overrides.pop(get_current_user, None)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "berhasil"
        assert data["wilayah"] == "Pekanbaru"
        assert "fri" in data
        assert "tingkat_risiko" in data
        assert "rekomendasi" in data
        assert "mitigasi" in data
        assert "cuaca" in data
        assert data["RR"] == 31.0
        assert data["Rain7"] == 175.0
        assert data["RH_avg"] == 80.0
        assert data["Tavg"] == 27.5
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


class TestFriV2FeatureEngineering:
    """Verify the FRI v2 feature vector without invoking model prediction."""

    def test_v2_feature_order_and_removed_features_absent(self):
        from ml.feature_engineering.builder import build_features_v2

        raw = {"tanggal": "2026-01-15", "rr": 10.0, "rh_avg": 80.0, "tavg": 27.5, "tmax": 32.0, "tmin": 24.0}
        history = [{"rr": 1.0}, {"rr": 2.0}, {"rr": 3.0}, {"rr": 4.0}, {"rr": 5.0}, {"rr": 6.0}, {"rr": 7.0}]
        df = build_features_v2(raw, history=history)

        assert list(df.columns) == ["RR", "Rain7", "RH_avg", "Tavg"]
        assert not {"Rain3", "Rain14", "TempRange", "RainfallAnomaly", "Month", "DayOfYear"}.intersection(df.columns)

    def test_v2_rain7_matches_training_methodology(self):
        from ml.feature_engineering.builder import build_features_v2

        raw = {"tanggal": "2026-01-15", "rr": 10.0, "rh_avg": 80.0, "tavg": 27.5, "tmax": 32.0, "tmin": 24.0}
        history = [{"rr": 1.0}, {"rr": 2.0}, {"rr": 3.0}, {"rr": 4.0}, {"rr": 5.0}, {"rr": 6.0}, {"rr": 7.0}]
        df = build_features_v2(raw, history=history)

        assert df["Rain7"].iloc[0] == 37.0

    def test_gateway_builds_v2_features_without_prediction(self):
        from datetime import date as d
        from backend.providers.models import RawWeatherData
        from backend.services.prediction_gateway import build_prediction_features_v2

        weather = RawWeatherData(
            tanggal=d(2026, 1, 15), rr=10.0, rh_avg=80.0,
            tmax=32.0, tmin=24.0, latitude=0.5, longitude=101.4,
            sumber="test", tavg=27.5,
        )
        history = [{"rr": 1.0}, {"rr": 2.0}, {"rr": 3.0}, {"rr": 4.0}, {"rr": 5.0}, {"rr": 6.0}, {"rr": 7.0}]

        features = build_prediction_features_v2(weather, history=history)
        assert list(features.keys()) == ["RR", "Rain7", "RH_avg", "Tavg"]
        assert features == {"RR": 10.0, "Rain7": 37.0, "RH_avg": 80.0, "Tavg": 27.5}


class TestFriV2RandomForestCompatibility:
    """Verify RF v2 artifact and runtime feature metadata are compatible."""

    def test_runtime_feature_list_matches_rf_v2_artifact(self):
        import joblib
        from ml.predict.preprocess import ARTIFACTS_DIR, get_feature_list

        features = get_feature_list()
        model = joblib.load(ARTIFACTS_DIR / "random_forest_v2.pkl")

        assert features == ["RR", "Rain7", "RH_avg", "Tavg"]
        assert len(features) == 4
        assert list(model.feature_names_in_) == features
        assert model.n_features_in_ == 4

    def test_rf_loader_uses_v2_artifact(self, monkeypatch):
        from ml.predict import random_forest

        loaded_paths = []

        class DummyModel:
            def predict(self, df):
                return [42.0]

        def fake_load(path):
            loaded_paths.append(path.name)
            return DummyModel()

        monkeypatch.setattr(random_forest, "_model", None)
        monkeypatch.setattr(random_forest.joblib, "load", fake_load)

        result = random_forest.predict_rf(None)

        assert result == 42.0
        assert loaded_paths == ["random_forest_v2.pkl"]

    def test_rf_v2_smoke_prediction(self):
        from ml.service.predictor import prediksi

        features = {"RR": 10.0, "Rain7": 37.0, "RH_avg": 80.0, "Tavg": 27.5}

        result = prediksi(features, model="rf", top_n=1)

        assert result["model"] == "rf"
        assert isinstance(result["fri"], float)
        assert "tingkat_risiko" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
