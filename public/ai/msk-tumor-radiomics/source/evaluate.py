"""Held-out evaluation: automatic (nnU-Net) vs expert masks.
Segmentation: Dice, HD95, volume. Radiomics: per-feature ICC(1,1) auto vs expert,
combined with the perturbation ICC to give the final 'robust' feature list."""
import sys, os, json
import numpy as np, pandas as pd, SimpleITK as sitk
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
import radiomics_pipeline as rp
SRC, PRED, RES = sys.argv[1:4]
split = json.load(open(f'{SRC}/split.json'))

def lcc(a):
    l, n = ndimage.label(a)
    if n <= 1: return a
    s = ndimage.sum(a, l, range(1, n + 1)); return l == (np.argmax(s) + 1)

def consensus(case, seq, pred_dir):
    """Two-sequence consensus (MRI): keep components of this sequence's prediction that overlap
    the largest component of the intersection with the other sequence's prediction
    (resampled in physical space). Falls back to the largest connected component."""
    other = 'T2FS' if seq == 'T1' else 'T1'
    me_img = sitk.ReadImage(f'{pred_dir}/{case}{seq}.nii.gz'); me = sitk.GetArrayFromImage(me_img) == 1
    of = f'{pred_dir}/{case}{other}.nii.gz'
    if not os.path.exists(of): return lcc(me)
    ot = sitk.GetArrayFromImage(sitk.Resample(sitk.ReadImage(of), me_img, sitk.Transform(), sitk.sitkNearestNeighbor, 0)) == 1
    if not (me & ot).any(): return lcc(me)
    core = lcc(me & ot); l, n = ndimage.label(me); u = np.unique(l[core])
    return np.isin(l, u[u > 0])

def hd95(a, b, sp):
    if a.sum() == 0 or b.sum() == 0: return np.nan
    sa = a ^ ndimage.binary_erosion(a); sb = b ^ ndimage.binary_erosion(b)
    da = ndimage.distance_transform_edt(~sb, sampling=sp)[sa]; db = ndimage.distance_transform_edt(~sa, sampling=sp)[sb]
    return float(np.percentile(np.concatenate([da, db]), 95))

rows, feat_rows = [], []
for mod, (pdir, suffix) in {'MR_T1': ('mri', 'T1'), 'MR_T2FS': ('mri', 'T2FS'), 'CT': ('ct', '')}.items():
    m = 'CT' if mod == 'CT' else 'MR'
    for case in split['test']:
        pf = f'{PRED}/{pdir}/{case}{suffix}.nii.gz'
        if not os.path.exists(pf): continue
        lab = sitk.ReadImage(f'{SRC}/{mod}/{case}_lab.nii.gz'); ref = sitk.GetArrayFromImage(lab) == 1
        pr_img = sitk.ReadImage(pf); raw = sitk.GetArrayFromImage(pr_img) == 1; single = lcc(raw)
        pr = single if mod == 'CT' else consensus(case, suffix, f'{PRED}/{pdir}')
        sp = lab.GetSpacing()[::-1]; vox = np.prod(sp) / 1000
        d = lambda a, b: 2 * (a & b).sum() / max(a.sum() + b.sum(), 1)
        pm = sitk.GetImageFromArray(pr.astype(np.uint8)); pm.CopyInformation(lab)
        os.makedirs(f'{PRED}/post/{mod}', exist_ok=True); sitk.WriteImage(pm, f'{PRED}/post/{mod}/{case}.nii.gz')
        rows.append(dict(case=case, modality=mod, dice_raw=d(raw, ref), dice_lcc=d(single, ref), dice=d(pr, ref), hd95_mm=hd95(pr, ref, sp),
                         vol_ref_ml=ref.sum() * vox, vol_auto_ml=pr.sum() * vox,
                         **{f'auto_{k}': v for k, v in rp.volumetrics(pm).items() if k != 'volume_ml'},
                         **{f'ref_{k}': v for k, v in rp.volumetrics(sitk.Cast(lab == 1, sitk.sitkUInt8)).items() if k != 'volume_ml'}))
        print(rows[-1]['case'], mod, round(rows[-1]['dice'], 3), flush=True)
        if pr.sum() > 10:
            img = rp.prepare(sitk.ReadImage(f'{SRC}/{mod}/{case}_img.nii.gz'), m)
            for k, mk in [('expert', sitk.Cast(lab == 1, sitk.sitkUInt8)), ('auto', pm)]:
                feat_rows.append(dict(case=case, modality=mod, mask=k, **rp.extract(img, mk, m)))
seg = pd.DataFrame(rows); seg.to_csv(f'{RES}/segmentation_test.csv', index=False)
fr = pd.DataFrame(feat_rows); fr.to_csv(f'{RES}/features_test_auto_vs_expert.csv', index=False)
st = pd.read_csv(f'{RES}/stability.csv')
agree = []
for mod, g in fr.groupby('modality'):
    for c in [c for c in g.columns if c.startswith('original_')]:
        X = g.pivot(index='case', columns='mask', values=c)[['expert', 'auto']].dropna().values
        agree.append(dict(modality=mod, feature=c, icc_auto_vs_expert=rp.icc1(X)))
st = st.merge(pd.DataFrame(agree), on=['modality', 'feature'], how='left')
st['robust'] = (st.icc >= 0.9) & (st.icc_auto_vs_expert >= 0.75)
st.to_csv(f'{RES}/stability.csv', index=False)
print(seg.groupby('modality')[['dice_raw', 'dice_lcc', 'dice', 'hd95_mm']].median())
print(st.groupby('modality').robust.sum())
