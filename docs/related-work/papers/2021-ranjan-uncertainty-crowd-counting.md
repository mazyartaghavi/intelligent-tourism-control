# Uncertainty Estimation and Sample Selection for Crowd Counting

**Citation:** Viresh Ranjan, Boyu Wang, Mubarak Shah, and Minh Hoai (2021). *Computer Vision – ACCV 2020*, LNCS 12626, pp. 375–391. Published conference chapter; conference held in 2020. [Publisher record; DOI: 10.1007/978-3-030-69541-5_23](https://link.springer.com/chapter/10.1007/978-3-030-69541-5_23).

**Reviewed:** 2026-11-06. [Full-text author manuscript, arXiv:2009.14411v2](https://arxiv.org/html/2009.14411v2), Sections 3–4, 5.2, and 7.3; Table 4.

## Findings

The Crowd Transformer Network learns Gaussian density means and variances using negative log likelihood. Predicted variance or ensemble disagreement ranks target-domain images for annotation. After UCF-QNRF pretraining, selecting 500 NWPU training images by aleatoric uncertainty yields validation count MAE of 81.5, versus 96.7 for random selection in Table 4.

## Relevance to This Repository

Our interpretation: [UAV-assisted monitoring](../../../README.md#1-uav-assisted-tourism-monitoring) could prioritize annotation when adapting a counting model to new camera scenes. This informs data collection before occupancy evaluation; the method is not implemented here.

## Limitations

The evidence concerns image benchmarks, not aerial deployment. Error-ranking quality does not establish calibrated total-count intervals. Pixel variances alone omit spatial covariance when aggregating uncertainty. Image budgets also differ from annotation-time budgets because crowd densities vary.

## Proposed Next Step

Compare random, predicted-count, variance, and ensemble selection on an aerial dataset split by scene. Restrict selection to training scenes and compare learning curves against measured annotation time and labeled-head counts. On untouched test scenes, report count MAE, regional undercount bias, and error-ranking quality across seeds. This experiment is proposed.
