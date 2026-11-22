"""Simulated lateral radiographs (DRRs) from CT + landmark transfer.
Parallel-beam lateral projection through a 1 mm isotropic RAS volume, so the DRR
pixel grid equals the (A, S) landmark frame in mm (pixel spacing 1.0 mm, no magnification)."""
import numpy as np
from scipy import ndimage as ndi

def lateral_drr(ct, slab=None):
    """ct: HU volume (x=R, y=A, z=S). Returns float image [S rows (top = superior), A cols]."""
    mu = np.clip(ct.astype(np.float32) + 1000.0, 0, None) / 1000.0     # relative to water
    bone = np.clip(ct.astype(np.float32) - 150.0, 0, None) / 1000.0    # boost bone contrast like kV spectrum
    if slab is not None: mu, bone = mu[slab[0]:slab[1]], bone[slab[0]:slab[1]]
    p = 0.02 * mu.sum(0) + 0.06 * bone.sum(0)                          # line integrals (A, S)
    img = 1.0 - np.exp(-p * 0.35)
    img = img.T[::-1]                                                  # rows = S (top superior), cols = A
    lo, hi = np.percentile(img, [1, 99.7])
    return np.clip((img - lo) / (hi - lo + 1e-6), 0, 1)

def to_image_xy(pt, shape):
    """(A, S) landmark -> (col, row) in the DRR image."""
    return [pt[0], shape[0] - 1 - pt[1]]
