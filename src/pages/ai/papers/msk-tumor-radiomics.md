---
layout: ../../../layouts/Paper.astro
title: Automated segmentation and radiomic robustness of extremity soft-tissue sarcoma on MRI and CT with a CPU-trained nnU-Net, a public-data baseline
short: Sarcoma segmentation and radiomics paper
description: Preprint draft. nnU-Net v2 segmentation of extremity soft-tissue sarcoma on MRI and CT from the public TCIA Soft-tissue-Sarcoma collection, with radiomic feature robustness analysis.
authors: Edgar L. Martinez Salazar, MD, and research fellow (author list to be finalized). Department of Radiology, Beth Israel Deaconess Medical Center, Harvard Medical School, Boston, MA.
updated: November 2026
---

## Abstract

**Purpose:** To build and evaluate an openly released, CPU-trained nnU-Net model for automatic segmentation of extremity soft-tissue sarcoma on MRI and CT, and to identify radiomic features that stay reliable when automatic contours replace expert contours.

**Materials and Methods:** This retrospective technical study used the public TCIA Soft-tissue-Sarcoma collection: 51 patients with T1-weighted MRI, T2-weighted fat-suppressed or STIR MRI, the CT from FDG-PET/CT, and expert gross tumor volume contours. Patients were split randomly into 40 training and 11 test patients. Two nnU-Net v2 3D models (contrast-agnostic MRI and CT) were trained from random initialization on a 4-core CPU with a shortened schedule (3,000–4,000 iterations). A two-sequence consensus post-processing step was applied on MRI. PyRadiomics extracted 107 IBSI-aligned features. A feature was called robust if its ICC(1,1) was at least 0.90 under contour perturbation (all 51 patients) and at least 0.75 between automatic and expert masks (test patients).

**Results:** Median Dice was 0.74 (IQR 0.64–0.84) on T1, 0.75 (0.55–0.88) on T2FS/STIR and 0.48 (0.07–0.56) on CT. Median HD95 was 18.9, 21.1 and 46.1 mm. Post-processing raised median Dice from 0.41 to 0.74 on T1 and from 0.49 to 0.75 on T2FS/STIR. One small tumor (79 mL) was missed on all sequences. Under perturbation, 99–107 of 107 features per sequence had ICC ≥ 0.90. Only 23 (T1), 26 (T2FS/STIR) and 30 (CT) features met both robustness criteria.

**Conclusion:** A CPU-trained nnU-Net gives an editable starting contour for extremity sarcoma on MRI, but not on PET/CT CT. Perturbation stability alone overstates radiomic reliability. Agreement between automatic and expert masks should be tested directly.

**Keywords:** soft-tissue sarcoma; segmentation; nnU-Net; radiomics; feature robustness; MRI; open data

## 1. Introduction

Soft-tissue sarcomas of the extremities are rare, heterogeneous tumors. MRI is the reference for local staging and treatment planning. Tumor volume and diameters guide management and response assessment, and radiomic texture features are widely studied as markers of grade, metastatic risk and outcome (Vallières et al., 2015).

Both uses depend on a tumor contour. Manual contouring of large, irregular sarcomas takes time and varies between readers. Many radiomic features also change with small contour differences, so the Image Biomarker Standardization Initiative (IBSI) recommends testing feature robustness, for example by perturbing the mask (Zwanenburg et al., 2019; 2020).

nnU-Net is a self-configuring segmentation framework that adapts its preprocessing, architecture and training to each dataset (Isensee et al., 2021). It usually needs a GPU and a long schedule. Whether a short, CPU-only training run on a small public dataset can give a usable sarcoma contour is not known. Nor is it known how many radiomic features survive when an automatic contour replaces the expert one.

**Objectives**

1. Train contrast-agnostic MRI and CT segmentation models for extremity sarcoma on public data, using only a CPU.
2. Measure segmentation accuracy and volumetric agreement on held-out patients.
3. Test a simple two-sequence consensus to remove false-positive components on MRI.
4. Identify radiomic features that are stable under contour perturbation and that agree between automatic and expert masks.
5. Release the models, code and an offline viewer openly.

