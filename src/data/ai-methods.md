## Introduction

Musculoskeletal (MSK) imaging relies on many manual measurements and contours: tumor volumes, vertebral body heights, acetabular angles and alignment lines. They take time, and readers disagree on them. The projects on this page are a set of open, reproducible baselines that test how far small models, trained only on public datasets and on ordinary computing hardware, can automate these tasks. Each one returns editable output (a contour or draggable landmarks), so the radiologist stays in control.

This section is written like the methods section of a research paper. It covers, step by step, how each model was built, trained and evaluated, so that a research fellow can reproduce the work and write it up. Every number below comes from the project's code, configuration files or saved result files. Where a detail was not recorded, the text says so.

### Objectives

1. Build openly licensed, research-only baselines for four MSK tasks: (a) segmentation and radiomic texture analysis of extremity soft-tissue sarcoma on MRI and CT; (b) vertebral morphometry (height loss, Genant grade and retropulsion) on lateral spine radiographs; (c) landmark detection for the acetabular index and IHDI grade on infant AP pelvis radiographs; and (d) automated lumbar lordosis.
2. Use only public datasets with licenses that allow reuse, and no institutional or patient data.
3. Train on a standard 4-core CPU with no GPU, to show what is possible without specialized hardware.
4. Report accuracy on held-out data with standard metrics, including the failures.
5. Release each model as a self-contained, offline browser tool with editable output, so readers can check and correct it.

<details>
<summary><b>1. Study design, data governance and ethics</b></summary>

- **Design.** Retrospective technical development and validation on public datasets. Every model was evaluated on a held-out test set that was set aside before training and never used to tune the models.
- **Data.** Only publicly released, de-identified datasets were used (listed in section 4 and the data table in section 8). No data from Beth Israel Deaconess Medical Center (BIDMC) or any other institution was used, and no protected health information was handled.
- **Ethics.** Because all data are public and de-identified, institutional review board (IRB) review was not sought for this technical work. *The fellow should confirm with the BIDMC IRB office whether a formal non-human-subjects determination is needed for publication.*
- **Licenses.** Each dataset was used under its own license (CC BY 3.0, CC BY 4.0 or CC BY-SA 4.0). Derived images and weights are shared under the same terms. Project code is MIT-licensed.
- **Intended use.** Research and education only. None of the models is an FDA-cleared device, and none is validated for patient care.

</details>

<details>
<summary><b>2. Computing environment, software and AI assistance</b></summary>

**Hardware.** All training and inference ran on a 4-core x86-64 CPU with no GPU (`torch.set_num_threads(4)` in every training script), in a Linux cloud container. Inference in the published tools runs in the user's own web browser.

**Base models.** No foundation model or pretrained network was used for any released model. The landmark networks were **trained from scratch** (random initialization). The tumor model uses **nnU-Net v2**, a self-configuring segmentation *framework* (Isensee et al., Nat Methods 2021) that designs and trains a U-Net for each dataset. Here it was also trained from random initialization, not fine-tuned from TotalSegmentator or any other pretrained weights. Promptable foundation models (for example MedSAM2) are listed as future work only.

**Frontier large language model.** The code was written, run and documented with **Claude Code**, Anthropic's AI coding agent, running the **Claude Opus 5.5** large language model. The repository history records this as `Co-authored-by: Claude Opus 5.5` on the commits that added these projects. The language model wrote and debugged code, ran experiments and drafted the documentation, under the radiologist's direction and review. It did not label images, does not appear in any trained model, and makes no predictions on images.

**Software.**

| Purpose | Software |
|---|---|
| Language | Python 3 |
| Deep learning | PyTorch; nnU-Net v2 with `dynamic_network_architectures` (PlainConvUNet) |
| Radiomics | PyRadiomics 3.1 (IBSI-aligned feature definitions) |
| Medical image input/output | SimpleITK, pydicom, nibabel; NCI Imaging Data Commons client (`idc-index`) |
| Image processing and statistics | NumPy, SciPy (`ndimage`), scikit-image, OpenCV, pandas |
| Model export and browser inference | ONNX (opset 17), onnxruntime-web 1.20.1 |
| Viewers and testing | Single-file HTML/JavaScript viewers; Playwright (headless Chromium) for end-to-end tests |

*Exact version numbers of Python, PyTorch, nnU-Net, SimpleITK and OpenCV were not saved with the runs. Record them (`pip freeze`) when the models are retrained for the paper.*

