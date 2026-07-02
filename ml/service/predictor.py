"""predictor.py – Unified prediction service combining all DSS components."""

from dataclasses import dataclass, asdict
from typing import Any

import pandas as pd

from ml.predict.preprocess import prepare_dataframe, get_feature_list, validate_input
from ml.predict.random_forest import predict_rf
from ml.predict.risk import classify_risk
from ml.recommendation.recommender import recommend, Rekomendasi
from ml.recommendation.explain import explain_recommendation, Penjelasan
from ml.recommendation.mitigation import get_mitigasi, TindakanMitigasi

VALID_MODELS = ("rf", "lstm")


@dataclass
class HasilPrediksi:
    """Complete prediction result."""
    model: str
    fri: float
    tingkat_risiko: str
    rekomendasi: list[dict]
    mitigasi: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


def prediksi(data: dict | list[dict], model: str = "rf", top_n: int = 5) -> dict:
    """Run the full prediction-to-recommendation pipeline.

    Args:
        data: Single dict of features (RF) or list of 7+ dicts (LSTM).
        model: Model to use — 'rf' or 'lstm'.
        top_n: Number of commodity recommendations to return.

    Returns:
        Complete prediction result as dict with FRI, risk level,
        recommendations with explanations, and mitigation actions.

    Raises:
        ValueError: If model is invalid or required features are missing.
    """
    if model not in VALID_MODELS:
        raise ValueError(f"Model tidak valid: '{model}'. Gunakan: {', '.join(VALID_MODELS)}")

    # Validate input
    rows = data if isinstance(data, list) else [data]
    for i, row in enumerate(rows):
        missing = validate_input(row)
        if missing:
            raise ValueError(f"Baris {i}: fitur tidak lengkap {missing}")

    features = get_feature_list()
    df = pd.DataFrame(rows)[features]

    # Predict FRI
    if model == "rf":
        fri = predict_rf(df.iloc[[-1]])
    else:
        from ml.predict.lstm import predict_lstm, LOOKBACK
        if len(df) < LOOKBACK:
            raise ValueError(f"LSTM memerlukan minimal {LOOKBACK} baris data, diterima {len(df)}")
        fri = predict_lstm(df)

    # Classify risk
    risiko = classify_risk(fri)

    # Get recommendations with explanations
    recs = recommend(fri, top_n=top_n)
    rekomendasi = []
    for r in recs:
        exp = explain_recommendation(r.komoditas_id, fri, r.skor, r.tingkat_keyakinan)
        rekomendasi.append(exp.to_dict())

    # Get mitigation actions
    mitigasi = [a.to_dict() for a in get_mitigasi(risiko)]

    result = HasilPrediksi(
        model=model,
        fri=round(fri, 2),
        tingkat_risiko=f"Risiko {risiko}",
        rekomendasi=rekomendasi,
        mitigasi=mitigasi,
    )
    return result.to_dict()