## 2. Materials and methods

### 2.1 Study design and ethics

Retrospective technical development study on a public, de-identified dataset. No institutional or patient data was used. The test patients were fixed before training and were never used for training or tuning.

### 2.2 Dataset

The TCIA Soft-tissue-Sarcoma collection (Vallières et al., 2015; Clark et al., 2013) was downloaded through the NCI Imaging Data Commons (`idc-index`; Fedorov et al., 2021). License: CC BY 3.0. It contains 51 patients with extremity soft-tissue sarcoma. Each has a T1-weighted MRI, a T2-weighted fat-suppressed or STIR MRI, the CT from FDG-PET/CT, and expert contours of the gross tumor volume (GTV mass) and peritumoral edema, stored as RTSTRUCT on each series. Median expert tumor volume on MRI was 352 mL (IQR 141–699 mL).

**Split.** Patients were shuffled with a fixed seed (42) and the first 11 held out as the test set (STS_005, 010, 012, 017, 020, 024, 026, 027, 030, 032, 046). The other 40 formed the training set. The same patients were held out for every sequence.

### 2.3 Label preparation

1. Each RTSTRUCT was matched to its referenced series. Contours were rasterized slice by slice onto the native image grid (scikit-image polygon fill; label 1 = GTV mass, label 2 = edema outside the mass).
2. Only label 1 (tumor) was used for training and evaluation. Edema was not modeled.
3. T2FS and STIR were pooled as one fluid-sensitive class.
4. One CT contour (STS_046, a test patient) did not map onto its CT. That patient was excluded from CT results only (10 CT test patients).

### 2.4 Segmentation models

The final MRI model used a pooled, contrast-agnostic nnU-Net dataset (T1 and T2FS/STIR from the 40 training patients, 80 images). The CT model used 40 images. Both used the 3D full-resolution configuration.

**Architecture.** PlainConvUNet with 5 stages (16, 32, 64, 128 and 192 feature maps), 2 convolutions per stage in the encoder and decoder, instance normalization and leaky ReLU. A lighter plan (`nnUNetPlansCPUlite`) reduced memory and compute for the CPU.

| Setting | MRI model | CT model |
|---|---|---|
| Normalization | z-score per image | nnU-Net CT normalization |
| Target spacing (z × y × x) | 5.2 × 1.4 × 1.4 mm | 4.0 × 2.0 × 2.0 mm |
| Patch size (voxels) | 28 × 96 × 128 | 64 × 80 × 64 |
| Downsampling strides | (1,1,1), (1,2,2), (2,2,2), (2,2,2), (1,2,2) | (1,1,1), (1,2,2), (2,2,2), (2,2,2), (2,2,2) |
| Batch size | 2 | 2 |
| Trainer | 40 epochs × 100 iterations | 30 epochs × 100 iterations |
| Training data | All 40 patients, one model (`fold_all`) | Same |

The custom trainers change only the training length. Everything else is the nnU-Net default: Dice plus cross-entropy loss with deep supervision; the default spatial and intensity augmentation; SGD with Nesterov momentum (0.99), initial learning rate 0.01 and polynomial decay; and sliding-window inference. The schedule is about 1.2–1.6% of the default 250,000 iterations. All models were trained from random initialization; no pretrained weights or foundation models were used.

### 2.5 Post-processing

The raw output contained many small false-positive components. Two rules were compared:

- **Largest connected component (LCC):** keep the largest 3D component. Used for CT and for single-sequence MRI.
- **Two-sequence consensus (MRI):** resample the other sequence's prediction into this sequence's physical space (nearest neighbor), take the LCC of the intersection of the two predictions, and keep every component of this sequence's prediction that overlaps it. If the predictions do not overlap, fall back to LCC.

### 2.6 Computing environment and AI assistance

Training and inference ran on a 4-core x86-64 CPU with no GPU, in a Linux cloud container. Software: Python 3, PyTorch, nnU-Net v2, PyRadiomics 3.1, SimpleITK, pydicom, scikit-image, SciPy, NumPy and pandas.

