# Multi-period Allocation: Model and Algorithm

Implemented and evaluated on **9 November 2026**. [Evidence report](../../reports/milestone-2026-11-09/README.md) · [Python implementation](../../src/tourism_control/optimization/linear.py) · [Tests](../../tests/unit/test_linear.py).

## Scope and units

Allocate a divisible service resource across locations and periods. All demand, capacity, budget, allocation, and change quantities use the same service unit. The budget is a resource quantity, not currency. Periods are abstract intervals; the benchmark assigns no physical duration. The model has no travel network, admission queue, occupancy dynamics, or integer visitors. It is a continuous planning model.

The research contribution here is a transparent model implementation, diagnostics, and reproducible comparison. The optimization algorithm is provided by the established SciPy/HiGHS library.

## Mathematical formulation

For locations $i=1,\ldots,n$ and periods $t=1,\ldots,T$, inputs are non-negative planning demand $d_{i,t}$, local capacity $C_{i,t}$, shared resource budget $B_t$, unmet-demand penalty $w_{i,t}$, operating cost $c_{i,t}$, adjustment cost $\kappa_i$, and initial allocation $x_{i,0}$. All coefficients are finite. Optional $\Delta_i\geq0$ limits changes.

Choose allocations $x$, unmet demand $u$, and adjustment auxiliaries $a$:

$$
\min_{x,u,a}\ J=\sum_{t=1}^{T}\sum_{i=1}^{n}
\left(w_{i,t}u_{i,t}+c_{i,t}x_{i,t}+\kappa_i a_{i,t}\right)
$$

subject to

$$
x_{i,t}+u_{i,t}=d_{i,t},\quad 0\leq x_{i,t}\leq C_{i,t},\quad
\sum_i x_{i,t}\leq B_t,\quad u_{i,t}\geq0,
$$

$$
a_{i,t}\geq x_{i,t}-x_{i,t-1},\quad
a_{i,t}\geq x_{i,t-1}-x_{i,t},\quad a_{i,t}\geq0.
$$

When enabled, add $a_{i,t}\leq\Delta_i$. For positive $\kappa_i$, minimization makes $a_{i,t}=|x_{i,t}-x_{i,t-1}|$. Zero-cost auxiliaries need not be tight, so reporting always recomputes actual absolute changes from $x$. Demand balance implies $x\leq d$; excess demand remains visible in $u$.

Without change limits, zero allocation gives a feasible solution. With limits, an initial allocation incompatible with a closure or reduced budget can make the problem infeasible. The software reports failure explicitly; it does not invent a feasible fallback. Increasing a budget cannot increase the optimal objective for otherwise identical feasible problems, because the feasible set expands. This does not imply that all service or fairness metrics improve.

## Sparse construction and solver

The implementation uses time-major arrays and a variable vector $z=(x,u,a)$ containing $3nT$ variables. It creates $nT$ demand-balance equalities and $T+2nT$ inequalities; capacity and optional adjustment limits are variable bounds. Constraint nonzeros grow linearly with $nT$. This is a construction-size statement, not a solver-runtime guarantee.

The call is `scipy.optimize.linprog(..., method="highs-ds")`, with presolve, a 30-second default time limit, and primal/dual solver tolerances of `1e-9`. SciPy's [official interface](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html) documents statuses and marginals. [Huangfu and Hall](../related-work/papers/2018-huangfu-dual-simplex.md) provide relevant solver background; this repository does not implement their parallel methods.

```text
Algorithm 1: Solve and validate a capacity plan
Input: d, C, B, w, c, kappa, x_initial, optional Delta
1. Reject missing fields, mismatched shapes, booleans, negative or nonfinite values.
2. Flatten variables in [period][location] order as z = (x, u, a).
3. Build sparse demand-balance, shared-budget, and absolute-change constraints.
4. Set nonnegative bounds; add capacity and optional change bounds.
5. Call the HiGHS dual-simplex solver through SciPy.
6. If termination is not optimal, return an explicit failure; do not score a plan.
7. Independently recompute capacity, demand, budget, and change residuals from x.
8. Reconstruct objective components and check primal-dual diagnostics.
9. Reject a numerically invalid result; otherwise return allocations and diagnostics.
```

## Numerical diagnostics

For the assembled minimization LP $\min c_z^Tz$ with $Az\leq b$, $Ez=d$, $0\leq z\leq U$, the solver returns inequality marginals $y\leq0$, equality marginals $\lambda$, and lower/upper bound marginals $\ell\geq0$, $v\leq0$. The code checks stationarity

$$
c_z-A^Ty-E^T\lambda-\ell-v\approx0
$$

and the dual objective $b^Ty+d^T\lambda+\sum_{j:U_j<\infty}U_jv_j$ against the primal objective. It also checks raw variable bounds, equalities, inequalities, multiplier signs, and the independently reconstructed physical objective. These are floating-point diagnostics, not an exact-arithmetic proof.

Absolute feasibility and stationarity tolerance is `1e-7`; objective reconstruction and primal-dual gap use `1e-7 * (1 + abs(objective))`. No allocation is rounded or repaired before validation. Optional budget marginals are local RHS sensitivities, not globally valid prices or causal effects.

## Comparator and interpretation

For each period, the existing heuristic computes $e_i=\min(d_i,C_i)$ and $x_i=e_i\min(1,B/\sum_j e_j)$, with zero allocation when the denominator is zero. It uses the same demand, capacities, and budget as the optimizer. It does not use costs or temporal coupling. Both methods are scored with the same objective and initial allocation.

With equal positive unmet-demand penalties and zero other costs, proportional allocation already maximizes served demand in the simple uncoupled model. The benchmark includes that equality case. With heterogeneous costs or priorities, the optimizer can improve the declared objective while increasing unweighted unmet demand. Repeated proportional allocation may violate change limits: such a pair is displayed as **incomparable**, not counted as a performance win.

## Input and output contract

[Example JSON](../../configs/optimization/milestone-example.json) is directly executable:

```sh
python src/tourism_control/optimization/linear.py configs/optimization/milestone-example.json
```

| Field | Shape | Meaning |
|---|---|---|
| `demand`, `capacity` | `[T][n]` | Planning demand and local service limit |
| `unmet_penalty`, `operating_cost` | `[T][n]` | Non-negative objective coefficients |
| `budget` | `[T]` | Shared resource limit per period |
| `adjustment_cost`, `initial_allocation` | `[n]` | Change penalties and preceding allocation |
| `max_change` | `[n]`, optional | Maximum absolute change per location and period |

Arrays must be rectangular, nonempty, numeric, finite, and non-negative. Numeric strings and booleans are rejected. Unknown fields are rejected to expose configuration errors. The output records solver termination, allocations, unmet demand, objective components, resource slacks, residuals, dual diagnostics, iterations, and elapsed time. A solver failure exits with status 1; malformed input exits with status 2.

`evaluate_allocation(problem, x, realized_demand=...)` separately scores a committed plan against realized demand. Served volume is $\min(x,y)$; unmet volume is $(y-x)_+$; unused service is $(x-y)_+$. Operating costs apply to the whole planned allocation. Feasibility remains defined by the planning contract. This scorer models unused service, not a queue, cancellations, or visitor behavior.
