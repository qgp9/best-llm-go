import json
import os
import re

import console_data

# OpenCode console provider catalog: authoritative context/output limits,
# supported modalities, tool support, release dates and list prices.
CONSOLE_PROVIDERS = console_data.load()
CONSOLE_INDEX = console_data.build_index(CONSOLE_PROVIDERS)
GO_ROWS = []
if os.path.exists('data/opencode_go_complete.json'):
    with open('data/opencode_go_complete.json', 'r', encoding='utf-8') as f:
        GO_ROWS = json.load(f)


def console_entry(model_id):
    # console ids are keyed by their last path segment
    return console_data.lookup(CONSOLE_INDEX, (model_id or '').split('/')[-1], allow_prefix=False)


def format_context(tokens):
    if not tokens:
        return None
    if tokens >= 1000000:
        return f"{round(tokens / 1000000, 1)}M"
    return f"{int(tokens / 1000)}K"


# 1. OpenRouter Live Free Models Data
or_file = 'data/openrouter_free_models.json'
or_free_models_raw = []

# Try live fetch first if network is available
try:
    import urllib.request
    req = urllib.request.Request("https://openrouter.ai/api/v1/models", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        if resp.status == 200:
            data = json.loads(resp.read().decode('utf-8'))
            for m in data.get('data', []):
                p = m.get('pricing', {})
                try:
                    p_val = float(p.get('prompt', 0) or 0)
                    c_val = float(p.get('completion', 0) or 0)
                except:
                    p_val, c_val = -1, -1
                mid = m.get('id', '')
                if (p_val == 0.0 and c_val == 0.0) or mid.endswith(':free') or ':free' in mid:
                    or_free_models_raw.append(m)
            with open(or_file, 'w', encoding='utf-8') as out:
                json.dump(or_free_models_raw, out, ensure_ascii=False, indent=2)
except Exception:
    pass

# Fallback to local cached file
if not or_free_models_raw and os.path.exists(or_file):
    with open(or_file, 'r', encoding='utf-8') as f:
        or_free_models_raw = json.load(f)

print(f"Loaded {len(or_free_models_raw)} raw free models from OpenRouter API")

# 1b. OpenRouter 공급자별 데이터 정책(학습/보존) 조회
or_provider_policy = {}
try:
    import urllib.request
    req = urllib.request.Request("https://openrouter.ai/api/frontend/v1/all-providers",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        if resp.status == 200:
            pdata = json.loads(resp.read().decode('utf-8')).get('data', [])
            for p in pdata:
                if p.get('slug'):
                    or_provider_policy[p['slug']] = p.get('dataPolicy') or {}
    print(f"Loaded {len(or_provider_policy)} OpenRouter provider data policies")
except Exception as e:
    print(f"Provider policy fetch skipped ({e})")

# Catalog Builder
catalog = []

# --- SECTION 1: OpenRouter Free Models ---
for m in or_free_models_raw:
    mid = m.get('id', '')
    name = m.get('name', mid)
    ctx = m.get('context_length') or 128000
    bench = m.get('benchmarks', {}) or {}
    aa = bench.get('artificial_analysis', {}) or {}
    intel_idx = aa.get('intelligence_index')
    coding_idx = aa.get('coding_index')
    desc = m.get('description', '')
    
    # Clean name
    clean_name = name.replace(' (free)', '').replace(': ', ' · ')
    
    # Categorization and insights
    provider = mid.split('/')[0] if '/' in mid else 'OpenRouter'
    category = "general"
    strengths = []
    drawbacks = []
    identity = ""
    rec = ""
    aa_name = None

    # console catalog: real context limit, modalities, tools, list price
    or_entry = console_entry(mid)
    or_model = or_entry['model'] if or_entry else {}
    or_context = or_model.get('context_limit') or ctx
    or_modalities = or_model.get('input_modalities') or []
    or_multimodal = [m for m in or_modalities if m != 'text']
    or_base = console_data.base_model_for(mid, CONSOLE_INDEX, GO_ROWS, or_model.get('family'), or_entry['provider'] if or_entry else None)
    
    if "ling-3.1-flash" in mid:
        category = "reasoning"
        clean_name = "Ling 3.1 Flash (inclusionAI)"
        identity = "inclusionAI(Ant Group/알리바바 계열)의 최신 560B MoE 하이브리드 추론 모델"
        strengths = ["지능 지수 41.1점으로 무료 모델 중 독보적 1위", "25B 활성 파라미터로 매우 빠른 응답", "복합 추론 및 에이전트 도구 호출(Tool Calling) 우수"]
        drawbacks = ["한국어/일반 지식보다는 영문 코딩 및 수리 추론에 집중"]
        rec = "무료 모델로 Claude 3.5 Sonnet / GLM-5.3급의 고난도 코드 리팩토링이나 아키텍처 설계를 시도할 때 1순위 추천"
    elif "ling-3.0" in mid:
        category = "reasoning"
        clean_name = "Ling 3.0 Flash Sante"
        identity = "Ling 3.1의 이전 세대 안정화 추론 모델"
        strengths = ["262K 컨텍스트", "MoE 구조 기반 빠른 처리 속도"]
        drawbacks = ["Ling 3.1 대비 추론 정밀도 약간 낮음"]
        rec = "Ling 3.1의 분당 요청 한도(RPM) 초과 시 대체 백업 모델"
    elif "nemotron-3-ultra" in mid:
        category = "reasoning"
        clean_name = "Nemotron 3 Ultra (550B MoE)"
        identity = "NVIDIA의 550B 초거대 파라미터(55B 활성) 오픈 웨이트 플래그십"
        strengths = ["100만 토큰(1M) 대규모 컨텍스트", "지능 지수 22.9점", "엔터프라이즈급 추론 및 시스템 설계 역량"]
        drawbacks = ["거대한 모델 크기로 인해 대기열(큐) 발생 시 지연시간 증가"]
        rec = "대용량 프로젝트 파일(1M 컨텍스트)을 통째로 넣고 시스템 전반의 버그나 흐름을 추론할 때"
    elif "nemotron-3.5-lightning" in mid:
        category = "lightweight"
        clean_name = "Nemotron 3.5 Lightning"
        identity = "NVIDIA의 1M 초경량 고속 서빙 모델"
        strengths = ["1M 컨텍스트 지원", "극도로 빠른 생성 속도(토큰 레이턴시 최소화)"]
        drawbacks = ["지능 지수 12.9점으로 단순 쿼리나 요약에 적합"]
        rec = "긴 로그 파일 분석, 단순 텍스트 변환 및 고속 요약 작업"
    elif "nemotron-3-super" in mid:
        category = "general"
        clean_name = "Nemotron 3 Super (120B MoE)"
        identity = "NVIDIA의 120B(12B 활성) 미들급 MoE 모델"
        strengths = ["262K 컨텍스트", "지능 지수 12.8점", "균형 잡힌 리소스 소모"]
        drawbacks = ["코딩 특화 튜닝은 부족"]
        rec = "일반 도메인 문서 작성 및 코드 주석 생성"
    elif "nemotron-3-nano" in mid:
        category = "lightweight"
        clean_name = "Nemotron 3 Nano Omni"
        identity = "NVIDIA 30B 콤팩트 멀티모달 추론 모델"
        strengths = ["낮은 레이턴시", "가벼운 질의응답 최적화"]
        drawbacks = ["지능 점수 10.3점"]
        rec = "간단한 터미널 헬퍼 및 1회성 스크립트 작성"
    elif "inkling-small" in mid or "inkling:free" in mid:
        category = "coding"
        clean_name = "Thinking Machines · Inkling" + (" Small" if "small" in mid else "")
        identity = "Thinking Machines의 100만(1M) 토큰 에이전트 사고 체인(CoT) 모델"
        strengths = ["지능 지수 25.7점 (Small 기준)", "1M 컨텍스트", "생각(Thinking) 토큰을 적극적으로 소모하여 다단계 문제 해결"]
        drawbacks = ["추론 토큰 생성 시간으로 인해 첫 응답(TTFT) 대기 시간 발생"]
        rec = "긴 함수 로직 검증, 에지 케이스 분석 및 복잡한 알고리즘 설계"
    elif "laguna-s" in mid or "laguna-xs" in mid:
        category = "coding"
        clean_name = "Poolside · Laguna " + ("S 2.1" if "laguna-s" in mid else "XS 2.1")
        identity = "Poolside AI의 코딩 전문 파운데이션 모델 (개발자 에이전트 특화)"
        strengths = ["262K 컨텍스트", "Git diff, 터미널 명령, Bash 문법 이해도 최상위", "간결하고 정확한 코드 블록 생성"]
        drawbacks = ["일반 자연어 대화보다는 프로그래밍 태스크에만 전적으로 집중됨"]
        rec = "터미널 코딩 에이전트 백엔드 및 일상 코드 수정/패치 작성"
    elif "gemma-4-31b" in mid:
        category = "general"
        clean_name = "Google · Gemma 4 31B"
        identity = "구글의 최신 31B Dense 오픈 웨이트 모델"
        strengths = ["262K 컨텍스트", "지능 지수 14.7점", "자연어 질의응답과 코딩의 균형"]
        drawbacks = ["대형 MoE 모델 대비 복합 에이전트 능력 다소 제한"]
        rec = "일상적인 프로그래밍 질의, 기술 문서 번역 및 기초 코드 작성"
    elif "gemma-4-26b" in mid:
        category = "reasoning"
        clean_name = "Google · Gemma 4 26B A4B"
        identity = "구글의 26B(4B 활성) MoE 아키텍처 모델"
        strengths = ["지능 지수 16.7점", "262K 컨텍스트", "저비용 고효율 MoE 라우팅"]
        drawbacks = ["매우 복잡한 롱체인 추론 시 토큰 제약"]
        rec = "빠른 유닛 테스트 작성 및 디버깅 힌트 도출"
    elif "north-mini-code" in mid:
        category = "coding"
        clean_name = "Cohere · North Mini Code"
        identity = "Cohere의 256K 코드 인라인 완성 및 함수 생성 특화 모델"
        strengths = ["Cohere 특유의 정확한 도구 호출(Tool use)", "256K 컨텍스트"]
        drawbacks = ["지능 지수 9.9점으로 복잡한 논리 설계보다는 함수 단위 코드에 적합"]
        rec = "API 래퍼 작성, 보일러플레이트 코드 생성 및 문법 교정"
    elif "apodex-1.1-mini" in mid:
        category = "reasoning"
        clean_name = "Apodex 1.1 Mini"
        identity = "Apodex의 복합 리서치 및 장기 예측(Forecasting) 추론 모델"
        strengths = ["262K 컨텍스트", "파일 데이터 및 외부 도구를 조합한 분석력"]
        drawbacks = ["코딩보다는 데이터 분석과 논리 리서치에 더 최적화"]
        rec = "프로젝트 요구사항 분석, 기술 스택 비교 보고서 작성"
    elif "dots-3-note" in mid:
        category = "long_context"
        clean_name = "Dots3-Note Preview"
        identity = "Dots Studio의 512K 초장문 문서 노트 및 컨텍스트 리트리벌 모델"
        strengths = ["512K 컨텍스트", "대규모 문서/코드베이스에서 필요한 단락 정확 검색"]
        drawbacks = ["추론 및 생성 지능 자체는 표준 수준"]
        rec = "수만 줄짜리 레거시 코드베이스 분석 및 아키텍처 다이어그램 추출"
    elif "liquid" in mid:
        category = "lightweight"
        clean_name = "LiquidAI · LFM2.5 2.6B"
        identity = "Liquid AI의 비-트랜스포머 기반 리퀴드 신경망(LFM) 모델"
        strengths = ["경량(2.6B)", "신경망 상태 공간(SSM) 기반의 차세대 구조"]
        drawbacks = ["65K 컨텍스트", "지능 지수 8.4점으로 실험적 성격"]
        rec = "초경량 엣지 환경 테스트 및 리퀴드 신경망 구조 실험"
    elif "minimax-m3.1-flash" in mid:
        category = "general"
        clean_name = "MiniMax · M3.1 Flash"
        aa_name = "MiniMax-M3.1-Flash"
        identity = "MiniMax의 멀티모달(text+image+video) Flash 모델. M3 대비 에이전트·코딩·사이버보안 성능 대폭 개선"
        strengths = ["OpenRouter에서 $0 (:free) 제공",
                     "100만 토큰(1M) 컨텍스트 + 최대 524K 출력 토큰",
                     "reasoning effort max 지원 (강한 사고 체인)",
                     "이미지·비디오 입력 멀티모달"]
        drawbacks = ["OpenRouter 무료 공통 한도(20 RPM · RPD) 적용",
                     "공급자(MiniMax) 정책상 프롬프트는 보관됨 (학습 미사용)"]
        rec = "장문 리포지토리 분석, 에이전트 작업, 멀티모달(이미지) 분석을 $0로 병렬 처리할 때"
    elif "openrouter/free" in mid:
        category = "general"
        clean_name = "OpenRouter Free Auto-Router"
        identity = "요청에 따라 가장 성능이 좋고 대기열이 짧은 무료 모델로 자동 라우팅"
        strengths = ["단일 엔드포인트로 여러 무료 모델 자동 순환", "특정 모델 다운타임 자동 우회"]
        drawbacks = ["요청마다 응답하는 모델이 달라져 일관성이 변할 수 있음"]
        rec = "어떤 모델을 골라야 할지 모르겠을 때 만능 기본 엔드포인트로 사용"
    else:
        continue # skip safety or niche embeddings

    # console-sourced facts appended to every OpenRouter entry
    if or_multimodal and not any("멀티모달" in s for s in strengths):
        strengths.append("멀티모달 입력 지원: " + ", ".join(or_multimodal))
    if or_base:
        relation = {'same': '동일 모델', 'sibling': '동일 계열', 'family': '유사 모델'}.get(
            or_base.get('relation'), '유사 모델')
        drawbacks.append(
            f"무료 종료 후 유료가 {relation} {or_base['id']} 기준 "
            f"${or_base['input']:.2f}/1M (입력) · ${or_base['output']:.2f}/1M (출력)")

    # 공급자 데이터 정책 기반 프라이버시 표기
    ppol = or_provider_policy.get(provider.lower(), {})
    p_train = ppol.get('training')
    p_retains = ppol.get('retainsPrompts')
    p_days = ppol.get('retentionDays')
    if p_train is None:
        privacy = {
            "is_safe": True,
            "label": "🛡️ 보호됨 (표준 API 이용 약관)",
            "detail": "OpenRouter 공식 정책: API 키 호출 시 프롬프트는 제3자 학습에 강제 사용되지 않음 (공식 공급자 정책 준수)"
        }
    elif p_train:
        privacy = {
            "is_safe": False,
            "label": "⚠️ 데이터 학습 가능 (공급사 정책)",
            "detail": f"OpenRouter 공급자 정책: {provider}는 프롬프트를 학습에 사용할 수 있음"
        }
    else:
        if not p_retains:
            ret_txt = "보관 없음 (ZDR)"
        elif p_days:
            ret_txt = f"보관 {p_days}일"
        else:
            ret_txt = "보관 (기간 미공개)"
        privacy = {
            "is_safe": True,
            "label": f"🛡️ 학습 미사용 ({ret_txt})",
            "detail": f"OpenRouter 공급자({provider}) 정책: 학습 미사용 · 프롬프트 {ret_txt}"
        }

    catalog.append({
        "id": f"or/{mid.replace('/', '_').replace(':', '_')}",
        "name": clean_name,
        "model_id": mid,
        "platform": ["OpenRouter"],
        "provider": provider.capitalize(),
        "category": category,
        "context_tokens": or_context,
        "context_window": format_context(or_context) or (f"{int(ctx/1000)}K" if ctx < 1000000 else f"{round(ctx/1000000, 1)}M"),
        "modalities": or_modalities,
        "tool_call": or_model.get('tool_call'),
        "release_date": or_model.get('release_date'),
        "base_model": or_base,
        "intelligence_index": intel_idx,
        "coding_index": coding_idx,
        "aa_name": aa_name,
        "rate_limit": "20 RPM · 50~1,000 RPD (OpenRouter 무료 공통 한도)",
        "privacy": privacy,
        "summary": {
            "one_liner": desc[:180] + "..." if len(desc) > 180 else desc,
            "identity": identity,
            "strengths": strengths,
            "drawbacks": drawbacks,
            "recommended_for": rec
        },
        "links": {
            "model_page": f"https://openrouter.ai/{mid.replace(':free', '')}",
            "docs": "https://openrouter.ai/docs#free-models",
            "benchmark": "https://artificialanalysis.ai" if intel_idx else None
        },
        "cli_usage": f"curl https://openrouter.ai/api/v1/chat/completions -H 'Authorization: Bearer $OPENROUTER_API_KEY' -d '{{\"model\": \"{mid}\"}}'"
    })

# --- SECTION 2: CommandCode.ai Free Models ---
cmd_models = [
    {
        "id": "cmd/ox-alpha",
        "name": "Ox Alpha (GLM-5.3 Flash 기반)",
        "model_id": "stealth/ox-alpha",
        "platform": ["CommandCode"],
        "provider": "CommandCode · Zhipu AI",
        "category": "reasoning",
        "context_tokens": 1000000,
        "context_window": "1M",
        "intelligence_index": 41.8,
        "coding_index": 71.5,
        "aa_name": "GLM-5.3-Flash",
        "rate_limit": "하루 100T 토큰 용량 (프로모션 무료 제공, 5시간 제한 없음)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Zero Retention)",
            "detail": "CommandCode의 $0 프로모션 모델로 사용자 코드 Zero Retention 보장"
        },
        "summary": {
            "one_liner": "커뮤니티 검증 결과 Zhipu GLM-5.3 Flash(지능 41.8점)의 리브랜딩 스텔스 모델로, 1M 컨텍스트와 압도적인 코딩 성능을 무료 제공.",
            "identity": "실체: Zhipu AI의 플래그십 코딩 추론 모델 GLM-5.3-Flash",
            "strengths": ["지능 지수 41.8점으로 Claude 3.5 Sonnet 직하위권", "100만(1M) 토큰 대형 컨텍스트", "CommandCode CLI에서 100T/day의 방대한 한도"],
            "drawbacks": ["스텔스 프리뷰 프로모션이므로 향후 유료화되거나 티어가 변경될 가능성 있음"],
            "recommended_for": "CommandCode 터미널 에이전트에서 복잡한 전체 프로젝트 리팩토링 및 다중 파일 수정 시 강력 추천"
        },
        "links": {
            "model_page": "https://commandcode.ai",
            "docs": "https://commandcode.ai/docs",
            "benchmark": "https://artificialanalysis.ai/models/glm-5-3-flash"
        },
        "cli_usage": "cmd --model stealth/ox-alpha"
    },
    {
        "id": "cmd/space-bunny-alpha",
        "name": "Space Bunny Alpha (Step 3.5 Flash 기반)",
        "model_id": "stealth/space-bunny-alpha",
        "platform": ["CommandCode"],
        "provider": "CommandCode · Tencent/Step",
        "category": "general",
        "context_tokens": 1000000,
        "context_window": "1M",
        "intelligence_index": 17.0,
        "coding_index": 42.0,
        "rate_limit": "모든 요금제(무료 포함)에서 완전 $0.00 제공",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Zero Retention)",
            "detail": "CommandCode 내에서 입력/출력/캐시 모두 $0.00 처리되며 데이터 보관 없음"
        },
        "summary": {
            "one_liner": "StepFun의 Step 3.5 Flash 기반 스텔스 멀티모달 모델. 1M 컨텍스트와 빠른 응답 속도를 자랑하는 데일리 작업용 무료 모델.",
            "identity": "실체: Tencent / StepFun Step 3.5 Flash",
            "strengths": ["1M 컨텍스트 및 멀티모달(이미지+텍스트) 지원", "초고속 TTFT 및 가벼운 인터랙션", "토큰 비용 $0"],
            "drawbacks": ["고난도 알고리즘이나 심층 아키텍처 분석은 Ox Alpha 대비 열세"],
            "recommended_for": "일상적인 버그 탐색, UI/기능 제안 및 빠른 커밋 메시지 생성"
        },
        "links": {
            "model_page": "https://commandcode.ai",
            "docs": "https://commandcode.ai/docs",
            "benchmark": "https://artificialanalysis.ai"
        },
        "cli_usage": "cmd --model stealth/space-bunny-alpha"
    },
    {
        "id": "cmd/glyph-cluster",
        "name": "Glyph Cluster (Stealth Preview)",
        "model_id": "stealth/glyph-cluster:free",
        "platform": ["CommandCode"],
        "provider": "CommandCode Labs",
        "category": "coding",
        "context_tokens": 262144,
        "context_window": "262K",
        "intelligence_index": 35.0,
        "coding_index": 49.5,
        "rate_limit": "계정당 하루 100회 요청 (100 req/day per account)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Stealth Tier)",
            "detail": "CommandCode의 연구용 클러스터 서빙 모델로 Vercel AI Gateway 호환"
        },
        "summary": {
            "one_liner": "Command Code의 독자적인 코딩 리팩토링 특화 추론 클러스터 모델. 하루 100회까지 무료 사용 가능.",
            "identity": "연구용 코딩 에이전트 전용 클러스터 앙상블",
            "strengths": ["터미널 쉘 명령어 및 패치 생성 정확도 우수", "단일 요청당 풍부한 컨텍스트 반영"],
            "drawbacks": ["하루 100회 요청 한도 (초과 시 다른 모델로 전환 필요)"],
            "recommended_for": "CommandCode의 taste-1 학습과 결합하여 개인 코딩 스타일 기반 리팩토링 진행 시"
        },
        "links": {
            "model_page": "https://commandcode.ai",
            "docs": "https://commandcode.ai/docs",
            "benchmark": None
        },
        "cli_usage": "cmd --model stealth/glyph-cluster:free"
    }
]

