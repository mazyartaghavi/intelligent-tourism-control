# Detection, Tracking, and Counting Meets Drones in Crowds: A Benchmark

**Citation:** Longyin Wen, Dawei Du, Pengfei Zhu, Qinghua Hu, Qilong Wang, Liefeng Bo, and Siwei Lyu (2021). Published conference paper, *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*. [DOI: 10.1109/CVPR46437.2021.00772](https://doi.org/10.1109/CVPR46437.2021.00772).

**Reviewed:** 2026-10-24. [Full-text author manuscript, arXiv:2105.02440v1](https://arxiv.org/html/2105.02440v1), Sections 3-5 and Tables 3-5.

## Findings

DroneCrowd provides annotated aerial videos for counting, localization, and tracking, with 82 training sequences and 30 test sequences from different locations. STNNet jointly learns density, localization, and association using neighboring motion relationships. On the test set, Table 3 reports overall count MAE of 15.8 for STNNet versus 18.4 for DM-Count.

## Relevance to This Repository

Our interpretation: [UAV-assisted monitoring](../../../README.md#1-uav-assisted-tourism-monitoring) should assess aggregate counts and trajectory quality separately. Accurate totals can conceal incorrect spatial assignments or broken tracks. Neither repeated image counts nor trajectory fragments directly measure unique arrivals. This method is not implemented here.

## Limitations

STNNet does not lead every counting subset; CAN performs better on crowded scenes. The authors identify tracking as unresolved. Image coordinates require camera-motion compensation and spatial calibration before estimating physical-zone occupancy. These benchmarks do not establish reliable tourism admission control.

## Proposed Next Step

Compare STNNet and DM-Count on the official sequence split, reserving training sequences for tuning. Report count MAE and bias by illumination and density, plus localization and tracking metrics under matched association rules. In a separate simulation, inject measured count errors into occupancy observations and measure missed capacity exceedances and unnecessary admission rejections.
