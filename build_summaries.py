#!/usr/bin/env python3
"""Build-time LLM summaries for a handful of representative sets.

Runs daily in CI (update.sh). For each representative set it picks the
top models from the already-built catalogs and asks an LLM for a short
ko+en summary (2-3 lines + top-3 one-line reasons). Results go to
data/summaries.json / .js.

Uses the OpenCode Go inference endpoint, so a single OPENCODE_API_KEY
covers it (no separate OpenRouter/NVIDIA keys). Key resolution order:
env var > .env file in repo root > skip. Without a key it keeps the
previous summaries.json untouched and exits 0 — the site simply shows
the last generated summaries.

SUMMARY_MODELS: comma-separated fallback chain of OpenCode model IDs
(default: "glm-5.3-flash,mimo-v2.6-flash,deepseek-v4.1-flash").
Free/event models get delisted without notice, so each set tries
them in order. SUMMARY_BASE_URL overrides the endpoint.
"""
import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Minimal .env loader (no dependency): KEY=value lines, ignores # comments.
_env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            _k, _v = _k.strip(), _v.strip().strip("'\"")
            if _k and _k not in os.environ:
                os.environ[_k] = _v

API_KEY = os.environ.get("OPENCODE_API_KEY", "").strip()
BASE_URL = os.environ.get(
    "SUMMARY_BASE_URL",
    "https://opencode.ai/inference/go/openai/v1").rstrip("/")
# Comma-separated fallback chain of OpenCode model IDs.
MODELS = [m.strip() for m in os.environ.get(
    "SUMMARY_MODELS", os.environ.get(
        "SUMMARY_MODEL", "glm-5.3-flash,mimo-v2.6-flash,deepseek-v4.1-flash")
).strip().split(",") if m.strip()] or ["glm-5.3-flash"]
SESSION_ID = os.environ.get("SUMMARY_SESSION_ID", "best-llm-daily-summaries")

FREE_PATH = os.path.join(DATA_DIR, "free_models_catalog.json")
GO_PATH = os.path.join(DATA_DIR, "opencode_go_complete.json")
OUT_JSON = os.path.join(DATA_DIR, "summaries.json")
OUT_JS = os.path.join(DATA_DIR, "summaries.js")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def spec_free(m):
    s = m.get("summary", {}) or {}
    return (f"{m.get('name')} ({m.get('model_id')}) | "
            f"platform={','.join(m.get('platform', []))} | "
            f"intel={m.get('intelligence_index')} coding={m.get('coding_index')} "
            f"ctx={m.get('context_window')} | {s.get('one_liner', '')} "
            f"rec:{s.get('recommended_for', '')}")


def spec_go(m):
    return (f"{m.get('name')} | creator={m.get('creator')} | "
            f"index={m.get('index')} coding={m.get('coding')} "
            f"eff_price=${(m.get('effective_price') or 0):.4f}/1M allowance=${m.get('allowance')} "
            f"5h_req={m.get('requests_5h')}")


def top(models, key, n=6, reverse=True):
    return sorted(models, key=lambda m: (m.get(key) is not None, m.get(key) or 0),
                  reverse=reverse)[:n]


def build_sets(free, go):
    safe = [m for m in free if (m.get("privacy") or {}).get("is_safe")]
    return [
        {"id": "free-overall", "title": "무료 전체 추천",
         "models": [spec_free(m) for m in top(free, "intelligence_index")]},
        {"id": "free-coding", "title": "무료 코딩용",
         "models": [spec_free(m) for m in top([m for m in free if m.get("category") == "coding"], "coding_index")]},
        {"id": "free-reasoning", "title": "무료 추론용",
         "models": [spec_free(m) for m in top([m for m in free if m.get("category") == "reasoning"], "intelligence_index")]},
        {"id": "free-longcontext", "title": "무료 롱컨텍스트",
         "models": [spec_free(m) for m in top([m for m in free if m.get("category") == "long_context"], "context_tokens")]},
        {"id": "free-fast", "title": "무료 경량/빠른 응답",
         "models": [spec_free(m) for m in top([m for m in free if m.get("category") == "lightweight"], "intelligence_index")]},
        {"id": "free-private", "title": "무료 + 학습 미사용",
         "models": [spec_free(m) for m in top(safe, "intelligence_index")]},
        {"id": "go-overall", "title": "Go 가성비 종합",
         "models": [spec_go(m) for m in top(go, "index")]},
        {"id": "go-coding", "title": "Go 코딩용",
         "models": [spec_go(m) for m in top(go, "coding")]},
        {"id": "go-budget", "title": "Go 저예산",
         "models": [spec_go(m) for m in top(go, "effective_price", reverse=False)]},
    ]


PROMPT = """You compare LLM options for developers. Given the candidate models below, write a concise summary.

Respond with JSON only: {"ko": "...", "en": "..."}
Each text: 2-3 sentences naming the top 2-3 picks and when to choose which. No markdown, no extra keys. Keep each under 500 characters.

Set: {title}
Candidates:
{models}
"""


def summarize(title, models):
    last_err = None
    for model in MODELS:
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user",
                          "content": PROMPT.replace("{title}", title).replace(
                              "{models}", chr(10).join(models))}],
            "temperature": 0.3,
            "max_tokens": 1500,
        }).encode()
        try:
            req = urllib.request.Request(
                BASE_URL + "/chat/completions", data=body,
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json",
                         "User-Agent": "best-llm-summaries/1.0",
                         "x-opencode-session": SESSION_ID})
            with urllib.request.urlopen(req, timeout=90) as r:
                res = json.load(r)
            msg = res["choices"][0]["message"]
            text = (msg.get("content") or "").strip()
            if not text:
                raise RuntimeError("empty content (thinking-only response)")
            # strip code fences if any
            if text.startswith("```"):
                text = text.strip("`").split("\n", 1)[1] if "\n" in text else text.strip("`")
                if text.lstrip().startswith("json"):
                    text = text.lstrip()[4:].lstrip()
            parsed = json.loads(text)
            assert isinstance(parsed.get("ko"), str) and isinstance(parsed.get("en"), str)
            if model != MODELS[0]:
                print(f"    (fell back to {model})", end=" ")
            return {"ko": parsed["ko"][:600], "en": parsed["en"][:600]}
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"all summary models failed {MODELS}: {last_err}")


def main():
    free, go = load(FREE_PATH), load(GO_PATH)
    sets = build_sets(free, go)
    print(f"sets: {len(sets)} (endpoint={BASE_URL} models={MODELS})")
    if not API_KEY:
        print("no OPENCODE_API_KEY (env or .env) — keeping previous summaries.json")
        if not os.path.exists(OUT_JSON):
            with open(OUT_JSON, "w", encoding="utf-8") as f:
                json.dump({}, f)
            with open(OUT_JS, "w", encoding="utf-8") as f:
                f.write("window.__SUMMARIES__ = {};\n")
        return
    prev = {}
    if os.path.exists(OUT_JSON):
        try:
            prev = load(OUT_JSON)
        except Exception:
            prev = {}
    out = dict(prev)
    for s in sets:
        try:
            out[s["id"]] = {"title": s["title"], **summarize(s["title"], s["models"])}
            print(f"  ok: {s['id']}")
        except Exception as e:
            print(f"  fail: {s['id']} ({e}) — keeping previous" if s["id"] in out
                  else f"  fail: {s['id']} ({e})")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("window.__SUMMARIES__ = " + json.dumps(out, ensure_ascii=False) + ";\n")
    print(f"wrote summaries: {len(out)} sets")


if __name__ == "__main__":
    main()
