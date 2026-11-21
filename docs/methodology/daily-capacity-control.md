# Stage C — Daily capacity-control environment

One episode covers 42 UTC days. At the beginning of day $t$, all deployable policies receive the same dates, up to seven days of seasonal-mean demand forecasts, scheduled local and shared capacities, and their own previous commitment $x_{t-1}$. The prior commitment starts at zero. A forecast uses completed days only. Each policy commits one allocation $x_t$. Realized demand $d_t$ is revealed afterwards. Requests left unmet are lost for that day. The episode ends after the last day's outcome.

The hard bounds are $0\le x_{i,t}\le \min(\hat d_{i,t},C_{i,t})$ and $\sum_i x_{i,t}\le B_t$. No hard ramp constraint is active. An infeasible action fails validation before the day advances. Rewards are computed after the action:

$$
r_t=-\sum_i \left[w_i\max(d_{i,t}-x_{i,t},0)+c_i x_{i,t}
+k_i |x_{i,t}-x_{i,t-1}|\right].
$$

This is the negative of the realized Stage B cost for the day. The prior commitment is the state variable that the policy controls across days. Demand is exogenous. A static solution can miss how a current commitment changes tomorrow's adjustment cost. Receding-horizon linear optimization remains a strong baseline because the forecast-based subproblem is tractable.

## Feasible actions for policy learning

The agent chooses one of four candidate commitments for the current day:

1. Proportional allocation under the public forecast and resource limits.
2. Greedy allocation in order of decreasing unmet penalty minus operating cost.
3. Retain as much of the previous commitment as the current bounds and budget allow, then fill the remaining budget in priority order.
4. Average the proportional and priority allocations.

The first three candidates satisfy the same local and shared limits. Convexity gives the same guarantee for their average. All policies are checked against the hard bounds when they commit. The agent observes a discretization of public information, which is an approximation to the full state. The action menu also restricts it to four feasible alternatives per day. Neither restriction applies to the linear optimizer.

A tabular policy is a bounded test of whether switching among these candidates improves realized cost on unseen synthetic trajectories. Compare it against both receding-horizon optimization and the best fixed candidate chosen on disjoint validation scenarios. If learning adds little, the experiment supports retaining the simpler control policy.

The [environment tests](../../tests/unit/test_daily_environment.py) check that reward equals negative realized cost, altering unavailable demand leaves the current observation unchanged, and rejected commitments leave the environment at the same decision point.
