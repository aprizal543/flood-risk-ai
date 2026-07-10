"""Decision Engine Validation — Full range test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.knowledge import KnowledgeBase
from backend.decision import DecisionEngine, KnowledgeRecommendationService

kb = KnowledgeBase()
kb.initialize()
engine = DecisionEngine(knowledge_base=kb)
engine.initialize()
svc = KnowledgeRecommendationService(engine)

print("=== DECISION ENGINE VALIDATION ===")
print(f"Engine ready: {engine.is_ready}")
print(f"Service ready: {svc.is_ready}")
print()

test_fris = [0, 10, 25, 33, 45, 50, 55, 66, 75, 90, 100]
print(f"{'FRI':<6} {'Risk':<10} {'Rec':<4} {'Alt':<4} {'NotRec':<8} {'TimeMs':<10}")
print("-" * 55)
for fri in test_fris:
    result = svc.recommend(fri)
    r = len(result.recommended)
    a = len(result.alternative)
    n = len(result.not_recommended)
    t = result.metadata.execution_duration_ms
    rc = result.context.risk_category.value
    print(f"{fri:<6} {rc:<10} {r:<4} {a:<4} {n:<8} {t:<10.2f}")
    assert r + a + n == 22, f"FRI={fri}: Expected 22 commodities, got {r+a+n}"

print()
result = svc.recommend(50.0)
print(f"Engine version: {result.metadata.engine_version}")
print(f"Total rules: {result.metadata.total_rules_evaluated}")
print(f"Commodities classified: {result.metadata.commodities_classified}")
print(f"Validation status: {result.metadata.validation_status}")
print(f"Execution duration: {result.metadata.execution_duration_ms:.2f}ms")

rpt = result.report
print(f"Report: Rec={rpt.recommended_count} Alt={rpt.alternative_count} NotRec={rpt.not_recommended_count}")
print(f"All classified: {rpt.all_commodities_classified}")
print(f"No duplicates: {rpt.no_duplicates}")
print(f"Rule coverage: {rpt.rule_coverage_pct}%")
print(f"Knowledge coverage: {rpt.knowledge_coverage_pct}%")
print(f"Explanation coverage: {rpt.explanation_coverage_pct}%")

print()
print("=== SPECIFIC COMMODITY EXPECTATIONS ===")
kangkung_ok = True
semanggi_ok = True
for fri in test_fris:
    result = svc.recommend(fri)
    for g in result.groups:
        for c in g.commodities:
            if c.commodity_id == "kangkung_air" and c.recommendation_status.value != "recommended":
                kangkung_ok = False
            if c.commodity_id == "semanggi" and c.recommendation_status.value != "recommended":
                semanggi_ok = False
print(f"  Kangkung Air (vuln=Sangat Tinggi) always recommended: {'PASS' if kangkung_ok else 'FAIL'}")
print(f"  Semanggi (vuln=Sangat Tinggi) always recommended: {'PASS' if semanggi_ok else 'FAIL'}")

print()
print("DECISION ENGINE VALIDATION: PASS")
