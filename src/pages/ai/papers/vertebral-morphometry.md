---
layout: ../../../layouts/Paper.astro
title: Automated vertebral morphometry and retropulsion estimation on lateral spine radiographs using a landmark network trained on CT-simulated and public radiographs
short: Vertebral morphometry paper
description: Preprint draft. A small landmark network for vertebral height loss, Genant grade and retropulsion on lateral spine radiographs, trained on VerSe CT-simulated radiographs and public lumbar radiographs.
authors: Edgar L. Martinez Salazar, MD, and research fellow (author list to be finalized). Department of Radiology, Beth Israel Deaconess Medical Center, Harvard Medical School, Boston, MA.
updated: November 2026
---

## Abstract

**Purpose:** To develop an open landmark network for vertebral morphometry on lateral spine radiographs, trained without manual annotation of radiographs, and to evaluate height measurement, Genant grading and retropulsion estimation.

**Materials and Methods:** Reference landmarks were derived automatically from vertebra masks of 34 VerSe 2019 spine CTs (26 training, 8 test). The CTs were projected into simulated lateral radiographs. A 0.5-million-parameter CenterNet-style network was trained from scratch on a 4-core CPU to detect each vertebral body and place 7 landmarks (v0.1). It was then fine-tuned with 351 real lateral lumbar radiographs from a public dataset that carries corner labels only (v0.2). A measurement engine computed anterior, middle and posterior heights, height loss against interpolated neighbours, the Genant grade, posterior wall displacement and sagittal canal compromise. Evaluation used 74 gradable levels in 8 held-out simulated cases and 204 held-out real radiographs (1,449 bodies).

**Results:** On simulated radiographs, median landmark error was 1.3–1.8 mm, height mean absolute error (MAE) was 1.5/1.9/1.5 mm (anterior/middle/posterior) and posterior wall displacement MAE was 0.9 mm. Fracture detection (Genant ≥ 1) had a sensitivity of 6/14 (43%) and a specificity of 57/60 (95%), with a linear-weighted kappa of 0.49. All 4 grade 3 fractures were detected, but only 2 of 8 grade 2 and 0 of 2 grade 1. On real radiographs, adding real training images raised detection from 52% to 91% and lowered median corner error from 4.1 to 2.5 px (7.9% of body height).

**Conclusion:** CT-simulated radiographs give accurate, annotation-free landmark training, and a modest number of real radiographs closes most of the domain gap for detection. Severe fractures were found reliably, but mild and moderate deformities were missed, so real labeled fracture data is needed before clinical testing.

**Keywords:** vertebral fracture; morphometry; Genant; digitally reconstructed radiograph; landmark detection; deep learning; open data

## 1. Introduction

Vertebral fractures are the most common osteoporotic fracture, and most are never clinically diagnosed. Many are visible on lateral spine or chest radiographs taken for other reasons. The Genant semiquantitative method grades a fracture by the loss of anterior, middle or posterior vertebral height relative to the expected height (Genant et al., 1993). Quantitative morphometry measures those heights from six points per vertebral body. It is accurate but slow to do by hand.

In trauma, a radiograph also gives a first estimate of posterior wall retropulsion before CT. A tool that places the landmarks and computes heights, grade and posterior wall position automatically, while letting the reader move any point, could speed reporting and improve opportunistic detection.

Training such a model normally needs many radiographs with point-level annotations, which are expensive to produce and rarely public. Spine CT datasets with vertebra masks are public (VerSe; Sekuboyina et al., 2021). Projecting a CT sideways gives a simulated radiograph on which landmarks derived from the masks are exactly known. The question is how well a model trained on such images transfers to real radiographs.

**Objectives**

1. Derive morphometric reference landmarks automatically from public CT vertebra masks.
2. Train a small landmark network on simulated lateral radiographs, without manual radiograph annotation, on a CPU.
3. Measure landmark, height, fracture-grade and retropulsion accuracy against the CT reference on held-out cases.
4. Measure how much a small set of real, corner-labeled radiographs improves detection on real images.
5. Release the model, code and an editable offline viewer.

## 2. Materials and methods

### 2.1 Study design and ethics

Retrospective technical development study on public, de-identified data. No institutional or patient data was used. Test cases were fixed before training.

### 2.2 Data

