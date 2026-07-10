# Decision Validation Specification

## 1. Validation Scope

The `DecisionValidator` performs 6 integrity checks on every `DecisionResult`:

| # | Check | Failure Condition |
|---|-------|-----------------|
| 1 | **No duplicates** | Same `commodity_id` appears in multiple groups |
| 2 | **All 17 classified** | Total commodities ≠ 17 |
| 3 | **No empty groups** | A group has zero commodities |
| 4 | **Rule coverage 100%** | All commodities evaluated by rule engine |
| 5 | **Knowledge coverage 100%** | All commodities from KB are included |
| 6 | **Explanation coverage 100%** | Every commodity has a non-empty reason |

## 2. Validation Flow

```
DecisionResult
    │
    ▼
DecisionValidator.validate_result()
    │
    ├── 1. Collect all CommodityRecommendations from all groups
    ├── 2. Check for duplicate IDs
    ├── 3. Count total commodities
    ├── 4. Check for empty groups
    ├── 5. Verify rule/knowledge/explanation coverage
    │
    ├── If any check fails → raise DecisionValidationError
    └── If all pass → return DecisionReport
```

## 3. DecisionReport

On successful validation, a `DecisionReport` is produced:

| Field | Type | Description |
|-------|------|-------------|
| `total_commodities` | int | Total classified |
| `recommended_count` | int | Count in recommended group |
| `alternative_count` | int | Count in alternative group |
| `not_recommended_count` | int | Count in not_recommended group |
| `all_commodities_classified` | bool | True if count == 17 |
| `no_duplicates` | bool | True if all IDs unique |
| `rule_coverage_pct` | float | % of commodities with rule applied |
| `knowledge_coverage_pct` | float | % of KB commodities included |
| `explanation_coverage_pct` | float | % with non-empty explanation |

## 4. Startup Validation

During application startup, the Decision Engine validates:

1. **Knowledge Base is ready** (KB initialized)
2. **Rule Engine is valid** (all 15 rules check out)
3. **Decision Engine initializes successfully**

If any step fails, the startup fails loudly (exception propagates to FastAPI startup event).

## 5. Expected Values

| Risk Level | Recommended (min) | Alternative (min) | Not Recommended (min) |
|------------|------------------:|------------------:|----------------------:|
| Rendah     | 12                | 1                 | 2                     |
| Sedang     | 7                 | 4                 | 6                     |
| Tinggi     | 2                 | 5                 | 10                    |
