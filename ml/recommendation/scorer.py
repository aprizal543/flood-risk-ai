"""scorer.py – Dynamic commodity scoring based on current flood risk conditions."""

import json
from dataclasses import dataclass
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"

# Configurable scoring weights (sum to 1.0)
WEIGHTS = {
    "toleransi_banjir": 0.35,
    "risiko_optimal": 0.25,
    "drainase": 0.20,
    "durasi_tanam": 0.10,
    "prioritas": 0.10,
}

# Flood tolerance ordinal mapping
TOLERANSI_SKOR = {
    "Sangat Tinggi": 100,
    "Tinggi": 75,
    "Sedang": 50,
    "Rendah": 25,
    "Sangat Rendah": 0,
}

# Drainage requirement ordinal mapping (lower requirement = better in flood)
DRAINASE_SKOR = {
    "Minimal": 100,
    "Rendah": 80,
    "Sedang": 50,
    "Tinggi": 20,
    "Sangat Tinggi": 0,
}

# Priority ordinal mapping
PRIORITAS_SKOR = {
    "Sangat Tinggi": 100,
    "Tinggi": 75,
    "Sedang": 50,
    "Rendah": 25,
}

# Risk level mapping for optimal risk matching
RISIKO_NILAI = {"Rendah": 0, "Sedang": 50, "Tinggi": 100}

_profiles: list[dict] | None = None


def _load_profiles() -> list[dict]:
    """Lazy-load commodity profiles."""
    global _profiles
    if _profiles is None:
        path = KNOWLEDGE_DIR / "commodity_profiles.json"
        _profiles = json.loads(path.read_text(encoding="utf-8"))
    return _profiles


@dataclass(frozen=True)
class SkorKomoditas:
    """Scored commodity with breakdown."""
    id: str
    nama: str
    skor: float
    skor_toleransi: float
    skor_risiko_optimal: float
    skor_drainase: float
    skor_durasi: float
    skor_prioritas: float


def _score_toleransi(toleransi: str, fri: float) -> float:
    """Higher tolerance -> higher score, amplified when FRI is high."""
    base = TOLERANSI_SKOR.get(toleransi, 50)
    risk_factor = fri / 100
    return base * (0.5 + 0.5 * risk_factor) + (100 - base) * (1 - risk_factor) * 0.5


def _score_risiko_optimal(risiko_optimal: str, fri: float) -> float:
    """How well does the commodity's optimal risk match current conditions?"""
    optimal_val = RISIKO_NILAI.get(risiko_optimal, 50)
    distance = abs(fri - optimal_val) / 100
    return (1 - distance) * 100


def _score_drainase(drainase: str, fri: float) -> float:
    """Lower drainage requirement is better when FRI is high."""
    base = DRAINASE_SKOR.get(drainase, 50)
    risk_factor = fri / 100
    return base * (0.4 + 0.6 * risk_factor) + (100 - base) * (1 - risk_factor) * 0.4


def _score_durasi(hari: int, fri: float) -> float:
    """Shorter growing duration preferred at higher risk."""
    score = max(0, min(100, (180 - hari) / (180 - 25) * 100))
    risk_factor = fri / 100
    return score * (0.5 + 0.5 * risk_factor) + 50 * (1 - risk_factor)


def _score_prioritas(prioritas: str) -> float:
    """Map priority label to score."""
    return PRIORITAS_SKOR.get(prioritas, 50)


def score_commodities(fri: float) -> list[SkorKomoditas]:
    """Score all commodities given current FRI value.

    Args:
        fri: Current Flood Risk Index (0-100).

    Returns:
        List of SkorKomoditas objects with normalised scores (0-100).
    """
    profiles = _load_profiles()
    results = []

    for p in profiles:
        ft = _score_toleransi(p["toleransi_banjir"], fri)
        ro = _score_risiko_optimal(p["risiko_optimal"], fri)
        dr = _score_drainase(p["kebutuhan_drainase"], fri)
        du = _score_durasi(p["durasi_tanam_hari"], fri)
        pr = _score_prioritas(p["prioritas"])

        total = (
            WEIGHTS["toleransi_banjir"] * ft
            + WEIGHTS["risiko_optimal"] * ro
            + WEIGHTS["drainase"] * dr
            + WEIGHTS["durasi_tanam"] * du
            + WEIGHTS["prioritas"] * pr
        )

        results.append(SkorKomoditas(
            id=p["id"],
            nama=p["nama"],
            skor=round(total, 2),
            skor_toleransi=round(ft, 2),
            skor_risiko_optimal=round(ro, 2),
            skor_drainase=round(dr, 2),
            skor_durasi=round(du, 2),
            skor_prioritas=round(pr, 2),
        ))

    return results
