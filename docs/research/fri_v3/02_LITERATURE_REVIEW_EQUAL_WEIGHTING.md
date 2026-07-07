# Literature Review: Equal Weighting in Composite Index Methodology

## Objective

Provide a literature-based justification for considering equal weighting as a scientifically defensible approach for FRI Version 3.

This document distinguishes between established scientific evidence and research hypotheses. Claims marked as hypotheses have not been experimentally verified for this specific system and dataset.

---

## 1. Composite Index Methodology

A composite index aggregates multiple individual indicators into a single numerical value representing a multidimensional concept (OECD, 2008). The FRI is a composite index that combines four meteorological indicators into a unified flood risk score.

The key methodological steps in composite index construction are (Nardo et al., 2005):

1. Theoretical framework development
2. Variable selection
3. Multivariate analysis
4. **Weighting**
5. Aggregation
6. Sensitivity analysis
7. Validation

Weighting is widely recognised as one of the most consequential methodological choices, capable of substantially altering index rankings and distributions (Greco et al., 2019).

**Reference**: OECD (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publications.

---

## 2. Equal Weighting as a Methodological Baseline

Equal weighting assigns the same weight to every component indicator. It is the most widely used weighting method in composite index construction (Decancq & Lugo, 2013).

### Established Advantages (Evidence-Based)

1. **Simplicity and Transparency**: Equal weights are immediately interpretable and require no complex statistical estimation (Munda & Nardo, 2009).

2. **Natural Baseline**: Equal weighting provides an unbiased starting point against which alternative weighting schemes can be compared (Freudenberg, 2003).

3. **Avoids Arbitrary Differentiation**: When empirical justification for differential weighting is limited or contested, equal weighting avoids imposing unsupported assumptions (Meyer et al., 1993).

4. **Reduces Model Overfitting Risk**: Data-driven weight optimisation can capitalise on sample-specific noise. Equal weighting is immune to this form of overfitting (Hastie et al., 2009).

### Established Disadvantages (Evidence-Based)

1. **Ignores Differential Importance**: Not all indicators contribute equally to the underlying construct. Equal weighting may under-represent or over-represent specific dimensions (OECD, 2008).

2. **Lack of Theoretical Grounding**: For constructs where causal mechanisms are well understood (e.g., flood risk where rainfall is the primary driver), equal weighting may contradict established physical science (Greco et al., 2019).

3. **Sensitivity to Indicator Set**: The relative contribution of each dimension depends on how many indicators represent it. If a construct has multiple correlated rainfall indicators and a single humidity indicator, equal weighting overweights the rainfall dimension (Decancq & Lugo, 2013).

**Reference**: Decancq, K., & Lugo, M. A. (2013). Weights in Multidimensional Indices of Wellbeing: An Overview. *Econometric Reviews*, 32(1), 7–34.

---

## 3. Equal Weighting in Environmental and Risk Indices

Several established environmental indices use equal or near-equal weighting:

| Index | Components | Weighting | Source |
|-------|-----------|-----------|--------|
| Environmental Performance Index (EPI) | 40 indicators across 11 categories | Category-level equal weighting | Wendling et al. (2020) |
| Human Development Index (HDI) | 4 indicators across 3 dimensions | Equal dimensional weights | UNDP (2022) |
| Climate Risk Index (CRI) | 4 indicators | Equal (implicit) | Germanwatch (2021) |
| Water Poverty Index | 5 components | Equal weights (default) | Sullivan et al. (2003) |

These examples demonstrate that equal weighting has precedent in policy-relevant composite indices. However, none of these indices specifically address flood risk or use precipitation-based variables.

---

## 4. Information Redundancy Between RR and Rain7

### Evidence

RR (daily rainfall) and Rain7 (7-day cumulative rainfall) are not independent variables. Rain7 is a rolling sum that includes RR as its most recent term. The Pearson correlation between RR and Rain7 in the FRI v2 scoring pipeline has been documented as moderately high (see `sprint-v2.2-statistical-analysis.md`).

Redundancy between rainfall accumulation windows is a recognised issue in hydrometeorological index construction (Keyantash & Dracup, 2004). When correlated indicators are included in a composite index without adjustment, the shared variance is implicitly double-counted.

### Hypotheses

- **H₁a**: The combined weight of RR (10%) and Rain7 (50%) in FRI v2 (= 60%) over-represents the precipitation dimension relative to its independent information content.

- **H₁b**: Reducing the combined precipitation weight from 60% to 50% (25% + 25%) will produce a target distribution that better reflects multi-dimensional flood risk contributions.

---

## 5. Why Rain7 Should Not Necessarily Dominate the Index

### Evidence

Rain7 is a cumulative measure of antecedent precipitation. While antecedent moisture is a critical flood precondition, it is not the sole determinant of flood risk. Key additional factors include:

1. **Rainfall intensity**: A single high-intensity event on dry soil can produce flash flooding even without antecedent saturation (Smith et al., 2018). RR captures this dimension.

2. **Atmospheric moisture**: RH_avg governs evapotranspiration rates and indicates the potential for additional or sustained precipitation (Trenberth et al., 2003). Persistent high humidity extends waterlogging duration.

3. **Temperature**: Tavg influences evapotranspiration rates and, through the Clausius-Clapeyron relationship, the moisture-holding capacity of the atmosphere (Allen & Ingram, 2002). Warmer air can hold more moisture, potentially intensifying rainfall when precipitation occurs.

### Premise

The literature supports multi-dimensional flood risk assessment but does not prescribe a specific weight allocation between precipitation accumulation, intensity, humidity, and temperature. The choice of Rain7 at 50% is one plausible configuration, not a scientifically mandated one.

---

## 6. Hydrological Reasoning for Balanced Weights

From a hydrological perspective, flooding in lowland tropical environments involves multiple interacting processes:

| Process | Primary Variable | Weight Consideration |
|---------|-----------------|---------------------|
| Infiltration exceedance (Hortonian overland flow) | RR (intensity) | Captures rapid-onset flooding |
| Saturation excess (Dunne overland flow) | Rain7 (antecedent) | Captures gradual soil saturation |
| Evapotranspiration suppression | RH_avg | Extends surface water persistence |
| Atmospheric moisture capacity | Tavg | Modulates rainfall potential |

No single process dominates across all flood events. Equal weighting can be justified as a neutral prior that treats each process with equal importance until empirical evidence supports differential weighting.

**Hypothesis**: H₂ — Equal weighting produces a hydrologically more representative index than Rain7-dominant weighting because it acknowledges the multi-process nature of tropical lowland flooding.

---

## 7. Agricultural Reasoning for Balanced Weights

For horticultural flood risk applications, the four variables affect crop outcomes through distinct pathways:

| Variable | Agricultural Impact Pathway |
|---------|------------------------------|
| RR | Direct physical damage from rain, soil erosion, seed displacement |
| Rain7 | Soil waterlogging duration, root zone oxygen depletion |
| RH_avg | Fungal disease pressure, post-rain drying rate |
| Tavg | Crop growth rate, evapotranspiration demand, disease epidemiology |

These four pathways are interdependent but not equivalent. A balanced weighting ensures that no single agricultural risk pathway dominates the composite risk score.

**Hypothesis**: H₃ — A balanced FRI target produces commodity recommendations that are more robust across diverse weather scenarios because no single variable can dominate the risk assessment.

---

## 8. Random Forest Regression-to-the-Mean Behaviour

### Evidence

Random Forest is an ensemble method that averages predictions across many decision trees (Breiman, 2001). By construction, its predictions tend toward the conditional mean of the training target, a phenomenon known as regression to the mean (Friedman et al., 2001).

When the training target distribution is concentrated around medium values, the model's predictions will similarly cluster around the medium range, reducing sensitivity at the extremes.

### Hypotheses

- **H₄ₐ**: FRI v2's Rain7-dominant weighting compresses the target distribution, reducing variance and contributing to Random Forest prediction concentration around medium-risk values.

- **H₄_b**: FRI v3's equal weighting will produce a wider target distribution, enabling Random Forest to learn more differentiated predictions across the full risk spectrum.

- **H₄_c**: Prediction diversity (measured by standard deviation of predictions) will improve under FRI v3 while overall performance (MAE, RMSE, R²) remains comparable to or better than v2.

---

## 9. Summary of Evidence vs. Hypothesis

| Claim | Status |
|-------|--------|
| Equal weighting is a standard composite index method | **Evidence** (OECD, 2008; Decancq & Lugo, 2013) |
| RR and Rain7 are correlated variables | **Evidence** (confirmed in FRI v2 statistical analysis) |
| Random Forest exhibits regression to the mean | **Evidence** (Breiman, 2001; Friedman et al., 2001) |
| Equal weighting will improve FRI distribution | **Hypothesis** (not yet tested) |
| Equal weighting will improve ML prediction performance | **Hypothesis** (not yet tested) |
| Equal weighting will improve recommendation diversity | **Hypothesis** (not yet tested) |

---

## References

- Allen, M. R., & Ingram, W. J. (2002). Constraints on future changes in climate and the hydrologic cycle. *Nature*, 419(6903), 224–232.
- Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.
- Decancq, K., & Lugo, M. A. (2013). Weights in multidimensional indices of wellbeing: An overview. *Econometric Reviews*, 32(1), 7–34.
- Freudenberg, M. (2003). Composite indicators of country performance: A critical assessment. *OECD Science, Technology and Industry Working Papers*, 2003/16.
- Friedman, J., Hastie, T., & Tibshirani, R. (2001). *The Elements of Statistical Learning*. Springer.
- Greco, S., Ishizaka, A., Tasiou, M., & Torrisi, G. (2019). On the methodological framework of composite indices: A review and issues. *Journal of the Royal Statistical Society: Series A*, 182(1), 79–108.
- Keyantash, J., & Dracup, J. A. (2004). An aggregate drought index: Assessing drought severity based on fluctuations in the hydrologic cycle. *Water Resources Research*, 40(9).
- Meyer, M. A., Booker, J. M., & Kianifard, F. (1993). *Eliciting and Analyzing Expert Judgment: A Practical Guide*. SIAM.
- Munda, G., & Nardo, M. (2009). Noncompensatory/nonlinear composite indicators for ranking countries. *Journal of the Royal Statistical Society: Series A*, 172(2), 361–384.
- Nardo, M., et al. (2005). *Handbook on Constructing Composite Indicators*. OECD Statistics Working Paper.
- OECD (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publications.
- Smith, J. A., et al. (2018). Flash flooding in urban areas. *Water Resources Research*, 54(8), 4996–5015.
- Sullivan, C. A., et al. (2003). The Water Poverty Index: Development and application. *Water International*, 28(2), 189–202.
- Trenberth, K. E., et al. (2003). The changing character of precipitation. *Bulletin of the American Meteorological Society*, 84(9), 1205–1218.
- Wendling, Z. A., et al. (2020). *Environmental Performance Index*. Yale Center for Environmental Law & Policy.
