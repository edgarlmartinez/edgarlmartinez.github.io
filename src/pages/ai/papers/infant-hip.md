---
layout: ../../../layouts/Paper.astro
title: A small open landmark network for the acetabular index and IHDI grade on infant pelvic radiographs, running in the browser
short: Infant hip landmarks paper
description: Preprint draft. A 1.1-million-parameter landmark network trained on the public MTDDH dataset measures the infant acetabular index and IHDI grade in the browser.
authors: Edgar L. Martinez Salazar, MD, and research fellow (author list to be finalized). Department of Radiology, Beth Israel Deaconess Medical Center, Harvard Medical School, Boston, MA.
updated: November 2026
---

## Abstract

**Purpose:** To develop a small, openly released landmark network that measures the acetabular index and assigns the International Hip Dysplasia Institute (IHDI) grade on infant AP pelvic radiographs, and that runs privately in a web browser.

**Materials and Methods:** This retrospective study used the public MTDDH dataset (infants aged 5–40 months; CC BY 4.0) with its packaged split: 731 training and 731 test radiographs. A U-Net of about 1.1 million parameters was trained from random initialization on a 4-core CPU to place 8 landmarks (per hip: lateral acetabular edge, triradiate point, top of the femoral head ossific nucleus, H-point). The acetabular index and IHDI grade were computed geometrically. The model was exported to ONNX and runs in the browser with editable points. Outcomes were landmark error, acetabular index error, and IHDI agreement against grades computed from the expert landmarks.

**Results:** On 731 test images (1,462 hips), median landmark error was 2.1–2.8 px (about 1% of the inter-triradiate distance). After excluding the 52 images the dataset lists as outliers (679 images, 1,358 hips), acetabular index mean absolute error was 2.0° (median 1.5°), 94% of hips were within 5°, and bias was +0.2°. IHDI grade agreed in 94% of hips. Sensitivity and specificity for IHDI grade II or higher were 67% and 98%. All grade III and IV hips were graded II or higher, but 55 of 120 grade II hips were called grade I. Images with a low model confidence score (5.6%) had a mean worst-side error of 11.9°, compared with 2.9° for the rest.

**Conclusion:** A small CPU-trained network measures the infant acetabular index with an average error of about 2° and flags its own unreliable cases. Subluxation (IHDI grade II) is its weak point.

**Keywords:** developmental dysplasia of the hip; acetabular index; IHDI classification; landmark detection; deep learning; pediatric radiology; open data

## 1. Introduction

Developmental dysplasia of the hip (DDH) ranges from mild acetabular immaturity to frank dislocation. Once the femoral head ossific nucleus appears, the AP pelvic radiograph becomes the main imaging test. Two measurements dominate. The acetabular index is the angle between Hilgenreiner's line and the acetabular roof. The IHDI classification grades the position of the proximal femoral metaphysis relative to Hilgenreiner's and Perkin's lines (Narayanan et al., 2015).

Both depend on a handful of landmarks that are hard to place consistently on small, often rotated infant pelves, and readers disagree by several degrees. A model that proposes the landmarks, which the reader can then adjust, could speed reporting and reduce variability.

The MTDDH dataset, released openly in 2025, provides expert landmarks on infant pelvic radiographs. This makes a fully open model possible. Running it in the browser means images never leave the reader's device.

**Objectives**

1. Train a small landmark network on the public MTDDH dataset using only a CPU.
2. Measure landmark accuracy, acetabular index error and IHDI grade agreement on the held-out test split.
3. Test whether the model's own peak score identifies unreliable cases.
4. Deploy the model in an offline browser toolkit with editable points.

## 2. Materials and methods

### 2.1 Study design and ethics

Retrospective technical development study on a public, de-identified dataset. No institutional or patient data was used. The test split was fixed by the dataset publishers.

### 2.2 Dataset

MTDDH pelvic radiographs (Sci Data 2025, doi:10.1038/s41597-025-05146-x), as repackaged by the Open Hip Dysplasia project. License: CC BY 4.0. Infants and toddlers aged 5–40 months. The packaged split was used as is: 731 training, 365 validation (not used) and 731 test images. The split is by image because the release has no patient identifiers. The package also lists outlier images (frog-leg views, wrong body part, implants). They were kept in training, and test results are reported with and without them (52 test images listed).

### 2.3 Landmarks and label preparation

