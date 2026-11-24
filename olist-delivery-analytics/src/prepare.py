import pandas as pd

def prepare_orders(tables):
    o = tables["orders"].drop_duplicates("order_id").copy()
    c = tables["customers"].drop_duplicates("customer_id")
    for col in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]:
        o[col] = pd.to_datetime(o[col], errors="coerce", utc=True)
    o = o.merge(c, on="customer_id", how="left", validate="many_to_one")
    r = tables["reviews"].dropna(subset=["review_score"]).groupby("order_id", as_index=False).review_score.mean()
    o = o.merge(r, on="order_id", how="left", validate="one_to_one")
    items = tables["items"].drop_duplicates()
    items = items.merge(tables["products"].drop_duplicates("product_id"), on="product_id", how="left", validate="many_to_one")
    items = items.merge(tables["categories"].drop_duplicates("product_category_name"), on="product_category_name", how="left", validate="many_to_one")
    items = items.merge(tables["sellers"].drop_duplicates("seller_id"), on="seller_id", how="left", validate="many_to_one")
    item_agg = items.groupby("order_id", as_index=False).agg(
        category=("product_category_name_english", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else "Unknown"),
        seller_state=("seller_state", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else "Unknown"))
    o = o.merge(item_agg, on="order_id", how="left", validate="one_to_one")
    o = o[o.order_status.eq("delivered") & o.order_delivered_customer_date.notna() & o.order_estimated_delivery_date.notna()].copy()
    o["delay_days"] = (o.order_delivered_customer_date - o.order_estimated_delivery_date).dt.total_seconds() / 86400
    o["late"] = (o.delay_days > 0).astype("int8")
    o["low_review"] = (o.review_score <= 2).where(o.review_score.notna())
    o["purchase_month"] = o.order_purchase_timestamp.dt.strftime("%Y-%m")
    o["customer_region"] = o.customer_state.map(state_region).fillna("Unknown")
    o["seller_region"] = o.seller_state.map(state_region).fillna("Unknown")
    return o[["order_id", "purchase_month", "category", "customer_region", "seller_region", "delay_days", "late", "review_score", "low_review"]]

def state_region(state):
    groups = {"North": "AC AM AP PA RO RR TO", "Northeast": "AL BA CE MA PB PE PI RN SE", "Central-West": "DF GO MT MS", "Southeast": "ES MG RJ SP", "South": "PR RS SC"}
    return next((region for region, states in groups.items() if state in states.split()), "Unknown")
