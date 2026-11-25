# Fairness Metrics Report

## Scope and limitation

This analysis uses customer macroregion only as a service-operation slice. The Olist files do not include age, gender, race, or other protected demographic attributes. Accordingly, the statistics below do not measure protected-class fairness and must not be described as such. Fairness metrics express different policy assumptions; demographic parity compares prediction rates, whereas equalized odds compares true-positive and false-positive rates (Fairlearn, n.d.).

## Test-slice diagnostics

- Regional demographic-parity difference: **0.465**.
- Regional disparate-impact ratio (minimum / maximum positive-prediction rate): **0.019**.
- Regional equalized-odds gap (largest TPR or FPR range): **0.633**.
- Per-region order counts and error rates: `../reports/fairness_metrics.csv`.

## Interpretation and decision

Regional differences can reflect route distance, marketplace coverage, infrastructure, historical service patterns, or model error. The public data cannot distinguish these explanations or support conclusions about protected populations. No algorithmic mitigation is applied because there is no validated protected-group variable and threshold intervention could shift errors without addressing the underlying service conditions. The prototype remains advisory and may not trigger adverse decisions. Before deployment, obtain governance approval for lawful, representative subgroup data; report uncertainty and adequate sample sizes; investigate false positives and false negatives by subgroup; assess effects of candidate mitigations; and document a human-accountable release decision.
