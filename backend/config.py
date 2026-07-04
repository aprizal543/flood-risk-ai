"""Backend configuration bootstrap.

Loads the repository root .env exactly once during application startup.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def load_backend_environment() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=root_dir / ".env", override=False)
