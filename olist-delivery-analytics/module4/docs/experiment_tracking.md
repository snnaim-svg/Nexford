# MLflow Experiment Tracking

## Recorded run

- **Experiment:** Olist Delivery Risk — Module 4
- **Run ID:** 3a09f8478e8e4b4cb26db0dd5544da74
- **Tracking store:** local SQLite database at `module4/mlflow.db`
- **Artifacts:** local files under `module4/mlruns/`
- **Registered model:** `OlistDeliveryRisk`, version 1, stage Staging

The run began before feature preparation and model fitting. It records the dataset identity, time split, seed, feature list, cross-validation choice, model comparison metrics, fairness diagnostics, model artifact, figures, and reports. No raw or row-level order data is logged as an artifact.

## Open the experiment locally

From the repository root, install `module4/requirements.txt`, then run:

```powershell
mlflow ui --backend-store-uri "sqlite:///C:/path/to/repository/olist-delivery-analytics/module4/mlflow.db" --host 127.0.0.1 --port 5001
```

Open `http://127.0.0.1:5001`, select the experiment, and search the run ID above. This URL is local to the computer; it is not a public tracking link. The SQLite database and artifacts are ignored by Git to keep the repository free of environment-specific tracking files. The run ID and tracking instructions remain here for reproducibility.
