"""Exception hierarchy for the Decision Engine."""


class DecisionEngineError(Exception):
    """Base exception for all Decision Engine errors."""

    def __init__(self, message: str = "Decision Engine error") -> None:
        self.message = message
        super().__init__(message)


class DecisionNotInitializedError(DecisionEngineError):
    """Raised when querying before initialization."""

    def __init__(self) -> None:
        super().__init__("Decision Engine has not been initialized yet")


class DecisionRuleError(DecisionEngineError):
    """Raised when a rule definition is invalid."""

    def __init__(self, rule_id: str, detail: str) -> None:
        self.rule_id = rule_id
        self.detail = detail
        super().__init__(f"Rule '{rule_id}' error: {detail}")


class DecisionValidationError(DecisionEngineError):
    """Raised when validation fails."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        msg = "; ".join(errors)
        super().__init__(f"Decision validation failed: {msg}")


class DecisionContextError(DecisionEngineError):
    """Raised when the decision context is invalid."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(f"Invalid decision context: {detail}")


class DecisionKnowledgeError(DecisionEngineError):
    """Raised when Knowledge Base is unavailable or incompatible."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(f"Knowledge Base error: {detail}")
