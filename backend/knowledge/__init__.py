"""Knowledge Base Package — Structured commodity knowledge for KB-DSS.

This package implements the knowledge layer of the Knowledge-Based Decision
Support System. It is completely independent from Machine Learning modules.

Modules:
    models:       Strongly-typed commodity knowledge models (Pydantic)
    exceptions:   Dedicated exception hierarchy
    validator:    Schema, enum, and integrity validation
    loader:       JSON loading, validation, and object construction
    cache:        Thread-safe read-only in-memory cache
    query:        Read-only query interface
    knowledge_base: Facade combining all components
"""

from backend.knowledge.knowledge_base import KnowledgeBase

__all__ = ["KnowledgeBase"]
