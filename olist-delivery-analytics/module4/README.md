# Module 4 Delivery Risk Model

This folder contains the additive Module 4 work for the Olist delivery analytics capstone. It is isolated from the previously submitted Module 3 pipeline. Source CSVs are read from `../data/raw`; no source data or order-level customer data is included in this folder.

## Reproduce

1. Install `module4/requirements.txt` in a fresh environment.
2. Place the licensed Olist CSV files in `data/raw/` using the filenames already documented in `../docs/data_dictionary.md`.
3. From the repository root, run `python olist-delivery-analytics/module4/train.py`.
4. Start the API with `uvicorn olist-delivery-analytics.module4.api:app --app-dir olist-delivery-analytics/module4` (or run `uvicorn api:app` from this folder).

The script writes charts, metrics, fairness results, model artifacts, and an MLflow run to this folder. The model predicts whether a delivered order later missed the promised date using checkout-time features. It is retrospective course research and is not approved for live operational decisions.

## Deliverables

- `validation_report.md` and `validation_report.docx`
- `notebooks/shap_and_fairness.ipynb`
- `reports/fairness_metrics.csv`, `reports/metrics.json`, and plots
- `docs/model_card.md` and `docs/ai_disclosure_form.docx`
- `model_artifacts/delivery_risk_model.joblib`
- `api.py` with `/predict`
- `mlruns/` experiment data (local and not committed)

Protected demographic attributes are not present in this dataset. Regional metrics are labeled operational diagnostics only and cannot establish demographic fairness.
