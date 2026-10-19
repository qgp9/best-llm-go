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
# Default chain: free Go flash models first (MiniMax M3.1 Flash Free,
# DeepSeek V4.1 Flash), then NIM/GLM flash as fallback.
MODELS = [m.strip() for m in os.environ.get(
    "SUMMARY_MODELS", os.environ.get(
        "SUMMARY_MODEL",
        "go:minimax-m3.1-flash-free,go:deepseek-v4.1-flash,go:glm-5.3-flash")
).strip().split(",") if m.strip()] or ["go:minimax-m3.1-flash-free"]
# Reasoning models burn the output budget on thinking tokens and can hit the
# length cutoff before emitting JSON. A low reasoning effort plus a larger
# completion budget keeps the response short and parseable.
REASONING_EFFORT = os.environ.get("SUMMARY_REASONING_EFFORT", "low").strip()
MAX_TOKENS = int(os.environ.get("SUMMARY_MAX_TOKENS", "16000"))
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


# --- catalog digest -------------------------------------------------------
# The summaries are cross-cutting guides, not per-category pick lists, so the
# model receives the whole catalog (every free model and every Go model) as a
# compact digest plus a topic-specific shortlist to steer attention.

def digest_free(free):
    lines = []
    for m in free:
        priv = m.get("privacy") or {}
        summary = m.get("summary") or {}
        lines.append(
            f"- {m.get('name')} | model_id={m.get('model_id')} | "
            f"platform={','.join(m.get('platform', []))} | provider={m.get('provider')} | "
            f"intel={m.get('intelligence_index')} coding={m.get('coding_index')} "
            f"ctx={m.get('context_window')} | "
            f"training={'no' if priv.get('is_safe') else 'yes'} | "
            f"{summary.get('one_liner', '')} {summary.get('recommended_for', '')}".rstrip()
        )
    return lines


def digest_go(go):
    lines = []
    for m in go:
        price = "unknown" if m.get("effective_price") is None else f"${m['effective_price']:.4f}/1M"
        lines.append(
            f"- {m.get('name')} | go_id={m.get('go_id')} | creator={m.get('creator')} | "
            f"index={m.get('index')} coding={m.get('coding')} | eff_price={price} | "
            f"allowance=${m.get('allowance')} | 5h_req={m.get('requests_5h')} | "
            f"kind={m.get('kind')} | "
            f"training={'yes' if m.get('trains_on_data') else 'no'}"
        )
    return lines


def digest_stats(free, go):
    safe_free = sum(1 for m in free if (m.get("privacy") or {}).get("is_safe"))
    tiers = {}
    for m in go:
        key = m.get("allowance")
        tiers[key] = tiers.get(key, 0) + 1
    tier_text = ", ".join(f"${k}: {v}" for k, v in sorted(tiers.items(), key=lambda kv: (kv[0] is None, kv[0])))
    return [
        f"free catalog: {len(free)} models (no-training {safe_free}, training {len(free) - safe_free})",
        f"go catalog: {len(go)} models (tiers {tier_text}; "
        f"$0 free {sum(1 for m in go if m.get('kind') == 'free')}, "
        f"training {sum(1 for m in go if m.get('trains_on_data'))})",
    ]


def build_digest(free, go):
    return "\n".join([
        "## Free model catalog (OpenCode Zen/Go, OpenRouter, CommandCode, NIM, ...)",
        *digest_free(free),
        "",
        "## OpenCode Go subscription models",
        *digest_go(go),
        "",
        "## Totals",
        *digest_stats(free, go),
    ])


