"""Knowledge Loader — loads, validates, and constructs in-memory objects.

The loader executes once during application startup. It:
  1. Reads the JSON data file
  2. Validates the raw data (schema, enums, required fields)
  3. Constructs CommodityKnowledge Pydantic objects
  4. Assembles the KnowledgeCollection
  5. Hands it to the Cache

No repeated disk reads after initial load.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Final

from backend.knowledge.exceptions import KnowledgeLoadError
from backend.knowledge.models import (
    CommodityKnowledge,
    FloodToleranceLevel,
    KNOWLEDGE_SCHEMA_VERSION,
    KnowledgeCollection,
    KnowledgeMetadata,
)
from backend.knowledge.validator import assert_valid

logger = logging.getLogger(__name__)

# ── Default path relative to this file ──────────────────────────────
DEFAULT_DATA_DIR: Final[Path] = Path(__file__).resolve().parent / "data"
DEFAULT_DATA_FILE: Final[str] = "commodity_knowledge.json"


class KnowledgeLoader:
    """Loads commodity knowledge from a structured JSON source.

    Usage:
        loader = KnowledgeLoader()
        collection = loader.load()
        # collection.commodities -> list[CommodityKnowledge]
        # collection.metadata   -> KnowledgeMetadata
    """

    def __init__(
        self,
        data_path: str | Path | None = None,
    ) -> None:
        self._data_path = Path(data_path) if data_path else (
            DEFAULT_DATA_DIR / DEFAULT_DATA_FILE
        )
        self._loaded: bool = False

    @property
    def data_path(self) -> Path:
        return self._data_path

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> KnowledgeCollection:
        """Execute the full load pipeline.

        Raises:
            KnowledgeLoadError: If the file cannot be read.
            KnowledgeValidationError: If validation fails (from assert_valid).
        """
        start = time.perf_counter()

        # ── Step 1: Read JSON ────────────────────────────────────────
        if not self._data_path.exists():
            raise KnowledgeLoadError(
                str(self._data_path),
                "File does not exist",
            )
        if not self._data_path.is_file():
            raise KnowledgeLoadError(
                str(self._data_path),
                "Path is not a file",
            )

        try:
            raw_text = self._data_path.read_text(encoding="utf-8")
        except OSError as e:
            raise KnowledgeLoadError(str(self._data_path), str(e))

        try:
            raw_data: list[dict] = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise KnowledgeLoadError(
                str(self._data_path),
                f"Invalid JSON: {e.msg}",
            )

        if not isinstance(raw_data, list):
            raise KnowledgeLoadError(
                str(self._data_path),
                "Expected JSON root to be an array",
            )

        # ── Step 2: Validate ─────────────────────────────────────────
        assert_valid(raw_data, schema_version=KNOWLEDGE_SCHEMA_VERSION)

        # ── Step 3: Construct objects ────────────────────────────────
        commodities: list[CommodityKnowledge] = []
        for item in raw_data:
            commodity = CommodityKnowledge(**item)
            commodities.append(commodity)

        # ── Step 4: Gather metadata ──────────────────────────────────
        categories = sorted(set(c.commodity_category for c in commodities))
        vuln_levels = sorted(
            set(c.vulnerability_level for c in commodities),
            key=lambda x: FloodToleranceLevel.ordinal(x),
            reverse=True,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        metadata = KnowledgeMetadata(
            schema_version=KNOWLEDGE_SCHEMA_VERSION,
            commodity_count=len(commodities),
            loaded_at=__import__("datetime").datetime.now().isoformat(),
            load_duration_ms=round(elapsed_ms, 2),
            validation_status="passed",
            categories=categories,
            vulnerability_levels=vuln_levels,
        )

        collection = KnowledgeCollection(
            commodities=commodities,
            metadata=metadata,
        )

        self._loaded = True

        logger.info(
            "Knowledge loaded: %d commodities, %d categories, "
            "schema v%s, %.1f ms",
            len(commodities),
            len(categories),
            KNOWLEDGE_SCHEMA_VERSION,
            elapsed_ms,
        )

        return collection
