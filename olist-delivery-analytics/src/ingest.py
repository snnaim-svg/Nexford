from pathlib import Path
import pandas as pd

FILES = {
    "orders": "olist_orders_dataset.csv", "customers": "olist_customers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv", "items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv", "sellers": "olist_sellers_dataset.csv",
    "categories": "product_category_name_translation.csv",
}
USECOLS = {
    "orders": ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"],
    "customers": ["customer_id", "customer_state"],
    "reviews": ["order_id", "review_score"],
    "items": ["order_id", "product_id", "seller_id"],
    "products": ["product_id", "product_category_name"],
    "sellers": ["seller_id", "seller_state"],
    "categories": ["product_category_name", "product_category_name_english"],
}

def load_sources(data_dir="data/raw"):
    root = Path(data_dir)
    missing = [f for f in FILES.values() if not (root / f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing Olist source files: {missing}")
    return {k: pd.read_csv(root / FILES[k], usecols=USECOLS[k]) for k in FILES}
