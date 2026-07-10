# Knowledge Base Query Guide

## 1. Accessing the Knowledge Base

The Knowledge Base is exposed as `app.state.knowledge_base` on the FastAPI application instance.

```python
from backend.app import create_app

app = create_app()
kb = app.state.knowledge_base  # KnowledgeBase instance
```

## 2. Initialization

Initialization happens automatically on application startup via `AppStartup.warm_up`. The default data path is `backend/knowledge/data/commodity_knowledge.json`.

```python
await kb.initialize()                    # Use default path
await kb.initialize(path="custom.json")  # Custom path
```

Calling `initialize()` after the KB is already loaded is a no-op (idempotent).

## 3. Query Methods

### Get all commodities

```python
all_commodities: list[CommodityKnowledge] = kb.get_all()
```

### Get by ID

```python
kangkung: CommodityKnowledge = kb.get_by_id("kangkung")
# Raises CommodityNotFoundError if not found
```

### Get by name (case-insensitive)

```python
kangkung: CommodityKnowledge = kb.get_by_name("Kangkung")
kangkung: CommodityKnowledge = kb.get_by_name("kangkung")  # Same result
# Returns None if not found
```

### Get by category

```python
sayuran: list[CommodityKnowledge] = kb.get_by_category("sayuran_daun")
buah: list[CommodityKnowledge] = kb.get_by_category("buah")
```

### Get by vulnerability level

```python
sangat_tinggi: list[CommodityKnowledge] = kb.get_by_vulnerability("Sangat Tinggi")
```

### Check existence

```python
kb.exists("kangkung")  # True
kb.exists("nonexistent")  # False
```

### Count

```python
kb.count()  # 17
```

### List categories and vulnerability levels

```python
kb.list_categories()          # ["buah", "sayuran_buah", "sayuran_daun", ...]
kb.list_vulnerability_levels()  # ["Rendah", "Sedang", "Sangat Rendah", ...]
```

### Health status

```python
status: dict = kb.health_status()
# {"ready": true, "commodity_count": 17, "loaded_at": "2026-07-08T12:00:00", "data_path": "..."}
```

## 4. Error Handling

| Scenario | Exception |
|----------|-----------|
| KB not initialized | `KnowledgeNotLoadedError` |
| Commodity not found by ID | `CommodityNotFoundError` |
| Invalid data path | `KnowledgeLoadError` |
| Schema/validation failure | `KnowledgeValidationError` |

```python
from backend.knowledge.exceptions import (
    CommodityNotFoundError,
    KnowledgeNotLoadedError,
    KnowledgeValidationError,
)
```

## 5. Metadata

```python
meta: KnowledgeMetadata | None = kb.get_metadata()
# {
#     "schema_version": "1.0",
#     "commodity_count": 17,
#     "loaded_at": "2026-07-08T12:00:00",
#     "load_duration_ms": 12.34,
#     "validation_status": "passed",
#     "categories": [...],
#     "vulnerability_levels": [...],
# }
```
