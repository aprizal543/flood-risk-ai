"""Tests for the RiskMapper."""

from __future__ import annotations


from backend.decision.mapper import RiskMapper
from backend.decision.models import RiskCategory
from backend.knowledge.models import CommodityKnowledge


class TestRiskMapper:
    def setup_method(self):
        self.mapper = RiskMapper()

    def test_to_risk_category_rendah(self):
        assert self.mapper.to_risk_category(20) == RiskCategory.RENDAH

    def test_to_risk_category_sedang(self):
        assert self.mapper.to_risk_category(50) == RiskCategory.SEDANG

    def test_to_risk_category_tinggi(self):
        assert self.mapper.to_risk_category(80) == RiskCategory.TINGGI

    def test_to_risk_level_str(self):
        assert self.mapper.to_risk_level_str(20) == "Rendah"
        assert self.mapper.to_risk_level_str(50) == "Sedang"
        assert self.mapper.to_risk_level_str(80) == "Tinggi"

    def test_vulnerability_ordinal(self):
        assert self.mapper.vulnerability_ordinal("Sangat Tinggi") == 5
        assert self.mapper.vulnerability_ordinal("Tinggi") == 4
        assert self.mapper.vulnerability_ordinal("Sedang") == 3
        assert self.mapper.vulnerability_ordinal("Rendah") == 2
        assert self.mapper.vulnerability_ordinal("Sangat Rendah") == 1
        assert self.mapper.vulnerability_ordinal("Unknown") == 0

    def test_risk_ordinal(self):
        assert self.mapper.risk_ordinal("Rendah") == 1
        assert self.mapper.risk_ordinal("Sedang") == 2
        assert self.mapper.risk_ordinal("Tinggi") == 3

    def test_commodity_to_dict(self):
        c = CommodityKnowledge(
            commodity_id="test",
            commodity_name="Test",
            aliases=[],
            kelompok_kerentanan=["Sedang"],
            tingkat_kerentanan="Sedang (Moderate)",
            batas_toleransi_genangan="24 jam",
        dampak_utama=["Dampak sedang"],
        gejala_kerusakan=["Gejala sedang"],
        main_impacts=["Dampak sedang"],
        damage_symptoms=["Gejala sedang"],
        commodity_category="sayuran_daun",
            vulnerability_level="Sedang",
            flood_tolerance_category="Sedang",
            maximum_inundation_duration="24 jam",
            drainage_requirement="Sedang",
            growing_duration_days=30,
            optimal_risk_level="Rendah",
            economic_priority="Sedang",
            major_impacts=["A"],
            recommendation_notes="Note",
            scientific_reference="Ref",
            version="2.0",
            last_updated="2026-07-10",
        )
        d = self.mapper.commodity_to_dict(c)
        assert d["commodity_id"] == "test"
        assert d["commodity_name"] == "Test"
        assert d["vulnerability_level"] == "Sedang"

    def test_create_context(self):
        ctx = self.mapper.create_context(55.0)
        assert ctx.fri == 55.0
        assert ctx.risk_category == RiskCategory.SEDANG
