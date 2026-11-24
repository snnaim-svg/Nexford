import pandas as pd
from src.metrics import calculate_delivery_kpis
from src.prepare import state_region
from src.privacy import suppress_small_cells
from src.bias import representation_checks

def test_state_region_mapping():
    assert state_region("SP") == "Southeast"
    assert state_region("ZZ") == "Unknown"

def test_segment_metrics_and_suppression():
    orders = pd.DataFrame({"order_id":[str(i) for i in range(100)], "purchase_month":["2018-01"]*100,
        "customer_region":["Southeast"]*100,"seller_region":["South"]*100,"category":["books"]*100,
        "late":[1]*25+[0]*75,"delay_days":[2]*25+[-1]*75,"review_score":[5]*100,"low_review":[False]*100})
    out = calculate_delivery_kpis(orders)
    assert out.iloc[0].late_rate == .25
    assert len(suppress_small_cells(out, 100)) == 1
    assert len(suppress_small_cells(out, 101)) == 0

def test_representation_check_flags_review_coverage_gap():
    data = pd.DataFrame({"order_id":[str(i) for i in range(200)],
        "customer_region":["North"]*100+["South"]*100,
        "review_score":[None]*20+[5]*80+[5]*100})
    out = representation_checks(data)
    assert out.coverage_gap_pp_from_max.max() >= 19
    assert out.review_coverage_gap_over_10pp.any()
