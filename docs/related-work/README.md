# Related Work and Literature Review

An expanding, selective review of research relevant to intelligent tourism control. Each paper has a separate note with a verified citation, concise findings, relevance to repository modules, limitations, and a possible experiment. Suggested applications are our interpretation, not results demonstrated by this repository.

This is a curated starting collection, not an exhaustive or systematic review. Notes are added individually. Published papers and preprints are identified separately; full-text access and the sections reviewed are recorded in each note.

## Paper Index

| Paper | Year | Topic | Evidence reviewed | Added |
|---|---:|---|---|---|
| [Yi et al.: Congestion-aware route recommendation](papers/2024-yi-congestion-aware-routes.md) | 2024 | Tourism recommendation; user experience | Full-text methods and results | 2026-10-17 |
| [Lim et al.: Temporal Fusion Transformers](papers/2021-lim-temporal-fusion-transformers.md) | 2021 | Multi-horizon forecasting; uncertainty | Full-text author manuscript | 2026-10-17 |
| [Achiam et al.: Constrained Policy Optimization](papers/2017-achiam-constrained-policy-optimization.md) | 2017 | Constrained reinforcement learning | Full-text formulation and implementation | 2026-10-17 |
| [Lewis et al.: Retrieval-Augmented Generation](papers/2020-lewis-retrieval-augmented-generation.md) | 2020 | Grounded language services | Full-text experiments and results | 2026-10-17 |
| [Meng et al.: Multi-modal crowd counting](papers/2025-meng-multimodal-crowd-counting.md) | 2025 | UAV/crowd sensing; visual-thermal measurement | Full-text methods, results, and ablations | 2026-10-18 |
| [Garcia et al.: Hotel price-response estimation](papers/2022-garcia-hotel-price-response.md) | 2022 | Tourism-specific dynamic pricing; causal demand estimation | Full-text identification and empirical results | 2026-10-19 |
| [Elmachtoub and Grigas: Smart "Predict, then Optimize"](papers/2022-elmachtoub-smart-predict-optimize.md) | 2022 | Prediction-optimization integration; decision-focused evaluation | Full-text author manuscript | 2026-10-20 |
| [Olivares et al.: Hierarchical Poisson-mixture forecasts](papers/2024-olivares-hierarchical-poisson-mixtures.md) | 2024 | Tourism demand forecasting; probabilistic aggregation | Full-text author manuscript, methods and results | 2026-10-21 |
| [Hausenblas et al.: Offline network pricing](papers/2025-hausenblas-offline-network-pricing.md) | 2025 | Dynamic pricing; offline reinforcement learning; shared inventory | Full-text formulation, methods, and simulation results | 2026-10-23 |
| [Wen et al.: DroneCrowd benchmark](papers/2021-wen-dronecrowd-benchmark.md) | 2021 | UAV/crowd sensing; counting; localization and tracking | Full-text author manuscript, dataset, methods, and results | 2026-10-24 |
| [Bandalouski et al.: Disaggregated hotel pricing](papers/2021-bandalouski-disaggregated-hotel-pricing.md) | 2021 | Tourism-specific dynamic pricing; constrained optimization; demand segmentation | Full-text assumptions, formulation, and simulation design | 2026-10-25 |

## Emerging Connections

- [Route recommendation](papers/2024-yi-congestion-aware-routes.md) motivates evaluating visitor experience alongside congestion and spatial distribution.
- [TFT](papers/2021-lim-temporal-fusion-transformers.md) offers a candidate forecasting architecture; its value here depends on held-out demand and downstream decision evaluation.
- [CPO](papers/2017-achiam-constrained-policy-optimization.md) separates policy rewards from cost constraints, while operational capacity enforcement remains a distinct requirement.
- [RAG](papers/2020-lewis-retrieval-augmented-generation.md) informs the evidence-supported interaction layer; retrieval quality and consistency with numerical decisions need separate evaluation.
- [Multi-modal crowd counting](papers/2025-meng-multimodal-crowd-counting.md) motivates testing observation errors before using sensed counts in forecasts or occupancy decisions; image counts do not directly measure future arrivals.
- [Hotel price-response estimation](papers/2022-garcia-hotel-price-response.md) highlights the distinction between forecasting bookings and identifying the effect of changing prices; pricing simulators need defensible response assumptions.
- [Smart "Predict, then Optimize"](papers/2022-elmachtoub-smart-predict-optimize.md) motivates evaluating forecasts through downstream decision losses, while distinguishing uncertain objective coefficients from uncertain constraints.
- [Hierarchical Poisson-mixture forecasts](papers/2024-olivares-hierarchical-poisson-mixtures.md) suggest joint demand scenarios with consistent location and regional totals; aggregation coherence, uncertainty calibration, and capacity compliance require distinct checks.
- [Offline network pricing](papers/2025-hausenblas-offline-network-pricing.md) connects logged decisions to candidate pricing policies, but useful action coverage and credible evaluation remain prerequisites; avoiding live training does not establish deployment safety.
- [DroneCrowd](papers/2021-wen-dronecrowd-benchmark.md) motivates separate checks of count accuracy and trajectory quality; aggregate counts alone cannot validate spatial occupancy or unique arrivals.
- [Disaggregated hotel pricing](papers/2021-bandalouski-disaggregated-hotel-pricing.md) offers a tractable pricing baseline while motivating tests of category sparsity, price-response assumptions, and realized inventory limits.

Together, these papers suggest evaluating measurement, prediction, feasible decision making, visitor acceptance, and factual explanation as distinct parts of an integrated system. This is a proposed research direction, not a demonstrated end-to-end result.

These connections inform the [mathematical framework](../methodology/mathematical-framework.md) and [evaluation protocol](../experiments/evaluation-protocol.md). Literature coverage does not imply that a referenced method has been implemented.

## Coverage to Extend

Priorities include tourism demand forecasting, constrained decision making, adaptive pricing, recommendation under shared capacities, UAV-assisted crowd measurement, retrieval-grounded assistance, and evaluation of integrated systems. Balance foundational methods with recent directly relevant studies. Review an accessible, relevant paper rather than adding an unverified citation to fill a category.

See the [review guidelines](review-guidelines.md) for selection, evidence, and update conventions.
