"""Pack held-out cases + metrics into the JSON payload of the offline viewer."""
import sys, os, json, io, base64
import numpy as np, pandas as pd, SimpleITK as sitk
from PIL import Image
from scipy import ndimage
SRC, PRED, RES, OUT = sys.argv[1:5]
PX = 192
split = json.load(open(f'{SRC}/split.json'))
seg = pd.read_csv(f'{RES}/segmentation_test.csv')
fr = pd.read_csv(f'{RES}/features_test_auto_vs_expert.csv')
st = pd.read_csv(f'{RES}/stability.csv')

def lcc(a):
    l, n = ndimage.label(a)
    if n <= 1: return a
    s = ndimage.sum(a, l, range(1, n + 1)); return l == (np.argmax(s) + 1)

def rle(a):
    f = a.ravel().astype(np.uint8); idx = np.flatnonzero(np.diff(np.concatenate([[0], f, [0]])))
    return np.diff(np.concatenate([[0], idx])).tolist()  # alternating 0-run,1-run,...

def resample_xy(vol, sz, order):
    return np.stack([np.asarray(Image.fromarray(s).resize((sz, sz), Image.BILINEAR if order else Image.NEAREST)) for s in vol])

cases = []
for _, r in seg.iterrows():
    mod, case = r.modality, r.case
    suffix = {'MR_T1': 'T1', 'MR_T2FS': 'T2FS', 'CT': ''}[mod]; pdir = 'ct' if mod == 'CT' else 'mri'
    img = sitk.ReadImage(f'{SRC}/{mod}/{case}_img.nii.gz'); a = sitk.GetArrayFromImage(img).astype(np.float32)
    ref = sitk.GetArrayFromImage(sitk.ReadImage(f'{SRC}/{mod}/{case}_lab.nii.gz')) == 1
    pr = sitk.GetArrayFromImage(sitk.ReadImage(f'{PRED}/post/{mod}/{case}.nii.gz')) == 1
    sp = img.GetSpacing()  # x,y,z
    u = ref | pr; zz, yy, xx = np.where(u)
    z0, z1 = max(zz.min() - 2, 0), min(zz.max() + 3, a.shape[0])
    side = max((yy.max() - yy.min()) * sp[1], (xx.max() - xx.min()) * sp[0]) * 1.6 + 30
    half = int(side / sp[0] / 2); cy, cx = (yy.min() + yy.max()) // 2, (xx.min() + xx.max()) // 2
    pad = half + 2
    ap = np.pad(a[z0:z1], ((0, 0), (pad, pad), (pad, pad)), constant_values=a.min())
    sl = lambda v: np.pad(v[z0:z1], ((0, 0), (pad, pad), (pad, pad)))[:, cy + pad - half:cy + pad + half, cx + pad - half:cx + pad + half]
    crop = ap[:, cy + pad - half:cy + pad + half, cx + pad - half:cx + pad + half]
    if mod == 'CT': lo, hi = -160, 240
    else:
        body = a[a > 0.08 * np.percentile(a, 99)]; lo, hi = np.percentile(body, [0.5, 99.5])
    g = (np.clip((crop - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    g = resample_xy(g, PX, 1)
    R = resample_xy(sl(ref).astype(np.uint8) * 255, PX, 0) > 127; P = resample_xy(sl(pr).astype(np.uint8) * 255, PX, 0) > 127
    sprite = Image.fromarray(g.reshape(-1, PX)); buf = io.BytesIO(); sprite.save(buf, 'JPEG', quality=68)
    mmpx = 2 * half * sp[0] / PX
    f = fr[(fr.case == case) & (fr.modality == mod)].set_index('mask')
    feats = []
    for _, s in st[st.modality == mod].iterrows():
        if s.feature not in f.columns or 'expert' not in f.index: continue
        feats.append([s.feature.replace('original_', ''), float(f.loc['expert', s.feature]), float(f.loc['auto', s.feature]) if 'auto' in f.index else None,
                      round(float(s.icc), 3), None if pd.isna(s.icc_auto_vs_expert) else round(float(s.icc_auto_vs_expert), 3), bool(s.robust)])
    cases.append(dict(id=case, mod=mod, n=int(g.shape[0]), px=PX, mmpx=mmpx, dz=sp[2], z0=int(z0),
                      img='data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(),
                      ref=rle(R), auto=rle(P), metrics={k: (None if pd.isna(v) else (round(float(v), 4) if isinstance(v, float) else v)) for k, v in r.items()},
                      feats=feats))
    print(case, mod, g.shape, len(buf.getvalue()) // 1024, 'KB', flush=True)

summ = {}
for mod, g in seg.groupby('modality'):
    s = st[st.modality == mod]
    summ[mod] = dict(n=len(g), dice_median=float(g.dice.median()), dice_q1=float(g.dice.quantile(.25)), dice_q3=float(g.dice.quantile(.75)),
                     hd95_median=float(g.hd95_mm.median()), vol=[[float(a), float(b)] for a, b in zip(g.vol_ref_ml, g.vol_auto_ml)],
                     n_features=len(s), n_stable=int((s.icc >= 0.9).sum()), n_robust=int(s.robust.sum()))
meta = json.load(open(f'{RES}/run_meta.json')) if os.path.exists(f'{RES}/run_meta.json') else {}
json.dump(dict(cases=cases, summary=summ, meta=meta), open(OUT, 'w'), separators=(',', ':'))
print(OUT, os.path.getsize(OUT) // 1024, 'KB')
