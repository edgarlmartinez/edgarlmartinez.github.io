import sys, numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, '/home/user/vmorph')
from model import Net, NPTS
KEYS = ('as', 'ai', 'ms', 'mi', 'ps', 'pi', 'sl')
_net = None
def load(path='/home/user/data/vlm_net.pt'):
    global _net
    _net = Net(); _net.load_state_dict(torch.load(path, map_location='cpu')); _net.eval(); return _net
def predict(img, thr=0.3, S=2):
    """img: float [0,1] at ~1 mm/px. Returns list of dict(score, pts{key: [col,row]}) sorted top->bottom."""
    net = _net or load()
    h, w = img.shape; ph, pw = (-h) % 16, (-w) % 16
    x = torch.from_numpy(np.pad(img, ((0, ph), (0, pw)), mode='edge').astype(np.float32))[None, None]
    with torch.no_grad():
        hm, off, kp = net(x)
        hm2 = torch.sigmoid(hm); kp = torch.sigmoid(kp)[0].numpy()
        # test-time flip augmentation for the centre heatmap
        hmf, _, _ = net(torch.flip(x, [3])); hm2 = (hm2 + torch.flip(torch.sigmoid(hmf), [3])) / 2
        peaks = (hm2 == F.max_pool2d(hm2, 9, 1, 4)) & (hm2 > thr)
    Hh, Ww = kp.shape[1:]
    ys, xs = torch.nonzero(peaks[0, 0], as_tuple=True)
    out = []
    for y, x_ in zip(ys.tolist(), xs.tolist()):
        o = off[0, :, y, x_].numpy() * 8.0
        pts = {}
        for i, k in enumerate(KEYS):
            px, py = x_ + o[2*i], y + o[2*i+1]          # regressed location (stride units)
            # refine with the per-point heatmap: best response near the regressed location
            r = 5; x0, x1 = int(max(0, px - r)), int(min(Ww, px + r + 1)); y0, y1 = int(max(0, py - r)), int(min(Hh, py + r + 1))
            if x1 > x0 and y1 > y0:
                win = kp[i, y0:y1, x0:x1]
                yy, xx = np.mgrid[y0:y1, x0:x1]
                sc = win * np.exp(-((xx - px)**2 + (yy - py)**2) / (2 * 3.0**2))
                j = np.unravel_index(np.argmax(sc), sc.shape)
                if win[j] > 0.25:
                    cy, cx = yy[j], xx[j]
                    a0, a1, b0, b1 = max(0, cy-1), min(Hh, cy+2), max(0, cx-1), min(Ww, cx+2)
                    wv = kp[i, a0:a1, b0:b1]; gy, gx = np.mgrid[a0:a1, b0:b1]
                    px, py = float((wv*gx).sum()/wv.sum()), float((wv*gy).sum()/wv.sum())
            pts[k] = [float(px * S), float(py * S)]
        if pts['as'][1] >= h or pts['as'][0] >= w: continue
        out.append(dict(score=float(hm2[0, 0, y, x_]), pts=pts))
    # suppress duplicate detections of the same body (centres closer than 40% of body height)
    out.sort(key=lambda d: -d['score']); keep = []
    for d in out:
        c = np.mean([d['pts'][k] for k in KEYS[:6]], 0)
        hgt = np.linalg.norm(np.array(d['pts']['ms']) - np.array(d['pts']['mi']))
        if all(np.linalg.norm(c - np.mean([e['pts'][k] for k in KEYS[:6]], 0)) > 0.4 * max(hgt, 10) for e in keep): keep.append(d)
    keep.sort(key=lambda d: d['pts']['ms'][1])
    # reject detections far from the spinal column (robust quadratic fit of centre x on y)
    if len(keep) >= 5:
        C = np.array([np.mean([d['pts'][k] for k in KEYS[:6]], 0) for d in keep])
        good = np.ones(len(C), bool)
        for _ in range(3):
            co = np.polyfit(C[good, 1], C[good, 0], 2)
            res = np.abs(np.polyval(co, C[:, 1]) - C[:, 0])
            good = res < max(15.0, 2.5 * np.median(res[good]))
        keep = [d for d, g in zip(keep, good) if g]
    # flag bodies cut by the image edge (not graded)
    for d in keep:
        P = np.array([d['pts'][k] for k in KEYS[:6]])
        d['truncated'] = bool((P[:, 0] < 2).any() or (P[:, 1] < 2).any() or (P[:, 0] > w - 3).any() or (P[:, 1] > h - 3).any())
    return keep