</details>

<details>
<summary><b>3. General pipeline (common to all projects)</b></summary>

1. **Define the clinical task** and the measurement it feeds (for example, the Genant grade from vertebral heights, or the acetabular index from four landmarks per hip).
2. **Find a public dataset** whose labels match the task and whose license allows reuse. Download it with scripted tools (`idc-index` for TCIA; `remotezip` for partial downloads of large archives).
3. **Convert and harmonize labels.** Convert DICOM/RTSTRUCT or vendor annotation files into one internal format (NIfTI volumes, or NumPy arrays of points). Fix inconsistent label order by geometry, and exclude unusable cases, with the reasons logged.
4. **Split by patient before training.** Use the publisher's split where one exists; otherwise use a fixed random split (seed 42). The test set is never used for training or tuning.
5. **Preprocess** (resampling, intensity normalization, resizing) with the same code for training and inference.
6. **Train** with heavy data augmentation, sized to fit a 4-core CPU.
7. **Post-process** the raw network output into clinically meaningful objects (largest connected component, landmark decoding, duplicate suppression).
8. **Compute the clinical measurement** with a deterministic measurement engine, the same one used for the reference labels.
9. **Evaluate** on the held-out set with technical metrics (Dice, landmark error) and clinical ones (volume, angle, grade agreement).
10. **Package** the model in an offline browser viewer that shows the reference and automatic output side by side and lets the reader edit it.

</details>

<details>
<summary><b>4. Model-specific methods</b></summary>

#### 4.1 Soft-tissue sarcoma segmentation and radiomics (MRI and CT)

**Objective.** Automatically contour extremity soft-tissue sarcomas (gross tumor volume, GTV), report volume and diameters, and find which radiomic texture features stay reliable when the contour changes.

**Dataset.** TCIA *Soft-tissue-Sarcoma* collection (Vallières M, et al. Phys Med Biol 2015;60:5471–96), obtained through the NCI Imaging Data Commons. License CC BY 3.0. 51 patients with extremity soft-tissue sarcoma. Each has T1-weighted MRI, T2-weighted fat-suppressed or STIR MRI, the CT from FDG-PET/CT, and expert GTV contours (RTSTRUCT) drawn on each series.

**Split.** 40 training and 11 test patients, randomly assigned by patient (seed 42), so the same patients are held out for every sequence. One CT contour (STS_046) did not map onto its CT and was excluded from the CT test results (10 CT test patients).

**Preprocessing.**
1. RTSTRUCT contours were rasterized onto each native series (`convert_sts.py`; label 1 = tumor mass, label 2 = peritumoral edema). Only the tumor label was used for training.
2. T2FS and STIR were pooled as one fluid-sensitive class.
3. A single *contrast-agnostic* MRI dataset was built by pooling T1 and T2FS/STIR (80 training images from 40 patients). A separate CT dataset had 40 training images.
4. nnU-Net automatic planning: z-score normalization for MRI and CT normalization (HU clipping and scaling from the dataset fingerprint) for CT.

**Architecture.** nnU-Net v2, 3D full-resolution configuration, PlainConvUNet with 5 stages (16, 32, 64, 128 and 192 feature maps), 2 convolutions per stage, instance normalization and leaky ReLU. To fit a CPU, a lighter custom plan (`nnUNetPlansCPUlite`) was used:

| | MRI model | CT model |
|---|---|---|
| Target spacing | 5.2 × 1.4 × 1.4 mm | 4.0 × 2.0 × 2.0 mm |
| Patch size (voxels) | 28 × 96 × 128 | 64 × 80 × 64 |
| Batch size | 2 | 2 |
| Trainer | `nnUNetTrainerCPU`: 40 epochs × 100 iterations | `nnUNetTrainerCPU30`: 30 epochs × 100 iterations |
| Training data | All 40 training patients, single model (`fold_all`), no cross-validation | Same |

All other settings are nnU-Net defaults: Dice plus cross-entropy loss with deep supervision, the default augmentation pipeline, SGD with Nesterov momentum and polynomial learning-rate decay, and sliding-window inference. The schedule is about 1–2% of the nnU-Net default (1,000 epochs × 250 iterations). The results are therefore a lower bound on what the framework can reach.

