# Data Lineage

## Objective

This document traces the complete end-to-end data pipeline from raw BMKG Excel files through all transformation stages to the final dashboard recommendations. Each stage is described with its inputs, processes, outputs, and data quality checkpoints. The lineage supports reproducibility, auditability, and thesis documentation (Chapter III – Methodology).

---

## Pipeline Overview

```
Stage 1: Data Acquisition
    ↓
Stage 2: Data Merge (Sprint 1)
    ↓
Stage 3: Data Validation (Sprint 1.5)
    ↓
Stage 4: Data Cleaning (Sprint 2)
    ↓
Stage 5: Feature Engineering (Sprint 3)
    ↓
Stage 6: FRI Computation (Sprint 4)
    ↓
Stage 7: Classification & Recommendation (Sprint 5)
    ↓
Stage 8: Dashboard Presentation
```

---

## Stage 1: Data Acquisition

### Input
- BMKG daily climate observation reports downloaded as Excel files
- Source: BMKG Dataonline or station reports from Stasiun Meteorologi Sultan Syarif Kasim II

### Process
- Manual download of monthly Excel files (`laporan_iklim_harian-[bulan]-[tahun].xlsx`)
- Files placed in designated raw data directory

### Output
| Artifact | Path |
|----------|------|
| Raw Excel files | `data/raw/pekanbaru/*.xlsx` |

### Quality Checkpoint
- Verify file integrity (not corrupted, openable)
- Confirm station identity (WMO ID 96109)
- Confirm expected columns present in header row

### Data Characteristics
- Format: BMKG standard daily climate report (xlsx)
- Metadata rows: 5 rows (station ID, name, coordinates, elevation)
- Header row: Row 8 (TANGGAL, TN, TX, TAVG, RH_AVG, RR)
- Data rows: 28–31 per file (daily observations)
- Sentinel values: 8888 (unmeasured), 9999 (no observation)

---

## Stage 2: Data Merge

### Input
| Artifact | Path |
|----------|------|
| Raw Excel files | `data/raw/pekanbaru/*.xlsx` |

### Process
Script: `scripts/etl/01_merge_dataset.py`

1. Discover all `.xlsx` files, excluding temporary files (`~$*`)
2. For each file:
   - Detect header row by scanning for "TANGGAL" in column A
   - Read data starting from header row
   - Filter rows with valid parseable dates (removes KETERANGAN metadata)
   - Add `source_file` column with original filename
3. Validate required columns: TANGGAL, TN, TX, TAVG, RH_AVG, RR
4. Concatenate all DataFrames
5. Convert TANGGAL to datetime (dayfirst=True)
6. Sort chronologically
7. Remove exact duplicate rows

### Output
| Artifact | Path | Format |
|----------|------|--------|
| Merged dataset | `data/interim/bmkg_merged.csv` | CSV, datetime + numeric + string columns |

### Quality Checkpoint
- Row count matches sum of individual file observations
- No NaN in TANGGAL column
- Zero duplicate rows
- Zero duplicate dates
- Zero missing calendar dates
- Sentinel values (8888, 9999) preserved (not modified)

### Data Shape (Current)
- Records: 726
- Columns: 7 (TANGGAL, TN, TX, TAVG, RH_AVG, RR, source_file)
- Date range: 2024-07-01 to 2026-06-26

---

## Stage 3: Data Validation

### Input
| Artifact | Path |
|----------|------|
| Merged dataset | `data/interim/bmkg_merged.csv` |

### Process
Script: `scripts/utils/validate_dataset.py`

1. Load merged dataset
2. Validate required columns present
3. Compute dataset summary (records, date range, coverage)
4. Count missing values per column
5. Count sentinel values (8888, 9999) per numeric column
6. Check for duplicate rows and duplicate dates
7. Identify missing calendar dates
8. Compute descriptive statistics
9. Tabulate source file distribution
10. Produce overall validation verdict

### Output
| Artifact | Path | Format |
|----------|------|--------|
| Validation report (human-readable) | `outputs/reports/dataset_validation_report.md` | Markdown |
| Validation report (machine-readable) | `outputs/reports/dataset_validation.json` | JSON |

### Quality Checkpoint
- Validation status: PASS (no critical issues)
- Missing calendar dates: 0
- Duplicate dates: 0
- Duplicate rows: 0
- All required columns present

### Gate Condition
Stage 4 (cleaning) should only proceed if validation passes. Failures require investigation and correction at Stage 1 or Stage 2.

---

## Stage 4: Data Cleaning

