"""Feature stability under mask perturbation, per modality, on reference (expert) masks.
Writes features_reference.csv (all cases, reference mask) and stability.csv (ICC per feature)."""
import sys, os, json
import numpy as np, pandas as pd, SimpleITK as sitk
sys.path.insert(0, os.path.dirname(__file__))
import radiomics_pipeline as rp
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
rows = []
for mod in ['MR_T1', 'MR_T2FS', 'CT']:
    m = 'CT' if mod == 'CT' else 'MR'
    for f in sorted(os.listdir(f'{SRC}/{mod}')):
        if not f.endswith('_img.nii.gz'): continue
        case = f.split('_img')[0]
        lab = sitk.ReadImage(f'{SRC}/{mod}/{case}_lab.nii.gz')
        mask = sitk.Cast(lab == 1, sitk.sitkUInt8)
        if sitk.GetArrayViewFromImage(mask).sum() == 0: continue
        img = rp.prepare(sitk.ReadImage(f'{SRC}/{mod}/{f}'), m)
        masks = {'reference': mask, **rp.perturb_masks(mask, n_random=2)}
        for k, mk in masks.items():
            try: feats = rp.extract(img, mk, m)
            except Exception as e: print('fail', case, mod, k, e); continue
            rows.append(dict(case=case, modality=mod, mask=k, **(rp.volumetrics(lab) if k == 'reference' else {}), **feats))
        print(mod, case, flush=True)
    pd.DataFrame(rows).to_csv(f'{OUT}/features_perturbed.csv', index=False)
df = pd.DataFrame(rows)
out = []
for mod, g in df.groupby('modality'):
    feats = [c for c in g.columns if c.startswith('original_')]
    piv = {c: g.pivot(index='case', columns='mask', values=c).dropna() for c in feats}
    for c, X in piv.items():
        out.append(dict(modality=mod, feature=c, icc=rp.icc1(X.values), n=len(X)))
st = pd.DataFrame(out); st.to_csv(f'{OUT}/stability.csv', index=False)
df[df['mask'] == 'reference'].to_csv(f'{OUT}/features_reference.csv', index=False)
print(st.groupby('modality').icc.apply(lambda s: f'{(s>=0.9).sum()} excellent / {(s>=0.75).sum()} good of {len(s)}'))