| Dataset | Use | Size | License |
|---|---|---|---|
| VerSe 2019 spine CT with vertebra masks (Sekuboyina et al., 2021; Löffler et al., 2020) | CT reference landmarks and simulated radiographs | 34 CTs: 26 training, 8 test | CC BY-SA 4.0 |
| Spondylolisthesis Vertebral Landmark, Mendeley Data, doi:10.17632/5jdfdgp762.1 (mostly BUU-LSPINE, Burapha University) | Real lateral lumbar radiographs with 4 corners per body | 698 images; 564 usable: 351 training, 204 test (publisher's validation split) | CC BY 4.0 |

The real images had been resized by the publisher to 640 × 640, distorting the aspect ratio. They have no fracture labels.

### 2.3 CT reference landmarks

Each CT and its mask were reoriented to RAS and resampled to 1-mm isotropic voxels. For each vertebra:

1. A 3-voxel sagittal slab through the vertebra's centroid was taken, and its largest anterior component was kept as the vertebral body; the rest formed the posterior elements.
2. The local craniocaudal axis was estimated from neighbouring centroids and refined with the body's minimum-area bounding rectangle.
3. The four corners were taken as extreme points along the diagonals of the body's normalized local frame. The mid-superior and mid-inferior endplate points were taken at the body's anteroposterior centre.
4. The posterior wall profile was sampled at 7 heights, and the spinolaminar point was taken as the posterior-element voxel nearest the posterior wall midpoint.
5. Vertebrae touching the scan edge were flagged as truncated and not graded.

### 2.4 Simulated radiographs

Each CT was projected laterally with parallel beams through the 1-mm volume, giving 1.0 mm per pixel with no magnification. Attenuation was modeled as a water-relative term plus a bone-weighted term, followed by exponential transmission and percentile windowing. Two versions were made per CT: the whole body, and a ±70-mm slab around the midline. The CT landmarks map exactly onto the image. The 26 training CTs gave 52 images.

### 2.5 Real radiograph labels

Corner order in the source files was inconsistent, so corners were reassigned by geometry: superior and inferior along the local spine axis, then anterior and posterior. For BUU-LSPINE images the anterior side was on the image left. For other-source images, the anterior side came from a vote of the v0.1 model and was kept only when it agreed with the direction of the lordotic curve. Images with fewer than 3 valid bodies, or no agreed side, were excluded (698 to 564). Images were scaled to a working scale of about 1 mm per pixel.

### 2.6 Network

A CenterNet-style (Zhou et al., 2019) U-Net with about 0.5 million parameters, trained from random initialization (no pretrained or foundation model):

- **Encoder:** 5 levels of two 3 × 3 convolutions with batch normalization and ReLU (12, 24, 48, 64, 96 channels), with 2 × 2 max pooling.
- **Decoder:** bilinear upsampling with skip connections, back to stride 2.
- **Heads at stride 2:** a vertebral-centre heatmap; 14 offset channels giving the x and y position of each of the 7 points from the centre; and 7 per-point heatmaps for refinement.

### 2.7 Training

- **Sampling:** random 384 × 192 crops centred near a randomly chosen vertebra, with fractured bodies sampled 5 times as often.
- **Augmentation:** scale 0.75–1.35; rotation ±15°; translation; mirroring; gamma 0.6–1.6; contrast and brightness; Gaussian blur; Gaussian noise; intensity inversion (30%). For real images, aspect-ratio jitter (horizontal scale 0.7–1.05).
- **Loss:** penalty-reduced focal loss (Lin et al., 2017; Zhou et al., 2019) on the centre and point heatmaps, plus 5 × smooth-L1 on the offsets.
- **Optimization:** AdamW, learning rate 2 × 10⁻³, weight decay 10⁻⁴, one-cycle schedule, batch size 8, 4 CPU threads.
- **v0.1:** simulated images only. **v0.2:** fine-tuned from v0.1 with half simulated and half real images per batch; real images supervised only the corners and centres, with loss masks for the other points and for unlabeled levels.

### 2.8 Inference

Flip test-time augmentation of the centre heatmap; peak detection; refinement of each point to the best per-point heatmap response within 5 pixels; duplicate suppression; and rejection of detections far from a robust quadratic fit of the spinal column.

### 2.9 Measurement engine

- **Heights:** anterior (Ha), middle (Hm) and posterior (Hp).
- **Expected normal height:** levels with heights below 80% of the median of nearby levels, or with Ha/Hp or Hm/Hp under 0.75, were flagged. Each level was then compared with heights interpolated from the nearest unflagged vertebrae above and below, weighted by level distance, or taken from one side at the ends.
- **Grade:** maximum percent loss gives the Genant grade (<20% normal; 20–25% grade 1; 25–40% grade 2; >40% grade 3), with morphology (wedge, biconcave or crush).
- **Retropulsion:** posterior wall displacement is the distance of the posterior wall midpoint behind the line joining the adjacent posterior-wall midpoints. Sagittal canal compromise compares the posterior wall to spinolaminar distance with adjacent levels.
- C1, C2 and truncated bodies are not graded. The Python and JavaScript versions of the engine agreed on all 863 VerSe 2019 levels.

### 2.10 Computing environment and AI assistance

4-core x86-64 CPU, no GPU; Python 3 with PyTorch, NumPy, SciPy, OpenCV and nibabel. Software development was assisted by a large language model coding agent (Claude Code, Claude Opus 5.5; Anthropic), under the radiologist's direction and review. The language model labeled no images and is not part of the model.

### 2.11 Evaluation

**Simulated test set (8 CTs).** Point error (mm); MAE of heights, maximum height loss, posterior wall displacement and canal compromise; fracture detection (Genant ≥ 1) sensitivity and specificity; exact and within-one grade agreement; linear-weighted Cohen's kappa.

**Real test set (204 images).** Detection rate (centre within half a body height); extra detections; corner error in working pixels (about 1 mm) and as a percentage of body height; and morphometry from predicted against published corners.

## 3. Results

### 3.1 Simulated test set

The 8 test CTs gave 74 gradable levels (39 thoracic, 35 lumbar). By the CT reference, 60 were normal and 14 fractured (2 grade 1, 8 grade 2, 4 grade 3).

**Landmark error (mm, v0.2)**

| Point | Median | Mean |
|---|---|---|
| Anterior superior | 1.65 | 2.08 |
| Anterior inferior | 1.26 | 1.84 |
| Middle superior | 1.64 | 2.13 |
| Middle inferior | 1.44 | 1.89 |
| Posterior superior | 1.66 | 2.20 |
| Posterior inferior | 1.62 | 1.90 |
| Spinolaminar | 1.78 | 2.11 |

**Measurements**

| Measure | v0.1 | v0.2 |
|---|---|---|
| Ha / Hm / Hp MAE | 1.4 / 2.0 / 1.6 mm | 1.52 / 1.89 / 1.53 mm |
| Maximum height loss MAE | 7.0 points | 7.5 points |
| Posterior wall displacement MAE | 0.9 mm | 0.92 mm |
| Canal compromise MAE | 3.2 points | 3.0 points |
| Sensitivity, Genant ≥ 1 | 6/14 (43%) | 6/14 (43%) |
| Specificity | 59/61 (97%) | 57/60 (95%) |
| Exact grade agreement | 81% | 81% |
| Within one grade | 88% | 91% |
| Linear-weighted kappa | 0.43 | 0.49 |

**Grade confusion (v0.2; rows = predicted, columns = CT reference)**

| Predicted \ Reference | Normal | Grade 1 | Grade 2 | Grade 3 |
|---|---|---|---|---|
| Normal | 57 | 2 | 6 | 0 |
| Grade 1 | 2 | 0 | 1 | 0 |
| Grade 2 | 1 | 0 | 1 | 2 |
| Grade 3 | 0 | 0 | 0 | 2 |

**Every fracture and false positive (v0.2)**

| Case | Level | Reference grade (height loss) | Predicted grade (height loss) |
|---|---|---|---|
| sub-verse004 | L1 | 3 (62%) | 2 (30%) |
| sub-verse056 | L1 | 3 (52%) | 3 (43%) |
| sub-verse105 | T7 | 3 (52%) | 2 (34%) |
| sub-verse122 | T11 | 3 (46%) | 3 (64%) |
| sub-verse061 | L2 | 2 (36%) | 2 (25%) |
| sub-verse122 | T7 | 2 (27%) | 1 (24%) |
| sub-verse056 | T12 | 2 (27%) | normal (16%) |
| sub-verse056 | L2 | 2 (28%) | normal (1%) |
| sub-verse105 | T6 | 2 (27%) | normal (12%) |
| sub-verse105 | T8 | 2 (26%) | normal (13%) |
| sub-verse122 | L1 | 2 (35%) | normal (8%) |
| sub-verse102 | L3 | 2 (37%) | normal (7%) |
| sub-verse061 | L1 | 1 (21%) | normal (16%) |
| sub-verse141 | T11 | 1 (24%) | normal (12%) |
| sub-verse004 | L5 | normal (5%) | 1 (22%) |
| sub-verse056 | L3 | normal (5%) | 2 (29%) |
| sub-verse056 | L4 | normal (6%) | 1 (24%) |

All 4 grade 3 fractures were detected. Only 2 of 8 grade 2 and 0 of 2 grade 1 fractures were detected. Several misses and false positives were next to another fracture, where the expected height comes from neighbours that are themselves deformed or far away.

### 3.2 Real lateral lumbar radiographs (204 images, 1,449 bodies)

| Measure | v0.1 (simulated only) | v0.2 (+ 351 real) |
|---|---|---|
| Bodies detected | 751 (52%) | 1,315 (91%) |
| Extra detections within the labeled span | 259 | 68 |
| Corner error, median | 4.08 px | 2.54 px |
| Corner error, mean | 6.63 px | 5.30 px |
| Corner error, 90th percentile | 14.2 px | 9.31 px |
| Corner error, median % of body height | 13.0% | 7.9% |
| Height loss difference vs published corners, MAE | 6.2 points (712 levels) | 8.7 points (1,315 levels) |
| Genant grade agreement vs published corners | 89% (712 levels) | 80% (1,315 levels) |

v0.1 compared morphometry only on the bodies it detected, which were the easier ones, so those two rows are not directly comparable between versions.

## 4. Discussion

A 0.5-million-parameter network trained on a CPU, without a single manually annotated radiograph, placed vertebral landmarks on simulated lateral radiographs to within about 1.5 mm. It found every severe fracture but missed most mild and moderate ones.

**Simulation gives labels for free, but not realism.** The model trained only on simulated images found half of the bodies on real radiographs. Adding 351 real images with corner-only labels, through masked losses, raised detection to 91% and cut median corner error to 2.5 px.

**Why mild fractures are missed.** Landmark errors of 1.5–2 mm are 6–8% of a 25-mm body, about the width of the grade 1 band, so cases near a threshold flip. Most misses were biconcave deformities: on a projection radiograph the endplate rims overlap the central depression, so radiographic middle height reads higher than the CT midsagittal reference. Part of the gap is projection physics, not model error.

**Retropulsion.** Posterior wall displacement was within 0.9 mm on average. This is a midline sagittal estimate only; it does not give canal area and will miss fragments off the midline, so CT remains the reference.

**Design for review.** The viewer shows every number and lets the reader drag any point with live recalculation, because the tool is meant to speed measurement, not replace judgment.

## 5. Limitations

- **No real-radiograph fracture test.** Fracture grading was tested only on 8 simulated cases with 14 fractures.
- **Algorithmic reference.** The CT reference landmarks were computed from masks, not placed by radiologists.
- **Publisher resizing** distorts the real images, so pixel-to-mm conversion is approximate.
- **Lumbar only** for real images.
- **Field ends:** at the top and bottom of the image, expected heights come from one side only.
- **Small training set** (26 CTs) and **no reader study**.

## 6. Conclusion

CT-simulated radiographs allow annotation-free training of a small vertebral landmark network, and a few hundred real corner-labeled radiographs close most of the gap for detection on real images. The model reliably finds severe fractures but misses most mild and moderate ones, so a real, labeled fracture set is the next requirement.

## Data and code availability

Code, v0.1 weights, the test-case list, per-level results and an offline viewer are in the [project folder on GitHub](https://github.com/edgarlmartinez/edgarlmartinez.github.io/tree/main/public/ai/vertebral-morphometry), with an [interactive demo](/ai/vertebral-morphometry/). The v0.2 weights will be released with the final paper. VerSe-derived images are CC BY-SA 4.0; code is MIT-licensed.

## References

1. Genant HK, Wu CY, van Kuijk C, Nevitt MC. Vertebral fracture assessment using a semiquantitative technique. J Bone Miner Res. 1993;8:1137–48.
2. Sekuboyina A, Husseini ME, Bayat A, et al. VerSe: a vertebrae labelling and segmentation benchmark for multi-detector CT images. Med Image Anal. 2021;73:102166.
3. Löffler MT, Sekuboyina A, Jacob A, et al. A vertebral segmentation dataset with fracture grading. Radiol Artif Intell. 2020;2:e190138.
4. Spondylolisthesis Vertebral Landmark dataset (BUU-LSPINE images, Burapha University). Mendeley Data. doi:10.17632/5jdfdgp762.1.
5. Zhou X, Wang D, Krähenbühl P. Objects as points. arXiv:1904.07850. 2019.
6. Lin TY, Goyal P, Girshick R, He K, Dollár P. Focal loss for dense object detection. ICCV. 2017.
7. Ronneberger O, Fischer P, Brox T. U-Net: convolutional networks for biomedical image segmentation. MICCAI. 2015.

*Preprint draft for open review. Not peer reviewed. Research use only; not for clinical use.*
