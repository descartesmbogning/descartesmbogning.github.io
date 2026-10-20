# Scientific Contributions Archive — Version 2

Astro-powered, editable research archive for `https://descartesmbogning.github.io/`.

## Contents

One site in the CognosX palette (black, white, yellow) with five pages:

- **Home** – headline, research numbers, "About me" story and research areas, six featured projects, links to the other pages, contact.
- **Projects** – six research programmes plus an open-source toolbox (from `src/data/programmes.json`), each with its lead study, related projects, and the tools and skills used across them; search and status filter; one page per project.
- **Publications** – articles, preprints and thesis, with publisher notices labelled.
- **Experience & skills** – career, skills with proof, "beyond research" skills, degrees, and certificates (each with a "View certificate" link when `url` is set).

Old addresses (`/portfolio/`, `/research/…`, `/methods/`, `/credentials/`, `/about/`) forward to the new pages.

## Run locally

```bash
npm install
npm run dev
npm run build
npm run preview
```

## Update content without redesigning

Use **/edit/** on the live site (not linked from the public pages, so bookmark https://descartesmbogning.github.io/edit/): pick a file, edit the form, copy the result, then paste it over the file on GitHub (pencil icon, then "Commit changes"). Or edit the JSON directly:

| Information | File |
| --- | --- |
| Name, headline, summary, numbers, links, email, About text | `src/data/profile.json` |
| Projects (set `featured` 1–6 to show on Home; `status` is Published, In preparation, Software & data or Ongoing work) | `src/data/projects.json` |
| Research areas used as filters | `src/data/domains.json` |
| Publications | `src/data/publications.json` |
| Career and "Beyond research" | `src/data/experience.json` |
| Degrees | `src/data/qualifications.json` |
| Certificates | `src/data/certificates.json` |
| Skills with proof | `src/data/skills.json` |
| Talks | `src/data/talks.json` |

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

## Downloadable CV

The public CV lives at `public/cv/Mbogning-Fonkou-CV.pdf` (2 pages, no phone number or address).
To update it, either replace that file with a new PDF of the same name, or regenerate it from the data files:

```bash
python3 scripts/build_cv.py . cv.html          # builds the CV page from src/data
npx playwright install chromium                # once
node scripts/cv_to_pdf.js "$PWD/cv.html" public/cv/Mbogning-Fonkou-CV.pdf
```

## New publications are found automatically

Every Monday, `.github/workflows/publications.yml` runs `scripts/update_publications.py`. It asks
OpenAlex (author `A5023046200`) and ORCID (`0000-0001-5581-3891`) for your works and adds any whose
DOI and title are not already in `src/data/publications.json`. It also refreshes the "research works"
number on the home page. It never edits or removes existing entries.

The changes arrive as a pull request called **"New publications found"**, which GitHub emails you about.
Check that each work is yours, add a `notice` if a publisher issued one, then **Merge**. The site updates
a minute later. To run it right away, open **Actions → Check for new publications → Run workflow**.

To stop a work from being proposed again, add its DOI or exact title to `scripts/publications_ignore.json`:

```json
{ "dois": ["10.1234/example"], "titles": ["A paper that is not mine"] }
```

One-time setting (already needed for this to work): **Settings → Actions → General → Workflow permissions →
tick "Allow GitHub Actions to create and approve pull requests"**.

## Bacteria I described

`/species/` lists every bacterial species and genus you described, from `src/data/species.json`. Each entry has
`name`, `role` (`lead` or `co`), `status` (`Validly published` or `Effectively published`), `authority` (the LPSN
citation, for validly published names), `typeStrain`, `source`, `lpsn` (link), `papers` and an optional `note`.
When a name is validated on a new IJSEM Validation List, change its `status` and add its `authority`.

## Project images

Images live in `public/images/projects/` (WebP, at most 1600 px wide). Each project in `projects.json` has an
`images` list; the first image appears on the project's card and at the top of its page. Each entry has
`src`, `alt` (what the image shows, for screen readers), `caption`, `credit`, `fit` (`contain` for charts,
`cover` for photos), `width` and `height`, and `dark: true` for dark screenshots. Name new files after the
project's slug, e.g. `phage-therapy-patent-landscape-3.webp`.

## Research programmes

`src/data/programmes.json` decides how projects are grouped on the Projects page. Each programme has an `id`
(used in links such as `/projects/#preprints`), `title`, `question`, `summary`, a `lead` project slug and a
`members` list of slugs. Every project should appear in exactly one programme. The "Tools used" and "Skills"
lists are counted automatically from each project's `methods` and `skills`.
