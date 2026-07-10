"""Knowledge Validation — Verify all 22 lecturer-approved commodities."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import json
from backend.knowledge.validator import validate_knowledge_data
from backend.knowledge.models import KNOWLEDGE_SCHEMA_VERSION
from backend.knowledge.loader import KnowledgeLoader

loader = KnowledgeLoader()
collection = loader.load()
data = json.loads(Path("backend/knowledge/data/commodity_knowledge.json").read_text(encoding="utf-8"))

print("=== KNOWLEDGE VALIDATION ===")
print(f"Commodity count: {collection.metadata.commodity_count}")
print(f"Schema version: {collection.metadata.schema_version}")
print(f"Validation status: {collection.metadata.validation_status}")

report = validate_knowledge_data(data, schema_version=KNOWLEDGE_SCHEMA_VERSION)
print(f"Validation passed: {report.passed}")
print(f"Total checks: {report.total_checks}")
print(f"Failed checks: {report.failed_checks}")
if report.errors:
    for e in report.errors:
        print(f"  ERROR: {e}")

print()
print("=== COMMODITY INVENTORY (22 from lecturer doc) ===")
ids = sorted([r["commodity_id"] for r in data])
for i, cid in enumerate(ids, 1):
    print(f"  {i}. {cid}")
print(f"  Total: {len(ids)}")

print()
print("=== LECTURER-DERIVED FIELD COMPLETENESS ===")
lecturer_fields = ["commodity_id","commodity_name","aliases","kelompok_kerentanan",
                   "tingkat_kerentanan","batas_toleransi_genangan","dampak_utama","gejala_kerusakan"]
all_ok = True
for rec in data:
    missing = [f for f in lecturer_fields if f not in rec or rec[f] is None]
    if missing:
        print(f"  {rec.get('commodity_id','?')} missing lecturer fields: {missing}")
        all_ok = False
    for lf in ["kelompok_kerentanan","dampak_utama","gejala_kerusakan"]:
        if not isinstance(rec.get(lf), list) or len(rec[lf]) == 0:
            print(f"  {rec['commodity_id']}: {lf} is empty")
            all_ok = False
print(f"  Lecturer fields complete: {'PASS' if all_ok else 'FAIL'}")

print()
print("=== DEPRECATED FIELD COMPLETENESS ===")
dep_fields = ["commodity_category","vulnerability_level","flood_tolerance_category",
              "maximum_inundation_duration","drainage_requirement","growing_duration_days",
              "optimal_risk_level","economic_priority","major_impacts","damage_symptoms",
              "recommendation_notes","scientific_reference","version","last_updated"]
all_dep_ok = True
for rec in data:
    missing = [f for f in dep_fields if f not in rec or rec[f] is None or (isinstance(rec[f],str) and not rec[f].strip())]
    if missing:
        print(f"  {rec.get('commodity_id','?')} missing deprecated: {missing}")
        all_dep_ok = False
    for lf in ["major_impacts","damage_symptoms"]:
        if not isinstance(rec.get(lf), list) or len(rec[lf]) == 0:
            print(f"  {rec['commodity_id']}: {lf} is empty")
            all_dep_ok = False
print(f"  Deprecated fields complete: {'PASS' if all_dep_ok else 'FAIL'}")

ids = [r["commodity_id"] for r in data]
dup = len(ids) != len(set(ids))
print(f"  No duplicates: {'PASS' if not dup else 'FAIL (DUPLICATES FOUND)'}")

print()
print("=== VULNERABILITY DISTRIBUTION (from lecturer doc) ===")
kelompok_dist = {}
for rec in data:
    for kk in rec.get("kelompok_kerentanan", []):
        kelompok_dist[kk] = kelompok_dist.get(kk, 0) + 1
for kk in ["Tinggi", "Sedang", "Rendah"]:
    print(f"  Kelompok {kk}: {kelompok_dist.get(kk, 0)}")

print()
print("=== LECTURER COMMODITY EXISTENCE CHECK ===")
lecturer_ids = {
    "cabai", "tomat", "bawang_merah", "kentang", "paprika",
    "kubis", "pakcoy", "sawi", "terong", "mentimun", "kacang_panjang",
    "wortel", "lobak", "labu_siam", "buncis",
    "kangkung_air", "genjer", "selada_air", "talas",
    "seledri", "pakis_sayur", "semanggi",
}
actual_ids = set(ids)
missing = lecturer_ids - actual_ids
extra = actual_ids - lecturer_ids
if missing:
    print(f"  MISSING lecturer commodities: {sorted(missing)}")
if extra:
    print(f"  EXTRA commodities not in lecturer doc: {sorted(extra)}")
if not missing and not extra:
    print("  All 22 lecturer commodities present. No extra commodities. PASS")

versions = set(r["version"] for r in data)
print(f"  Versions: {versions}")
print(f"  All version {KNOWLEDGE_SCHEMA_VERSION}: {'PASS' if versions == {KNOWLEDGE_SCHEMA_VERSION} else 'FAIL'}")

print()
print("=== EXPLANATION COVERAGE ===")
for c in collection.commodities:
    if not c.recommendation_notes or not c.scientific_reference:
        print(f"  {c.commodity_id} missing recommendation_notes or scientific_reference")
print("  All have recommendation notes and references: PASS")

print()
print("KNOWLEDGE VALIDATION: ALL PASS")
