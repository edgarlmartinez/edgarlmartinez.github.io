"""Run the landmark model on held-out simulated radiographs, compare with CT reference, package viewer data."""
import sys, json, glob, os, base64, numpy as np, cv2
sys.path.insert(0, '/home/user/vmorph')
from infer import predict, load, KEYS
from morph import analyze, level_name
load()
test_ids = json.load(open('/home/user/data/drr_test_ids.json'))
variant = sys.argv[1] if len(sys.argv) > 1 else 'full'
cases, rows, pt_err = [], [], []
for sid in test_ids:
    f = f'/home/user/data/drr/{sid}_{variant}.npz'
    if not os.path.exists(f): print('missing', sid); continue
    d = np.load(f); img = d['img'].astype(np.float32) / 255
    gt = d['pts']; labels = d['labels'].tolist(); trunc = d['truncated'].tolist()
    pred = predict(img)
    gtc = np.array([np.nanmean(g[:6], 0) for g in gt])
    used, levels = set(), []
    for p in pred:
        c = np.mean([p['pts'][k] for k in KEYS[:6]], 0)
        dd = np.linalg.norm(gtc - c, axis=1); j = int(np.argmin(dd))
        if dd[j] < 12 and j not in used:
            used.add(j); levels.append(dict(label=labels[j], truncated=bool(trunc[j]) or p['truncated'], pts=p['pts'], score=p['score'], gt=j))
            for k_i, k in enumerate(KEYS):
                if np.all(np.isfinite(gt[j, k_i])): pt_err.append((k, float(np.linalg.norm(np.array(p['pts'][k]) - gt[j, k_i]))))
        else:
            levels.append(dict(label=None, truncated=p['truncated'], pts=p['pts'], score=p['score'], gt=None))
    # label unmatched detections from neighbours (cranial -> caudal order)
    levels.sort(key=lambda l: l['pts']['ms'][1])
    for i, l in enumerate(levels):
        if l['label'] is None:
            prev = next((levels[j]['label'] + (i - j) for j in range(i-1, -1, -1) if levels[j]['label'] is not None), None)
            l['label'] = prev if prev is not None else 99
    ref = [dict(label=labels[j], truncated=trunc[j], pts={k: (gt[j, i].tolist() if np.all(np.isfinite(gt[j, i])) else None) for i, k in enumerate(KEYS)}) for j in range(len(gt))]
    for r_ in ref: r_['pts'] = {k: v for k, v in r_['pts'].items() if v is not None}
    pr = analyze([dict(label=l['label'], truncated=l['truncated'], lm=l['pts']) for l in levels])
    rr = analyze([dict(label=r_['label'], truncated=r_['truncated'], lm=r_['pts']) for r_ in ref])
    rmap = {x['label']: x for x in rr}
    for x in pr:
        y = rmap.get(x['label'])
        if y and x['genant_grade'] is not None and y['genant_grade'] is not None:
            rows.append(dict(sid=sid, level=x['level'], **{f'p_{k}': x.get(k) for k in ('Ha','Hm','Hp','max_height_loss_pct','genant_grade','posterior_wall_displacement_mm','canal_compromise_pct')},
                             **{f'r_{k}': y.get(k) for k in ('Ha','Hm','Hp','max_height_loss_pct','genant_grade','posterior_wall_displacement_mm','canal_compromise_pct')}))
    missed = [level_name(labels[j]) for j in range(len(gt)) if j not in used]
    ok, jpg = cv2.imencode('.jpg', (img * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
    fx = [f"{x['level']} G{x['genant_grade']}" for x in rr if x['genant_grade']]
    cases.append(dict(id=sid, title=sid.replace('sub-', '').replace('verse', 'VerSe '),
        subtitle=f"Simulated lateral radiograph from public CT ({variant} projection). CT reference: {', '.join(fx) if fx else 'no deformity at or above 20%'}." + (f" Model missed: {', '.join(missed)}." if missed else ''),
        img='data:image/jpeg;base64,' + base64.b64encode(jpg.tobytes()).decode(), mmPerPx=1.0, calibNote='1.0 mm/px (simulated, no magnification)',
        levels=[dict(label=l['label'], truncated=l['truncated'], pts=l['pts']) for l in levels], ref=ref))
    print(sid, 'detected', len(pred), 'gt', len(gt), 'missed', missed, flush=True)
# summary metrics
import collections
pe = collections.defaultdict(list)
for k, e in pt_err: pe[k].append(e)
summ = dict(variant=variant, n_cases=len(cases), n_levels=len(rows),
    point_error_mm={k: round(float(np.median(v)), 2) for k, v in pe.items()},
    point_error_mm_mean={k: round(float(np.mean(v)), 2) for k, v in pe.items()})
def mae(k): v = [abs(r['p_'+k]-r['r_'+k]) for r in rows if r['p_'+k] is not None and r['r_'+k] is not None]; return round(float(np.mean(v)), 2) if v else None
for k in ('Ha','Hm','Hp','max_height_loss_pct','posterior_wall_displacement_mm','canal_compromise_pct'): summ['mae_'+k] = mae(k)
P = [r['p_genant_grade'] > 0 for r in rows]; R = [r['r_genant_grade'] > 0 for r in rows]
tp = sum(p and r for p, r in zip(P, R)); fp = sum(p and not r for p, r in zip(P, R)); fn = sum(r and not p for p, r in zip(P, R)); tn = len(rows) - tp - fp - fn
summ.update(fracture_tp=tp, fracture_fp=fp, fracture_fn=fn, fracture_tn=tn,
    sensitivity=round(tp/(tp+fn), 3) if tp+fn else None, specificity=round(tn/(tn+fp), 3) if tn+fp else None,
    exact_grade_agreement=round(sum(r['p_genant_grade'] == r['r_genant_grade'] for r in rows)/len(rows), 3),
    within_one_grade=round(sum(abs(r['p_genant_grade'] - r['r_genant_grade']) <= 1 for r in rows)/len(rows), 3))
# linear weighted kappa
import itertools
O = np.zeros((4, 4))
for r in rows: O[r['p_genant_grade'], r['r_genant_grade']] += 1
Wt = np.array([[abs(i-j)/3 for j in range(4)] for i in range(4)]); E = np.outer(O.sum(1), O.sum(0)) / O.sum()
summ['weighted_kappa'] = round(float(1 - (Wt*O).sum()/(Wt*E).sum()), 3)
summ['confusion_pred_rows_ref_cols'] = O.astype(int).tolist()
print(json.dumps(summ, indent=1))
json.dump(dict(cases=cases, summary=summ), open(f'/home/user/data/viewer_data_{variant}.json', 'w'))
json.dump(rows, open(f'/home/user/data/eval_rows_{variant}.json', 'w'), indent=0)
