# Probabilistic Hierarchical Forecasting with Deep Poisson Mixtures

**Citation:** Kin G. Olivares, O. Nganba Meetei, Ruijun Ma, Rohan Reddy, Mengfei Cao, and Lee Dicker (2024). *International Journal of Forecasting*, 40(2):470-489. Published journal article. [DOI: 10.1016/j.ijforecast.2023.04.007](https://doi.org/10.1016/j.ijforecast.2023.04.007).

**Reviewed:** 2026-10-21. [Full-text author manuscript, arXiv:2110.13179v8](https://arxiv.org/html/2110.13179v8), Sections 3-4, 6.1-6.6, and 7; Table 3.

## Findings

DPMN combines neural forecasts with a joint Poisson mixture whose aggregation rules ensure probabilistic coherence. Group-based composite likelihood learns within-group dependencies. On monthly Australian Tourism-L data, with a 12-month test horizon, Table 3 reports overall mean scaled CRPS of 0.1249 for DPMN-GroupBU versus 0.1472 for HierE2E, averaged over eight runs; lower is better.

## Relevance to This Repository

Our interpretation: the [forecasting module](../../methodology/mathematical-framework.md#2-forecasting-and-uncertainty) could generate joint demand scenarios consistent across locations and regional totals. Define non-overlapping counting units first; summed service events are not necessarily unique visitors. This method is not implemented here.

## Limitations

GroupBU did not improve forecasts on the randomly grouped traffic benchmark. Finite mixtures and cross-group component matching can misrepresent uncertainty. Monthly tourism evidence does not validate real-time crowd forecasts. Aggregation coherence is distinct from calibration and operational capacity compliance.

## Proposed Next Step

Compare DPMN-GroupBU, DPMN-NaiveBU, and a seasonal-naive probabilistic baseline on Tourism-L using rolling forecast origins. Measure CRPS, interval coverage and width, and sampled aggregation residuals by level. Repeat with shuffled groups to test dependence on meaningful structure. Keep tuning strictly before each test window.
