# Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting

**Citation:** Bryan Lim, Sercan O. Arik, Nicolas Loeff, and Tomas Pfister. Published in *International Journal of Forecasting* (2021), [DOI](https://doi.org/10.1016/j.ijforecast.2021.03.012). [Author manuscript](https://arxiv.org/abs/1912.09363), first posted in 2019; manuscript version 3 reviewed.

**Reviewed:** 2026-10-17. [Full text](https://arxiv.org/pdf/1912.09363), architecture, quantile objective, and Sections 6.1-6.5.

## Findings

TFT combines recurrent processing, attention, variable selection, and gating for multi-horizon quantile forecasting. It distinguishes static features, known future inputs, and historically observed inputs. Experiments report improved quantile losses against the evaluated alternatives on electricity, traffic, retail, and volatility datasets.

## Relevance to This Repository

Our interpretation: the input structure suits forecasts combining location descriptors, scheduled events, historical demand, and monitoring observations. Quantiles could inform uncertainty-aware allocation; this extends the [forecasting specification](../../methodology/mathematical-framework.md#2-forecasting-and-uncertainty).

## Limitations

These benchmarks do not establish tourism-demand performance. Attention weights are not causal explanations, and estimated quantiles require calibration checks before informing resource decisions.

## Proposed Next Step

Compare TFT with seasonal-naive and simpler learned forecasts using chronological splits, quantile loss, interval coverage, and downstream allocation outcomes.
