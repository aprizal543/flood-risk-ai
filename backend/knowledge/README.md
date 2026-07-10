# Knowledge Base Module

## Overview

The Knowledge Base module provides a structured, validated, and queryable repository of commodity knowledge for the KB-DSS (Knowledge-Based Decision Support System). It is completely independent from Machine Learning modules.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   KnowledgeBase (Facade)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Loader  │→ │Validator │→ │  Cache   │→ │   Query    │  │
│  │          │  │          │  │          │  │   Engine   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Models (Pydantic, frozen)                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Exceptions (dedicated hierarchy)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Lifecycle

```
Application Startup
        │
        ▼
  KnowledgeBase.initialize()
        │
        ├── KnowledgeLoader.load()
        │     ├── Read JSON from disk
        │     ├── Validate (schema, enums, duplicates)
        │     └── Construct CommodityKnowledge objects
        │
        ├── KnowledgeCache.load(collection)
        │     └── Build ID/name/category/vulnerability indexes
        │
        └── KnowledgeBase.is_ready = True
              │
              ▼
        Query via KnowledgeBase facade
```

## Package Structure

```
backend/knowledge/
├── __init__.py              # Exports KnowledgeBase
├── models.py                # Pydantic data models + enums
├── exceptions.py            # Exception hierarchy
├── validator.py             # Schema & integrity validation
├── loader.py                # JSON loading + validation pipeline
├── cache.py                 # Thread-safe in-memory cache
├── query.py                 # Read-only query interface
├── knowledge_base.py        # Public facade
├── README.md                # This file
└── data/
    └── commodity_knowledge.json  # Structured commodity data
```

## Usage

```python
from backend.knowledge import KnowledgeBase

# During startup:
kb = KnowledgeBase()
kb.initialize()  # Loads, validates, caches. Raises on failure.

# During requests:
kb.is_ready                  # True after successful init
kb.count()                   # 17
kangkung = kb.get_by_id("kangkung")
kb.get_by_category("sayuran_daun")
kb.get_by_vulnerability("Sangat Tinggi")
kb.exists("melon")           # True
kb.list_categories()
kb.health_status()           # For /api/health endpoint
```

## Key Design Decisions

1. **Pydantic frozen models**: Immutability guarantees thread safety and prevents accidental modification.
2. **Fail-fast startup**: If the knowledge data is invalid, the application fails to start — no silent degradation.
3. **No ML dependency**: The module never imports from `ml.*`. It is a pure backend component.
4. **Singleton cache**: Loaded once at startup. No repeated disk reads.
5. **Zero-copy lookups**: The cache stores all commodities in an immutable tuple. `get_all()` returns references, not copies.

## Adding New Commodities

1. Add the commodity record to `data/commodity_knowledge.json`
2. Bump the `version` field for the new record
3. The validator will automatically check all fields
4. Restart the application — the new commodity is available immediately
