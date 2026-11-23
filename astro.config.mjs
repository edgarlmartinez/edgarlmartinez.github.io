import { defineConfig } from 'astro/config';
import toolkitChrome from './scripts/toolkit-chrome.mjs';

// For a GitHub user site (repo named edgarlmartinez.github.io) the base is "/".
// For a project repo (e.g. "website") set BASE_PATH=/website in the workflow.
export default defineConfig({
  site: process.env.SITE_URL || 'https://edgarlmartinez.github.io',
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'ignore',
  integrations: [toolkitChrome()],
});
