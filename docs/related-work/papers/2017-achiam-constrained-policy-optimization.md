# Constrained Policy Optimization

**Citation:** Joshua Achiam, David Held, Aviv Tamar, and Pieter Abbeel (2017). *Proceedings of the 34th International Conference on Machine Learning*, PMLR 70:22-31. Published conference paper. [Official record](https://proceedings.mlr.press/v70/achiam17a.html).

**Reviewed:** 2026-10-17. [Full text](https://proceedings.mlr.press/v70/achiam17a/achiam17a.pdf), constrained-MDP formulation and Sections 5-6; experimental scope from the introduction.

## Findings

CPO optimizes policy reward subject to bounds on expected discounted costs. It derives trust-region updates with constraint-violation bounds and a practical approximation for neural policies. The paper demonstrates the approach on simulated robot locomotion tasks, rather than tourism management.

## Relevance to This Repository

Our interpretation: separate congestion-cost limits from revenue or satisfaction rewards when developing [pricing policies](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making). This provides a principled comparison to reward penalties alone.

## Limitations

Expected-cost constraints are not per-step occupancy guarantees. The practical algorithm uses sampling and approximations and includes recovery from infeasible updates. Operational admission limits would still need explicit enforcement.

## Proposed Next Step

After a simulator exists, compare constrained and penalty-based policies under matched scenarios, reporting return, violation frequency, and violation magnitude under the [evaluation protocol](../../experiments/evaluation-protocol.md).
