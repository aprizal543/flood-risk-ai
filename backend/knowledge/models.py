"""Strongly-typed data models for the Knowledge Base.

Uses Pydantic BaseModel with frozen=True to enforce immutability
and extra='forbid' to reject unknown fields.
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from pydantic import BaseModel, Field


class CommodityCategory(str, Enum):
    """Agronomic commodity categories (DEPRECATED — not from lecturer doc)."""

    SAYURAN_DAUN = "sayuran_daun"
    SAYURAN_BUAH = "sayuran_buah"
    SAYURAN_SEREALIA = "sayuran_serealia"
    KACANG_KACANGAN = "kacang-kacangan"
    UMBI = "umbi"
    BUAH = "buah"
    HERBA = "herba"
    SAYURAN_UMBI = "sayuran_umbi"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]


class FloodToleranceLevel(str, Enum):
    """Flood tolerance classification levels (ordinal)."""

    SANGAT_TINGGI = "Sangat Tinggi"
    TINGGI = "Tinggi"
    SEDANG = "Sedang"
    RENDAH = "Rendah"
    SANGAT_RENDAH = "Sangat Rendah"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def ordinal(cls, level: str) -> int:
        mapping: dict[str, int] = {
            "Sangat Tinggi": 5,
            "Tinggi": 4,
            "Sedang": 3,
            "Rendah": 2,
            "Sangat Rendah": 1,
        }
        return mapping.get(level, 0)


class DrainageRequirement(str, Enum):
    """Drainage requirement levels (DEPRECATED — not from lecturer doc)."""

    MINIMAL = "Minimal"
    RENDAH = "Rendah"
    SEDANG = "Sedang"
    TINGGI = "Tinggi"
    SANGAT_TINGGI = "Sangat Tinggi"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def ordinal(cls, level: str) -> int:
        mapping: dict[str, int] = {
            "Minimal": 1,
            "Rendah": 2,
            "Sedang": 3,
            "Tinggi": 4,
            "Sangat Tinggi": 5,
        }
        return mapping.get(level, 0)


class RiskLevel(str, Enum):
    """FRI-based risk levels."""

    RENDAH = "Rendah"
    SEDANG = "Sedang"
    TINGGI = "Tinggi"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]


class EconomicPriority(str, Enum):
    """Economic/Cultural importance ranking (DEPRECATED — not from lecturer doc)."""

    SANGAT_TINGGI = "Sangat Tinggi"
    TINGGI = "Tinggi"
    SEDANG = "Sedang"
    RENDAH = "Rendah"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def ordinal(cls, level: str) -> int:
        mapping: dict[str, int] = {
            "Sangat Tinggi": 4,
            "Tinggi": 3,
            "Sedang": 2,
            "Rendah": 1,
        }
        return mapping.get(level, 0)


# ── Schema version constant ────────────────────────────────────────
KNOWLEDGE_SCHEMA_VERSION: Final[str] = "2.1"


class CommodityKnowledge(BaseModel, frozen=True, extra="forbid"):
    """A single commodity record in the Knowledge Base.

    Lecturer-derived fields (source of truth):
      - commodity_id, commodity_name, aliases
      - kelompok_kerentanan, tingkat_kerentanan
      - batas_toleransi_genangan, dampak_utama, gejala_kerusakan
      - main_impacts, damage_symptoms

    DEPRECATED fields (kept for backward compatibility):
      - commodity_category, vulnerability_level, flood_tolerance_category
      - drainage_requirement, growing_duration_days, optimal_risk_level
      - economic_priority, major_impacts
      - recommendation_notes, scientific_reference, version, last_updated
    """

    # ── Lecturer-derived fields (source of truth) ────────────────────
    commodity_id: str = Field(
        ..., min_length=1, description="Unique URL-safe identifier"
    )
    commodity_name: str = Field(
        ..., min_length=1, description="Common Indonesian name from lecturer document"
    )
    aliases: list[str] = Field(
        default_factory=list, description="Alternative names from lecturer document (Alias column)"
    )
    kelompok_kerentanan: list[str] = Field(
        ..., min_length=1,
        description="Vulnerability groups from lecturer doc (Tinggi/Sedang/Rendah)",
    )
    tingkat_kerentanan: str = Field(
        ..., min_length=1,
        description="Primary vulnerability level from lecturer doc (e.g. 'Sangat Rentan (Highly Sensitive)')",
    )
    batas_toleransi_genangan: str = Field(
        ..., min_length=1,
        description="Maximum inundation tolerance from lecturer doc",
    )
    dampak_utama: list[str] = Field(
        ..., min_length=1,
        description="Main physiological impacts from lecturer doc (Indonesian)",
    )
    gejala_kerusakan: list[str] = Field(
        ..., min_length=1,
        description="Observable damage symptoms from lecturer doc (Indonesian)",
    )
    main_impacts: list[str] = Field(
        ..., min_length=1,
        description="Authoritative main impacts — exact wording from lecturer document",
    )
    damage_symptoms: list[str] = Field(
        ..., min_length=1,
        description="Authoritative damage symptoms — exact wording from lecturer document",
    )

    # ── DEPRECATED fields (kept for backward compatibility) ──────────
    commodity_category: str = Field(
        ..., description="DEPRECATED — Agronomic category. Kept for backward compat."
    )
    vulnerability_level: str = Field(
        ..., description="DEPRECATED — Flood tolerance level. Derived from lecturer doc."
    )
    flood_tolerance_category: str = Field(
        ..., description="DEPRECATED — Flood tolerance category. Derived from lecturer doc."
    )
    maximum_inundation_duration: str = Field(
        ..., min_length=1,
        description="DEPRECATED — Max survivable flood duration. Maps from batas_toleransi_genangan.",
    )
    drainage_requirement: str = Field(
        ..., description="DEPRECATED — Minimum drainage needed. Kept for backward compat."
    )
    growing_duration_days: int = Field(
        ..., gt=0, lt=365,
        description="DEPRECATED — Days from planting to harvest. Kept for backward compat.",
    )
    optimal_risk_level: str = Field(
        ..., description="DEPRECATED — Optimal risk level. Kept for backward compat."
    )
    economic_priority: str = Field(
        ..., description="DEPRECATED — Economic importance. Kept for backward compat."
    )
    major_impacts: list[str] = Field(
        ..., min_length=1,
        description="DEPRECATED — Physiological effects. Maps from dampak_utama.",
    )
    recommendation_notes: str = Field(
        ..., min_length=1,
        description="DEPRECATED — Planting guidance (catatan). Kept for backward compat. "
                    "No longer authoritative — use main_impacts and damage_symptoms instead.",
    )
    scientific_reference: str = Field(
        ..., min_length=1,
        description="DEPRECATED — Citation or source. Kept for backward compat.",
    )
    version: str = Field(
        ..., description="DEPRECATED — Knowledge record schema version."
    )
    last_updated: str = Field(
        ..., description="DEPRECATED — ISO date of last update."
    )


class KnowledgeMetadata(BaseModel, frozen=True, extra="forbid"):
    """Metadata about the loaded Knowledge Base."""

    schema_version: str
    commodity_count: int
    loaded_at: str
    load_duration_ms: float
    validation_status: str
    validation_errors: list[str] = []
    categories: list[str]
    vulnerability_levels: list[str]


class KnowledgeCollection(BaseModel, frozen=True, extra="forbid"):
    """The complete in-memory knowledge collection.

    This is the top-level container returned by the Loader and stored
    in the Cache.
    """

    commodities: list[CommodityKnowledge]
    metadata: KnowledgeMetadata


class ValidationReport(BaseModel, frozen=True, extra="forbid"):
    """Result of a validation run."""

    passed: bool
    total_checks: int
    failed_checks: int
    errors: list[str]
    warnings: list[str]
