"""Complete validation logic for Knowledge Base data.

Performs multi-layered validation:
  1. Schema version check
  2. Duplicate commodity_id detection
  3. Required field presence (both lecturer-derived and deprecated)
  4. Empty string / zero-length checks
  5. Enum value validity
  6. Duration format sanity
  7. List field completeness
"""

from __future__ import annotations

from typing import Any

from backend.knowledge.exceptions import KnowledgeValidationError
from backend.knowledge.models import (
    CommodityCategory,
    DrainageRequirement,
    EconomicPriority,
    FloodToleranceLevel,
    KNOWLEDGE_SCHEMA_VERSION,
    RiskLevel,
    ValidationReport,
)

# ── Required lecturer-derived fields (source of truth) ──────────────
REQUIRED_LECTURER_FIELDS: list[str] = [
    "commodity_id",
    "commodity_name",
    "aliases",
    "kelompok_kerentanan",
    "tingkat_kerentanan",
    "batas_toleransi_genangan",
    "dampak_utama",
    "gejala_kerusakan",
    "main_impacts",
    "damage_symptoms",
]

# ── Required deprecated fields (kept for backward compat) ───────────
REQUIRED_DEPRECATED_FIELDS: list[str] = [
    "commodity_category",
    "vulnerability_level",
    "flood_tolerance_category",
    "maximum_inundation_duration",
    "drainage_requirement",
    "growing_duration_days",
    "optimal_risk_level",
    "economic_priority",
    "major_impacts",
    "recommendation_notes",
    "scientific_reference",
    "version",
    "last_updated",
]

REQUIRED_FIELDS: list[str] = REQUIRED_LECTURER_FIELDS + REQUIRED_DEPRECATED_FIELDS

ENUM_FIELDS: dict[str, set[str]] = {
    "commodity_category": set(CommodityCategory.values()),
    "vulnerability_level": set(FloodToleranceLevel.values()),
    "flood_tolerance_category": set(FloodToleranceLevel.values()),
    "drainage_requirement": set(DrainageRequirement.values()),
    "optimal_risk_level": set(RiskLevel.values()),
    "economic_priority": set(EconomicPriority.values()),
}

REQUIRED_LIST_FIELDS: list[str] = [
    "kelompok_kerentanan",
    "dampak_utama",
    "gejala_kerusakan",
    "main_impacts",
    "damage_symptoms",
    "major_impacts",
]

OPTIONAL_LIST_FIELDS: list[str] = [
    "aliases",
]


def validate_schema_version(version: str) -> list[str]:
    """Check that the data schema version matches the expected version."""
    errors: list[str] = []
    if not version:
        errors.append("Missing schema version in knowledge data")
    elif version != KNOWLEDGE_SCHEMA_VERSION:
        errors.append(
            f"Schema version mismatch: expected '{KNOWLEDGE_SCHEMA_VERSION}', "
            f"got '{version}'"
        )
    return errors


def validate_commodity_record(
    record: dict[str, Any],
    index: int,
) -> list[str]:
    """Validate a single commodity record. Returns a list of error strings."""
    errors: list[str] = []

    # ── Required field presence ─────────────────────────────────────
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(
                f"Record [{index}] missing required field: '{field}'"
            )
            continue

        value = record[field]
        if value is None:
            errors.append(
                f"Record [{index}] field '{field}' is null"
            )
        elif isinstance(value, str) and value.strip() == "":
            errors.append(
                f"Record [{index}] field '{field}' is empty string"
            )

    # ── Enum validation ─────────────────────────────────────────────
    for field, valid_values in ENUM_FIELDS.items():
        val = record.get(field)
        if val is not None and val not in valid_values:
            errors.append(
                f"Record [{index}] field '{field}' has invalid value "
                f"'{val}'. Valid: {sorted(valid_values)}"
            )

    # ── Integer field validation ────────────────────────────────────
    dur = record.get("growing_duration_days")
    if dur is not None:
        if not isinstance(dur, int) or isinstance(dur, bool):
            errors.append(
                f"Record [{index}] 'growing_duration_days' must be an "
                f"integer, got {type(dur).__name__}"
            )
        elif dur <= 0 or dur >= 365:
            errors.append(
                f"Record [{index}] 'growing_duration_days'={dur} out of "
                f"range (1-364)"
            )

    # ── List field validation (required) ────────────────────────────
    for field in REQUIRED_LIST_FIELDS:
        val = record.get(field)
        if val is not None:
            if not isinstance(val, list):
                errors.append(
                    f"Record [{index}] field '{field}' must be a list, "
                    f"got {type(val).__name__}"
                )
            elif len(val) == 0:
                errors.append(
                    f"Record [{index}] field '{field}' is an empty list"
                )
            else:
                for i, item in enumerate(val):
                    if not isinstance(item, str) or item.strip() == "":
                        errors.append(
                            f"Record [{index}] field '{field}'[{i}] is "
                            f"empty or not a string"
                        )

    # ── List field validation (optional — allowed to be empty) ──────
    for field in OPTIONAL_LIST_FIELDS:
        val = record.get(field)
        if val is not None:
            if not isinstance(val, list):
                errors.append(
                    f"Record [{index}] field '{field}' must be a list, "
                    f"got {type(val).__name__}"
                )
            else:
                for i, item in enumerate(val):
                    if not isinstance(item, str) or item.strip() == "":
                        errors.append(
                            f"Record [{index}] field '{field}'[{i}] is "
                            f"empty or not a string"
                        )

    # ── Duration format sanity check ────────────────────────────────
    dur_str = record.get("batas_toleransi_genangan")
    if dur_str is not None and isinstance(dur_str, str):
        dur_str = dur_str.strip()
        if not dur_str:
            errors.append(
                f"Record [{index}] 'batas_toleransi_genangan' is "
                f"empty string"
            )

    # ── Version field check ─────────────────────────────────────────
    ver = record.get("version")
    if ver is not None and isinstance(ver, str) and not ver.strip():
        errors.append(f"Record [{index}] 'version' is empty string")

    # ── last_updated format check ───────────────────────────────────
    lu = record.get("last_updated")
    if lu is not None and isinstance(lu, str):
        lu = lu.strip()
        if not lu:
            errors.append(f"Record [{index}] 'last_updated' is empty string")

    return errors


