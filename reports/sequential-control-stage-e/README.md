# Milestone 02 — Forecasting, allocation, and sequential control

**Verified 21 November 2026.** This milestone links daily demand forecasts, capacity allocation, and a sequential policy experiment. It uses seeded synthetic data and the existing linear allocator.

| Stage | Verified output | Commit |
|---|---|---|
| A | [Chronological forecasting benchmark](../forecasting-stage-a/README.md) | `a434cd5` |
| B | [Forecast-to-allocation benchmark](../forecast-allocation-stage-b/README.md) | `09dda61` |
| C | [Daily environment, constraints, and reward](../../docs/methodology/daily-capacity-control.md) | `a96d461` |
| D | [Tabular policy and training algorithm](../../docs/methodology/tabular-allocation-policy.md) | `7207e9d` |
| E | [Paired daily comparison and archived results](results.json) | Commit containing this report |

Stage A selected a three-week seasonal mean on validation. Its held-out MAE was 7.35 requests per site-day versus 8.78 for seasonal naive and 14.55 for persistence. In Stage B, the optimizer using the seasonal mean lowered weighted cost by 15.6% against proportional allocation using the same forecasts. Persistence had worse accuracy and a lower weighted cost than seasonal mean when used by the optimizer. Its allocations changed less and served fewer requests.

## Daily comparison

The three locations use the same demand generator and objective as Stage B. Each deployable policy receives up to seven days of seasonal-mean forecasts, scheduled capacity, and its own previous commitment. It submits the current day's allocation before demand becomes available. The receding-horizon LP replans daily, executes the first allocation in its plan, and carries that commitment forward. The proportional rule uses the first forecast day. Four learned policies select from the same four feasible candidates with the published discretization of the public decision information.

The Q policies used the same 48 training scenarios in shuffled order, with three passes per learning seed and 6,048 transitions per fit. Another 16 scenarios selected the best fixed candidate, priority-first. All methods were evaluated on the same 16 additional scenarios, each lasting 42 days. All three scenario partitions are disjoint from one another and from Stage A and B. Optimization with full realized demand is a separate perfect-information reference. Scoring uses undiscounted realized cost for all methods. Discounting at 0.97 is used only in training.

| Policy | Weighted cost ↓ | Served ↑ | Unmet ↓ | Weighted unmet ↓ | Adjustment cost ↓ |
|---|---:|---:|---:|---:|---:|
| Proportional | 12,624.00 | 5,253.81 | 2,625.25 | 7,936.33 | 156.44 |
| Priority-first, validation-selected fixed rule | 10,556.26 | 5,141.37 | 2,737.69 | 5,780.33 | 324.00 |
| Receding-horizon LP | 10,549.00 | 5,102.76 | 2,776.31 | 5,838.25 | 295.48 |
| Q-learning, mean over four fits | 11,407.11 | 5,197.91 | 2,681.16 | 6,584.14 | 339.85 |
| Full-test exact-demand oracle | 9,792.40 | 5,205.05 | 2,674.01 | 5,116.61 | 312.53 |

Values are means per test trajectory. Proportional allocation served the most requests among the evaluated policies, while its weighted unmet demand was highest. The Q policy cut weighted cost by 9.6% versus proportional and cost 8.1% more than the receding-horizon LP. Priority-first was within 0.07% of the LP on mean weighted cost. Their service totals and changes differed.

| Paired difference in realized weighted cost | Mean | Scenario SD | 95% scenario bootstrap interval |
|---|---:|---:|---:|
| Q-learning minus proportional | -1,216.89 | 160.60 | [-1,293.76, -1,142.21] |
| Q-learning minus priority-first | 850.85 | 107.01 | [803.84, 905.55] |
| Q-learning minus receding-horizon LP | 858.10 | 106.72 | [811.87, 912.42] |

Q-learning differences average the four frozen fits within each scenario. The intervals use 2,000 bootstrap draws of whole scenarios, conditional on those four fits. The standard deviation of mean objective across the four fits was 327.13. All four training runs completed, and all 160 evaluation records passed planning feasibility checks. The largest recorded residual was about 2.84e-14 service units, below the 1e-7 tolerance. Each non-oracle record contains its objective gap to the oracle on the same trajectory.

This experiment provides no advantage for the tested learned policy over the simpler priority-first rule or the LP under the declared costs. Forecast error and decision quality diverged in Stage B. Follow-up experiments should prioritize sensitivity to objective weights and compare resource-allocation choices under empirically defensible demand scenarios before adding a larger RL model. Evaluation here covers one synthetic demand process and a finite action menu. The priority and capacity assumptions, use of point forecasts, and coarse policy state limit transfer to field operations.

## Reproduce the results

Use Python 3.13 with [locked dependencies](../../requirements-milestone-lock.txt). The run used the existing local environment. The four fits took roughly 0.5 seconds each, excluding forecast generation. The median trajectory-level planning time per daily decision was approximately 0.016 ms for proportional, 3.9 ms for the LP, and 0.040 ms for the first Q fit. These times are machine-specific and exclude precomputed forecasts.

```sh
python -m pip install -r requirements-milestone-lock.txt
python -m unittest discover -s tests/unit -v
python scripts/evaluation/run_daily_comparison.py --output reports/local-reproduction/daily-comparison
```

All 40 repository tests passed. A separate rerun reproduced the Stage E JSON and per-trajectory CSV byte for byte. The timings vary by environment. Stage B scientific outputs were also reproduced separately.

- [Results, configurations, fitted tables, uncertainty, and constraints](results.json)
- [Per-trajectory evaluation records](trajectories.csv)
- [Training and decision timings](runtime.csv)
