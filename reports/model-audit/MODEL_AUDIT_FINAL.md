# FloodRisk AI Final Scientific Audit

## Executive Summary

This report consolidates verified evidence from MODEL-AUDIT-1, MODEL-AUDIT-1.5, MODEL-AUDIT-1.6, and MODEL-AUDIT-2.

Scope covered:
- Open-Meteo Provider
- Feature Engineering
- Prediction Gateway
- Random Forest
- Risk Classification
- Recommendation Engine
- Backend API
- Frontend Integration

Overall result:
- The realtime inference pipeline is scientifically valid based on runtime validation.
- Feature engineering is consistent with the 9-feature specification.
- The deployed Random Forest model functions correctly and shows strong test performance.
- The only material technical concern is an sklearn artifact/runtime version mismatch warning.

## Audit Scope

The audit inspected the deployed inference stack end-to-end and the model evaluation artifacts stored in the repository. No production code, backend behavior, frontend behavior, model training, or ML artifacts were modified.

## MODEL-AUDIT-1

Verified findings:
- The realtime inference pipeline routes through `backend/services/prediction_gateway.py`.
- Open-Meteo data is retrieved in `backend/providers/openmeteo_provider.py`.
- Feature engineering is performed in `ml/feature_engineering/builder.py`.
- The feature order matches `ml/artifacts/feature_list.json` exactly.
- The backend realtime API returns `fri`, `tingkat_risiko`, `rekomendasi`, `mitigasi`, and weather data.
- The frontend consumes `/api/prediksi/realtime` and renders the returned values.

Conclusion:
- The pipeline structure was correct from source inspection, but runtime proof was still required at that stage.

## MODEL-AUDIT-1.5

Verified evidence:
- `reports/model-audit/feature_importance.csv` shows the top features as `rain7`, `rain3`, and `rh_avg`.
- `reports/model-audit/realtime_distribution.csv` and `realtime_distribution_stats.csv` show realtime rows with only `rr` and `rh_avg` populated; engineered rolling fields are empty in that exported distribution.
- `reports/model-audit/distribution_diff_summary.csv` marks several features as `High Shift` because realtime summary tables were incomplete or missing.
- `reports/model-audit/model_feature_importances.csv` shows correlations only for `rr` and `rh_avg`; the other features were marked `Data missing` in that report.

Confirmed later:
- The feature ranking itself was real and came from the trained model.

Disproved or not confirmed:
- The missing engineered fields in the distribution export were not proven to be a runtime pipeline bug.

Interpretation:
- MODEL-AUDIT-1.5 identified a data-visibility problem in the audit exports, not a confirmed inference failure.

## MODEL-AUDIT-1.6

Runtime validation evidence:
- `tests/test_weather_provider.py` and `tests/test_api_integration.py` both passed.
- Direct runtime execution of `predict_from_raw()` produced a 9-feature vector in the correct order.
- Runtime feature vector observed:
  `rr, rain3, rain7, rain14, rh_avg, temp_range, rainfall_anomaly, month, day_of_year`
- Runtime example prediction:
  `fri = 52.32`, `tingkat_risiko = Risiko Sedang`
- The realtime API response matched the internal prediction output.
- The frontend service and dashboard consume the same API response fields.

Why the earlier suspicion was not confirmed:
- The engineered feature gaps seen in distribution exports were not evidence that the runtime pipeline dropped features.
- Runtime validation showed the 9-feature vector was assembled and passed to Random Forest correctly.

## MODEL-AUDIT-2

Dataset evidence:
- Source dataset: `data/processed/bmkg_fri_dataset.csv`
- Total samples: `726`
- Training split: `580`
- Test split: `146`
- Split method: chronological 80/20, no shuffle
- Target variable: `fri`

Performance metrics on the deployed model:
- MAE: `3.5122`
- RMSE: `4.7820`
- R²: `0.9212`
- Explained Variance: `0.9217`

Generalization:
- Train R²: `0.9949`
- Test R²: `0.9212`
- Train MAE: `1.0208`
- Test MAE: `3.5122`

Scientific interpretation:
- Test performance is strong for a 0–100 regression target.
- The train-test gap is real and indicates some overfitting tendency, but not severe failure.
- The model generalizes well enough to be scientifically acceptable based on available evidence.

## Technical Debt

Verified items:
- sklearn artifact/runtime version mismatch warning was observed when loading `ml/artifacts/random_forest.pkl`.
  - Artifact warning: serialized with sklearn `1.6.1`
  - Runtime sklearn version: `1.8.0`
- The previous audit report file for MODEL-AUDIT-1.6 was not present in the workspace, so this final report relies on verified findings recorded during the audit session and current repository outputs.

## Limitations

- The original training notebook is not stored in the repository.
- There is no separate saved validation split beyond the chronological train/test artifacts.
- The audit is based on repository artifacts and runtime validation available in the current workspace.
- No new metrics were generated for this report beyond the verified outputs from prior phases.

## Final Scientific Conclusion

1. Is the realtime inference pipeline valid?
- Yes. Runtime validation showed the feature vector, API response, and frontend consumption are consistent.

2. Is feature engineering consistent?
- Yes. The 9-feature order matches `ml/artifacts/feature_list.json`, and runtime execution produced the expected vector.

3. Is the deployed Random Forest model functioning correctly?
- Yes. The model loads successfully and produces strong regression performance on the saved test split.

4. Is there evidence of inference pipeline bugs?
- No confirmed bug. The earlier suspicion about missing realtime engineered features was not supported by runtime evidence.

5. Is retraining scientifically justified?
- Not strictly from the current evidence. The model is acceptable, though the train-test gap and sklearn version mismatch justify monitoring and future validation.

## Recommendations

### Immediate
- Add explicit runtime logging for the 9-feature vector before model inference.
- Preserve the current deployed model and pipeline behavior.

### Medium-term
- Re-run artifact compatibility checks when the sklearn runtime changes.
- Keep audit exports for feature distributions and comparisons under version control.

### Long-term
- Restore or document the original training notebook outside the production repository.
- Add a formal model governance record for future retraining decisions.

## Final Statement

FloodRisk AI demonstrates a scientifically coherent realtime inference pipeline and a well-performing deployed Random Forest regressor. The system is suitable for continued production use under audit monitoring, with future work focused on documentation completeness, artifact compatibility, and model governance rather than immediate retraining.
