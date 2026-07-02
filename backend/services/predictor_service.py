"""predictor_service.py – Service layer for pre-engineered feature prediction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.service.predictor import prediksi


def run_prediction(data: dict, model: str = "rf", top_n: int = 5) -> dict:
    """Jalankan prediksi dari fitur yang sudah direkayasa.

    Raises:
        ValueError: Jika input tidak valid atau model tidak dikenali.
    """
    return prediksi(data, model=model, top_n=top_n)
