"""Unit tests for the Knowledge Cache."""

from __future__ import annotations

import pytest

from backend.knowledge.cache import KnowledgeCache
from backend.knowledge.models import (
    KnowledgeCollection,
    KnowledgeMetadata,
)


@pytest.fixture
def sample_collection(sample_commodity) -> KnowledgeCollection:
    meta = KnowledgeMetadata(
        schema_version="1.0",
        commodity_count=1,
        loaded_at="2026-07-08T12:00:00",
        load_duration_ms=10.0,
        validation_status="passed",
        categories=["sayuran_daun"],
        vulnerability_levels=["Sangat Tinggi"],
    )
    return KnowledgeCollection(commodities=[sample_commodity], metadata=meta)





class TestKnowledgeCache:
    def test_not_loaded_by_default(self):
        cache = KnowledgeCache()
        assert not cache.is_loaded
        assert cache.size == 0

    def test_load_single(self, sample_collection):
        cache = KnowledgeCache()
        cache.load(sample_collection)
        assert cache.is_loaded
        assert cache.size == 1

    def test_get_all(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        all_c = cache.get_all()
        assert len(all_c) == 3

    def test_get_by_id_found(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        c = cache.get_by_id("kangkung_air")
        assert c is not None
        assert c.commodity_name == "Kangkung Air"

    def test_get_by_id_not_found(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        c = cache.get_by_id("nonexistent")
        assert c is None

    def test_get_by_name(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        results = cache.get_by_name("Cabai")
        assert len(results) == 1
        assert results[0].commodity_id == "cabai"

    def test_get_by_name_case_insensitive(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        results = cache.get_by_name("KANGKUNG AIR")
        assert len(results) == 1

    def test_get_by_name_not_found(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        results = cache.get_by_name("nonexistent")
        assert len(results) == 0

    def test_get_by_category(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        results = cache.get_by_category("sayuran_daun")
        assert len(results) == 2

    def test_get_by_category_no_match(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        results = cache.get_by_category("herba")
        assert len(results) == 0

    def test_get_by_vulnerability(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        results = cache.get_by_vulnerability("Sangat Tinggi")
        assert len(results) == 2
        assert results[0].commodity_id == "kangkung_air"

    def test_exists_true(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        assert cache.exists("kangkung_air")

    def test_exists_false(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        assert not cache.exists("nonexistent")

    def test_count(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        assert cache.count() == 3

    def test_list_categories(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        cats = cache.list_categories()
        assert "sayuran_buah" in cats
        assert "sayuran_daun" in cats
        assert cats == sorted(cats)  # sorted

    def test_list_vulnerability_levels(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        levels = cache.list_vulnerability_levels()
        assert "Sangat Tinggi" in levels
        assert "Sangat Rendah" in levels

    def test_metadata_accessible(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        meta = cache.metadata
        assert meta is not None
        assert meta.commodity_count == 3
        assert meta.schema_version == "2.1"

    def test_load_idempotent(self, multi_commodity_collection, sample_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        assert cache.count() == 3
        # Second load should be a no-op
        cache.load(sample_collection)
        assert cache.count() == 3  # still 3, not 1

    def test_get_all_returns_immutable(self, multi_commodity_collection):
        cache = KnowledgeCache()
        cache.load(multi_commodity_collection)
        all_c = cache.get_all()
        with pytest.raises(TypeError):
            all_c[0] = None  # type: ignore
