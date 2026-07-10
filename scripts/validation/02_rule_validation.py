"""Rule Validation — Validate every deterministic rule."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.decision.rules import InferenceRuleEngine
from backend.decision.models import RecommendationStatus

engine = InferenceRuleEngine()
print("=== RULE VALIDATION MATRIX ===")
print(f"Rule count: {engine.rule_count}")
print(f"Is valid: {engine.is_valid}")
print()

vuln_levels = ["Sangat Tinggi","Tinggi","Sedang","Rendah","Sangat Rendah"]
risk_levels = ["Rendah","Sedang","Tinggi"]

header = f"{'Vulnerability':<20}"
for r in risk_levels:
    header += f" {r:<20}"
print(header)
print("-" * 80)
for vuln in vuln_levels:
    row = f"{vuln:<18}"
    for risk in risk_levels:
        result = engine.evaluate(vuln, risk)
        row += f"  {result.value:<18}"
    print(row)

print()
expected = {
    ("Sangat Tinggi","Rendah"): RecommendationStatus.RECOMMENDED,
    ("Sangat Tinggi","Sedang"): RecommendationStatus.RECOMMENDED,
    ("Sangat Tinggi","Tinggi"): RecommendationStatus.RECOMMENDED,
    ("Tinggi","Rendah"): RecommendationStatus.RECOMMENDED,
    ("Tinggi","Sedang"): RecommendationStatus.RECOMMENDED,
    ("Tinggi","Tinggi"): RecommendationStatus.ALTERNATIVE,
    ("Sedang","Rendah"): RecommendationStatus.RECOMMENDED,
    ("Sedang","Sedang"): RecommendationStatus.ALTERNATIVE,
    ("Sedang","Tinggi"): RecommendationStatus.NOT_RECOMMENDED,
    ("Rendah","Rendah"): RecommendationStatus.ALTERNATIVE,
    ("Rendah","Sedang"): RecommendationStatus.NOT_RECOMMENDED,
    ("Rendah","Tinggi"): RecommendationStatus.NOT_RECOMMENDED,
    ("Sangat Rendah","Rendah"): RecommendationStatus.NOT_RECOMMENDED,
    ("Sangat Rendah","Sedang"): RecommendationStatus.NOT_RECOMMENDED,
    ("Sangat Rendah","Tinggi"): RecommendationStatus.NOT_RECOMMENDED,
}

all_pass = True
for (vuln, risk), exp in expected.items():
    actual = engine.evaluate(vuln, risk)
    status = "PASS" if actual == exp else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  {vuln:<18} x {risk:<8} => Expected: {exp.value:<18} Actual: {actual.value:<18} [{status}]")

msg = "ALL PASS (100%)" if all_pass else "FAILURES FOUND"
print(f"\nRule validation: {msg} ({len(expected)}/15)")
print(f"Rule coverage: {100.0 if all_pass else 0}%")
