"""Tests for the DecisionValidator."""

from __future__ import annotations

import pytest

from backend.decision.exceptions import DecisionValidationError
from backend.decision.models import (
    CommodityRecommendation,
    DecisionContext,
    DecisionMetadata,
    DecisionReport,
    DecisionResult,
    RecommendationGroup,
    RecommendationStatus,
)
from backend.decision.validator import DecisionValidator


class TestDecisionValidator:
    def _make_rec(self, cid: str, status: RecommendationStatus) -> CommodityRecommendation:
        return CommodityRecommendation(
            commodity_id=cid,
            commodity_name=cid.title(),
            recommendation_status=status,
            vulnerability_level="Sedang",
            maximum_inundation_duration="24 jam",
            main_impacts=["Main Impact"],
            major_impacts=["Impact"],
            damage_symptoms=["Symptom"],
            recommendation_reason="Test reason for " + cid,
            knowledge_reference="Ref",
        )

    def _make_result(
        self, commodities: list[CommodityRecommendation]
    ) -> DecisionResult:
        recs = [c for c in commodities if c.recommendation_status == RecommendationStatus.RECOMMENDED]
        alts = [c for c in commodities if c.recommendation_status == RecommendationStatus.ALTERNATIVE]
        nots = [c for c in commodities if c.recommendation_status == RecommendationStatus.NOT_RECOMMENDED]

        groups = [
            RecommendationGroup(status=RecommendationStatus.RECOMMENDED, label="R", commodities=recs),
            RecommendationGroup(status=RecommendationStatus.ALTERNATIVE, label="A", commodities=alts),
            RecommendationGroup(status=RecommendationStatus.NOT_RECOMMENDED, label="N", commodities=nots),
        ]
        ctx = DecisionContext.create(50.0)
        meta = DecisionMetadata()
        report = DecisionReport(
            total_commodities=len(commodities),
            recommended_count=len(recs),
            alternative_count=len(alts),
            not_recommended_count=len(nots),
            all_commodities_classified=True,
            no_duplicates=True,
            rule_coverage_pct=100.0,
            knowledge_coverage_pct=100.0,
            explanation_coverage_pct=100.0,
        )
        return DecisionResult(context=ctx, groups=groups, metadata=meta, report=report)

    def test_valid_result(self):
        commodities = []
        for i in range(22):
            cid = f"commodity_{i}"
            status = RecommendationStatus.RECOMMENDED if i < 8 else (
                RecommendationStatus.ALTERNATIVE if i < 15 else RecommendationStatus.NOT_RECOMMENDED
            )
            commodities.append(self._make_rec(cid, status))
        result = self._make_result(commodities)
        report = DecisionValidator.validate_result(result)
        assert report.all_commodities_classified is True
        assert report.no_duplicates is True

    def test_duplicate_ids_raises(self):
        commodities = [
            self._make_rec("same_id", RecommendationStatus.RECOMMENDED),
            self._make_rec("same_id", RecommendationStatus.ALTERNATIVE),
        ]
        result = self._make_result(commodities)
        with pytest.raises(DecisionValidationError) as exc:
            DecisionValidator.validate_result(result)
        assert "duplicate" in str(exc.value).lower()

    def test_missing_commodities_raises(self):
        commodities = [self._make_rec("only_one", RecommendationStatus.RECOMMENDED)]
        result = self._make_result(commodities)
        with pytest.raises(DecisionValidationError) as exc:
            DecisionValidator.validate_result(result)
        assert "Expected 22" in str(exc.value)

    def test_empty_group_raises(self):
        commodities = []
        for i in range(22):
            commodities.append(self._make_rec(f"c{i}", RecommendationStatus.RECOMMENDED))
        result = self._make_result(commodities)
        with pytest.raises(DecisionValidationError) as exc:
            DecisionValidator.validate_result(result)
        assert "empty" in str(exc.value).lower()

    def test_missing_explanation_raises(self):
        commodities = []
        for i in range(7):
            c = self._make_rec(f"c{i}", RecommendationStatus.RECOMMENDED)
            commodities.append(c)
        # Add one more with empty reason to trigger the break in explanation check
        bad = self._make_rec("bad_c", RecommendationStatus.ALTERNATIVE)
        bad_dict = dict(bad)
        bad_dict["recommendation_reason"] = ""
        bad_fixed = CommodityRecommendation(**bad_dict)
        commodities.append(bad_fixed)
        for i in range(14):
            commodities.append(self._make_rec(f"d{i}", RecommendationStatus.NOT_RECOMMENDED))

        result = self._make_result(commodities)
        with pytest.raises(DecisionValidationError) as exc:
            DecisionValidator.validate_result(result)
        assert "explanation" in str(exc.value).lower()

    def test_count_by_status(self):
        commodities = [
            self._make_rec("a", RecommendationStatus.RECOMMENDED),
            self._make_rec("b", RecommendationStatus.ALTERNATIVE),
            self._make_rec("c", RecommendationStatus.NOT_RECOMMENDED),
        ]
        result = self._make_result(commodities)
        with pytest.raises(DecisionValidationError):
            DecisionValidator.validate_result(result)
