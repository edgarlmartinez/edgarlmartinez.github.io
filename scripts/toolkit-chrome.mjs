// Astro integration: after the build, give the standalone toolkit page (public/toolkit/index.html,
// copied as-is to dist/toolkit/) the same header, nav, footer, fonts and palette as the rest of
// the site, and links from each toolkit section to its teaching cases.
// The header and footer are copied from the built home page, so they always match Base.astro.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';

const CHROME_CSS = `
/* Site chrome (header, nav, footer) and site palette, injected at build by scripts/toolkit-chrome.mjs */
html:root,html:root[data-theme]{
  --bg:#000000; --surface:#0b0f14; --surface-2:#11161c; --ink:#e6ebf1; --muted:#9aa7b6; --line:#262d36;
  --accent:#5cc8da; --accent-ink:#04222a; --accent-soft:#10292f; --canvas:#05080b;
  --f-body:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  --f-head:'Source Serif 4',Georgia,'Times New Roman',serif;
}
.site-header,.site-footer{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;font-size:16px;line-height:1.6}
.site-header .wrap,.site-footer .wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.site-header{border-bottom:1px solid var(--line);background:#000}
.site-header .header-inner{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:60px;flex-wrap:wrap}
.site-header .brand{font-family:'Source Serif 4',Georgia,serif;font-weight:600;color:#e9f1f8;text-decoration:none;font-size:1.05rem}
.site-header nav{display:flex;gap:4px;max-width:100%;overflow-x:auto;scrollbar-width:none}
.site-header nav::-webkit-scrollbar{display:none}
.site-header nav a{white-space:nowrap;color:var(--muted);text-decoration:none;padding:6px 12px;border-radius:999px;font-size:.95rem}
.site-header nav a:hover{color:#e9f1f8;background:#11161c}
.site-header nav a[aria-current='page']{color:#e9f1f8;background:var(--accent-soft);font-weight:500}
.site-footer{border-top:1px solid var(--line);color:var(--muted);font-size:.875rem;padding:28px 0 40px;margin-top:64px}
.caselinks{margin:6px 0 0;font-size:14px;color:var(--muted)}
.caselinks a{color:var(--accent)}
@media print{.site-header,.site-footer{display:none}}
`;

const FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">';

const grab = (html, re, what) => {
  const m = html.match(re);
  if (!m) throw new Error(`toolkit-chrome: could not find the site ${what} in the built home page`);
  return m[0];
};

export function wrapToolkit(distDir, root, base) {
  const page = path.join(distDir, 'toolkit', 'index.html');
  if (!fs.existsSync(page)) return;
  const home = fs.readFileSync(path.join(distDir, 'index.html'), 'utf8');
  let header = grab(home, /<header class="site-header[\s\S]*?<\/header>/, 'header');
  const footer = grab(home, /<footer class="site-footer[\s\S]*?<\/footer>/, 'footer');
  // Mark the toolkit link as the current page, and clear the Home marker copied from the home page.
  header = header.replace(/ aria-current="page"/g, '').replace(/(<a href="[^"]*\/toolkit\/")/, '$1 aria-current="page"');

  // Teaching cases that link to a toolkit section (toolkit_link: toolkit/#<section>) get a link back.
  const cases = yaml.load(fs.readFileSync(path.join(root, 'src', 'data', 'cases.yaml'), 'utf8'));
  const links = {};
  for (const c of cases.cases || []) {
    const m = (c.toolkit_link?.href || '').match(/toolkit\/#([\w-]+)/);
    if (m) (links[m[1]] ||= []).push({ href: `${base}/cases/#${c.id}`, title: c.title });
  }

  let s = fs.readFileSync(page, 'utf8');
  if (s.includes('class="site-header')) return; // already wrapped
  s = s.replace('</head>', `${FONTS}\n</head>`);
  s = s.replace('<body>', `<body>\n${header}\n<style>${CHROME_CSS}</style>\n<script>window.SITE_CASE_LINKS = ${JSON.stringify(links)};</script>`);
  s = s.replace(/<\/body>(?![\s\S]*<\/body>)/, `${footer}\n</body>`);
  fs.writeFileSync(page, s);
}

export default function toolkitChrome() {
  let base = '';
  return {
    name: 'toolkit-chrome',
    hooks: {
      'astro:config:done': ({ config }) => { base = (config.base || '/').replace(/\/$/, ''); },
      'astro:build:done': ({ dir }) => wrapToolkit(fileURLToPath(dir), process.cwd(), base),
    },
  };
}
