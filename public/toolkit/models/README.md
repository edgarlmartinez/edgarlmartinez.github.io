# Automatic landmark models (research and education only)

This small model proposes landmarks in the toolkit's "Measure an image" view. They run in the browser with onnxruntime-web (loaded from jsDelivr); the image is never uploaded. Every proposed point is an ordinary, draggable point, and the usual engine computes and grades the result. **Not a medical device. Not for clinical use.**

| File | Measurement | Input | Output |
|---|---|---|---|
| `infant-hip-v1.onnx` | Acetabular index (right, left) and IHDI grade | Grayscale AP pelvis, letterboxed to 320 × 480 | 8 landmark heatmaps at stride 2 |

It is a small U-Net (about 1.1M parameters, 4.4 MB) trained from scratch on a CPU with focal heatmap loss and heavy augmentation (scale, rotation, shift, mirroring, gamma, contrast, blur, noise, inversion). At run time the image and its mirror image are both run, and the heatmaps are averaged. A low peak score triggers a "low confidence" note.

## Infant hip (`infant-hip-v1.onnx`)

**Data:** MTDDH pelvic radiographs (Scientific Data 2025, doi:10.1038/s41597-025-05146-x), as repackaged by the Open Hip Dysplasia project (github.com/radoss-org/open-hip-dysplasia), **CC BY 4.0**. Infants and toddlers aged 5–40 months. 8 landmarks: for each hip, the lateral edge of the acetabular roof, the triradiate (Hilgenreiner) point, the top of the femoral head ossific nucleus, and the H-point (midpoint of the top of the metaphysis). The packaged split was used as is: 731 training, 365 validation (unused), 731 test images. Splits are by image; the release has no patient identifiers.

**Held-out test (731 images, 1,462 hips; 679 images after removing the dataset's listed frog-leg, wrong-body-part and implant outliers):**

| | All | Without listed outliers |
|---|---|---|
| Landmark error, median | 2.1–2.8 px (about 1% of the inter-triradiate distance) | same |
| Acetabular index, mean absolute error | 2.4° | **2.0°** |
| Acetabular index, median absolute error | 1.6° | 1.5° |
| Within 3° / 5° | 76% / 92% | 79% / 94% |
| Bias | +0.3° | +0.2° |
| IHDI grade, exact agreement per hip | 92% | **94%** |

IHDI grade by reference grade (without outliers): grade I 1,170 of 1,189 correct; grade II 62 of 120 correct (55 called grade I); grade III 22 of 25; grade IV 22 of 24. Every grade III or IV hip was called grade II or higher. The reference IHDI grade is computed from the expert landmarks with the same geometry, not taken from a separate reading. **Grade II (subluxation) is where the model is weakest.**

The 5.6% of images with a low peak score (under 0.15) had a mean worst-side acetabular index error of 11.9°, against 3.0° for the rest, so the "low confidence" note is worth heeding.

## Lumbar lordosis: tried, not released

A lordosis model was trained on the public "Spondylolisthesis Vertebral Landmark" set (Mendeley Data, doi:10.17632/5jdfdgp762.1, CC BY 4.0; BUU-LSPINE images). It is **not** in the toolkit because it is not accurate enough. On 192 held-out lateral lumbar radiographs:

- A direct 4-point model (L1 and S1 superior endplates) found the right L1 only 41% of the time; mean lordosis error 21°.
- The vertebral corner detector from the vertebral morphometry demo, counting up from S1, picked both levels correctly in 65% of images; mean error 11° overall and 8° even with the right levels, mostly from the S1 endplate (systematic 6° rotation).

Likely causes: only about 270 training images with L1 to S1 labelled, images squashed to 640 × 640 by the publisher, and S1 labelled as a box rather than an endplate. The full-resolution BUU-LSPINE release (access request) is the next step.

## Limitations

- Trained and tested on one public dataset; performance on other equipment, populations and positioning is unknown.
- The model does not know when it is given the wrong view. Pick the measurement first, then add the image.
- No age-specific acetabular index norms are applied; the bands are general guides and are marked as varying in the literature.

## Rebuilding

Training, evaluation and export scripts are kept with the project files (`ai-projects/toolkit-auto-landmarks/`). Export uses `torch.onnx.export` (opset 17), checked against PyTorch to within 1e-5, and the browser decoder was checked against the Python decoder on the same image.
