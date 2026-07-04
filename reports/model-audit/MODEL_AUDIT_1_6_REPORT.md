# MODEL-AUDIT-1.6 Report

## Verdict

PASS.

Runtime validation proves that the realtime inference pipeline sends the expected 9-feature vector to the Random Forest model and that the API response matches the internal prediction result for the audited fixture.

## Runtime Evidence

Command executed:

```powershell
python scripts/audit_1_6_validate.py
```

Output artifact:

```text
reports/model-audit/audit_1_6_runtime_validation.json
```

The script uses deterministic weather data and patches the Open-Meteo provider only inside the validation process. Application runtime code is not modified.

## Pipeline Validated

```text
Open-Meteo provider -> realtime API -> prediction_gateway -> build_features -> Random Forest
```

Source locations verified:

- `backend/routers/realtime.py`
- `backend/services/prediction_gateway.py`
- `ml/feature_engineering/builder.py`
- `ml/service/predictor.py`
- `ml/predict/random_forest.py`

## Captured Feature Vector

Feature order captured at Random Forest input:

```text
rr, rain3, rain7, rain14, rh_avg, temp_range, rainfall_anomaly, month, day_of_year
```

Captured values:

| Feature | Value |
|---|---:|
| rr | 14.0 |
| rain3 | 41.0 |
| rain7 | 73.0 |
| rain14 | 123.0 |
| rh_avg | 83.0 |
| temp_range | 8.0 |
| rainfall_anomaly | 62.0 |
| month | 1.0 |
| day_of_year | 14.0 |

## API vs Internal Prediction

| Field | API | Internal |
|---|---:|---:|
| model | rf | rf |
| fri | 56.54 | 56.54 |
| tingkat_risiko | Risiko Sedang | Risiko Sedang |

Additional API checks:

- HTTP status: `200`
- `hari_historis`: `13`
- realtime weather `rr`: `14.0`
- provider history request: `14` days

## Root Cause Analysis

No runtime defect was found in the audited realtime RF path.

The validation confirms:

- All 9 features are generated.
- Feature order matches the model feature order.
- Rolling rainfall features reach the Random Forest input.
- API response matches the direct internal prediction result.

Residual risk:

- The validation emitted an `InconsistentVersionWarning` because the Random Forest artifact was trained with scikit-learn `1.6.1` and loaded with `1.8.0`. This does not fail the audited consistency checks, but it should be tracked for production reproducibility.

## Conclusion

MODEL-AUDIT-1.6 is complete for the realtime RF inference path. The pipeline is internally consistent based on runtime evidence from `audit_1_6_runtime_validation.json`.
