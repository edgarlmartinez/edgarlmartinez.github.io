// Vertebral morphometry engine (JS port of morph.py). Research use only.
// Points per level, in image pixels: as, ai, ms, mi, ps, pi (+ optional sl). mmPerPx converts to mm.
const LEVELS = ['C1','C2','C3','C4','C5','C6','C7','T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12','L1','L2','L3','L4','L5','L6'];
function levelName(l) { return l === 28 ? 'T13' : (l >= 1 && l <= LEVELS.length ? LEVELS[l - 1] : String(l)); }
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
function heights(lm, s) { return { Ha: dist(lm.as, lm.ai) * s, Hm: dist(lm.ms, lm.mi) * s, Hp: dist(lm.ps, lm.pi) * s }; }
function genantGrade(loss) { return loss < 0.20 ? 0 : loss < 0.25 ? 1 : loss < 0.40 ? 2 : 3; }
const pmid = lm => [(lm.ps[0] + lm.pi[0]) / 2, (lm.ps[1] + lm.pi[1]) / 2];
// signed distance from line a->b, positive toward the posterior side (side away from anterior points)
function posteriorDist(p, a, b, antRef) {
  const d = [b[0] - a[0], b[1] - a[1]], L = Math.hypot(d[0], d[1]);
  let n = [d[1] / L, -d[0] / L];
  const sAnt = (antRef[0] - a[0]) * n[0] + (antRef[1] - a[1]) * n[1];
  if (sAnt > 0) n = [-n[0], -n[1]];
  return (p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1];
}
function analyze(levels, mmPerPx = 1, opt = {}) {
  const flagThr = opt.flagThr ?? 0.80, shapeThr = opt.shapeThr ?? 0.75, exclude = opt.exclude ?? ['C1', 'C2'];
  const n = levels.length, K = ['Ha', 'Hm', 'Hp'];
  const H = levels.map(l => heights(l.pts, mmPerPx));
  const names = levels.map(l => l.name || levelName(l.label));
  const skip = levels.map((l, i) => exclude.includes(names[i]) || !!l.truncated);
  const refHeights = (i, abn) => {
    let up = null, dn = null;
    for (let j = i - 1; j >= Math.max(0, i - 3); j--) if (!abn[j]) { up = j; break; }
    for (let j = i + 1; j <= Math.min(n - 1, i + 3); j++) if (!abn[j]) { dn = j; break; }
    if (up === null && dn === null) return [null, []];
    if (up === null || dn === null) { const j = up ?? dn; return [{ ...H[j] }, [j]]; }
    const wu = dn - i, wd = i - up, r = {};
    K.forEach(k => r[k] = (H[up][k] * wu + H[dn][k] * wd) / (wu + wd));
    return [r, [up, dn]];
  };
  const abnormal = skip.slice();
  for (let i = 0; i < n; i++) {
    if (skip[i]) continue;
    const nb = []; for (let j = Math.max(0, i - 3); j <= Math.min(n - 1, i + 3); j++) if (j !== i && !skip[j]) nb.push(j);
    if (nb.length) {
      const med = {}; K.forEach(k => { const v = nb.map(j => H[j][k]).sort((a, b) => a - b); const m = v.length >> 1; med[k] = v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; });
      if (Math.min(...K.map(k => H[i][k] / med[k])) < flagThr) abnormal[i] = true;
    }
    if (H[i].Ha / H[i].Hp < shapeThr || H[i].Hm / H[i].Hp < shapeThr) abnormal[i] = true;
  }
  for (let it = 0; it < 2; it++) for (let i = 0; i < n; i++) {
    if (skip[i]) continue;
    const [ref] = refHeights(i, abnormal.map((a, j) => j === i ? true : a));
    if (ref) abnormal[i] = Math.min(...K.map(k => H[i][k] / ref[k])) < flagThr;
  }
  const canal = levels.map(l => l.pts.sl ? dist(pmid(l.pts), l.pts.sl) * mmPerPx : null);
  const r1 = x => x == null ? null : Math.round(x * 10) / 10;
  return levels.map((l, i) => {
    const h = H[i];
    const r = { label: l.label, level: names[i], Ha: r1(h.Ha), Hm: r1(h.Hm), Hp: r1(h.Hp),
      wedge_ratio: Math.round(h.Ha / h.Hp * 1000) / 1000, biconcave_ratio: Math.round(h.Hm / h.Hp * 1000) / 1000, graded: !skip[i] };
    if (skip[i]) return { ...r, genant_grade: null, morphology: 'not graded', max_height_loss_pct: null, reference_levels: [] };
    const [ref, refidx] = refHeights(i, abnormal.map((a, j) => j === i ? true : a));
    r.reference_levels = refidx.map(j => names[j]);
    const loss = {};
    if (ref) K.forEach(k => { r[k + '_expected'] = r1(ref[k]); loss[k] = 1 - h[k] / ref[k]; r[k + '_loss_pct'] = r1(100 * loss[k]); });
    const m = Object.keys(loss).length ? Math.max(...Object.values(loss)) : 0;
    r.max_height_loss_pct = r1(100 * Math.max(m, 0));
    r.genant_grade = genantGrade(Math.max(m, 0));
    if (r.genant_grade === 0) r.morphology = 'normal';
    else {
      const kmax = K.reduce((a, b) => loss[a] >= loss[b] ? a : b);
      r.morphology = { Ha: 'wedge', Hm: 'biconcave', Hp: 'crush' }[kmax];
      if (r.morphology === 'crush' && Math.min(...Object.values(loss)) < 0.15) r.morphology = 'crush (posterior)';
    }
    if (i > 0 && i < n - 1) {
      const a = pmid(levels[i - 1].pts), b = pmid(levels[i + 1].pts), p = l.pts;
      const ant = [(p.as[0] + p.ai[0]) / 2, (p.as[1] + p.ai[1]) / 2];
      const cands = [p.ps, p.pi, pmid(p), ...(p.pwall || [])];
      r.posterior_wall_displacement_mm = r1(Math.max(...cands.map(q => posteriorDist(q, a, b, ant))) * mmPerPx);
      if (canal[i] && canal[i - 1] && canal[i + 1]) {
        const rc = (canal[i - 1] + canal[i + 1]) / 2;
        r.canal_ap_mm = r1(canal[i]); r.canal_ap_expected_mm = r1(rc);
        r.canal_compromise_pct = r1(100 * Math.max(0, 1 - canal[i] / rc));
      }
    }
    return r;
  });
}
if (typeof module !== 'undefined') module.exports = { analyze, levelName };
