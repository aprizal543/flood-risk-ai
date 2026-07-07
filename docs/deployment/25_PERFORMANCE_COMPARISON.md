# Performance Comparison

## Expected Latency Reduction

### Geocoding

| Metric              | Before Cache | After Cache (HIT) | Improvement |
|---------------------|-------------|-------------------|-------------|
| Average latency     | ~200–500 ms | ~0.001 ms         | 200,000–500,000x |
| P99 latency         | ~2000 ms    | ~0.01 ms          | 200,000x    |
| External HTTP calls | 1 per request | 0 after first    | 100% reduction for repeats |

### Forecast

| Metric              | Before Cache | After Cache (HIT) | Improvement |
|---------------------|-------------|-------------------|-------------|
| Average latency     | ~300–800 ms | ~0.001 ms         | 300,000–800,000x |
| P99 latency         | ~3000 ms    | ~0.01 ms          | 300,000x    |
| External HTTP calls | 1 per request | 0 after first    | 100% reduction for repeats |

### End-to-End Request

| Scenario           | Cache MISS      | Cache HIT       | Speedup  |
|--------------------|----------------|----------------|----------|
| First request      | ~1200 ms       | N/A            | —        |
| Repeat (same city) | ~1200 ms       | ~300–400 ms    | 3–4x     |

## Cache Hit Rate Projections

Assumptions:
- 60% of daily requests are for top-5 cities (Pekanbaru, Dumai, Jakarta, etc.)
- 40% are for less-common cities

| Day | Requests | Unique Cities | Geocoding Hit Rate | Forecast Hit Rate |
|-----|---------|---------------|-------------------|-------------------|
| 1   | 1000    | 50            | 50%               | 60%               |
| 7   | 7000    | 80            | 80%               | 75%               |
| 30  | 30000   | 120           | 90%               | 85%               |

After 30 days of operation, 85–90% of cache lookups should be HITs.

## API Call Reduction

Assume 10,000 requests/month:

| Component    | Without Cache | With Cache (85% HR) | Savings |
|-------------|--------------|--------------------|---------|
| Geocoding   | 10,000       | 1,500              | 8,500   |
| Forecast    | 10,000       | 1,500              | 8,500   |
| **Total**   | **20,000**   | **3,000**          | **17,000** |

## Benchmark Script

Run the cache benchmark to measure real-world latency:

```bash
python scripts/cache_benchmark.py --city Pekanbaru --iterations 5
```

Sample output:

```
>>> Geocoding Benchmark <<<
  Cache MISS avg: 342.15 ms
  Cache HIT  avg: 0.002 ms
  Speedup ratio:  171075.0x

>>> Forecast Benchmark <<<
  Cache MISS avg: 521.78 ms
  Cache HIT  avg: 0.003 ms
  Speedup ratio:  173926.7x
```
