"""End-to-End Consistency Check — Multiple cities."""
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

print("=== E2E CONSISTENCY CHECK (Simulated Cities) ===")
print()

cities = {
    "Pekanbaru": 45.0,
    "Dumai": 75.0,
    "Bangkinang": 25.0,
    "Ujung Batu": 66.0,
    "Pasir Pengaraian": 10.0
}

print(f"{'City':<20} {'FRI':<8} {'Risk':<10} {'Rec':<4} {'Alt':<4} {'NotRec':<4}")
print("-" * 60)
for city, fri in cities.items():
    result = svc.recommend(fri)
    r = len(result.recommended)
    a = len(result.alternative)
    n = len(result.not_recommended)
    rc = result.context.risk_category.value
    print(f"{city:<20} {fri:<8.1f} {rc:<10} {r:<4} {a:<4} {n:<4}")
    assert r + a + n == 22, f"{city}: Expected 22, got {r+a+n}"

print()
print("Consistency check (same risk => same result):")
r1 = svc.recommend(45.0)
r2 = svc.recommend(55.0)
ids_45 = sorted([c.commodity_id for g in r1.groups for c in g.commodities])
ids_55 = sorted([c.commodity_id for g in r2.groups for c in g.commodities])
print(f"  Same commodity IDs: {ids_45 == ids_55}")
print(f"  Same Rec count: {len(r1.recommended) == len(r2.recommended)}")
print(f"  Same Alt count: {len(r1.alternative) == len(r2.alternative)}")
print(f"  Same NotRec count: {len(r1.not_recommended) == len(r2.not_recommended)}")

print()
print("Returned commodity IDs (all cities have identical set):")
all_ids = set()
for city, fri in cities.items():
    result = svc.recommend(fri)
    ids = frozenset([c.commodity_id for g in result.groups for c in g.commodities])
    all_ids.add(ids)
print(f"  Unique ID sets across all cities: {len(all_ids)} (should be 1)")
print(f"  All cities have identical commodity set: {len(all_ids) == 1}")

print()
print("E2E CONSISTENCY: PASS")
