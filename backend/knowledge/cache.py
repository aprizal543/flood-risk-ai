"""Thread-safe, read-only, in-memory cache for the Knowledge Base.

The cache is populated once during application startup and never
invalidated. All lookups return references to immutable Pydantic
objects (frozen=True), making the cache safe for concurrent reads
without locks.
"""

from __future__ import annotations

import threading
from typing import Final

from backend.knowledge.models import (
    CommodityKnowledge,
    KnowledgeCollection,
    KnowledgeMetadata,
)

# ── Sentinel for uninitialised cache ────────────────────────────────
_UNSET: Final[str] = "__UNSET__"


class KnowledgeCache:
    """Singleton in-memory cache for commodity knowledge.

    Thread-safety is guaranteed by:
      - Using a Lock for the single write operation (load).
      - All subsequent reads are on frozen Pydantic objects.
      - The cache is never modified after initial load.

    Usage:
        cache = KnowledgeCache()
        cache.load(collection)   # one-time, during startup
        cache.is_loaded          # bool
        cache.get_all()          # list[CommodityKnowledge]
        cache.get_by_id("kangkung")  # CommodityKnowledge | None
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._commodities_by_id: dict[str, CommodityKnowledge] = {}
        self._commodities_by_name: dict[str, list[CommodityKnowledge]] = {}
        self._commodities_by_category: dict[str, list[CommodityKnowledge]] = {}
        self._commodities_by_vulnerability: dict[str, list[CommodityKnowledge]] = {}
        self._metadata: KnowledgeMetadata | None = None
        self._loaded: bool = False
        self._all_commodities: tuple[CommodityKnowledge, ...] = ()

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def metadata(self) -> KnowledgeMetadata | None:
        return self._metadata

    @property
    def size(self) -> int:
        return len(self._all_commodities)

    # ── Load (write-once) ───────────────────────────────────────────

    def load(self, collection: KnowledgeCollection) -> None:
        """Populate the cache from a KnowledgeCollection.

        Thread-safe: acquires a lock during the write.
        Must be called exactly once during application startup.

        Args:
            collection: The validated KnowledgeCollection to cache.
        """
        with self._lock:
            if self._loaded:
                return  # already loaded; silently ignore

            for commodity in collection.commodities:
                cid = commodity.commodity_id
                name = commodity.commodity_name.lower()
                cat = commodity.commodity_category
                vuln = commodity.vulnerability_level

                # Primary index: by ID
                self._commodities_by_id[cid] = commodity

                # Secondary index: by name (case-insensitive)
                self._commodities_by_name.setdefault(name, []).append(commodity)

                # Secondary index: by category
                self._commodities_by_category.setdefault(cat, []).append(commodity)

                # Secondary index: by vulnerability
                self._commodities_by_vulnerability.setdefault(vuln, []).append(commodity)

            # Immutable tuple for zero-copy iteration
            self._all_commodities = tuple(collection.commodities)
            self._metadata = collection.metadata
            self._loaded = True

    # ── Query helpers (all read-only, no lock needed) ───────────────

    def get_all(self) -> tuple[CommodityKnowledge, ...]:
        """Return all commodities as an immutable tuple (zero-copy)."""
        return self._all_commodities

    def get_by_id(self, commodity_id: str) -> CommodityKnowledge | None:
        """Look up a commodity by its unique ID."""
        return self._commodities_by_id.get(commodity_id)

    def get_by_name(self, name: str) -> list[CommodityKnowledge]:
        """Look up commodities by name (case-insensitive)."""
        return list(self._commodities_by_name.get(name.lower(), []))

    def get_by_category(self, category: str) -> list[CommodityKnowledge]:
        """Get all commodities in a given category."""
        return list(self._commodities_by_category.get(category, []))

    def get_by_vulnerability(self, level: str) -> list[CommodityKnowledge]:
        """Get all commodities with a given vulnerability level."""
        return list(self._commodities_by_vulnerability.get(level, []))

    def exists(self, commodity_id: str) -> bool:
        """Check whether a commodity ID exists."""
        return commodity_id in self._commodities_by_id

    def count(self) -> int:
        """Return the total number of commodities."""
        return len(self._all_commodities)

    def list_categories(self) -> list[str]:
        """Return sorted list of all commodity categories."""
        return sorted(self._commodities_by_category.keys())

    def list_vulnerability_levels(self) -> list[str]:
        """Return sorted list of all vulnerability levels."""
        from backend.knowledge.models import FloodToleranceLevel
        return sorted(
            self._commodities_by_vulnerability.keys(),
            key=lambda x: FloodToleranceLevel.ordinal(x),
            reverse=True,
        )
