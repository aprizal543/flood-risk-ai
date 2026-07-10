"""Tests for Decision Engine exceptions."""

from __future__ import annotations

from backend.decision.exceptions import (
    DecisionContextError,
    DecisionEngineError,
    DecisionKnowledgeError,
    DecisionNotInitializedError,
    DecisionRuleError,
    DecisionValidationError,
)


class TestDecisionEngineError:
    def test_base_exception(self):
        err = DecisionEngineError("test error")
        assert str(err) == "test error"
        assert err.message == "test error"

    def test_default_message(self):
        err = DecisionEngineError()
        assert str(err) == "Decision Engine error"


class TestDecisionNotInitializedError:
    def test_message(self):
        err = DecisionNotInitializedError()
        assert "not been initialized" in str(err)


class TestDecisionRuleError:
    def test_with_rule_id(self):
        err = DecisionRuleError("rule_01", "invalid condition")
        assert "rule_01" in str(err)
        assert err.rule_id == "rule_01"
        assert err.detail == "invalid condition"


class TestDecisionValidationError:
    def test_with_errors(self):
        err = DecisionValidationError(["error1", "error2"])
        assert "error1" in str(err)
        assert len(err.errors) == 2

    def test_empty_errors(self):
        err = DecisionValidationError([])
        assert "validation failed" in str(err).lower()


class TestDecisionContextError:
    def test_with_detail(self):
        err = DecisionContextError("FRI out of range")
        assert "FRI out of range" in str(err)
        assert err.detail == "FRI out of range"


class TestDecisionKnowledgeError:
    def test_with_detail(self):
        err = DecisionKnowledgeError("KB not loaded")
        assert "KB not loaded" in str(err)
        assert err.detail == "KB not loaded"


class TestExceptionHierarchy:
    def test_all_are_decision_engine_errors(self):
        errors = [
            DecisionNotInitializedError(),
            DecisionRuleError("r", "d"),
            DecisionValidationError([]),
            DecisionContextError("d"),
            DecisionKnowledgeError("d"),
        ]
        for err in errors:
            assert isinstance(err, DecisionEngineError)
