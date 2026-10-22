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
const areaToProgramme = { biomedical: 'lab', 'public-health': 'evidence', science: 'left-out', patents: 'invest', data: 'evidence', ai: 'invest' };
for (const s of ['crossref-preprints-explorer', 'crossref-preprint-harvesting-and-labeling', 'datacite-preprint-harvesting', 'openalex-preprint-metadata-extraction']) redirects[`/projects/${s}`] = '/projects/preprint-harvester-toolkit/';
for (const s of ['biomedical-ner-tf-idf-and-topic-modelling-tools', 'scientific-network-analysis-and-patent-preparation', 'postgresql-data-transfer-utility', 'biotech-sosci-research-pipelines']) redirects[`/projects/${s}`] = '/projects/analysis-code/';
redirects['/projects/cognosx-field-intelligence-initiative'] = '/#contact';
for (const a of areas) redirects[`/research/${a}`] = `/projects/#${areaToProgramme[a]}`;

export default defineConfig({
  site: 'https://descartesmbogning.github.io',
  output: 'static',
  trailingSlash: 'ignore',
  redirects,
  integrations: [sitemap({ filter: (page) => !page.includes('/edit/') && !Object.keys(redirects).some((r) => page.replace(/\/$/, '').endsWith(r)) })],
});
