"""Logging utilities — request context propagation and structured helpers."""

from __future__ import annotations

import contextvars
import uuid

_request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


def generate_request_id() -> str:
    """Return a short random identifier for the current request."""
    return uuid.uuid4().hex[:8]


def set_request_id(rid: str) -> None:
    """Store the request ID in the current execution context."""
    _request_id_var.set(rid)


def get_request_id() -> str:
    """Retrieve the current request ID (empty string if none set)."""
    return _request_id_var.get()


def format_with_rid(logger_name: str, level: str, message: str) -> str:
    """Format a log line with request ID prefix when available."""
    rid = get_request_id()
    if rid:
        return f"[{rid}] {message}"
    return message
