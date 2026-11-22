# The Price of Robustness

**Citation** — Dimitris Bertsimas and Melvyn Sim (2004). *Operations Research*, 52(1), 35–53. Published journal article. [Publisher record and DOI 10.1287/opre.1030.0065](https://pubsonline.informs.org/doi/10.1287/opre.1030.0065).

**Reviewed 2026-11-22.** [Author-hosted published full text](https://web.mit.edu/~dbertsim/www/papers/melvyn/The-Price-Of-Robustness-OR52.pdf), Sections 3–5 and 6.1.

## Findings

A protection budget controls how many uncertain coefficients in a constraint can move jointly toward their adverse limits. Theorem 1 gives an equivalent linear formulation. In the 200-item knapsack example, full protection reduced the nominal objective by 5.5% relative to the unprotected solution. Section 5 extends the formulation to coefficients driven by shared uncertainty factors.

## Relevance to This Repository

Our interpretation is that the allocation module could test a separate staffing constraint with uncertain staff time per assigned request. The protection budget would control how much simultaneous workload variation the schedule covers while retaining the existing service-capacity limits. [Constrained allocation framework](../../methodology/mathematical-framework.md#3-constrained-allocation-and-multiple-objectives)

## Limitations

Feasibility protection applies over the specified uncertainty set. The paper's probability bounds require assumptions such as independence and symmetry of the underlying shocks. Correlated site errors and asymmetric peaks require separate checks. The knapsack result gives no estimate of tourism performance.

## Proposed Next Step

Fit workload deviation ranges on training scenarios. Compare nominal allocation with partial and full protection on identical held-out days, including common workload surges. Report staffing overload frequency and magnitude, realized weighted unmet demand, and scheduled capacity. This experiment is proposed.
