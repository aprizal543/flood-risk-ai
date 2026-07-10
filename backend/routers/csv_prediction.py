"""CSV prediction endpoint – predicts latest observation using history for rolling features."""

import csv
import io
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from backend.dependencies.auth import get_current_user
from backend.providers.models import RawWeatherData
from backend.security.limits import PREDICTION_LIMIT
from backend.security.rate_limit import limiter
from backend.schemas.response import ErrorResponse
from backend.services.prediction_gateway import predict_from_raw
from backend.services.recommendation_gateway import augment_with_knowledge

logger = logging.getLogger("backend.csv")
router = APIRouter(tags=["Prediksi CSV"])

REQUIRED_COLUMNS = {"tanggal", "rr", "rh_avg", "tmax", "tmin"}


def _parse_csv(content: bytes) -> list[dict]:
    """Parse CSV bytes into list of row dicts with normalized keys."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=422, detail="File CSV kosong atau tidak valid.")

    columns = {c.strip().lower() for c in reader.fieldnames}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Kolom wajib tidak ditemukan: {', '.join(sorted(missing))}",
        )

    rows = []
    for raw_row in reader:
        row = {k.strip().lower(): v.strip() if v else "" for k, v in raw_row.items()}
        rows.append(row)
    return rows


def _validate_and_sort(rows: list[dict]) -> list[dict]:
    """Validate rows and sort ascending by tanggal."""
    if not rows:
        raise HTTPException(status_code=422, detail="File CSV tidak berisi data.")

    valid = []
    for row in rows:
        try:
            datetime.strptime(row["tanggal"], "%Y-%m-%d")
            rr = float(row["rr"])
            rh = float(row["rh_avg"])
            tmax = float(row["tmax"])
            tmin = float(row["tmin"])
            if rr < 0 or not (0 <= rh <= 100) or tmax < tmin:
                continue
            valid.append(row)
        except (ValueError, TypeError):
            continue

    if not valid:
        raise HTTPException(status_code=422, detail="Tidak ada baris valid dalam CSV.")

    valid.sort(key=lambda r: r["tanggal"])
    return valid


def _build_weather_and_history(valid_rows: list[dict]) -> tuple[RawWeatherData, list[dict] | None]:
    """Build RawWeatherData from latest row and history from preceding rows."""
    latest = valid_rows[-1]
    history = [{"rr": float(r["rr"])} for r in valid_rows[:-1]] or None

    weather = RawWeatherData(
        tanggal=datetime.strptime(latest["tanggal"], "%Y-%m-%d").date(),
        rr=float(latest["rr"]),
        rh_avg=float(latest["rh_avg"]),
        tmax=float(latest["tmax"]),
        tmin=float(latest["tmin"]),
        latitude=0.0,
        longitude=0.0,
        sumber="csv",
    )
    return weather, history


@router.post(
    "/api/prediksi/csv",
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Prediksi risiko banjir dari file CSV",
    description="Upload file CSV berisi data observasi BMKG harian. "
                "Baris historis digunakan untuk menghitung rolling features. "
                "Prediksi dilakukan hanya untuk tanggal terakhir.",
)
@limiter.limit(PREDICTION_LIMIT)
async def predict_csv(
    request: Request,
    _: object = Depends(get_current_user),
    file: UploadFile = File(..., description="File CSV observasi BMKG"),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="File harus berformat CSV.")

    content = await file.read()
    rows = _parse_csv(content)
    valid_rows = _validate_and_sort(rows)
    weather, history = _build_weather_and_history(valid_rows)

    try:
        result = predict_from_raw(weather, history=history, model="rf", top_n=5)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = augment_with_knowledge(
        fri=result["fri"],
        risk_label=result.get("tingkat_risiko", ""),
        top_n=5,
        base_result=result,
        request=request,
    )

    logger.info("CSV prediksi: tanggal=%s FRI=%.2f %s (%d baris historis)",
                weather.tanggal, result["fri"], result["tingkat_risiko"],
                len(history) if history else 0)

    return {
        "tanggal": weather.tanggal.isoformat(),
        "jumlah_baris_historis": len(history) if history else 0,
        **result,
    }


@router.post(
    "/api/prediksi/csv/download",
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Download hasil prediksi CSV",
    description="Upload CSV dan terima hasil prediksi tanggal terakhir dalam format CSV.",
)
@limiter.limit(PREDICTION_LIMIT)
async def predict_csv_download(
    request: Request,
    _: object = Depends(get_current_user),
    file: UploadFile = File(..., description="File CSV observasi BMKG"),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="File harus berformat CSV.")

    content = await file.read()
    rows = _parse_csv(content)
    valid_rows = _validate_and_sort(rows)
    weather, history = _build_weather_and_history(valid_rows)

    result = predict_from_raw(weather, history=history, model="rf", top_n=1)
    top_rec = result["rekomendasi"][0] if result["rekomendasi"] else {}

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["tanggal", "fri", "tingkat_risiko", "komoditas_terbaik", "tingkat_keyakinan"])
    writer.writeheader()
    writer.writerow({
        "tanggal": weather.tanggal.isoformat(),
        "fri": round(result["fri"], 2),
        "tingkat_risiko": result["tingkat_risiko"],
        "komoditas_terbaik": top_rec.get("komoditas", ""),
        "tingkat_keyakinan": top_rec.get("tingkat_keyakinan", 0),
    })

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=hasil_prediksi.csv"},
    )
