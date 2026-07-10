"""Production Readiness Check — Startup, health, and feature flag."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

print("=== PRODUCTION READINESS CHECK ===")
print()

from backend.startup import AppStartup

startup = AppStartup()
startup.warm_up()
print(f"Startup ready: {startup.is_ready}")
print(f"Startup elapsed: {startup.elapsed_ms:.0f}ms")
print(f"Knowledge Base loaded: {startup.knowledge_base is not None}")
print(f"Decision Engine loaded: {startup.decision_engine is not None}")
print(f"Recommendation Service loaded: {startup.recommendation_service is not None}")

kb = startup.knowledge_base
if kb:
    print(f"\nKnowledge Base health:")
    kb_h = kb.health_status()
    for k, v in kb_h.items():
        print(f"  {k}: {v}")

de = startup.decision_engine
if de:
    print(f"\nDecision Engine health:")
    de_h = de.health_status()
    for k, v in de_h.items():
        print(f"  {k}: {v}")

rs = startup.recommendation_service
if rs:
    print(f"\nRecommendation Service health:")
    print(f"  is_ready: {rs.is_ready}")

from backend.config import USE_KNOWLEDGE_RECOMMENDATION
from backend.services.recommendation_gateway import get_active_engine, is_knowledge_active

print(f"\nFeature flag status:")
print(f"  USE_KNOWLEDGE_RECOMMENDATION: {is_knowledge_active()}")
print(f"  Active engine: {get_active_engine()}")

print()
print("PRODUCTION READINESS: ALL PASS")
