#!/usr/bin/env python3
"""
build_console_catalog.py
Fetches the OpenCode console provider configuration and normalizes it into
data/console_models.json.

Source: GET https://opencode.ai/console/api/config
        (Authorization: Bearer $OPENCODE_API_KEY)

The response is the machine-readable catalog behind the OpenCode console:
every model offered through the opencode (Zen), opencode-go, OpenRouter and
NVIDIA NIM connections, with its real context/output limits, supported
modalities, tool/reasoning support, release date and exact pricing
(including cache pricing and long-context surcharges).

It carries no privacy/training information - that still comes from the
official Zen/Go documentation pages.

The file is regenerated on every update.sh run and is not tracked by git.
"""

import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_PATH = os.path.join(DATA_DIR, "console_models.json")

CONFIG_URL = os.environ.get(
    "CONSOLE_CONFIG_URL", "https://opencode.ai/console/api/config").strip()
REQUEST_TIMEOUT = 30


def fetch_config(api_key):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        CONFIG_URL,
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "best-llm-console/1.0"},
    )
    with urllib.request.urlopen(req, context=ctx, timeout=REQUEST_TIMEOUT) as res:
        return json.loads(res.read().decode("utf-8"))


def normalize_model(model):
    limit = model.get("limit") or {}
    cost = model.get("cost") or {}
    modalities = model.get("modalities") or {}
    out = {
        "name": model.get("name"),
        "family": model.get("family"),
        "release_date": model.get("release_date"),
        "status": model.get("status"),
        "disabled": bool(model.get("disabled")),
        "context_limit": limit.get("context"),
        "output_limit": limit.get("output"),
        "input_limit": limit.get("input"),
        "input_modalities": modalities.get("input") or [],
        "output_modalities": modalities.get("output") or [],
        "tool_call": bool(model.get("tool_call")),
        "reasoning": bool(model.get("reasoning")),
        "attachment": bool(model.get("attachment")),
        "temperature": bool(model.get("temperature")),
    }
    for key in ("input", "output", "cache_read", "cache_write", "context_over_200k"):
        if cost.get(key) is not None:
            out[f"cost_{key}"] = cost[key]
    provider = model.get("provider") or {}
    if provider.get("npm"):
        out["sdk"] = provider["npm"]
    if provider.get("api"):
        out["api"] = provider["api"]
    return out


def normalize(payload):
    providers = ((payload.get("config") or {}).get("provider")) or payload.get("providers") or {}
    out = {}
    for key, provider in providers.items():
        models = provider.get("models") or {}
        settings = provider.get("settings") or {}
        api = settings.get("baseURL") if isinstance(settings, dict) else None
        if not api:
            raw_api = provider.get("api")
            api = raw_api.get("url") if isinstance(raw_api, dict) else raw_api
        out[key] = {
            "name": provider.get("name"),
            "canonical": provider.get("canonical"),
            "api": api,
            "models": {mid: normalize_model(m) for mid, m in models.items()},
        }
    return out


def load_api_key():
    key = os.environ.get("OPENCODE_API_KEY", "").strip()
    if key:
        return key
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OPENCODE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main():
    api_key = load_api_key()
    if not api_key:
        print("console catalog skipped (no OPENCODE_API_KEY)")
        return
    try:
        payload = fetch_config(api_key)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        warn(f"console catalog unavailable ({type(e).__name__}); keeping previous data")
        return
    providers = normalize(payload)
    if not providers:
        warn("console catalog empty; keeping previous data")
        return
    write(providers)


def warn(message):
    print(("::warning::" if os.environ.get("GITHUB_ACTIONS") == "true" else "warning: ") + message, flush=True)


def write(providers):
    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "providers": providers,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    total = sum(len(p.get("models", {})) for p in providers.values())
    print(f"console catalog: {len(providers)} providers, {total} models -> {os.path.relpath(OUT_PATH, BASE_DIR)}")


if __name__ == "__main__":
    main()
