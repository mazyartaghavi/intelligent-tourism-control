# NWPU-Crowd: A Large-Scale Benchmark for Crowd Counting and Localization

**Citation** — Qi Wang, Junyu Gao, Wei Lin, and Xuelong Li (2021). *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 43(6), 2141–2149. Published journal article. [DOI 10.1109/TPAMI.2020.3013269](https://doi.org/10.1109/TPAMI.2020.3013269).

**Reviewed 2026-11-25.** Sections 3.3 and 4.2–4.6, including Tables 4–5, in the [author-hosted full text](https://crabwq.github.io/pdf/2020%20NWPU-Crowd%20A%20Large-Scale%20Benchmark%20for%20Crowd%20Counting%20and%20Localization.pdf).

## Findings

The benchmark includes 351 person-free images such as empty halls and repeated textures that resemble crowds. In a validation comparison using C3F-VGG, mean absolute error on person-free images was 18.54 people when training used person-free and low-density examples, versus 147.53 when training paired person-free examples with the two highest-density groups. The test leaderboard also shows that performance varies sharply with density and lighting.

## Relevance to This Repository

Our interpretation is that crowd monitoring needs an explicit false-count test on unoccupied paths and plazas. False counts there could trigger unnecessary capacity alerts even when aggregate error looks acceptable. [UAV-assisted monitoring design](../../../README.md#1-uav-assisted-tourism-monitoring)

## Limitations

The training comparison changes the composition of the positive examples, so the two errors do not isolate the effect of density alone. Still-image counts do not measure arrivals or establish performance on aerial sequences or mapped zones.

## Proposed Next Step

Compare the same counting model with and without difficult person-free training examples, holding positive data and training steps fixed. On scenes from held-out camera sites, report false-alert rates for empty scenes and missed exceedances for crowded scenes by lighting condition. This experiment is proposed.
