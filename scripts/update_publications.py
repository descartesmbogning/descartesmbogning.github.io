"""Find new publications on OpenAlex and ORCID and add them to src/data/publications.json.

Run weekly by .github/workflows/publications.yml. It never deletes or edits existing
entries: it only appends works whose DOI and title are not already listed, and refreshes
the "research works" number on the home page. The workflow then opens a pull request
so a person reviews every change before it goes live.

To stop a work from being proposed again, add its DOI (or exact title) to
scripts/publications_ignore.json.

Usage: python3 scripts/update_publications.py [--body pr_body.md] [--offline fixtures.json]
"""
import argparse
import datetime as dt
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

AUTHOR = "A5023046200"          # OpenAlex author ID
ORCID = "0000-0001-5581-3891"
NAME_RE = re.compile(r"mbogning|fonkou", re.I)
# Publisher notices that OpenAlex lists as separate works: never added as papers.
NOTICE_RE = re.compile(r"^\s*(expression of concern|retraction( note)?|retracted|erratum|corrigendum|correction)\b", re.I)
CONTACT = "cognosxx@gmail.com"  # public contact; OpenAlex and Crossref ask for one
ROOT = Path(__file__).resolve().parent.parent
PUBS = ROOT / "src/data/publications.json"
PROFILE = ROOT / "src/data/profile.json"
IGNORE = ROOT / "scripts/publications_ignore.json"
UA = f"descartesmbogning.github.io publication updater (mailto:{CONTACT})"

# OpenAlex / ORCID work types -> the site's labels. Anything else is skipped.
TYPES = {
    "article": "Article", "journal-article": "Article", "review": "Article", "letter": "Article",
    "editorial": "Article", "preprint": "Preprint", "posted-content": "Preprint",
    "dissertation": "Thesis", "book-chapter": "Book chapter", "book": "Book",
}


def get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # network hiccups: retry, then give up on this source
            if attempt == 2:
                print(f"::warning::{url.split('?')[0]}: {e}")
                return None
            time.sleep(3 * (attempt + 1))


def norm_doi(s):
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", s)
    return s


