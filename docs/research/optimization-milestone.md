# Optimization Milestone: Capacity Allocation Baseline

## Purpose

The next technical milestone is a small, reproducible optimization baseline for allocating limited capacity across locations and time periods. Its purpose is to establish a transparent decision model that can later support comparisons with heuristics and adaptive policies.

This document is a technical specification. It does not report completed experiments or performance results.

## Problem Definition

For a set of locations and discrete time periods, the model will assign available capacity while balancing three objectives:

1. serve forecast demand,
2. limit overload and unmet demand, and
3. avoid unnecessary reallocation effort.

The initial formulation will use synthetic, versioned inputs so that the complete experiment can be reproduced without dependence on restricted or proprietary data.

## Initial Model

### Inputs

- forecast demand by location and time period,
- nominal and maximum capacity,
- allocation or adjustment cost,
- penalty for unmet demand or overload,
- optional fairness or service-level thresholds.

### Decision variables

- capacity assigned to each location and time period,
- unmet demand or overload slack,
- optional transfers between locations or adjacent periods.

### Constraints

- total resource availability,
- local capacity limits,
- non-negativity and variable domains,
- conservation of transferable resources,
- optional minimum service levels,
- optional limits on changes between consecutive periods.

### Objective

The baseline will minimize a weighted combination of unmet-demand penalties, operating or transfer costs, and allocation instability. All weights and units will be declared in configuration files and examined through sensitivity analysis.

## Baselines and Evaluation

The optimization result will be compared with at least one simple, deterministic heuristic, such as proportional allocation. Evaluation will report:

- constraint feasibility,
- objective value and its components,
- served and unmet demand,
- utilization and overload by location,
- allocation stability between periods,
- solver status and runtime,
- sensitivity to demand and penalty parameters.

No single metric will be treated as sufficient evidence of performance. Results will be interpreted together with assumptions, constraint activity, and scenario characteristics.

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
