# Smart "Predict, then Optimize"

**Citation:** Adam N. Elmachtoub and Paul Grigas. *Management Science*, 68(1):9-26 (2022 issue; first online 2021). Published journal article. [DOI: 10.1287/mnsc.2020.3922](https://doi.org/10.1287/mnsc.2020.3922).

**Reviewed:** 2026-10-20. [Full-text author manuscript, arXiv:1710.08005v5](https://arxiv.org/html/1710.08005v5): formulation in Section 2, surrogate in Section 3.2, consistency conditions in Section 4, and experiments in Section 6.

## Findings

SPO measures the realized objective loss of decisions induced by predicted costs, relative to a true-cost optimum. SPO+ provides a surrogate convex in those predictions. Synthetic shortest-path and portfolio experiments report improvements under model misspecification; least squares remains competitive in some settings.

## Relevance to This Repository

Our interpretation: the [allocation evaluation protocol](../../experiments/evaluation-protocol.md#4-allocation-and-policy-metrics) should assess downstream decision loss alongside forecast accuracy. This offers a candidate link between prediction and optimization, not an implemented method or demonstrated tourism result.

## Limitations

The formulation assumes a fixed, known feasible set and uncertainty in linear objective coefficients. It does not directly cover uncertain demand or capacity entering constraints. Consistency requires distributional and geometric assumptions, and training can cost substantially more than standard regression.

## Proposed Next Step

Build a synthetic allocation variant with fixed demand and capacity bounds, a feasible positive minimum-service target, and uncertain operating costs. Compare matched linear cost predictors trained with least squares and SPO+ across increasing nonlinear misspecification. On shared held-out scenarios, report cost regret against the true-cost optimum, prediction error, feasibility, and training time across seeds. This is a proposed experiment.