Software development was assisted by a large language model coding agent (Claude Code, Claude Opus 5.5; Anthropic), under the radiologist's direction and review. The language model labeled no images and is not part of the trained models. The authors reviewed all code and results.

### 2.7 Volumetrics

From each mask: volume (mL); the longest axial diameter, taken as the maximum in-plane Feret diameter over all slices, with its perpendicular; and craniocaudal extent.

### 2.8 Radiomic feature extraction

PyRadiomics 3.1 (van Griethuysen et al., 2017) extracted 107 original-image features in 7 classes: shape (14), first order (18), GLCM (24), GLRLM (16), GLSZM (16), GLDM (14) and NGTDM (5).

| Setting | CT | MRI |
|---|---|---|
| Intensity preparation | Hounsfield units unchanged | N4 bias-field correction (Tustison et al., 2010) inside a body mask, then z-score over the body |
| Resegmentation | −200 to 400 HU | −3 to +3 SD |
| Discretization | Fixed bin width, 25 HU | Fixed bin count, 32 |
| Resampling | 1 × 1 × 3 mm, B-spline | 1 × 1 mm in plane, slice spacing kept |
| Texture dimension | 3D | 2D per slice, aggregated (slices 4–15 mm) |

The body mask used a threshold at 8% of the 99th intensity percentile, morphological opening and closing, and hole filling per slice. Otsu thresholding was avoided because fat suppression makes fat as dark as air.

### 2.9 Feature robustness

**Perturbation stability (all 51 patients, expert masks).** Each expert mask was perturbed four ways: 1-voxel in-plane erosion, 1-voxel in-plane dilation, and two random smooth contour jitters of up to about 2 mm, after Zwanenburg et al. (2019). ICC(1,1) was computed across the reference and perturbed masks.

**Automatic versus expert agreement (test patients).** Features from the post-processed automatic mask were compared with features from the expert mask by ICC(1,1).

**Robust feature.** ICC ≥ 0.90 under perturbation **and** ICC ≥ 0.75 between automatic and expert masks.

### 2.10 Statistical analysis

Segmentation was assessed by the Dice similarity coefficient, the 95th-percentile symmetric Hausdorff distance (HD95, mm) and volume error ((automatic − expert) / expert), given as median and interquartile range. ICC(1,1) was a one-way random-effects, single-measure model (Shrout and Fleiss, 1979). All analyses were descriptive.

## 3. Results

### 3.1 Segmentation

| Sequence | n | Dice, raw | Dice, LCC | Dice, final (IQR) | HD95, median | Volume error, median |
|---|---|---|---|---|---|---|
| MRI T1 | 11 | 0.41 | 0.66 | 0.74 (0.64–0.84) | 18.9 mm | +15% |
| MRI T2FS/STIR | 11 | 0.49 | 0.59 | 0.75 (0.55–0.88) | 21.1 mm | +4% |
| CT of PET/CT | 10 | 0.25 | 0.48 | 0.48 (0.07–0.56) | 46.1 mm | −6% |

Raw is the network output; LCC is the largest connected component; final is the two-sequence consensus on MRI and LCC on CT. On MRI, LCC alone sometimes kept the wrong component (Dice 0 for STS_026 and STS_046 on T1, and for STS_017 and STS_027 on T2FS/STIR). The consensus recovered all four (Dice 0.71–0.90).

**Per-patient Dice (final) and expert volume**

| Patient | Expert volume (MRI) | T1 | T2FS/STIR | CT |
|---|---|---|---|---|
| STS_005 | 585 mL | 0.89 | 0.94 | 0.00 |
| STS_010 | 183 mL | 0.62 | 0.52 | 0.68 |
| STS_012 | 79 mL | 0.00 | 0.00 | 0.00 |
| STS_017 | 745 mL | 0.84 | 0.87 | 0.78 |
| STS_020 | 2,361 mL | 0.86 | 0.84 | 0.56 |
| STS_024 | 78 mL | 0.66 | 0.59 | 0.55 |
| STS_026 | 380 mL | 0.71 | 0.92 | 0.00 |
| STS_027 | 901 mL | 0.84 | 0.90 | 0.46 |
| STS_030 | 338 mL | 0.22 | 0.02 | 0.51 |
| STS_032 | 111 mL | 0.77 | 0.64 | 0.28 |
| STS_046 | 751 mL | 0.74 | 0.75 | excluded |