def validate_knowledge_data(
    data: list[dict[str, Any]],
    schema_version: str | None = None,
) -> ValidationReport:
    """Validate a complete knowledge data list.

    Args:
        data: List of commodity dicts loaded from JSON.
        schema_version: Optional top-level schema version to check.

    Returns:
        ValidationReport with passed/failed status and error details.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # ── Schema version check ────────────────────────────────────────
    if schema_version is not None:
        errors.extend(validate_schema_version(schema_version))

    # ── Empty data check ────────────────────────────────────────────
    if not data:
        errors.append("Knowledge data is empty")
        return ValidationReport(
            passed=False,
            total_checks=1,
            failed_checks=1,
            errors=errors,
            warnings=warnings,
        )

    # ── Duplicate commodity_id check ────────────────────────────────
    seen_ids: dict[str, int] = {}
    for i, record in enumerate(data):
        cid = record.get("commodity_id", "")
        if cid in seen_ids:
            errors.append(
                f"Duplicate commodity_id '{cid}' at records "
                f"[{seen_ids[cid]}] and [{i}]"
            )
        seen_ids[cid] = i

    # ── Per-record validation ───────────────────────────────────────
    for i, record in enumerate(data):
        errors.extend(validate_commodity_record(record, i))

    # ── Commodity existence validation (against lecturer doc) ───────
    lecturer_commodity_ids = {
        "cabai", "tomat", "bawang_merah", "kentang", "paprika",
        "kubis", "pakcoy", "sawi", "terong", "mentimun", "kacang_panjang",
        "wortel", "lobak", "labu_siam", "buncis",
        "kangkung_air", "genjer", "selada_air", "talas",
        "seledri", "pakis_sayur", "semanggi",
    }

    actual_ids = set(seen_ids.keys())
    missing = lecturer_commodity_ids - actual_ids
    extra = actual_ids - lecturer_commodity_ids

    if missing:
        errors.append(
            f"Missing lecturer commodities: {sorted(missing)}"
        )
    if extra:
        errors.append(
            f"Unsupported commodities (not in lecturer doc): {sorted(extra)}"
        )

    # ── Kelompok kerentanan validation ──────────────────────────────
    valid_kelompok = {"Tinggi", "Sedang", "Rendah"}
    for i, record in enumerate(data):
        kk = record.get("kelompok_kerentanan", [])
        for k in kk:
            if k not in valid_kelompok:
                errors.append(
                    f"Record [{i}] invalid kelompok_kerentanan '{k}'. "
                    f"Valid: {sorted(valid_kelompok)}"
                )

    # ── Count checks ────────────────────────────────────────────────
    total_checks = (
        1  # empty data
        + (1 if schema_version else 0)  # schema version
        + len(seen_ids)  # duplicates check
        + len(data) * len(REQUIRED_FIELDS)  # field presence
        + len(data) * len(ENUM_FIELDS)  # enum validity
        + len(data)  # growing_duration_days type
        + len(data) * len(REQUIRED_LIST_FIELDS)  # list fields
        + (1 if missing or extra else 0)  # lecturer existence check
        + len(data)  # kelompok_kerentanan validity
    )

    passed = len(errors) == 0

    return ValidationReport(
        passed=passed,
        total_checks=total_checks,
        failed_checks=len(errors),
        errors=errors,
        warnings=warnings,
    )


def assert_valid(
    data: list[dict[str, Any]],
    schema_version: str | None = None,
) -> None:
    """Validate and raise KnowledgeValidationError on failure.

    This is the fail-fast entry point used during startup.
    """
    report = validate_knowledge_data(data, schema_version)
    if not report.passed:
        raise KnowledgeValidationError(report.errors)
