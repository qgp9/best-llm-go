#!/usr/bin/env python3
"""Generate daily ko/en summaries. Failed sets are omitted, never reused.

OPENCODE_API_KEY: environment > repository .env. SUMMARY_MODELS (or legacy
SUMMARY_MODEL) selects a comma-separated go:/nim: fallback chain; bare IDs use Go.
SUMMARY_BASE_URL overrides Go; SUMMARY_NIM_CONN overrides Console discovery.
"""
from contextlib import contextmanager
import http.client
import json
import os
import signal
import re
import socket
import tempfile
import time
import urllib.error
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
GO_BASE = os.environ.get(
    "SUMMARY_BASE_URL",
    "https://opencode.ai/inference/go/openai/v1").rstrip("/")
# Each chain entry: "go:<model>" (Go endpoint) or "nim:<model>"
# (console gateway -> NVIDIA custom connection, discovered at runtime).
# Default tries Muse Spark (Go) first, then NIM flash via console.
MODELS = [m.strip() for m in os.environ.get(
    "SUMMARY_MODELS", os.environ.get(
        "SUMMARY_MODEL",
        "go:muse-spark-1.3-contributor,nim:z-ai/glm-5.3-flash,"
        "go:glm-5.3-flash,go:mimo-v2.6-flash,go:deepseek-v4.1-flash")
).strip().split(",") if m.strip()] or ["go:glm-5.3-flash"]
SESSION_ID = os.environ.get("SUMMARY_SESSION_ID", "best-llm-daily-summaries")
NIM_CONN_ENV = os.environ.get("SUMMARY_NIM_CONN", "").strip()
NIM_KEY_HINT = os.environ.get("SUMMARY_NIM_KEY", "console-nvidia").strip()

_NIM_URL = None
REQUEST_TIMEOUT = 90
RUN_TIMEOUT = 900


class SummaryError(Exception):
    """A safe diagnostic code, never a remote response body."""


def remaining(deadline):
    left = deadline - time.monotonic()
    if left <= 0:
        raise SummaryError("deadline")
    return left


@contextmanager
def transfer_timeout(seconds):
    """Linux CI: interrupt slow headers/body reads at the absolute deadline."""
    def expired(signum, frame):
        raise TimeoutError()
    previous = signal.signal(signal.SIGALRM, expired)
    timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, *timer)
        signal.signal(signal.SIGALRM, previous)


def request_json(url, body=None, deadline=None):
    deadline = deadline if deadline is not None else time.monotonic() + RUN_TIMEOUT
    for attempt in range(2):
        remaining(deadline)
        req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {API_KEY}",
                     "Content-Type": "application/json",
                     "User-Agent": "best-llm-summaries/1.0",
                     "x-opencode-session": SESSION_ID})
        retry = False
        start = time.monotonic()
        try:
            # Bound the entire transfer as well as each blocking socket read.
            with transfer_timeout(min(REQUEST_TIMEOUT, remaining(deadline))), \
                    urllib.request.urlopen(req, timeout=min(REQUEST_TIMEOUT, remaining(deadline))) as r:
                chunks = []
                request_deadline = min(deadline, time.monotonic() + REQUEST_TIMEOUT)
                while True:
                    remaining(request_deadline)
                    chunk = r.read1(65536)
                    remaining(request_deadline)
                    if not chunk:
                        break
                    chunks.append(chunk)
                try:
                    return json.loads(b"".join(chunks))
                except (ValueError, UnicodeError):
                    raise SummaryError("response-json") from None
        except urllib.error.HTTPError as e:
            code = e.code
            e.close()
            error = f"http-{code}"
            retry = code == 429 or 500 <= code < 600
        except (TimeoutError, socket.timeout):
            error, retry = "timeout", True
        except urllib.error.URLError as e:
            error = "timeout" if isinstance(e.reason, (TimeoutError, socket.timeout)) else "network"
            retry = True
        except (http.client.HTTPException, ConnectionError, OSError):
            error, retry = "network", True
        if retry and attempt == 0:
            label = body["model"] if body else "discovery"
            print(f"    model={label} stage={error} attempt=1 retry=1 elapsed={time.monotonic()-start:.1f}s", flush=True)
            time.sleep(min(1, remaining(deadline)))
            continue
        raise SummaryError(error)


def nim_endpoint(deadline):
    global _NIM_URL
    if _NIM_URL:
        return _NIM_URL
    if NIM_CONN_ENV:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", NIM_CONN_ENV):
            raise ValueError("invalid SUMMARY_NIM_CONN")
        _NIM_URL = f"https://opencode.ai/inference/custom/{NIM_CONN_ENV}"
    else:
        conns = request_json("https://opencode.ai/console/api/providers", deadline=deadline)
        if not isinstance(conns, list):
            raise SummaryError("discovery-shape")
        matches = [c for c in conns if isinstance(c, dict)
                   and c.get("configKey") == NIM_KEY_HINT and c.get("enabled") is True]
        if len(matches) != 1 or not isinstance(matches[0].get("id"), str):
            raise SummaryError("discovery-no-unique-enabled-connection")
        conn = matches[0]["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", conn):
            raise SummaryError("discovery-invalid-id")
        _NIM_URL = f"https://opencode.ai/inference/custom/{conn}"
    return _NIM_URL


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
    price = "unknown" if m.get("effective_price") is None else f"${m['effective_price']:.4f}/1M"
    return (f"{m.get('name')} | creator={m.get('creator')} | "
            f"index={m.get('index')} coding={m.get('coding')} "
            f"eff_price={price} allowance=${m.get('allowance')} "
            f"5h_req={m.get('requests_5h')}")


