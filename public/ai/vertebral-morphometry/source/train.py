import sys, glob, json, os, time, math, numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, '/home/user/vmorph')
from model import Net, NPTS
import cv2
torch.set_num_threads(4)
H, W, S = 384, 192, 2
rng = np.random.default_rng(0)
files = sorted(glob.glob('/home/user/data/drr/*.npz'))
test_ids = set(json.load(open('/home/user/data/drr_test_ids.json')))
train = [f for f in files if os.path.basename(f).rsplit('_', 1)[0] not in test_ids]
data = [dict(np.load(f)) for f in train]
from morph import analyze
KEYS = ('as', 'ai', 'ms', 'mi', 'ps', 'pi', 'sl')
for d in data:   # per-vertebra sampling weights: oversample deformed bodies
    lv = [dict(label=int(l), truncated=bool(tr), lm={k: p[i].tolist() for i, k in enumerate(KEYS) if np.all(np.isfinite(p[i]))}) for l, tr, p in zip(d['labels'], d['truncated'], d['pts'])]
    g = [x['genant_grade'] or 0 for x in analyze(lv)]
    w = np.array([1.0 + 4.0 * (gi > 0) for gi in g]); d['w'] = w / w.sum()
print('train images', len(data), flush=True)

def sample(d):
    img = d['img'].astype(np.float32) / 255; pts = d['pts'].copy()      # (n, 7, 2) as (col,row)
    # random affine: scale, rotation, translation; then crop to H x W
    sc = rng.uniform(0.75, 1.35); ang = rng.uniform(-15, 15)
    n = len(pts); i0 = rng.choice(n, p=d['w'])                                 # centre crop near a random vertebra
    c = np.nanmean(pts[i0, :6], 0)
    M = cv2.getRotationMatrix2D((float(c[0]), float(c[1])), ang, sc)
    M[:, 2] += np.array([W/2, H/2]) - c + rng.normal(0, [20, 60])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=float(rng.uniform(0, 0.3)))
    P = pts @ M[:, :2].T + M[:, 2]
    if rng.random() < 0.5:                                                # mirror: anterior left/right
        out = out[:, ::-1].copy(); P[..., 0] = W - 1 - P[..., 0]
    # photometric
    g = rng.uniform(0.6, 1.6); out = np.clip(out, 0, 1) ** g
    out = out * rng.uniform(0.7, 1.2) + rng.uniform(-0.15, 0.15)
    if rng.random() < 0.5: out = cv2.GaussianBlur(out, (0, 0), rng.uniform(0.3, 1.5))
    out = out + rng.normal(0, rng.uniform(0, 0.05), out.shape)
    if rng.random() < 0.3: out = 1 - out                                  # some displays/inverted films
    return np.clip(out, -0.5, 1.5).astype(np.float32), P

def targets(P, trunc):
    h, w = H // S, W // S
    kp = np.zeros((NPTS, h, w), np.float32); hm = np.zeros((h, w), np.float32); off = np.zeros((2*NPTS, h, w), np.float32); m = np.zeros((2*NPTS, h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    for v in range(len(P)):
        ctr = np.nanmean(P[v, :6], 0) / S
        if not np.all(np.isfinite(ctr)) or not (0 <= ctr[0] < w and 0 <= ctr[1] < h): continue
        size = np.linalg.norm(P[v, 0] - P[v, 5]) / S if np.all(np.isfinite(P[v, [0, 5]])) else 10
        sig = max(1.0, size / 6)
        g = np.exp(-((xx - ctr[0])**2 + (yy - ctr[1])**2) / (2*sig**2))
        hm = np.maximum(hm, g)
        for k in range(NPTS):
            q = P[v, k] / S
            if np.all(np.isfinite(q)) and 0 <= q[0] < w and 0 <= q[1] < h:
                kp[k] = np.maximum(kp[k], np.exp(-((xx - q[0])**2 + (yy - q[1])**2) / (2*1.5**2)))
                kp[k, int(round(q[1])) if round(q[1]) < h else h-1, int(round(q[0])) if round(q[0]) < w else w-1] = 1.0
        cx, cy = int(round(ctr[0])), int(round(ctr[1]))
        if 0 <= cx < w and 0 <= cy < h: hm[cy, cx] = 1.0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                x, y = cx + dx, cy + dy
                if not (0 <= x < w and 0 <= y < h): continue
                for k in range(NPTS):
                    if np.all(np.isfinite(P[v, k])):
                        off[2*k:2*k+2, y, x] = (P[v, k] / S - [x, y]) / 8.0
                        m[2*k:2*k+2, y, x] = 1
    return hm, off, m, kp

def batch(bs):
    X, HM, OF, MK, KP = [], [], [], [], []
    for _ in range(bs):
        d = data[rng.integers(len(data))]
        img, P = sample(d); hm, off, m, kp = targets(P, d['truncated'])
        X.append(img[None]); HM.append(hm[None]); OF.append(off); MK.append(m); KP.append(kp)
    return [torch.from_numpy(np.stack(a)) for a in (X, HM, OF, MK, KP)]

def focal(pred, gt):
    p = torch.sigmoid(pred).clamp(1e-4, 1 - 1e-4)
    pos = gt.eq(1).float() if False else (gt > 0.99).float()
    neg = 1 - pos
    lp = -torch.log(p) * (1 - p)**2 * pos
    ln = -torch.log(1 - p) * p**2 * (1 - gt)**4 * neg
    return (lp.sum() + ln.sum()) / pos.sum().clamp(min=1)

if __name__ == '__main__':
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    net = Net(); opt = torch.optim.AdamW(net.parameters(), 2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, total_steps=iters, pct_start=0.1)
    t0 = time.time()
    for it in range(iters):
        X, HM, OF, MK, KP = batch(8)
        ph, po, pk = net(X)
        l1 = focal(ph, HM) + focal(pk, KP) / NPTS; l2 = (F.smooth_l1_loss(po, OF, reduction='none', beta=0.05) * MK).sum() / MK.sum().clamp(min=1)
        loss = l1 + 5*l2
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if it % 50 == 0: print(f'{it} hm {l1.item():.3f} off {l2.item():.4f} {time.time()-t0:.0f}s', flush=True)
        if it % 500 == 499: torch.save(net.state_dict(), '/home/user/data/vlm_net.pt')
    torch.save(net.state_dict(), '/home/user/data/vlm_net.pt')
