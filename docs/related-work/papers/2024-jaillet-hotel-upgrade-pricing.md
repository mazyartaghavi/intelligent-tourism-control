# When Should you Offer an Upgrade: Online Upgrading Mechanisms for Resource Allocation

**Citation.** Patrick Jaillet, Chara Podimata, Andrew Vakhutinsky, and Zijie Zhou (2024). Presented at the 20th Conference on Web and Internet Economics. [WINE 2024 program](https://wine2024.org/) and [arXiv record 2402.08804](https://arxiv.org/abs/2402.08804).

**Reviewed 2026-11-11.** Sections 4.2, 5 and 6, including Algorithm 3 and Table 1 of the [full author manuscript, version 1](https://arxiv.org/html/2402.08804v1).

## Findings

DynUp-n uses remaining inventory and expected arrivals to decide how much to charge for upgrading a booking to the next room category. The authors fitted upgrade acceptance curves using 13,155 recorded offers. In a three-category simulation with 100 arrival orders per day, DynUp-n earned about 17% more annual revenue than first-come, first-served booking at the recorded upgrade fees.

## Limitations

The simulation assumes single-night stays and constructs arrival-rate estimates using each day's realized request totals plus random variation. A hotel making advance offers would have to forecast those totals. The revenue comparison also combines the effects of pricing and inventory decisions.

## Relevance to This Repository

Our interpretation is that each accepted upgrade earns a fee and uses a room that could serve a later premium booking. Tracking both outcomes would extend the [proposed pricing module](../../methodology/mathematical-framework.md#4-dynamic-pricing-as-sequential-decision-making).

## Proposed Next Step

Estimate arrival rates from earlier dates only. Replay identical booking requests under fixed and inventory-dependent upgrade fees, holding admission rules constant. Report revenue, displaced premium requests and unused rooms by category, then repeat with more last-minute premium demand.
