"""Regression tests for weather caching layer.

Verifies:
- Repeated requests use cache (no HTTP)
- TTL expiration works
- Different cities create separate cache entries
- Prediction output is bit-identical before and after cache
- Cache metrics are accurate
"""

import sys
import time
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from backend.cache import CacheMetrics, ThreadSafeCache
from backend.providers.geocoding import (
    GeoLocation,
    geocode,
    geocoding_cache,
    geocoding_metrics,
)
from backend.providers.openmeteo_provider import (
    OpenMeteoProvider,
    forecast_cache,
    forecast_metrics,
)

YESTERDAY = (date.today() - timedelta(days=1)).isoformat()

MOCK_GEOCODING_RESPONSE = {
    "results": [{"latitude": 0.507, "longitude": 101.447, "name": "Pekanbaru"}]
}

MOCK_GEOCODING_RESPONSE_DUMAI = {
    "results": [{"latitude": 1.667, "longitude": 101.467, "name": "Dumai"}]
}

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


@pytest.fixture(autouse=True)
def clear_caches():
    geocoding_cache.clear()
    forecast_cache.clear()
    yield


# ── ThreadSafeCache unit tests ───────────────────────────────────────


class TestThreadSafeCache:
    def test_set_and_get(self):
        cache: ThreadSafeCache[str] = ThreadSafeCache(maxsize=10, ttl=3600)
        cache.set("k1", "v1")
        assert cache.get("k1") == "v1"

    def test_get_missing(self):
        cache: ThreadSafeCache[str] = ThreadSafeCache(maxsize=10, ttl=3600)
        assert cache.get("missing") is None

    def test_size(self):
        cache: ThreadSafeCache[str] = ThreadSafeCache(maxsize=10, ttl=3600)
        assert cache.size == 0
        cache.set("a", "1")
        assert cache.size == 1

    def test_clear(self):
        cache: ThreadSafeCache[str] = ThreadSafeCache(maxsize=10, ttl=3600)
        cache.set("a", "1")
        cache.clear()
        assert cache.size == 0
        assert cache.get("a") is None

    def test_maxsize(self):
        cache: ThreadSafeCache[int] = ThreadSafeCache(maxsize=2, ttl=3600)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.size <= 2

    def test_ttl_expiry(self):
        cache: ThreadSafeCache[str] = ThreadSafeCache(maxsize=10, ttl=1)
        cache.set("k", "v")
        assert cache.get("k") == "v"
        time.sleep(1.1)
        assert cache.get("k") is None


# ── CacheMetrics unit tests ──────────────────────────────────────────


class TestCacheMetrics:
    def test_initial_state(self):
        m = CacheMetrics()
        assert m.hits == 0
        assert m.misses == 0
        assert m.total == 0
        assert m.hit_rate == 0.0

    def test_hit(self):
        m = CacheMetrics()
        m.hit()
        assert m.hits == 1
        assert m.total == 1

    def test_miss(self):
        m = CacheMetrics()
        m.miss()
        assert m.misses == 1
        assert m.total == 1

    def test_hit_rate(self):
        m = CacheMetrics()
        m.hit()
        m.hit()
        m.miss()
        assert m.hit_rate == pytest.approx(0.6667, rel=1e-3)

    def test_snapshot(self):
        m = CacheMetrics()
        m.hit()
        snap = m.snapshot()
        assert snap["hits"] == 1
        assert snap["misses"] == 0
        assert snap["hit_rate"] == 1.0


# ── Geocoding cache integration ──────────────────────────────────────