def norm_title(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def surname_first(name):
    """'Qing Han' -> 'Han, Qing'; our own name keeps its two-part surname."""
    if NAME_RE.search(name or ""):
        return "Mbogning Fonkou, Maxime Descartes"
    parts = (name or "").split()
    return name if len(parts) < 2 else f"{parts[-1]}, {' '.join(parts[:-1])}"


def author_string(names, limit=6):
    names = [n for n in names if n]
    s = "; ".join(names[:limit])
    return s + ("; et al." if len(names) > limit else "")


# ---------- sources ----------

def openalex_works():
    works, cursor = [], "*"
    while cursor:
        q = urllib.parse.urlencode({"filter": f"author.id:{AUTHOR}", "per-page": 200,
                                    "cursor": cursor, "mailto": CONTACT})
        data = get(f"https://api.openalex.org/works?{q}")
        if not data:
            break
        works += data.get("results", [])
        cursor = data.get("meta", {}).get("next_cursor")
    return works


def orcid_dois():
    data = get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    out = []
    for g in (data or {}).get("group", []):
        ws = (g.get("work-summary") or [{}])[0]
        doi = ""
        for e in ((ws.get("external-ids") or {}).get("external-id") or []):
            if e.get("external-id-type") == "doi":
                doi = norm_doi(e.get("external-id-value"))
        title = (((ws.get("title") or {}).get("title")) or {}).get("value", "")
        out.append({"doi": doi, "title": title, "type": ws.get("type", "")})
    return out


def openalex_by_doi(doi):
    return get(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?mailto={CONTACT}")


def crossref_authors(doi):
    data = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={CONTACT}")
    msg = (data or {}).get("message") or {}
    names = []
    for a in msg.get("author", []):
        fam, giv = a.get("family") or "", a.get("given") or ""
        names.append(f"{fam}, {giv}".strip(", ") if fam else (a.get("name") or ""))
    return names


# ---------- conversion ----------

def from_openalex(w, use_crossref=True):
    doi = norm_doi(w.get("doi"))
    kind = TYPES.get(w.get("type") or "")
    if not kind:
        return None
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    venue = src.get("display_name") or ""
    if kind == "Article" and (src.get("type") == "repository" or re.search(r"rxiv|preprint", venue, re.I)):
        kind = "Preprint"
    auths = w.get("authorships") or []
    names = crossref_authors(doi) if (doi and use_crossref) else []
    if not names:
        names = [surname_first((a.get("author") or {}).get("display_name") or a.get("raw_author_name") or "") for a in auths]
    first = bool(auths) and str((auths[0].get("author") or {}).get("id") or "").endswith(AUTHOR)
    if not first and names:
        first = bool(NAME_RE.search(names[0]))
    url = f"https://doi.org/{doi}" if doi else (loc.get("landing_page_url") or w.get("id") or "")
    return {
        "title": (w.get("display_name") or w.get("title") or "").strip(),
        "authors": author_string(names),
        "venue": venue,
        "year": str(w.get("publication_year") or ""),
        "type": kind,
        "firstAuthor": first,
        "notice": "Retracted" if w.get("is_retracted") else "",
        "url": url,
        "linkLabel": "Read",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", default="pr_body.md")
    ap.add_argument("--offline", help="JSON fixtures instead of live APIs (for testing)")
    args = ap.parse_args()

    pubs = json.loads(PUBS.read_text())
    ignore = json.loads(IGNORE.read_text()) if IGNORE.exists() else {"dois": [], "titles": []}
    skip_dois = {norm_doi(d) for d in ignore.get("dois", [])}
    skip_titles = {norm_title(t) for t in ignore.get("titles", [])}

    have_dois = {norm_doi(p["url"]) for p in pubs if "doi.org/" in p.get("url", "")}
    have_titles = {norm_title(p["title"]): p["title"] for p in pubs}

    if args.offline:
        fx = json.loads(Path(args.offline).read_text())
        oa, orc, author = fx["openalex"], fx["orcid"], fx.get("author")
        global crossref_authors, openalex_by_doi
        crossref_authors = lambda doi: fx.get("crossref", {}).get(doi, [])
        openalex_by_doi = lambda doi: fx.get("by_doi", {}).get(doi)
    else:
        oa, orc = openalex_works(), orcid_dois()
        author = get(f"https://api.openalex.org/authors/{AUTHOR}?mailto={CONTACT}")
    if not oa and not orc:
        print("No data from OpenAlex or ORCID; nothing changed.")
        Path(args.body).write_text("No changes.\n")
        return

    candidates, seen = [], set()
    for w in oa:
        candidates.append(("OpenAlex", w))
        seen.add(norm_doi(w.get("doi")))
    for o in orc:  # works on ORCID that OpenAlex did not attach to this author
        if o["doi"] and o["doi"] not in seen:
            w = openalex_by_doi(o["doi"])
            if w:
                candidates.append(("ORCID", w))
                seen.add(o["doi"])

    added, versions, skipped, notices = [], [], [], []
    for source, w in candidates:
        doi, title = norm_doi(w.get("doi")), (w.get("display_name") or "")
        nt = norm_title(title)
        if NOTICE_RE.search(title):
            notices.append(title)
            continue
        if not nt or doi in have_dois or nt in have_titles or doi in skip_dois or nt in skip_titles:
            continue
        if nt in {norm_title(a["title"]) for a in added}:
            continue
        rec = from_openalex(w, use_crossref=True)
        if rec is None:
            skipped.append(f"{title} ({w.get('type')})")
            continue
        close = difflib.get_close_matches(nt, list(have_titles), n=1, cutoff=0.9)
        if close:  # same work under a slightly different title: mention it, don't add it
            versions.append((rec, have_titles[close[0]]))
            continue
        rec["_source"] = source
        added.append(rec)

    lines = []
    if added:
        for r in added:
            r.pop("_source", None)
        pubs = sorted(pubs + added, key=lambda p: -int(p["year"] or 0))  # stable: keeps order within a year
        PUBS.write_text(json.dumps(pubs, ensure_ascii=False, indent=2) + "\n")
        lines += [f"Found **{len(added)} new work(s)** on OpenAlex/ORCID that are not on the Publications page yet.", "",
                  "| Year | Type | Title | Journal | First author | Notice |", "| --- | --- | --- | --- | --- | --- |"]
        for r in added:
            lines.append(f"| {r['year']} | {r['type']} | [{r['title']}]({r['url']}) | {r['venue']} | "
                         f"{'yes' if r['firstAuthor'] else ''} | {r['notice']} |")

    # refresh the "research works" number on the home page
    profile = json.loads(PROFILE.read_text())
    count = (author or {}).get("works_count")
    for m in profile.get("metrics", []):
        if m.get("label") == "research works" and count and str(count) != m["value"]:
            lines += ["", f"Home page: research works {m['value']} → {count} (OpenAlex)."]
            m["value"] = str(count)
            profile["metricsSource"] = f"OpenAlex author record, {dt.date.today():%B %Y} (research works)"
            PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")

    if not lines:
        print("No new publications.")
        Path(args.body).write_text("No changes.\n")
        return
    if versions:
        lines += ["", "**Not added: very similar title already listed** (usually the same work). "
                  "If one is really a separate work, add it by hand:"]
        lines += [f"- {r['title']} ({r['venue']}) ≈ already listed: {old}" for r, old in versions]
    lines += ["", "**Before merging, check:**",
              "- Each work is really yours (OpenAlex sometimes mixes up similar names).",
              "- Notices: add `\"notice\": \"Expression of concern\"` where a publisher issued one.",
              "", "To drop a work, delete it in *Files changed* → *Edit file*, or close this pull request and add its DOI "
              "to `scripts/publications_ignore.json` so it is not proposed again."]
    if skipped:
        lines += ["", "Not added (types the site doesn't list): " + "; ".join(skipped)]
    if notices:
        lines += ["", f"Skipped {len(notices)} publisher notice(s) (expressions of concern, corrections). "
                  "If one concerns a paper already listed, set its `notice` field:"]
        lines += [f"- {t}" for t in notices]
    Path(args.body).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def annotate(level, msg):
    """Show a message on the GitHub Actions run page (::notice / ::error)."""
    print(f"::{level}::" + msg.replace("%", "%25").replace("\r", "").replace("\n", "%0A"))


if __name__ == "__main__":
    import traceback
    try:
        main()
        body = Path(sys.argv[sys.argv.index("--body") + 1] if "--body" in sys.argv else "pr_body.md")
        annotate("notice", body.read_text()[:20000] if body.exists() else "done")
    except Exception:
        annotate("error", traceback.format_exc()[-3000:])
        raise
