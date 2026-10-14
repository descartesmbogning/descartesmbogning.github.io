# Editable research portfolio

Astro static portfolio for GitHub Pages. The content is separated from the layout.

## Update content
- Edit `src/data/profile.json` for name, headline, bio and links.
- Edit `src/data/projects.json` to add/edit/remove projects. Each item needs a unique `slug`; new pages are generated automatically.
- Edit `src/pages/index.astro` for homepage layout/styles and `src/pages/projects/[slug].astro` for case-study layout.
- Put images and a CV in `public/`, then link to them in the page templates or JSON data.

## Local preview
```bash
npm install
npm run dev
```

## Deploy
1. Create a **public** GitHub repository named `descartesmbogning.github.io`.
2. In `astro.config.mjs`, set `site` to `https://descartesmbogning.github.io` and no `base` setting is required for this user site.
3. Upload these files to the repository root and commit to `main`.
4. The workflow runs `npm install` before building. For more reproducible deployments, generate and commit a `package-lock.json` and switch to `npm ci`.
5. In repository **Settings → Pages**, choose **GitHub Actions** as the build/deployment source.
6. Push to `main`; the included workflow builds and deploys automatically.

For future edits, update JSON in GitHub's web editor and commit. The website will rebuild.

## Caution
This is a starter, not a published site. Verify project claims, authorship, links and publication status before sharing. Do not publish unpublished data, credentials, proprietary code, or private client information. Add a privacy-safe contact email only if desired.
