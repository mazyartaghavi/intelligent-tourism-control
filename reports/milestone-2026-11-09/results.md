# Generated Results

Synthetic evaluation; all costs use declared scenario coefficients.

## Fixed cases

| Case | LP objective | Proportional objective | LP unmet | Proportional unmet | Comparable |
|---|---:|---:|---:|---:|:---:|
| uniform_priorities | 60.000 | 60.000 | 60.000 | 60.000 | yes |
| weighted_priorities | 215.000 | 309.615 | 60.000 | 60.000 | yes |
| expensive_service | 76.000 | 96.000 | 70.000 | 50.000 | yes |
| temporal_coupling | 15.500 | 19.500 | 8.000 | 0.000 | yes |
| closed_location | 32.000 | 32.000 | 10.000 | 10.000 | yes |
| zero_demand | 0.000 | 0.000 | 0.000 | 0.000 | yes |
| zero_budget | 30.000 | 30.000 | 30.000 | 30.000 | yes |
| ramp_transition | 90.000 | 70.000 | 90.000 | 70.000 | no: heuristic violates ramp limit |

The ramp case reports both outputs for diagnosis; it is excluded from performance claims.

## Forecast-error stress test

Positive saving means lower realized objective for LP.

| Log-noise sigma | Forecast MAE | LP objective | Proportional objective | Paired saving (95% CI) | Aggregate saving | LP worse |
|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.000 | 1801.039 | 2174.560 | 373.521 [339.608, 407.165] | 17.18% | 0/50 |
| 0.15 | 4.783 | 1855.019 | 2173.212 | 318.193 [286.728, 350.401] | 14.64% | 0/50 |
| 0.35 | 11.107 | 1946.662 | 2197.479 | 250.818 [220.926, 281.624] | 11.41% | 0/50 |
| 0.70 | 21.722 | 2173.103 | 2316.813 | 143.710 [119.412, 168.641] | 6.20% | 1/50 |

Intervals resample whole paired trajectories, separately at each noise level. They are not simultaneous intervals or field-performance guarantees.

## Numerical validation

- Successful LP solves: 218.
- Allocations feasible at 1e-7 tolerance: 218.
- Maximum constraint violation: 1.42e-14.
- Maximum absolute primal-dual gap: 2.73e-12.
- Unexpected solve failures: 0 (the runner aborts if one occurs).
