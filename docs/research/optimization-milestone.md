# Optimization Milestone: Capacity Allocation Baseline

## Purpose

The next technical milestone is a small, reproducible optimization baseline for allocating limited capacity across locations and time periods. Its purpose is to establish a transparent decision model that can later support comparisons with heuristics and adaptive policies.

This document is a technical specification. It does not report completed experiments or performance results.

## Available Heuristic Comparator

The [proportional-allocation module](../../src/tourism_control/optimization/proportional.py) provides a first executable comparator. For each location, eligible demand is the minimum of requested demand and local capacity. If the shared budget is scarce, every eligible demand is multiplied by the same factor: budget divided by total eligible demand. Otherwise, each location receives its eligible demand and any excess budget remains unused.

Inputs are non-negative, finite quantities in a common divisible capacity unit for a single time period. Demand and capacity lists must have equal, nonzero lengths. Allocations respect local limits and the shared budget within floating-point tolerance; unmet demand includes any demand above local capacity.

The module exposes `allocate_capacity(demand, capacity, budget)` and a command-line interface returning JSON. The [README example](../../README.md#try-the-capacity-allocation-baseline) uses synthetic inputs. Unit tests check feasibility, boundary cases, and deterministic behavior. This heuristic has no costs, integer decisions, transfers, or time coupling; the full optimization milestone below remains open.

## Problem Definition

For a set of locations and discrete time periods, the model will assign available capacity while balancing three objectives:

1. serve forecast demand,
2. limit overload and unmet demand, and
3. avoid unnecessary reallocation effort.

The initial formulation will use synthetic, versioned inputs so that the complete experiment can be reproduced without dependence on restricted or proprietary data.

## Initial Model

### Inputs

- forecast demand by location and time period,
- maximum service capacity and shared resource budget,
- operating and adjustment costs,
- unmet-demand penalties,
- previous allocation for the first period.

### Decision variables

- capacity assigned to each location and time period,
- unmet demand,
- absolute allocation-change auxiliaries.

### Constraints

- total resource availability,
- local capacity limits,
- non-negativity and variable domains,
- demand balance,
- optional limits on changes between consecutive periods.

Transfers, fairness constraints, and minimum service levels are possible later extensions. They are not part of the initial formulation below.

### Objective

The first baseline will minimize a weighted combination of unmet-demand penalties, operating costs, and allocation instability. Transfers and optional service-level constraints require later extensions. All weights and units will be declared in configuration files and examined through sensitivity analysis.

### Deterministic Allocation Formulation

For locations $i=1,\ldots,n$ and periods $t=1,\ldots,T$, let $d_{i,t}\geq0$ be fixed scenario demand, $C_{i,t}\geq0$ local service capacity, and $B_t\geq0$ the shared budget. These inputs and allocations use a common divisible service-capacity unit per period. Demand may be synthetic or a forecast frozen at the planning origin. The budget is a capacity resource, not money.

Choose continuous allocations $x_{i,t}\geq0$, unmet demand $u_{i,t}\geq0$, and non-negative adjustment variables $a_{i,t}$. Given a fixed previous allocation $x_{i,0}$, the planned linear program is

$$
\min_{x,u,a}\sum_{t=1}^{T}\sum_{i=1}^{n}
\left(w_{i,t}u_{i,t}+c_{i,t}x_{i,t}+\kappa_i a_{i,t}\right)
$$

subject to

$$
x_{i,t}+u_{i,t}=d_{i,t},\qquad
0\leq x_{i,t}\leq C_{i,t},\qquad
\sum_{i=1}^{n}x_{i,t}\leq B_t,
$$

$$
a_{i,t}\geq x_{i,t}-x_{i,t-1},\qquad
a_{i,t}\geq x_{i,t-1}-x_{i,t},\qquad
u_{i,t},a_{i,t}\geq0.
$$

All coefficients are finite and non-negative. The weights $w_{i,t}$ price unmet demand, $c_{i,t}$ price operating service, and $\kappa_i$ price adjustments, in a common objective unit per service-capacity unit. Demand balance implies $x_{i,t}\leq d_{i,t}$. With positive $\kappa_i$, minimizing makes $a_{i,t}=|x_{i,t}-x_{i,t-1}|$; when $\kappa_i=0$, compute the actual absolute change directly for reporting. An optional bound $a_{i,t}\leq\Delta_i$ models a maximum change and must be checked for feasibility against $x_{i,0}$ and the capacity sequence.

Without optional constraints, zero allocation is feasible with $u=d$ and appropriate adjustment values. Expensive service may deliberately leave demand unmet; interpret that outcome through the coefficients rather than assuming the entire budget must be used. A monetary budget or heterogeneous resource consumption requires separate coefficients and constraints. This model has no resource-transfer network, waiting queue, or concurrent occupancy dynamics.

### Relationship to the Existing Heuristic

For one period, define $e_i=\min(d_i,C_i)$ and $E=\sum_i e_i$. The implemented rule is

$$
x_i^{\mathrm{prop}}=
\begin{cases}
0,& E=0,\\
e_i\min(1,B/E),& E>0.
\end{cases}
$$

It satisfies the simple capacity and budget constraints within floating-point tolerance and serves $\min(B,E)$ total demand. Setting $u_i=d_i-x_i^{\mathrm{prop}}$ provides a feasible comparator for the single-period linear program. If unmet-demand weights are identical and positive and operating and adjustment costs are zero, this heuristic already attains an optimum for total unmet demand. Weighted priorities, costs, and temporal coupling can change which allocation is preferred; comparisons must state those assumptions.

Repeated single-period allocations do not automatically satisfy optional limits on inter-period changes. Compare only common feasible settings or specify and evaluate a separate repair policy. The linear program above is a specification; no solver is included in the current implementation.

## Baselines and Evaluation

The optimization result will be compared with at least one simple, deterministic heuristic, such as proportional allocation. Evaluation will report:

- constraint feasibility,
- objective value and its components,
- served and unmet demand,
- utilization and overload by location,
- allocation stability between periods,
- solver status and runtime,
- sensitivity to demand and penalty parameters.

No single metric will be treated as sufficient evidence of performance. Results will be interpreted together with assumptions, constraint activity, and scenario characteristics. The [evaluation protocol](../experiments/evaluation-protocol.md) defines comparison and reporting rules; the [mathematical framework](../methodology/mathematical-framework.md) connects allocation to forecasting, pricing, recommendation, and language interfaces.

## Reproducibility Requirements

The milestone is complete when the repository contains:

- a documented synthetic scenario schema,
- a configuration-driven model implementation,
- a fixed random seed where scenario generation is stochastic,
- unit tests for constraint construction and solution validation,
- a command-line experiment entry point,
- machine-readable results and a concise human-readable summary,
- environment and solver information recorded with each run.

## Interface to Later Work

Forecasting modules should eventually provide demand estimates and uncertainty information through a stable input schema. The optimizer should return allocations, slacks, objective components, and diagnostic metadata. This boundary will allow optimization baselines to be compared with reinforcement-learning policies under consistent scenarios and metrics.

## Out of Scope for This Milestone

- claims based on real-world deployment,
- online policy learning,
- dynamic pricing implementation,
- multi-agent control,
- production infrastructure,
- causal claims about visitor behavior.

These topics require separate assumptions, evidence, and validation.
