from pathlib import Path
import json
from prefect import flow, task
from src.ingest import load_sources
from src.prepare import prepare_orders
from src.metrics import calculate_delivery_kpis
from src.privacy import anonymize_aggregate, suppress_small_cells
from src.validate import validate_metrics
from src.audit import log_event
from src.bias import representation_checks

@task(retries=2, retry_delay_seconds=5)
def ingest():
    tables = load_sources(); log_event("ingest_sources", "data/raw/olist_orders_dataset.csv", len(tables["orders"])); return tables
@task
def prepare(tables):
    orders = prepare_orders(tables); log_event("prepare_joined_orders", rows=len(orders)); return anonymize_aggregate(orders)
@task
def aggregate(orders):
    return suppress_small_cells(calculate_delivery_kpis(orders))
@task
def validate(metrics):
    result = validate_metrics(metrics)
    Path("reports").mkdir(exist_ok=True)
    Path("reports/ge_validation_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    log_event("validate_aggregate", rows=len(metrics), status="success" if all(result[k] for k in ["gx_success","thresholds_pass","schema_pass","grain_pass"]) else "failed")
    if not all(result[k] for k in ["gx_success","thresholds_pass","schema_pass","grain_pass"]): raise ValueError(result)
    return result
@task
def bias_review(orders):
    report = representation_checks(orders)
    Path("reports").mkdir(exist_ok=True)
    report.to_csv("reports/representation_bias_checks.csv", index=False)
    log_event("representation_coverage_check", rows=len(report))
    return report
@task
def publish(metrics):
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    out = Path("data/processed/delivery_segments.csv"); metrics.to_csv(out, index=False)
    log_event("write_aggregate_feed", out, len(metrics)); return str(out)
@flow(name="olist-delivery-analytics-etl", log_prints=True)
def pipeline():
    tables = ingest(); orders = prepare(tables); metrics = aggregate(orders); validate(metrics); bias_review(orders); return publish(metrics)
def run_local():
    """Execute task bodies directly where a local Prefect API server is unavailable."""
    tables = ingest.fn(); orders = prepare.fn(tables); metrics = aggregate.fn(orders)
    validate.fn(metrics); bias_review.fn(orders); return publish.fn(metrics)

if __name__ == "__main__":
    import os
    run_local() if os.getenv("PREFECT_LOCAL_TASKS") == "1" else pipeline()
