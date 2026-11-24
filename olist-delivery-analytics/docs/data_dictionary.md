# Olist pipeline data dictionary

## Source and terms
Source: Olist Brazilian E-Commerce Public Dataset, Kaggle (Olist, 2018), roughly 100k orders from 2016–2018; CSV; one-time historical snapshot, not a live feed. License shown by Kaggle: CC BY-NC-SA 4.0. Use for this non-commercial educational project with attribution; raw data are local and excluded from GitHub. Do not redistribute source files.

## Inputs and lineage
`olist_orders_dataset.csv` (order grain; `order_id` PK, `customer_id` FK; purchase, delivered, estimated timestamps and order status) is joined to `olist_customers_dataset.csv` (customer key and state only). `olist_order_reviews_dataset.csv` contributes numeric score only; review text is excluded. Items join products, sellers, and category translation through their IDs; seller/customer state is mapped to Brazil macroregion. Payment, geolocation precision, customer city/postal code, identifiers, and free text are excluded.

```text
orders ─┬─ customers (state → macroregion)
        ├─ reviews (numeric score only)
        └─ items → products → category translation
                    └→ sellers (state → macroregion)
              ↓ validated order-grain table (local interim only)
       month × customer region × seller region × category KPIs
              ↓ ≥100-order cell suppression → CSV aggregate feed
```

The final feed contains month, broad regions, category, aggregation level, order count, late rate, mean delay days, low-review share, and review coverage. Segments under 100 orders are pooled into one clearly labeled residual aggregate, preserving total eligible-order reconciliation without exposing small cells. Frequency is a one-time batch over historical data; rerunning is idempotent at the output level. No row-level identifiers or comment text are published.

## Data quality and transformations
Deduplicate primary keys; enforce many-to-one joins; parse timestamps in UTC; retain delivered orders with actual and estimated delivery dates; define late as actual delivery after estimate; define low review as score ≤2. Missing reviews remain missing and are excluded from the low-review denominator; report review coverage. Unknown category/state are retained as “Unknown”. Aggregate and suppress segments below 100 orders. Public dataset lacks demographics, so regional representation checks are operational coverage checks, not protected-group fairness tests.
