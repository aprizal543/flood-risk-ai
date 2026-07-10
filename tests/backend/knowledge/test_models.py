"""Unit tests for knowledge base models (Pydantic, enums)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.knowledge.models import (
    CommodityCategory,
    CommodityKnowledge,
    DrainageRequirement,
    EconomicPriority,
    FloodToleranceLevel,
    KNOWLEDGE_SCHEMA_VERSION,
    KnowledgeCollection,
    KnowledgeMetadata,
    RiskLevel,
    ValidationReport,
)


class TestEnums:
    def test_commodity_category_values(self):
        assert "sayuran_daun" in CommodityCategory.values()
        assert "sayuran_buah" in CommodityCategory.values()
        assert len(CommodityCategory.values()) == 8

    def test_flood_tolerance_values(self):
        assert "Sangat Tinggi" in FloodToleranceLevel.values()
        assert "Sangat Rendah" in FloodToleranceLevel.values()
        assert len(FloodToleranceLevel.values()) == 5

    def test_flood_tolerance_ordinal(self):
        assert FloodToleranceLevel.ordinal("Sangat Tinggi") == 5
        assert FloodToleranceLevel.ordinal("Tinggi") == 4
        assert FloodToleranceLevel.ordinal("Sedang") == 3
        assert FloodToleranceLevel.ordinal("Rendah") == 2
        assert FloodToleranceLevel.ordinal("Sangat Rendah") == 1
        assert FloodToleranceLevel.ordinal("Unknown") == 0

    def test_drainage_ordinal(self):
        assert DrainageRequirement.ordinal("Minimal") == 1
        assert DrainageRequirement.ordinal("Sangat Tinggi") == 5

    def test_economic_priority_ordinal(self):
        assert EconomicPriority.ordinal("Sangat Tinggi") == 4
        assert EconomicPriority.ordinal("Rendah") == 1

    def test_risk_level_values(self):
        assert len(RiskLevel.values()) == 3


class TestCommodityKnowledge:
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

    def test_valid_commodity_creates(self):
        c = CommodityKnowledge(**self.VALID_RECORD)
        assert c.commodity_id == "kangkung_air"
        assert c.commodity_name == "Kangkung Air"
        assert c.growing_duration_days == 25

    def test_immutable(self):
        c = CommodityKnowledge(**self.VALID_RECORD)
        with pytest.raises(ValidationError):
            c.commodity_name = "Changed"

    def test_extra_fields_forbidden(self):
        data = {**self.VALID_RECORD, "extra_field": "should_fail"}
        with pytest.raises(ValidationError):
            CommodityKnowledge(**data)

    def test_empty_id_fails(self):
        data = {**self.VALID_RECORD, "commodity_id": ""}
        with pytest.raises(ValidationError):
            CommodityKnowledge(**data)

    def test_negative_duration_fails(self):
        data = {**self.VALID_RECORD, "growing_duration_days": -1}
        with pytest.raises(ValidationError):
            CommodityKnowledge(**data)

    def test_duration_over_365_fails(self):
        data = {**self.VALID_RECORD, "growing_duration_days": 400}
        with pytest.raises(ValidationError):
            CommodityKnowledge(**data)

    def test_empty_impacts_fails(self):
        data = {**self.VALID_RECORD, "major_impacts": []}
        with pytest.raises(ValidationError):
            CommodityKnowledge(**data)

    def test_missing_required_field_fails(self):
        data = {k: v for k, v in self.VALID_RECORD.items() if k != "commodity_name"}
        with pytest.raises(ValidationError):
            CommodityKnowledge(**data)


class TestKnowledgeMetadata:
    def test_valid_metadata(self):
        meta = KnowledgeMetadata(
            schema_version="1.0",
            commodity_count=22,
            loaded_at="2026-07-08T12:00:00",
            load_duration_ms=45.2,
            validation_status="passed",
            categories=["buah", "herba"],
            vulnerability_levels=["Sangat Tinggi", "Sangat Rendah"],
        )
        assert meta.commodity_count == 22
        assert meta.validation_status == "passed"

    def test_immutable(self):
        meta = KnowledgeMetadata(
            schema_version="1.0",
            commodity_count=22,
            loaded_at="2026-07-08T12:00:00",
            load_duration_ms=45.2,
            validation_status="passed",
            categories=[],
            vulnerability_levels=[],
        )
        with pytest.raises(ValidationError):
            meta.commodity_count = 5


class TestKnowledgeCollection:
    def test_valid_collection(self, sample_commodity):
        meta = KnowledgeMetadata(
            schema_version="1.0",
            commodity_count=1,
            loaded_at="2026-07-08T12:00:00",
            load_duration_ms=10.0,
            validation_status="passed",
            categories=["sayuran_daun"],
            vulnerability_levels=["Sangat Tinggi"],
        )
        collection = KnowledgeCollection(
            commodities=[sample_commodity],
            metadata=meta,
        )
        assert len(collection.commodities) == 1
        assert collection.metadata.commodity_count == 1


class TestValidationReport:
    def test_passed_report(self):
        report = ValidationReport(
            passed=True,
            total_checks=50,
            failed_checks=0,
            errors=[],
            warnings=[],
        )
        assert report.passed
        assert report.total_checks == 50

    def test_failed_report(self):
        report = ValidationReport(
            passed=False,
            total_checks=50,
            failed_checks=2,
            errors=["error1", "error2"],
            warnings=[],
        )
        assert not report.passed
        assert len(report.errors) == 2


class TestSchemaVersion:
    def test_knowledge_schema_version(self):
        assert KNOWLEDGE_SCHEMA_VERSION == "2.1"
