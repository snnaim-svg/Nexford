# Model Card: Olist Late Delivery Risk

## Model details

- **Version:** 1.0 course prototype; selected model: Logistic Regression.
- **Owner:** Sandra Nassif, BAN6800 capstone.
- **Problem:** estimate whether a delivered order will arrive after its checkout promise.
- **Unit:** one order; **prediction moment:** checkout; **target:** actual delivery timestamp later than estimated timestamp.
- **Intended use:** analyst prioritization for service investigation only.
- **Prohibited use:** seller sanctions, customer compensation or eligibility, changed customer treatment, delivery guarantees, or unattended operational actions.

## Data and evaluation

Olist public historical e-commerce tables (2016–2018); 96,470 eligible labeled orders. A chronological 80/20 split reserves the later period for testing. Predictors cover planned lead time, item/basket values, category, broad customer/seller region, and purchase calendar fields. Identifiers, review data, and post-purchase fields are excluded. Missing numeric/categorical values are imputed within the training pipeline; categoricals are one-hot encoded.

| Metric | Hold-out result |
|---|---:|
| accuracy | 0.902 |
| precision | 0.082 |
| recall | 0.083 |
| f1 | 0.083 |
| roc_auc | 0.707 |
| pr_auc | 0.093 |

The majority baseline F1 is 0.000; the test confusion matrix at 0.50 is `[[17320, 953], [936, 85]]`. Recall and precision at the reported threshold are too low for an early-warning pilot; the model is **not approved for operational use**. Metrics are historical and are not a deployment guarantee.

## Fairness and explainability

The data contain no protected demographic attributes. Macroregion comparisons are operational diagnostics only: regional demographic-parity difference 0.465; regional disparate-impact ratio 0.019; regional equalized-odds gap 0.633. These are not demographic fairness findings. SHAP global and local outputs are in `reports/figures/`; they describe model behavior, not causal effects. Sensitivity and counterfactual perturbations are scenario analyses, not customer recourse.

## Limitations and monitoring

Historical data, omitted carrier/route/weather/capacity features, possible proxy effects from geography, label maturity requirements, and temporal drift limit validity. Before a real pilot: use fresh time-based data, calibrate risk, review false negatives and false positives with operations, obtain approved protected-group evidence, evaluate privacy and lawful use, define human accountability, and approve rollback criteria. Monitor matured-order performance, calibration, prevalence, input missingness, category and region mix, and drift.
