"""Reference landmarks from VerSe CT vertebra masks (midsagittal slab), in a global lateral frame."""
import numpy as np, nibabel as nib
from scipy import ndimage as ndi

def load_iso(path, order=0):
    img = nib.as_closest_canonical(nib.load(path))       # RAS: x=R, y=A, z=S
    d = np.asarray(img.dataobj)
    z = img.header.get_zooms()[:3]
    if order == 0: d = d.astype(np.int16)
    else: d = d.astype(np.float32)
    d = ndi.zoom(d, z, order=order, mode='nearest')      # 1 mm isotropic
    return d, img.affine

def vertebra_landmarks(seg):
    labels = [int(l) for l in np.unique(seg) if 0 < l < 30]
    cents = {l: np.array(ndi.center_of_mass(seg == l)) for l in labels}
    labels.sort(key=lambda l: -cents[l][2])                # cranial -> caudal by S coordinate
    res = []
    for i, l in enumerate(labels):
        cx = int(round(cents[l][0]))
        slab = (seg[max(cx-1,0):cx+2] == l).sum(0) >= 2   # (A, S) plane
        if slab.sum() < 50: continue
        comp, nc = ndi.label(slab)
        if nc == 0: continue
        sizes = ndi.sum(slab, comp, range(1, nc+1))
        ant = ndi.mean(np.indices(slab.shape)[0], comp, range(1, nc+1))
        ok = [k+1 for k in range(nc) if sizes[k] > 0.2*sizes.max()]
        body_id = max(ok, key=lambda k: ant[k-1])
        body = comp == body_id
        post = slab & ~body
        # local SI axis from neighbouring centroids in (A,S)
        nb = [labels[j] for j in (i-1, i+1) if 0 <= j < len(labels)]
        if len(nb) == 2: axis = cents[nb[0]][1:] - cents[nb[1]][1:]
        elif nb and labels.index(nb[0]) < i: axis = cents[nb[0]][1:] - cents[l][1:]
        elif nb: axis = cents[l][1:] - cents[nb[0]][1:]
        else: axis = np.array([0., 1.])
        v_ax = axis / np.linalg.norm(axis)                 # spine-axis estimate (superior)
        # refine with the body's own minimum-area rectangle: take the rectangle side
        # closest to the spine axis as the cranio-caudal axis
        import cv2
        bp = np.argwhere(body)[:, ::-1].astype(np.float32)   # (S, A) as (x, y) for cv2
        (_, _), (w_, h_), ang = cv2.minAreaRect(bp)
        t = np.deg2rad(ang)
        e1 = np.array([np.sin(t), np.cos(t)]); e2 = np.array([-np.cos(t), np.sin(t)])
        cand = max((e1, e2), key=lambda e: abs(np.dot(e, v_ax)))
        if np.dot(cand, v_ax) < 0: cand = -cand
        if abs(np.dot(cand, v_ax)) > np.cos(np.deg2rad(35)): v_ax = cand / np.linalg.norm(cand)
        u_ax = np.array([v_ax[1], -v_ax[0]])               # perpendicular
        if u_ax[0] < 0: u_ax = -u_ax                       # anterior (+A)
        pts = np.argwhere(body).astype(float)
        o = pts.mean(0)
        u = (pts - o) @ u_ax; v = (pts - o) @ v_ax
        def to_g(uu, vv): p = o + uu*u_ax + vv*v_ax; return [float(p[0]), float(p[1])]
        umin, umax = u.min(), u.max(); depth = umax - umin
        # corners = extreme points along the diagonals of the normalised local frame
        un = (u - umin) / depth - 0.5
        vmin_, vmax_ = v.min(), v.max(); vn = (v - vmin_) / (vmax_ - vmin_) - 0.5
        def ext(su, sv):
            k = np.argmax(su*un + sv*vn); return u[k], v[k]
        c = {'as': ext(1, 1), 'ai': ext(1, -1), 'ps': ext(-1, 1), 'pi': ext(-1, -1)}
        off = {'as': (0.5, 0.5), 'ai': (0.5, -0.5), 'ps': (-0.5, 0.5), 'pi': (-0.5, -0.5)}
        lm = {k: to_g(c[k][0] + off[k][0], c[k][1] + off[k][1]) for k in c}
        uc = (c['as'][0] + c['ps'][0] + c['ai'][0] + c['pi'][0]) / 4
        sel = np.abs(u - uc) <= 0.75
        if sel.sum() < 3: continue
        lm['ms'] = to_g(uc, v[sel].max() + 0.5); lm['mi'] = to_g(uc, v[sel].min() - 0.5)
        # posterior wall profile
        vlo, vhi = v.min(), v.max(); hh = vhi - vlo
        pw = []
        for vv in np.linspace(vlo + 0.15*hh, vhi - 0.15*hh, 7):
            sel = np.abs(v - vv) <= 0.75
            if sel.any(): pw.append(to_g(u[sel].min() - 0.5, vv))
        lm['pwall'] = pw
        # spinolaminar point: posterior-element pixel nearest to posterior wall midpoint
        pm = (np.array(lm['ps']) + np.array(lm['pi'])) / 2
        pp = np.argwhere(post).astype(float)
        if len(pp):
            pv = (pp - o) @ v_ax; pu = (pp - o) @ u_ax
            sel = (pv > vlo - 0.2*hh) & (pv < vhi + 0.2*hh) & (pu < umin)
            if sel.any():
                q = pp[sel]; lm['sl'] = [float(x) for x in q[np.argmin(np.linalg.norm(q - pm, axis=1))]]
        lm['_lateral_x'] = float(cents[l][0])
        zs = np.where((seg == l).any(axis=(0, 1)))[0]
        trunc = zs.min() <= 1 or zs.max() >= seg.shape[2] - 2
        res.append({'label': l, 'lm': lm, 'truncated': bool(trunc)})
    return res
