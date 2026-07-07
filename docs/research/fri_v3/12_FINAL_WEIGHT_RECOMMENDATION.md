# Final Weight Recommendation

## Recommended Configuration

**Configuration F** — V2-like with reduced Rain7, higher RH

| Feature | Weight |
|---------|--------|
| RR | 15% |
| Rain7 | 35% |
| RH_avg | 30% |
| Tavg | 20% |
| **Total** | **100%** |

## Rationale

### 1. Distribution Quality

Configuration F produces the best balance among non-v2 configs:
- Mean = 44.38 (between v2's 45.40 and equal-weight's 41.64)
- Std = 14.44 (preserves 77% of v2 spread)
- Range = 70.50
- CV = 0.3253

### 2. Risk Class Distribution

- Low: 180 (24.8%) — adequate low-risk representation
- Medium: 495 (68.2%) — dominant but not collapsed
- High: 51 (7.0%) — best extreme-risk retention among non-A configs

Configuration F achieves the highest High-risk proportion (7.0%) among all non-v2 configurations, making it the best candidate for preserving extreme-value signal.

### 3. Hydrological Interpretation

Rain7 (35%) remains the largest single weight, consistent with the hydrological principle that antecedent rainfall is the primary flood precondition. However, reducing it from 50% to 35% acknowledges that:
- RR (15%) captures flash-flood potential from high-intensity daily events
- RH_avg (30%) reflects humidity's role in sustaining wet conditions and reducing evapotranspiration
- Tavg (20%) provides thermal context without over-contributing

### 4. Agricultural Interpretation

For horticultural flood risk:
- Rain7 (35%) captures prolonged waterlogging risk
- RH_avg (30%) captures disease pressure from persistent humidity
- RR (15%) captures direct rain damage potential
- Tavg (20%) captures thermal conditions affecting crop recovery

### 5. Machine Learning Suitability

Configuration F provides a target distribution that:
- Has adequate variance (σ = 14.44) for Random Forest to learn differentiated patterns
- Retains extreme values (max = 79) for training on high-risk scenarios
- Preserves all three risk classes without collapse
- Reduces regression-to-the-mean risk compared to v2 by balancing feature contributions

## Comparison with Other Configurations

| Criterion | A (v2) | B (Equal) | F (Recommended) | E (Balanced) |
|-----------|--------|-----------|-----------------|------------------|
| Std | 18.68 | 12.53 | 14.44 | 15.08 |
| High % | 16.1% | 2.8% | 7.0% | 5.6% |
| Single var dominance | Rain7=50% | None | Rain7=35% | Rain7=40% |
| Rain dominance | 60% | 50% | 50% | 60% |
| RH + Tavg contribution | 40% | 50% | 50% | 40% |
| Skewness | -0.146 | 0.172 | -0.080 | -0.009 |

## Limitations

1. **No ML validation**: This recommendation is based solely on target distribution analysis. Model training is required to confirm that Configuration F produces superior predictions.
2. **No flood event validation**: Without ground-truth flood records, optimality cannot be empirically confirmed.
3. **Dataset-specific**: These findings apply to the 726-record BMKG dataset and may not generalise to other regions or longer timeframes.
4. **Quantile-based scoring**: Percentile thresholds are dataset-dependent; if the dataset shifts, score distributions and optimal weights may change.

## Next Step

1. Generate FRI target using Configuration F weights.
2. Train Random Forest on the new target.
3. Compare against v2 baseline (MAE, RMSE, R², prediction distribution).
4. Validate hypotheses H₁–H₆ from `03_RESEARCH_HYPOTHESIS.md`.
