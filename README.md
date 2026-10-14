# Scientific Contributions Archive — Version 2

Astro-powered, editable research archive for `https://descartesmbogning.github.io/`.

## Contents

- Homepage with the scientific journey and transparent record counts.
- Six interconnected research domains, with dedicated pages.
- Searchable **all-projects index** with 32 project areas and evidence notes.
- Project details generated automatically for each record.
- Publication catalogue (initial subset, pending complete reconciliation).
- Academic qualifications separated from course certificates.
- Searchable certification catalogue with 39 sourced entries.
- Methods & skills, About, and contact links.

## Run locally

```bash
npm install
npm run dev
npm run build
npm run preview
```

## Update content without redesigning

Edit the appropriate JSON file:

| Information | File |
| --- | --- |
| Name, headline, links, location | `src/data/profile.json` |
| Every research or software project | `src/data/projects.json` |
| Research domain labels and descriptions | `src/data/domains.json` |
| Publications and status notices | `src/data/publications.json` |
| Certificates and training | `src/data/certificates.json` |
| Academic degrees and qualifications | `src/data/qualifications.json` |
| Method and technical skill categories | `src/data/skills.json` |

Each project requires a unique slug and uses `domains` ids from `domains.json`. The build automatically makes `/projects/SLUG/` pages and connects them across their research domains. For citations and project figures, extend the relevant JSON record with public `links`, then update the `src/pages/projects/[slug].astro` detail template.

For source control, create a branch and pull request for future changes. The `.github/workflows/deploy.yml` workflow publishes the `main` branch automatically after a successful build.

### Privacy / academic integrity

**Do not upload private diploma or transcript scans, Gmail attachments, student numbers, identity numbers, signatures or addresses into this public repository.** Diplomas are listed as metadata only. Only use external verification links intentionally meant for public sharing. Remove token-bearing credential invitation URLs. Some entries were inventoried from LinkedIn screenshots, Gmail and selected Google Drive folders; they require title, issuer, date and duplicate reconciliation before treating this as a final audited record. Publications with retractions or expressions of concern must retain their status notices. Claims of software deployment, methods, leadership and specific individual contribution should be verified before promotion.

### Deployment

The repository name is `descartesmbogning.github.io` and `astro.config.mjs` has the corresponding site URL and no project base path. GitHub Pages -> Source: GitHub Actions. The workflow uses `npm install` and `npm run build`; it does not require a committed lockfile. Recommended: generate `package-lock.json` and switch to `npm ci` after verifying installation.

## Next editorial pass

1. Obtain a full Google Scholar BibTeX/CSV export, match DOIs, remove duplicates and update publication notices.
2. Verify doctoral diploma date, other degree descriptions and certificate authenticity. Retain original documents privately.
3. Add verified project figures and dashboard screenshots in `public/images` (with alt text and rights clearance).
4. Review GitHub project source, reproducibility, licences, and individual authorship.
5. Add a downloadable redacted CV and portfolio narrative when approved for publication.