**Post-processing.** On MRI, a *two-sequence consensus* keeps only the predicted components that agree between T1 and T2FS/STIR (the other sequence's mask is resampled in physical space). When only one sequence is available, and on CT, the largest connected component is kept.

**Radiomics.** PyRadiomics 3.1 extracted 107 original-image features (shape, first order, GLCM, GLRLM, GLSZM, GLDM and NGTDM), with modality-specific settings:

| | CT | MRI |
|---|---|---|
| Intensity | Hounsfield units unchanged | N4 bias-field correction inside a body mask, then z-score over the body |
| Resegmentation | −200 to 400 HU | ±3 SD |
| Discretization | Fixed bin width, 25 HU | Fixed bin number, 32 |
| Resampling | 1 × 1 × 3 mm, B-spline | 1 × 1 mm in plane, 2D texture aggregated over slices (slices are 4–15 mm) |

**Feature robustness.** The expert masks of all 51 patients were perturbed by 1-voxel erosion, 1-voxel dilation and two random contour jitters of about 2 mm, following Zwanenburg et al. (Sci Rep 2019). A feature was called *robust* if its ICC(1,1) was at least 0.90 across perturbations **and** its ICC between automatic and expert masks on the test patients was at least 0.75.

#### 4.2 Vertebral morphometry on lateral spine radiographs

**Objective.** Detect each vertebral body on a lateral radiograph, place 7 landmarks, and compute anterior, middle and posterior heights, percent height loss against the expected normal height from adjacent levels, the Genant grade, and two retropulsion proxies: posterior wall displacement and sagittal canal compromise.

**Datasets.**
- *VerSe 2019* spine CT with vertebra masks (Sekuboyina et al. 2021; Löffler et al. 2020), CC BY-SA 4.0. Reference landmarks were generated automatically from the midsagittal slab of each vertebra mask (`ct_reference.py`). 34 CTs were used: 26 for training and 8 held out (IDs saved in `drr_test_ids.json`). *The reason this subset of VerSe 2019 was chosen should be confirmed.*
- *Simulated radiographs.* No public, labeled set of lateral spine radiographs was freely downloadable, so each CT was turned into a digitally reconstructed radiograph (DRR) by parallel lateral projection at 1.0 mm per pixel, both whole-body and as a midline slab (`drr.py`). This gave 52 training images. The CT landmarks map exactly onto the DRR.
- *Real radiographs (v0.2, in development).* The "Spondylolisthesis Vertebral Landmark" dataset (Mendeley Data, doi:10.17632/5jdfdgp762.1, CC BY 4.0; most images from BUU-LSPINE, Burapha University): 698 lateral lumbar radiographs with 4 corner points per body, resized by the publisher to 640 × 640. Inconsistent corner order was fixed by geometry. After quality checks, 564 images were usable: 351 for training and 204 held out from the publisher's validation split.

**Architecture.** A small CenterNet-style U-Net (5 encoder levels with 12–96 channels, about 0.5 million parameters), **trained from scratch**. It has three heads at stride 2: a vertebral-centre heatmap, 14 offset channels (x and y for each of 7 points), and 7 per-point refinement heatmaps. Input is a grayscale image at about 1 mm per pixel.

**Training.** Random 384 × 192 crops centred near a vertebra, with deformed (fractured) bodies oversampled 5 to 1. Augmentation: scale 0.75–1.35, rotation ±15°, translation, left-right mirroring, gamma, contrast and brightness changes, blur, noise and occasional inversion; for real images, aspect-ratio jitter as well. Loss: focal heatmap loss plus 5 × smooth-L1 offset loss. Optimizer AdamW (learning rate 2 × 10⁻³, weight decay 10⁻⁴) with a one-cycle schedule, batch size 8. v0.2 was fine-tuned from the v0.1 weights on simulated and real images, with loss masks for points the real labels lack. *The number of iterations used for the released weights was set on the command line and not saved. The script default is 3,000.*

**Inference.** Flip test-time augmentation of the centre heatmap, peak detection, refinement of each point with its own heatmap, suppression of duplicate detections, and rejection of detections that lie off a quadratic fit of the spinal column. The measurement engine exists in Python and JavaScript, and the two versions were checked to agree on all 863 VerSe 2019 levels.

#### 4.3 Infant hip landmarks (acetabular index and IHDI grade)

**Objective.** Place the 8 landmarks needed for the acetabular index and the International Hip Dysplasia Institute (IHDI) grade on infant AP pelvis radiographs, inside the MSK Measurement Toolkit.

**Dataset.** MTDDH pelvic radiographs (Sci Data 2025, doi:10.1038/s41597-025-05146-x), as repackaged by the Open Hip Dysplasia project, CC BY 4.0. Infants and toddlers aged 5–40 months. Per hip: the lateral edge of the acetabular roof, the triradiate (Hilgenreiner) point, the top of the femoral head ossific nucleus, and the H-point. The packaged split was used as is: 731 training, 365 validation (not used) and 731 test images. The split is by image because the release has no patient identifiers.

**Architecture and training.** A small U-Net with a stride-2 stem, 6 levels (24–128 channels) and about 1.1 million parameters, **trained from scratch**, with one heatmap per landmark at stride 2. Inputs were letterboxed to 320 × 480. Augmentation: rotation ±10°, scale 0.85–1.25, translation, mirroring with left-right hip swap, gamma, contrast, blur, noise and inversion. Focal heatmap loss, AdamW (2 × 10⁻³, weight decay 10⁻⁴), one-cycle schedule, batch size 8. *The iteration count was set on the command line and should be confirmed.* At inference the image and its mirror image are averaged, and a low peak score shows a "low confidence" note. The model was exported to ONNX (opset 17), checked against PyTorch to within 10⁻⁵, and runs in the browser with onnxruntime-web, so the image is never uploaded.

#### 4.4 Lumbar lordosis (tried, not released)

A 4-point model (L1 and S1 superior endplates, same architecture and training as 4.3, 384 × 384 input) was trained on the BUU-LSPINE images of the Mendeley set that had at least 6 labeled bodies, and tested on 192 held-out images. Two alternatives that use the vertebral corner detector of 4.2 to count levels up from S1 were also tested. None was accurate enough to release (section 7). The result is reported so it is not repeated.

#### 4.5 Lisfranc interval measurement review

A reader-measurement tool and OHIF viewer extension built by collaborator Ibraheem Shaikh, using public foot radiographs (UNIFESP X-ray Body Part, CC BY-NC-SA 4.0; HVAngleEst, CC BY 4.0). Readers place C1 and M2 landmarks, and the tool measures the Lisfranc interval. Its methods are documented in the author's repository.

</details>

<details>
<summary><b>5. Evaluation metrics and statistics</b></summary>

- **Segmentation.** Dice similarity coefficient, 95th-percentile Hausdorff distance (HD95, mm), and volume error relative to the expert contour, reported as median and interquartile range.
- **Radiomics.** ICC(1,1), one-way random effects, single measurement; ≥ 0.90 counted as excellent and ≥ 0.75 as good.
- **Landmarks.** Euclidean point error in mm (simulated radiographs), in working pixels (about 1 mm on the resized real radiographs), and as a percentage of body height or inter-triradiate distance.
- **Vertebral morphometry.** Mean absolute error of Ha, Hm and Hp (mm) and of maximum height loss (percentage points). Fracture detection (any Genant grade ≥ 1) against the CT reference: sensitivity and specificity. Grade agreement: exact, within one grade, and linear-weighted Cohen's kappa.
- **Infant hip.** Acetabular index absolute error (mean, median, 90th percentile, percentage within 3° and 5°, and bias). IHDI exact agreement per hip, and sensitivity and specificity for IHDI ≥ II. The reference IHDI grade was computed from the expert landmarks with the same geometry.
- **Lordosis.** Correct-level rate for L1 and S1, and L1–S1 angle error.
- No formal hypothesis testing was done. These are descriptive baselines.

</details>

<details>
<summary><b>6. Results on held-out data</b></summary>

**Soft-tissue sarcoma (11 test patients).**

| Sequence | n | Dice, median (IQR) | HD95, median | Volume error, median | Robust features |
|---|---|---|---|---|---|
| MRI T1 | 11 | 0.74 (0.64–0.84) | 18.9 mm | +15% | 23 of 107 |
| MRI T2FS/STIR | 11 | 0.75 (0.55–0.88) | 21.1 mm | +4% | 26 of 107 |
| CT of PET/CT | 10 | 0.48 (0.07–0.56) | 46.1 mm | −6% | 30 of 107 |

Without post-processing the median Dice was 0.41 (T1), 0.49 (T2FS/STIR) and 0.25 (CT). The two-sequence consensus raised the MRI median Dice from about 0.63 (largest component alone) to about 0.74. One small tumor (80 mL) was missed on every sequence. Almost every feature was stable under mask perturbation (ICC ≥ 0.90 for 99–107 of 107).

**Vertebral morphometry, simulated radiographs (8 CTs, 74–75 gradable levels).** Median landmark error 1.3–1.8 mm (mean about 2.0 mm). Height error 1.5 / 1.9 / 1.5 mm (Ha / Hm / Hp). Maximum height loss within about 7 percentage points. Posterior wall displacement error 0.9 mm. Fracture detection: sensitivity 6 of 14 (43%), specificity 95–97%, weighted kappa 0.43–0.49 (v0.1 and v0.2).

**Vertebral morphometry, real radiographs (204 images, 1,449 bodies).** Training on simulated images only found 52% of bodies (median corner error 4.1 px, 13% of body height). Adding real images (v0.2) found 91% (median 2.5 px, 7.9% of body height; 90th percentile 9.3 px). These images have no fracture labels.

**Infant hip (731 test images, 1,462 hips; 679 images after removing the dataset's listed outliers).**

| | All images | Without listed outliers |
|---|---|---|
| Landmark error, median | 2.1–2.8 px (about 1% of the inter-triradiate distance) | 2.1–2.7 px |
| Acetabular index, mean absolute error | 2.4° | 2.0° |
| Within 3° / 5° | 76% / 92% | 79% / 94% |
| IHDI exact agreement per hip | 92% | 94% |
| IHDI ≥ II: sensitivity / specificity | 69% / 97% | 67% / 98% |

Grade II (subluxation) was the weakest category.

**Lumbar lordosis (192 test images).** The direct model found the correct L1 in 41% of images (mean angle error 21°). Counting up from S1 with the corner detector chose both levels correctly in 65% (mean error 11°; 8° when both levels were correct).

</details>

<details>
<summary><b>7. Limitations</b></summary>

- Small training sets and short CPU training schedules. All results are baselines, not the ceiling of each method.
- Each model was trained and tested on a single public dataset. Performance on other scanners, populations and positioning is unknown, and external validation is needed.
- The tumor CT model was trained on the low-dose CT of PET/CT and is not yet usable. The MRI model needs review and editing before any use.
- Vertebral fracture grading has been tested only on simulated radiographs, with 14 reference fractures. The reference is CT midsagittal morphometry, and some of the gap between it and the radiograph reflects projection physics, not only model error.
- The real spine radiographs were resized by the publisher, distorting the aspect ratio, so pixel-to-mm conversions are approximate.
- The hip dataset is split by image, not by patient, and reference IHDI grades come from the same landmarks rather than an independent reading.
- No reader study has been done.

</details>

<details>
<summary><b>8. Data sources and references</b></summary>

| Dataset | Used for | License |
|---|---|---|
| TCIA Soft-tissue-Sarcoma (Vallières et al., Phys Med Biol 2015), via NCI Imaging Data Commons | Tumor segmentation and radiomics | CC BY 3.0 |
| VerSe 2019 (Sekuboyina et al., Med Image Anal 2021; Löffler et al., Radiol Artif Intell 2020) | CT reference and simulated radiographs | CC BY-SA 4.0 |
| Spondylolisthesis Vertebral Landmark, Mendeley Data, doi:10.17632/5jdfdgp762.1 (BUU-LSPINE, Burapha University) | Real lateral lumbar radiographs; lordosis | CC BY 4.0 |
| MTDDH (Sci Data 2025, doi:10.1038/s41597-025-05146-x), via Open Hip Dysplasia | Infant hip landmarks | CC BY 4.0 |
| UNIFESP X-ray Body Part (Kitamura) and HVAngleEst | Lisfranc review tool | CC BY-NC-SA 4.0 and CC BY 4.0 |

Methods references: Isensee F, et al. nnU-Net. Nat Methods 2021;18:203–11. van Griethuysen JJM, et al. PyRadiomics. Cancer Res 2017;77:e104–7. Zwanenburg A, et al. IBSI. Radiology 2020;295:328–38. Zwanenburg A, et al. Assessing robustness of radiomic features by image perturbation. Sci Rep 2019;9:614. Genant HK, et al. J Bone Miner Res 1993;8:1137–48. Zhou X, et al. Objects as points (CenterNet). arXiv:1904.07850, 2019. Lin TY, et al. Focal loss. ICCV 2017.

Code, configuration files and saved results for each project are linked from its card below.

</details>
