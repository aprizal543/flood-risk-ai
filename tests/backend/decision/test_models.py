"""Tests for Decision Engine models."""

from __future__ import annotations

from datetime import datetime

import pytest

from backend.decision.models import (
    CommodityRecommendation,
    DecisionContext,
    DecisionMetadata,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
    RiskCategory,
)


class TestRiskCategory:
    def test_from_fri_rendah(self):
        assert RiskCategory.from_fri(0) == RiskCategory.RENDAH
        assert RiskCategory.from_fri(33) == RiskCategory.RENDAH

    def test_from_fri_sedang(self):
        assert RiskCategory.from_fri(34) == RiskCategory.SEDANG
        assert RiskCategory.from_fri(66) == RiskCategory.SEDANG

    def test_from_fri_tinggi(self):
        assert RiskCategory.from_fri(67) == RiskCategory.TINGGI
        assert RiskCategory.from_fri(100) == RiskCategory.TINGGI

    def test_ordinal(self):
        assert RiskCategory.ordinal("Rendah") == 1
        assert RiskCategory.ordinal("Sedang") == 2
        assert RiskCategory.ordinal("Tinggi") == 3
        assert RiskCategory.ordinal("Unknown") == 0


class TestDecisionContext:
    def test_create(self):
        ctx = DecisionContext.create(45.0)
        assert ctx.fri == 45.0
        assert ctx.risk_category == RiskCategory.SEDANG
        assert isinstance(ctx.timestamp, datetime)

    def test_create_edge_cases(self):
        assert DecisionContext.create(0.0).risk_category == RiskCategory.RENDAH
        assert DecisionContext.create(33.0).risk_category == RiskCategory.RENDAH
        assert DecisionContext.create(33.1).risk_category == RiskCategory.SEDANG
        assert DecisionContext.create(66.0).risk_category == RiskCategory.SEDANG
        assert DecisionContext.create(66.1).risk_category == RiskCategory.TINGGI
        assert DecisionContext.create(100.0).risk_category == RiskCategory.TINGGI

    def test_frozen(self):
        ctx = DecisionContext.create(50.0)
        with pytest.raises(Exception):
            ctx.fri = 99.0


class TestCommodityRecommendation:
    def test_valid_recommendation(self):
        rec = CommodityRecommendation(
            commodity_id="kangkung_air",
            commodity_name="Kangkung Air",
            recommendation_status=RecommendationStatus.RECOMMENDED,
            vulnerability_level="Sangat Tinggi",
            maximum_inundation_duration=">7 hari",
            main_impacts=["Pertumbuhan subur"],
            major_impacts=["Pertumbuhan subur"],
            damage_symptoms=["Tidak ada gejala"],
            recommendation_reason="Sangat toleran terhadap genangan",
            knowledge_reference="FAO guides",
        )
        assert rec.commodity_id == "kangkung_air"
        assert rec.recommendation_status == RecommendationStatus.RECOMMENDED

    def test_frozen(self):
        rec = CommodityRecommendation(
            commodity_id="kangkung_air",
            commodity_name="Kangkung Air",
            recommendation_status=RecommendationStatus.ALTERNATIVE,
            vulnerability_level="Sangat Tinggi",
            maximum_inundation_duration=">7 hari",
            main_impacts=[],
            major_impacts=[],
            damage_symptoms=[],
            recommendation_reason="Test",
            knowledge_reference="Test",
        )
        with pytest.raises(Exception):
            rec.commodity_id = "changed"


class TestRecommendationGroup:
    def test_group_creation(self):
        rec = CommodityRecommendation(
            commodity_id="kangkung_air",
            commodity_name="Kangkung Air",
            recommendation_status=RecommendationStatus.RECOMMENDED,
            vulnerability_level="Sangat Tinggi",
            maximum_inundation_duration=">7 hari",
            main_impacts=[],
            major_impacts=[],
            damage_symptoms=[],
            recommendation_reason="Test",
            knowledge_reference="Test",
        )
        group = RecommendationGroup(
            status=RecommendationStatus.RECOMMENDED,
            label="Direkomendasikan",
            commodities=[rec],
        )
        assert len(group.commodities) == 1
        assert group.status == RecommendationStatus.RECOMMENDED


class TestDecisionResult:
    def test_get_group(self):
        rec = CommodityRecommendation(
            commodity_id="kangkung_air",
            commodity_name="Kangkung Air",
            recommendation_status=RecommendationStatus.RECOMMENDED,
            vulnerability_level="Sangat Tinggi",
            maximum_inundation_duration=">7 hari",
            main_impacts=[],
            major_impacts=[],
            damage_symptoms=[],
            recommendation_reason="Test",
            knowledge_reference="Test",
        )
        group = RecommendationGroup(
            status=RecommendationStatus.RECOMMENDED,
            label="Direkomendasikan",
            commodities=[rec],
        )
        ctx = DecisionContext.create(50.0)
        meta = DecisionMetadata()
        report = DecisionReport(
            total_commodities=1,
            recommended_count=1,
            alternative_count=0,
            not_recommended_count=0,
            all_commodities_classified=True,
            no_duplicates=True,
            rule_coverage_pct=100.0,
            knowledge_coverage_pct=100.0,
            explanation_coverage_pct=100.0,
        )
        result = DecisionResult(context=ctx, groups=[group], metadata=meta, report=report)
        assert result.recommended == [rec]
        assert result.alternative == []
        assert result.not_recommended == []

    def test_group_not_found(self):
        ctx = DecisionContext.create(50.0)
        meta = DecisionMetadata()
        report = DecisionReport(
            total_commodities=0,
            recommended_count=0,
            alternative_count=0,
            not_recommended_count=0,
            all_commodities_classified=True,
            no_duplicates=True,
            rule_coverage_pct=100.0,
            knowledge_coverage_pct=100.0,
            explanation_coverage_pct=100.0,
        )
        result = DecisionResult(context=ctx, groups=[], metadata=meta, report=report)
        assert result.get_group(RecommendationStatus.RECOMMENDED) is None
        assert result.recommended == []
        assert result.alternative == []
        assert result.not_recommended == []


class TestDecisionMetadata:
    def test_defaults(self):
        meta = DecisionMetadata()
        assert meta.engine_version == "1.0"
        assert isinstance(meta.decision_timestamp, datetime)
        assert meta.execution_duration_ms == 0.0
        assert meta.total_rules_evaluated == 0
        assert meta.commodities_classified == 0


class TestDecisionReport:
    def test_valid_report(self):
        report = DecisionReport(
            total_commodities=22,
            recommended_count=5,
            alternative_count=5,
            not_recommended_count=12,
            all_commodities_classified=True,
            no_duplicates=True,
            rule_coverage_pct=100.0,
            knowledge_coverage_pct=100.0,
            explanation_coverage_pct=100.0,
        )
        assert report.total_commodities == 22
        assert report.recommended_count == 5
