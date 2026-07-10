"""Unit tests for the Knowledge Base exception hierarchy."""

from __future__ import annotations

from backend.knowledge.exceptions import (
    CommodityNotFoundError,
    KnowledgeBaseError,
    KnowledgeLoadError,
    KnowledgeNotLoadedError,
    KnowledgeValidationError,
    KnowledgeVersionError,
)


class TestKnowledgeBaseError:
    def test_base_exception(self):
        exc = KnowledgeBaseError("test error")
        assert str(exc) == "test error"
        assert isinstance(exc, Exception)

    def test_default_message(self):
        exc = KnowledgeBaseError()
        assert "Knowledge Base error" in str(exc)


class TestKnowledgeLoadError:
    def test_with_path(self):
        exc = KnowledgeLoadError("/path/to/file.json")
        assert "/path/to/file.json" in str(exc)

    def test_with_detail(self):
        exc = KnowledgeLoadError("file.json", "File not found")
        assert "file.json" in str(exc)
        assert "File not found" in str(exc)


class TestKnowledgeValidationError:
    def test_with_errors(self):
        errors = ["Field X missing", "Field Y invalid"]
        exc = KnowledgeValidationError(errors)
        assert exc.errors == errors
        assert "2 error(s)" in str(exc)

    def test_empty_errors(self):
        exc = KnowledgeValidationError([])
        assert "0 error(s)" in str(exc)


class TestCommodityNotFoundError:
    def test_with_id(self):
        exc = CommodityNotFoundError("kangkung_air")
        assert exc.commodity_id == "kangkung_air"
        assert "kangkung_air" in str(exc)


class TestKnowledgeVersionError:
    def test_mismatch(self):
        exc = KnowledgeVersionError(expected="1.0", actual="2.0")
        assert exc.expected == "1.0"
        assert exc.actual == "2.0"
        assert "1.0" in str(exc)
        assert "2.0" in str(exc)


class TestKnowledgeNotLoadedError:
    def test_default_message(self):
        exc = KnowledgeNotLoadedError()
        assert "not been loaded" in str(exc)


class TestExceptionHierarchy:
    def test_all_are_knowledge_base_errors(self):
        assert isinstance(KnowledgeLoadError("x"), KnowledgeBaseError)
        assert isinstance(KnowledgeValidationError([]), KnowledgeBaseError)
        assert isinstance(CommodityNotFoundError("x"), KnowledgeBaseError)
        assert isinstance(KnowledgeVersionError("1", "2"), KnowledgeBaseError)
        assert isinstance(KnowledgeNotLoadedError(), KnowledgeBaseError)
        assert isinstance(KnowledgeBaseError(), Exception)
