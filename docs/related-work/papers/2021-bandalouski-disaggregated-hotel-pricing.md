# Dynamic pricing with demand disaggregation for hotel revenue management

**Citation:** Andrei M. Bandalouski, Natalja G. Egorova, Mikhail Y. Kovalyov, Erwin Pesch, and S. Armagan Tarim (2021). *Journal of Heuristics*, 27:869-885. Published journal article. [Publisher record; DOI: 10.1007/s10732-021-09480-2](https://link.springer.com/article/10.1007/s10732-021-09480-2).

**Reviewed:** 2026-10-25. Publisher full-text Sections 1, 3-8, especially the demand assumptions, optimization equations (4)-(11), and simulation design.

## Findings

The approach segments bookings, forecasts category demand, and maximizes a concave quadratic profit objective under linear price and capacity constraints. Experiments using altered data from one hotel report higher modeled revenue than historical fixed pricing. Simulated demand varies within 5% of the fitted linear response.

## Relevance to This Repository

Our interpretation: this provides a candidate optimization baseline for the [dynamic-pricing module](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making). Separate demand forecasts at reference prices, response slopes, and shared room inventory. Category detail should be tested against data sparsity. This method is not implemented here.

## Limitations

The model assumes uncorrelated category demands and linear price responses. Historical price regressions do not establish causal response; the authors acknowledge endogeneity. Simulation gains are not field evidence. Constraints on predicted demand do not guarantee that realized bookings respect capacity.

## Proposed Next Step

Build a synthetic single-hotel benchmark comparing fixed prices with the quadratic optimizer under coarse and fine segmentation. Use identical demand draws, then perturb response slopes and introduce substitution between categories. Report revenue, profit, rejected requests, and infeasible optimization instances under tighter price bounds. Enforce booking inventory independently, including every occupied night.
