# Allocation policy sensitivity — 22 November 2026

This follow-up tests whether the near-tie between receding-horizon optimization and the fixed priority rule in [Milestone 02](../sequential-control-stage-e/README.md) persists under different planning assumptions.

All three policies used the same daily seasonal-mean forecasts and scheduled capacities on 16 fresh synthetic trajectories, each 42 days long. These seeds were separate from the earlier forecasting, allocation, and learning comparisons. Each setting changes one assumption at a time from the published baseline. The [study configuration](../../configs/control/policy-sensitivity.json) declares the changes. Policies are compared within each setting under its own objective weights and budget.

| Setting | LP minus priority cost | 95% paired bootstrap interval | LP minus priority served |
|---|---:|---:|---:|
| Baseline | -6.20 | [-8.03, -4.59] | -51.36 |
| Equal priorities | -462.38 | [-500.29, -425.40] | +97.00 |
| Reversed priorities | 0.00 | [0.00, 0.00] | -44.62 |
| Low adjustment cost | 0.00 | [0.00, 0.00] | 0.00 |
| High adjustment cost | -116.44 | [-134.50, -100.10] | -96.06 |
| Tight budget | -1.73 | [-2.42, -1.14] | -17.26 |
| Loose budget | -30.26 | [-37.35, -23.67] | -33.61 |

Differences are means over whole trajectories. Negative cost differences favor the LP. Displayed zeros are rounded. The LP had the lowest mean cost or tied in each setting. Equal priorities widened the gap with the fixed priority rule, but proportional allocation came within 20.84 cost units of the LP and served 21.27 more requests on average. With high adjustment cost, the LP saved weighted cost while serving fewer requests than the priority rule. A cost tie under reversed priorities also concealed a service difference.

All 336 policy trajectories passed the feasibility checks. The largest residual was about 2.84e-14 service units against a tolerance of 1e-7. The bootstrap resamples whole paired trajectories within each setting. This study covers the stated synthetic generator and one-at-a-time changes. It leaves interactions between assumptions and empirical performance open.

## Reproduce

From the repository root with the existing Python 3.13 environment and locked dependencies:

```sh
python scripts/evaluation/run_policy_sensitivity.py --output reports/local-reproduction/policy-sensitivity
python -m unittest discover -s tests/unit
```

[Results and paired effects](results.json) · [Per-trajectory metrics](trajectories.csv) · [Recorded planning times](runtime.csv)