# Cross-cutting topics. Each set gets the full digest plus a shortlist that
# highlights the models most relevant to the topic.
SET_DEFS = [
    {
        "id": "overview",
        "title": {"ko": "전체 시장 지도와 선택 원칙", "en": "Market map and how to choose"},
        "focus": {
            "ko": "무료($0) 모델과 Go 구독 모델의 구도, 각 구간에서 무엇이 우위인지, "
                  "한 줄로 말하는 선택 원칙. 무엇을 먼저 써야 하고 언제 유료/구독으로 넘어가야 하는지.",
            "en": "How the $0 free tier and the Go subscription divide the field, who wins in each "
                  "segment, and the one-line rule for choosing. What to try first and when to move on.",
        },
        "shortlist": lambda free, go: (
            [spec_free(m) for m in top(free, "intelligence_index", n=5)]
            + [spec_go(m) for m in top(go, "index", n=5)]
            + [spec_go(m) for m in top(go, "effective_price", n=3, reverse=False)]
        ),
    },
    {
        "id": "agentic",
        "title": {"ko": "에이전트·코딩 워크로드 가이드", "en": "Agentic and coding workload guide"},
        "focus": {
            "ko": "대규모 리팩토링, 테스트 작성, 멀티파일 에이전트, 롱컨텍스트 문서 분석, "
                  "이미지·멀티모달 작업별로 어떤 모델을 골라야 하는지. 컨텍스트 길이와 응답 속도 트레이드오프 포함.",
            "en": "Which model to pick per workload: large refactors, test writing, multi-file agents, "
                  "long-document analysis, image/multimodal work. Include context-length vs latency tradeoffs.",
        },
        "shortlist": lambda free, go: (
            [spec_free(m) for m in top([m for m in free if m.get("category") == "coding"], "coding_index", n=4)]
            + [spec_free(m) for m in top([m for m in free if m.get("category") == "long_context"], "context_tokens", n=3)]
            + [spec_free(m) for m in top(free, "intelligence_index", n=3)]
            + [spec_go(m) for m in top(go, "coding", n=4)]
        ),
    },
    {
        "id": "privacy",
        "title": {"ko": "데이터 프라이버시 가이드", "en": "Data privacy guide"},
        "focus": {
            "ko": "프롬프트가 학습에 사용되는 모델(Contributor)을 언제 써도 되고 언제 피해야 하는지, "
                  "ZDR(보존 0일) 모델 목록, 무료 티어의 한계와 사내 기밀 취급 지침.",
            "en": "When a prompt-training (Contributor) model is acceptable and when to avoid it, which "
                  "models are zero-retention, and how to treat confidential code on free tiers.",
        },
        "shortlist": lambda free, go: (
            [spec_free(m) for m in free if not (m.get("privacy") or {}).get("is_safe")]
            + [spec_free(m) for m in top([m for m in free if (m.get("privacy") or {}).get("is_safe")], "intelligence_index", n=4)]
            + [spec_go(m) for m in go if m.get("trains_on_data")]
        ),
    },
    {
        "id": "cost",
        "title": {"ko": "비용·쿼터 효율 가이드", "en": "Cost and quota efficiency guide"},
        "focus": {
            "ko": "월 한도 대비 비용 효율, 5시간 롤링 한도, Go 배율(x1.5/x3/x6)과 쿼터 소모율, "
                  "$0 무료 모델이 언제 실제로 가장 유리한지. 월 예산별 추천 조합.",
            "en": "Cost efficiency against the monthly cap, 5-hour rolling limits, Go multipliers "
                  "(x1.5/x3/x6) and quota burn, and when a $0 model is genuinely the best deal.",
        },
        "shortlist": lambda free, go: (
            [spec_go(m) for m in sorted(go, key=lambda m: (m.get("allowance") is None, m.get("allowance") or 0))]
            + [spec_free(m) for m in top(free, "intelligence_index", n=4)]
        ),
    },
    {
        "id": "free-guide",
        "title": {"ko": "무료 모델 카탈로그 총정리", "en": "Free model catalog guide"},
        "focus": {
            "ko": "무료로 쓸 수 있는 모델 전체 구도, 플랫폼별 차이(OpenCode Zen/Go, OpenRouter, "
                  "CommandCode, NIM), 카테고리별 최선, 무료 티어의 실질 한계.",
            "en": "The full landscape of models available for $0, how the platforms differ (OpenCode "
                  "Zen/Go, OpenRouter, CommandCode, NIM), the best per category, and real free-tier limits.",
        },
        "shortlist": lambda free, go: [spec_free(m) for m in free],
    },
    {
        "id": "go-guide",
        "title": {"ko": "Go 구독 가이드", "en": "Go subscription guide"},
        "focus": {
            "ko": "Go 구독 티어 구조($15/$30/$60)와 배율, 5시간 롤링 한도, 모델별 체감 단가와 "
                  "무료($0) 모델과의 관계, 구독이 실제로 이득인 작업.",
            "en": "How the Go tiers ($15/$30/$60) and multipliers work, the 5-hour rolling limits, "
                  "effective per-model price, and the workloads where the subscription actually pays off.",
        },
        "shortlist": lambda free, go: [spec_go(m) for m in go],
    },
]


def build_sets(free, go):
    digest = build_digest(free, go)
    sets = []
    for definition in SET_DEFS:
        shortlist = definition["shortlist"](free, go)
        sets.append({
            "id": definition["id"],
            "title": definition["title"]["ko"] + " / " + definition["title"]["en"],
            "focus": definition["focus"]["ko"] + "\n" + definition["focus"]["en"],
            "digest": digest,
            "models": shortlist,
        })
    return sets


PROMPT = """You are the analyst behind a developer-facing LLM comparison dashboard (OpenCode Go subscription + a unified free-model catalog).
Using ONLY the catalog digest and the focus shortlist below, write a structured recommendation for the topic: {title}

Respond with JSON only, exactly this shape (no markdown, no extra keys):
{
  "ko": {"headline": "<=160 chars",
         "picks": [{"model": "<=50 chars, exact model name from the digest", "why": "<=200 chars"}],
         "caveats": ["<=140 chars"],
         "howto": "<=260 chars"},
  "en": {"headline": "<=160 chars",
         "picks": [{"model": "<=50 chars, exact model name from the digest", "why": "<=200 chars"}],
         "caveats": ["<=140 chars"],
         "howto": "<=260 chars"}
}

Rules:
- ko is written in Korean, en is written in English.
- 2-4 picks, 0-4 caveats. Only name models that appear in the digest, using their exact names.
- Never invent metrics; if a metric is missing, say it is unknown.
- Cover the topic as a whole: who wins, when to pick which, and what to watch out for.
- howto is the concrete next step for a developer deciding right now.

Topic: {title}
Focus:
{focus}

Catalog digest:
{digest}

Focus shortlist:
{models}
"""

