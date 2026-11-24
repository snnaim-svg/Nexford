import pandas as pd

def representation_checks(orders):
    """Operational coverage diagnostics, not protected-class fairness metrics."""
    counts = orders.groupby("customer_region", dropna=False).order_id.nunique().rename("orders")
    coverage = orders.groupby("customer_region", dropna=False).review_score.apply(lambda s: s.notna().mean()).rename("review_coverage")
    out = pd.concat([counts, coverage], axis=1).reset_index()
    out["eligible_for_comparison"] = out.orders >= 100
    eligible = out[out.eligible_for_comparison]
    out["coverage_gap_pp_from_max"] = ((eligible.review_coverage.max() - out.review_coverage) * 100).round(1)
    out["review_coverage_gap_over_10pp"] = out.coverage_gap_pp_from_max > 10
    return out
