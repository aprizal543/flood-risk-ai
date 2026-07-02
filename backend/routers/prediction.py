"""Prediction endpoints."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.providers.models import RawWeatherData
from backend.schemas.request import PrediksiManualRequest, PrediksiEngineeredRequest
from backend.schemas.response import PrediksiResponse, ErrorResponse
from backend.services.prediction_gateway import predict_from_raw
from backend.services.predictor_service import run_prediction

logger = logging.getLogger("backend.prediction")
router = APIRouter(tags=["Prediksi"])


@router.post(
    "/api/prediksi/manual",
    response_model=PrediksiResponse,
    responses={422: {"model": ErrorResponse}},
    summary="Prediksi risiko banjir dari data mentah BMKG",
    description="Menerima data observasi cuaca mentah (tanggal, rr, rh_avg, tmax, tmin), "
                "melakukan feature engineering otomatis, dan mengembalikan prediksi lengkap.",
)
def predict_manual(req: PrediksiManualRequest) -> PrediksiResponse:
    logger.info("Feature engineering dimulai")
    tanggal = datetime.strptime(req.tanggal, "%Y-%m-%d").date()
    weather = RawWeatherData(
        tanggal=tanggal,
        rr=req.rr,
        rh_avg=req.rh_avg,
        tmax=req.tmax,
        tmin=req.tmin,
        latitude=0.0,
        longitude=0.0,
        sumber="manual",
    )
    try:
        result = predict_from_raw(weather, model=req.model, top_n=req.top_n)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    logger.info("Prediksi selesai: FRI=%.2f, risiko=%s", result["fri"], result["tingkat_risiko"])
    return PrediksiResponse(**result)


@router.post(
    "/api/prediksi/engineered",
    response_model=PrediksiResponse,
    responses={422: {"model": ErrorResponse}},
    summary="Prediksi dari fitur yang sudah direkayasa",
    description="Menerima 9 fitur ML yang sudah dihitung sebelumnya (kompatibilitas).",
)
def predict_engineered(req: PrediksiEngineeredRequest) -> PrediksiResponse:
    features = req.model_dump(exclude={"model", "top_n"})
    try:
        result = run_prediction(features, model=req.model, top_n=req.top_n)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    logger.info("Prediksi selesai: FRI=%.2f", result["fri"])
    return PrediksiResponse(**result)
