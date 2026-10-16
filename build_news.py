#!/usr/bin/env python3
"""Build a single chronological news feed (no sections).

Sources (all keyless, build-time only):
- GitHub Releases: sst/opencode (versions, dates, notes)
- opencode.ai/changelog: latest entry (static HTML)
- HN Algolia: queries covering OpenCode / providers / general AI
Output: data/news.json / .js  (items sorted newest-first, capped at 60)
"""
import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0"}


def get_json(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def get_text(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


items = []

# --- 1. GitHub releases: sst/opencode ---
try:
    rels = get_json("https://api.github.com/repos/sst/opencode/releases?per_page=12")
    if isinstance(rels, list):
        for r in rels:
            if not isinstance(r, dict) or r.get("draft"):
                continue
            tag = r.get("tag_name", "") or ""
            if tag.startswith("pr-"):
                continue  # PR demo artifacts, not releases
            body = (r.get("body") or "").strip().split("\n")
            summary = next((l.strip("# *") for l in body if l.strip("# *")[:1].isalnum()), "")
            items.append({
                "date": (r.get("published_at") or "")[:10],
                "ts": int(datetime.fromisoformat((r.get("published_at") or "2000-01-01T00:00:00Z").replace("Z", "+00:00")).timestamp()),
                "source": "OpenCode Releases",
                "title": f"{r.get('tag_name', '')} — {(r.get('name') or '')[:80]}".strip(" —"),
                "summary": summary[:220],
                "url": r.get("html_url", ""),
            })
    print(f"github releases: {len([i for i in items if i['source']=='OpenCode Releases'])}")
except Exception as e:
    print(f"github releases failed: {e}")

# --- 2. opencode.ai/changelog latest entry ---
try:
    html = get_text("https://opencode.ai/changelog")
    text = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "|", text)
    text = re.sub(r"\|+", "|", text)
    m = re.search(r"\|(v\d+\.\d+\.\d+)\|([A-Z][a-z]+ \d{1,2}, \d{4})\|(.{20,600})", text)
    if m:
        ver, datestr, body = m.groups()
        dt = datetime.strptime(datestr, "%B %d, %Y").replace(tzinfo=timezone.utc)
        items.append({
            "date": dt.strftime("%Y-%m-%d"),
            "ts": int(dt.timestamp()),
            "source": "OpenCode Changelog",
            "title": f"{ver} — changelog highlights",
            "summary": re.sub(r"\|", " ", body)[:220],
            "url": "https://opencode.ai/changelog",
        })
        print(f"changelog: {ver} {datestr}")
except Exception as e:
    print(f"changelog failed: {e}")

# --- 3. HN Algolia ---
QUERIES = ["opencode", "openrouter", "NVIDIA NIM", "AI coding agent", "decision model"]
since = int(time.time()) - 90 * 86400
for q in QUERIES:
    try:
        url = ("https://hn.algolia.com/api/v1/search?tags=story"
               f"&query={urllib.parse.quote(q)}&hitsPerPage=6"
               f"&numericFilters=created_at_i>{since}")
        d = get_json(url)
        for h in d.get("hits", []):
            link = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            items.append({
                "date": (h.get("created_at") or "")[:10],
                "ts": h.get("created_at_i", 0),
                "source": f"Hacker News · {q}",
                "title": h.get("title", ""),
                "summary": f"▲{h.get('points', 0)} · 💬{h.get('num_comments', 0)}",
                "url": link,
            })
        print(f"hn '{q}': {d.get('nbHits', 0)} hits total, took {len(d.get('hits', []))}")
    except Exception as e:
        print(f"hn '{q}' failed: {e}")

# dedupe by url, newest first, cap 60
seen, feed = set(), []
for it in sorted(items, key=lambda x: x["ts"], reverse=True):
    if it["url"] in seen or not it["title"]:
        continue
    seen.add(it["url"])
    feed.append(it)
    if len(feed) >= 60:
        break

meta = {"fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "count": len(feed)}
with open(os.path.join(DATA_DIR, "news.json"), "w", encoding="utf-8") as f:
    json.dump({"meta": meta, "items": feed}, f, ensure_ascii=False, indent=2)
with open(os.path.join(DATA_DIR, "news.js"), "w", encoding="utf-8") as f:
    f.write("window.__NEWS_FEED__ = " + json.dumps({"meta": meta, "items": feed}, ensure_ascii=False) + ";\n")

print(f"news feed: {len(feed)} items, {meta['fetched_at_utc']}")
