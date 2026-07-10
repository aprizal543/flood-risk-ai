"""Shared fixtures for knowledge base tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.knowledge.models import (
    CommodityKnowledge,
    KnowledgeCollection,
    KnowledgeMetadata,
)

FIXTURE_DATA_DIR = Path(__file__).resolve().parents[3] / "backend" / "knowledge" / "data"
FIXTURE_DATA_FILE = FIXTURE_DATA_DIR / "commodity_knowledge.json"


@pytest.fixture(scope="session")
def knowledge_data() -> list[dict]:
    """Load the full commodity_knowledge.json dataset."""
    data = json.loads(FIXTURE_DATA_FILE.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="session")
def sample_commodity() -> CommodityKnowledge:
    """A single valid CommodityKnowledge instance for isolated tests."""
    return CommodityKnowledge(
        commodity_id="kangkung_air",
        commodity_name="Kangkung Air",
        aliases=[],
        kelompok_kerentanan=["Tinggi", "Rendah"],
        tingkat_kerentanan="Toleran (Tolerant)",
        batas_toleransi_genangan="Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
        dampak_utama=["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
        gejala_kerusakan=["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
        main_impacts=["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
        damage_symptoms=["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
        commodity_category="sayuran_daun",
        vulnerability_level="Sangat Tinggi",
        flood_tolerance_category="Sangat Tinggi",
        maximum_inundation_duration="Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
        drainage_requirement="Minimal",
        growing_duration_days=25,
        optimal_risk_level="Tinggi",
        economic_priority="Sangat Tinggi",
        major_impacts=["Pertumbuhan subur di genangan"],
        recommendation_notes="Ideal untuk area rawan banjir.",
        scientific_reference="Lecturer recommendation document",
        version="2.1",
        last_updated="2026-07-10",
    )


@pytest.fixture
def multi_commodity_collection() -> KnowledgeCollection:
    c1 = CommodityKnowledge(
        commodity_id="kangkung_air",
        commodity_name="Kangkung Air",
        aliases=[],
        kelompok_kerentanan=["Tinggi", "Rendah"],
        tingkat_kerentanan="Toleran (Tolerant)",
        batas_toleransi_genangan="Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
        dampak_utama=["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
        gejala_kerusakan=["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
        main_impacts=["Tanaman tetap tumbuh optimal karena memiliki jaringan aerenkim"],
        damage_symptoms=["Tidak menunjukkan gejala kerusakan berarti pada genangan"],
        commodity_category="sayuran_daun",
        vulnerability_level="Sangat Tinggi",
        flood_tolerance_category="Sangat Tinggi",
        maximum_inundation_duration="Lebih dari 72 jam (dapat beradaptasi pada kondisi basah)",
        drainage_requirement="Minimal",
        growing_duration_days=25,
        optimal_risk_level="Tinggi",
        economic_priority="Sangat Tinggi",
        major_impacts=["A"],
        recommendation_notes="Note A",
        scientific_reference="Ref A",
        version="2.1",
        last_updated="2026-07-10",
    )
    c2 = CommodityKnowledge(
        commodity_id="cabai",
        commodity_name="Cabai",
        aliases=[],
        kelompok_kerentanan=["Tinggi"],
        tingkat_kerentanan="Sangat Rentan (Highly Sensitive)",
        batas_toleransi_genangan="Kurang dari 24 jam",
        dampak_utama=["Akar langsung membusuk akibat ketiadaan oksigen"],
        gejala_kerusakan=["Daun menguning (klorosis)"],
        main_impacts=["Akar langsung membusuk akibat ketiadaan oksigen"],
        damage_symptoms=["Daun menguning (klorosis)"],
        commodity_category="sayuran_buah",
        vulnerability_level="Sangat Rendah",
        flood_tolerance_category="Sangat Rendah",
        maximum_inundation_duration="Kurang dari 24 jam",
        drainage_requirement="Tinggi",
        growing_duration_days=90,
        optimal_risk_level="Rendah",
        economic_priority="Tinggi",
        major_impacts=["C"],
        recommendation_notes="Note B",
        scientific_reference="Ref B",
        version="2.1",
        last_updated="2026-07-10",
    )
    c3 = CommodityKnowledge(
        commodity_id="semanggi",
        commodity_name="Semanggi",
        aliases=[],
        kelompok_kerentanan=["Rendah"],
        tingkat_kerentanan="Sangat Toleran (Vegetasi Akuatik / Hidrofit)",
        batas_toleransi_genangan="Permanen (mampu tumbuh pada lahan basah/rawa)",
        dampak_utama=["Membutuhkan kondisi tanah yang jenuh air atau tergenang permanen"],
        gejala_kerusakan=["Tidak menunjukkan gejala kerusakan pada genangan"],
        main_impacts=["Membutuhkan kondisi tanah yang jenuh air atau tergenang permanen"],
        damage_symptoms=["Tidak menunjukkan gejala kerusakan pada genangan"],
        commodity_category="sayuran_daun",
        vulnerability_level="Sangat Tinggi",
        flood_tolerance_category="Sangat Tinggi",
        maximum_inundation_duration="Permanen (mampu tumbuh pada lahan basah/rawa)",
        drainage_requirement="Minimal",
        growing_duration_days=30,
        optimal_risk_level="Tinggi",
        economic_priority="Tinggi",
        major_impacts=["E"],
        recommendation_notes="Note C",
        scientific_reference="Ref C",
        version="2.1",
        last_updated="2026-07-10",
    )
    meta = KnowledgeMetadata(
        schema_version="2.1",
        commodity_count=3,
        loaded_at="2026-07-10T12:00:00",
        load_duration_ms=5.0,
        validation_status="passed",
        categories=["sayuran_buah", "sayuran_daun"],
        vulnerability_levels=["Sangat Tinggi", "Sangat Rendah"],
    )
    return KnowledgeCollection(commodities=[c1, c2, c3], metadata=meta)
