import sys, json, os, glob, numpy as np
sys.path.insert(0, '/home/user/vmorph')
from multiprocessing import Pool
from ct_reference import load_iso
from drr import lateral_drr, to_image_xy
KEYS = ('as', 'ai', 'ms', 'mi', 'ps', 'pi', 'sl')
lm = json.load(open('/home/user/data/verse/lm19.json'))
OUT = '/home/user/data/drr'
def work(f):
    sid = os.path.basename(f).split('_ct')[0]
    if os.path.exists(f'{OUT}/{sid}_slab.npz'): return sid
    ct, _ = load_iso(f, order=1)
    lv = lm[sid]
    xs = [l['lm']['_lateral_x'] for l in lv]
    mid = int(np.median(xs))
    variants = {'full': None, 'slab': (max(mid-70, 0), mid+70)}
    for name, slab in variants.items():
        img = lateral_drr(ct, slab)
        pts = []
        for l in lv:
            p = [to_image_xy(l['lm'][k], img.shape) if l['lm'].get(k) is not None else [np.nan, np.nan] for k in KEYS]
            pts.append(p)
        np.savez_compressed(f'{OUT}/{sid}_{name}.npz', img=(img*255).astype(np.uint8),
                            pts=np.array(pts, np.float32), labels=np.array([l['label'] for l in lv]),
                            truncated=np.array([l.get('truncated', False) for l in lv]))
    return sid
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fs = sorted(glob.glob('/home/user/data/verse/ct19/*_ct.nii.gz'))
    with Pool(3) as p:
        for s in p.imap_unordered(work, fs): print(s, flush=True)
