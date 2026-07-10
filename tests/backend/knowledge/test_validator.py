"""Unit tests for the knowledge base validator."""

from __future__ import annotations

import pytest

from backend.knowledge.exceptions import KnowledgeValidationError
from backend.knowledge.validator import (
    assert_valid,
    validate_commodity_record,
    validate_knowledge_data,
    validate_schema_version,
)


class TestSchemaVersionValidation:
    def test_valid_version(self):
        errors = validate_schema_version("2.1")
        assert len(errors) == 0

    def test_invalid_version(self):
        errors = validate_schema_version("1.0")
        assert len(errors) == 1
        assert "Schema version mismatch" in errors[0]

    def test_empty_version(self):
        errors = validate_schema_version("")
        assert len(errors) == 1

    def test_none_version(self):
        errors = validate_schema_version(None)  # type: ignore
        assert len(errors) == 1


class TestCommodityRecordValidation:
    VALID_RECORD = {
        "commodity_id": "kangkung_air",
        "commodity_name": "Kangkung Air",
        "aliases": [],
        "kelompok_kerentanan": ["Tinggi", "Rendah"],
        "tingkat_kerentanan": "Toleran (Tolerant)",
        "batas_toleransi_genangan": "Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
        "dampak_utama": ["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
        "gejala_kerusakan": ["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
        "main_impacts": ["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
        "damage_symptoms": ["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
        "commodity_category": "sayuran_daun",
        "vulnerability_level": "Sangat Tinggi",
        "flood_tolerance_category": "Sangat Tinggi",
        "maximum_inundation_duration": ">7 hari",
        "drainage_requirement": "Minimal",
        "growing_duration_days": 25,
        "optimal_risk_level": "Tinggi",
        "economic_priority": "Sangat Tinggi",
        "major_impacts": ["Pertumbuhan subur"],
        "damage_symptoms": ["Tidak ada gejala"],
        "recommendation_notes": "Ideal untuk area rawan banjir.",
        "scientific_reference": "FAO guides [Pending]",
        "version": "2.0",
        "last_updated": "2026-07-10",
    }

    def test_valid_record_passes(self):
        errors = validate_commodity_record(self.VALID_RECORD, 0)
        assert len(errors) == 0

    def test_missing_field(self):
        data = dict(self.VALID_RECORD)
        del data["commodity_name"]
        errors = validate_commodity_record(data, 0)
        assert any("commodity_name" in e for e in errors)

    def test_empty_string(self):
        data = dict(self.VALID_RECORD)
        data["commodity_name"] = ""
        errors = validate_commodity_record(data, 0)
        assert any("commodity_name" in e for e in errors)

    def test_null_field(self):
        data = dict(self.VALID_RECORD)
        data["commodity_name"] = None
        errors = validate_commodity_record(data, 0)
        assert any("commodity_name" in e and "null" in e for e in errors)

    def test_invalid_enum(self):
        data = dict(self.VALID_RECORD)
        data["commodity_category"] = "invalid_category"
        errors = validate_commodity_record(data, 0)
        assert any("commodity_category" in e for e in errors)

    def test_invalid_vulnerability(self):
        data = dict(self.VALID_RECORD)
        data["vulnerability_level"] = "Unknown Level"
        errors = validate_commodity_record(data, 0)
        assert any("vulnerability_level" in e for e in errors)

    def test_non_integer_duration(self):
        data = dict(self.VALID_RECORD)
        data["growing_duration_days"] = "not_an_int"
        errors = validate_commodity_record(data, 0)
        assert any("growing_duration_days" in e for e in errors)

    def test_negative_duration_days(self):
        data = dict(self.VALID_RECORD)
        data["growing_duration_days"] = -5
        errors = validate_commodity_record(data, 0)
        assert any("growing_duration_days" in e and "out of range" in e for e in errors)

    def test_empty_impacts_list(self):
        data = dict(self.VALID_RECORD)
        data["major_impacts"] = []
        errors = validate_commodity_record(data, 0)
        assert any("major_impacts" in e and "empty" in e for e in errors)

    def test_impacts_not_a_list(self):
        data = dict(self.VALID_RECORD)
        data["major_impacts"] = "not_a_list"
        errors = validate_commodity_record(data, 0)
        assert any("major_impacts" in e for e in errors)

    def test_empty_string_in_impacts(self):
        data = dict(self.VALID_RECORD)
        data["major_impacts"] = [""]
        errors = validate_commodity_record(data, 0)
        assert any("major_impacts" in e and "empty" in e for e in errors)

    def test_empty_damage_symptoms(self):
        data = dict(self.VALID_RECORD)
        data["damage_symptoms"] = []
        errors = validate_commodity_record(data, 0)
        assert any("damage_symptoms" in e and "empty" in e for e in errors)

    def test_empty_inundation_duration(self):
        data = dict(self.VALID_RECORD)
        data["maximum_inundation_duration"] = ""
        errors = validate_commodity_record(data, 0)
        assert any("maximum_inundation_duration" in e for e in errors)


class TestFullDataValidation:
    def test_empty_data_fails(self, knowledge_data):
        report = validate_knowledge_data([])
        assert not report.passed
        assert any("empty" in e.lower() for e in report.errors)

    def test_valid_data_passes(self, knowledge_data):
        report = validate_knowledge_data(knowledge_data, schema_version="2.1")
        assert report.passed, f"Validation errors: {report.errors}"
        assert report.failed_checks == 0

    def test_duplicate_ids_fail(self, knowledge_data):
        data = list(knowledge_data)
        data.append(dict(data[0]))  # duplicate first entry
        report = validate_knowledge_data(data)
        assert not report.passed
        assert any("duplicate" in e.lower() for e in report.errors)

    def test_valid_data_has_correct_count(self, knowledge_data):
        report = validate_knowledge_data(knowledge_data)
        assert report.passed
        assert len(knowledge_data) == 22


class TestAssertValid:
    def test_valid_data_does_not_raise(self, knowledge_data):
        assert_valid(knowledge_data, schema_version="2.1")

    def test_invalid_data_raises(self):
        with pytest.raises(KnowledgeValidationError) as exc:
            assert_valid([{"commodity_id": ""}], schema_version="2.0")
        assert "validation failed" in str(exc.value).lower()

    def test_empty_list_raises(self):
        with pytest.raises(KnowledgeValidationError):
            assert_valid([])
