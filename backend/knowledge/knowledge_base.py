"""KnowledgeBase — Public facade for the Knowledge Base module.

Provides a single entry point for all knowledge operations.
Manages the lifecycle: Load → Validate → Cache → Query.

Usage:
    kb = KnowledgeBase()
    kb.initialize()         # Called once during app startup
    kb.is_ready             # True after successful initialize()
    kb.get_by_id("kangkung")
    kb.get_all()
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.knowledge.cache import KnowledgeCache
from backend.knowledge.exceptions import (
    KnowledgeBaseError,
    KnowledgeNotLoadedError,
)
from backend.knowledge.loader import KnowledgeLoader
from backend.knowledge.models import (
    CommodityKnowledge,
    KnowledgeCollection,
    KnowledgeMetadata,
)
from backend.knowledge.query import KnowledgeQueryEngine

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Public facade for the Knowledge Base.

    Singleton pattern — one instance per application lifecycle.
    """

    def __init__(self) -> None:
        self._cache = KnowledgeCache()
        self._query = KnowledgeQueryEngine(self._cache)
        self._ready: bool = False
        self._initialization_error: str | None = None

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def cache(self) -> KnowledgeCache:
        return self._cache

    @property
    def initialization_error(self) -> str | None:
        return self._initialization_error

    # ── Lifecycle ───────────────────────────────────────────────────

    def initialize(self, data_path: str | None = None) -> None:
        """Load, validate, and cache all commodity knowledge.

        Must be called exactly once during application startup.
        Subsequent calls are no-ops.

        Args:
            data_path: Optional custom path to the JSON knowledge file.

        Raises:
            KnowledgeBaseError: If initialization fails.
        """
        if self._ready:
            logger.debug("KnowledgeBase already initialized, skipping")
            return

        start = time.perf_counter()

        try:
            loader = KnowledgeLoader(data_path)
            collection: KnowledgeCollection = loader.load()
            self._cache.load(collection)
            self._ready = True
            self._initialization_error = None

            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "KnowledgeBase initialized: %d commodities, "
                "schema v%s, %.1f ms",
                collection.metadata.commodity_count,
                collection.metadata.schema_version,
                elapsed_ms,
            )

        except KnowledgeBaseError:
            self._ready = False
            self._initialization_error = "Knowledge Base initialization failed"
            logger.exception("KnowledgeBase initialization failed")
            raise

        except Exception as e:
            self._ready = False
            self._initialization_error = str(e)
            logger.exception("KnowledgeBase initialization failed with unexpected error")
            raise KnowledgeBaseError(
                f"Unexpected error during KnowledgeBase initialization: {e}"
            ) from e

    # ── Query delegation ────────────────────────────────────────────

    def get_all(self) -> list[CommodityKnowledge]:
        """Return all commodities."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.get_all()

    def get_by_id(self, commodity_id: str) -> CommodityKnowledge:
        """Look up a commodity by its unique ID.

        Raises:
            CommodityNotFoundError: If the ID does not exist.
        """
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.get_by_id(commodity_id)

    def get_by_name(self, name: str) -> list[CommodityKnowledge]:
        """Look up commodities by name (case-insensitive)."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.get_by_name(name)

    def get_by_category(self, category: str) -> list[CommodityKnowledge]:
        """Get all commodities in a given category."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.get_by_category(category)

    def get_by_vulnerability(self, level: str) -> list[CommodityKnowledge]:
        """Get all commodities with a given vulnerability level."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.get_by_vulnerability(level)

    def exists(self, commodity_id: str) -> bool:
        """Check whether a commodity ID exists."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.exists(commodity_id)

    def count(self) -> int:
        """Return the total number of commodities."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.count()

    def list_categories(self) -> list[str]:
        """Return sorted list of all commodity categories."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.list_categories()

    def list_vulnerability_levels(self) -> list[str]:
        """Return sorted list of all vulnerability levels."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._query.list_vulnerability_levels()

    def get_metadata(self) -> KnowledgeMetadata | None:
        """Return the Knowledge Collection metadata."""
        if not self._ready:
            raise KnowledgeNotLoadedError()
        return self._cache.metadata

    def health_status(self) -> dict[str, Any]:
        """Return health/status information for the health endpoint.

        This is an additive, non-breaking method for extending the
        /api/health endpoint.
        """
        if not self._ready:
            return {
                "knowledge_ready": False,
                "knowledge_version": None,
                "commodity_count": 0,
                "validation_status": "not_loaded",
            }

        meta = self._cache.metadata
        return {
            "knowledge_ready": True,
            "knowledge_version": meta.schema_version if meta else None,
            "commodity_count": self._cache.count(),
            "validation_status": meta.validation_status if meta else "unknown",
        }
