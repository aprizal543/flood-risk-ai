"""Tests for the ExplainabilityEngine."""

from __future__ import annotations


from backend.decision.explainability import ExplainabilityEngine
from backend.decision.models import RecommendationStatus
from backend.knowledge.models import CommodityKnowledge


class TestExplainabilityEngine:
    def setup_method(self):
        self.engine = ExplainabilityEngine()
        self.kangkung = CommodityKnowledge(
            commodity_id="kangkung_air",
            commodity_name="Kangkung Air",
            aliases=[],
            kelompok_kerentanan=["Tinggi", "Rendah"],
            tingkat_kerentanan="Toleran (Tolerant)",
            batas_toleransi_genangan="Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
            dampak_utama=["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
            gejala_kerusakan=["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
            main_impacts=["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
            damage_symptoms=["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
            commodity_category="sayuran_daun",
            vulnerability_level="Sangat Tinggi",
            flood_tolerance_category="Sangat Tinggi",
            maximum_inundation_duration=">7 hari",
            drainage_requirement="Minimal",
            growing_duration_days=25,
            optimal_risk_level="Tinggi",
            economic_priority="Sangat Tinggi",
            major_impacts=["Pertumbuhan subur di genangan"],
            recommendation_notes="Ideal untuk area rawan banjir.",
            scientific_reference="FAO guides [Pending]",
            version="2.0",
            last_updated="2026-07-10",
        )
        self.cabai = CommodityKnowledge(
            commodity_id="cabai",
            commodity_name="Cabai",
            aliases=[],
            kelompok_kerentanan=["Tinggi"],
            tingkat_kerentanan="Sangat Rentan (Highly Sensitive)",
            batas_toleransi_genangan="Kurang dari 24 jam",
            dampak_utama=["Akar langsung membusuk akibat ketiadaan oksigen"],
            gejala_kerusakan=["Daun menguning (klorosis)"],
            main_impacts=["Akar langsung membusuk akibat ketiadaan oksigen"],
            damage_symptoms=["Daun menguning (klorosis)"],
            commodity_category="sayuran_buah",
            vulnerability_level="Sangat Rendah",
            flood_tolerance_category="Sangat Rendah",
            maximum_inundation_duration="Kurang dari 24 jam",
            drainage_requirement="Tinggi",
            growing_duration_days=90,
            optimal_risk_level="Rendah",
            economic_priority="Tinggi",
            major_impacts=["Buah kontak tanah sangat rentan"],
            recommendation_notes="Sangat sensitif genangan.",
            scientific_reference="Cabai production [Pending]",
            version="2.0",
            last_updated="2026-07-10",
        )

    def test_recommended_reason(self):
        reason = self.engine.generate_reason(
            self.kangkung, RecommendationStatus.RECOMMENDED, "Tinggi"
        )
        assert "direkomendasikan" in reason.lower()
        assert "Kangkung Air" in reason
        assert "sangat toleran" in reason.lower()

    def test_not_recommended_reason(self):
        reason = self.engine.generate_reason(
            self.cabai, RecommendationStatus.NOT_RECOMMENDED, "Tinggi"
        )
        assert "tidak direkomendasikan" in reason.lower()
        assert "Cabai" in reason
        assert "sangat rentan" in reason.lower()

    def test_alternative_reason(self):
        sawi = CommodityKnowledge(
            commodity_id="sawi",
            commodity_name="Sawi",
            aliases=[],
            kelompok_kerentanan=["Rendah"],
            tingkat_kerentanan="Rentan (Sensitive)",
            batas_toleransi_genangan="24-48 jam",
            dampak_utama=["Daun menguning dan pertumbuhan terhambat"],
            gejala_kerusakan=["Nekrosis pada tepi daun"],
            main_impacts=["Daun menguning dan pertumbuhan terhambat"],
            damage_symptoms=["Nekrosis pada tepi daun"],
            commodity_category="sayuran_daun",
            vulnerability_level="Rendah",
            flood_tolerance_category="Rendah",
            maximum_inundation_duration="24-48 jam",
            drainage_requirement="Rendah",
            growing_duration_days=30,
            optimal_risk_level="Sedang",
            economic_priority="Sangat Tinggi",
            major_impacts=["A"],
            recommendation_notes="Note",
            scientific_reference="Ref",
            version="2.0",
            last_updated="2026-07-10",
        )
        reason = self.engine.generate_reason(
            sawi, RecommendationStatus.ALTERNATIVE, "Tinggi"
        )
        assert "alternatif" in reason.lower()
        assert "Sawi" in reason
        assert "kurang toleran" in reason.lower()

    def test_detailed_explanation(self):
        detail = self.engine.generate_detailed_explanation(
            self.kangkung, RecommendationStatus.RECOMMENDED, "Tinggi"
        )
        assert "ringkasan" in detail
        assert "faktor_utama" in detail
        assert "dampak_utama" in detail
        assert "gejala_kerusakan" in detail
        assert "durasi_tanam_hari" in detail
        assert "referensi" in detail
        assert len(detail["faktor_utama"]) == 3
