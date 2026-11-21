# Stage A — Reproducible Demand Forecasting

**Verified 21 November 2026.** Three point forecast baselines were evaluated on 12 seeded synthetic demand trajectories at three locations. The seasonal mean selected on validation also produced the lowest held-out MAE and RMSE.

| Baseline | Validation MAE | Test MAE | Test RMSE |
|---|---:|---:|---:|
| Persistence | 14.90 | 14.55 | 17.80 |
| Seasonal naive | 8.46 | 8.78 | 11.16 |
| Three-week seasonal mean | 6.92 | 7.35 | 9.39 |

Errors are in requested service volumes per daily period. Test MAE for the seasonal mean was about 16% lower than for seasonal naive, and its test MAE was lower in all 12 scenarios. On the 552 test site-days where requests exceeded the synthetic local service ceiling, test MAE was 7.95 for seasonal mean, 8.23 for persistence, and 9.27 for seasonal naive. This subgroup uses realized demand for diagnosis after forecasting.

## Data and timing

The [versioned configuration](../../configs/forecasting/stage-a.json) defines 140 days and three locations per scenario. Daily requested service is a nonnegative synthetic count before any capacity limit is applied. It represents a flow during a UTC day. Concurrent occupancy would require separate arrival, departure, and service-duration information. Stage B may use divisible capacity units at the same daily frequency, with one unit able to serve one request in this synthetic setting.

The [generator](../../src/tourism_control/forecasting/experiment.py) adds a site-specific baseline, a linear trend, site-scaled weekday seasonality, a shared autocorrelated disturbance, and independent Gaussian site noise. It adds signed shocks on seeded dates with half their effect carried into the next day. Values are rounded and clipped at zero. Weekend service ceilings are lower than weekday ceilings, creating variation in demand relative to service capacity. Ceilings, shock schedules, and future simulated outcomes are unavailable to the baseline models.

The [forecast interface](../../src/tourism_control/forecasting/baselines.py) identifies scenarios, sites, and calendar dates. Each history row represents the UTC day starting at its date. At midnight UTC on the origin date, only earlier completed days are visible. Horizon 1 predicts demand during the origin day. Horizon 7 predicts demand six calendar days later. Each forecast point carries its scenario, location, origin, target date, horizon, method, nonnegative prediction, and an optional interval. All three baselines leave the interval empty.

## Methods and evaluation

Let $Y_{i,t}$ be requests at site $i$ on UTC day $t$. At origin $t$, for horizon $h$, the target is $Y_{i,t+h-1}$. Let $r=(h-1)\bmod 7$.

- Persistence uses $Y_{i,t-1}$.
- Seasonal naive uses $Y_{i,t-7+r}$.
- Seasonal mean averages $Y_{i,t-7+r}$, $Y_{i,t-14+r}$, and $Y_{i,t-21+r}$.

Each scenario uses 70 initial history days, 28 validation days, and 42 test days in that order. Origins advance by seven days. Each seven-day batch is issued before any of its outcomes are used. After outcomes are available, they enter the history for the next origin. The baselines have fixed formulas. Method selection uses pooled validation MAE, with alphabetical order breaking an exact tie. The test comparison reports all prespecified methods on identical site-days. See the [evaluation protocol](../../docs/experiments/evaluation-protocol.md#3-forecasting-metrics) for error definitions.

There are 1,008 validation site-days and 1,512 test site-days per baseline. Site-days within a trajectory share temporal and spatial dependencies. The per-scenario table preserves the 12 distinct replications for later paired analysis. Performance reflects this synthetic generator, which includes weekly seasonality. These experiments establish point forecast behavior under the specified scenarios. They leave interval calibration, empirical tourism accuracy, and the downstream effect on allocation for separate evaluation.

## Reproduce

The forecast experiment uses the Python standard library and was verified with Python 3.13.2. From the repository root, choose a new output directory:

```sh
python scripts/evaluation/run_forecasting.py --config configs/forecasting/stage-a.json --output reports/local-reproduction/forecasting-stage-a
python -m unittest discover -s tests/unit -p test_forecasting.py -v
```

All 30 repository unit tests passed in the existing milestone environment, including five new forecasting tests. A second run reproduced all three result files byte for byte. The runner resolves its default configuration from the repository and rejects an existing output directory.

- [Summary and configuration](summary.json)
- [Metrics by split, horizon, and service pressure](metrics.csv)
- [Metrics by scenario and split](scenario_metrics.csv)

The next stage is to feed forecast batches into the constrained allocator and evaluate decisions against realized demand, with separate deployable baselines and an exact-demand oracle.
