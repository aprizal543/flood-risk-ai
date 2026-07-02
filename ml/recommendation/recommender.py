"""recommender.py – Top-N commodity recommendation engine."""

from dataclasses import dataclass

from ml.recommendation.scorer import score_commodities, SkorKomoditas


@dataclass(frozen=True)
class Rekomendasi:
    """A single commodity recommendation."""
    peringkat: int
    komoditas: str
    komoditas_id: str
    skor: float
    tingkat_keyakinan: float


def recommend(fri: float, top_n: int = 5) -> list[Rekomendasi]:
    """Generate top-N commodity recommendations for a given FRI.

    Args:
        fri: Current Flood Risk Index (0-100).
        top_n: Number of recommendations to return.

    Returns:
        Ranked list of Rekomendasi objects.
    """
    scores = score_commodities(fri)
    sorted_scores = sorted(scores, key=lambda s: s.skor, reverse=True)
    top = sorted_scores[:top_n]

    max_score = top[0].skor if top else 0

    return [
        Rekomendasi(
            peringkat=i + 1,
            komoditas=s.nama,
            komoditas_id=s.id,
            skor=s.skor,
            tingkat_keyakinan=round(s.skor / max_score, 3) if max_score > 0 else 0,
        )
        for i, s in enumerate(top)
    ]
