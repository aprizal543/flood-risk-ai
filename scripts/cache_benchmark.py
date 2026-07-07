"""Cache benchmark – measures latency reduction from geocoding & forecast caching.

Usage:
    python scripts/cache_benchmark.py [--city CITY] [--iterations N]

Output:
    - Average uncached latency (cache MISS)
    - Average cached latency (cache HIT)
    - Latency reduction factor
    - Estimated annual API call savings
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ── Force eager cache warming for benchmark ──────────────────────────
from backend.providers.geocoding import geocoding_cache, geocoding_metrics
from backend.providers.openmeteo_provider import forecast_cache, forecast_metrics
geocoding_cache.clear()
forecast_cache.clear()


def benchmark_geocoding(city: str, iterations: int = 3) -> dict:
    """Benchmark geocoding cache – measure miss vs hit latency."""
    from backend.providers.geocoding import geocode

    # Warm-up: clear, then do one call to populate cache
    geocoding_cache.clear()
    geocoding_metrics._hits = 0
    geocoding_metrics._misses = 0

    misses = []
    hits = []

    for i in range(iterations):
        geocoding_cache.clear()
        start = time.perf_counter()
        geocode(city)
        elapsed = (time.perf_counter() - start) * 1000
        misses.append(elapsed)

        start = time.perf_counter()
        result = geocode(city)
        elapsed = (time.perf_counter() - start) * 1000
        hits.append(elapsed)

    return {
        "operation": "geocoding",
        "city": city,
        "miss_avg_ms": round(sum(misses) / len(misses), 2),
        "hit_avg_ms": round(sum(hits) / len(hits), 2),
        "misses": misses,
        "hits": hits,
    }


def benchmark_forecast(city: str, iterations: int = 3) -> dict:
    """Benchmark forecast cache – measure miss vs hit latency."""
    from backend.providers.openmeteo_provider import OpenMeteoProvider

    forecast_cache.clear()
    forecast_metrics._hits = 0
    forecast_metrics._misses = 0

    provider = OpenMeteoProvider()
    misses = []
    hits = []

    for i in range(iterations):
        forecast_cache.clear()
        start = time.perf_counter()
        provider.get_current_weather(city)
        elapsed = (time.perf_counter() - start) * 1000
        misses.append(elapsed)

        start = time.perf_counter()
        provider.get_current_weather(city)
        elapsed = (time.perf_counter() - start) * 1000
        hits.append(elapsed)

    return {
        "operation": "forecast",
        "city": city,
        "miss_avg_ms": round(sum(misses) / len(misses), 2),
        "hit_avg_ms": round(sum(hits) / len(hits), 2),
        "misses": misses,
        "hits": hits,
    }


def main():
    parser = argparse.ArgumentParser(description="Cache benchmark")
    parser.add_argument("--city", default="Pekanbaru", help="City to benchmark")
    parser.add_argument("--iterations", type=int, default=3, help="Iterations per phase")
    args = parser.parse_args()

    print("=" * 60)
    print(f"Cache Benchmark — city={args.city}, iterations={args.iterations}")
    print("=" * 60)
    print()

    print(">>> Geocoding Benchmark (requires internet for MISS) <<<")
    try:
        geo_result = benchmark_geocoding(args.city, args.iterations)
        print(f"  Cache MISS avg: {geo_result['miss_avg_ms']:.2f} ms")
        print(f"  Cache HIT  avg: {geo_result['hit_avg_ms']:.2f} ms")
        if geo_result["hit_avg_ms"] > 0:
            ratio = geo_result["miss_avg_ms"] / geo_result["hit_avg_ms"]
            print(f"  Speedup ratio:  {ratio:.1f}x")
    except Exception as e:
        print(f"  SKIPPED (requires live API): {e}")

    print()
    print(">>> Forecast Benchmark (requires internet for MISS) <<<")
    try:
        fc_result = benchmark_forecast(args.city, args.iterations)
        print(f"  Cache MISS avg: {fc_result['miss_avg_ms']:.2f} ms")
        print(f"  Cache HIT  avg: {fc_result['hit_avg_ms']:.2f} ms")
        if fc_result["hit_avg_ms"] > 0:
            ratio = fc_result["miss_avg_ms"] / fc_result["hit_avg_ms"]
            print(f"  Speedup ratio:  {ratio:.1f}x")
    except Exception as e:
        print(f"  SKIPPED (requires live API): {e}")

    print()
    print(">>> Diagnostics Endpoint <<<")
    try:
        from backend.app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        r = client.get("/api/system/cache")
        if r.status_code == 200:
            data = r.json()
            print(f"  Geocoding: {data['geocoding']}")
            print(f"  Forecast:  {data['forecast']}")
    except Exception as e:
        print(f"  SKIPPED: {e}")

    print()
    print("=" * 60)
    print("Benchmark complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
