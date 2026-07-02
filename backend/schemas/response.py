"""Response schemas for the prediction API."""

from pydantic import BaseModel


class TindakanMitigasiResponse(BaseModel):
    prioritas: int
    kategori: str
    tindakan: str


class PenjelasanResponse(BaseModel):
    komoditas: str
    komoditas_id: str
    skor: float
    tingkat_keyakinan: float
    tingkat_risiko: str
    alasan: list[str]
    ringkasan: str


class PrediksiResponse(BaseModel):
    model: str
    fri: float
    tingkat_risiko: str
    rekomendasi: list[PenjelasanResponse]
    mitigasi: list[TindakanMitigasiResponse]


class HealthResponse(BaseModel):
    status: str
    versi: str


class ErrorResponse(BaseModel):
    status: str = "error"
    kode: int
    pesan: str
