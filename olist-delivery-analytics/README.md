# Olist Delivery Analytics

Course project: analyze delivery performance and customer experience using the public Olist Brazilian E-Commerce dataset. This pipeline implements the Module 1 vision and Module 2 architecture, with an aggregate-only operational feed for human investigation.

**GitHub project folder:** https://github.com/snnaim-svg/Nexford/tree/main/olist-delivery-analytics

![Sprint planning board](reports/project_board.png)

## Run
1. Create a Python 3.12 environment and install `requirements.txt`.
2. Obtain the dataset from the Kaggle source in `data/manifests/source_manifest.yml`; place CSVs in `data/raw/`. Do not commit or redistribute raw data.
3. Run the Prefect flow with `python -m orchestration.flow`. For environments without a local Prefect API service, set `PREFECT_LOCAL_TASKS=1` to execute task bodies sequentially.
4. Run checks with `pytest -q`.

## Data and privacy
The pipeline writes an aggregate feed under `data/processed/`, a Great Expectations result summary and regional representation diagnostics under `reports/`, and a metadata-only JSONL privacy audit log. Generated data and logs are excluded from Git.

## Structure
`src/` contains ingestion, preparation, KPIs, privacy controls, validation and bias diagnostics. `orchestration/flow.py` defines the Prefect DAG. `tests/` contains unit tests. `docs/` contains the data dictionary, governance and ethical project records. `deliverables/` contains the course presentation.

## Ethics and limitations
Only required columns are read. Review free text, identifiers, city/postal fields and precise geolocation are excluded. Final outputs are aggregated and cells under 100 orders are suppressed. The public dataset has no protected attributes; region-based representation and review-coverage checks are operational diagnostics and cannot establish demographic fairness. Outputs support human investigation only, never automated adverse decisions.
