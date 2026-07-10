"""Tests for the InferenceRuleEngine."""

from __future__ import annotations

import pytest

from backend.decision.models import RecommendationStatus
from backend.decision.rules import InferenceRuleEngine


class TestInferenceRuleEngine:
    def setup_method(self):
        self.engine = InferenceRuleEngine()

    def test_rule_count(self):
        assert self.engine.rule_count == 15

    def test_sangat_tinggi_always_recommended(self):
        for risk in ["Rendah", "Sedang", "Tinggi"]:
            status = self.engine.evaluate("Sangat Tinggi", risk)
            assert status == RecommendationStatus.RECOMMENDED

    def test_tinggi_at_rendah(self):
        assert self.engine.evaluate("Tinggi", "Rendah") == RecommendationStatus.RECOMMENDED

    def test_tinggi_at_sedang(self):
        assert self.engine.evaluate("Tinggi", "Sedang") == RecommendationStatus.RECOMMENDED

    def test_tinggi_at_tinggi(self):
        assert self.engine.evaluate("Tinggi", "Tinggi") == RecommendationStatus.ALTERNATIVE

    def test_sedang_at_rendah(self):
        assert self.engine.evaluate("Sedang", "Rendah") == RecommendationStatus.RECOMMENDED

    def test_sedang_at_sedang(self):
        assert self.engine.evaluate("Sedang", "Sedang") == RecommendationStatus.ALTERNATIVE

    def test_sedang_at_tinggi(self):
        assert self.engine.evaluate("Sedang", "Tinggi") == RecommendationStatus.NOT_RECOMMENDED

    def test_rendah_at_rendah(self):
        assert self.engine.evaluate("Rendah", "Rendah") == RecommendationStatus.ALTERNATIVE

    def test_rendah_at_sedang(self):
        assert self.engine.evaluate("Rendah", "Sedang") == RecommendationStatus.NOT_RECOMMENDED

    def test_rendah_at_tinggi(self):
        assert self.engine.evaluate("Rendah", "Tinggi") == RecommendationStatus.NOT_RECOMMENDED

    def test_sangat_rendah_all_not_recommended(self):
        for risk in ["Rendah", "Sedang", "Tinggi"]:
            status = self.engine.evaluate("Sangat Rendah", risk)
            assert status == RecommendationStatus.NOT_RECOMMENDED

    def test_unknown_vulnerability_raises(self):
        with pytest.raises(Exception):
            self.engine.evaluate("Unknown", "Rendah")

    def test_unknown_risk_raises(self):
        with pytest.raises(Exception):
            self.engine.evaluate("Sedang", "Unknown")

    def test_evaluate_all(self):
        results = self.engine.evaluate_all(
            ["Sangat Tinggi", "Tinggi", "Sedang"],
            "Sedang",
        )
        assert len(results) == 3
        assert results[0] == ("Sangat Tinggi", RecommendationStatus.RECOMMENDED)
        assert results[1] == ("Tinggi", RecommendationStatus.RECOMMENDED)
        assert results[2] == ("Sedang", RecommendationStatus.ALTERNATIVE)

    def test_is_valid(self):
        assert self.engine.is_valid is True

    def test_get_status_reason_recommended(self):
        reason = self.engine.get_status_reason("Sangat Tinggi", "Tinggi", "Kangkung")
        assert "direkomendasikan" in reason.lower()
        assert "Kangkung" in reason

    def test_get_status_reason_alternative(self):
        reason = self.engine.get_status_reason("Tinggi", "Tinggi", "Bayam")
        assert "alternatif" in reason.lower()
        assert "Bayam" in reason

    def test_get_status_reason_not_recommended(self):
        reason = self.engine.get_status_reason("Sangat Rendah", "Rendah", "Melon")
        assert "tidak direkomendasikan" in reason.lower()
        assert "Melon" in reason
