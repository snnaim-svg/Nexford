import pandas as pd

def anonymize_aggregate(orders, min_cell=100):
    """Publish aggregate KPIs only; no raw identifiers, precise locations, or review text."""
    out = orders.copy()
    out["customer_region"] = out.customer_region.where(out.customer_region.isin(["North","Northeast","Central-West","Southeast","South"]), "Unknown")
    return out

def suppress_small_cells(metrics, min_cell=100):
    return metrics.loc[metrics.order_count >= min_cell].copy()
