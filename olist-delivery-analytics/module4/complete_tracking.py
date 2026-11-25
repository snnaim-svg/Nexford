"""Finish a run after training when only the artifact logging step was interrupted."""
import json
from pathlib import Path
import joblib
import mlflow
from mlflow.tracking import MlflowClient

HERE=Path(__file__).resolve().parent
mlflow.set_tracking_uri(f"sqlite:///{(HERE/'mlflow.db').as_posix()}")
client=MlflowClient()
exp=client.get_experiment_by_name("Olist Delivery Risk — Module 4")
runs=client.search_runs([exp.experiment_id],max_results=20,order_by=["attributes.start_time DESC"])
if not runs:
    raise RuntimeError("No actual training run found to complete.")
run=runs[0]
model=joblib.load(HERE/"model_artifacts"/"delivery_risk_model.joblib")
with mlflow.start_run(run_id=run.info.run_id):
    info=mlflow.sklearn.log_model(model,name="model",registered_model_name="OlistDeliveryRisk",skops_trusted_types=["numpy.dtype"])
    version=getattr(info,"registered_model_version",None)
    if version is None:
        versions=client.search_model_versions("name='OlistDeliveryRisk'")
        version=max((v.version for v in versions),key=int) if versions else None
    if version is not None:
        try: client.transition_model_version_stage(name="OlistDeliveryRisk",version=str(version),stage="Staging",archive_existing_versions=True)
        except Exception as exc: print(f"Version registered; stage transition unavailable: {exc}")
    path=HERE/"reports"/"metrics.json"
    results=json.loads(path.read_text(encoding="utf-8"))
    results["mlflow"]={"tracking_uri":"SQLite backend in module4/mlflow.db; artifacts in module4/mlruns","experiment":"Olist Delivery Risk — Module 4","run_id":run.info.run_id,"registered_model":"OlistDeliveryRisk","model_version":version,"stage":"Staging" if version is not None else "Not recorded"}
    path.write_text(json.dumps(results,indent=2),encoding="utf-8")
    mlflow.log_artifact(str(path)); mlflow.log_artifact(str(HERE/"reports"/"fairness_metrics.csv")); mlflow.log_artifact(str(HERE/"reports"/"sensitivity_analysis.csv")); mlflow.log_artifacts(str(HERE/"reports"/"figures"),artifact_path="figures")
print(json.dumps(results["mlflow"],indent=2))
