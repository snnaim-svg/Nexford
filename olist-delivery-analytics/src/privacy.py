import pandas as pd

def anonymize_aggregate(orders, min_cell=100):
    """Publish aggregate KPIs only; no raw identifiers, precise locations, or review text."""
    out = orders.copy()
    out["customer_region"] = out.customer_region.where(out.customer_region.isin(["North","Northeast","Central-West","Southeast","South"]), "Unknown")
    return out

def suppress_small_cells(metrics, min_cell=100):
    """Keep large segments and pool smaller cells so the aggregate reconciles."""
    large = metrics.loc[metrics.order_count >= min_cell].copy()
    large["aggregation_level"] = "Detail segment"
    small = metrics.loc[metrics.order_count < min_cell]
    if small.empty:
        return large.reset_index(drop=True)
    n = int(small.order_count.sum())
    review_n = small.order_count * small.review_coverage
    pooled = {
        "purchase_month": "Pooled period", "customer_region": "Pooled small cells",
        "seller_region": "Pooled", "category": "Pooled", "order_count": n,
        "late_rate": (small.late_rate * small.order_count).sum() / n,
        "mean_delay_days": (small.mean_delay_days * small.order_count).sum() / n,
        "low_review_share": (small.low_review_share * review_n).sum() / review_n.sum() if review_n.sum() else float("nan"),
        "review_coverage": review_n.sum() / n, "aggregation_level": "Pooled small cells",
    }
    return pd.concat([large, pd.DataFrame([pooled])], ignore_index=True)
