# Stage B — Forecast-to-allocation integration

The existing allocator now accepts a complete, dated forecast batch. The [adapter](../../src/tourism_control/optimization/forecast_allocation.py) checks scenario, origin, forecast method, horizon, and site labels, then constructs the optimizer's day-by-site demand matrix. Each synthetic request can consume one service-capacity unit. The shared budget is a daily resource limit set at 65% of the sum of the scheduled local service ceilings.

## Experimental design

Reuse the 12 synthetic trajectories and 42-day test split from [Stage A](../forecasting-stage-a/README.md). At each weekly origin, each policy plans the next seven days using completed history. The prior week's final assigned capacity becomes the next week's initial allocation. The proportional baseline uses the validation-selected seasonal mean. Three optimizer variants use persistence, seasonal naive, and seasonal mean. An exact-demand oracle plans the full test trajectory using future realized demand as a lower-bound reference.

Deployable plans enforce their own forecast ceilings, site ceilings, and shared budgets. Realized service is the lesser of planned allocation and actual requests. The realized objective adds priority-weighted unmet demand, operating charges on all committed capacity, and absolute allocation-change charges. All policies start at zero. There are no hard ramp limits in this comparison. In this configuration, operating cost per unit exceeds twice the change cost per unit. With known demand, removing excess allocations reduces operating cost by more than the maximum increase in adjacent change costs, so limiting the oracle to actual demand preserves a global lower bound.

## Results

Means per 42-day trajectory. Lower objective is better.

| Policy | Forecast MAE | Realized objective | Served | Unmet | Change cost |
|---|---:|---:|---:|---:|---:|
| Proportional, seasonal mean | 7.35 | 12,163.29 | 5,238.90 | 2,480.51 | 160.55 |
| Optimizer, persistence | 14.55 | 10,153.35 | 4,668.43 | 3,050.98 | 108.35 |
| Optimizer, seasonal naive | 8.78 | 10,469.85 | 4,969.59 | 2,749.83 | 330.76 |
| Optimizer, seasonal mean | 7.35 | 10,268.10 | 5,072.98 | 2,646.44 | 307.27 |
| Full-test exact-demand oracle | — | 9,505.15 | 5,177.18 | 2,542.23 | 329.27 |

The seasonal-mean optimizer reduced the mean objective by 15.6% versus the proportional policy using the same forecasts. The paired difference was 1,895.20 objective units in favor of optimization (scenario bootstrap 95% interval 1,783.63 to 1,993.78), while total service fell. Persistence had worse forecast error and lower service than seasonal mean. With the optimizer it achieved a lower mean weighted objective by 114.75 units (paired 95% interval 44.52 to 178.77), with lower change and operating costs. The trade-off depends on the selected cost weights. The bootstrap resamples whole trajectories. Each policy passed the numerical feasibility checks across all 12 scenarios.

## Reproduce

```sh
python -m pip install -r requirements-milestone-lock.txt
python scripts/evaluation/run_forecast_allocation.py --output reports/local-reproduction/forecast-allocation
python -m unittest discover -s tests/unit -p test_forecast_allocation.py -v
```

- [Parameters, metrics, paired effects and feasibility diagnostics](results.json)
- [Per-trajectory metrics](trajectories.csv)
- [Measured planning times](runtime.csv), which vary by environment

The simulated service model treats unmet requests as lost for that day and models adjustment through previous assignments. It provides no field-performance evidence. The subsequent daily experiment uses a separate protocol and new scenarios.
