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

## Emerging Connections

- [Route recommendation](papers/2024-yi-congestion-aware-routes.md) motivates evaluating visitor experience alongside congestion and spatial distribution.
- [TFT](papers/2021-lim-temporal-fusion-transformers.md) offers a candidate forecasting architecture; its value here depends on held-out demand and downstream decision evaluation.
- [CPO](papers/2017-achiam-constrained-policy-optimization.md) separates policy rewards from cost constraints, while operational capacity enforcement remains a distinct requirement.
- [RAG](papers/2020-lewis-retrieval-augmented-generation.md) informs the evidence-supported interaction layer; retrieval quality and consistency with numerical decisions need separate evaluation.

Together, these papers suggest evaluating prediction, feasible decision making, visitor acceptance, and factual explanation as distinct parts of an integrated system. This is a proposed research direction, not a demonstrated end-to-end result.

These connections inform the [mathematical framework](../methodology/mathematical-framework.md) and [evaluation protocol](../experiments/evaluation-protocol.md). Literature coverage does not imply that a referenced method has been implemented.

## Coverage to Extend

Priorities include tourism demand forecasting, constrained decision making, adaptive pricing, recommendation under shared capacities, UAV-assisted crowd measurement, retrieval-grounded assistance, and evaluation of integrated systems. Balance foundational methods with recent directly relevant studies. Review an accessible, relevant paper rather than adding an unverified citation to fill a category.

See the [review guidelines](review-guidelines.md) for selection, evidence, and update conventions.