def top(models, key, n=6, reverse=True):
    known = [m for m in models if m.get(key) is not None]
    unknown = [m for m in models if m.get(key) is None]
    return (sorted(known, key=lambda m: m[key], reverse=reverse) + unknown)[:n]


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

Use only supplied candidates and facts. Missing metrics are unknown; do not invent scores or availability.

Set: {title}
Candidates:
{models}
"""


def parse_summary(text):
    text = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        text = match[1]
    try:
        parsed = json.loads(text)
    except (ValueError, TypeError):
        raise SummaryError("summary-json") from None
    if not isinstance(parsed, dict) or set(parsed) != {"ko", "en"}:
        raise SummaryError("summary-schema")
    for lang in ("ko", "en"):
        value = parsed[lang]
        if not isinstance(value, str) or not value.strip():
            raise SummaryError("summary-empty-or-type")
        if len(value) > 500:
            raise SummaryError("summary-too-long")
    return {lang: parsed[lang].strip() for lang in ("ko", "en")}


def model_route(entry):
    route, model = entry.split(":", 1) if ":" in entry else ("go", entry)
    if route not in ("go", "nim") or not model or not re.fullmatch(r"[A-Za-z0-9_./:-]+", model):
        raise ValueError("invalid SUMMARY_MODELS entry")
    return route, model


def response_text(res, protocol):
    if not isinstance(res, dict):
        raise SummaryError("response-shape")
    if protocol == "responses":
        if res.get("status") != "completed":
            details = res.get("incomplete_details")
            if isinstance(details, dict) and details.get("reason") == "max_output_tokens":
                raise SummaryError("response-length")
            raise SummaryError("response-failed" if res.get("status") == "failed" else "response-incomplete")
        output = res.get("output")
        if not isinstance(output, list):
            raise SummaryError("response-shape")
        for item in output:
            if not isinstance(item, dict) or (item.get("type") == "message" and not isinstance(item.get("content"), list)):
                raise SummaryError("response-shape")
        texts = [c.get("text") for item in output
                 if isinstance(item, dict) and item.get("type") == "message"
                 for c in item.get("content", []) if isinstance(c, dict)
                 and c.get("type") == "output_text" and isinstance(c.get("text"), str)]
        text = "".join(texts)
    else:
        choices = res.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise SummaryError("response-choices")
        reason = choices[0].get("finish_reason")
        if reason != "stop":
            raise SummaryError("response-length" if reason == "length" else "response-not-stopped")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise SummaryError("response-shape")
        text = message.get("content")
    if not isinstance(text, str) or not text.strip():
        raise SummaryError("response-empty")
    return text


def call_model(entry, prompt, deadline):
    route, model = model_route(entry)
    base = nim_endpoint(deadline) if route == "nim" else GO_BASE
    protocol = "responses" if route == "go" and model.startswith("muse-spark-") else "chat/completions"
    body = {"model": model, "temperature": 0.3}
    if protocol == "responses":
        body.update(input=prompt, max_output_tokens=8000)
    else:
        body.update(messages=[{"role": "user", "content": prompt}], max_tokens=8000)
    return parse_summary(response_text(request_json(base + "/" + protocol, body, deadline), protocol))


def summarize(title, models, deadline):
    if not models:
        raise SummaryError("no-candidates")
    prompt = PROMPT.replace("{title}", title).replace("{models}", "\n".join(models))
    for entry in MODELS:
        remaining(deadline)
        start = time.monotonic()
        try:
            result = call_model(entry, prompt, deadline)
        except SummaryError as e:
            print(f"    model={entry} stage={e} elapsed={time.monotonic()-start:.1f}s", flush=True)
        else:
            print(f"    model={entry} stage=ok elapsed={time.monotonic()-start:.1f}s", flush=True)
            return result
    raise SummaryError("all-models-failed")


def write_outputs(out):
    # Stage both serializations before replacing either published file.
    staged = []
    try:
        for path, content in ((OUT_JSON, json.dumps(out, ensure_ascii=False, indent=2) + "\n"),
                              (OUT_JS, "window.__SUMMARIES__ = " + json.dumps(out, ensure_ascii=False) + ";\n")):
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(path),
                                             delete=False) as f:
                staged.append((f.name, path))
                f.write(content)
            os.chmod(f.name, 0o644)
        for temp, path in staged:
            os.replace(temp, path)
    finally:
        for temp, _ in staged:
            if os.path.exists(temp):
                os.unlink(temp)


def warn(message):
    print(("::warning::" if os.environ.get("GITHUB_ACTIONS") == "true" else "warning: ") + message, flush=True)


def main():
    deadline = time.monotonic() + RUN_TIMEOUT
    for entry in MODELS:
        model_route(entry)  # Configuration errors must not masquerade as model outages.
    free, go = load(FREE_PATH), load(GO_PATH)
    if not isinstance(free, list) or not isinstance(go, list):
        raise ValueError("catalogs must be arrays")
    sets = build_sets(free, go)
    out = {}
    print(f"sets: {len(sets)} (chain={MODELS})", flush=True)
    for s in sets:
        try:
            if not API_KEY:
                raise SummaryError("no-api-key")
            out[s["id"]] = {"title": s["title"], **summarize(s["title"], s["models"], deadline)}
            print(f"  ok: {s['id']}", flush=True)
        except SummaryError as e:
            warn(f"summary {s['id']} omitted: {e}")
    write_outputs(out)
    print(f"summaries: success={len(out)} failed={len(sets)-len(out)}", flush=True)


if __name__ == "__main__":
    main()
