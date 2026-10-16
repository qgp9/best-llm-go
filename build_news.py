#!/usr/bin/env python3
"""Build a single chronological news feed (no sections).

Sources (all keyless, build-time only):
- HN Algolia: queries covering OpenCode Go/Zen, providers, general AI.
  (opencode CLI releases/changelog deliberately excluded — Go/Zen
  service news is what matters here.)
Output: data/news.json / .js  (items sorted newest-first, capped at 60)
"""
import json
import os
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


items = []

# --- HN Algolia (sole source: Go/Zen service news, providers, general AI) ---
QUERIES = ["OpenCode Zen", "OpenCode Go", "openrouter", "NVIDIA NIM", "AI coding agent", "decision model", "free LLM API"]
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