catalog.extend(cmd_models)

# Also cross-tag Ling 3.1 Flash with CommandCode if available
for m in catalog:
    if "ling-3.1-flash" in m["model_id"]:
        if "CommandCode" not in m["platform"]:
            m["platform"].append("CommandCode")

# --- SECTION 3: OpenCode Zen & Go Free Models ---
opencode_raw_path = 'data/opencode_free_models.json'
if os.path.exists(opencode_raw_path):
    with open(opencode_raw_path, 'r', encoding='utf-8') as f:
        op_list = json.load(f)
    
    for op in op_list:
        mid = op.get('model_id')
        name = op.get('name')
        creator = op.get('creator') or 'OpenCode'
        cat = op.get('catalog') or 'Zen Only'
        platforms = ["OpenCode Zen"]
        if op.get('available_in_go'):
            platforms.append("OpenCode Go")

        is_safe = not op.get('trains_on_data', False)
        trains = op.get('trains_on_data', False)

        # --- console catalog: real limits, modalities, tools, list price ---
        entry = console_entry(mid)
        console_model = entry['model'] if entry else {}
        context_tokens = console_model.get('context_limit') or 128000
        context_window = format_context(context_tokens) or "128K"
        output_limit = console_model.get('output_limit')
        modalities = console_model.get('input_modalities') or []
        tool_call = console_model.get('tool_call')
        release_date = console_model.get('release_date')
        family = console_model.get('family')
        base_model = console_data.base_model_for(mid, CONSOLE_INDEX, GO_ROWS, family, entry['provider'] if entry else None)
        multimodal = [m for m in modalities if m not in ('text',)]

        category = "general"
        if "LongCat" in name: category = "coding"
        elif "Space Bunny" in name: category = "general"
        elif "Muse" in name: category = "reasoning"
        elif "Pickle" in name or "Exo" in name or "Fledge" in name: category = "lightweight"
        
        strengths = []
        drawbacks = []
        identity = ""
        rec = ""
        
        if "Space Bunny" in name:
            identity = "Tencent / StepFun Step 3.5 Flash의 OpenCode 서빙 버전"
            strengths = ["$0 완전 무료", "Zero Retention (학습 미활용 안전)", "빠른 반응 속도"]
            drawbacks = ["Zen 전용 (Go 쿼터에는 별도 미포함)"]
            rec = "OpenCode Zen API를 통해 웹/스크립트에서 무료로 호출할 때 최적"
        elif "LongCat" in name:
            identity = "LongCat 2.0 기반 멀티모달 & 코딩 지원 모델"
            strengths = ["Zen과 Go 양쪽 모두에서 $0 무료", "지능 지수 19.1점, 코딩 지수 45.3점", "Zero Retention 보안 안심"]
            drawbacks = ["20B급 모델로 초고난도 아키텍처 설계에는 한계"]
            rec = "OpenCode Go 구독자 및 Zen 사용자 모두에게 가장 안전하고 실용적인 데일리 무료 코딩 모델"
        elif "Muse Spark" in name:
            identity = "초저가/무료 제공 대가로 데이터 피드백을 수집하는 기여자(Contributor) 모델"
            strengths = ["지능 지수 20.5점 (1.3 버전)", "수학 및 코드 해결 능력 우수"]
            drawbacks = ["⚠️ 사용자 프롬프트 및 완성 데이터가 모델 개선 학습에 수집됨"]
            rec = "사내 기밀이 아닌 공개 오픈소스 코드나 개인 학습용 문제 풀이에 한해 활용 추천"
        elif "Big Pickle" in name:
            identity = "OpenCode의 스텔스 테스트베드 모델"
            strengths = ["새로운 추론 기법 사전 체험 가능", "완전 $0"]
            drawbacks = ["⚠️ 무료 기간 중 수집 데이터가 모델 개선에 활용됨", "스펙 미공개"]
            rec = "실험적인 새로운 모델 테스트"
        elif "MiniMax M3.1 Flash" in name:
            identity = "MiniMax의 멀티모달 Flash 모델을 OpenCode Zen/Go에서 $0으로 제공"
            strengths = ["Zen & Go 양쪽 모두에서 $0 무료", "지능 지수 42.4점 (무료 모델 중 상위권)",
                         "Zero Retention · 학습 미사용 (Go Privacy 표: Not used / 0 days)",
                         "M3 대비 에이전트·코딩·사이버보안 성능 개선"]
            drawbacks = ["벤치마크 코딩 지수 미공개", "Go 5시간 롤링 요청 한도 적용"]
            rec = "사내 기밀성보다 처리량과 비용이 중요한 대규모 에이전트/코딩 작업"
        else:
            identity = f"OpenCode {cat} 무료 서비스 모델"
            strengths = ["$0 무료", "OpenCode 콘솔에서 즉시 활성화"]
            drawbacks = ["데이터 학습 정책 확인 필요" if trains else "벤치마크 점수 미공개"]
            rec = "OpenCode 무료 엔드포인트 연동 테스트"
        
        # console-sourced facts appended to every free model
        if multimodal and not any("멀티모달" in s for s in strengths):
            strengths.append("멀티모달 입력 지원: " + ", ".join(multimodal))
        if output_limit:
            strengths.append(f"최대 출력 {format_context(output_limit)} 토큰")
        if base_model:
            relation = {'same': '동일 모델', 'sibling': '동일 계열', 'family': '유사 모델'}.get(
                base_model.get('relation'), '유사 모델')
            label = "무료 종료 후 유료가"
            drawbacks.append(
                f"{label} {relation} {base_model['id']} 기준 "
                f"${base_model['input']:.2f}/1M (입력) · ${base_model['output']:.2f}/1M (출력)")

        catalog.append({
            "id": f"opencode/{mid}",
            "name": name,
            "model_id": mid,
            "platform": platforms,
            "provider": creator,
            "category": category,
            "context_tokens": context_tokens,
            "context_window": context_window,
            "output_limit": output_limit,
            "modalities": modalities,
            "tool_call": tool_call,
            "release_date": release_date,
            "base_model": base_model,
            "intelligence_index": op.get('index'),
            "coding_index": op.get('coding'),
            "aa_name": op.get('aa_name'),
            "rate_limit": "OpenCode Zen / Go 표준 롤링 정책 ($0 무과금)",
            "privacy": {
                "is_safe": is_safe,
                "label": "🛡️ 보호됨 (학습 미사용)" if is_safe else "⚠️ 데이터 학습 활용 (피드백 수집)",
                "detail": op.get('privacy_note') or ("Zero retention" if is_safe else "Collected data may be used to improve model")
            },
            "summary": {
                "one_liner": f"OpenCode {cat}에서 $0(Free)로 제공되는 {creator}의 공식 지원 모델.",
                "identity": identity,
                "strengths": strengths,
                "drawbacks": drawbacks,
                "recommended_for": rec
            },
            "links": {
                "model_page": "https://opencode.ai/v2/docs/console/models/",
                "docs": "https://opencode.ai/v2/docs/console/go/" if op.get('available_in_go') else "https://opencode.ai/v2/docs/console/models/",
                "benchmark": "https://artificialanalysis.ai" if op.get('index') else None
            },
            "cli_usage": f"opencode run --model {mid}"
        })

