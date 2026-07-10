"""Performance Benchmark — Measure latency."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.knowledge import KnowledgeBase
from backend.decision import KnowledgeRecommendationService, DecisionEngine
from backend.services.recommendation_mapper import to_knowledge_recommendation, to_knowledge_source, to_legacy_rekomendasi
import time, statistics

kb = KnowledgeBase()
kb.initialize()
engine = DecisionEngine(knowledge_base=kb)
engine.initialize()
svc = KnowledgeRecommendationService(engine)

print("=== PERFORMANCE BENCHMARK ===")
_ = svc.recommend(50.0)

times = []
for _ in range(100):
    start = time.perf_counter()
    _ = svc.recommend(50.0)
    times.append((time.perf_counter() - start) * 1000)

print(f"\nDecision Engine (100 iterations at FRI=50):")
print(f"  Mean:   {statistics.mean(times):.2f}ms")
print(f"  Median: {statistics.median(times):.2f}ms")
print(f"  Min:    {min(times):.2f}ms")
print(f"  Max:    {max(times):.2f}ms")
print(f"  P95:    {sorted(times)[94]:.2f}ms")
print(f"  P99:    {sorted(times)[98]:.2f}ms")

print(f"\nPer risk level (100 iterations each):")
for fri in [10, 50, 90]:
    times_risk = []
    for _ in range(100):
        start = time.perf_counter()
        result = svc.recommend(fri)
        times_risk.append((time.perf_counter() - start) * 1000)
    rc = result.context.risk_category.value
    print(f"  FRI={fri:<3} ({rc:<8}): mean={statistics.mean(times_risk):.3f}ms, median={statistics.median(times_risk):.3f}ms")

print(f"\nTotal recommendation pipeline (inc. mapper, 100 iterations):")
full_times = []
for _ in range(100):
    start = time.perf_counter()
    result = svc.recommend(50.0)
    groups = to_knowledge_recommendation(result)
    src = to_knowledge_source(result)
    leg = to_legacy_rekomendasi(result, 50.0, 5)
    full_times.append((time.perf_counter() - start) * 1000)
print(f"  Mean:   {statistics.mean(full_times):.2f}ms")
print(f"  Median: {statistics.median(full_times):.2f}ms")
print(f"  Min:    {min(full_times):.2f}ms")
print(f"  Max:    {max(full_times):.2f}ms")
print(f"  P95:    {sorted(full_times)[94]:.2f}ms")
print(f"  P99:    {sorted(full_times)[98]:.2f}ms")

print()
print("PERFORMANCE BENCHMARK: COMPLETE")
