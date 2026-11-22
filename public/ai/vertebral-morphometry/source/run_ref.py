import glob, json, sys, os
sys.path.insert(0, '/home/user/vmorph')
from multiprocessing import Pool
from ct_reference import load_iso, vertebra_landmarks
def work(f):
    sid = os.path.basename(f).split('_seg')[0]
    seg, aff = load_iso(f)
    return sid, vertebra_landmarks(seg)
if __name__ == '__main__':
    fs = sorted(glob.glob('/home/user/data/verse/masks19/*_seg-vert_msk.nii.gz'))
    with Pool(4) as p: res = dict(p.map(work, fs))
    json.dump(res, open('/home/user/data/verse/lm19.json', 'w'))
