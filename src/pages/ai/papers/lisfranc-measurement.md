---
layout: ../../../layouts/Paper.astro
title: An open radiologist-in-the-loop tool for Lisfranc measurements on AP and lateral foot radiographs
short: Lisfranc measurement review tool
description: Preprint draft. A structured, radiologist-reviewed workflow for C1–M2 and related Lisfranc measurements, as an offline demo and OHIF extensions.
authors: Ibraheem Shaikh and Edgar L. Martinez Salazar, MD (author list and affiliations to be finalized). Department of Radiology, Beth Israel Deaconess Medical Center, Harvard Medical School, Boston, MA.
updated: November 2026
---

## Abstract

**Purpose:** To describe an open, radiologist-in-the-loop software tool for measuring Lisfranc (tarsometatarsal) alignment on AP and lateral foot radiographs, and its integration into the OHIF DICOM viewer.

**Materials and Methods:** The tool supports a primary AP C1–M2 interval measured by a three-point tangent method, plus optional findings: a lateral dorsal C2–M2 step-off, an AP medial C2–M2 offset, dorsal soft-tissue depth, a dorsal-to-plantar bone-depth ratio, an avulsion-fragment marker and a four-corner M2 proxy. AI-generated draft landmarks are shown only as proposals that a radiologist must review, correct and approve, and a blind mode hides them. A self-contained offline demo bundles 25 public foot radiographs (10 UNIFESP AP/lateral pairs, CC BY-NC-SA 4.0; 5 HVAngleEst v5 images, CC BY 4.0). Two OHIF extensions (for OHIF 3.7.0 and v3.11.0) share a clinical API and database schema for study claims, corrected reviews, revision history and CSV enrollment.

**Results:** Accuracy and reader-agreement results are not yet available. The software runs offline in Chrome or Edge, exports reviews as JSON and CSV, and records measurements in pixel units because the public images lack reliable calibration.

**Conclusion:** The tool provides a reproducible workflow for collecting radiologist-corrected Lisfranc measurements, which can serve as reference data for future validation and model development.

**Keywords:** Lisfranc injury; tarsometatarsal joint; foot radiograph; measurement software; OHIF; human-in-the-loop; open data

## 1. Introduction

Lisfranc injuries disrupt the tarsometatarsal joint complex and are easy to miss on radiographs, especially when subtle or non-weight-bearing. Diagnosis relies on small measurements of alignment between the medial cuneiform (C1), intermediate cuneiform (C2) and second metatarsal base (M2), which vary with projection and between readers.

Automated measurement needs reference data that radiologists have placed or corrected, and few public datasets provide it. We built a measurement and review tool that captures these findings in a structured, reproducible way, shows AI-drafted landmarks only as proposals, and runs both offline and inside a clinical DICOM viewer.

**Objectives**

1. Define a structured set of Lisfranc measurements on AP and lateral foot radiographs, with explicit landmark rules.
2. Build a review workflow in which a radiologist checks, corrects and approves every measurement, including AI-drafted ones.
3. Provide an offline demo on openly licensed radiographs and OHIF extensions for clinical-research deployment.

## 2. Materials and methods

### 2.1 Images

| Source | Images | License | Use |
|---|---|---|---|
| UNIFESP X-Ray Body Part Classification Dataset (F. Kitamura) | 10 paired AP/lateral studies | CC BY-NC-SA 4.0, noncommercial | Main paired demo set |
| HVAngleEst v5 (Wang Q et al., doi:10.57760/sciencedb.19819) | 5 AP images | CC BY 4.0 | Original AP pilot cases |
| Lateral teaching image (Mikael Häggström, MD) | 1 lateral image | CC0 | Separate lateral example, kept outside the 25 |

UNIFESP images are released at 256 × 256 pixels. Their DICOM ViewPosition and laterality tags are blank, so AP and lateral views were assigned by AI curation from the image and visible markers, pending radiologist confirmation. Source patient groups are anonymous dataset identifiers, and no attempt was made to identify patients.

**Image handling.** Original DICOM bytes are preserved, and file hashes were verified. Display PNGs use a linear min/max window and MONOCHROME1 inversion on the unchanged pixel grid, with no crop, flip, geometric transform or overlay removal. Measurements are recorded in pixel units because the public images have no reliable physical calibration.

### 2.2 Measurements

The primary measurement is on the AP view; the others are optional and recorded separately. Missing or obscured findings are stored as incomplete, never as zero.

| Finding | View | Landmarks and rule |
|---|---|---|
| C1–M2 interval (primary) | AP | Points A and B define the C1 lateral reference line; point T is the medial M2 base. The interval is measured by tangent from T to line A–B. |
| Medial C2–M2 offset (optional) | AP | Two points on the medial C2 cortex, then the corresponding medial M2 cortex. Direction recorded separately. |
| Dorsal C2–M2 step-off | Lateral | M2 is traced to its recessed TMT joint. Two dorsal C2 reference points, then the dorsal M2 base. The uppermost M1 contour is not used. Direction recorded separately. |
| Dorsal soft-tissue depth | Lateral | At the M2 base, from dorsal cortex to outer skin along the cortical normal. Total soft tissue, not to a dressing or cast. |
| Bone-depth ratio (optional) | Lateral | Dorsal then plantar cortex at the same M2 level, same view. Optional ratio denominator. |
| Avulsion fragment marker (optional) | AP or lateral | Location marker. Absence is distinct from not assessed. |
| Four-corner M2 proxy (optional) | AP | Four M2 base corners as an alternative proxy. |

