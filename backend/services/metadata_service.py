"""metadata_service.py – System metadata and health checks."""

import json
import sys
import time
from pathlib import Path

import fastapi

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "ml" / "artifacts"
KNOWLEDGE_DIR = ROOT / "ml" / "knowledge"

_start_time = time.time()

APP_INFO = {
    "nama_aplikasi": "Flood Risk DSS",
    "versi": "1.0.0",
    "build": "2026-06-28",
    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    "fastapi_version": fastapi.__version__,
}

_REQUIRED_ARTIFACTS = {
    "random_forest": ARTIFACTS_DIR / "random_forest_v2.pkl",
    "random_forest_legacy": ARTIFACTS_DIR / "random_forest.pkl",
    "lstm": ARTIFACTS_DIR / "best_lstm.keras",
    "scaler_lstm": ARTIFACTS_DIR / "scaler_lstm.pkl",
    "feature_list": ARTIFACTS_DIR / "feature_list.json",
}

_REQUIRED_KNOWLEDGE = {
    "commodity_profiles": KNOWLEDGE_DIR / "commodity_profiles.json",
    "recommendation_rules": KNOWLEDGE_DIR / "recommendation_rules.json",
    "mitigation_rules": KNOWLEDGE_DIR / "mitigation_rules.json",
}

FRI_V2_FEATURES = ["RR", "Rain7", "RH_avg", "Tavg"]


def get_model_info() -> dict:
    """Informasi model ML yang digunakan."""
    feature_path = ARTIFACTS_DIR / "feature_list.json"
    features = json.loads(feature_path.read_text()) if feature_path.exists() else []
    return {
        "nama_model": "Random Forest Regressor v2 + LSTM legacy",
        "versi_model": "2.0",
        "target_prediksi": "Flood Risk Index (FRI)",
        "jumlah_fitur": len(features),
        "nama_fitur": features,
        "status_artifact": {
            name: "tersedia" if path.exists() else "tidak ditemukan"
            for name, path in _REQUIRED_ARTIFACTS.items()
        },
        "fri_v2_feature_engineering": {
            "status": "tersedia",
            "feature_order": FRI_V2_FEATURES,
            "model_artifact": "random_forest_v2.pkl",
        },
    }


def get_version_info() -> dict:
    """Informasi versi aplikasi."""
    return APP_INFO


def get_health_detail() -> dict:
    """Pemeriksaan kesehatan detail seluruh komponen sistem."""
    checks = {}

    # API
    checks["api"] = "sehat"

    # Feature engineering
    checks["feature_engineering"] = "sehat"

    # Feature list
    checks["feature_list"] = "sehat" if _REQUIRED_ARTIFACTS["feature_list"].exists() else "tidak tersedia"

    # Prediction engine artifacts
    checks["random_forest"] = "sehat" if _REQUIRED_ARTIFACTS["random_forest"].exists() else "tidak tersedia"
    checks["lstm"] = "sehat" if _REQUIRED_ARTIFACTS["lstm"].exists() else "tidak tersedia"

    # Recommendation engine
    checks["recommendation_engine"] = "sehat"

    # Knowledge base
    kb_ok = all(p.exists() for p in _REQUIRED_KNOWLEDGE.values())
    checks["knowledge_base"] = "sehat" if kb_ok else "tidak lengkap"

    # Overall status
    all_healthy = all(v == "sehat" for v in checks.values())
    status = "sehat" if all_healthy else "degraded"

    uptime_seconds = int(time.time() - _start_time)

    return {
        "status": status,
        "uptime_detik": uptime_seconds,
        "komponen": checks,
    }
