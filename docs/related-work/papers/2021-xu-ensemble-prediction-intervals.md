# Conformal Prediction Interval for Dynamic Time-Series

**Citation:** Chen Xu and Yao Xie (2021). *ICML*, PMLR 139:11559-11569. Published conference paper. [Official record and persistent identifier: pmlr-v139-xu21h](https://proceedings.mlr.press/v139/xu21h.html).

**Reviewed:** 2026-11-18. [Published full text](https://proceedings.mlr.press/v139/xu21h/xu21h.pdf), Sections 2-4 and 5.1-5.2, Algorithm 1, and Theorem 1.

## Findings

EnbPI builds prediction intervals from bootstrap ensembles and leave-one-out residuals, updating a rolling residual window as observations arrive without refitting the predictors. Its approximate marginal-coverage analysis depends on error-process and estimation-quality assumptions. In the Atlanta solar experiment, Section 5.2 reports 90% aggregate coverage but poorer coverage around midday, illustrating why overall calibration can conceal systematic failures.

## Relevance to This Repository

Our interpretation: the [forecasting module](../../methodology/mathematical-framework.md#2-forecasting-and-uncertainty) could use residual calibration around demand forecasts before comparing allocation decisions under uncertainty. This complements the [hierarchical forecasting review](2024-olivares-hierarchical-poisson-mixtures.md): calibration and aggregation coherence are different properties. EnbPI is not implemented here.

## Limitations

The main bound assumes stationary, strongly mixing errors with a Lipschitz CDF and improving estimator accuracy; arbitrary demand shifts or discrete counts do not automatically satisfy these conditions. Marginal intervals do not guarantee simultaneous coverage across sites or horizons. Energy experiments do not establish tourism performance, and interval inputs alone do not make the allocator robust.

## Proposed Next Step

Compare rolling EnbPI intervals with fixed residual intervals around the same bootstrap demand predictor on chronological tourism data. Update residuals only after outcomes become available. Report coverage and width by horizon, site, and peak period, with a separate synthetic abrupt-shift stress test. Any allocation comparison must specify how intervals change decisions. This experiment is proposed.
