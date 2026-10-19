# Demand Estimation Using Managerial Responses to Automated Price Recommendations

**Citation:** Daniel Garcia, Juha Tolvanen, and Alexander K. Wagner (2022). *Management Science*, 68(11):7918-7939. Published journal article. [DOI: 10.1287/mnsc.2021.4261](https://doi.org/10.1287/mnsc.2021.4261).

**Reviewed:** 2026-10-19. [Publisher full text](https://pubsonline.informs.org/doi/10.1287/mnsc.2021.4261): data description, Sections 3.1 and 3.3-3.4, and results in Sections 4-4.1 and 5.1.

## Findings

Using bookings, recommended prices, and charged rates from nine hotels over about 14 months, the authors estimate price sensitivity with a control-function approach and post-double-selection LASSO. Identification exploits delayed managerial price adjustments. Omitting recommendations can yield misleading positive price-demand coefficients; recommendation-aware estimates are supported by a pooled difference-in-differences check.

## Relevance to This Repository

Our interpretation: the [dynamic-pricing module](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making) needs price-response estimates, not merely booking forecasts. Log recommendations, implemented prices, decision times, inventory, and context separately to support later identification. This estimator is not implemented here.

## Limitations

Causal interpretation requires recommendations to capture relevant demand information and residual price variation to be conditionally unrelated to demand shocks. LASSO alone does not establish these assumptions. Hotel evidence does not validate attraction pricing or demonstrate reinforcement-learning policy gains.

## Proposed Next Step

Simulate bookings with known price effects and delayed price updates. Compare naive regression with recommendation-aware double selection, measuring coefficient bias and interval coverage. Repeat with managers reacting to unlogged demand shocks to test sensitivity to violated assumptions before evaluating pricing policies.
