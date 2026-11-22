# Vertebral morphometry on lateral radiographs: public-data baseline (v0.1)

**Research use only. Not for clinical use.** No BIDMC or patient data was used.

Open `index.html` in any browser. It works offline as a single file, with no network calls.

## What it does
- **Height loss.** It finds 6 points per vertebral body: the anterior, middle and posterior points on the superior and inferior endplates. From these it computes the anterior, middle and posterior heights (Ha, Hm, Hp). It compares each height with the **expected normal height**, interpolated from the nearest non-fractured vertebra above and below (weighted by level distance, or taken from one side at the ends). It reports % loss for each height, the max loss, the **Genant** grade (<20% normal, 20–25% grade 1, 25–40% grade 2, >40% grade 3) and the morphology (wedge, biconcave or crush). It also reports the Ha/Hp and Hm/Hp ratios. C1 and C2, and bodies cut by the image edge, are not graded.
- **Retropulsion (radiographic proxy).** Posterior wall displacement (PWD, in mm) is how far the posterior wall sits behind the line joining the posterior-wall midpoints of the adjacent vertebrae. Sagittal canal compromise % uses the posterior-wall midpoint and the spinolaminar point (a 7th landmark), compared with the adjacent levels.
- **Viewer.** It has a worklist, editable points with live recalculation, a CT-reference overlay, an agreement panel and CSV export. You can open your own PNG/JPEG, which stays in the browser. Place points with "Add vertebra", set mm/px, and double-click a row to set the level name.

## Data and models (all public)
| Item | Source | License |
|---|---|---|
| CT scans + vertebra masks | VerSe 2019 (Sekuboyina et al. 2021; Löffler et al. 2020), github.com/anjany/verse | CC BY-SA 4.0 (data), MIT (code) |
| Landmark model | Trained here from scratch (small U-Net / CenterNet-style with per-point heatmaps, 0.5M params, CPU) | Ours |

There's no public pretrained lateral-spine corner model that fit this task. The lateral radiographs used here are **simulated** (digitally reconstructed radiographs, made by projecting each CT sideways). This is because NHANES II's spine X-rays are no longer available from NLM's download site, and BUU-LSPINE and VinDr-SpineXR need access requests. Images derived from VerSe are shared under CC BY-SA 4.0.

## Pipeline (`source/`)
1. `ct_reference.py`: takes the midsagittal slab of each VerSe vertebra mask, finds the body, orients it, then picks the 6 corner and endplate points, the posterior wall profile and the spinolaminar point. This gives the **CT reference**.
2. `drr.py`, `build_drr_set.py`: make a lateral parallel projection at 1.0 mm/px (whole body, plus a midline slab variant). The reference points transfer exactly onto it.
3. `model.py`, `train.py`: train on 26 CTs (52 images), with augmentation and oversampling of deformed bodies. The weights are in `vertebra_landmark_net.pt`.
4. `infer.py`, `evaluate.py`: detect, refine and evaluate on 8 held-out CTs (`drr_test_ids.json`).
5. `morph.py`, `web/morph.js`: the same measurement engine in Python and JavaScript, checked to agree on all 863 VerSe 2019 levels. `build_viewer.py` builds `index.html`.

## Results on held-out simulated radiographs (8 cases, 75 gradable levels, whole-body projection)
- Landmark error: median about **1.5–1.8 mm** per point, mean about 2.0 mm.
- Height error (mean absolute): Ha 1.4, Hm 2.0, Hp 1.6 mm. Max height loss is within **7.0 percentage points** on average.
- PWD error 0.9 mm (mean absolute). Canal compromise is within 3.2 percentage points.
- Fracture (any grade ≥1) against CT reference: sensitivity **6/14 (43%)**, specificity **59/61 (97%)**. Exact grade agreement 81%, within one grade 88%, weighted kappa 0.43.

## Limitations (read before showing anyone)
- **Small test set** (8 cases, 14 reference fractures) on **simulated** images. Real radiographs (with magnification, scatter, positioning, rotation and overlapping ribs) will be harder. A real-radiograph test set is the next step.
- The reference is morphometry on the **CT midsagittal slice**. Most misses were biconcave deformities. On a projection the endplate rims overlap the central depression, so radiographic Hm runs high. Some of this gap is the physics of radiographs, not only model error.
- About 1.5–2 mm of point error is 6–8% of a 25 mm body, so cases near the 20% threshold are unstable. Showing the numbers and letting you drag points is intentional.
- Retropulsion on a radiograph is a **midline sagittal estimate**. It gives no canal area and misses fragments off the midline. CT stays the reference.
- In the demo, level names come from the reference. A real workflow needs one anchor level set by the user.
- mm values on your own images need correct pixel spacing and a magnification correction. % values don't.

## Next steps
Request BUU-LSPINE and VinDr-SpineXR to test on real radiographs. Add all VerSe 2019 and 2020 CTs to training. Add DICOM loading and automatic level labeling from the sacrum.