LIMITS = {"headline": 160, "model": 50, "why": 200, "caveat": 140, "howto": 260}
LANG_KEYS = {"headline", "picks", "caveats", "howto"}


def _text(value, limit, allow_empty=False):
    if not isinstance(value, str):
        raise SummaryError("summary-schema")
    value = value.strip()
    if not value and not allow_empty:
        raise SummaryError("summary-empty-or-type")
    if len(value) > limit:
        # Trim instead of dropping the whole summary: a slightly long answer is
        # still useful, whereas a missing one is not.
        value = value[:limit - 1].rstrip() + "…"
    return value


def _known_names(free, go):
    names = set()
    for m in free:
        if m.get("name"):
            names.add(str(m["name"]).strip().lower())
    for m in go:
        if m.get("name"):
            names.add(str(m["name"]).strip().lower())
    return names


def _model_is_known(pick, known):
    if not known:
        return True
    candidate = pick.strip().lower()
    for name in known:
        if candidate == name or name in candidate:
            return True
    return False


def parse_summary(text, known=None):
    text = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        text = match.group(1)
    try:
        parsed = json.loads(text)
    except (ValueError, TypeError):
        raise SummaryError("summary-json") from None
    if not isinstance(parsed, dict) or set(parsed) != {"ko", "en"}:
        raise SummaryError("summary-schema")
    known = known or set()
    for lang in ("ko", "en"):
        value = parsed[lang]
        if not isinstance(value, dict) or set(value) != LANG_KEYS:
            raise SummaryError("summary-schema")
        value["headline"] = _text(value["headline"], LIMITS["headline"])
        picks = value["picks"]
        if not isinstance(picks, list) or not 1 <= len(picks) <= 4:
            raise SummaryError("summary-schema")
        for pick in picks:
            if not isinstance(pick, dict) or set(pick) != {"model", "why"}:
                raise SummaryError("summary-schema")
            pick["model"] = _text(pick["model"], LIMITS["model"])
            pick["why"] = _text(pick["why"], LIMITS["why"])
            if not _model_is_known(pick["model"], known):
                raise SummaryError("summary-unknown-model")
        caveats = value["caveats"]
        if not isinstance(caveats, list) or len(caveats) > 4:
            raise SummaryError("summary-schema")
        value["caveats"] = [_text(c, LIMITS["caveat"]) for c in caveats]
        value["howto"] = _text(value["howto"], LIMITS["howto"], allow_empty=True)
    return parsed



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


def call_model(entry, prompt, deadline, known=None):
    route, model = model_route(entry)
    base = nim_endpoint(deadline) if route == "nim" else GO_BASE
    protocol = "responses" if route == "go" and model.startswith("muse-spark-") else "chat/completions"
    body = {"model": model, "temperature": 0.3}
    if protocol == "responses":
        body.update(input=prompt, max_output_tokens=MAX_TOKENS)
    else:
        body.update(messages=[{"role": "user", "content": prompt}], max_tokens=MAX_TOKENS)
    if REASONING_EFFORT and protocol == "chat/completions":
        body["reasoning_effort"] = REASONING_EFFORT
    try:
        raw = response_text(request_json(base + "/" + protocol, body, deadline), protocol)
    except SummaryError as e:
        # Not every upstream model accepts reasoning_effort; retry once
        # without it instead of losing the model from the fallback chain.
        if REASONING_EFFORT and protocol == "chat/completions" and str(e) == "http-400":
            body.pop("reasoning_effort", None)
            raw = response_text(request_json(base + "/" + protocol, body, deadline), protocol)
        else:
            raise
    return parse_summary(raw, known)


def summarize(spec, deadline, known=None):
    if not spec.get("models"):
        raise SummaryError("no-candidates")
    prompt = (PROMPT.replace("{title}", spec["title"])
              .replace("{focus}", spec["focus"])
              .replace("{digest}", spec["digest"])
              .replace("{models}", "\n".join(spec["models"])))
    for entry in MODELS:
        remaining(deadline)
        start = time.monotonic()
        try:
            result = call_model(entry, prompt, deadline, known)
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
    known = _known_names(free, go)
    out = {}
    print(f"sets: {len(sets)} (chain={MODELS})", flush=True)
    for s in sets:
        try:
            if not API_KEY:
                raise SummaryError("no-api-key")
            out[s["id"]] = {"title": s["title"], **summarize(s, deadline, known)}
            print(f"  ok: {s['id']}", flush=True)
        except SummaryError as e:
            warn(f"summary {s['id']} omitted: {e}")
    write_outputs(out)
    print(f"summaries: success={len(out)} failed={len(sets)-len(out)}", flush=True)


if __name__ == "__main__":
    main()
