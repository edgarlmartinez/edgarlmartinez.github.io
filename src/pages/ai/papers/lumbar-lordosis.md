---
layout: ../../../layouts/Paper.astro
title: Why automated L1–S1 lordosis fails on a public lateral lumbar radiograph dataset, a negative-result technical note
short: Lumbar lordosis technical note
description: Preprint draft. Three approaches to automated L1–S1 lordosis on public lateral lumbar radiographs, and why none was accurate enough to release.
authors: Edgar L. Martinez Salazar, MD, and research fellow (author list to be finalized). Department of Radiology, Beth Israel Deaconess Medical Center, Harvard Medical School, Boston, MA.
updated: November 2026
---

## Abstract

**Purpose:** To test whether L1–S1 lumbar lordosis can be measured automatically on lateral lumbar radiographs with a small model trained on a public dataset, and to report why it failed.

**Materials and Methods:** Lateral lumbar radiographs from the public Spondylolisthesis Vertebral Landmark dataset (BUU-LSPINE images; CC BY 4.0) with at least 6 labeled vertebral bodies were used, with the publisher's split (192 test images). Three approaches were compared: (A) a direct 4-point heatmap network for the L1 and S1 superior endplates, trained from scratch on a CPU; (B) a vertebral corner detector (from the companion vertebral morphometry model) taking the lowest detected body as S1 and counting up 5 levels to L1; and (C) a combination that chose S1 as the detected body nearest approach A's S1 estimate. Outcomes were correct-level rate and L1–S1 angle error.

**Results:** Reference lordosis was 32.6° ± 12.8°. Approach A found the correct L1 in 41% of images (median L1 point error about 50 px, against 5–9 px for S1); its mean angle error was 21.3°, with no correlation with the reference (r = 0.04). Approach B identified both levels correctly in 55% of usable images (mean error 12.1°). Approach C did best: both levels correct in 65%, mean error 11.0°, 60% within 10°, r = 0.47. Even with both levels correct, mean error was 8.1° with a +6.6° bias.

**Conclusion:** Automated lordosis on this dataset fails mainly from level identification, and secondly from a systematic S1 endplate error caused by how S1 is labeled. The model was not released.

**Keywords:** lumbar lordosis; landmark detection; vertebral level identification; negative result; lateral radiograph; open data

## 1. Introduction

Lumbar lordosis, usually measured as the Cobb angle between the L1 and S1 superior endplates, is a core parameter of sagittal spinal alignment, measured routinely before and after spinal surgery and in deformity assessment. Manual measurement takes time and varies between readers, so automation is attractive.

The angle depends on two things: choosing the correct vertebral levels, and placing each endplate line accurately. We tested whether a small model trained on a public dataset could measure lordosis well enough to add to an open measurement toolkit.

**Objectives**

1. Train and evaluate a direct L1–S1 endplate landmark model on public data with a CPU.
2. Compare it with level counting by a vertebral corner detector.
3. Identify the causes of failure, to guide future work.

## 2. Materials and methods

### 2.1 Data

Spondylolisthesis Vertebral Landmark dataset (Mendeley Data, doi:10.17632/5jdfdgp762.1; CC BY 4.0). Only BUU-LSPINE images (Burapha University) were used, because they follow one orientation convention. The publisher had resized all images to 640 × 640, and each vertebral body is labeled with 4 corners. Images with at least 6 labeled bodies were kept; the lowest body was taken as S1 and the sixth from the bottom as L1. The publisher's training split was used for training and its validation split (192 images) for testing. The reference lordosis is the angle between the L1 and S1 superior endplate lines, each defined by the two most superior corners.

### 2.2 Approach A: direct 4-point model

The same small U-Net as the infant hip model (about 1.1 million parameters), trained from random initialization to output 4 heatmaps (L1 and S1 anterior and posterior superior corners). Input letterboxed to 384 × 384. Augmentation: rotation ±15°; scale 0.8–1.3; horizontal aspect-ratio jitter 0.65–1.1; translation; mirroring; gamma, contrast, blur, noise; inversion in 10%. Penalty-reduced focal heatmap loss; AdamW (2 × 10⁻³, weight decay 10⁻⁴); one-cycle schedule; batch 8; 4 CPU threads. Flip test-time augmentation and a 5 × 5 weighted-centroid decode.

### 2.3 Approach B: count from the lowest detected body

The vertebral corner detector from the [vertebral morphometry model](/ai/papers/vertebral-morphometry/) was run on each image. The lowest detected body was taken as S1 and the fifth body above it as L1. Images with fewer than 6 detected bodies were not usable.

