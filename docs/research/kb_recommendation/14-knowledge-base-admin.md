# Knowledge Base Administration Guide

## 1. Overview

The Knowledge Base is a single-file JSON dataset (`backend/knowledge/data/commodity_knowledge.json`) managed through code review. There is no admin UI — all changes go through the standard development workflow.

## 2. Adding a New Commodity

### Step 1: Research
- Gather scientific references for the commodity's flood tolerance, inundation duration, and drainage needs.
- If no reference exists, mark `scientific_reference` with `[Assumption] — reason` and set `version` to `0.1` (preliminary).

### Step 2: Edit the JSON
Add a new object to the `commodity_knowledge.json` array:

```json
{
  "commodity_id": "new_commodity",
  "commodity_name": "New Commodity",
  "commodity_category": "sayuran_daun",
  "vulnerability_level": "Sedang",
  "flood_tolerance_category": "Sedang",
  "maximum_inundation_duration": "1-2 hari",
  "drainage_requirement": "Sedang",
  "growing_duration_days": 60,
  "optimal_risk_level": "Sedang",
  "economic_priority": "Sedang",
  "major_impacts": ["Impact description"],
  "damage_symptoms": ["Symptom description"],
  "recommendation_notes": "Planting guidance.",
  "scientific_reference": "[Source] — Title",
  "version": "1.0",
  "last_updated": "2026-07-08"
}
```

### Step 3: Verify
```bash
# Run all KB tests
python -m pytest tests/backend/knowledge/ -v --tb=short

# Run the full test suite
python -m pytest tests/backend/knowledge/test_integration.py -v --tb=short
```

### Step 4: Update test assertions
If the total commodity count changes, update the `test_exactly_17_commodities` assertion in `tests/backend/knowledge/test_integration.py`.

## 3. Editing an Existing Commodity

- Update the relevant fields in the JSON object.
- Bump the `version` field (e.g., `1.0` → `1.1`).
- Update `last_updated` to the current date.
- Update `scientific_reference` if the edit is based on new research.

## 4. Removing a Commodity

- Remove the JSON object from the array.
- **Do not reuse commodity_ids** — IDs are permanent for traceability.
- Update the count assertion if needed.
- Consider adding a deprecation note in the commit message.

## 5. Schema Changes

### Adding a new field
1. Update the `CommodityKnowledge` model in `backend/knowledge/models.py`.
2. Update the schema section in `01_KNOWLEDGE_BASE_SPECIFICATION.md`.
3. Update the data dictionary in `12-knowledge-data-dictionary.md`.
4. If the field is required, ensure all 17 records have it populated.
5. Run the full test suite.

### Changing enum values
1. Update the enum class in `backend/knowledge/models.py`.
2. Update all affected commodity records in the JSON.
3. Update documentation.
4. Run the full test suite.

### Removing a field
- Mark as optional first, then remove in a subsequent sprint.
- Never remove a required field without a schema version bump.

## 6. Data Integrity Checks

Run these regularly:

```bash
# Full integrity check
python -m pytest tests/backend/knowledge/test_integration.py::TestDatasetIntegrity -v

# Individual checks
python -c "
from backend.knowledge.knowledge_base import KnowledgeBase
import asyncio

async def check():
    kb = KnowledgeBase()
    await kb.initialize()
    print(f'Commodities: {kb.count()}')
    print(f'Categories: {kb.list_categories()}')
    print(f'Vulnerability levels: {kb.list_vulnerability_levels()}')
    print(f'Ready: {kb.health_status()["ready"]}')

asyncio.run(check())
"
```

## 7. Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `KnowledgeValidationError` on startup | Invalid enum value or missing field | Check the JSON against the model |
| `KnowledgeLoadError` | File not found or invalid JSON | Verify the data path and JSON syntax |
| Test count assertion fails | Commodity count changed | Update the assertion |
| Duplicate ID error | Two records share a `commodity_id` | Rename one of them |

## 8. Deployment Notes

- The JSON file is deployed as part of the application code (not a separate artifact).
- No migration scripts needed — the schema is forward-compatible.
- Monitoring: the `/health` endpoint reports KB readiness. Alert on `knowledge.ready == false`.
