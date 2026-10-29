# Distribution Matching for Crowd Counting

**Citation:** Boyu Wang, Huidong Liu, Dimitris Samaras, and Minh Hoai Nguyen (2020). *Advances in Neural Information Processing Systems*, 33. Published conference paper. [Official record](https://proceedings.neurips.cc/paper/2020/hash/118bd558033a1016fcc82560c65cca5f-Abstract.html).

**Reviewed:** 2026-10-29. [Full-text author manuscript, arXiv:2009.13077v2](https://arxiv.org/html/2009.13077v2), Sections 3 and 5.2; Table 2.

## Findings

DM-Count combines absolute count error, optimal transport between normalized density maps, and total variation distance, avoiding Gaussian-smoothed training targets. On the NWPU test set, Table 2 reports count MAE of 88.4 versus 105.4 for Bayesian Loss, both using VGG-19 backbones. These are image-level benchmark results.

## Relevance to This Repository

Our interpretation: [UAV-assisted monitoring](../../../README.md#1-uav-assisted-tourism-monitoring) should evaluate spatial counting errors alongside total-count accuracy before estimating zone occupancy. DM-Count is a candidate training objective for this comparison, not an implemented component.

## Limitations

Single-image benchmarks do not establish transfer to aerial scenes or reliable capacity decisions. A density map is not a calibrated uncertainty interval or a record of unique arrivals. Spatial calibration and temporal association remain separate requirements. Optimal transport is approximated during training, and loss weights require validation.

## Proposed Next Step

On the official DroneCrowd sequence split, compare matched RGB backbones trained with Gaussian pixelwise loss, Bayesian Loss, and DM-Count. Reserve training sequences for tuning. Report total and regional count MAE, undercount bias, and training cost across seeds. In a separate occupancy simulation, inject regional errors and measure missed capacity-threshold crossings. This experiment is proposed.
