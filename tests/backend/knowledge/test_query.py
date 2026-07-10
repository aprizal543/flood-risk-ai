"""Unit tests for the Knowledge Query Engine."""

from __future__ import annotations

import pytest

from backend.knowledge.cache import KnowledgeCache
from backend.knowledge.exceptions import CommodityNotFoundError, KnowledgeNotLoadedError
from backend.knowledge.models import KnowledgeCollection, KnowledgeMetadata
from backend.knowledge.query import KnowledgeQueryEngine


@pytest.fixture
def loaded_engine(multi_commodity_collection) -> KnowledgeQueryEngine:
    cache = KnowledgeCache()
    cache.load(multi_commodity_collection)
    return KnowledgeQueryEngine(cache)


class TestKnowledgeQueryEngine:
    def test_not_loaded_raises(self):
        cache = KnowledgeCache()
        engine = KnowledgeQueryEngine(cache)
        with pytest.raises(KnowledgeNotLoadedError):
            engine.get_all()

    def test_get_all(self, loaded_engine):
        result = loaded_engine.get_all()
        assert len(result) == 3

    def test_get_by_id_found(self, loaded_engine):
        c = loaded_engine.get_by_id("kangkung_air")
        assert c.commodity_name == "Kangkung Air"

    def test_get_by_id_not_found_raises(self, loaded_engine):
        with pytest.raises(CommodityNotFoundError) as exc:
            loaded_engine.get_by_id("nonexistent")
        assert "nonexistent" in str(exc.value)

    def test_get_by_name_found(self, loaded_engine):
        results = loaded_engine.get_by_name("Cabai")
        assert len(results) == 1

    def test_get_by_name_not_found(self, loaded_engine):
        results = loaded_engine.get_by_name("nonexistent")
        assert len(results) == 0

    def test_get_by_category(self, loaded_engine):
        results = loaded_engine.get_by_category("sayuran_daun")
        assert len(results) == 2

    def test_get_by_category_empty(self, loaded_engine):
        results = loaded_engine.get_by_category("herba")
        assert len(results) == 0

    def test_get_by_vulnerability(self, loaded_engine):
        results = loaded_engine.get_by_vulnerability("Sangat Tinggi")
        assert len(results) == 2  # kangkung_air, semanggi

    def test_exists_true(self, loaded_engine):
        assert loaded_engine.exists("kangkung_air")

    def test_exists_false(self, loaded_engine):
        assert not loaded_engine.exists("nonexistent")

    def test_count(self, loaded_engine):
        assert loaded_engine.count() == 3

    def test_list_categories(self, loaded_engine):
        cats = loaded_engine.list_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_list_vulnerability_levels(self, loaded_engine):
        levels = loaded_engine.list_vulnerability_levels()
        assert isinstance(levels, list)
        assert len(levels) > 0


class TestKnowledgeQueryEngineIntegration:
    """Integration tests using the full 22-commodity dataset."""

    def test_full_dataset_loads(self, knowledge_data):
        from backend.knowledge.models import CommodityKnowledge

        commodities = [CommodityKnowledge(**d) for d in knowledge_data]
        meta = KnowledgeMetadata(
            schema_version="1.0",
            commodity_count=len(commodities),
            loaded_at="2026-07-08T12:00:00",
            load_duration_ms=50.0,
            validation_status="passed",
            categories=list(set(c.commodity_category for c in commodities)),
            vulnerability_levels=list(set(c.vulnerability_level for c in commodities)),
        )
        collection = KnowledgeCollection(commodities=commodities, metadata=meta)
        cache = KnowledgeCache()
        cache.load(collection)
        engine = KnowledgeQueryEngine(cache)

        assert engine.count() == 22
        assert engine.exists("kangkung_air")
        assert engine.exists("talas")
        assert not engine.exists("nonexistent")

        by_cat = engine.get_by_category("sayuran_daun")
        assert 8 <= len(by_cat) <= 10

        by_vuln = engine.get_by_vulnerability("Sangat Tinggi")
        assert len(by_vuln) == 3  # genjer, kangkung_air, semanggi
