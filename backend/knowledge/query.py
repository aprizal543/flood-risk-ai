"""Read-only query engine for the Knowledge Base.

Provides a clean public API for querying commodity knowledge. All
methods delegate to the Cache layer.

No recommendation logic, scoring, ranking, or FRI filtering.
"""

from __future__ import annotations

from backend.knowledge.cache import KnowledgeCache
from backend.knowledge.exceptions import (
    CommodityNotFoundError,
    KnowledgeNotLoadedError,
)
from backend.knowledge.models import CommodityKnowledge


class KnowledgeQueryEngine:
    """Read-only query interface for commodity knowledge.

    Usage:
        engine = KnowledgeQueryEngine(cache)
        all_commodities = engine.get_all()
        kangkung = engine.get_by_id("kangkung")
    """

    def __init__(self, cache: KnowledgeCache) -> None:
        self._cache = cache

    def _check_loaded(self) -> None:
        if not self._cache.is_loaded:
            raise KnowledgeNotLoadedError()

    def get_all(self) -> list[CommodityKnowledge]:
        """Return all commodities."""
        self._check_loaded()
        return list(self._cache.get_all())

    def get_by_id(self, commodity_id: str) -> CommodityKnowledge:
        """Look up a commodity by its unique ID.

        Raises:
            CommodityNotFoundError: If the ID does not exist.
        """
        self._check_loaded()
        result = self._cache.get_by_id(commodity_id)
        if result is None:
            raise CommodityNotFoundError(commodity_id)
        return result

    def get_by_name(self, name: str) -> list[CommodityKnowledge]:
        """Look up commodities by name (case-insensitive)."""
        self._check_loaded()
        return self._cache.get_by_name(name)

    def get_by_category(self, category: str) -> list[CommodityKnowledge]:
        """Get all commodities in a given category."""
        self._check_loaded()
        return self._cache.get_by_category(category)

    def get_by_vulnerability(self, level: str) -> list[CommodityKnowledge]:
        """Get all commodities with a given vulnerability level."""
        self._check_loaded()
        return self._cache.get_by_vulnerability(level)

    def exists(self, commodity_id: str) -> bool:
        """Check whether a commodity ID exists."""
        self._check_loaded()
        return self._cache.exists(commodity_id)

    def count(self) -> int:
        """Return the total number of commodities."""
        self._check_loaded()
        return self._cache.count()

    def list_categories(self) -> list[str]:
        """Return sorted list of all commodity categories."""
        self._check_loaded()
        return self._cache.list_categories()

    def list_vulnerability_levels(self) -> list[str]:
        """Return sorted list of all vulnerability levels."""
        self._check_loaded()
        return self._cache.list_vulnerability_levels()
