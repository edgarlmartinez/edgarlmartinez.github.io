#!/usr/bin/env python3
"""De-identify a teaching image's pixel data.

Usage: python3 scripts/deid-image.py IN.png OUT.png [--mask x0,y0,x1,y1[,ring]]... [--color]

Masks are in original pixel coordinates. A mask is filled black, or with the median of
the surrounding pixels when ",ring" is added. The image is then intensity-normalized
(grayscale), resampled to 95% (max 900 px), given faint noise so every pixel value changes,
and saved as a new PNG without metadata.
"""
import argparse
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--mask', action='append', default=[])
ap.add_argument('--color', action='store_true')
a = ap.parse_args()
im = Image.open(a.src).convert('RGB' if a.color else 'L')
x = np.asarray(im).astype(np.float32)
for m in a.mask:
    p = m.split(','); x0, y0, x1, y1 = map(int, p[:4])
    if len(p) > 4 and p[4] == 'ring':
        ring = np.concatenate([x[max(y0-6, 0):y0, x0:x1].ravel(), x[y1:y1+6, x0:x1].ravel(),
                               x[y0:y1, max(x0-6, 0):x0].ravel(), x[y0:y1, x1:x1+6].ravel()])
        x[y0:y1, x0:x1] = np.median(ring)
    else:
        x[y0:y1, x0:x1] = 0
if not a.color:
    lo, hi = np.percentile(x, [0.2, 99.95]); x = np.clip((x - lo) / max(hi - lo, 1) * 255, 0, 255)
out = Image.fromarray(x.astype(np.uint8))
f = min(0.95, 900 / max(out.size))
out = out.resize((round(out.width * f), round(out.height * f)), Image.LANCZOS)
y = np.asarray(out).astype(np.float32) + np.random.default_rng().normal(0, 1.5, np.asarray(out).shape)
out = Image.fromarray(np.clip(y, 0, 255).astype(np.uint8), out.mode)
Image.frombytes(out.mode, out.size, out.tobytes()).save(a.dst, optimize=True)
print('wrote', a.dst, out.size)
