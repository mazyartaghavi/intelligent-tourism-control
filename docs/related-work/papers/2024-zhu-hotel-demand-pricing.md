# Dynamic Hotel Pricing at Online Travel Platforms: A Popularity and Competitiveness Aware Demand Learning Approach

**Citation:** Fanwei Zhu, Wendong Xiao, Yao Yu, Zemin Liu, Zulong Chen, and Weibin Cai (2024). *Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining*. Published conference paper. [Conference record](https://kdd.org/kdd2024/research-track-papers/); DOI: `10.1145/3637528.3671921`.

**Reviewed:** 2026-11-04. [Author-uploaded full text](https://www.researchgate.net/publication/383413862_Dynamic_Hotel_Pricing_at_Online_Travel_Platforms_A_Popularity_and_Competitiveness_Aware_Demand_Learning_Approach), Sections 3, 4.1, and 5.2.

## Findings

PCANet learns popularity and competitiveness coefficients through joint room- and group-level occupancy prediction, then derives prices from a demand curve. In a two-week Fliggy online A/B test against a gradient-boosted demand-curve baseline, the authors report 11.39% higher gross merchandise volume (GMV).

## Relevance to This Repository

Our interpretation: the [pricing module](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making) could test group-level learning when room-level bookings are sparse. Preserve price bounds and enforce room-night inventory separately. PCANet is not implemented here.

## Limitations

One platform's short test does not establish long-term or attraction-pricing benefits. Section 5.2 gives limited detail on assignment and uncertainty. Predictive coefficients alone do not establish causal price elasticity; GMV also differs from profit.

## Proposed Next Step

Build a synthetic hotel-group benchmark with known substitution effects and sparse bookings. Compare joint room/group training with room-only prediction under matched data and capacity limits. Evaluate held-out demand and shifted competitor prices, reporting prediction error, revenue, rejected bookings, and inventory violations across seeds. This experiment is proposed.
