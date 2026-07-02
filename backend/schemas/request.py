"""Request schemas with validation rules."""

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class PrediksiManualRequest(BaseModel):
    """Input data mentah BMKG untuk prediksi otomatis."""
    tanggal: str = Field(..., description="Tanggal observasi (YYYY-MM-DD)", examples=["2026-01-15"])
    rr: float = Field(..., ge=0, description="Curah hujan harian (mm), minimal 0", examples=[25.0])
    rh_avg: float = Field(..., ge=0, le=100, description="Kelembaban rata-rata (%), 0-100", examples=[85.0])
    tmax: float = Field(..., ge=-20, le=60, description="Suhu maksimum (°C), -20 s/d 60", examples=[33.0])
    tmin: float = Field(..., ge=-20, le=60, description="Suhu minimum (°C), -20 s/d 60", examples=[24.0])
    model: str = Field(default="rf", pattern="^(rf|lstm)$", description="Model prediksi: rf atau lstm")
    top_n: int = Field(default=5, ge=1, le=17, description="Jumlah rekomendasi komoditas")

    @model_validator(mode="after")
    def validate_fields(self):
        # Validate tanggal format and not future
        try:
            d = datetime.strptime(self.tanggal, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
        if d > date.today():
            raise ValueError("Tanggal tidak boleh di masa depan.")
        # Validate tmax >= tmin
        if self.tmax < self.tmin:
            raise ValueError("Suhu maksimum (tmax) harus >= suhu minimum (tmin).")
        return self


class PrediksiEngineeredRequest(BaseModel):
    """Input fitur yang sudah direkayasa."""
    rr: float = Field(..., ge=0, description="Curah hujan harian (mm)")
    rain3: float = Field(..., ge=0, description="Akumulasi hujan 3 hari (mm)")
    rain7: float = Field(..., ge=0, description="Akumulasi hujan 7 hari (mm)")
    rain14: float = Field(..., ge=0, description="Akumulasi hujan 14 hari (mm)")
    rh_avg: float = Field(..., ge=0, le=100, description="Kelembaban rata-rata (%)")
    temp_range: float = Field(..., ge=0, description="Rentang suhu harian (°C)")
    rainfall_anomaly: float = Field(..., ge=0, le=100, description="Anomali curah hujan (0-100)")
    month: int = Field(..., ge=1, le=12, description="Bulan (1-12)")
    day_of_year: int = Field(..., ge=1, le=366, description="Hari dalam setahun (1-366)")
    model: str = Field(default="rf", pattern="^(rf|lstm)$", description="Model prediksi")
    top_n: int = Field(default=5, ge=1, le=17, description="Jumlah rekomendasi")
