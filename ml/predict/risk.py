"""risk.py – Flood risk classification from FRI values."""

from dataclasses import dataclass

# Configurable thresholds (3 levels)
RENDAH_MAX = 33.0
SEDANG_MAX = 66.0


@dataclass(frozen=True)
class RiskResult:
    """Classification result with FRI value and risk label."""
    fri: float
    risk: str


def classify_risk(fri: float) -> str:
    """Classify FRI value into 3 risk categories.

    Thresholds:
        0–33:  Rendah
        34–66: Sedang
        67–100: Tinggi
    """
    if fri <= RENDAH_MAX:
        return "Rendah"
    if fri <= SEDANG_MAX:
        return "Sedang"
    return "Tinggi"