class TestGeocodingCache:
    @patch("backend.providers.geocoding.requests.get")
    def test_first_request_is_miss_second_is_hit(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_GEOCODING_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        # First request — should be a cache MISS
        geo_metrics_before = geocoding_metrics.hits, geocoding_metrics.misses
        r1 = geocode("Pekanbaru")
        assert r1.latitude == 0.507
        assert mock_get.call_count == 1

        # Second request — should be a cache HIT, no HTTP
        r2 = geocode("Pekanbaru")
        assert r2.latitude == 0.507
        assert r2.longitude == 101.447
        assert r2.name == "Pekanbaru"
        assert mock_get.call_count == 1  # No additional HTTP call

    @patch("backend.providers.geocoding.requests.get")
    def test_different_cities_create_separate_entries(self, mock_get):
        def side_effect(*args, **kwargs):
            name = kwargs.get("params", {}).get("name", "")
            if name == "Pekanbaru":
                resp = MagicMock(
                    status_code=200, json=lambda: MOCK_GEOCODING_RESPONSE
                )
            elif name == "Dumai":
                resp = MagicMock(
                    status_code=200, json=lambda: MOCK_GEOCODING_RESPONSE_DUMAI
                )
            else:
                resp = MagicMock(status_code=200, json=lambda: {"results": None})
            resp.raise_for_status = MagicMock()
            return resp

        mock_get.side_effect = side_effect

        r1 = geocode("Pekanbaru")
        r2 = geocode("Dumai")
        assert r1.latitude == 0.507
        assert r2.latitude == 1.667
        assert mock_get.call_count == 2

        # Both should now be cached
        r3 = geocode("Pekanbaru")
        r4 = geocode("Dumai")
        assert mock_get.call_count == 2  # No additional calls
        assert r3.latitude == 0.507
        assert r4.latitude == 1.667

    @patch("backend.providers.geocoding.requests.get")
    def test_case_insensitive_cache_key(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_GEOCODING_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        r1 = geocode("  Pekanbaru  ")
        assert mock_get.call_count == 1

        r2 = geocode("pekanbaru")
        assert mock_get.call_count == 1  # Cached

        r3 = geocode("PEKANBARU")
        assert mock_get.call_count == 1  # Cached

        assert r1.latitude == r2.latitude == r3.latitude

    @patch("backend.providers.geocoding.requests.get")
    def test_cache_metrics_updated(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_GEOCODING_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        hits_before = geocoding_metrics.hits
        misses_before = geocoding_metrics.misses

        geocode("Pekanbaru")
        assert geocoding_metrics.misses == misses_before + 1

        geocode("Pekanbaru")
        assert geocoding_metrics.hits == hits_before + 1


# ── Forecast cache integration ───────────────────────────────────────


class TestForecastCache:
    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_first_request_is_miss_second_is_hit(self, mock_geocode, mock_get):
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_WEATHER_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        provider = OpenMeteoProvider()

        # First request — cache MISS
        r1 = provider.get_current_weather("Pekanbaru")
        assert r1.rr == 12.5
        assert mock_get.call_count == 1

        # Second request — cache HIT, no HTTP
        r2 = provider.get_current_weather("Pekanbaru")
        assert r2.rr == 12.5
        assert r2.tavg == 28.5
        assert mock_get.call_count == 1  # No additional HTTP

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_different_cities_cached_separately(self, mock_geocode, mock_get):
        def geo_side(wilayah):
            if wilayah == "Pekanbaru":
                return GeoLocation(0.507, 101.447, "Pekanbaru")
            return GeoLocation(-6.208, 106.845, "Jakarta")

        mock_geocode.side_effect = geo_side

        response_pekanbaru = dict(MOCK_WEATHER_RESPONSE)
        response_jakarta = {
            "daily": {
                "time": [YESTERDAY],
                "precipitation_sum": [5.0],
                "relative_humidity_2m_mean": [78.0],
                "temperature_2m_mean": [30.0],
                "temperature_2m_max": [35.0],
                "temperature_2m_min": [26.0],
            }
        }

        def http_side(*args, **kwargs):
            params = kwargs.get("params", {})
            lat = params.get("latitude")
            if lat == 0.507:
                resp = MagicMock(status_code=200, json=lambda: response_pekanbaru)
            else:
                resp = MagicMock(status_code=200, json=lambda: response_jakarta)
            resp.raise_for_status = MagicMock()
            return resp

        mock_get.side_effect = http_side

        provider = OpenMeteoProvider()
        r1 = provider.get_current_weather("Pekanbaru")
        r2 = provider.get_current_weather("Jakarta")
        assert mock_get.call_count == 2
        assert r1.rr == 12.5
        assert r2.rr == 5.0

        # Both cached now
        r3 = provider.get_current_weather("Pekanbaru")
        r4 = provider.get_current_weather("Jakarta")
        assert mock_get.call_count == 2
        assert r3.rr == 12.5
        assert r4.rr == 5.0

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_forecast_cache_metrics(self, mock_geocode, mock_get):
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_WEATHER_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        provider = OpenMeteoProvider()
        hits_before = forecast_metrics.hits
        misses_before = forecast_metrics.misses

        provider.get_current_weather("Pekanbaru")
        assert forecast_metrics.misses == misses_before + 1

        provider.get_current_weather("Pekanbaru")
        assert forecast_metrics.hits == hits_before + 1

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_forecast_cache_ttl(self, mock_geocode, mock_get):
        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_WEATHER_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        provider = OpenMeteoProvider()
        provider.get_current_weather("Pekanbaru")
        assert mock_get.call_count == 1

        # Fast-forward by manually clearing cache to simulate TTL expiry
        forecast_cache.clear()

        r2 = provider.get_current_weather("Pekanbaru")
        assert mock_get.call_count == 2  # New HTTP call after cache clear
        assert r2.rr == 12.5


# ── Prediction equality before/after cache ───────────────────────────


class TestPredictionEquality:
    """Verify predictions are identical with and without cache.

    Since caching stores raw JSON and rebuilds RawWeatherData identically,
    prediction outputs must be bit-for-bit identical.
    """

    @patch("backend.providers.openmeteo_provider.requests.get")
    @patch("backend.providers.openmeteo_provider.geocode")
    def test_prediction_identical_with_cache(self, mock_geocode, mock_get):
        """Compare prediction results from first (miss) and second (hit) calls."""
        from backend.providers.models import RawWeatherData
        from backend.services.prediction_gateway import predict_from_raw

        mock_geocode.return_value = GeoLocation(0.507, 101.447, "Pekanbaru")
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_WEATHER_RESPONSE
        )
        mock_get.return_value.raise_for_status = MagicMock()

        provider = OpenMeteoProvider()

        # First call — fresh data from HTTP (cache MISS)
        weather1 = provider.get_current_weather("Pekanbaru")

        # Build a minimal history for the gateway (needed for rolling features)
        history = [{"rr": 10.0}, {"rr": 8.0}, {"rr": 6.0}]

        pred1 = predict_from_raw(weather1, history=history, model="rf", top_n=3)

        # Second call — from cache (cache HIT)
        weather2 = provider.get_current_weather("Pekanbaru")
        pred2 = predict_from_raw(weather2, history=history, model="rf", top_n=3)

        # Both RawWeatherData instances must be identical
        assert weather1 == weather2

        # Prediction outputs must be identical
        assert pred1["fri"] == pred2["fri"]
        assert pred1["tingkat_risiko"] == pred2["tingkat_risiko"]
        assert pred1["rekomendasi"] == pred2["rekomendasi"]
        assert pred1["mitigasi"] == pred2["mitigasi"]


# ── Cache diagnostics endpoint test ──────────────────────────────────


class TestCacheDiagnostics:
    def test_cache_endpoint_returns_expected_structure(self):
        from backend.app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        r = client.get("/api/system/cache")
        assert r.status_code == 200
        data = r.json()
        assert "geocoding" in data
        assert "forecast" in data
        assert "hits" in data["geocoding"]
        assert "misses" in data["geocoding"]
        assert "hit_rate" in data["geocoding"]
        assert "entries" in data["geocoding"]
        assert "maxsize" in data["geocoding"]
        assert "ttl_seconds" in data["geocoding"]
        assert "hits" in data["forecast"]
        assert "misses" in data["forecast"]
        assert "entries" in data["forecast"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