### Input
| Artifact | Path |
|----------|------|
| Merged dataset | `data/interim/bmkg_merged.csv` |

### Process
Script: `scripts/etl/02_clean_dataset.py`

1. Load merged dataset
2. Rename columns to snake_case (TANGGAL→tanggal, TN→tn, TX→tx, TAVG→tavg, RH_AVG→rh_avg, RR→rr)
3. Replace sentinel values (8888, 9999) with NaN in numeric columns
4. Enforce data types (tanggal→datetime64, numerics→float64)
5. Sort chronologically
6. Validate: row count unchanged, types correct, no duplicate dates

### Output
| Artifact | Path | Format |
|----------|------|--------|
| Cleaned dataset | `data/interim/bmkg_clean.csv` | CSV, snake_case columns, NaN for missing |

### Quality Checkpoint
- Row count preserved (726 = input)
- No sentinel values remain in numeric columns
- All numeric columns are float64
- tanggal is datetime64
- No rows dropped
- No values imputed

### Transformation Summary
| Action | Effect |
|--------|--------|
| Column rename | Standardised naming convention |
| Sentinel → NaN | 74 values converted (73× RR, 1× TX) |
| Type enforcement | Consistent dtypes for downstream computation |

---

## Stage 5: Feature Engineering

### Input
| Artifact | Path |
|----------|------|
| Cleaned dataset | `data/interim/bmkg_clean.csv` |

### Process
Script: `scripts/etl/03_feature_engineering.py`

1. Load cleaned dataset
2. Compute derived features:
   - `rain3` = rolling sum of `rr` over 3 days
   - `rain7` = rolling sum of `rr` over 7 days
   - `rain14` = rolling sum of `rr` over 14 days
   - `temp_range` = `tx` - `tn`
   - `month` = month extracted from `tanggal`
   - `rain_anomaly_pct` = percentile rank of `rr` within full distribution
   - `rain_deviation_30d` = `rr` - rolling mean of `rr` (30-day window, shifted)
3. Preserve all original columns
4. Sort chronologically

### Output
| Artifact | Path | Format |
|----------|------|--------|
| Feature-engineered dataset | `data/interim/bmkg_features.csv` | CSV, original + derived columns |

### Quality Checkpoint
- Row count preserved
- No original columns modified
- Rolling features have expected NaN in initial rows (window warm-up period)
- Feature ranges are physically plausible
- No data leakage (future data not used in rolling computations)

### Expected NaN Introduction
- `rain3`: First 2 rows NaN (insufficient window)
- `rain7`: First 6 rows NaN
- `rain14`: First 13 rows NaN
- `rain_deviation_30d`: First 30 rows NaN

---

## Stage 6: FRI Computation

### Input
| Artifact | Path |
|----------|------|
| Feature-engineered dataset | `data/interim/bmkg_features.csv` |
| Percentile thresholds | `config/thresholds.json` (computed during EDA) |
| Weight configuration | `config/weights.json` (TBD) |

### Process
Script: `scripts/etl/04_generate_fri.py`

1. Load feature-engineered dataset
2. Compute percentile thresholds from training data (or load pre-computed)
3. Apply scoring functions:
   - `score_rr` = BMKG piecewise linear scoring
   - `score_rain3` = percentile-based scoring
   - `score_rain7` = percentile-based scoring
   - `score_rain14` = percentile-based scoring
   - `score_rh_avg` = percentile-based scoring
   - `score_temp_range` = inverse percentile-based scoring
4. Compute weighted aggregation: FRI = Σ(w_i × S_i)
5. Compute confidence score based on available features
6. Apply classification thresholds (Low/Medium/High)

### Output
| Artifact | Path | Format |
|----------|------|--------|
| FRI dataset | `data/processed/fri_dataset.csv` | CSV with scores, FRI, confidence, classification |

### Quality Checkpoint
- FRI values bounded [0, 100]
- Confidence values bounded [0, 1]
- Classification consistent with FRI ranges
- Score distributions are plausible (not degenerate)
- No systematic bias toward floor or ceiling

---

## Stage 7: Classification & Recommendation

### Input
| Artifact | Path |
|----------|------|
| FRI dataset | `data/processed/fri_dataset.csv` |
| Commodity reference | `config/commodities.json` |
| Mitigation reference | `config/mitigations.json` |

### Process
Script: `scripts/etl/05_generate_label.py`

1. Load FRI dataset
2. Map FRI values to risk levels (Low/Medium/High)
3. Map risk levels to suitable commodity lists
4. Map risk levels + dominant risk factors to mitigation recommendations
5. Generate reasoning/explanation text

