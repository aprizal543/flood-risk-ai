# Knowledge Base Error Handling

## 1. Exception Hierarchy

```
KnowledgeBaseError (base)
├── KnowledgeLoadError          — File I/O and JSON parse failures
├── KnowledgeValidationError    — Schema validation failures
├── CommodityNotFoundError      — Unknown commodity ID lookups
├── KnowledgeVersionError       — Schema version mismatch
└── KnowledgeNotLoadedError     — Query before initialization
```

All exceptions live in `backend/knowledge/exceptions.py`.

## 2. Exception Details

### `KnowledgeBaseError`
- Base for all KB exceptions.
- Accepts an optional `message` (default: `"Knowledge base error"`).
- All subclasses inherit from this, so `except KnowledgeBaseError` catches any KB error.

### `KnowledgeLoadError`
- Raised when the JSON file cannot be read or parsed.
- Accepts `path` (the file path) and `detail` (underlying error message).
- `str()` format: `"Failed to load knowledge base from {path}: {detail}"`

### `KnowledgeValidationError`
- Raised when data fails schema validation.
- Accepts `errors` (list of error message strings).
- `str()` format: `"Knowledge validation failed with {N} error(s)"`
- Individual errors accessible via `.errors` attribute.

### `CommodityNotFoundError`
- Raised by `get_by_id()` when the commodity ID does not exist in the loaded data.
- Accepts `commodity_id` parameter.
- `str()` format: `"Commodity '{id}' not found in knowledge base"`

### `KnowledgeVersionError`
- Raised when the JSON schema version does not match the expected version.
- Accepts `expected` and `found` version strings.
- `str()` format: `"Schema version mismatch: expected {expected}, found {found}"`

### `KnowledgeNotLoadedError`
- Raised when any query method is called before `initialize()`.
- Default message: `"Knowledge base has not been loaded yet"`

## 3. Error Propagation

### In the loader (`loader.py`)
```
JSONDecodeError → KnowledgeLoadError
OSError         → KnowledgeLoadError
validate() fail → KnowledgeValidationError
```

### In the knowledge base facade (`knowledge_base.py`)
```
KnowledgeNotLoadedError  — any query before initialize()
CommodityNotFoundError   — get_by_id with unknown ID
KnowledgeLoadError       — invalid path passed to initialize()
KnowledgeValidationError — invalid data file passed to initialize()
```

### In the validator (`validator.py`)
```
KnowledgeValidationError — always, with list of individual errors
KnowledgeVersionError   — schema version mismatch
```

## 4. Health Endpoint Error Handling

The `/health` endpoint always succeeds. If the KB is not loaded, the `knowledge` field shows:

```json
{
  "knowledge": {
    "ready": false,
    "commodity_count": 0,
    "loaded_at": null,
    "data_path": null
  }
}
```

This ensures monitoring tools never see a `5xx` response due to KB state.

## 5. Quick Reference

| Condition | Exception | Where Raised |
|-----------|-----------|--------------|
| File not found | `KnowledgeLoadError` | `loader.load()` |
| Invalid JSON | `KnowledgeLoadError` | `loader.load()` |
| Missing required field | `KnowledgeValidationError` | `validator.validate()` |
| Invalid enum value | `KnowledgeValidationError` | `validator.validate()` |
| Duplicate commodity_id | `KnowledgeValidationError` | `validator.validate()` |
| Missing commodity | `CommodityNotFoundError` | `kb.get_by_id()` |
| Query before init | `KnowledgeNotLoadedError` | All `kb.*` query methods |
| Schema version mismatch | `KnowledgeVersionError` | `validator.validate()` |
