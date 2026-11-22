"""Vertebral morphometry engine (research use only).

Works on per-level landmarks in a 2D lateral (sagittal) frame, in mm:
  6 points per vertebral body: as, ps (anterior/posterior superior corners),
  ai, pi (anterior/posterior inferior corners), ms, mi (mid superior/inferior endplate)
  optional 'sl': spinolaminar point (anterior border of the posterior arch at midline)
Coordinates: x = anterior (+), y = superior (+).
The same engine is used for CT-derived reference landmarks and for
landmarks predicted on (simulated) radiographs.
"""
import numpy as np

LEVELS = ['C1','C2','C3','C4','C5','C6','C7'] + [f'T{i}' for i in range(1,13)] + ['L1','L2','L3','L4','L5','L6']
def level_name(lbl):
    return {28:'T13'}.get(lbl, LEVELS[lbl-1] if 1 <= lbl <= len(LEVELS) else str(lbl))

P = lambda d, k: np.asarray(d[k], float)

def heights(lm):
    """Anterior, middle, posterior heights (mm) from 6 points."""
    return dict(Ha=float(np.linalg.norm(P(lm,'as')-P(lm,'ai'))),
                Hm=float(np.linalg.norm(P(lm,'ms')-P(lm,'mi'))),
                Hp=float(np.linalg.norm(P(lm,'ps')-P(lm,'pi'))))

def genant_grade(loss):
    """Semiquantitative Genant grade from fractional height loss."""
    if loss < 0.20: return 0
    if loss < 0.25: return 1
    if loss < 0.40: return 2
    return 3

def _line_dist(p, a, b, ant):
    """Signed distance of p from line a->b; positive = posterior (away from the anterior reference point)."""
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([d[1], -d[0]])
    if np.dot(ant - a, n) > 0: n = -n
    return float(np.dot(p - a, n))

def analyze(levels, flag_thr=0.80, shape_thr=0.75, exclude=('C1','C2')):
    """levels: list of dicts {label, lm: {...}, truncated?} ordered cranial->caudal.
    Height loss is measured against the EXPECTED normal heights of this vertebra,
    obtained by interpolating the anterior/middle/posterior heights of the nearest
    non-fractured vertebrae above and below (extrapolated from one side at the ends).
    Returns per-level heights, expected heights, % loss, Genant grade, morphology,
    posterior wall displacement (retropulsion proxy) and sagittal canal compromise."""
    n = len(levels)
    H = [heights(l['lm']) for l in levels]
    names = [level_name(l['label']) for l in levels]
    skip = [names[i] in exclude or levels[i].get('truncated', False) for i in range(n)]
    K = ('Ha', 'Hm', 'Hp')

    def ref_heights(i, abn):
        up = next((j for j in range(i-1, max(-1, i-4), -1) if not abn[j]), None)
        dn = next((j for j in range(i+1, min(n, i+4)) if not abn[j]), None)
        if up is None and dn is None: return None, []
        if up is None or dn is None:
            j = up if up is not None else dn
            return dict(H[j]), [j]
        wu, wd = (dn - i), (i - up)
        return {k: (H[up][k]*wu + H[dn][k]*wd)/(wu+wd) for k in K}, [up, dn]

    # pass 1: robust screen against the median of nearby levels and obvious shape deformity
    abnormal = list(skip)
    for i in range(n):
        if skip[i]: continue
        nb = [j for j in range(max(0, i-3), min(n, i+4)) if j != i and not skip[j]]
        if nb:
            med = {k: float(np.median([H[j][k] for j in nb])) for k in K}
            if min(H[i][k]/med[k] for k in K) < flag_thr: abnormal[i] = True
        if H[i]['Ha']/H[i]['Hp'] < shape_thr or H[i]['Hm']/H[i]['Hp'] < shape_thr: abnormal[i] = True
    # pass 2: re-test flagged levels against interpolated references from unflagged neighbours
    for _ in range(2):
        for i in range(n):
            if skip[i]: continue
            ref, _ = ref_heights(i, [a if j != i else True for j, a in enumerate(abnormal)])
            if ref: abnormal[i] = min(H[i][k]/ref[k] for k in K) < flag_thr

    def pmid(lm): return (P(lm,'ps') + P(lm,'pi')) / 2
    canal = [float(np.linalg.norm(pmid(l['lm']) - P(l['lm'],'sl'))) if l['lm'].get('sl') is not None else None for l in levels]

    out = []
    for i, l in enumerate(levels):
        h = H[i]
        r = dict(label=l['label'], level=names[i], **{k: round(v, 1) for k, v in h.items()},
                 wedge_ratio=round(h['Ha']/h['Hp'], 3), biconcave_ratio=round(h['Hm']/h['Hp'], 3),
                 graded=not skip[i])
        if skip[i]:
            r.update(genant_grade=None, morphology='not graded', max_height_loss_pct=None,
                     reference_levels=[]); out.append(r); continue
        ref, refidx = ref_heights(i, [a if j != i else True for j, a in enumerate(abnormal)])
        r['reference_levels'] = [names[j] for j in refidx]
        loss = {}
        if ref:
            for k in K:
                r[f'{k}_expected'] = round(ref[k], 1)
                loss[k] = 1 - h[k]/ref[k]
                r[f'{k}_loss_pct'] = round(100*loss[k], 1)
        m = max(loss.values()) if loss else 0
        r['max_height_loss_pct'] = round(100*max(m, 0), 1)
        r['genant_grade'] = genant_grade(max(m, 0))
        if r['genant_grade'] == 0: r['morphology'] = 'normal'
        else:
            # Genant morphology: which height is most reduced relative to expected
            r['morphology'] = {'Ha': 'wedge', 'Hm': 'biconcave', 'Hp': 'crush'}[max(loss, key=loss.get)]
            if r['morphology'] == 'crush' and min(loss.values()) < 0.15: r['morphology'] = 'crush (posterior)'
        if 0 < i < n-1:
            a, b = pmid(levels[i-1]['lm']), pmid(levels[i+1]['lm'])
            pts = [P(l['lm'], k) for k in ('ps','pi')] + [pmid(l['lm'])] + [np.asarray(p, float) for p in l['lm'].get('pwall', [])]
            ant = (P(l['lm'],'as') + P(l['lm'],'ai')) / 2
            r['posterior_wall_displacement_mm'] = round(max(_line_dist(p, a, b, ant) for p in pts), 1)
            if canal[i] and canal[i-1] and canal[i+1]:
                ref_c = (canal[i-1] + canal[i+1]) / 2
                r['canal_ap_mm'] = round(canal[i], 1)
                r['canal_ap_expected_mm'] = round(ref_c, 1)
                r['canal_compromise_pct'] = round(100*max(0, 1 - canal[i]/ref_c), 1)
        out.append(r)
    return out
