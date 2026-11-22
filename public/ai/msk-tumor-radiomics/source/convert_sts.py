"""Convert TCIA Soft-tissue-Sarcoma (via NCI IDC) DICOM + RTSTRUCT to NIfTI.
Keeps native (non-aligned) T1, T2FS/STIR and CT series with their own contours.
Labels: 1 = GTV_Mass (tumor), 2 = GTV_Edema minus mass (peritumoral edema)."""
import glob, os, sys, json
import numpy as np, pydicom, SimpleITK as sitk
from skimage.draw import polygon

ROOT = sys.argv[1]; OUT = sys.argv[2]
KEEP = {'RTSTRUCT_T1': 'T1', 'RTSTRUCT_T2FS': 'T2FS', 'RTSTRUCT_STIR': 'STIR', 'RTSTRUCT_CT': 'CT'}

def read_series(d):
    r = sitk.ImageSeriesReader()
    ids = r.GetGDCMSeriesIDs(d)
    files = r.GetGDCMSeriesFileNames(d, ids[0])
    r.SetFileNames(files)
    return r.Execute()

def rasterize(img, roi):
    size = img.GetSize()
    m = np.zeros(size[::-1], np.uint8)  # z,y,x
    for c in roi.ContourSequence:
        pts = np.array(c.ContourData, float).reshape(-1, 3)
        idx = np.array([img.TransformPhysicalPointToContinuousIndex(p.tolist()) for p in pts])
        k = int(round(idx[:, 2].mean()))
        if not (0 <= k < size[2]) or len(idx) < 3:
            continue
        rr, cc = polygon(idx[:, 1], idx[:, 0], shape=(size[1], size[0]))
        sl = np.zeros((size[1], size[0]), np.uint8); sl[rr, cc] = 1
        m[k] ^= sl
    return m

meta = []
for p in sorted(os.listdir(ROOT)):
    pdir = os.path.join(ROOT, p)
    for f in glob.glob(f'{pdir}/RTSTRUCT_*/*.dcm'):
        d = pydicom.dcmread(f)
        key = d.SeriesDescription.replace(' ', '').upper()
        key = {k.upper(): v for k, v in KEEP.items()}.get(key)
        if key is None:
            continue
        ref = d.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID
        sdir = [x for x in glob.glob(f'{pdir}/*_{ref}')]
        if not sdir:
            print('missing ref', p, key); continue
        img = read_series(sdir[0])
        names = {r.ROINumber: r.ROIName for r in d.StructureSetROISequence}
        lab = np.zeros(img.GetSize()[::-1], np.uint8); masks = {}
        for rc in d.ROIContourSequence:
            n = names[rc.ReferencedROINumber].upper()
            if 'ContourSequence' in rc:
                masks[n] = rasterize(img, rc)
        if 'GTV_EDEMA' in masks: lab[masks['GTV_EDEMA'] > 0] = 2
        if 'GTV_MASS' in masks: lab[masks['GTV_MASS'] > 0] = 1
        mod = 'CT' if key == 'CT' else 'MR_' + ('T1' if key == 'T1' else 'T2FS')  # STIR + T2FS pooled as fluid-sensitive
        o = os.path.join(OUT, mod); os.makedirs(o, exist_ok=True)
        L = sitk.GetImageFromArray(lab); L.CopyInformation(img)
        sitk.WriteImage(img, f'{o}/{p}_img.nii.gz'); sitk.WriteImage(L, f'{o}/{p}_lab.nii.gz')
        vox = np.prod(img.GetSpacing()) / 1000
        meta.append(dict(case=p, mod=mod, seq=key, size=img.GetSize(), spacing=img.GetSpacing(),
                         mass_ml=float((lab == 1).sum() * vox), edema_ml=float((lab == 2).sum() * vox)))
        print(meta[-1], flush=True)
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
