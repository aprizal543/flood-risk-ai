"""mitigation.py – Flood mitigation action engine."""

import json
from dataclasses import dataclass, asdict
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"
VALID_LEVELS = ("Rendah", "Sedang", "Tinggi")

_rules: dict | None = None


def _load_rules() -> dict:
    """Lazy-load mitigation rules."""
    global _rules
    if _rules is None:
        path = KNOWLEDGE_DIR / "mitigation_rules.json"
        _rules = json.loads(path.read_text(encoding="utf-8"))
    return _rules


@dataclass(frozen=True)
class TindakanMitigasi:
    """A single mitigation action."""
    prioritas: int
    kategori: str
    tindakan: str

    def to_dict(self) -> dict:
        return asdict(self)


# Map action IDs to categories
_KATEGORI = {
    "routine_drainage": "Drainase",
    "clear_drainage": "Drainase",
    "activate_drainage": "Drainase",
    "soil_monitoring": "Monitoring",
    "weather_monitoring": "Monitoring",
    "raised_beds": "Persiapan Lahan",
    "mulching": "Persiapan Lahan",
    "harvest_ready": "Panen",
    "emergency_harvest": "Panen",
    "flood_barriers": "Perlindungan",
    "protect_seedlings": "Perlindungan",
    "delay_planting": "Penanaman",
    "prepare_recovery": "Pemulihan",
    "document_conditions": "Dokumentasi",
}


def get_mitigasi(risiko: str) -> list[TindakanMitigasi]:
    """Return prioritised mitigation actions for the given risk level.

    Args:
        risiko: Risk level — must be 'Rendah', 'Sedang', or 'Tinggi'.

    Returns:
        List of TindakanMitigasi sorted by priority.

    Raises:
        ValueError: If risiko is not a valid level.
    """
    if risiko not in VALID_LEVELS:
        raise ValueError(
            f"Tingkat risiko tidak valid: '{risiko}'. "
            f"Gunakan salah satu dari: {', '.join(VALID_LEVELS)}"
        )

    rules = _load_rules()
    actions = rules["aturan"][risiko]["tindakan"]

    return [
        TindakanMitigasi(
            prioritas=a["prioritas"],
            kategori=_KATEGORI.get(a["id"], "Umum"),
            tindakan=a["deskripsi"],
        )
        for a in sorted(actions, key=lambda x: x["prioritas"])
    ]
