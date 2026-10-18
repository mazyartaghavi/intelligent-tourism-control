# Free Lunch Enhancements for Multi-modal Crowd Counting

**Citation:** Haoliang Meng, Xiaopeng Hong, Zhengqin Lai, and Miao Shang. Published in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)* (2025), pp. 14013-14023. [Conference record](https://openaccess.thecvf.com/content/CVPR2025/html/Meng_Free_Lunch_Enhancements_for_Multi-modal_Crowd_Counting_CVPR_2025_paper.html), identifier: `Meng_2025_CVPR`.

**Reviewed:** 2026-10-18. [Full text](https://openaccess.thecvf.com/content/CVPR2025/papers/Meng_Free_Lunch_Enhancements_for_Multi-modal_Crowd_Counting_CVPR_2025_paper.pdf), Sections 3-4 and Tables 1-3.

## Findings

The authors combine contrastive cross-modal alignment before fine-tuning with regional density supervision derived from existing point annotations. These training enhancements leave inference architecture unchanged. On DroneRGBT, their broker-modality (BM) framework with Swin-T achieves count RMSE of 7.81, compared with 10.40 for BM in Table 1.

## Relevance to This Repository

Our interpretation: this is a candidate for [UAV-assisted monitoring](../../../README.md#1-uav-assisted-tourism-monitoring), supplying crowd observations to forecasting and capacity decisions. An image count is neither future arrival demand nor interval service capacity; these quantities need separate modeling. The method is not implemented here.

## Limitations

Image benchmarks do not establish live tourism-control performance. Additional training is still required. Improvements are not universal: ShanghaiTechRGBD RMSE rises from 5.28 for BM to 5.38 for the proposed method (Table 2). Transfer to new camera locations and illumination conditions requires evaluation.

## Proposed Next Step

Compare RGB-only, BM, and BM with the two enhancements on held-out paired images. Report count MAE, RMSE, regional errors, and undercount bias by illumination; then test how measured sensing errors affect occupancy estimates in a separate admission-control simulation.
