# A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II

**Citation:** Kalyanmoy Deb, Amrit Pratap, Sameer Agarwal, and T. Meyarivan (2002). *IEEE Transactions on Evolutionary Computation*, 6(2), 182–197. Published journal paper. [DOI: 10.1109/4235.996017](https://doi.org/10.1109/4235.996017).

**Reviewed:** 2026-11-05. [Published full text, academic mirror](https://dynamics.org/~altenber/UH_ICS/EC_REFS/MULTI_OBJ/DebPratapAgarwalMeyarivan.pdf), Sections III, IV.B–C, and VI.A.

## Findings

NSGA-II combines nondominated sorting, parent–offspring selection, and crowding distance to preserve objective-space diversity. Constrained dominance prefers feasible solutions; among infeasible solutions, it prefers smaller overall violation. Benchmark results show improved spread relative to PAES and SPEA, while convergence depends on the problem. Under the tested ZDT4 settings, real-coded NSGA-II gets stuck at a local Pareto front.

## Relevance to This Repository

Our interpretation: the [multiple-objective allocation specification](../../methodology/mathematical-framework.md#3-constrained-allocation-and-multiple-objectives) could compare alternative service–cost trade-offs before choosing weights. Crowding distance concerns objective-space diversity, not physical congestion. NSGA-II is a candidate later comparator, not an implemented method or a replacement for the documented linear baseline.

## Limitations

These benchmarks do not validate tourism decisions. Finite search does not certify a globally complete Pareto front. Feasibility must be checked independently, including constraint scaling and numerical tolerances.

## Proposed Next Step

For a small discretized allocation scenario, enumerate feasible allocations to obtain its exact discrete Pareto set for unmet demand and operating cost. Compare NSGA-II and weighted-objective solutions on the same grid. Report feasibility, normalized distance to the reference set, objective-space coverage, and runtime across seeds. This experiment is proposed.
