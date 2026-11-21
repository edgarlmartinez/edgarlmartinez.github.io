// Builds a PDF of the HMS CV from the built site: `npm run build && npm run pdf`.
// The GitHub workflow runs this on every push, so the site always serves a fresh /cv.pdf.
// Needs Playwright (npx playwright install chromium) on your computer.
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const dist = path.resolve('dist');
const base = (process.env.BASE_PATH || '/').replace(/\/$/, '');
const server = createServer(async (req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (base && p.startsWith(base)) p = p.slice(base.length) || '/';
  if (p.endsWith('/')) p += 'index.html';
  try {
    const body = await readFile(path.join(dist, p));
    const type = p.endsWith('.html') ? 'text/html' : p.endsWith('.css') ? 'text/css' : p.endsWith('.svg') ? 'image/svg+xml' : 'application/octet-stream';
    res.writeHead(200, { 'content-type': type }).end(body);
  } catch { res.writeHead(404).end(); }
}).listen(4329);

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(`http://localhost:4329${base}/cv/`, { waitUntil: 'networkidle' });
const out = process.argv[2] || 'dist/cv.pdf';
await page.pdf({
  path: out, format: 'Letter', preferCSSPageSize: true, printBackground: true,
  displayHeaderFooter: true, headerTemplate: '<span></span>',
  footerTemplate: '<div style="font-size:9pt;width:100%;text-align:right;padding-right:0.8in;font-family:Times New Roman"><span class="pageNumber"></span></div>',
});
await browser.close();
server.close();
console.log('Wrote', out);
