# Allocation Benchmark Contract — 9 November 2026

[Configuration](../../configs/optimization/milestone-benchmark.json) · [Runner](../../scripts/evaluation/run_milestone.py) · [Results](../../reports/milestone-2026-11-09/README.md).

This is a synthetic computational benchmark. Its design and configuration were set before the first reported run. It contains no empirical tourism dataset, fitted forecast model, or online policy. No parameter was selected to maximize the reported improvement.

## Questions and comparisons

1. Does the LP reproduce known analytical and enumerated optimal solutions and satisfy the stated constraints?
2. How do priorities, operating costs, and adjustment costs change allocations compared with a proportional rule?
3. How does forecast error change realized decision quality under a fixed synthetic distribution?

Both methods receive identical planning information and coefficient settings. The primary comparison is **proportional objective minus LP objective**; positive values favor LP. Report unweighted unmet demand and constraint violations alongside the objective. Timing is descriptive, not a performance claim: LP timings include validation, sparse model construction, and solving; heuristic timings cover allocation calculation.

## Fixed cases and sensitivity

Eight versioned cases cover uniform and weighted priorities, expensive service, temporal coupling, a closed location, zero demand, zero budget, and a change-limited transition. The first seven are compared on a common feasible set. The last demonstrates why an infeasible comparator cannot establish superiority: proportional allocation violates the change limit and is explicitly marked incomparable.

Budget sensitivity uses five budgets `[30, 60, 90, 120, 150]` for the weighted-priority example. Temporal sensitivity uses five adjustment penalties `[0, 0.25, 0.75, 2, 5]`. All ten pairs are retained. They are deterministic illustrations, not independent statistical samples.

## Forecast-error generation

Each seed from 1000 through 1049 generates one independent six-period, four-location trajectory. All four noise levels reuse that trajectory and its standard-normal noise array. Within a trajectory:

- Realized demand $y_{i,t}$ is sampled uniformly from the integers 20 through 60.
- Capacity $C_{i,t}$ is independently sampled uniformly from 15 through 55.
- $B_t=0.65\sum_i C_{i,t}$; this depends on known capacity, not realized demand.
- Each location's penalty is sampled uniformly from integers 1 through 7; its operating coefficient is uniform on $[0.2,1.0)$. These coefficients are constant over periods.
- Adjustment cost is 0.5 for every location; initial allocations are zero; change limits are disabled for the paired comparison.

Planning demand is a controlled perturbation:

$$
\hat d_{i,t}=y_{i,t}\exp(\sigma z_{i,t}-\sigma^2/2),\qquad
z_{i,t}\sim\mathcal N(0,1),\quad \sigma\in\{0,0.15,0.35,0.70\}.
$$

The multiplier has mean one under this synthetic construction. This is an error-injection experiment, not a trained forecasting method. The evaluator uses realized demand to generate forecasts for a controlled stress test; neither allocation method receives realized demand as an extra input. There is no train/test fitting claim. Actual future error distributions need empirical estimation.

Plans are evaluated without replanning:

$$
J_{\mathrm{real}}(x;y)=\sum_{i,t}\left[
w_{i,t}(y_{i,t}-x_{i,t})_+ + c_{i,t}x_{i,t}
+\kappa_i|x_{i,t}-x_{i,t-1}|\right].
$$

Planned service can exceed realized demand; the unused portion still incurs cost. Resource feasibility is checked against the same capacity and budget. The LP is optimal for its planning problem, not necessarily for this realized objective. There is no claim of robust optimization or safe crowd admission.

```text
Algorithm 2: Paired forecast-error stress test
For each predeclared noise level sigma:
    For each of the 50 independent trajectory seeds:
        Generate realized demand, capacities, costs, and standard-normal noise.
        Construct perturbed planning demand; keep realized demand in the evaluator.
        Solve LP and compute proportional allocation with identical planning inputs.
        Validate both plans and record planning and realized objective components.
        Store every input, allocation, metric, and timing; stop on an unexpected failure.
    Form 50 paired differences: proportional realized objective minus LP objective.
    Bootstrap entire paired trajectories and report mean, interval, and loss count.
```

## Statistical reporting

At each noise level, report the mean paired difference and a percentile 95% bootstrap interval from 5,000 resamples of **whole trajectories**, using seed 7301. The six periods and four locations are not treated as independent replicates. The same seeds appear across noise levels, so there are 50 independent trajectories, not 200 independent trajectories. Intervals are pointwise and are not adjusted for multiple comparisons. No significance test or universal superiority claim is made.

Aggregate percentage saving is $100\sum_s(J_s^{\mathrm{prop}}-J_s^{\mathrm{LP}})/\sum_s J_s^{\mathrm{prop}}$, not the average of individual percentages. Report the number of trajectories where LP is worse. These intervals describe Monte Carlo variation under this generator; they do not quantify uncertainty about actual tourism conditions.

## Failure, verification, and reproducibility rules

The runner stops on any unexpected solve or numerical-validation failure. It never silently drops an unsuccessful seed. The infeasible-shutdown case is tested separately as an expected failure, not included in the 218 successful benchmark solves. Validation includes analytical priorities, temporal coupling, a small exhaustive integer-grid reference, and 50 independent fractional-knapsack reference instances.

The published artifact contains full inputs and outputs in JSON, flattened CSV metrics, a generated table and figure, pinned dependencies, environment/solver versions, and canonical text SHA-256 fingerprints. Runtime and solver bookkeeping can vary between runs; scientific results are compared with absolute tolerance `1e-7`. The verifier does not overwrite the reference results. Non-unique optimal allocations can also vary across solver builds; the validated environment is recorded rather than assuming all future versions are identical.

Remaining threats include the synthetic distribution, linear penalties, divisible resources, complete planning-horizon information, absence of fairness requirements, and missing queue/behavior dynamics. Historical replay, independently sourced data, measured forecast errors, and stakeholder-defined objectives are required before making practical performance claims.
