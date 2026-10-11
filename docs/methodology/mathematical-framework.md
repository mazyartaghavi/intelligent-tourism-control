# Mathematical Framework

Status: research specification. The [proportional capacity-allocation heuristic](../../src/tourism_control/optimization/proportional.py) is implemented; the forecasting, pricing, recommendation, and language interfaces below describe planned components. No empirical performance or deployment results are asserted.

## 1. Notation and Decision Timing

| Symbol | Meaning |
|---|---|
| $i \in \{1,\ldots,n\}$ | Location index |
| $t$ and $h$ | Discrete time period and forecast horizon |
| $d_{i,t}$ | Requested service volume at location $i$ during period $t$ |
| $C_{i,t}$ | Maximum service capacity in that period |
| $x_{i,t}$ | Assigned service capacity, in the same unit as demand |
| $o_{i,t}$ | Concurrent occupancy, distinct from arrivals or service volume |
| $z_t$ | Observed context and monitoring features available at time $t$ |
| $p_{i,t}$ | Price offered for the next decision interval |
| $B_t$ | Shared service-capacity budget for period $t$ |

Use a fixed interval length and declare units in every scenario. A service volume measured over an interval cannot be compared directly with a simultaneous occupancy limit without a model of arrivals, departures, and service duration.

The intended sequence is observation, forecast, feasible decision, visitor response, and state update. Information arriving after a decision is unavailable to that decision. Historical demand observed under previous prices must be distinguished from hypothetical demand under a new price.

## 2. Forecasting and Uncertainty

Let $\mathcal I_t$ contain information available at the forecast origin, including past demand, context, and any known future schedules. For a location graph $G$ and history length $k$, a point forecast is

$$
\widehat{\mathbf d}_{t+h\mid t}
= f_\theta(\mathbf d_{t-k:t},z_t,G).
$$

The function may be a statistical or learned model. Any future contextual inputs must be known at time $t$ or forecast separately. Forecasts of non-negative service volumes should use a declared non-negative output or postprocessing rule.

A probabilistic model instead estimates

$$
p(\mathbf d_{t+h}\mid\mathcal I_t).
$$

For a single demand variable and parameters $\theta$, a Bayesian predictive formulation is

$$
p(d_{i,t+h}\mid\mathcal I_t)
=\int p(d_{i,t+h}\mid\theta,\mathcal I_t)
       p(\theta\mid\mathcal I_t)\,d\theta.
$$

Prediction intervals refer to future observations, not merely uncertainty about the mean. Their nominal coverage and horizon must be declared. Joint scenario sampling should preserve relevant spatial and temporal dependence when used for downstream allocation.

The first allocation model treats a point forecast as a fixed scenario input. Robust or stochastic optimization will require a separate specification; supplying intervals alone does not make a deterministic model robust.

## 3. Constrained Allocation and Multiple Objectives

For generic decision variables $v$, a destination-level design may consider

$$
\max_{v\in\mathcal F}
\left(\operatorname{Sat}(v),\operatorname{Rev}(v),
      -\operatorname{Cong}(v),-\operatorname{Env}(v)\right),
$$

where $\mathcal F$ is the feasible set and the four functions represent satisfaction, revenue, congestion, and environmental impact. Each function needs an operational definition; a proxy should be identified as such.

A weighted scalar objective is one possible comparison rule:

$$
J(v)=w_s\widetilde{\operatorname{Sat}}(v)
    +w_r\widetilde{\operatorname{Rev}}(v)
    -w_c\widetilde{\operatorname{Cong}}(v)
    -w_e\widetilde{\operatorname{Env}}(v),
\qquad w_j\geq0,\quad\sum_jw_j=1.
$$

Tildes indicate declared scaling to comparable units, fixed before test evaluation. Report component values and sensitivity to weights; a single weighted score does not establish that all objectives improve. Capacity and resource constraints remain explicit rather than being enforced only through penalties.

