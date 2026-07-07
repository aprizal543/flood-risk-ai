"""Shared test fixtures and cache reset."""

import pytest

from backend.providers.geocoding import geocoding_cache
from backend.providers.openmeteo_provider import forecast_cache


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear in-memory caches before every test to prevent cross-test pollution."""
    geocoding_cache.clear()
    forecast_cache.clear()
    yield
