# Bayesian Loss for Crowd Count Estimation With Point Supervision

**Citation:** Zhiheng Ma, Xing Wei, Xiaopeng Hong, and Yihong Gong (2019). *IEEE/CVF International Conference on Computer Vision*, pp. 6142-6151. Published conference paper. [DOI: 10.1109/ICCV.2019.00624](https://doi.org/10.1109/ICCV.2019.00624).

**Reviewed:** 2026-11-15. [Full author manuscript, arXiv:1908.03684v1](https://arxiv.org/html/1908.03684v1), Sections 3.2-3.4 and 4.2-4.5, including Tables 2-4.

## Findings

Bayesian Loss assigns predicted density to annotated heads through spatial probabilities and supervises each head's expected contribution toward one. Bayesian+ adds a background contribution with target zero. With matched VGG-19 networks on UCF-QNRF, Table 3 reports count MAE of 88.7 for Bayesian+ versus 106.8 for the pixelwise baseline when both use image resizing. Annotation-perturbation experiments also favor the proposed loss.

## Relevance to This Repository

Our interpretation: this supplies the missing methodological basis for the Bayesian Loss comparator proposed in the [DM-Count review](2020-wang-distribution-matching-counts.md). Testing supervision choices could improve crowd observations used by the planned sensing module. Implementation and aerial validation remain proposed work.

## Limitations

The evidence uses image-counting benchmarks. Spatial assignment probabilities provide a training mechanism, while calibrated count intervals require additional evaluation. Image resizing materially affects accuracy, and camera transfer, regional occupancy errors, and temporal identities need separate checks.

## Proposed Next Step

Compare pixelwise loss, Bayesian+, and DM-Count with identical backbones, resizing, training budgets, and scene splits on DroneCrowd. Perturb training annotations only. Report total and regional MAE, undercount bias, and background false counts across seeds, selecting parameters on validation scenes. This experiment is proposed.
