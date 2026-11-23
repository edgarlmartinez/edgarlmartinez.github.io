"""Build nnU-Net v2 raw datasets (one per modality) with a fixed patient-level test split."""
import os, json, random, shutil, sys
import SimpleITK as sitk, numpy as np
SRC = sys.argv[1]; RAW = sys.argv[2]
cases = sorted({f.split('_img')[0] for f in os.listdir(f'{SRC}/MR_T1') if f.endswith('_img.nii.gz')})
random.Random(42).shuffle(cases)
test = sorted(cases[:11]); train = sorted(cases[11:])
json.dump({'train': train, 'test': test}, open(f'{SRC}/split.json', 'w'), indent=1)
SPEC = {601: ('STS_CT', 'CT', 'CT', {'background': 0, 'tumor': 1}),
        602: ('STS_MRT1', 'MR_T1', 'T1', {'background': 0, 'tumor': 1}),
        603: ('STS_MRT2FS', 'MR_T2FS', 'T2FS', {'background': 0, 'tumor': 1, 'edema': 2})}
for did, (name, mod, ch, labels) in SPEC.items():
    d = f'{RAW}/Dataset{did}_{name}'
    for sub in ['imagesTr', 'labelsTr', 'imagesTs', 'labelsTs']: os.makedirs(f'{d}/{sub}', exist_ok=True)
    n = 0
    for c in cases:
        lab = sitk.ReadImage(f'{SRC}/{mod}/{c}_lab.nii.gz')
        a = sitk.GetArrayFromImage(lab)
        if (a == 1).sum() == 0: print('skip empty', mod, c); continue
        if len(labels) == 2: a = (a == 1).astype(np.uint8)
        L = sitk.GetImageFromArray(a); L.CopyInformation(lab)
        tr = 'Tr' if c in train else 'Ts'
        shutil.copy(f'{SRC}/{mod}/{c}_img.nii.gz', f'{d}/images{tr}/{c}_0000.nii.gz')
        sitk.WriteImage(L, f'{d}/labels{tr}/{c}.nii.gz')
        n += tr == 'Tr'
    json.dump({'channel_names': {'0': ch}, 'labels': labels, 'numTraining': n, 'file_ending': '.nii.gz',
               'license': 'CC BY 3.0 (TCIA Soft-tissue-Sarcoma, Vallieres et al. 2015)'}, open(f'{d}/dataset.json', 'w'), indent=1)
    print(name, n)
