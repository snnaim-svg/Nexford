import great_expectations as gx

def validate_metrics(metrics):
    """Great Expectations dataframe validation; raises on any failed condition."""
    context = gx.get_context(mode="ephemeral")
    ds = context.data_sources.add_pandas(name="olist_pipeline")
    asset = ds.add_dataframe_asset(name="aggregated_delivery_metrics")
    batch_def = asset.add_batch_definition_whole_dataframe("all_metrics")
    suite = gx.ExpectationSuite(name="olist_delivery_quality")
    suite.add_expectation(gx.expectations.ExpectTableRowCountToBeBetween(min_value=1))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="late_rate", min_value=0, max_value=1))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="order_count", min_value=100))
    suite = context.suites.add(suite)
    validation = context.validation_definitions.add(
        gx.ValidationDefinition(name="olist_metrics_validation", data=batch_def, suite=suite))
    result = validation.run(batch_parameters={"dataframe": metrics})
    checks_passed = metrics.order_count.ge(100).all() and metrics.late_rate.between(0,1).all() and metrics.review_coverage.between(0,1).all()
    required = {"purchase_month","customer_region","seller_region","category","order_count","late_rate","mean_delay_days","low_review_share","review_coverage"}
    pii = {"order_id","customer_id","seller_id","zip_code","comment"}
    schema_ok = required.issubset(metrics.columns) and not (pii & set(metrics.columns))
    grain_ok = not metrics.duplicated(["purchase_month","customer_region","seller_region","category"]).any()
    expectation_results = [{"expectation": r.expectation_config.type, "success": bool(r.success)} for r in result.results]
    return {"gx_success": bool(result.success), "expectations": expectation_results, "thresholds_pass": bool(checks_passed), "schema_pass": bool(schema_ok), "grain_pass": bool(grain_ok), "rows": int(len(metrics)), "columns": list(metrics.columns)}
