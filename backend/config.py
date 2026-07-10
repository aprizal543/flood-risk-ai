"""Backend configuration bootstrap.

Loads the repository root .env exactly once during application startup.
Provides shared timeout constants with environment variable overrides.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"


@lru_cache(maxsize=1)
def load_backend_environment() -> bool:
    """Load the root .env before any configuration value is read."""
    return load_dotenv(dotenv_path=ENV_PATH, override=False)


load_backend_environment()


# ── HTTP timeout defaults (overridable via env) ──────────────────────────
# Format: (connect_timeout, read_timeout) in seconds.

def _int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


# Geocoding: fast lookup, short timeouts.
GEOCODING_CONNECT_TIMEOUT: int = _int_env("GEOCODING_CONNECT_TIMEOUT", 3)
GEOCODING_READ_TIMEOUT: int = _int_env("GEOCODING_READ_TIMEOUT", 5)

# Open-Meteo forecast: returns 14 days of daily aggregates.
OPENMETEO_CONNECT_TIMEOUT: int = _int_env("OPENMETEO_CONNECT_TIMEOUT", 3)
OPENMETEO_READ_TIMEOUT: int = _int_env("OPENMETEO_READ_TIMEOUT", 10)

# Supabase Auth
AUTH_CONNECT_TIMEOUT: int = _int_env("AUTH_CONNECT_TIMEOUT", 3)
AUTH_READ_TIMEOUT: int = _int_env("AUTH_READ_TIMEOUT", 15)

# ── Feature flags ────────────────────────────────────────────────────────
def is_knowledge_recommendation_enabled() -> bool:
    """Read the KB recommendation feature flag at runtime."""
    load_backend_environment()
    return os.getenv("USE_KNOWLEDGE_RECOMMENDATION", "false").lower() in (
        "1", "true", "yes"
    )


USE_KNOWLEDGE_RECOMMENDATION: bool = is_knowledge_recommendation_enabled()

# ── Connection pool defaults ─────────────────────────────────────────────
POOL_CONNECTIONS: int = _int_env("HTTP_POOL_CONNECTIONS", 10)
POOL_MAXSIZE: int = _int_env("HTTP_POOL_MAXSIZE", 20)

# ── Retry defaults ───────────────────────────────────────────────────────
RETRY_TOTAL: int = _int_env("HTTP_RETRY_TOTAL", 3)
RETRY_BACKOFF_FACTOR: float = float(
    os.getenv("HTTP_RETRY_BACKOFF_FACTOR", "1.0")
)

# ── Cache TTL defaults (overridable via env) ────────────────────────────
# Geocoding: city -> coordinates rarely changes; 24-hour cache is safe.
GEOCODING_CACHE_TTL: int = _int_env("GEOCODING_CACHE_TTL", 86400)
GEOCODING_CACHE_MAXSIZE: int = _int_env("GEOCODING_CACHE_MAXSIZE", 1000)

# Forecast: 10-minute TTL balances freshness with latency reduction.
FORECAST_CACHE_TTL: int = _int_env("FORECAST_CACHE_TTL", 600)
FORECAST_CACHE_MAXSIZE: int = _int_env("FORECAST_CACHE_MAXSIZE", 100)
