# Sprint v2.2 FRI v1 vs FRI v2 Comparison

## Summary Metrics

| Metric | Value |
|--------|-------|
| Mean Difference (FRI_v2 - FRI_v1) | 4.8608 |
| Median Difference (FRI_v2 - FRI_v1) | 4.7258 |
| Records With Category Change | 153 |
| Category Change Percentage | 21.07% |

## Distribution Comparison

| Bin | FRI v1 Count | FRI v2 Count |
|-----|--------------|--------------|
| 0-20 | 139 | 95 |
| 20-40 | 219 | 185 |
| 40-60 | 238 | 245 |
| 60-80 | 114 | 197 |
| 80-100 | 16 | 4 |

## Scientific Observation

The approved v2 weighting makes the index less dispersed overall than FRI v1, but more concentrated around the weekly-rainfall signal. The largest methodological driver is the 50% `Rain7` contribution, while removed short-window, long-window, temperature-range, and anomaly features no longer dilute the weekly antecedent rainfall signal.