STS_012 (79 mL) was missed on every sequence. STS_030 failed on both MRI sequences, with a large false-positive volume on T1 (1,853 mL predicted against 338 mL). On CT, the largest component was the wrong structure in 3 of 10 patients. Volume errors were largest for small tumors: the three tumors under 120 mL had volume errors of +39% to +418% on T1.

### 3.2 Radiomic robustness

| Sequence | Features | ICC ≥ 0.90 under perturbation | ICC ≥ 0.75 auto vs expert | Robust (both) |
|---|---|---|---|---|
| MRI T1 | 107 | 107 | 23 | 23 |
| MRI T2FS/STIR | 107 | 106 | 26 | 26 |
| CT | 107 | 99 | 32 | 30 |

**Robust features**

- **T1 (23):** shape Maximum2DDiameterSlice, SurfaceVolumeRatio; first order 10Percentile, 90Percentile, Energy, Mean, Minimum, RootMeanSquared, TotalEnergy; GLCM Imc1, Imc2, InverseVariance; GLRLM GrayLevelNonUniformity, LongRunHighGrayLevelEmphasis, RunEntropy; GLSZM GrayLevelNonUniformityNormalized, SmallAreaEmphasis, ZoneEntropy; GLDM DependenceNonUniformity, GrayLevelNonUniformity, LargeDependenceEmphasis; NGTDM Busyness, Complexity.
- **T2FS/STIR (26):** shape Maximum2DDiameterSlice, MeshVolume, SurfaceArea, VoxelVolume; first order Energy, Maximum, TotalEnergy; GLCM Id, Idm, Imc1; GLRLM GrayLevelNonUniformity, LongRunEmphasis, LongRunHighGrayLevelEmphasis, RunPercentage, RunVariance; GLSZM GrayLevelNonUniformity, LargeAreaEmphasis, LargeAreaHighGrayLevelEmphasis, LargeAreaLowGrayLevelEmphasis, ZoneVariance; GLDM DependenceNonUniformity, DependenceVariance, GrayLevelNonUniformity, LargeDependenceEmphasis, LargeDependenceHighGrayLevelEmphasis; NGTDM Complexity.
- **CT (30):** first order Entropy, InterquartileRange, RobustMeanAbsoluteDeviation, Uniformity; GLCM Contrast, DifferenceAverage, DifferenceEntropy, DifferenceVariance, Id, Idm, InverseVariance, JointEnergy, JointEntropy, MaximumProbability, SumEntropy; GLRLM GrayLevelNonUniformityNormalized, LongRunEmphasis, RunLengthNonUniformityNormalized, RunPercentage, RunVariance, ShortRunEmphasis; GLSZM GrayLevelNonUniformityNormalized, SizeZoneNonUniformityNormalized, SmallAreaEmphasis, ZoneEntropy, ZonePercentage; GLDM DependenceNonUniformityNormalized, DependenceVariance, LargeDependenceEmphasis, SmallDependenceEmphasis.

Ten features were robust on both MRI sequences: shape Maximum2DDiameterSlice; first order Energy and TotalEnergy; GLCM Imc1; GLRLM GrayLevelNonUniformity and LongRunHighGrayLevelEmphasis; GLDM DependenceNonUniformity, GrayLevelNonUniformity and LargeDependenceEmphasis; and NGTDM Complexity. Only GLDM LargeDependenceEmphasis was robust on all three sequences.

## 4. Discussion

A CPU-trained nnU-Net, given about 1.5% of the usual training schedule, produced MRI contours of extremity sarcoma with a median Dice of 0.74–0.75. That is good enough to serve as an editable starting contour, not as a final one. CT from PET/CT reached only 0.48 and is not usable.

