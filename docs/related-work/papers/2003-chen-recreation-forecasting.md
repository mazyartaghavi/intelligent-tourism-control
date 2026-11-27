# An Evaluation of Alternative Forecasting Methods to Recreation Visitation

**Citation** — Rachel J. C. Chen, Peter Bloomfield, and Joshua S. Fu (2003). *Journal of Leisure Research*, 35(4), 441–454. Published journal article. [DOI 10.1080/00222216.2003.11950005](https://doi.org/10.1080/00222216.2003.11950005).

**Reviewed 2026-11-27.** [Full text](https://csbt.tennessee.edu/pubs/pdf/ForecastingSiteUse.pdf), Case Study, Forecasting Results (Table 1), Conclusion, and Appendix B.

## Findings

The authors compare seven methods using 228 monthly zoo attendance observations. They exclude the final 12, 24, or 60 months from model estimation. In Table 1, SARIMA ranks first by the authors' modified percentage-error measures in the 12-month configuration. A moving average with seasonal decomposition ranks first in the 24- and 60-month configurations.

## Relevance to This Repository

Our interpretation is that a seasonal decomposition baseline is worth comparing with simpler seasonal forecasts before adding more complex models. Model rankings should be measured at the actual planning horizon. [Forecasting framework](../../methodology/mathematical-framework.md#2-forecasting-and-uncertainty)

## Limitations

Appendix B pools estimation-period one-step errors with errors on future observations. Consequently the published rankings do not isolate held-out accuracy, and the compared configurations vary both history length and horizon. The results concern one recreation site.

## Proposed Next Step

Compare a seasonal-naive model, seasonal averaging, and a decomposition model at matched chronological forecast origins and matched history lengths using multiple parks. Report held-out MAE separately by lead and site, and evaluate downstream allocation cost under common capacity assumptions. This experiment is proposed.
