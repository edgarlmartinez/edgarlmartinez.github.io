# MSK tumor segmentation and radiomics on CT and MRI: public-data baseline (v0.1)

**Research use only. Not for clinical use.** No BIDMC or patient data was used.

Open `index.html` in any browser. It works offline as a single file, with no network calls.

## What it does
- **Automatic segmentation.** nnU-Net v2 (3D full resolution), the same self-configuring framework that TotalSegmentator is built on. There are two models: one contrast-agnostic MRI model (T1 and T2FS/STIR pooled) and one CT model. The output is the tumor mask (GTV). On MRI, a **two-sequence consensus** keeps only the predicted components that T1 and T2FS/STIR agree on (the other sequence's mask is resampled in physical space); with one sequence, or on CT, the largest connected component is kept. On the held-out MRI this raised the median Dice from about 0.63 (largest component alone) to about 0.74.
- **Volumetrics.** Volume (mL), longest axial diameter with its perpendicular, and craniocaudal extent.
- **Texture features.** PyRadiomics 3.1 (IBSI-aligned definitions): shape, first order, GLCM, GLRLM, GLSZM, GLDM and NGTDM, 107 features on the original image.
- **Robustness filter.** A feature is flagged *robust* when ICC(1,1) is at least 0.90 under mask perturbation (1-voxel erosion, 1-voxel dilation, and two random ~2 mm contour jitters, after Zwanenburg et al., Sci Rep 2019) on all 51 patients, **and** ICC is at least 0.75 between automatic and expert masks on the held-out patients.
- **Viewer.** It has a worklist of the held-out patients, expert and automatic contour overlays, a brush to correct the automatic mask with live volume, Dice and diameter updates, the feature table with ICCs, and CSV export.

## Normalization (per modality)
| | CT | MRI (T1, T2FS/STIR) |
|---|---|---|
| Intensity | Hounsfield units unchanged | N4 bias-field correction inside a body mask, then z-score over the body |
| Resegmentation | −200 to 400 HU (keeps fat for lipomatous tumors, drops air and cortical bone) | ±3 SD |
| Discretization | Fixed bin **width** 25 HU | Fixed bin **number** 32 |
| Resampling | 1 × 1 × 3 mm, B-spline | 1 × 1 mm in plane, slice spacing unchanged; 2D texture aggregated over slices (slices are 4–15 mm) |

The settings live in `source/params/ct.yaml` and `source/params/mr.yaml`.

## Data (all public)
| Item | Source | License |
|---|---|---|
| 51 extremity soft-tissue sarcomas: T1, T2FS/STIR, CT of FDG-PET/CT, expert GTV contours (RTSTRUCT) | TCIA *Soft-tissue-Sarcoma* (Vallières M, et al. Phys Med Biol 2015;60:5471), via NCI Imaging Data Commons (`idc-index`) | CC BY 3.0 |

The split is 40 training and 11 held-out patients (random, seed 42, by patient, so the same patients are held out for every sequence). One CT contour (STS_046) did not map onto its CT and is excluded from the CT results. The CT is the low-dose attenuation CT of PET/CT, so the CT numbers are a lower bound for diagnostic CT.

## Pipeline (`source/`)
1. `convert_sts.py`: reads DICOM and RTSTRUCT and rasterizes the native T1, T2FS/STIR and CT contours to NIfTI (1 = mass, 2 = edema).
2. `make_nnunet_datasets.py`: builds the nnU-Net raw datasets and the fixed patient split.
3. nnU-Net v2 planning, preprocessing and training (commands below).
4. `radiomics_pipeline.py`: normalization, feature extraction, volumetrics, mask perturbation and ICC.
5. `stability.py`: perturbation ICC on the expert masks of all 51 patients.
6. `evaluate.py`: Dice, HD95 and volumes on the held-out patients, auto-vs-expert feature ICC, and the robust flag.
7. `export_viewer.py` and `build_viewer.py`: pack the held-out cases into the single-file viewer.

## Results on the 11 held-out patients
| Sequence | n | Dice, median (IQR) | HD95, median | Volume error, median | Robust features |
|---|---|---|---|---|---|
| MRI T1 | 11 | 0.74 (0.64–0.84) | 18.9 mm | +15% | 23 of 107 |
| MRI T2FS/STIR | 11 | 0.75 (0.55–0.88) | 21.1 mm | +4% | 26 of 107 |
| CT (of PET/CT) | 10 | 0.48 (0.07–0.56) | 46.1 mm | −6% | 30 of 107 |

Without post-processing the median Dice was 0.41 (T1), 0.49 (T2FS) and 0.25 (CT): the short training leaves many false-positive islands. **One patient (STS_012, a small 80 mL tumor) was missed on every sequence**, and on CT the largest component was the wrong structure in 3 of 10 patients. MRI is usable as a starting contour that needs review; CT is not yet usable. Almost every feature was stable under small mask perturbations (ICC ≥ 0.90 for 99–107 of 107). The stricter filter is agreement between automatic and expert masks. With only 11 patients those ICCs are noisy, so treat the robust lists (`source/results/stability.csv`) as provisional.

## Using the models
The weights in `source/models/` are standard nnU-Net v2 model folders (optimizer state removed).
```bash
pip install nnunetv2   # then copy source/nnUNetTrainerCPU.py into nnunetv2/training/nnUNetTrainer/variants/
nnUNetv2_predict_from_modelfolder -i <folder of *_0000.nii.gz> -o <out> -m source/models/mri -f all -device cpu
```
Then run `radiomics_pipeline.py` (`prepare`, `extract`, `volumetrics`) on the image and mask.

## Training here vs. the full recipe
This build was trained on a 4-core CPU with no GPU, so it uses a **shortened schedule** (`nnUNetTrainerCPU`: 40 epochs × 100 iterations, about 4,000 iterations, versus nnU-Net's default 1,000 × 250 = 250,000) and a **lighter network** (16–192 features per stage, smaller patches, at 1.4 × 1.4 × 5.2 mm for MRI and 2 × 2 × 4 mm for CT). The held-out Dice is therefore a floor, not what the framework can reach.

To train the full recipe on a GPU (about a day per model on one modern GPU):
```bash
export nnUNet_raw=... nnUNet_preprocessed=... nnUNet_results=...
python source/convert_sts.py <dicom_dir> <nifti_dir>
python source/make_nnunet_datasets.py <nifti_dir> $nnUNet_raw   # then pool T1 + T2FS into Dataset604 as in this repo
nnUNetv2_plan_and_preprocess -d 601 604 --verify_dataset_integrity
for f in 0 1 2 3 4; do nnUNetv2_train 604 3d_fullres $f; nnUNetv2_train 601 3d_fullres $f; done
nnUNetv2_find_best_configuration 604 -c 3d_fullres
```
With more data (WORC, 930 patients, needs an XNAT account; or institutional cases), fine-tune from these weights with `nnUNetv2_train ... -pretrained_weights`.

## Next steps
- Add WORC (lipoma vs. liposarcoma, desmoid, myxofibrosarcoma, GIST, CRLM) for broader MSK tumor types.
- Use an interactive model (InteractiveNet or MedSAM2) for click-based correction instead of the brush.
- Add a peritumoral edema label on T2FS/STIR (the data has it; it was left out of this short training run).
