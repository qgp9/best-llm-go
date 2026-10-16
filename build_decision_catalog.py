#!/usr/bin/env python3
"""Build the Decision-models catalog (System One / Decisions API).

Live source: OpenRouter models catalog filtered by output_modalities=decisions.
Enriched with curated vendor-service info (OpenCode Zen, TypeSafe direct,
Cloudflare Workers AI, Laya) and free/paid flags.
Outputs: data/decision_models_catalog.json / .js
"""
import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- 1. Live fetch from OpenRouter ---
raw = []
try:
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models?output_modalities=decisions",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status == 200:
            raw = json.loads(resp.read().decode("utf-8")).get("data", [])
    with open(os.path.join(DATA_DIR, "openrouter_decision_models.json"), "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"live fetch failed ({e}), using cached snapshot")
    with open(os.path.join(DATA_DIR, "openrouter_decision_models.json"), encoding="utf-8") as f:
        raw = json.load(f)

print(f"Loaded {len(raw)} decision models from OpenRouter")

# --- 2. Curated enrichment: vendor service / open weights / notes ---
# vendor_service: where else the model family is served besides OpenRouter.
ENRICH = {
    "typesafe/jev-1.13": {
        "vendor_service": "TypeSafe direct + OpenCode Zen",
        "open_weights": False,
        "systemone": True,
        "platforms": ["OpenRouter", "OpenCode Zen", "TypeSafe"],
        "notes": "System One 원조. Choice 최대 255옵션, 32K 컨텍스트. OpenCode Zen에서 jev-1.13-free(무료) / jev-1.13($0.042/M) 제공.",
        "links": {"docs": "https://docs.typesafe.ai/concepts/system-one", "model_page": "https://openrouter.ai/typesafe/jev-1.13"},
    },
    "~typesafe/jev-latest": {
        "vendor_service": "TypeSafe direct + OpenCode Zen",
        "open_weights": False,
        "systemone": True,
        "platforms": ["OpenRouter", "OpenCode Zen", "TypeSafe"],
        "notes": "항상 최신 Jev를 가리키는 별칭(alias). 재현성이 필요하면 jev-1.13에 핀.",
        "links": {"docs": "https://docs.typesafe.ai/models", "model_page": "https://openrouter.ai/typesafe"},
    },
    "jaredpalmer/kev-4b": {
        "vendor_service": "OpenRouter only",
        "open_weights": True,
        "systemone": True,
        "platforms": ["OpenRouter"],
        "notes": "Qwen3.5-4B-Base 기반 LoRA+pointer head. TypeSafe와 동일한 /v1/systemone 규격.",
        "links": {"docs": "https://openrouter.ai/docs/guides/community/jev", "model_page": "https://openrouter.ai/jaredpalmer/kev-4b"},
    },
    "togethercomputer/tev1-4b-experimental": {
        "vendor_service": "Together AI",
        "open_weights": False,
        "systemone": True,
        "platforms": ["OpenRouter", "Together AI"],
        "notes": "Qwen3.5-4B 기반 실험 모델. 2~24개 옵션 중 1개 선택 특화.",
        "links": {"docs": "https://openrouter.ai/docs/guides/community/jev", "model_page": "https://openrouter.ai/togethercomputer/tev1-4b-experimental"},
    },
    "cloudflare/clef": {
        "vendor_service": "Cloudflare Workers AI",
        "open_weights": True,
        "systemone": True,
        "platforms": ["OpenRouter", "Cloudflare"],
        "notes": "Qwen3.8-27B 파인튠 멀티모달 decision 모델. Workers AI에서 직접 서빙.",
        "links": {"docs": "https://developers.cloudflare.com/workers-ai/", "model_page": "https://openrouter.ai/cloudflare/clef"},
    },
    "cloudflare/clef-flash": {
        "vendor_service": "Cloudflare Workers AI",
        "open_weights": True,
        "systemone": True,
        "platforms": ["OpenRouter", "Cloudflare"],
        "notes": "9B 고속 멤버. 저지연 라우팅용.",
        "links": {"docs": "https://developers.cloudflare.com/workers-ai/", "model_page": "https://openrouter.ai/cloudflare/clef-flash"},
    },
    "cloudflare/clef-omni": {
        "vendor_service": "Cloudflare Workers AI",
        "open_weights": True,
        "systemone": True,
        "platforms": ["OpenRouter", "Cloudflare"],
        "notes": "Qwen3-Omni-30B 기반 MoE(3B 활성) 옴니모달 멤버.",
        "links": {"docs": "https://developers.cloudflare.com/workers-ai/", "model_page": "https://openrouter.ai/cloudflare/clef-omni"},
    },
    "openai/gpt-6-luna-decisions": {
        "vendor_service": "OpenAI Decisions API",
        "open_weights": False,
        "systemone": False,
        "platforms": ["OpenRouter", "OpenAI"],
        "notes": "GPT-6 Luna의 Decisions 서빙. 텍스트+이미지 컨텍스트 지원(Preview).",
        "links": {"docs": "https://openrouter.ai/docs/guides/community/jev", "model_page": "https://openrouter.ai/openai/gpt-6-luna-decisions"},
    },
    "inception/mercury-decide:free": {
        "vendor_service": "Inception",
        "open_weights": False,
        "systemone": True,
        "platforms": ["OpenRouter"],
        "notes": "무료 티어 제공. System One 규격.",
        "links": {"docs": "https://openrouter.ai/docs/guides/community/jev", "model_page": "https://openrouter.ai/inception/mercury-decide"},
    },
    "respan/span-01-lite:free": {
        "vendor_service": "Respan",
        "open_weights": False,
        "systemone": False,
        "platforms": ["OpenRouter"],
        "notes": "대화 span 행동 스코어링 특화. Lite 무료 티어.",
        "links": {"docs": "https://openrouter.ai/docs/guides/community/jev", "model_page": "https://openrouter.ai/respan/span-01-lite"},
    },
}

catalog = []
seen_base = set()
for m in raw:
    mid = m.get("id", "")
    base = mid.replace(":free", "")
    # alias entries (~) and :free duplicates: keep but flag
    is_alias = mid.startswith("~")
    is_free_variant = mid.endswith(":free")
    pricing = m.get("pricing") or {}
    try:
        prompt = float(pricing.get("prompt", 0) or 0)
    except (TypeError, ValueError):
        prompt = 0.0
    per_m = prompt * 1_000_000
    ctx = m.get("context_length") or 0
    en = ENRICH.get(mid, ENRICH.get(base, {}))
    vendor = (mid.split("/")[0] if "/" in mid else "Unknown").lstrip("~")
    catalog.append({
        "id": mid,
        "base_id": base,
        "name": m.get("name", mid),
        "vendor": vendor.capitalize() if vendor.islower() else vendor,
        "description": (m.get("description") or "")[:300],
        "context_tokens": ctx,
        "context_window": f"{int(ctx/1000)}K" if ctx and ctx < 1000000 else (f"{round(ctx/1000000,1)}M" if ctx else "—"),
        "price_per_m_in": round(per_m, 4),
        "price_label": "무료" if per_m == 0 else f"${per_m:.3f}/1M in",
        "is_free": per_m == 0,
        "is_alias": is_alias,
        "platforms": en.get("platforms", ["OpenRouter"]),
        "vendor_service": en.get("vendor_service", "OpenRouter only"),
        "open_weights": en.get("open_weights", False),
        "systemone_compatible": en.get("systemone", True),
        "notes": en.get("notes", ""),
        "links": en.get("links", {"docs": "https://openrouter.ai/docs/guides/community/jev",
                                   "model_page": f"https://openrouter.ai/{base}"}),
    })

catalog.sort(key=lambda x: (x["price_per_m_in"], -(x["context_tokens"] or 0)))

with open(os.path.join(DATA_DIR, "decision_models_catalog.json"), "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
with open(os.path.join(DATA_DIR, "decision_models_catalog.js"), "w", encoding="utf-8") as f:
    f.write("window.__DECISION_MODELS_CATALOG__ = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n")

print(f"Total decision catalog: {len(catalog)} entries")
print("Wrote data/decision_models_catalog.json and .js")
