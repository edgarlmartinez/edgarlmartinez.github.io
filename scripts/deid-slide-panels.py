#!/usr/bin/env python3
"""Cut image panels out of lecture-slide screenshots and de-identify them.

Usage: python3 scripts/deid-slide-panels.py SPEC.json SRC_DIR OUT_DIR

SPEC.json is a list of {"src": "slide.png", "box": [x0, y0, x1, y1], "out": "name.png",
"mask": [[x0, y0, x1, y1], ...]}. Boxes and masks are in slide pixel coordinates.
Only the image panel is kept (slide titles, ages and captions are dropped). Masks are
filled with the median of the surrounding pixels. Each panel is then intensity-normalized
(one window for all channels, so colored arrowheads keep their color), resampled to 95%
(max 900 px), given faint noise so every pixel value changes, and saved as a new PNG
without any metadata.
"""
import json, os, sys
import numpy as np
from PIL import Image

spec, src_dir, out_dir = sys.argv[1:4]
rng = np.random.default_rng()
for item in json.load(open(spec)):
    im = Image.open(os.path.join(src_dir, item['src'])).convert('RGB')
    x = np.asarray(im.crop(tuple(item['box']))).astype(np.float32)
    ox, oy = item['box'][:2]
    for m in item.get('mask', []):
        x0, y0, x1, y1 = m[0] - ox, m[1] - oy, m[2] - ox, m[3] - oy
        ring = np.concatenate([x[max(y0 - 6, 0):y0, x0:x1].reshape(-1, 3), x[y1:y1 + 6, x0:x1].reshape(-1, 3)])
        x[y0:y1, x0:x1] = np.median(ring, axis=0)
    gray = x.mean(axis=2)
    lo, hi = np.percentile(gray, [0.2, 99.8])
    x = np.clip((x - lo) / max(hi - lo, 1) * 255, 0, 255)
    out = Image.fromarray(x.astype(np.uint8), 'RGB')
    f = min(0.95, 900 / max(out.size))
    out = out.resize((round(out.width * f), round(out.height * f)), Image.LANCZOS)
    y = np.asarray(out).astype(np.float32) + rng.normal(0, 1.5, (out.height, out.width, 1))
    out = Image.fromarray(np.clip(y, 0, 255).astype(np.uint8), 'RGB')
    Image.frombytes('RGB', out.size, out.tobytes()).save(os.path.join(out_dir, item['out']), optimize=True)
    print('wrote', item['out'], out.size)