### Output
| Artifact | Path | Format |
|----------|------|--------|
| Recommendation dataset | `data/processed/recommendations.csv` | CSV with FRI + recommendations |
| Dashboard-ready JSON | `outputs/dashboard/daily_recommendations.json` | JSON for frontend consumption |

### Quality Checkpoint
- Every record has a valid risk level
- Commodity lists are non-empty for all risk levels
- Mitigation recommendations are present for Medium and High risk
- Reasoning text references actual score components

---

## Stage 8: Dashboard Presentation

### Input
| Artifact | Path |
|----------|------|
| Dashboard-ready data | `outputs/dashboard/daily_recommendations.json` |

### Process
- Frontend application renders daily FRI, risk level, commodity recommendations, and mitigation advice
- Interactive visualisation of FRI time series, component decomposition, and trend analysis

### Output
- User-facing dashboard with:
  - Daily Flood Risk Index (gauge/chart)
  - Risk level indicator (colour-coded)
  - Recommended commodities
  - Mitigation actions
  - FRI component breakdown (interpretability)
  - Confidence indicator

---

## Artifact Registry

### Data Artifacts

| Stage | Artifact | Path | Persistence |
|-------|----------|------|-------------|
| 1 | Raw Excel files | `data/raw/pekanbaru/*.xlsx` | Permanent (source of truth) |
| 2 | Merged dataset | `data/interim/bmkg_merged.csv` | Regenerable from Stage 1 |
| 3 | Validation reports | `outputs/reports/dataset_validation.*` | Regenerable from Stage 2 |
| 4 | Cleaned dataset | `data/interim/bmkg_clean.csv` | Regenerable from Stage 2 |
| 5 | Feature dataset | `data/interim/bmkg_features.csv` | Regenerable from Stage 4 |
| 6 | FRI dataset | `data/processed/fri_dataset.csv` | Regenerable from Stage 5 |
| 7 | Recommendations | `data/processed/recommendations.csv` | Regenerable from Stage 6 |

### Configuration Artifacts

| Artifact | Path | Purpose | Status |
|----------|------|---------|--------|
| Percentile thresholds | `config/thresholds.json` | Scoring function parameters | TBD (computed during EDA) |
| Weight configuration | `config/weights.json` | Aggregation weights | TBD (pending literature + EDA) |
| Commodity reference | `config/commodities.json` | Crop-to-tolerance mapping | TBD |
| Mitigation reference | `config/mitigations.json` | Risk-to-action mapping | TBD |

### Code Artifacts

| Script | Stage | Sprint |
|--------|-------|--------|
| `scripts/etl/01_merge_dataset.py` | 2 | Sprint 1 |
| `scripts/utils/validate_dataset.py` | 3 | Sprint 1.5 |
| `scripts/etl/02_clean_dataset.py` | 4 | Sprint 2 |
| `scripts/etl/03_feature_engineering.py` | 5 | Sprint 3 |
| `scripts/etl/04_generate_fri.py` | 6 | Sprint 4 |
| `scripts/etl/05_generate_label.py` | 7 | Sprint 5 |

---

## Data Quality Framework

### Validation Gates

Each stage transition has a validation gate that must pass before proceeding:

```
Stage 1 → Stage 2:  Files exist, not corrupted, correct station
Stage 2 → Stage 3:  Merge successful, no structural errors
Stage 3 → Stage 4:  Validation PASS (no critical issues)
Stage 4 → Stage 5:  Row count preserved, types correct, sentinels removed
Stage 5 → Stage 6:  Features computed, ranges plausible, no leakage
Stage 6 → Stage 7:  FRI bounded [0,100], distribution reasonable
Stage 7 → Stage 8:  All records have recommendations
```

### Immutability Principles

1. **Raw data is never modified**: All transformations produce new artifacts
2. **Each stage is reproducible**: Given the same input and code, output is deterministic
3. **Lineage is traceable**: Every derived value can be traced back to its raw source observation
4. **Configuration is versioned**: Thresholds and weights are stored as explicit configuration files, not hardcoded

---

## Relationship to Thesis

| Section | Thesis Chapter | Purpose |
|---------|---------------|---------|
| Pipeline overview | Chapter III §3.x (Alur Penelitian) | Research flow diagram |
| Stage descriptions | Chapter III §3.x (Metode Pengolahan Data) | Data processing methodology |
| Quality checkpoints | Chapter III §3.x (Validasi Data) | Quality assurance procedures |
| Artifact registry | Chapter III §3.x (Instrumen Penelitian) | Tools and outputs specification |
