# Video Individual Counting for Moving Drones

**Citation:** Yaowu Fan, Jia Wan, Tao Han, Antoni B. Chan, and Andy J. Ma (2025). *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, pp. 12284–12293. Published conference paper. [DOI: 10.1109/ICCV51701.2025.01142](https://doi.org/10.1109/ICCV51701.2025.01142).

**Reviewed:** 2026-11-10. [Full-text author manuscript, arXiv:2503.10701v2](https://arxiv.org/html/2503.10701v2), Sections 3–4 and 5.1–5.3, Table 2, and Appendices A and D. This note covers the 2025 SDNet paper.

## Findings

MovingDroneCrowd contains 89 clips with scene-disjoint splits. SDNet estimates shared pedestrian density between frame pairs, then derives inflow/outflow maps from global-minus-shared density through a decoder. Initial-frame counts plus accumulated inflow estimate video-level individuals. On its MovingDroneCrowd test split, Table 2 reports video-count MAE of 41.00 for SDNet versus 66.06 for CGNet.

## Relevance to This Repository

Our interpretation: [UAV-assisted monitoring](../../../README.md#1-uav-assisted-tourism-monitoring) needs temporal counting beyond repeated image totals. View entries require spatial calibration and re-entry checks before representing physical-zone arrivals or occupancy. SDNet is not implemented here.

## Limitations

Appendix D identifies erroneous shared-density responses and costly cross-frame attention. UAVVIC comparisons use its validation set because its test set was unavailable. These benchmarks do not establish reliable tourism admission decisions.

## Proposed Next Step

Compare SDNet and CGNet on the official scene split, tuning frame intervals only on validation scenes. Report video-count MAE, inflow/outflow errors, and runtime by density and lighting. Separately test annotated re-entry sequences for duplicate counts and false physical-zone arrivals. This experiment is proposed.