The [optimization milestone](../research/optimization-milestone.md#deterministic-allocation-formulation) defines a narrower linear model with allocation, unmet demand, operating cost, and temporal adjustment terms. It is the next implementation target for comparison with the existing heuristic.

## 4. Dynamic Pricing as Sequential Decision Making

A candidate Markov decision process is

$$
\mathcal M=(\mathcal S,\mathcal A,P,r,\gamma),
\qquad 0\leq\gamma<1.
$$

Here $P$ is the transition kernel, $r$ is the reward function, and $\gamma$ is the discount factor. A candidate state includes occupancy, demand forecasts, previous prices, and observed context:

$$
s_t=(\mathbf o_t,\widehat{\mathbf d}_{t+1\mid t},\mathbf p_{t-1},z_t),
\qquad a_t=\mathbf p_t\sim\pi(\cdot\mid s_t).
$$

This is a modeling assumption. If the available state does not summarize the relevant history, add history or a belief-state model rather than asserting the Markov property. Specify whether forecasts reflect previous prices or are conditional on candidate actions.

For bounded rewards, the discounted objective is

$$
J(\pi)=\mathbb E_\pi\left[\sum_{t=0}^{\infty}\gamma^t
r(s_t,a_t,s_{t+1})\right].
$$

Finite simulations must report their actual horizon and terminal treatment. A reward can combine scaled revenue, satisfaction, congestion, and environmental proxies as in Section 3. Price bounds and maximum permitted price changes belong in the admissible action set.

For differentiable expected demand $q_i(p)>0$ at price $p>0$, own-price elasticity is

$$
\varepsilon_i(p)=\frac{p}{q_i(p)}\frac{\partial q_i(p)}{\partial p}.
$$

Its sign and magnitude require estimation or explicit synthetic assumptions. Cross-location substitution requires a joint demand model; independent elasticity curves do not represent visitor redistribution by themselves.

The expression $\min(q_i(p),C_i)$ represents capped service in a simplified model. It does not prove that actual occupancy stays within a safety limit. An admission mechanism and occupancy dynamics, such as occupancy plus admissions minus departures, are needed to enforce such a limit operationally. Overflow, rejected demand, and waiting must be recorded rather than removed from evaluation.

## 5. Congestion-Aware Recommendation

For visitor $u$, location $i$, and context at time $t$, define a candidate utility

$$
U_{u,i,t}=\beta_s S_{u,i,t}+\beta_d D_{u,i,t}-\beta_c H_{i,t},
\qquad \beta_s,\beta_d,\beta_c\geq0.
$$

Here $S$ is predicted preference or satisfaction, $D$ is a declared diversification score, and $H$ is a congestion indicator. These components must use documented scales. Preference predictions are not measurements of realized satisfaction.

One possible congestion indicator is $H_{i,t}=o_{i,t}/K_i$ for a positive concurrent occupancy limit $K_i$. Closed or zero-capacity locations are excluded from candidates; utilization is not evaluated by division by zero. An alternative using forecast arrivals requires a compatible service-capacity denominator.

Recommendations may select the highest-scoring feasible candidates, with deterministic tie handling. Budget, travel time, accessibility, and availability filters should be applied before ranking. Diversification across a list requires a list-level definition. Recommending a location neither reserves its capacity nor guarantees visitor compliance; coupled simulations need a response and admission model.

## 6. Grounded Language Interface

Let $\mathcal K$ be a knowledge collection, $\xi$ a query, and $\operatorname{Retr}_k(\xi,\mathcal K)$ the retrieved evidence. A planned response interface is

$$
y_t=\operatorname{LLM}\left(\xi,
\operatorname{Retr}_k(\xi,\mathcal K),\mathcal D_t\right),
$$

where $\mathcal D_t$ contains structured outputs from forecasting, allocation, pricing, and recommendation, together with their timestamps and uncertainty indicators. The interface follows the general retrieval-plus-generation idea described by [Lewis et al. (2020)](https://arxiv.org/abs/2005.11401); it does not reproduce their model or experimental results.

The proposed interface explains feasible decisions and cites supporting evidence. Generated text must not silently change numerical allocations or prices. Retrieval does not guarantee factual accuracy: stale evidence, unsupported claims, and mismatches with structured outputs require separate checks. If the evidence is insufficient, the response should state that limitation.

## 7. Implementation Boundaries

| Component | Available artifact | Remaining work |
|---|---|---|
| Proportional allocation | Executable heuristic and unit tests | Comparative experiment runner |
| Constrained allocation | Explicit mathematical specification | Solver implementation and validation |
| Forecasting and pricing | Equations and assumptions | Data interfaces, models, simulator, policy evaluation |
| Recommendation and language interface | Utility and information-flow specification | Ranking, retrieval, generation, and evaluation implementations |

Use the [evaluation protocol](../experiments/evaluation-protocol.md) to design comparisons. Demonstrating that an equation is well defined or a unit test passes is separate from demonstrating useful performance on a research task.
