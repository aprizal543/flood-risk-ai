"""Unit tests for the Knowledge Loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.knowledge.exceptions import KnowledgeLoadError, KnowledgeValidationError
from backend.knowledge.loader import DEFAULT_DATA_DIR, KnowledgeLoader


class TestKnowledgeLoader:
    def test_default_path_exists(self):
        path = DEFAULT_DATA_DIR / "commodity_knowledge.json"
        assert path.exists(), f"Default data file not found at {path}"

    def test_load_returns_collection(self):
        loader = KnowledgeLoader()
        collection = loader.load()
        assert collection is not None
        assert len(collection.commodities) == 22
        assert collection.metadata.commodity_count == 22

    def test_load_populates_all_fields(self):
        loader = KnowledgeLoader()
        collection = loader.load()
        for c in collection.commodities:
            assert c.commodity_id
            assert c.commodity_name
            assert c.commodity_category
            assert c.vulnerability_level
            assert c.flood_tolerance_category
            assert c.maximum_inundation_duration
            assert c.drainage_requirement
            assert c.growing_duration_days > 0
            assert c.optimal_risk_level
            assert c.economic_priority
            assert len(c.major_impacts) > 0
            assert len(c.damage_symptoms) > 0
            assert c.recommendation_notes
            assert c.scientific_reference
            assert c.version
            assert c.last_updated

    def test_load_metadata_correct(self):
        loader = KnowledgeLoader()
        collection = loader.load()
        meta = collection.metadata
        assert meta.schema_version == "2.1"
        assert meta.commodity_count == 22
        assert meta.validation_status == "passed"
        assert len(meta.categories) == 5
        assert len(meta.vulnerability_levels) == 5

    def test_is_loaded_after_load(self):
        loader = KnowledgeLoader()
        assert not loader.is_loaded
        loader.load()
        assert loader.is_loaded

    def test_nonexistent_file_raises(self):
        loader = KnowledgeLoader("nonexistent/path.json")
        with pytest.raises(KnowledgeLoadError) as exc:
            loader.load()
        assert "does not exist" in str(exc.value)

    def test_invalid_json_raises(self, tmp_path: Path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json", encoding="utf-8")
        loader = KnowledgeLoader(str(bad_file))
        with pytest.raises(KnowledgeLoadError) as exc:
            loader.load()
        assert "Invalid JSON" in str(exc.value)

    def test_non_array_json_raises(self, tmp_path: Path):
        bad_file = tmp_path / "object.json"
        bad_file.write_text('{"key": "value"}', encoding="utf-8")
        loader = KnowledgeLoader(str(bad_file))
        with pytest.raises(KnowledgeLoadError) as exc:
            loader.load()
        assert "array" in str(exc.value).lower()

    def test_duplicate_id_raises(self, tmp_path: Path):
        bad_file = tmp_path / "duplicate.json"
        data = [
            {
                "commodity_id": "duplicate",
                "commodity_name": "First",
                "aliases": [],
                "kelompok_kerentanan": ["Tinggi"],
                "tingkat_kerentanan": "Rentan (Sensitive)",
                "batas_toleransi_genangan": "2 hari",
                "dampak_utama": ["Impact A"],
                "gejala_kerusakan": ["Symptom A"],
                "commodity_category": "sayuran_daun",
                "vulnerability_level": "Tinggi",
                "flood_tolerance_category": "Tinggi",
                "maximum_inundation_duration": "2 hari",
                "drainage_requirement": "Rendah",
                "growing_duration_days": 30,
                "optimal_risk_level": "Rendah",
                "economic_priority": "Sedang",
                "major_impacts": ["Impact A"],
                "damage_symptoms": ["Symptom A"],
                "recommendation_notes": "Note A",
                "scientific_reference": "Ref A",
                "version": "2.0",
                "last_updated": "2026-07-10",
            },
            {
                "commodity_id": "duplicate",
                "commodity_name": "Second",
                "aliases": [],
                "kelompok_kerentanan": ["Tinggi"],
                "tingkat_kerentanan": "Rentan (Sensitive)",
                "batas_toleransi_genangan": "2 hari",
                "dampak_utama": ["Impact B"],
                "gejala_kerusakan": ["Symptom B"],
                "commodity_category": "sayuran_daun",
                "vulnerability_level": "Tinggi",
                "flood_tolerance_category": "Tinggi",
                "maximum_inundation_duration": "2 hari",
                "drainage_requirement": "Rendah",
                "growing_duration_days": 30,
                "optimal_risk_level": "Rendah",
                "economic_priority": "Sedang",
                "major_impacts": ["Impact B"],
                "damage_symptoms": ["Symptom B"],
                "recommendation_notes": "Note B",
                "scientific_reference": "Ref B",
                "version": "2.0",
                "last_updated": "2026-07-10",
            },
        ]
        bad_file.write_text(json.dumps(data), encoding="utf-8")
        loader = KnowledgeLoader(str(bad_file))
        with pytest.raises(KnowledgeValidationError) as exc:
            loader.load()
        assert any("duplicate" in e.lower() for e in exc.value.errors)

    def test_custom_path(self, tmp_path: Path):
        custom_file = tmp_path / "custom_knowledge.json"
        lecturer_ids = [
            "cabai", "tomat", "bawang_merah", "kentang", "paprika",
            "kubis", "pakcoy", "sawi", "terong", "mentimun", "kacang_panjang",
            "wortel", "lobak", "labu_siam", "buncis",
            "kangkung_air", "genjer", "selada_air", "talas",
            "seledri", "pakis_sayur", "semanggi",
        ]
        base = {
            "commodity_name": "Test",
            "aliases": [],
            "kelompok_kerentanan": ["Tinggi"],
            "tingkat_kerentanan": "Rentan (Sensitive)",
            "batas_toleransi_genangan": "2 hari",
            "dampak_utama": ["Test impact"],
            "gejala_kerusakan": ["Test symptom"],
            "main_impacts": ["Test impact"],
            "damage_symptoms": ["Test symptom"],
            "commodity_category": "sayuran_daun",
            "vulnerability_level": "Tinggi",
            "flood_tolerance_category": "Tinggi",
            "maximum_inundation_duration": "2 hari",
            "drainage_requirement": "Rendah",
            "growing_duration_days": 30,
            "optimal_risk_level": "Rendah",
            "economic_priority": "Sedang",
            "major_impacts": ["Test impact"],
            "recommendation_notes": "Test notes",
            "scientific_reference": "Test ref",
            "version": "2.1",
            "last_updated": "2026-07-10",
        }
        data = [{**base, "commodity_id": cid, "commodity_name": cid.title()} for cid in lecturer_ids]
        custom_file.write_text(json.dumps(data), encoding="utf-8")
        loader = KnowledgeLoader(str(custom_file))
        collection = loader.load()
        assert len(collection.commodities) == 22
        assert collection.commodities[0].commodity_id == "cabai"
