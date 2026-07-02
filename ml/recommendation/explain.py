"""explain.py – Deterministic explainability engine for commodity recommendations."""

import json
from dataclasses import dataclass, asdict
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"

_profiles: dict[str, dict] | None = None


def _load_profiles() -> dict[str, dict]:
    """Lazy-load commodity profiles indexed by id."""
    global _profiles
    if _profiles is None:
        path = KNOWLEDGE_DIR / "commodity_profiles.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        _profiles = {p["id"]: p for p in data}
    return _profiles


_TOLERANSI_ALASAN = {
    "Sangat Tinggi": "Memiliki toleransi banjir sangat tinggi",
    "Tinggi": "Memiliki toleransi banjir tinggi",
    "Sedang": "Memiliki toleransi banjir sedang",
    "Rendah": "Toleransi banjir rendah \u2014 perlu perlindungan ekstra",
    "Sangat Rendah": "Toleransi banjir sangat rendah \u2014 hanya cocok saat risiko minimal",
}

_DRAINASE_ALASAN = {
    "Minimal": "Tidak memerlukan drainase khusus",
    "Rendah": "Kebutuhan drainase rendah",
    "Sedang": "Memerlukan drainase sedang",
    "Tinggi": "Memerlukan drainase baik",
    "Sangat Tinggi": "Memerlukan drainase sangat baik",
}

_KESESUAIAN_RISIKO = {
    ("Sangat Tinggi", "Tinggi"): "Sangat cocok untuk kondisi Risiko Tinggi saat ini",
    ("Sangat Tinggi", "Sedang"): "Sangat cocok bahkan pada Risiko Sedang",
    ("Sangat Tinggi", "Rendah"): "Cocok di semua kondisi risiko",
    ("Tinggi", "Tinggi"): "Cocok untuk kondisi Risiko Tinggi saat ini",
    ("Tinggi", "Sedang"): "Cocok untuk kondisi Risiko Sedang hingga Tinggi",
    ("Tinggi", "Rendah"): "Cocok di semua kondisi risiko",
    ("Sedang", "Sedang"): "Sesuai dengan kondisi Risiko Sedang saat ini",
    ("Sedang", "Rendah"): "Cukup sesuai untuk kondisi Risiko Rendah saat ini",
    ("Sedang", "Tinggi"): "Kurang optimal pada kondisi Risiko Tinggi",
    ("Rendah", "Rendah"): "Ideal untuk kondisi Risiko Rendah saat ini",
    ("Rendah", "Sedang"): "Berisiko pada kondisi Risiko Sedang saat ini",
    ("Rendah", "Tinggi"): "Tidak disarankan pada kondisi Risiko Tinggi",
    ("Sangat Rendah", "Rendah"): "Hanya cocok saat Risiko Rendah",
    ("Sangat Rendah", "Sedang"): "Tidak disarankan pada Risiko Sedang",
    ("Sangat Rendah", "Tinggi"): "Sangat tidak disarankan pada Risiko Tinggi",
}


def _get_risk_level(fri: float) -> str:
    if fri <= 33:
        return "Rendah"
    if fri <= 66:
        return "Sedang"
    return "Tinggi"


def _generate_alasan(profile: dict, fri: float, risk_level: str) -> list[str]:
    """Generate list of explanation reasons from commodity attributes."""
    alasan = []

    # Flood tolerance
    tol = profile["toleransi_banjir"]
    alasan.append(_TOLERANSI_ALASAN.get(tol, f"Toleransi banjir: {tol}"))

    # Risk match
    key = (tol, risk_level)
    if key in _KESESUAIAN_RISIKO:
        alasan.append(_KESESUAIAN_RISIKO[key])
    else:
        key_alt = (profile["risiko_optimal"], risk_level)
        if key_alt in _KESESUAIAN_RISIKO:
            alasan.append(_KESESUAIAN_RISIKO[key_alt])

    # Duration
    hari = profile["durasi_tanam_hari"]
    if hari <= 35:
        alasan.append(f"Masa panen singkat ({hari} hari) \u2014 mengurangi paparan risiko")
    elif hari <= 60:
        alasan.append(f"Masa panen relatif singkat ({hari} hari)")
    elif hari <= 90:
        alasan.append(f"Masa panen sedang ({hari} hari)")
    else:
        alasan.append(f"Masa panen panjang ({hari} hari) \u2014 pertimbangkan risiko jangka panjang")

    # Drainage
    alasan.append(_DRAINASE_ALASAN.get(profile["kebutuhan_drainase"], ""))

    return [a for a in alasan if a]


def _generate_ringkasan(profile: dict, fri: float, risk_level: str, skor: float) -> str:
    """Generate one-sentence Bahasa Indonesia summary."""
    nama = profile["nama"]
    tol = profile["toleransi_banjir"].lower()

    if skor >= 80:
        return f"{nama} sangat direkomendasikan karena memiliki toleransi banjir {tol} dan sesuai dengan kondisi Risiko {risk_level} saat ini (FRI: {fri:.0f})."
    if skor >= 60:
        return f"{nama} dapat dipertimbangkan untuk ditanam dengan memperhatikan kondisi drainase pada Risiko {risk_level} saat ini (FRI: {fri:.0f})."
    return f"{nama} kurang disarankan pada kondisi Risiko {risk_level} saat ini (FRI: {fri:.0f}) karena toleransi banjir yang terbatas."


@dataclass(frozen=True)
class Penjelasan:
    """Complete recommendation explanation."""
    komoditas: str
    komoditas_id: str
    skor: float
    tingkat_keyakinan: float
    tingkat_risiko: str
    alasan: list[str]
    ringkasan: str

    def to_dict(self) -> dict:
        return asdict(self)


def explain_recommendation(
    commodity_id: str,
    fri: float,
    skor: float,
    tingkat_keyakinan: float,
) -> Penjelasan:
    """Generate a human-readable explanation for a commodity recommendation.

    Args:
        commodity_id: Commodity identifier from profiles.
        fri: Current Flood Risk Index (0-100).
        skor: Recommendation score (0-100).
        tingkat_keyakinan: Confidence value (0-1).

    Returns:
        Penjelasan dataclass with alasan and ringkasan in Bahasa Indonesia.
    """
    profiles = _load_profiles()
    profile = profiles[commodity_id]
    risk_level = _get_risk_level(fri)

    alasan = _generate_alasan(profile, fri, risk_level)
    ringkasan = _generate_ringkasan(profile, fri, risk_level, skor)

    return Penjelasan(
        komoditas=profile["nama"],
        komoditas_id=commodity_id,
        skor=round(skor, 1),
        tingkat_keyakinan=round(tingkat_keyakinan * 100, 1),
        tingkat_risiko=f"Risiko {risk_level}",
        alasan=alasan,
        ringkasan=ringkasan,
    )
