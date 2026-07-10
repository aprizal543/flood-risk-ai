"""Dedicated exception hierarchy for the Knowledge Base module."""


class KnowledgeBaseError(Exception):
    """Base exception for all Knowledge Base errors."""

    def __init__(self, message: str = "Knowledge Base error") -> None:
        self.message = message
        super().__init__(self.message)


class KnowledgeLoadError(KnowledgeBaseError):
    """Raised when knowledge data cannot be loaded from the source file."""

    def __init__(self, path: str, detail: str = "") -> None:
        msg = f"Failed to load knowledge from {path}"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class KnowledgeValidationError(KnowledgeBaseError):
    """Raised when knowledge data fails validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        msg = f"Knowledge validation failed with {len(errors)} error(s)"
        super().__init__(msg)


class CommodityNotFoundError(KnowledgeBaseError):
    """Raised when a requested commodity ID does not exist."""

    def __init__(self, commodity_id: str) -> None:
        self.commodity_id = commodity_id
        super().__init__(f"Commodity not found: '{commodity_id}'")


class KnowledgeVersionError(KnowledgeBaseError):
    """Raised when the knowledge schema version is incompatible."""

    def __init__(self, expected: str, actual: str) -> None:
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Knowledge schema version mismatch: expected '{expected}', "
            f"got '{actual}'"
        )


class KnowledgeNotLoadedError(KnowledgeBaseError):
    """Raised when the Knowledge Base has not been loaded yet."""

    def __init__(self) -> None:
        super().__init__("Knowledge Base has not been loaded yet")