**Post-processing mattered as much as training.** Raw outputs had a median Dice of only 0.41–0.49 because of scattered false-positive islands. Keeping the largest component helped, but sometimes kept the wrong one. Requiring the tumor to appear on both MRI sequences raised Dice by about 0.1 and recovered four cases that LCC got completely wrong. This anatomical prior costs nothing at inference and needs no retraining.

**Failures were predictable.** Small tumors (under about 120 mL) had the largest volume errors, and one 79-mL tumor was missed entirely. On CT, low dose and poor soft-tissue contrast left the model unable to separate tumor from muscle in a third of patients. A longer schedule, cross-validation ensembling and more training data are the obvious next steps.

**Perturbation stability overstates radiomic reliability.** Almost every feature passed the IBSI-style perturbation test. Only 23–30 also agreed between automatic and expert masks. Perturbations are small and centred on the true boundary, whereas automatic contours make larger, systematic errors such as missed lobules or included edema. Radiomic studies that use automatic segmentation should test agreement between automatic and expert masks directly. Many of the robust MRI features are size- or intensity-driven, which is expected because they depend less on exact boundary placement.

## 5. Limitations

- **Short training schedule and single model.** No cross-validation or ensembling. The results are a floor for nnU-Net on this task.
- **Small test set.** With 11 patients (10 on CT), confidence intervals are wide and the auto-versus-expert ICCs are noisy. The robust feature lists should be treated as provisional.
- **Single dataset.** Performance on other scanners and protocols is unknown, and no external validation was done.
- **Thick, variable MRI slices** (4–15 mm) limit 3D segmentation and forced 2D texture.
- **CT is the low-dose CT of PET/CT**, not diagnostic contrast-enhanced CT.
- **Edema not modeled.**
- **No clinical endpoint** and **no reader study.**

## 6. Conclusion

A CPU-trained nnU-Net with a two-sequence consensus gives an editable MRI starting contour for extremity soft-tissue sarcoma (median Dice 0.74–0.75), but not a usable CT contour. Only about a quarter of radiomic features stay reliable when automatic contours replace expert ones, a much stricter result than perturbation testing alone suggests.

## Data and code availability

Code, model weights, radiomics parameter files, the patient split, per-patient results and an offline viewer are in the [project folder on GitHub](https://github.com/edgarlmartinez/edgarlmartinez.github.io/tree/main/public/ai/msk-tumor-radiomics). The [interactive demo](/ai/msk-tumor-radiomics/) runs in the browser. Code is MIT-licensed; derived images and weights are CC BY 3.0.

## References

1. Vallières M, Freeman CR, Skamene SR, El Naqa I. A radiomics model from joint FDG-PET and MRI texture features for the prediction of lung metastases in soft-tissue sarcomas of the extremities. Phys Med Biol. 2015;60:5471–96.
2. Clark K, Vendt B, Smith K, et al. The Cancer Imaging Archive (TCIA). J Digit Imaging. 2013;26:1045–57.
3. Fedorov A, Longabaugh WJR, Pot D, et al. NCI Imaging Data Commons. Cancer Res. 2021;81:4188–93.
4. Isensee F, Jaeger PF, Kohl SAA, Petersen J, Maier-Hein KH. nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation. Nat Methods. 2021;18:203–11.
5. van Griethuysen JJM, Fedorov A, Parmar C, et al. Computational radiomics system to decode the radiographic phenotype. Cancer Res. 2017;77:e104–7.
6. Zwanenburg A, Vallières M, Abdalah MA, et al. The Image Biomarker Standardization Initiative. Radiology. 2020;295:328–38.
7. Zwanenburg A, Leger S, Agolli L, et al. Assessing robustness of radiomic features by image perturbation. Sci Rep. 2019;9:614.
8. Tustison NJ, Avants BB, Cook PA, et al. N4ITK: improved N3 bias correction. IEEE Trans Med Imaging. 2010;29:1310–20.
9. Shrout PE, Fleiss JL. Intraclass correlations: uses in assessing rater reliability. Psychol Bull. 1979;86:420–8.

*Preprint draft for open review. Not peer reviewed. Research use only; not for clinical use.*
