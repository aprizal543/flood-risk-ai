"""Response schemas for the prediction API."""

from __future__ import annotations

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


class KnowledgeCommodityItem(BaseModel):
    komoditas: str
    komoditas_id: str
    vulnerability: str
    max_inundation: str
    maximum_inundation_duration: str | None = None
    main_impacts: list[str] | None = None
    damage_symptoms: list[str] | None = None
    impacts: list[str]
    symptoms: list[str]
    reason: str
    source: str | None = None


class KnowledgeRecommendationResponse(BaseModel):
    recommended: list[KnowledgeCommodityItem]
    alternative: list[KnowledgeCommodityItem]
    not_recommended: list[KnowledgeCommodityItem]


class KnowledgeSourceResponse(BaseModel):
    version: str = "1.0"
    engine: str = "KB-DSS"
    execution_duration_ms: float = 0.0


class PrediksiResponse(BaseModel):
    model: str
    fri: float
    tingkat_risiko: str
    rekomendasi: list[PenjelasanResponse]
    mitigasi: list[TindakanMitigasiResponse]
    knowledge_recommendation: KnowledgeRecommendationResponse | None = None
    knowledge_source: KnowledgeSourceResponse | None = None


class KnowledgeHealthResponse(BaseModel):
    knowledge_ready: bool
    knowledge_version: str | None = None
    commodity_count: int = 0
    validation_status: str = "not_loaded"


class DecisionEngineHealthResponse(BaseModel):
    decision_ready: bool
    engine_version: str = "1.0"
    rules_loaded: bool = False
    validation_status: str = "not_initialized"
    total_commodities: int = 0
    feature_flag_active: bool = False


class RecommendationEngineHealth(BaseModel):
    active_engine: str = "legacy_scoring"
    feature_flag_active: bool = False
    knowledge_engine_version: str = "1.0"
    decision_engine_ready: bool = False
    recommendation_service_ready: bool = False
    knowledge_dataset_ready: bool = False
    knowledge_dataset_version: str | None = None
    knowledge_dataset_commodities: int = 0


class KnowledgeEngineHealth(BaseModel):
    status: str = "disabled"
    feature_flag: bool = False
    active_engine: str = "legacy_scoring"
    decision_engine: str = "not_ready"
    recommendation_service: str = "not_ready"
    knowledge_dataset: str = "not_loaded"
    knowledge_dataset_version: str | None = None
    knowledge_dataset_commodities: int = 0


class HealthResponse(BaseModel):
    status: str
    versi: str
    ready: bool = True
    decision_engine: DecisionEngineHealthResponse | None = None
    recommendation_engine: RecommendationEngineHealth | None = None
    knowledge: KnowledgeHealthResponse | None = None
    knowledge_engine: KnowledgeEngineHealth | None = None


class ErrorResponse(BaseModel):
    status: str = "error"
    kode: int
    pesan: str