Eight landmarks, four per hip:

1. Lateral edge of the acetabular roof.
2. Triradiate (Hilgenreiner) point.
3. Top of the femoral head ossific nucleus.
4. H-point: midpoint of the top of the proximal femoral metaphysis.

Order was checked by geometry: of the two pelvic points, the one farther from the midline was taken as the lateral edge, and of the two femoral points, the higher one as the head top. Images were downsized to at most 768 × 512 pixels.

### 2.4 Network

A U-Net (Ronneberger et al., 2015) of about 1.1 million parameters (4.4 MB), trained from random initialization (no pretrained or foundation model):

- **Stem:** a 5 × 5 convolution with stride 2.
- **Encoder:** 6 levels of two 3 × 3 convolutions with batch normalization and ReLU (24, 32, 48, 72, 96, 128 channels).
- **Decoder:** bilinear upsampling with skip connections.
- **Head:** 8 heatmaps, one per landmark, at stride 2 of the input.

### 2.5 Training

- **Input:** grayscale, letterboxed to 320 × 480.
- **Targets:** Gaussian heatmaps (σ = 1.5 output pixels).
- **Augmentation:** rotation ±10°; scale 0.85–1.25; translation; horizontal mirroring with left-right hip swap; gamma 0.6–1.6; contrast and brightness; Gaussian blur; Gaussian noise; intensity inversion (10%).
- **Loss:** penalty-reduced focal heatmap loss (Lin et al., 2017; Zhou et al., 2019).
- **Optimization:** AdamW, learning rate 2 × 10⁻³, weight decay 10⁻⁴, one-cycle schedule, batch size 8, 4 CPU threads.

### 2.6 Inference and measurement

The image and its mirror image are both run, and the heatmaps are averaged. Each landmark is the weighted centroid of a 5 × 5 window around its heatmap peak.

- **Acetabular index (per hip):** the angle between Hilgenreiner's line (through both triradiate points) and the line from the triradiate point to the lateral acetabular edge.
- **IHDI grade (per hip):** Perkin's line passes through the lateral acetabular edge perpendicular to Hilgenreiner's line, and the diagonal line runs at 45° inferolaterally from their intersection. The H-point is grade I if medial to Perkin's line, II if lateral to it but medial to the diagonal, III if lateral to the diagonal, and IV if above Hilgenreiner's line.
- **Confidence:** the lowest of the 8 heatmap peak scores; under 0.15 shows a "low confidence" note.

### 2.7 Browser deployment

The network was exported to ONNX (opset 17) and matched PyTorch to within 10⁻⁵. In the [MSK Measurement Toolkit](/toolkit/) it runs with onnxruntime-web; the image stays in the browser, and the proposed landmarks become ordinary draggable points with live recalculation.

### 2.8 Computing environment and AI assistance

4-core x86-64 CPU, no GPU; Python 3 with PyTorch, OpenCV, NumPy, ONNX and onnxruntime. Software development was assisted by a large language model coding agent (Claude Code, Claude Opus 5.5; Anthropic), under the radiologist's direction and review. The language model labeled no images and is not part of the model.

### 2.9 Statistical analysis

Landmark error in pixels and as a percentage of the inter-triradiate distance; acetabular index absolute error (mean, median, 90th percentile), share within 3° and 5°, bias and Pearson correlation; IHDI exact agreement, confusion matrix, and sensitivity and specificity for grade II or higher (reference grades computed from the expert landmarks with the same geometry); and error with and without a low confidence score. All analyses were descriptive.

## 3. Results

### 3.1 Landmarks and acetabular index

Mean reference acetabular index was 24.9° (SD 6.8°) across all test hips, and 24.3° (SD 6.2°) without outliers.

| Measure | All (731 images, 1,462 hips) | Without listed outliers (679 images, 1,358 hips) |
|---|---|---|
| Lateral acetabular edge error, median | 2.6 px (1.2%) | 2.6 px (1.2%) |
| Triradiate point error, median | 2.8 px (1.3%) | 2.7 px (1.2%) |
| Femoral head top error, median | 2.1 px (1.0%) | 2.1 px (0.9%) |
| H-point error, median | 2.4 px (1.1%) | 2.3 px (1.1%) |
| Acetabular index MAE | 2.38° | 1.97° |
| Acetabular index median absolute error | 1.56° | 1.50° |
| 90th percentile absolute error | 4.55° | 4.14° |
| Within 3° | 76% | 79% |
| Within 5° | 92% | 94% |
| Bias | +0.26° | +0.23° |
| Pearson r | 0.78 | 0.90 |

