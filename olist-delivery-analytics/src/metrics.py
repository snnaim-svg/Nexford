import pandas as pd

def calculate_delivery_kpis(orders):
    x = orders.copy()
    x["late"] = x["late"].astype(float)
    x["low_review"] = x["low_review"].astype(float)
    out = x.groupby(["purchase_month", "customer_region", "seller_region", "category"], dropna=False).agg(
        order_count=("order_id", "nunique"), late_rate=("late", "mean"), mean_delay_days=("delay_days", "mean"),
        low_review_share=("low_review", "mean"), review_coverage=("review_score", lambda s: s.notna().mean())).reset_index()
    out["late_rate"] = out.late_rate.round(4)
    out["mean_delay_days"] = out.mean_delay_days.round(2)
    out["low_review_share"] = out.low_review_share.round(4)
    out["review_coverage"] = out.review_coverage.round(4)
    return out
