"""Backend configuration bootstrap.

Loads the repository root .env exactly once during application startup.
Provides shared timeout constants with environment variable overrides.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def load_backend_environment() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=root_dir / ".env", override=False)


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

# ── Connection pool defaults ─────────────────────────────────────────────
POOL_CONNECTIONS: int = _int_env("HTTP_POOL_CONNECTIONS", 10)
POOL_MAXSIZE: int = _int_env("HTTP_POOL_MAXSIZE", 20)

# ── Retry defaults ───────────────────────────────────────────────────────
RETRY_TOTAL: int = _int_env("HTTP_RETRY_TOTAL", 3)
RETRY_BACKOFF_FACTOR: float = float(
    os.getenv("HTTP_RETRY_BACKOFF_FACTOR", "1.0")
)
