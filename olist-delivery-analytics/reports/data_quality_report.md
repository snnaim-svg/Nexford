# Pipeline run quality summary

Run date: 2026-11-24  
Source: Olist Brazilian E-Commerce Public Dataset, Kaggle (historical 2016–2018 CSV snapshot).

## Reconciliation

- Source orders loaded: **99,441**.
- Delivered orders with both actual and estimated delivery dates: **96,470**.
- Output rows: **201**, including 200 detailed cells with at least 100 orders and one pooled residual row.
- Published order count: **96,470**, exactly matching the eligible input population.
- Detailed cells represent **39,223 orders (40.7%)**. The residual pool represents **57,247 orders (59.3%)**.

The residual row preserves totals but does not support month, region, seller-region, or category comparisons. Use it only in overall summaries. Segment comparisons cover the detailed portion.

## Validation results

All three Great Expectations checks passed: non-empty output, late-rate bounds [0, 1], and minimum aggregate cell count of 100. Project checks also passed for the expected schema, identifier exclusion, unique composite grain, and rate bounds. Three unit tests passed.

## Coverage and limitations

Numeric review coverage ranged from 99.05% to 99.51% across five broad Brazil regions, a maximum gap of 0.46 percentage points. This checks operational data representation only. The dataset has no protected-class attributes and cannot support demographic fairness claims. The dataset is historical and does not represent a live operation.

## Observed aggregate KPIs

Across all eligible orders, weighted late rate was **8.11%**; mean delivery was **11.18 days before the estimate**; **12.77%** of orders with numeric reviews had an average score of 2 or lower; review coverage was **99.33%**. These are descriptive measures, not causal findings.