Percentages in parentheses are of the reference inter-triradiate distance. Errors were smallest in the normal range and pulled toward the mean at the extremes (without outliers):

| Reference acetabular index | Hips | MAE | Bias |
|---|---|---|---|
| Under 20° | 287 | 2.53° | +1.90° |
| 20–30° | 886 | 1.69° | +0.09° |
| 30° or more | 185 | 2.40° | −1.67° |

### 3.2 IHDI grade

IHDI grade agreed exactly in 94% of hips without outliers (92% with them). Sensitivity and specificity for grade II or higher were 67% and 98% (69% and 97% with outliers).

**Confusion matrix without outliers (rows = predicted, columns = reference)**

| Predicted \ Reference | I | II | III | IV |
|---|---|---|---|---|
| I | 1,170 | 55 | 0 | 0 |
| II | 19 | 62 | 3 | 0 |
| III | 0 | 2 | 22 | 2 |
| IV | 0 | 0 | 1 | 22 |
| **Total** | 1,189 | 120 | 25 | 24 |

Every grade III and IV hip was graded II or higher. Errors were concentrated at the grade I/II boundary.

### 3.3 Confidence flag

Across all 731 test images, 41 (5.6%) had a lowest peak score under 0.15. Their mean worst-side acetabular index error was 11.9°, compared with 2.9° for the other images. Just over half of them (22 of 41) were the dataset's own outliers.

## 4. Discussion

A 1.1-million-parameter network trained on a CPU measured the infant acetabular index with a mean error of 2.0° and matched the IHDI grade in 94% of hips. It runs in a browser, so images never leave the reader's device.

**Accuracy in context.** Differences of several degrees between human readers are commonly reported for the acetabular index, so an average model error of 2°, with 94% of hips within 5°, is within the range of normal reading variation. Errors were larger at the extremes, with a pull toward the mean. This matters clinically because the high-angle hips are the dysplastic ones.

**IHDI grade II is the weak point.** Grade II depends on whether the H-point lies just lateral to Perkin's line, often a few pixels, so small landmark errors flip the grade. The model never under-called a grade III or IV hip as grade I. The tool therefore shows the grade together with the editable landmarks, so the reader can check boundary cases.

**The confidence flag works.** Images with a low peak score had about four times the error of the rest, and about half were views the model was never designed for.

## 5. Limitations

- **Single public dataset;** no external validation.
- **Split by image.** The same child may appear in both training and test images.
- **Reference grade derived from the same landmarks,** not from an independent clinical reading.
- **No age-specific norms** for the acetabular index.
- **No view check** other than the confidence score, and **no reader study**.

## 6. Conclusion

A small, open landmark network trained on public data with a CPU measures the infant acetabular index to about 2°, matches the IHDI grade in 94% of hips, runs privately in a browser, and flags its own unreliable cases. Its main weakness is IHDI grade II, where reader review of the proposed landmarks remains essential.

## Data and code availability

The ONNX model and its documentation are in the [toolkit models folder on GitHub](https://github.com/edgarlmartinez/edgarlmartinez.github.io/tree/main/public/toolkit/models), and the model runs in the [MSK Measurement Toolkit](/toolkit/) (Pediatric hip tab). Training and evaluation scripts will be released with the final paper.

## References

1. MTDDH pelvic radiograph dataset. Sci Data. 2025. doi:10.1038/s41597-025-05146-x.
2. Open Hip Dysplasia project. github.com/radoss-org/open-hip-dysplasia.
3. Narayanan U, Mulpuri K, Sankar WN, et al. Reliability of a new radiographic classification for developmental dysplasia of the hip. J Pediatr Orthop. 2015;35:478–84.
4. Ronneberger O, Fischer P, Brox T. U-Net: convolutional networks for biomedical image segmentation. MICCAI. 2015.
5. Lin TY, Goyal P, Girshick R, He K, Dollár P. Focal loss for dense object detection. ICCV. 2017.
6. Zhou X, Wang D, Krähenbühl P. Objects as points. arXiv:1904.07850. 2019.

*Preprint draft for open review. Not peer reviewed. Research use only; not for clinical use.*
