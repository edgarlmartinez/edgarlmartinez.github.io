"""Texture + volumetric analysis for MSK tumors on CT and MRI (research use only).

Normalization (per modality):
  CT  : raw HU, fixed bin width 25 HU, resegmentation [-200, 400] HU.
  MRI : N4 bias-field correction inside a body mask -> z-score over the body ->
        fixed bin number (32), 3-SD resegmentation, 2D texture (thick slices).
Features: PyRadiomics (IBSI-compliant definitions) on the tumor label.
Stability: features are re-extracted on perturbed masks (erode / dilate / random
contour jitter); ICC(1,1) across perturbations flags robust features.
"""
import logging, os
import numpy as np, SimpleITK as sitk
from scipy import ndimage
from radiomics import featureextractor
logging.getLogger('radiomics').setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = {'CT': os.path.join(HERE, 'params', 'ct.yaml'), 'MR': os.path.join(HERE, 'params', 'mr.yaml')}

def body_mask(img):
    """Body (non-air) mask: low threshold relative to the 99th percentile, fill holes per slice.
    Otsu is avoided because fat-suppressed sequences make fat as dark as air."""
    a = sitk.GetArrayFromImage(img).astype(np.float32)
    t = a > 0.08 * np.percentile(a, 99)
    t = ndimage.binary_opening(t, structure=np.ones((1, 3, 3)), iterations=2)
    t = np.stack([ndimage.binary_fill_holes(ndimage.binary_closing(s, iterations=3)) for s in t])
    m = sitk.GetImageFromArray(t.astype(np.uint8)); m.CopyInformation(img)
    return m

def normalize_mr(img, n4=True):
    img = sitk.Cast(img, sitk.sitkFloat32)
    bm = body_mask(img)
    if n4:
        shrink = 4
        small = sitk.Shrink(img, [shrink, shrink, 1]); smallm = sitk.Shrink(bm, [shrink, shrink, 1])
        corr = sitk.N4BiasFieldCorrectionImageFilter(); corr.SetMaximumNumberOfIterations([50, 50, 30])
        corr.Execute(small, smallm)
        logbias = corr.GetLogBiasFieldAsImage(img)
        img = img / sitk.Exp(logbias)
    a = sitk.GetArrayFromImage(img); b = sitk.GetArrayFromImage(bm) > 0
    mu, sd = a[b].mean(), a[b].std() + 1e-6
    out = sitk.GetImageFromArray(((a - mu) / sd).astype(np.float32)); out.CopyInformation(img)
    return out

def prepare(img, modality):
    return sitk.Cast(img, sitk.sitkFloat32) if modality == 'CT' else normalize_mr(img)

_ext = {}
def extractor(modality):
    k = 'CT' if modality == 'CT' else 'MR'
    if k not in _ext: _ext[k] = featureextractor.RadiomicsFeatureExtractor(PARAMS[k])
    return _ext[k]

def extract(img_prepared, mask, modality):
    r = extractor(modality).execute(img_prepared, mask, label=1)
    return {k: float(np.real(v)) for k, v in r.items() if not k.startswith('diagnostics')}

def volumetrics(mask, label=1):
    a = sitk.GetArrayFromImage(mask) == label
    sp = np.array(mask.GetSpacing())[::-1]  # z,y,x
    vol = a.sum() * sp.prod() / 1000.0
    out = {'volume_ml': float(vol)}
    if a.sum() == 0: return out
    zz = np.where(a.any((1, 2)))[0]
    out['craniocaudal_extent_mm'] = float((zz.max() - zz.min() + 1) * sp[0])
    # longest axial diameter (max over slices of max in-plane Feret) and its perpendicular
    best = (0, 0)
    for z in zz:
        pts = np.argwhere(a[z]) * sp[1:]
        if len(pts) < 3: continue
        from scipy.spatial import ConvexHull
        try: h = pts[ConvexHull(pts).vertices]
        except Exception: h = pts
        d = np.sqrt(((h[:, None] - h[None]) ** 2).sum(-1)); i, j = np.unravel_index(d.argmax(), d.shape)
        if d[i, j] > best[0]:
            u = (h[j] - h[i]) / (d[i, j] + 1e-9); perp = h @ np.array([-u[1], u[0]])
            best = (d[i, j], perp.max() - perp.min())
    out['axial_long_axis_mm'], out['axial_short_axis_mm'] = map(float, best)
    return out

def perturb_masks(mask, n_random=4, seed=0):
    """Mask perturbations in the spirit of Zwanenburg et al. 2019 (Sci Rep)."""
    a = sitk.GetArrayFromImage(mask) == 1
    st = np.zeros((3, 3, 3), bool); st[1] = ndimage.generate_binary_structure(2, 1)  # in-plane only
    outs = {'erode1': ndimage.binary_erosion(a, st), 'dilate1': ndimage.binary_dilation(a, st)}
    rng = np.random.default_rng(seed)
    dist_in = ndimage.distance_transform_edt(a, sampling=mask.GetSpacing()[::-1])
    dist_out = ndimage.distance_transform_edt(~a, sampling=mask.GetSpacing()[::-1])
    sdf = dist_out - dist_in  # signed distance, mm (negative inside)
    for k in range(n_random):
        noise = ndimage.gaussian_filter(rng.standard_normal(a.shape), sigma=(1, 6, 6))
        noise = noise / (np.abs(noise).max() + 1e-9) * 2.0  # up to ~2 mm boundary jitter
        outs[f'jitter{k}'] = (sdf + noise) < 0
    res = {}
    for k, v in outs.items():
        if v.sum() < 10: continue
        m = sitk.GetImageFromArray(v.astype(np.uint8)); m.CopyInformation(mask); res[k] = m
    return res

def icc1(X):
    """ICC(1,1), one-way random effects. X: subjects x raters."""
    X = np.asarray(X, float); n, k = X.shape
    gm = X.mean(); rm = X.mean(1)
    msb = k * ((rm - gm) ** 2).sum() / (n - 1)
    msw = ((X - rm[:, None]) ** 2).sum() / (n * (k - 1))
    return float((msb - msw) / (msb + (k - 1) * msw + 1e-12))
