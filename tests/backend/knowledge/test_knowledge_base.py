"""Unit tests for the KnowledgeBase facade."""

from __future__ import annotations

import pytest

from backend.knowledge.exceptions import (
    CommodityNotFoundError,
    KnowledgeBaseError,
    KnowledgeNotLoadedError,
)
from backend.knowledge.knowledge_base import KnowledgeBase


class TestKnowledgeBase:
    def test_not_ready_by_default(self):
        kb = KnowledgeBase()
        assert not kb.is_ready
        assert kb.initialization_error is None

    def test_initialize_loads_all_commodities(self):
        kb = KnowledgeBase()
        kb.initialize()
        assert kb.is_ready
        assert kb.count() == 22

    def test_get_by_id(self):
        kb = KnowledgeBase()
        kb.initialize()
        c = kb.get_by_id("kangkung_air")
        assert c.commodity_name == "Kangkung Air"

    def test_get_by_id_not_found_raises(self):
        kb = KnowledgeBase()
        kb.initialize()
        with pytest.raises(CommodityNotFoundError):
            kb.get_by_id("nonexistent")

    def test_get_all(self):
        kb = KnowledgeBase()
        kb.initialize()
        result = kb.get_all()
        assert len(result) == 22

    def test_get_by_category(self):
        kb = KnowledgeBase()
        kb.initialize()
        result = kb.get_by_category("sayuran_daun")
        assert len(result) == 9

    def test_get_by_vulnerability(self):
        kb = KnowledgeBase()
        kb.initialize()
        result = kb.get_by_vulnerability("Sangat Tinggi")
        assert len(result) == 3  # genjer, kangkung_air, semanggi

    def test_exists(self):
        kb = KnowledgeBase()
        kb.initialize()
        assert kb.exists("kangkung_air")
        assert not kb.exists("nonexistent")

    def test_count(self):
        kb = KnowledgeBase()
        kb.initialize()
        assert kb.count() == 22

    def test_list_categories(self):
        kb = KnowledgeBase()
        kb.initialize()
        cats = kb.list_categories()
        assert len(cats) == 5

    def test_list_vulnerability_levels(self):
        kb = KnowledgeBase()
        kb.initialize()
        levels = kb.list_vulnerability_levels()
        assert len(levels) >= 3

    def test_get_metadata(self):
        kb = KnowledgeBase()
        kb.initialize()
        meta = kb.get_metadata()
        assert meta is not None
        assert meta.commodity_count == 22
        assert meta.schema_version == "2.1"

    def test_health_status_when_ready(self):
        kb = KnowledgeBase()
        kb.initialize()
        status = kb.health_status()
        assert status["knowledge_ready"] is True
        assert status["commodity_count"] == 22
        assert status["knowledge_version"] == "2.1"
        assert status["validation_status"] == "passed"

    def test_health_status_when_not_ready(self):
        kb = KnowledgeBase()
        status = kb.health_status()
        assert status["knowledge_ready"] is False
        assert status["commodity_count"] == 0
        assert status["knowledge_version"] is None

    def test_not_loaded_raises_on_query(self):
        kb = KnowledgeBase()
        with pytest.raises(KnowledgeNotLoadedError):
            kb.get_all()

    def test_initialize_twice_is_noop(self):
        kb = KnowledgeBase()
        kb.initialize()
        kb.initialize()  # second call should not raise
        assert kb.is_ready
        assert kb.count() == 22

    def test_get_by_name(self):
        kb = KnowledgeBase()
        kb.initialize()
        result = kb.get_by_name("Kangkung Air")
        assert len(result) == 1
        assert result[0].commodity_id == "kangkung_air"

    def test_initialize_with_invalid_path(self):
        kb = KnowledgeBase()
        with pytest.raises(KnowledgeBaseError):
            kb.initialize(data_path="nonexistent/path.json")


class TestKnowledgeBaseIntegration:
    """Integration tests verifying the full 22-commodity dataset."""

    def test_all_ids_valid(self):
        kb = KnowledgeBase()
        kb.initialize()
        expected_ids = {
            "bawang_merah", "buncis", "cabai", "genjer",
            "kacang_panjang", "kangkung_air", "kentang", "kubis",
            "labu_siam", "lobak", "mentimun", "pakcoy",
            "pakis_sayur", "paprika", "sawi", "selada_air",
            "seledri", "semanggi", "talas", "terong",
            "tomat", "wortel",
        }
        actual_ids = {c.commodity_id for c in kb.get_all()}
        assert actual_ids == expected_ids

    def test_all_categories_present(self):
        kb = KnowledgeBase()
        kb.initialize()
        cats = kb.list_categories()
        assert "sayuran_daun" in cats
        assert "sayuran_buah" in cats
        assert "sayuran_umbi" in cats
        assert "kacang-kacangan" in cats
        assert "umbi" in cats

    def test_vulnerability_counts(self):
        kb = KnowledgeBase()
        kb.initialize()
        sangat_tinggi = kb.get_by_vulnerability("Sangat Tinggi")
        tinggi = kb.get_by_vulnerability("Tinggi")
        sedang = kb.get_by_vulnerability("Sedang")
        rendah = kb.get_by_vulnerability("Rendah")
        sangat_rendah = kb.get_by_vulnerability("Sangat Rendah")
        assert len(sangat_tinggi) == 3  # genjer, kangkung_air, semanggi
        assert len(tinggi) == 3  # pakis_sayur, selada_air, talas
        assert len(sedang) == 5  # buncis, labu_siam, lobak, seledri, wortel
        assert len(rendah) == 6  # kacang_panjang, kubis, mentimun, pakcoy, sawi, terong
        assert len(sangat_rendah) == 5  # bawang_merah, cabai, kentang, paprika, tomat