### 2.3 AI draft proposals

Draft landmarks for the demo cases were produced by general-purpose AI agents, with a separate revision pass for the lateral landmarks. Each draft carries a written rationale, an uncertainty note for each landmark, and an uncalibrated 0–1 visual self-rating that is not a probability of correctness. Drafting agents did not see earlier model, reference or coordinator annotations. All drafts are labeled "not expert truth" and require radiologist review.

### 2.4 Review workflow

- The reviewer enters a name and chooses a workflow: precise measurements, or a lighter review.
- Proposals are shown as editable handles. In blind mode they are hidden, and any prior exposure to a proposal is disclosed for that case.
- Handles are dragged or nudged by keyboard (1 pixel, or 5 with Shift); directions follow the original image.
- Approval requires valid landmarks and a recorded cortex relationship, and a reminder appears before the first paired-view approval. Viewing an image does not confirm its measurements.
- Reviews autosave locally (demo) or to the server (OHIF), with conflict handling across tabs, and export as JSON and CSV.

### 2.5 Software

**Offline demo:** a single HTML file (`demo/Lisfranc-Review.html`) with embedded images, run in current Chrome or Edge without a server.

**OHIF extensions:** two alternative packages named `@msk/extension-lisfranc`, one per viewer build.

| OHIF viewer | Extension | Stack |
|---|---|---|
| 3.7.0 (commit 5ddf8a1, upstream 3.7.0-beta.110) | 0.2.2-ohif3.7.0 | React 17.0.2, Cornerstone 1.20.3 |
| v3.11.0 (commit 522531c) | 0.2.1 | React 18.3.1, Cornerstone 3.32.5 |

The 3.7 backport blocks measurement on multiframe local files and WADO-URI, because the pinned loader can display the wrong frame; multiframe studies use WADO-RS. Both packages share a clinical API and database schema for study claims, corrected reviews, revision history and CSV enrollment.

## 3. Results

Accuracy, reader-agreement and timing results are not yet available; this section reports the dataset and software.

**Dataset.** The demo contains 25 radiographs: 10 UNIFESP AP/lateral pairs (20 images) and 5 HVAngleEst AP images. AI drafts were produced for the paired cases. Their written notes repeatedly flag the same limits: at 256 × 256 pixels, C1 facet endpoints blur over a few pixels, M2 and C2 overlap other cuneiform and metatarsal contours on the lateral view, the plantar M2 cortex often cannot be separated from superimposed bones, and small avulsion fragments cannot be excluded. In at least one lateral case the draft was recorded as partial, with roughly 4–6 pixels of uncertainty.

**Software.** Both OHIF packages open the same offline demo and share one clinical API and schema. Both pinned OHIF hosts include dependencies with published security advisories (dcmjs GHSA-px68-xx5g-48q5; Swiper GHSA-hmx5-qpq5-p643), which each site must review before deployment.

**Planned evaluation:** inter- and intra-reader agreement for the C1–M2 interval and dorsal step-off; agreement of AI drafts with radiologist-approved landmarks; and assisted versus blind review time and agreement.

## 4. Discussion

The tool turns Lisfranc assessment into a set of explicitly defined landmarks with recorded uncertainty, so every measurement can be traced, corrected and compared between readers. Its design favors reference-data quality over automation: AI drafts are only proposals, a blind mode supports unbiased reader studies, unassessed findings are never treated as normal, and approval requires an explicit cortex relationship rather than a glance at the image.

The lateral view is the hardest part. At low resolution the M2 base, C2 and M1 contours overlap, which is why the tool requires tracing M2 to its recessed TMT joint and excludes the uppermost M1 contour. Full-resolution clinical images should reduce this, but the same rules apply.

Running inside OHIF lets the same workflow be used on clinical DICOMweb sources, with server-side revision history for multi-reader studies.

## 5. Limitations

- No accuracy, agreement or clinical outcome data yet.
- Demo images are low resolution (256 × 256) and uncalibrated, so measurements are in pixels, not millimetres.
- AP/lateral view assignment and weight-bearing status of the public images are not radiologist confirmed.
- The public set is small.
- AI drafts come from general-purpose agents with uncalibrated self-ratings, not a validated model.
- The pinned OHIF builds carry dependency security advisories that sites must patch.
- UNIFESP images are noncommercial only (CC BY-NC-SA 4.0).

## 6. Conclusion

We describe an open, radiologist-in-the-loop tool for structured Lisfranc measurements on AP and lateral foot radiographs, available as an offline demo and as OHIF extensions. It is designed to collect corrected, traceable reference measurements; its accuracy and its value as an AI-assisted reading aid remain to be tested.

## Data and code availability

Code, offline demo and image credits: [github.com/rightawayileft/lisfranc-measurement](https://github.com/rightawayileft/lisfranc-measurement). Demo images are redistributed under their original licenses (CC BY-NC-SA 4.0, CC BY 4.0, CC0).

## References

1. Kitamura F. UNIFESP X-Ray Body Part Classification Dataset. Kaggle.
2. Wang Q, et al. HVAngleEst v5. Science Data Bank. doi:10.57760/sciencedb.19819.
3. Ziegler E, et al. Open Health Imaging Foundation Viewer: an extensible open-source framework for building web-based imaging applications. JCO Clin Cancer Inform. 2020.

*Preprint draft for open review. Not peer reviewed. Research use only; not for clinical use.*
