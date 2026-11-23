# A national model for estimating United States public land visitation

**Citation** — Nathaniel H. Merrill, Samantha G. Winder, Dieta R. Hanson, Spencer A. Wood, and Eric M. White (2025). *Scientific Reports*, 15, 42764. Published journal article. [DOI and research record](https://research.fs.usda.gov/treesearch/69988), DOI 10.1038/s41598-025-26926-w.

**Reviewed 2026-11-23.** Published full text, Model transferability methods, Cross validation results, Tables 2–4, and Discussion. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12663154/)

## Findings

The authors estimated monthly recreation visits using ground counts for calibration, digital mobility proxies, and site and seasonal covariates. Their all-sources model had about 31% mean absolute percentage error in visit counts when randomly selected unit-months were withheld at calibrated sites, compared with about 85% when entire sites were withheld across the three agencies. Transfer between agencies also performed poorly.

## Relevance to This Repository

Our interpretation is that the forecasting and monitoring modules should evaluate how much a proxy improves estimates at sites with local counts, then test transfer to sites without that calibration. [Forecasting framework](../../methodology/mathematical-framework.md#2-forecasting-and-uncertainty)

## Limitations

The random month holdout measures reconstruction across observed periods. It does not establish forward forecast accuracy or show that each proxy arrives before an allocation decision. Proxy coverage and official counting methods vary by site.

## Proposed Next Step

Compare a seasonal baseline with a model using a reusable, aggregated proxy. Emulate missing historical months and separately test chronological forecasting with a release lag. Report park-level MAE in both tests and stratify by whether local calibration counts were available. This experiment is proposed.
