import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Old addresses forward to the new pages so earlier links keep working.
const areas = ['biomedical', 'public-health', 'science', 'patents', 'data', 'ai'];
const redirects = {
  '/portfolio': '/',
  '/research': '/projects/',
  '/methods': '/experience/',
  '/about': '/#about',
  '/credentials': '/experience/',
  '/projects/research-intelligence-dashboards-and-web-portfolio': '/projects/',
  '/projects/research-meets-policy-communication': '/experience/',
};
for (const a of areas) redirects[`/research/${a}`] = `/projects/#area-${a}`;

export default defineConfig({
  site: 'https://descartesmbogning.github.io',
  output: 'static',
  trailingSlash: 'ignore',
  redirects,
  integrations: [sitemap({ filter: (page) => !page.includes('/edit/') && !Object.keys(redirects).some((r) => page.replace(/\/$/, '').endsWith(r)) })],
});
