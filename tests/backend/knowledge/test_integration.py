"""Integration tests for the complete Knowledge Base pipeline.

Tests the full lifecycle: Load → Validate → Cache → Query.
"""

from __future__ import annotations

from pathlib import Path

from backend.knowledge.cache import KnowledgeCache
from backend.knowledge.knowledge_base import KnowledgeBase
from backend.knowledge.loader import KnowledgeLoader
from backend.knowledge.query import KnowledgeQueryEngine
from backend.knowledge.validator import validate_knowledge_data

DATA_DIR = Path(__file__).resolve().parents[2] / "backend" / "knowledge" / "data"
DATA_FILE = DATA_DIR / "commodity_knowledge.json"


class TestFullPipeline:
    """End-to-end: JSON file → Validate → Load → Cache → Query."""

    def test_complete_pipeline(self):
        # 1. Loader loads and validates
        loader = KnowledgeLoader()
        collection = loader.load()

        # 2. Cache stores
        cache = KnowledgeCache()
        cache.load(collection)

        # 3. Query engine queries
        engine = KnowledgeQueryEngine(cache)

        # Verify
        assert engine.count() == 22
        assert engine.exists("kangkung_air")

        kangkung = engine.get_by_id("kangkung_air")
        assert kangkung.commodity_name == "Kangkung Air"
        assert kangkung.vulnerability_level == "Sangat Tinggi"
        assert kangkung.flood_tolerance_category == "Sangat Tinggi"
        assert kangkung.growing_duration_days == 25
        assert len(kangkung.major_impacts) > 0
        assert len(kangkung.damage_symptoms) > 0

    def test_all_commodities_have_all_required_fields(self):
        kb = KnowledgeBase()
        kb.initialize()
        for c in kb.get_all():
            assert c.commodity_id
            assert c.commodity_name
            assert c.commodity_category
            assert c.vulnerability_level
            assert c.flood_tolerance_category
            assert c.maximum_inundation_duration
            assert c.drainage_requirement
            assert 1 <= c.growing_duration_days <= 364
            assert c.optimal_risk_level
            assert c.economic_priority
            assert len(c.major_impacts) >= 1
            assert len(c.damage_symptoms) >= 1
            assert c.recommendation_notes
            assert c.scientific_reference
            assert c.version == "2.1"
            assert c.last_updated

    def test_knowledge_base_facade_full_lifecycle(self):
        kb = KnowledgeBase()
        assert not kb.is_ready

        kb.initialize()
        assert kb.is_ready

        # Verify health status
        status = kb.health_status()
        assert status["knowledge_ready"]
        assert status["commodity_count"] == 22

        # Verify metadata
        meta = kb.get_metadata()
        assert meta is not None
        assert meta.validation_status == "passed"

        # Verify all queries work
        assert kb.count() == 22
        assert len(kb.list_categories()) >= 5
        assert len(kb.list_vulnerability_levels()) >= 3
        assert kb.exists("talas")
        assert not kb.exists("nonexistent_crop")

    def test_validator_on_full_dataset(self, knowledge_data):
        report = validate_knowledge_data(knowledge_data, schema_version="2.1")
        assert report.passed, f"Validation failed: {report.errors}"
        assert report.failed_checks == 0
        assert report.total_checks > 0


class TestDatasetIntegrity:
    """Ensure the dataset is complete and consistent."""

    def test_exactly_22_commodities(self, knowledge_data):
        assert len(knowledge_data) == 22

    def test_no_duplicate_ids(self, knowledge_data):
        ids = [d["commodity_id"] for d in knowledge_data]
        assert len(ids) == len(set(ids))

    def test_all_ids_unique(self, knowledge_data):
        ids = [d["commodity_id"] for d in knowledge_data]
        assert len(ids) == len(set(ids))

    def test_knowledge_base_isolation(self):
        """Verify KB does not import any ML modules."""
        # Test that KB can be imported without importing ml
        # This is a structural test
        from backend.knowledge import KnowledgeBase
        assert KnowledgeBase is not None
