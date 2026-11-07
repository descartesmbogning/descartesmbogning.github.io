"""Collect new newsletter posts (Substack) and videos (YouTube) into src/data/feeds.json.

Run every day by .github/workflows/deploy.yml. Items already saved are kept, so older
posts and videos stay on the site even when they drop out of the public feeds
(the YouTube feed only lists the latest 15 videos).

Settings are at the top of this file. Usage: python3 scripts/update_feeds.py [--offline dir]
"""
import argparse
import email.utils
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SUBSTACK_FEED = "https://cognosxinsights.substack.com/feed"
YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=UClc2RCJ9-CbE6NEgvoiNDgg"
UA = "descartesmbogning.github.io feed updater"
# Placeholder posts that should not appear on the site.
SKIP_TITLES = re.compile(r"^\s*(coming soon|test)\s*$", re.I)
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/data/feeds.json"
NS = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/",
      "yt": "http://www.youtube.com/xml/schemas/2015"}


BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def fetch(url, ua=UA, quiet=False):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/rss+xml, application/xml, */*"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:  # network hiccup: retry, then skip this source
            if attempt == 2:
                if not quiet:
                    print(f"::warning::{url}: {e}")
                return None
            time.sleep(3 * (attempt + 1))


def clean(text, limit=220):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def substack_raw():
    """Substack often blocks requests from cloud servers such as GitHub's. Try a normal
    browser-style request first, then a public RSS relay (rss2json) as a fallback."""
    raw = fetch(SUBSTACK_FEED, ua=BROWSER_UA, quiet=True)
    if raw:
        return raw
    relay = "https://api.rss2json.com/v1/api.json?rss_url=" + urllib.parse.quote(SUBSTACK_FEED, safe="")
    data = fetch(relay, quiet=True)
    try:
        items = json.loads(data or b"{}").get("items") or []
    except ValueError:
        items = []
    if not items:
        print("::warning::Substack could not be reached today (blocked or down); kept the saved posts.")
        return None
    print(f"Substack read through the rss2json relay ({len(items)} recent posts).")
    return [{"source": "Newsletter", "title": clean(i.get("title"), 300), "url": (i.get("link") or "").strip(),
             "date": (i.get("pubDate") or "")[:10], "summary": clean(i.get("description"))} for i in items]


def substack(xml):
    items = []
    for it in ET.fromstring(xml).iter("item"):
        date = it.findtext("pubDate") or ""
        try:
            date = email.utils.parsedate_to_datetime(date).date().isoformat()
        except Exception:
            date = ""
        items.append({"source": "Newsletter", "title": clean(it.findtext("title"), 300),
                      "url": (it.findtext("link") or "").strip(), "date": date,
                      "summary": clean(it.findtext("description"))})
    return items


def youtube(xml):
    items = []
    for e in ET.fromstring(xml).findall("atom:entry", NS):
        link = e.find("atom:link", NS)
        desc = e.find("media:group/media:description", NS)
        items.append({"source": "Video", "title": clean(e.findtext("atom:title", "", NS), 300),
                      "url": link.get("href") if link is not None else "",
                      "date": (e.findtext("atom:published", "", NS) or "")[:10],
                      "summary": clean(desc.text if desc is not None else "")})
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", help="folder with substack.xml and youtube.xml (for testing)")
    args = ap.parse_args()

    saved = [i for i in (json.loads(OUT.read_text()) if OUT.exists() else []) if not SKIP_TITLES.match(i.get("title", ""))]
    by_url = {i["url"]: i for i in saved if i.get("url")}

    sources = [(SUBSTACK_FEED, "substack.xml", substack), (YOUTUBE_FEED, "youtube.xml", youtube)]
    new = 0
    for url, fixture, parse in sources:
        if args.offline:
            raw = (Path(args.offline) / fixture).read_bytes()
        else:
            raw = substack_raw() if url == SUBSTACK_FEED else fetch(url)
        if not raw:
            continue
        try:
            found = raw if isinstance(raw, list) else parse(raw)
        except ET.ParseError as e:
            print(f"::warning::Could not read {url}: {e}")
            continue
        for item in found:
            if not item["url"] or not item["title"] or SKIP_TITLES.match(item["title"]):
                continue
            if item["url"] not in by_url:
                new += 1
            by_url[item["url"]] = {**by_url.get(item["url"], {}), **item}

    items = sorted(by_url.values(), key=lambda i: i.get("date", ""), reverse=True)
    text = json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    if not OUT.exists() or OUT.read_text() != text:
        OUT.write_text(text)
    print(f"{len(items)} posts and videos saved, {new} new.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"::error::Feed update failed: {e}")
        sys.exit(1)