# --- SECTION 4: Standout Free API Models from awesome-free-llm-apis ---
awesome_models = [
    {
        "id": "groq/llama-3.3-70b-versatile",
        "name": "Groq · Llama 3.3 70B Versatile",
        "model_id": "llama-3.3-70b-versatile",
        "platform": ["Groq"],
        "provider": "Groq / Meta",
        "category": "coding",
        "context_tokens": 131072,
        "context_window": "131K",
        "intelligence_index": 32.0,
        "coding_index": 52.0,
        "rate_limit": "30 RPM · 14,400 RPD (신용카드 불필요, 1분 가입 무료)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Zero Retention)",
            "detail": "Groq API는 프롬프트를 보관하거나 모델 학습에 사용하지 않음 (표준 DPA)"
        },
        "summary": {
            "one_liner": "Groq의 LPU 하드웨어 가속으로 초당 300+ 토큰의 초광속 출력을 제공하는 Llama 3.3 70B.",
            "identity": "Meta Llama 3.3 70B Instruct + Groq LPU 초고속 서빙",
            "strengths": ["극도로 빠른 생성 속도 (인터랙티브 코딩/채팅 최상위)", "하루 14,400회 요청의 관대한 일일 한도", "신용카드 등록 없이 이메일만으로 1분 발급"],
            "drawbacks": ["131K 컨텍스트로 1M 초장문 파일 분석에는 제약"],
            "recommended_for": "Cursor, Claude Code, Aider 등 실시간 반응 속도가 생명인 코딩 툴에 적극 추천"
        },
        "links": {
            "model_page": "https://console.groq.com",
            "docs": "https://console.groq.com/docs/models",
            "benchmark": "https://artificialanalysis.ai/models/llama-3-3-70b-instruct"
        },
        "cli_usage": "export OPENAI_BASE_URL=\"https://api.groq.com/openai/v1\" && export OPENAI_API_KEY=\"gsk_...\""
    },
    {
        "id": "google/gemini-2.5-flash",
        "name": "Google · Gemini 2.5 Flash",
        "model_id": "gemini-2.5-flash",
        "platform": ["Google Gemini"],
        "provider": "Google",
        "category": "long_context",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": 38.5,
        "coding_index": 65.0,
        "rate_limit": "15 RPM · 1,500 RPD (Google AI Studio 무료 키, 카드 불필요)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (AI Studio 기본 약관)",
            "detail": "Google AI Studio 무료 API 키: 엔드포인트 호출 시 표준 약관 준수"
        },
        "summary": {
            "one_liner": "구글의 100만(1M) 토큰 멀티모달 플래그십 경량 모델. 코드베이스 전체 주입 및 네이티브 도구 호출 최적화.",
            "identity": "Google DeepMind 차세대 Flash 아키텍처",
            "strengths": ["100만(1M) 토큰 초대형 컨텍스트", "코딩 벤치마크 65.0점 및 강력한 멀티모달(비디오/PDF) 이해", "하루 1,500회 무료 호출"],
            "drawbacks": ["무료 티어 분당 15회 요청 한도 (동시 다발적 에이전트 호출 시 조절 필요)"],
            "recommended_for": "수만 줄 단위의 대형 리포지토리 전체 분석, 방대한 API 스펙 문서 기반 코드 작성"
        },
        "links": {
            "model_page": "https://aistudio.google.com",
            "docs": "https://ai.google.dev/gemini-api/docs",
            "benchmark": "https://artificialanalysis.ai"
        },
        "cli_usage": "curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY"
    },
    {
        "id": "cerebras/llama-3.1-70b",
        "name": "Cerebras · Llama 3.1 70B",
        "model_id": "llama3.1-70b",
        "platform": ["Cerebras"],
        "provider": "Cerebras / Meta",
        "category": "lightweight",
        "context_tokens": 131072,
        "context_window": "131K",
        "intelligence_index": 28.5,
        "coding_index": 48.0,
        "rate_limit": "10 RPM · 100 RPD (초당 1,500+ 토큰 세계 최고속)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise Grade)",
            "detail": "Cerebras 추론 클라우드 표준 보안 준수"
        },
        "summary": {
            "one_liner": "웨이퍼 스케일 엔진(WSE)으로 구동되는 세계에서 가장 빠른 LLM API (초당 1,500~2,000 토큰).",
            "identity": "Meta Llama 3.1 70B + Cerebras 웨이퍼 하드웨어",
            "strengths": ["체감상 기다림이 전혀 없는 즉각적인 텍스트 렌더링", "신용카드 불필요"],
            "drawbacks": ["일일 100회 요청 한도로 일상 대량 작업에는 한계"],
            "recommended_for": "실시간 자동완성(Auto-complete), 즉답이 필요한 터미널 질의응답"
        },
        "links": {
            "model_page": "https://cloud.cerebras.ai",
            "docs": "https://inference-docs.cerebras.ai",
            "benchmark": "https://artificialanalysis.ai"
        },
        "cli_usage": "export OPENAI_BASE_URL=\"https://api.cerebras.ai/v1\" && export OPENAI_API_KEY=\"csk-...\""
    },
    {
        "id": "cohere/command-a-plus",
        "name": "Cohere · Command A+ (218B)",
        "model_id": "command-a-218b",
        "platform": ["Cohere"],
        "provider": "Cohere",
        "category": "reasoning",
        "context_tokens": 131072,
        "context_window": "128K",
        "intelligence_index": 34.0,
        "coding_index": 48.0,
        "rate_limit": "20 RPM (신용카드 불필요 무료 체험 키)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (엔터프라이즈 기준)",
            "detail": "Cohere Trial API 키: 상업적 학습 미사용 보장"
        },
        "summary": {
            "one_liner": "Cohere의 218B 플래그십 엔터프라이즈 모델. 복합 검색 증강 생성(RAG)과 엄격한 도구 호출(Tool use)에 강점.",
            "identity": "Cohere Command 플래그십 아키텍처",
            "strengths": ["엄격한 JSON 스키마 및 정확한 툴 파라미터 매핑", "신용카드 없이 계정 생성 가능"],
            "drawbacks": ["20 RPM 분당 요청 제한"],
            "recommended_for": "다단계 API 툴 체이닝, 구조화된 JSON 데이터 추출 및 엔터프라이즈 RAG"
        },
        "links": {
            "model_page": "https://dashboard.cohere.com",
            "docs": "https://docs.cohere.com",
            "benchmark": "https://artificialanalysis.ai"
        },
        "cli_usage": "export CO_API_KEY=\"...\""
    },
    {
        "id": "nvidia-nim/glm-5.3",
        "name": "NVIDIA NIM · GLM-5.3",
        "model_id": "z-ai/glm-5.3",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · Zhipu AI",
        "category": "reasoning",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": 44.8,
        "coding_index": 74.8,
        "aa_name": ["GLM-5.3 (Max)", "GLM-5.3 (Low)"],
        "rate_limit": "NVIDIA NIM 무료 체험 크레딧 (전화 인증 필요)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "Z.ai의 753B MoE 플래그십(40B 활성). GLM-5.2와 동일 베이스의 후속 post-training으로 Terminal-Bench 3.0 오픈 웨이트 SOTA.",
            "identity": "Z.ai GLM-5.3 + NVIDIA NIM 가속 엔진 (NVFP4, 1M 컨텍스트)",
            "strengths": ["100만 토큰 컨텍스트", "저장소 규모 코드 생성·리팩토링 및 장기 에이전트 특화", "함수/도구 호출 및 추론 지원"],
            "drawbacks": ["전화번호 인증 필요", "체험 크레딧 소진 시 유료", "사이버 역량 관련 가드레일 필요"],
            "recommended_for": "대형 리포지토리 통째 분석 및 장기 터미널 에이전트 작업"
        },
        "links": {
            "model_page": "https://build.nvidia.com/z-ai/glm-5-3",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": None
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY' -d '{\"model\": \"z-ai/glm-5.3\"}'"
    },
    {
        "id": "nvidia-nim/deepseek-v4.1-flash",
        "name": "NVIDIA NIM · DeepSeek V4.1 Flash",
        "model_id": "deepseek-ai/deepseek-v4.1-flash",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · DeepSeek",
        "category": "reasoning",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": None,
        "coding_index": None,
        "rate_limit": "NVIDIA NIM 무료 체험 크레딧 (전화 인증 필요)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "DeepSeek의 552B MoE 멀티모달 추론 모델(8B 활성). 1M 컨텍스트와 조절 가능한 reasoning effort.",
            "identity": "DeepSeek-AI DeepSeek-V4.1-Flash + NVIDIA NIM",
            "strengths": ["100만 토큰 컨텍스트", "Terminal-Bench 2.1 90.6점(벤더 발표)", "텍스트+이미지 입력, 도구 호출 지원"],
            "drawbacks": ["전화번호 인증 필요", "체험 크레딧 소진 시 유료", "벤치마크는 벤더 발표치"],
            "recommended_for": "장문서·코드베이스横断 추론 및 도구 활용 에이전트"
        },
        "links": {
            "model_page": "https://build.nvidia.com/deepseek-ai/deepseek-v4.1-flash",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": None
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY' -d '{\"model\": \"deepseek-ai/deepseek-v4.1-flash\"}'"
    },
    {
        "id": "nvidia-nim/kimi-k3",
        "name": "NVIDIA NIM · Kimi K3",
        "model_id": "moonshotai/kimi-k3",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · Moonshot AI",
        "category": "coding",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": None,
        "coding_index": None,
        "rate_limit": "NVIDIA NIM 무료 체험 크레딧 (전화 인증 필요)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "Moonshot AI의 2.8T MoE 네이티브 멀티모달 에이전트 모델(104B 활성). 장기 코딩·지식 작업 특화.",
            "identity": "Moonshot AI Kimi-K3 + NVIDIA NIM (1M 컨텍스트)",
            "strengths": ["100만 토큰 컨텍스트", "장기 소프트웨어 엔지니어링 및 멀티모달 문서 이해", "함수/도구 호출 지원"],
            "drawbacks": ["전화번호 인증 필요", "체험 크레딧 소진 시 유료", "멀티턴·툴콜 시 reasoning_content 전체 반환 필요"],
            "recommended_for": "장기 코딩 에이전트 및 멀티모달 문서 기반 작업"
        },
        "links": {
            "model_page": "https://build.nvidia.com/moonshotai/kimi-k3",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": None
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY' -d '{\"model\": \"moonshotai/kimi-k3\"}'"
    },
    {
        "id": "nvidia-nim/gpt-oss-20b",
        "name": "NVIDIA NIM · GPT-OSS 20B",
        "model_id": "openai/gpt-oss-20b",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · OpenAI",
        "category": "lightweight",
        "context_tokens": 131072,
        "context_window": "131K",
        "intelligence_index": None,
        "coding_index": None,
        "rate_limit": "NVIDIA NIM 무료 체험 크레딧 (전화 인증 필요)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "OpenAI의 21B MoE 오픈 웨이트 추론 모델(3.6B 활성). 저지연·온프레미스 배포에 적합.",
            "identity": "OpenAI gpt-oss-20b + NVIDIA NIM (Apache 2.0)",
            "strengths": ["조절 가능한 reasoning effort", "함수 호출·구조화 출력·CoT 지원", "관대한 Apache 2.0 라이선스"],
            "drawbacks": ["전화번호 인증 필요", "131K 컨텍스트로 초대형 파일 분석에는 제약"],
            "recommended_for": "가벼운 추론·수리 작업 및 프라이빗 배포 테스트"
        },
        "links": {
            "model_page": "https://build.nvidia.com/openai/gpt-oss-20b",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": None
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY' -d '{\"model\": \"openai/gpt-oss-20b\"}'"
    },
    {
        "id": "nvidia-nim/glm-5.2",
        "name": "NVIDIA NIM · GLM-5.2",
        "model_id": "z-ai/glm-5.2",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · Zhipu AI",
        "category": "reasoning",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": 33.7,
        "coding_index": 68.8,
        "aa_name": ["GLM-5.2 (Max)", "GLM-5.2 (Reasoning)", "GLM-5.2 (Non-reasoning)"],
        "rate_limit": "최대 40 RPM (NVIDIA NIM 무료 개발자 크레딧 티어)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "NVIDIA NIM에서 서빙되는 GLM-5.2. 1M 컨텍스트의 안정화된 이전 세대 플래그십 추론 모델.",
            "identity": "Zhipu AI GLM-5.2 + NVIDIA NIM 가속 엔진",
            "strengths": ["100만 토큰 대규모 컨텍스트", "분당 40회(40 RPM)의 쾌적한 처리 속도", "GLM-5.3 대비 검증된 안정성"],
            "drawbacks": ["전화번호 인증 필요", "최신 5.3 대비 지능 소폭 낮음"],
            "recommended_for": "GLM-5.3 Flash의 RPM 한도 초과 시 대체 백업 모델"
        },
        "links": {
            "model_page": "https://build.nvidia.com/z-ai/glm-5-2",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": "https://artificialanalysis.ai"
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY' -d '{\"model\": \"z-ai/glm-5.2\"}'"
    },
    {
        "id": "nvidia-nim/glm-5.1",
        "name": "NVIDIA NIM · GLM-5.1",
        "model_id": "z-ai/glm-5.1",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · Zhipu AI",
        "category": "reasoning",
        "context_tokens": 202752,
        "context_window": "202K",
        "intelligence_index": 26.1,
        "coding_index": 55.8,
        "aa_name": ["GLM-5.1 (Reasoning)", "GLM-5.1 (Non-reasoning)"],
        "rate_limit": "최대 40 RPM (NVIDIA NIM 무료 개발자 크레딧 티어)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "NVIDIA NIM의 GLM-5.1. 202K 컨텍스트의 경량·고속 추론 모델.",
            "identity": "Zhipu AI GLM-5.1 + NVIDIA NIM 가속 엔진",
            "strengths": ["분당 40회(40 RPM) 처리", "가벼운 일상 코딩·요약 작업에 적합"],
            "drawbacks": ["전화번호 인증 필요", "202K 컨텍스트로 초대형 파일 분석에는 제약"],
            "recommended_for": "빠른 일상 질의응답 및 경량 코드 생성용 서브 모델"
        },
        "links": {
            "model_page": "https://build.nvidia.com/z-ai/glm-5-1",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": "https://artificialanalysis.ai"
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY' -d '{\"model\": \"z-ai/glm-5.1\"}'"
    },
    {
        "id": "nvidia-nim/glm-5.3-flash",
        "name": "NVIDIA NIM · GLM-5.3 Flash",
        "model_id": "z-ai/glm-5.3-flash",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · Zhipu AI",
        "category": "reasoning",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": 41.8,
        "coding_index": 71.5,
        "aa_name": "GLM-5.3-Flash",
        "rate_limit": "최대 40 RPM (NVIDIA NIM 무료 개발자 크레딧 티어)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "NVIDIA NIM 인프라에서 서빙되는 1M 컨텍스트의 최신 GLM-5.3 Flash. 최대 40 RPM의 높은 분당 처리량.",
            "identity": "Zhipu AI GLM-5.3-Flash + NVIDIA NIM 가속 엔진",
            "strengths": ["지능 지수 41.8점 및 100만 토큰 대규모 컨텍스트", "분당 40회(40 RPM)의 쾌적한 처리 속도"],
            "drawbacks": ["전화번호 인증 필요"],
            "recommended_for": "엔터프라이즈급 안정성이 요구되는 팀 협업 개발 및 대규모 추론 테스트"
        },
        "links": {
            "model_page": "https://build.nvidia.com/settings/api-keys",
            "docs": "https://docs.api.nvidia.com",
            "benchmark": "https://artificialanalysis.ai/models/glm-5-3-flash"
        },
        "cli_usage": "curl https://integrate.api.nvidia.com/v1/chat/completions -H 'Authorization: Bearer $NVIDIA_API_KEY'"
    }
]

catalog.extend(awesome_models)

# --- AA benchmark sync (fresh scores from the update_data.py pipeline) ---
# Hardcoded NIM/stealth scores rot as Artificial Analysis re-benchmarks
# (e.g. GLM-5.3-Flash 39.8/53.0 -> 41.8/71.5). Entries carrying `aa_name`
# get their (index, coding) re-resolved here from data/models.json, which
# update_data.py refreshes earlier in update.sh. Literals above remain
# as offline fallback. Score-dependent prose is refreshed too so text
# can't contradict the numbers.
AA_BY_NAME = {}
for _aa_src in ('data/models.json', 'data/opencode_go_complete.json'):
    try:
        with open(_aa_src, 'r', encoding='utf-8') as _f:
            _aa_raw = json.load(_f)
        _aa_list = _aa_raw.get('models', _aa_raw) if isinstance(_aa_raw, dict) else _aa_raw
        for _m in _aa_list:
            _n = _m.get('name') or _m.get('aa_name')
            if _n and (_n not in AA_BY_NAME or _m.get('index') is not None):
                AA_BY_NAME[_n] = _m
    except Exception:
        pass

def _aa_lookup(*names):
    cands = [AA_BY_NAME[n] for n in names
             if n in AA_BY_NAME and AA_BY_NAME[n].get('index') is not None]
    if not cands:
        return None
    cands.sort(key=lambda m: (m.get('index') or 0), reverse=True)
    best = cands[0]
    return best.get('index'), best.get('coding'), best.get('url')

for _m in catalog:
    _aa_names = _m.get('aa_name')
    if not _aa_names:
        continue
    if isinstance(_aa_names, str):
        _aa_names = [_aa_names]
    _hit = _aa_lookup(*_aa_names)
    if not _hit:
        continue
    _idx, _cod, _url = _hit
    _m['intelligence_index'] = _idx
    _m['coding_index'] = _cod
    if _url:
        _m['links']['benchmark'] = _url
    _s = _m.get('summary') or {}
    if _s.get('one_liner'):
        _s['one_liner'] = re.sub(r'\(지능 [\d.]+점\)', f'(지능 {_idx:.1f}점)', _s['one_liner'])
    _s['strengths'] = [re.sub(r'지능 지수 [\d.]+점', f'지능 지수 {_idx:.1f}점', _st)
                       for _st in (_s.get('strengths') or [])]
print(f"AA benchmark sync: resolved {sum(1 for m in catalog if m.get('aa_name'))} pinned entries against {len(AA_BY_NAME)} AA models")

# Final cross-platform pass: models served on BOTH OpenRouter/OpenCode and
# NVIDIA NIM (verified against https://build.nvidia.com/models).
# NIM keeps its own model IDs (nvidia/... or z-ai/...), so store nim_model_id
# separately instead of overwriting the primary model_id/cli_usage.
NIM_DUAL_TAG = {
    "nemotron-3-ultra": ("nvidia/nemotron-3-ultra-550b-a55b", "https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b"),
    "nemotron-3.5-lightning": ("nvidia/nemotron-3.5-lightning-30b-a3b", "https://build.nvidia.com/nvidia/nemotron-3-5-lightning-30b-a3b"),
    "nemotron-3-super": ("nvidia/nemotron-3-super-120b-a12b", "https://build.nvidia.com/nvidia/nemotron-3-super-120b-a12b"),
    "nemotron-3-nano": ("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"),
    "gemma-4-31b": ("google/gemma-4-31b-it", "https://build.nvidia.com/google/gemma-4-31b-it"),
    "laguna-xs": ("poolside/laguna-xs-2.1", "https://build.nvidia.com/poolside/laguna-xs-2-1"),
}
for m in catalog:
    mid_low = (m.get("model_id") or "").lower()
    for key, (nim_id, nim_page) in NIM_DUAL_TAG.items():
        if key in mid_low and "nvidia-nim/" not in (m.get("id") or ""):
            if "NVIDIA NIM" not in m["platform"]:
                m["platform"].append("NVIDIA NIM")
            m.setdefault("nim_model_id", nim_id)
            m["links"].setdefault("nim_model_page", nim_page)
            tag_note = f" OpenRouter/OpenCode와 NVIDIA NIM({nim_id}) 양쪽에서 무료 호출 가능."
            if tag_note not in (m["summary"].get("one_liner") or ""):
                m["summary"]["one_liner"] = (m["summary"]["one_liner"] or "") + tag_note
            break

print(f"Total Unified Free Models Catalog: {len(catalog)} entries")

# Sort catalog by intelligence_index desc (nulls last)
catalog.sort(key=lambda x: (x['intelligence_index'] is not None, x['intelligence_index'] or 0), reverse=True)

# Write to JSON and JS
with open('data/free_models_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

with open('data/free_models_catalog.js', 'w', encoding='utf-8') as f:
    f.write('window.__FREE_MODELS_CATALOG__ = ' + json.dumps(catalog, ensure_ascii=False, indent=2) + ';\n')

print("Successfully written data/free_models_catalog.json and data/free_models_catalog.js!")
