/**
 * data/i18n.js
 * Internationalization (EN / KO) & Theme (Light / Dark) manager
 * Default Language: English ('en')
 * Supports URL param '?lang=en' / '?lang=ko' and localStorage persistence.
 */

(function () {
  const DICT = {
    en: {
      // Banner
      banner_notice_tag: "⚠️ Personal Reference Only",
      banner_notice_text: "Unofficial sandbox for personal research. Data is scraped from public APIs; prices, quotas & limits may differ from production.",
      banner_vibe_tag: "🤖 100% Vibe-Coded with AI",
      banner_credit_text: "Look & Feel adapted from",
      banner_credit_author: "Terry Djony's project",

      // Header
      h1_title: "OpenCode Go Value Frontier",
      badge_go: "Official Go Catalog",
      hdr_sub: "Pareto frontier value analyzer combining <b>opencode.ai/go</b> official models ($15/$30/$60 monthly allowances), <b>models.dev</b> API costs, and <b>Artificial Analysis</b> Intelligence Index. Applying effective value multipliers (<b>x6.0</b> vs <b>x3.0</b> vs <b>x1.5</b>) under the $10/mo plan to highlight true value champions.",
      meta_loading: "Loading data…",
      meta_loaded: "{goCount} OpenCode Go models loaded ({totalCount} market models) · Sources: opencode.ai + models.dev + artificialanalysis.ai<br><span style='display:inline-flex;align-items:center;gap:6px;margin-top:4px;color:var(--accent-ink);font-weight:600;'>🕒 Last updated: {lastUpdated} · Automatically synced every 24 hours (~12:00 PM Finland time)</span>",
      free_last_updated: "🕒 Last updated: <b>{lastUpdated}</b> · Automatically updated every 24 hours (~12:00 PM Finland time)",

      // Free models page navigation & hero
      nav_free_hub_badge: "Free Models Hub",
      nav_link_frontier: "📊 OpenCode Go Value Frontier",
      nav_link_free: "🎁 Free AI Models Guide",
      hero_free_h1: "🎁 Free AI Models Comprehensive Guide & Benchmarks",
      hero_free_desc: "A centralized directory of $0 token cost models across OpenCode (Zen & Go), OpenRouter, CommandCode, Groq, and Google Gemini. Transparently compare their true identities, official benchmark intelligence indices, context limits, and privacy policies.",
      hero_free_credits_label: "⭐ Data References:",

      // Buttons
      btn_free_models: "🎁 Free AI Models Guide",
      btn_update_help: "🔄 Update Data",
      btn_save_preset: "Save Preset",
      btn_copy_link: "Copy Link",
      btn_mode_all: "Show All Models",
      btn_mode_custom: "Compare My Selection Only",
      btn_open_sections: "Open Provider Sections",
      btn_select_all: "Select All",
      btn_clear_all: "Deselect All",

      // Filters
      cost_go_effective: "🚀 Go Effective $/1M",
      cost_go_task: "🎯 Go /task",
      cost_task: "🎯 Raw /task",
      cost_go_quota: "📊 Quota Burn %",
      cost_blended: "💵 Raw API $/1M",
      scope_go_only: "OpenCode Go Models",
      scope_all: "All Market Models",

      mode_indicator_effective: "⚡ Basis: <b>OpenCode Go Effective Cost</b> ($10/mo subscription leverage)",
      mode_indicator_go_task: "🎯 Basis: <b>Go Cost per Task</b> (Effective task cost with reasoning tokens & Go multiplier)",
      mode_indicator_task: "🎯 Basis: <b>Official Cost per Task</b> (Raw API cost per completed AA task)",
      mode_indicator_quota: "📊 Basis: <b>Monthly Quota Burn %</b> (Quota consumed per 1M tokens)",
      mode_indicator_blended: "💵 Basis: <b>Official Raw API Price</b> (Unadjusted market rate)",

      lbl_min_idx: "Min Intelligence",
      lbl_collapse: "1 row per model",
      lbl_maker: "Maker",
      opt_all_makers: "All Makers",
      ph_search: "Search model…",
      lbl_frontier_only: "Frontier only",
      lbl_labels_all: "Show all labels",
      lbl_presets: "💾 Presets:",
      lbl_selection_mode: "🎯 Selection Mode:",
      lbl_privacy_policy: "🛡️ Data Privacy & Training Policy:",
      lbl_no_train: "Safe / No Training",
      lbl_train: "Model Training: Yes (Contributor)",
      lbl_privacy_hint: "※ Contributor models are disabled by default. Checking recalculates the <b>Frontier Edge</b> in real time.",
      drawer_help_text: "Click any Provider header to <b>toggle the entire group</b> on/off, or click individual chips to customize.",
      ph_drawer_search: "Filter models in section…",
      selected_count_label: "{n} selected",

      // Scatter Chart
      scatter_title: "Intelligence Index vs {costTitle}: {metric}",
      scatter_cap: "{costCap} The orange line on top is the <b>Frontier Edge</b>, representing Pareto-optimal models with highest capability per cost.",
      leg_frontier: "Value Frontier (Pareto Optimal)",
      leg_dominated: "Dominated (Cheaper model is smarter)",
      leg_edge: "Frontier Edge",
      leg_tier60: "$60 Tier (x6.0)",
      leg_tier30: "$30 Tier (x3.0)",
      leg_tier15: "$15 Tier (x1.5)",
      leg_training: "Training: Yes",

      // Strategy Guide
      guide_hdr: "OpenCode Go Strategy & Model Selection Guide",
      guide_cap: "Optimal model operation strategy under the official $10/mo OpenCode Go subscription:",
      guide_box1_h: "1. Daily Coding Driver: $60/mo Tier (x6.0 Multiplier)",
      guide_box1_p: "<b>GLM-5.3-Flash</b> (Score 41.8) costs just <b>$0.040</b> per 1M effective tokens with a generous 6,320 requests / 5h limit. For ultra-cheap high volume, <b>MiMo-V2.6-Flash</b> (Score 37.9, $0.029, 30,100 req/5h) is unbeatable.",
      guide_box2_h: "2. The $15/mo Tier Trap (GPT-6 Luna Eliminated)",
      guide_box2_p: "While <b>GPT 6 Luna</b> looks cheap at $0.20 raw, on Go it is capped at $15 (x1.5 multiplier), raising effective cost to <b>$0.133</b>. It is thoroughly outclassed by <b>GLM-5.3-Flash</b> ($0.040, score 41.8) and drops off the frontier.",
      guide_box3_h: "3. Heavy Reasoning & Agentic Tasks",
      guide_box3_p: "For complex refactoring and debugging, <b>MiMo-V2.6-Pro</b> (Score 46.3, effective $0.362) strikes the perfect balance, consuming less than 1/5th the quota of <b>Grok 4.7</b> ($2.000, 169 req/5h).",
      guide_box4_h: "4. 5-Hour Rolling Limit Management",
      guide_box4_p: "$15 tier models like <b>Kimi K3</b> (110 req/5h) or <b>Grok 4.7</b> (169 req/5h) quickly trigger 5h lockouts during intensive coding sessions. Route heavy work to $60 tier models whenever possible.",

      // Budget Table
      budget_title: "Best Model for Your Budget",
      budget_cap: "Pareto frontier lookup table. Top pick and runner-up matched to your effective budget or quota.",
      th_budget: "Effective Budget (/1M)",
      th_pick: "Top Pick",
      th_score: "Intelligence",
      th_price: "Effective Price",
      th_tier: "Go Tier (Allowance)",
      th_runner: "Runner-up",

      // Bar Index
      bar_index_title: "Pure Intelligence Ranking: {metric}",
      bar_index_cap: "Artificial Analysis Intelligence Index ranking (cost-independent).",

      // Free Models Section
      free_section_h2: "🎁 OpenCode Zen & Go Free Models ($0.00)",
      free_section_cap: "Special models offered at <b>$0 (Free)</b> token cost on OpenCode Zen and Go.",
      free_section_hint: "💡 Free models cost $0, meaning x=0 is undefined on a log scale scatter plot. They are organized here in a dedicated catalog.",
      btn_free_integrated: "🎁 Unified Catalog with OpenRouter & CommandCode ↗",
      lbl_free_include_train: "Include Contributor / Training Models",
      th_free_name: "Free Model",
      th_free_id: "OpenCode Model ID",
      th_free_creator: "Creator",
      th_free_platform: "Platform",
      th_free_index: "Intelligence (AA)",
      th_free_coding: "Coding (AA)",
      th_free_privacy: "Data Privacy",
      th_free_price: "Cost",
      free_section_note: "※ <b>Zen Only</b> models can be called with an OpenCode Zen API key at $0. <b>Zen & Go</b> models can be used in Go without deducting monthly allowance.<br>※ <b>Notice</b>: Many free promotional models may use prompt data for model improvement.",

      // All Models Table
      all_models_h2: "All Models Data Table (OpenCode Go)",
      all_models_cap: "Click column headers to sort. Inspect official OpenCode IDs and 5-hour rolling request limits.",
      th_all_select: "Select",
      th_all_model: "Model (OpenCode ID)",
      th_all_creator: "Creator",
      th_all_index: "Intelligence",
      th_all_privacy: "Data Privacy",
      th_all_allowance: "Go Monthly Cap",
      th_all_multiplier: "Multiplier",
      th_all_limit: "5h Limit",
      th_all_eff_task: "Go /task",
      th_all_raw_task: "Raw /task",
      th_all_eff_price: "Go Effective $/1M",
      th_all_quota: "Quota Burn %",
      th_all_raw_price: "Raw API $/1M",

      // Update Modal
      modal_update_h2: "🔄 How to Update Data",
      modal_update_p1: "Run the command below in your project terminal to scrape the latest <b>OpenCode official pricing & limits</b> and <b>Artificial Analysis benchmarks</b>:",
      modal_update_sources_h: "Automatically scraped sources:",
      modal_update_src1: "<b>Official Catalog & Rates</b>: <code>opencode.ai/v2/docs/console/go/</code> (token pricing, caps, context tiers)",
      modal_update_src2: "<b>5-Hour Rolling Request Limits</b>: <code>opencode.ai/go</code>",
      modal_update_src3: "<b>Benchmark Intelligence Indices</b>: <code>artificialanalysis.ai</code>",
      modal_update_cron_h: "💡 Automated Daily Updates via GitHub Actions:",
      modal_update_cron_p: "The repository includes <code>.github/workflows/deploy.yml</code> which runs daily around Finland lunchtime (~12:00 PM / 09:37 UTC) during the quietest GitHub runner window, commits updated data, and deploys to GitHub Pages.",
      modal_update_credit_h: "🎨 Design & Look-and-Feel Attribution:",
      modal_update_credit_p: "Heavily inspired by and adapted from Terry Djony's project <a href=\"https://bestmodelforyourbudget.terrydjony.com/\" target=\"_blank\" rel=\"noopener\">Best Model For Your Budget</a>. Built via AI vibe-coding for personal reference.",
      btn_confirm: "Got It",

      // Tooltips & Toasts
      tip_frontier: "★ Value Frontier (Pareto Optimal)",
      tip_dominated: "Dominated (Cheaper model is smarter)",
      toast_preset_saved: "'{name}' preset saved to browser!",
      toast_url_copied: "Shareable URL link copied to clipboard!",
      toast_url_failed: "Failed to copy URL (please copy from browser address bar)"
    },

    ko: {
      // Banner
      banner_notice_tag: "⚠️ 개인 참고용 비공식 도구",
      banner_notice_text: "개인 연구 및 편의용 비공식 도구입니다. 공개 데이터 실시간 스크래핑 기반이므로 실제 요금/한도와 차이가 있을 수 있습니다.",
      banner_vibe_tag: "🤖 100% AI 바이브 코딩",
      banner_credit_text: "Look & Feel 출처:",
      banner_credit_author: "Terry Djony 프로젝트",

      // Header
      h1_title: "OpenCode Go Value Frontier",
      badge_go: "공식 Go 카탈로그",
      hdr_sub: "<b>opencode.ai/go</b> 공식 모델 목록과 한도(\$15/\$30/\$60), <b>models.dev</b>의 API 비용, <b>Artificial Analysis</b> Intelligence Index를 결합한 가치 최적선 분석입니다. 월 \$10 구독 시 체감 가치 배율(<b>x6.0</b> vs <b>x3.0</b> vs <b>x1.5</b>)을 적용하여 진짜 가성비 챔피언을 확인하세요.",
      meta_loading: "데이터 로딩 중…",
      meta_loaded: "OpenCode Go 모델 {goCount}개 로드 완료 (전체 {totalCount}개 모델) · 출처: opencode.ai + models.dev + artificialanalysis.ai<br><span style='display:inline-flex;align-items:center;gap:6px;margin-top:4px;color:var(--accent-ink);font-weight:600;'>🕒 최근 업데이트: {lastUpdated} · 매 24시간마다 자동 갱신 (핀란드 낮 12시경)</span>",
      free_last_updated: "🕒 최근 업데이트: <b>{lastUpdated}</b> · 매 24시간마다 자동 갱신 (핀란드 낮 12시경)",

      // Free models page navigation & hero
      nav_free_hub_badge: "무료 모델 통합 허브",
      nav_link_frontier: "📊 OpenCode Go 가치 프론티어 분석기",
      nav_link_free: "🎁 무료 AI 모델 종합 가이드",
      hero_free_h1: "🎁 무료(Free) AI 모델 종합 가이드 & 벤치마크",
      hero_free_desc: "OpenCode (Zen & Go), OpenRouter, CommandCode, Groq, Google Gemini에서 토큰 비용 $0으로 제공되는 대표 무료 모델들을 한데 모았습니다. 각 모델의 실제 정체, 공식 벤치마크 지능 지수, 컨텍스트 용량 및 데이터 프라이버시를 투명하게 비교합니다.",
      hero_free_credits_label: "⭐ 데이터 참조:",

      // Buttons
      btn_free_models: "🎁 무료 모델 통합 가이드",
      btn_update_help: "🔄 데이터 업데이트 방법",
      btn_save_preset: "현재 셋 저장",
      btn_copy_link: "링크 복사",
      btn_mode_all: "전체 모델 표시",
      btn_mode_custom: "내가 선택한 모델만 비교",
      btn_open_sections: "제조사/그룹별 모델 섹션 열기",
      btn_select_all: "전체 선택",
      btn_clear_all: "선택 해제",

      // Filters
      cost_go_effective: "🚀 Go 체감 $/1M",
      cost_go_task: "🎯 Go 체감 /task",
      cost_task: "🎯 원본 /task",
      cost_go_quota: "📊 월 쿼터 소모율 %",
      cost_blended: "💵 원본 API $/1M",
      scope_go_only: "OpenCode Go 모델만",
      scope_all: "전체 모델 포함",

      mode_indicator_effective: "⚡ 기준: <b>OpenCode Go 체감 단가</b> ($10/월 구독 레버리지 반영)",
      mode_indicator_go_task: "🎯 기준: <b>태스크당 Go 체감 비용 (Cost per task)</b> (1회 완료당 추론 토큰량 및 Go 배율 반영)",
      mode_indicator_task: "🎯 기준: <b>태스크당 공식 정가 (Cost per task)</b> (1회 완료당 원본 API 비용)",
      mode_indicator_quota: "📊 기준: <b>월 쿼터 소모율 %</b> (100만 토큰당 한 달 한도 차감 비율)",
      mode_indicator_blended: "💵 기준: <b>공식 API 정가</b> (할인 전 원본 가격)",

      lbl_min_idx: "최소 지능 지수",
      lbl_collapse: "1 모델당 1행",
      lbl_maker: "제조사",
      opt_all_makers: "전체 제조사",
      ph_search: "모델 검색…",
      lbl_frontier_only: "프론티어만 보기",
      lbl_labels_all: "모든 점 라벨 표시",
      lbl_presets: "💾 설정 셋 (Presets):",
      lbl_selection_mode: "🎯 모델 선택 모드:",
      lbl_privacy_policy: "🛡️ 데이터 프라이버시 / 학습 정책:",
      lbl_no_train: "학습 미사용 (Safe / No Training)",
      lbl_train: "학습 활용 / 기여자 모델 (Model Training: Yes)",
      lbl_privacy_hint: "※ 학습 활용/기여자 모델은 기본 비활성화되어 있으며, 체크 시 포함하여 <b>가치 최적선(Frontier Edge)</b>이 실시간으로 재계산됩니다.",
      drawer_help_text: "각 제조사(Provider) 헤더를 클릭하면 <b>그룹 전체를 한 번에 On/Off</b> 할 수 있고, 개별 칩을 눌러 세부 선택할 수 있습니다.",
      ph_drawer_search: "섹션 내 모델 검색…",
      selected_count_label: "{n}개 선택됨",

      // Scatter Chart
      scatter_title: "지능 지수 vs {costTitle}: {metric}",
      scatter_cap: "{costCap} 주황색 최상단 최적선(Frontier Edge) 위의 모델들이 동일 비용 대비 최고 성능을 내는 파레토 최적 모델입니다.",
      leg_frontier: "가치 프론티어 (파레토 최적점)",
      leg_dominated: "열위 (더 싼 모델이 더 우수함)",
      leg_edge: "최상단 최적선 (Frontier Edge)",
      leg_tier60: "$60 티어 (x6.0)",
      leg_tier30: "$30 티어 (x3.0)",
      leg_tier15: "$15 티어 (x1.5)",
      leg_training: "Training: Yes",

      // Strategy Guide
      guide_hdr: "OpenCode Go 실전 모델 선택 가이드",
      guide_cap: "OpenCode Go 공식 $10/월 구독 환경에서 최적의 모델 운용 전략:",
      guide_box1_h: "1. 일상 코딩 메인: $60/월 티어 (x6.0 배율)",
      guide_box1_p: "<b>GLM-5.3-Flash</b> (점수 41.8)는 100만 토큰당 체감 <b>$0.040</b>이며 5시간당 6,320건의 여유로운 제한을 제공합니다. 초저비용 서브로는 <b>MiMo-V2.6-Flash</b> (점수 37.9, 체감 $0.029, 30,100건/5h)가 압도적인 가성비를 자랑합니다.",
      guide_box2_h: "2. $15/월 티어의 저가 함정 (GPT-6 Luna 탈락)",
      guide_box2_p: "API 정가(\$0.20)만 보면 싸 보이는 <b>GPT 6 Luna</b>는 Go에서 \$15 한도(x1.5 배율)에 묶여 체감 단가가 <b>$0.133</b>입니다. 체감 <b>$0.040</b>이면서 점수는 훨씬 높은 <b>GLM-5.3-Flash</b>(41.8점)에 완전히 밀려 프론티어에서 탈락합니다.",
      guide_box3_h: "3. 고난도 추론 / 에이전틱 작업",
      guide_box3_p: "복잡한 리팩토링이나 디버깅이 필요할 때는 <b>MiMo-V2.6-Pro</b> (점수 46.3, 체감 $0.362)가 가장 훌륭한 균형을 보입니다. 동일 점수대의 <b>Grok 4.7</b>(체감 $2.000, 169건/5h) 대비 쿼터를 1/5 이하로 아낄 수 있습니다.",
      guide_box4_h: "4. 5시간 롤링 윈도우 관리 팁",
      guide_box4_p: "$15 티어의 <b>Kimi K3</b>(110건/5h), <b>Grok 4.7</b>(169건/5h)은 연속 코딩 시 금방 5시간 락에 걸립니다. 대량 생성 작업은 반드시 $60 티어(GLM-5.3-Flash, MiMo Flash)로 라우팅하는 것이 효율적입니다.",

      // Budget Table
      budget_title: "예산별 추천 모델 (Best Model for Your Budget)",
      budget_cap: "가치 프론티어 룩업 테이블. 본인의 체감 예산 또는 쿼터에 맞는 최적의 Pick과 차선책(Runner-up)입니다.",
      th_budget: "체감 예산 (/1M 토큰)",
      th_pick: "추천 Pick",
      th_score: "지능 점수",
      th_price: "체감 단가",
      th_tier: "Go 티어 (한도)",
      th_runner: "차선책 (Runner-up)",

      // Bar Index
      bar_index_title: "순수 지능 랭킹: {metric}",
      bar_index_cap: "비용을 제외한 Artificial Analysis Intelligence Index 순위.",

      // Free Models Section
      free_section_h2: "🎁 OpenCode Zen & Go 무료 모델 목록 (100% Free / $0.00)",
      free_section_cap: "OpenCode Zen 및 Go에서 토큰 비용이 <b>$0(Free)</b>로 제공되는 특별 모델들입니다.",
      free_section_hint: "💡 무료 모델은 비용이 $0이므로 log scale 산점도에는 x=0이 정의되지 않아 별도의 무료 전용 카탈로그로 완벽 정리했습니다.",
      btn_free_integrated: "🎁 OpenRouter & CommandCode 포함 통합 가이드 ↗",
      lbl_free_include_train: "학습 활용 모델 포함",
      th_free_name: "무료 모델명",
      th_free_id: "OpenCode 모델 ID",
      th_free_creator: "제조사",
      th_free_platform: "제공 플랫폼",
      th_free_index: "지능 점수 (AA)",
      th_free_coding: "코딩 점수 (AA)",
      th_free_privacy: "데이터 프라이버시",
      th_free_price: "비용",
      free_section_note: "※ <b>Zen Only</b> 모델은 OpenCode Zen API 키에서 $0으로 호출 가능하며, <b>Zen & Go</b> 모델은 Go 플랜에서도 한도 차감 없이 사용 가능합니다.<br>※ <b>주의</b>: 대부분의 무료 모델은 프로모션/피드백 수집 기간 동안 사용자 프롬프트가 모델 학습에 활용될 수 있으니 유의하시기 바랍니다.",

      // All Models Table
      all_models_h2: "전체 유료 모델 데이터 (OpenCode Go)",
      all_models_cap: "열 제목을 클릭하면 정렬됩니다. OpenCode 공식 모델 ID와 5시간당 요청 제한을 확인하세요.",
      th_all_select: "선택",
      th_all_model: "모델 (OpenCode ID)",
      th_all_creator: "제조사",
      th_all_index: "지능 점수",
      th_all_privacy: "프라이버시 (학습 여부)",
      th_all_allowance: "Go 월간 한도",
      th_all_multiplier: "가치 배율",
      th_all_limit: "5시간 제한",
      th_all_eff_task: "Go 체감/task",
      th_all_raw_task: "정가/task",
      th_all_eff_price: "Go 체감 $/1M",
      th_all_quota: "월 쿼터 소모율",
      th_all_raw_price: "API 정가 $/1M",

      // Update Modal
      modal_update_h2: "🔄 데이터 최신 업데이트 방법",
      modal_update_p1: "터미널(프로젝트 폴더)에서 아래 명령을 실행하면 <b>OpenCode 공식 가격표</b>와 <b>Artificial Analysis 일일 벤치마크</b>를 한 번에 새로고침합니다:",
      modal_update_sources_h: "자동 수집되는 공식 출처:",
      modal_update_src1: "<b>공식 모델 및 단가표</b>: <code>opencode.ai/v2/docs/console/go/</code> (토큰 단가, $60/$30/$15 한도, 컨텍스트별 요율)",
      modal_update_src2: "<b>5시간 롤링 요청 제한</b>: <code>opencode.ai/go</code> (5시간당 최대 허용 횟수)",
      modal_update_src3: "<b>최신 지능 지수</b>: <code>artificialanalysis.ai</code> (Intelligence Index & Coding Index)",
      modal_update_cron_h: "💡 GitHub Actions를 통한 일일 자동 배포:",
      modal_update_cron_p: "<code>.github/workflows/deploy.yml</code> 워크플로우가 핀란드 낮 12시경 (09:37 UTC, 미국 심야 한산한 시간대)에 자동 실행되어 최신 데이터를 수집하고 GitHub Pages에 배포합니다.",
      modal_update_credit_h: "🎨 디자인 및 시각화 출처:",
      modal_update_credit_p: "Terry Djony의 <a href=\"https://bestmodelforyourbudget.terrydjony.com/\" target=\"_blank\" rel=\"noopener\">Best Model For Your Budget</a> 프로젝트 시각화 디자인을 상당 부분 클론/차용하여 제작되었습니다. AI 바이브 코딩으로 제작되었습니다.",
      btn_confirm: "확인",

      // Tooltips & Toasts
      tip_frontier: "★ 가치 프론티어 (파레토 최적)",
      tip_dominated: "열위 모델 (더 싼 모델이 더 우수)",
      toast_preset_saved: "'{name}' 셋이 브라우저에 저장되었습니다!",
      toast_url_copied: "현재 분석 상태가 담긴 URL 링크가 복사되었습니다!",
      toast_url_failed: "URL 복사 실패 (주소창 URL을 직접 복사하세요)"
    }
  };

  // State Management
  const params = new URLSearchParams(window.location.search);
  let currentLang = params.get("lang") || localStorage.getItem("preferred_lang") || "en";
  if (currentLang !== "en" && currentLang !== "ko") currentLang = "en";

  let currentTheme = localStorage.getItem("preferred_theme") || "light";

  const listeners = [];

  function t(key, vars = {}) {
    const d = DICT[currentLang] || DICT.en;
    let str = d[key] != null ? d[key] : (DICT.en[key] != null ? DICT.en[key] : key);
    for (const [k, v] of Object.entries(vars)) {
      str = str.replace(new RegExp(`\\{${k}\\}`, "g"), v);
    }
    return str;
  }

  function applyDOM() {
    document.documentElement.lang = currentLang;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const k = el.getAttribute("data-i18n");
      const text = t(k);
      if (text.includes("<") && text.includes(">")) {
        el.innerHTML = text;
      } else {
        el.textContent = text;
      }
    });

    document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
      const k = el.getAttribute("data-i18n-ph");
      el.placeholder = t(k);
    });

    // Update Language switcher buttons
    document.querySelectorAll("#langSeg button").forEach((b) => {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang") === currentLang ? "true" : "false");
    });

    // Update cross-page links to preserve current language
    const freeLink = document.getElementById("freeModelsLink");
    if (freeLink) {
      freeLink.href = `free_models.html?lang=${currentLang}`;
    }
    const indexLink = document.getElementById("indexLink");
    if (indexLink) {
      indexLink.href = `index.html?lang=${currentLang}`;
    }
  }

  function setLanguage(lang) {
    if (lang !== "en" && lang !== "ko") return;
    currentLang = lang;
    localStorage.setItem("preferred_lang", lang);

    // Sync URL without reload
    const url = new URL(window.location.href);
    url.searchParams.set("lang", lang);
    window.history.replaceState(null, "", url.toString());

    applyDOM();
    listeners.forEach((fn) => fn(currentLang));
  }

  function setTheme(theme) {
    currentTheme = theme === "dark" ? "dark" : "light";
    localStorage.setItem("preferred_theme", currentTheme);
    document.documentElement.setAttribute("data-theme", currentTheme);

    const btn = document.getElementById("btnThemeToggle");
    if (btn) {
      btn.textContent = currentTheme === "dark" ? "☀️" : "🌙";
      btn.title = currentTheme === "dark" ? "Switch to Light Theme" : "Switch to Dark Theme";
    }
  }

  function toggleTheme() {
    setTheme(currentTheme === "dark" ? "light" : "dark");
  }

  // Initial setup on script run
  document.documentElement.setAttribute("data-theme", currentTheme);

  document.addEventListener("DOMContentLoaded", () => {
    applyDOM();
    setTheme(currentTheme);

    // Bind lang buttons
    document.querySelectorAll("#langSeg button").forEach((b) => {
      b.addEventListener("click", () => setLanguage(b.getAttribute("data-lang")));
    });

    // Bind theme button
    const themeBtn = document.getElementById("btnThemeToggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", toggleTheme);
    }
  });

  // Export API
  window.I18N = {
    get lang() { return currentLang; },
    get theme() { return currentTheme; },
    t,
    setLanguage,
    setTheme,
    toggleTheme,
    onChange: (fn) => listeners.push(fn),
    applyDOM
  };
})();
