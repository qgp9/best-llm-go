import json
import os

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
    elif "openrouter/free" in mid:
        category = "general"
        clean_name = "OpenRouter Free Auto-Router"
        identity = "요청에 따라 가장 성능이 좋고 대기열이 짧은 무료 모델로 자동 라우팅"
        strengths = ["단일 엔드포인트로 여러 무료 모델 자동 순환", "특정 모델 다운타임 자동 우회"]
        drawbacks = ["요청마다 응답하는 모델이 달라져 일관성이 변할 수 있음"]
        rec = "어떤 모델을 골라야 할지 모르겠을 때 만능 기본 엔드포인트로 사용"
    else:
        continue # skip safety or niche embeddings

    catalog.append({
        "id": f"or/{mid.replace('/', '_').replace(':', '_')}",
        "name": clean_name,
        "model_id": mid,
        "platform": ["OpenRouter"],
        "provider": provider.capitalize(),
        "category": category,
        "context_tokens": ctx,
        "context_window": f"{int(ctx/1000)}K" if ctx < 1000000 else f"{round(ctx/1000000, 1)}M",
        "intelligence_index": intel_idx,
        "coding_index": coding_idx,
        "rate_limit": "20 RPM · 50~1,000 RPD (OpenRouter 무료 공통 한도)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (표준 API 이용 약관)",
            "detail": "OpenRouter 공식 정책: API 키 호출 시 프롬프트는 제3자 학습에 강제 사용되지 않음 (공식 공급자 정책 준수)"
        },
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
        "intelligence_index": 39.8,
        "coding_index": 53.0,
        "rate_limit": "하루 100T 토큰 용량 (프로모션 무료 제공, 5시간 제한 없음)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Zero Retention)",
            "detail": "CommandCode의 $0 프로모션 모델로 사용자 코드 Zero Retention 보장"
        },
        "summary": {
            "one_liner": "커뮤니티 검증 결과 Zhipu GLM-5.3 Flash(지능 39.8점)의 리브랜딩 스텔스 모델로, 1M 컨텍스트와 압도적인 코딩 성능을 무료 제공.",
            "identity": "실체: Zhipu AI의 플래그십 코딩 추론 모델 GLM-5.3-Flash",
            "strengths": ["지능 지수 39.8점으로 Claude 3.5 Sonnet 직하위권", "100만(1M) 토큰 대형 컨텍스트", "CommandCode CLI에서 100T/day의 방대한 한도"],
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
        else:
            identity = f"OpenCode {cat} 무료 서비스 모델"
            strengths = ["$0 무료", "OpenCode 콘솔에서 즉시 활성화"]
            drawbacks = ["데이터 학습 정책 확인 필요" if trains else "벤치마크 점수 미공개"]
            rec = "OpenCode 무료 엔드포인트 연동 테스트"
        
        catalog.append({
            "id": f"opencode/{mid}",
            "name": name,
            "model_id": mid,
            "platform": platforms,
            "provider": creator,
            "category": category,
            "context_tokens": 128000,
            "context_window": "128K",
            "intelligence_index": op.get('index'),
            "coding_index": op.get('coding'),
            "rate_limit": "OpenCode Zen / Go 표준 롤링 정책 ($0 무과금)",
            "privacy": {
                "is_safe": is_safe,
                "label": "🛡️ 보호됨 (학습 미사용 · ZDR)" if is_safe else "⚠️ 데이터 학습 활용 (피드백 수집)",
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
        "id": "nvidia-nim/glm-5.3-flash",
        "name": "NVIDIA NIM · GLM-5.3 Flash",
        "model_id": "z-ai/glm-5.3-flash",
        "platform": ["NVIDIA NIM"],
        "provider": "NVIDIA · Zhipu AI",
        "category": "reasoning",
        "context_tokens": 1048576,
        "context_window": "1M",
        "intelligence_index": 39.8,
        "coding_index": 53.0,
        "rate_limit": "최대 40 RPM (NVIDIA NIM 무료 개발자 크레딧 티어)",
        "privacy": {
            "is_safe": True,
            "label": "🛡️ 보호됨 (Enterprise NIM)",
            "detail": "NVIDIA 엔터프라이즈 클라우드 표준 보안"
        },
        "summary": {
            "one_liner": "NVIDIA NIM 인프라에서 서빙되는 1M 컨텍스트의 최신 GLM-5.3 Flash. 최대 40 RPM의 높은 분당 처리량.",
            "identity": "Zhipu AI GLM-5.3-Flash + NVIDIA NIM 가속 엔진",
            "strengths": ["지능 지수 39.8점 및 100만 토큰 대규모 컨텍스트", "분당 40회(40 RPM)의 쾌적한 처리 속도"],
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

print(f"Total Unified Free Models Catalog: {len(catalog)} entries")

# Sort catalog by intelligence_index desc (nulls last)
catalog.sort(key=lambda x: (x['intelligence_index'] is not None, x['intelligence_index'] or 0), reverse=True)

# Write to JSON and JS
with open('data/free_models_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

with open('data/free_models_catalog.js', 'w', encoding='utf-8') as f:
    f.write('window.__FREE_MODELS_CATALOG__ = ' + json.dumps(catalog, ensure_ascii=False, indent=2) + ';\n')

print("Successfully written data/free_models_catalog.json and data/free_models_catalog.js!")
