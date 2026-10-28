# Optimizing group utility in itinerary planning: a strategic and crowd-aware approach

**Citation:** Junhua Liu, Aldy Gunawan, Kristin L. Wood, and Kwan Hui Lim (2025). *Journal of Big Data*, 12, article 201. Published journal article. [Publisher full text; DOI: 10.1186/s40537-025-01249-9](https://link.springer.com/article/10.1186/s40537-025-01249-9).

**Reviewed:** 2026-10-28. Full-text problem formulation, SCAIRv2, experiments, results, and limitations.

## Findings

SCAIR coordinates itineraries using anticipated crowd distributions. SCAIRv2 records visitor counts by attraction and time interval, incorporating waiting, visit, and travel durations into recommendations. Simulations informed by four theme-park datasets report lower queuing times and improved modeled utility against distance, popularity, and popularity-per-distance baselines.

## Relevance to This Repository

Our interpretation: the [recommendation module](../../methodology/mathematical-framework.md#5-congestion-aware-recommendation) should model how issued recommendations change subsequent crowd conditions. Track expected visits separately from observed occupancy and confirmed admissions. SCAIR is not implemented here.

## Limitations

These are simulation results, not observed visitor improvements. Aggregate utility can conceal losses for individuals, and popularity is an imperfect preference proxy. The authors identify adoption and incentives as unresolved issues; recommended routes do not establish capacity compliance.

## Proposed Next Step

Compare independent rankings with a crowd-updating planner on identical simulated arrivals. Vary recommendation adherence and observation delays. Report mean and lower-decile visitor utility, waiting time, occupancy exceedances, and computation time across seeds. Keep admission limits explicit and assess how results change when visitors choose alternative routes. This experiment is proposed.
