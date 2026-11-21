import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const dataDir = path.resolve('src/data');
const load = (file) => yaml.load(fs.readFileSync(path.join(dataDir, file), 'utf8'));

export const cv = load('cv.yaml');
// Optional, git-ignored file with home address / phone for local printing only.
const privatePath = path.join(dataDir, 'private.yaml');
if (fs.existsSync(privatePath)) cv.private = load('private.yaml');
export const site = load('site.yaml');
export const aiProjects = fs.existsSync(path.join(dataDir, 'ai-projects.yaml')) ? (load('ai-projects.yaml')?.projects || []) : [];
export const lectures = fs.existsSync(path.join(dataDir, 'lectures.yaml')) ? load('lectures.yaml') : { lectures: [] };

// "MM/YYYY" -> sortable number. "Present" sorts last.
const key = (d) => {
  if (!d) return 0;
  if (String(d).toLowerCase() === 'present') return 999999;
  const [m, y] = String(d).split('/');
  return y ? Number(y) * 100 + Number(m) : Number(m) * 100;
};

/** Oldest first (HMS convention). Stable, so equal dates keep file order. */
export const chrono = (items = []) =>
  [...(items || [])].sort((a, b) => key(a.start) - key(b.start) || key(a.end) - key(b.end));

/** Newest first (for the website). */
export const newest = (items = []) => chrono(items).reverse();

export const range = (item) => {
  if (!item?.start) return '';
  if (!item.end || item.end === item.start) return String(item.start);
  return `${item.start} - ${item.end}`;
};

export const year = (d) => (d ? String(d).split('/').pop() : '');

export const isCurrent = (item) => String(item?.end || '').toLowerCase() === 'present';

const escapeHtml = (s = '') =>
  String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

/** Escape and bold the CV owner's name in an author string. */
export const boldMe = (text = '') => {
  let out = escapeHtml(text);
  for (const n of cv.my_name_in_citations || []) {
    out = out.split(escapeHtml(n)).join(`<strong>${escapeHtml(n)}</strong>`);
  }
  return out;
};

export const pubLinks = (p) => {
  const links = [];
  if (p.doi) links.push({ label: 'DOI', href: `https://doi.org/${p.doi}` });
  if (p.pmid) links.push({ label: 'PubMed', href: `https://pubmed.ncbi.nlm.nih.gov/${p.pmid}/` });
  if (p.pmcid) links.push({ label: 'PMC', href: `https://www.ncbi.nlm.nih.gov/pmc/articles/${p.pmcid}/` });
  return links;
};

/** "doi: x. PMID: y; PMCID: z." in the NLM style HMS uses. */
export const citationTail = (p) => {
  const ids = [p.pmid && `PMID: ${p.pmid}`, p.pmcid && `PMCID: ${p.pmcid}`].filter(Boolean).join('; ');
  return [p.doi && `doi: ${p.doi}.`, ids && `${ids}.`].filter(Boolean).join(' ');
};

export const citation = (p) => [p.authors, p.title, p.journal, p.details].filter(Boolean).join(' ');

export const allPublications = () => {
  const p = cv.publications || {};
  return [
    ...(p.research_investigations || []),
    ...(p.case_reports || []),
    ...(p.non_peer_reviewed || []),
  ];
};

export const has = (x) =>
  Array.isArray(x) ? x.length > 0 : x && typeof x === 'object' ? Object.values(x).some(has) : !!x;

export const levels = [
  ['local', 'Local'],
  ['regional', 'Regional'],
  ['national', 'National'],
  ['international', 'International'],
];