### 2.4 Approach C: combined

S1 was taken as the detected body whose superior endplate midpoint was nearest to approach A's S1 estimate, and L1 as the fifth body above it.

### 2.5 Evaluation

A level was correct if the predicted endplate midpoint lay within 40% of that level's reference endplate width of the reference midpoint. Angle error is reported as mean, median and 90th percentile absolute error, share within 5° and 10°, bias and Pearson r, for all usable images and for images with both levels correct.

### 2.6 Computing environment and AI assistance

4-core x86-64 CPU, no GPU; Python 3 with PyTorch, OpenCV and NumPy. Software development was assisted by a large language model coding agent (Claude Code, Claude Opus 5.5; Anthropic), under the radiologist's direction and review.

## 3. Results

Reference lordosis in the 192 test images was 32.6° ± 12.8° (median 32.3°, range 0–77°).

| Measure | A: direct model | B: count from lowest body | C: combined |
|---|---|---|---|
| Usable images | 192 | 187 | 178 |
| Correct L1 | 41% | 66% | 66% |
| Correct S1 | 74% | 57% | 68% |
| Both correct | 31% | 55% | 65% |
| MAE, all usable | 21.3° | 12.1° | 11.0° |
| Median absolute error, all | 15.0° | 10.2° | 8.5° |
| 90th percentile, all | 50.7° | 24.9° | 23.0° |
| Within 5° / 10°, all | 30% / 41% | 28% / 49% | 32% / 60% |
| Bias, all | +13.5° | −1.5° | +1.2° |
| Pearson r | 0.04 | 0.44 | 0.47 |
| MAE, both levels correct | 19.8° (n = 60) | 7.6° (n = 102) | 8.1° (n = 115) |
| Within 10°, both correct | 42% | 73% | 71% |
| Bias, both correct | +13.7° | +6.0° | +6.6° |

**Point error of the direct model (median, 640-px image):** L1 anterior 53.2 px, L1 posterior 50.0 px, S1 anterior 8.6 px, S1 posterior 5.4 px. The direct model located S1 reasonably but usually placed L1 on the wrong vertebra. With the corner detector, the main failure moved to S1 identification.

## 4. Discussion

Automated L1–S1 lordosis on this dataset failed for two separate reasons: finding the right vertebrae, and drawing the S1 endplate correctly.

**Level identification.** A direct landmark model cannot count. L1 looks much like T12 and L2, so the model often placed L1 a level off, and its angle errors were essentially random. Counting from a vertebral detector helped but transferred the problem to S1. Anchoring on the direct model's S1 estimate gave the best result, with both levels correct in 65% of images, still far below what a measurement tool needs.

**Systematic S1 error.** With both levels correct, a bias of about +6° remained. In this dataset S1 is labeled as a box around the sacral body, not along the sacral endplate, so the corner-derived S1 line does not match the true endplate slope. More training alone will not fix this.

**Data limits.** Only a few hundred training images had L1 to S1 labeled, and all had been squashed to 640 × 640, distorting angles before any model saw them. The full-resolution BUU-LSPINE release should address both problems.

## 5. Limitations

- One public dataset, with images distorted by the publisher's resizing.
- A longer training schedule was not tested.
- Levels were assigned by counting from the bottom of the labeled bodies, not by an independent reader.
- Transitional lumbosacral anatomy was not considered.
- No comparison with human inter-reader agreement on these images.

## 6. Conclusion

On a public, resized lateral lumbar dataset, small models could not measure L1–S1 lordosis reliably. The best approach chose both levels correctly in 65% of images, with a mean error of 11°. Level identification is the main obstacle, and box-style S1 labels add a systematic error of about 6°. Full-resolution images with endplate-level sacral labels are needed before this is worth retrying.

## Data and code availability

A summary is published in the [toolkit model notes](https://github.com/edgarlmartinez/edgarlmartinez.github.io/tree/main/public/toolkit/models). Training and evaluation scripts will be released with the final paper.

## References

1. Spondylolisthesis Vertebral Landmark dataset (BUU-LSPINE images, Burapha University). Mendeley Data. doi:10.17632/5jdfdgp762.1.
2. Ronneberger O, Fischer P, Brox T. U-Net: convolutional networks for biomedical image segmentation. MICCAI. 2015.
3. Lin TY, Goyal P, Girshick R, He K, Dollár P. Focal loss for dense object detection. ICCV. 2017.
4. Zhou X, Wang D, Krähenbühl P. Objects as points. arXiv:1904.07850. 2019.

*Preprint draft for open review. Not peer reviewed. Research use only; not for clinical use.*
