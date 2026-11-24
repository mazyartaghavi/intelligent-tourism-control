# Customized Regression Model for Airbnb Dynamic Pricing

**Citation** — Peng Ye, Julian Qian, Jieying Chen, Chen-Hung Wu, Yitong Zhou, Spencer De Mars, Frank Yang, and Li Zhang (2018). *KDD*, 932–940. Published proceedings paper. [DOI 10.1145/3219819.3219830](https://doi.org/10.1145/3219819.3219830).

**Reviewed 2026-11-24.** Sections 1.2, 2.1, 4.1–4.3, and 5.1–5.2, including Table 2. [Mirror of the published full text](https://manuals.plus/m/2097592a92b0f8310cba730645557b3110ff0844b0e6c4d95ecb6b085ce2efc4.pdf)

## Findings

A booking-probability model feeds a listing-specific price regressor. Its loss is zero inside a heuristic interval derived from the historical price and whether the night was booked. Compared with direct revenue maximization using the estimated demand curve, the regressor improved price-decrease recall on all three offline samples. Booking regret worsened in sample (a), the short high-season evaluation window.

## Relevance to This Repository

Our interpretation is that bounded price adjustments could provide a conservative comparator when bookings are sparse and demand curves are uncertain. Distinguish the suggested price from the price actually offered when adoption is partial. [Pricing framework](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making)

## Limitations

Historical prices and booking labels do not identify the outcome at a different price. The offline metrics measure agreement with directional price heuristics. Section 5.2 gives qualitative online results without effect sizes or enough detail to reproduce the test.

## Proposed Next Step

Simulate listing-nights with known price response and partial adoption. Compare bounded adjustments with direct revenue maximization using the same estimates. Report realized revenue, booking rates, and price changes as response estimates become noisier. This experiment is proposed.
