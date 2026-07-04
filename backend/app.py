"""FastAPI application – Flood Risk DSS Backend."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import load_backend_environment

load_backend_environment()

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.middleware import LoggingMiddleware
from backend.routers import health, prediction
from backend.routers.auth import router as auth_router
from backend.routers.csv_prediction import router as csv_router
from backend.routers.info import router as info_router
from backend.routers.provider import router as provider_router
from backend.routers.realtime import router as realtime_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="Flood Risk DSS API",
    description="Sistem Pendukung Keputusan Risiko Banjir untuk Hortikultura Pekanbaru. "
                "API ini menerima data observasi cuaca BMKG dan mengembalikan prediksi "
                "Flood Risk Index, rekomendasi komoditas, dan tindakan mitigasi.",
    version="1.0.0",
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Override default validation errors with consistent Indonesian format."""
    errors = exc.errors()
    messages = []
    for err in errors:
        loc = " > ".join(str(l) for l in err["loc"] if l != "body")
        msg = err["msg"]
        # Translate common Pydantic messages
        if "Value error" in msg:
            msg = msg.replace("Value error, ", "")
        messages.append(f"{loc}: {msg}" if loc else msg)
    return JSONResponse(
        status_code=422,
        content={"status": "error", "kode": 422, "pesan": "; ".join(messages)},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "kode": 422, "pesan": str(exc)},
    )


app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(auth_router)
app.include_router(csv_router)
app.include_router(info_router)
app.include_router(provider_router)
app.include_router(realtime_router)
