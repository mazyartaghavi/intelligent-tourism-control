# Modeling Price Elasticity for Occupancy Prediction in Hotel Dynamic Pricing

**Citation:** Fanwei Zhu, Wendong Xiao, Yao Yu, Ziyi Wang, Zulong Chen, Quan Lu, Zemin Liu, Minghui Wu, and Shenghua Ni (2022). *CIKM 2022*. Published conference paper. [DOI: 10.1145/3511808.3557646](https://doi.org/10.1145/3511808.3557646).

**Reviewed:** 2026-11-16. [Author manuscript, arXiv:2208.03135v2](https://arxiv.org/html/2208.03135v2), Sections 2 and 3, including Tables 2-4. Citation checked against publisher-deposited metadata; findings below refer to this manuscript.

## Findings

PEM models occupancy as $O=\bar O(P/\bar P)^{-\beta}$, learning elasticity from competitor representations and temporal features with joint room/hotel training. Candidate prices maximize predicted margin times occupancy. Table 2 reports Dataset-H WMAPE of 39.03% for PEM versus 39.22% for TFT. A two-week Fliggy test reports 7.42% higher daily GMV than manual pricing, but omits experimental details.

## Relevance to This Repository

Our interpretation: the [pricing module](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making) could compare explicit elasticity curves with direct demand prediction. This complements the later [PCANet review](2024-zhu-hotel-demand-pricing.md); neither model is implemented here.

## Limitations

Predictive elasticity is not automatically causal. The manuscript's Equation 2 does not enforce inventory. Online assignment and uncertainty are unspecified; GMV is not profit. Section 3.3's percentage-change prose does not agree with Table 4, so its numerical ablation claims are not adopted here.

## Proposed Next Step

In a synthetic hotel simulator with known elasticity, compare fixed and learned elasticity under identical price bounds and inventory limits. Separate held-out demand error, elasticity recovery, profit, and rejected bookings across seeds and demand shifts. This experiment is proposed.
