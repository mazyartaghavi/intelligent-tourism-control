# Observed visitation and simulated allocation — 22 November 2026

The benchmark uses monthly recreation visits for Acadia (ACAD), Shenandoah (SHEN), and Great Smoky Mountains (GRSM). The three parks span different visitation volumes. The [included 192-month panel](../../data/processed/nps-recreation-visits-2010-2025.csv) is a subset of the National Park Service’s 2025 Visitor Use Statistics Data Package (Ziesler, 2026, DOI 10.57830/2317666). The [catalog](https://irma.nps.gov/DataStore/Reference/Profile/2317666) identifies the release as CC0. We selected Total Recreation Visits (TRV) from the [official CSV](https://irma.nps.gov/DataStore/DownloadFile/756959?Reference=2317666). The observations are published visit estimates, and repeat visits are possible. They measure visits under actual access conditions. The source does not supply unconstrained demand, occupancy, or the operational costs and capacities in this benchmark. [NPS definitions and reporting timing](https://www.nps.gov/subjects/socialscience/statistics-faq.htm)

## Forecast results

Set aside 2010–2018 for initial history and capacity calibration, 2019–2021 for method selection, and 2022–2025 for test. Three-month forecasts are issued at the start of each calendar quarter using records through the second preceding month. This models the ordinary report delay, since the previous month's values are usually published after the new month starts. The experiment uses one finalized data release. Historical release vintages and actual reporting delays for individual parks were unavailable. The validation period includes the pandemic disruption. Each forecast method is fixed in advance. Select one by validation MAE and report all three test scores.

| Forecast | Validation MAE | Test MAE | Test RMSE |
|---|---:|---:|---:|
| Latest available month | 299,229 | 288,347 | 386,898 |
| Same month last year | 97,365 | 37,223 | 64,008 |
| Mean of same month in last three years | 83,381 | 47,924 | 78,304 |

Errors are in visits per park-month, pooled over 144 test forecast targets. The three-year mean won validation. The previous-year seasonal forecast had the lowest held-out MAE in each park and the lowest pooled test RMSE. The differing performance across splits could reflect changing demand patterns. The [forecast metrics](forecast_metrics.csv) retain park-level results.

## Counterfactual allocation

Treat each recorded visit as a proxy for one request. Set each park's monthly service ceiling to 110% of the same calendar month's median visits in 2010–2018. Give policies the same shared budget of 65% of the sum of local ceilings. Use the existing synthetic site-priority, operating, and change coefficients. Each policy plans a whole quarter at once, starts from the last period’s commitment, and incurs realized objective costs against the recorded visit proxy. The optimizer tests all three forecasts. The proportional comparator uses the validation-selected forecast.

| Policy | Weighted cost (million objective units) | Served (million visit equivalents) |
|---|---:|---:|
| Proportional, three-year mean | 121.09 | 40.74 |
| Optimizer, persistence | 129.27 | 34.90 |
| Optimizer, previous-year seasonal | 104.30 | 40.05 |
| Optimizer, three-year mean | 104.43 | 40.03 |

Using the same forecast, the optimizer had **13.8% lower weighted cost** than proportional allocation and served fewer visit equivalents. The optimizer with previous-year seasonal forecasts had the lowest total cost, but its advantage over the three-year mean was about **0.13%**. That comparison reversed in the final two years. All 16 policy-year records passed feasibility, with a maximum residual of about 2.33e-10 against the 1e-7 tolerance. These are descriptive results for one contiguous holdout. The three parks and four years do not represent independent replications. The capacity decisions and outcomes are simulated, so the percentage changes do not establish operational savings.

## Reproduce

Use Python 3.13 with the repository's [locked dependencies](../../requirements-milestone-lock.txt).

```sh
python scripts/evaluation/run_observed_visitation.py --output reports/local-reproduction/observed-visitation
python -m unittest discover -s tests/unit -p test_observed_visitation.py
```

To re-extract the subset, download the official CSV and run the same script with `--source-csv` and `--panel` pointing to a new output CSV. It checks the upstream SHA-256. The [machine-readable summary](results.json) records both data fingerprints, allocation settings, and realized feasibility. [Annual allocation metrics](annual_allocation.csv)
