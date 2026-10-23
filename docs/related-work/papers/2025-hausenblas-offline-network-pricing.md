# Improving Network Dynamic Pricing Policies through Offline Reinforcement Learning

**Citation:** Philipp Hausenblas, Dominik Eichhorn, Andreas Brieden, Matthias Soppert, and Claudius Steinhardt (2025). *OR Spectrum*, 47:1217-1266. Published journal article. [DOI: 10.1007/s00291-025-00821-2](https://doi.org/10.1007/s00291-025-00821-2).

**Reviewed:** 2026-10-23. [Publisher full text](https://link.springer.com/article/10.1007/s00291-025-00821-2), Sections 4, 5.2, 6.2-6.4, 6.5.4, and 6.6.

## Findings

Critic-regularized regression (CRR) learns pricing policies from static sales trajectories. The authors reduce state/action representations and exclude sold-out products from actor-loss terms. In simulated network-revenue benchmarks, many learned policies outperform the data-generating policies; gains depend on useful price variation in the logs.

## Relevance to This Repository

Our interpretation: the [dynamic-pricing module](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making) could model bookings sharing room-night inventory or tourism bundles competing for capacity. Log availability alongside prices, purchases, and next-state inventory. This is a proposed adaptation, not an implemented method.

## Limitations

Training is offline, but evaluation uses a simulator. There is no hotel field validation or universal improvement guarantee; some zero-variation cases underperform. Sparse data and shifted demand limit transfer. Avoiding live exploration does not establish deployment safety.

## Proposed Next Step

Build a synthetic two-night booking simulator with overlapping one- and two-night offers. Generate fixed logs from pricing rules with different action coverage; train CRR without new interactions. Compare with behavior cloning and those rules on shared held-out demand draws, reporting revenue, rejected bookings, infeasible offers, and performance under demand shifts. Enforce inventory limits independently of learned prices.
