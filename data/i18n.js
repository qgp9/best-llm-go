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
      banner_notice_tag: "Note",
      banner_vibe_tag: "🤖 100% Vibe-Coded with AI",
      banner_notice_text: "Unofficial personal sandbox (public API data) · UI inspired by <a href=\"https://bestmodelforyourbudget.terrydjony.com/\" target=\"_blank\" rel=\"noopener\">Terry Djony</a>.",

      // Header
      h1_title: "OpenCode Go Value Frontier",
      badge_go: "Official Go Catalog",
      hdr_sub: "Pareto frontier value analyzer for OpenCode Go ($10/mo plan). Combines official model allowances ($15/$30/$60), API rates, and Artificial Analysis benchmarks to highlight optimal models.",
      meta_loading: "Loading data…",
      meta_loaded: "{goCount} Go models ({totalCount} total) · Sources: opencode.ai + models.dev + artificialanalysis.ai · 🕒 <b>{lastUpdated}</b> (Daily sync)",
      free_last_updated: "🕒 <b>{lastUpdated}</b> (Daily sync)",

      // Free models page navigation & hero
      nav_free_hub_badge: "Free Models Hub",
      nav_link_frontier: "📊 OpenCode Go Value Frontier",
      nav_link_free: "🎁 Free AI Models Guide",
      hero_free_h1: "🎁 Free AI Models Guide & Benchmarks",
      hero_free_desc: "Directory of $0 models across OpenCode, OpenRouter, CommandCode, Groq, and Gemini. Compare underlying model identities, benchmarks, and data privacy policies.",
      hero_free_credits_label: "⭐ Sources:",

      // Buttons
      btn_free_models: "🎁 Free AI Models",
      btn_about_sources: "ℹ️ Data & Sources",
      btn_save_preset: "Save Preset",
      btn_copy_link: "Copy Link",
      btn_more_filters: "More Filters",
      btn_hide_filters: "Hide Filters",
      btn_mode_all: "Show All Models",
      btn_mode_custom: "Compare My Selection",
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

      mode_indicator_effective: "⚡ Basis: <b>Go Effective Cost</b> ($10/mo subscription leverage)",
      mode_indicator_go_task: "🎯 Basis: <b>Go Cost per Task</b> (Effective task cost with Go leverage)",
      mode_indicator_task: "🎯 Basis: <b>Raw Cost per Task</b> (Official API cost per completed task)",
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
      lbl_privacy_policy: "🛡️ Data Privacy:",
      lbl_no_train: "Safe / No Training",
      lbl_train: "Training: Yes (Contributor)",
      lbl_privacy_hint: "※ Contributor models excluded by default.",
      drawer_help_text: "Click provider header to toggle group, or chips to customize.",
      ph_drawer_search: "Filter models…",
      selected_count_label: "{n} selected",

      // Scatter Chart
      scatter_title: "Intelligence Index vs {costTitle}: {metric}",
      scatter_cap: "{costCap} The orange top line (Frontier Edge) marks Pareto-optimal models with the best intelligence per cost.",
      leg_frontier: "Value Frontier (Pareto Optimal)",
      leg_dominated: "Dominated (Cheaper model is smarter)",
      leg_edge: "Frontier Edge",
      leg_tier60: "$60 Tier (x6.0)",
      leg_tier30: "$30 Tier (x3.0)",
      leg_tier15: "$15 Tier (x1.5)",
      leg_training: "Training: Yes",

      // Strategy Guide
      guide_hdr: "OpenCode Go Strategy & Model Guide",
      guide_cap: "Optimal model operation strategy under the $10/mo OpenCode Go subscription:",
      guide_box1_h: "1. Daily Coding Driver: $60/mo Tier (x6.0 Multiplier)",
      guide_box1_p: "<b>GLM-5.3-Flash</b> (Score 41.8) costs just <b>$0.040</b>/1M effective tokens with 6,320 req/5h. For ultra-cheap volume, <b>MiMo-V2.6-Flash</b> (Score 37.9, $0.029, 30,100 req/5h) is unbeatable.",
      guide_box2_h: "2. The $15/mo Tier Trap (GPT-6 Luna Eliminated)",
      guide_box2_p: "<b>GPT 6 Luna</b> seems cheap at $0.20 raw, but Go caps it at $15 (x1.5), raising effective cost to <b>$0.133</b>. Outclassed by <b>GLM-5.3-Flash</b> ($0.040, score 41.8), it drops off the frontier.",
      guide_box3_h: "3. Heavy Reasoning & Agentic Tasks",
      guide_box3_p: "For complex refactoring and debugging, <b>MiMo-V2.6-Pro</b> (Score 46.3, effective $0.362) strikes the ideal balance, using <1/5th the quota of <b>Grok 4.7</b> ($2.000, 169 req/5h).",
      guide_box4_h: "4. 5-Hour Rolling Limit Management",
      guide_box4_p: "$15 tier models like <b>Kimi K3</b> (110 req/5h) or <b>Grok 4.7</b> (169 req/5h) lock quickly during long sessions. Route heavy coding work to $60 tier models whenever possible.",

      // Budget Table
      budget_title: "Best Model for Your Budget",
      budget_cap: "Pareto frontier lookup table: Top pick and runner-up matched to your budget.",
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
      free_section_h2: "🎁 OpenCode Zen & Go Free Models ($0)",
      free_section_cap: "Special models offered at <b>$0 (Free)</b> token cost on OpenCode Zen and Go.",
      free_section_hint: "💡 Free models ($0) cannot be plotted on a log scale, listed below separately.",
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
      free_section_note: "※ <b>Zen Only</b>: $0 via Zen API key. <b>Zen & Go</b>: $0 in Go without quota deduction.<br>※ <b>Privacy</b>: Free/promotional models may use prompts for training.",

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

      // About & Data Sources Modal
      modal_sources_h2: "ℹ️ About & Data Sources",
      modal_sources_h: "📊 Data Sources",
      modal_src1: "<b>OpenCode Go</b>: <code>opencode.ai/go</code> (Official catalog, monthly caps & limits)",
      modal_src2: "<b>Market Rates</b>: <code>models.dev</code> (Standard unadjusted API rates)",
      modal_src3: "<b>Intelligence Benchmarks</b>: <code>artificialanalysis.ai</code> (Intelligence Index & Coding Index)",
      modal_sync_h: "🕒 Update Schedule",
      modal_sync_p: "Data is automatically synchronized daily at 09:37 UTC via GitHub Actions.",
      modal_credit_h: "🎨 Attribution",
      modal_credit_p: "100% vibe-coded with AI. UI visualization adapted from Terry Djony's <a href=\"https://bestmodelforyourbudget.terrydjony.com/\" target=\"_blank\" rel=\"noopener\">Best Model For Your Budget</a>. Unofficial personal research project.",
      btn_confirm: "Got It",

      // Tooltips & Toasts
      tip_frontier: "★ Value Frontier (Pareto Optimal)",
      tip_dominated: "Dominated (Cheaper model is smarter)",
      toast_preset_saved: "'{name}' preset saved to browser!",
      toast_url_copied: "Shareable URL link copied to clipboard!",
      toast_url_failed: "Failed to copy URL (please copy from browser address bar)",

      // Free Models Cards
      free_plat_oc_badge: "14 Free Models",
      free_plat_oc_desc: "Preview and contributor models offered at $0 in OpenCode Zen API (<code>/zen/v1/</code>) and Go subscription plan.",
      free_plat_oc_spec1: "<b>Top Models:</b> Space Bunny Free, LongCat 2.0, MiMo Flash, Muse Spark",
      free_plat_oc_spec2: "<b>Pricing:</b> $0.00 / token (Input / Output / Cache all Free)",
      free_plat_oc_spec3: "<b>Rate Limits:</b> Standard rolling 5-hour limits apply (some unlimited)",
      free_plat_oc_spec4: "<b>Data Policy:</b> Contributor models may collect prompt data for training",
      free_plat_oc_foot1: "OpenCode Model Docs",
      free_plat_oc_foot2: "API & Go Subscription",

      free_plat_or_badge: "17 Free Models",
      free_plat_or_desc: "Free serving of top open-weights models worldwide with <code>:free</code> endpoint tags.",
      free_plat_or_spec1: "<b>Top Models:</b> Ling 3.1 Flash (Intel 41.1), Nemotron 3 Ultra (550B), Inkling (1M)",
      free_plat_or_spec2: "<b>Pricing:</b> $0 / token, no credit card required",
      free_plat_or_spec3: "<b>Rate Limits:</b> 20 RPM, 50 RPD unpaid, 1,000 RPD paid account",
      free_plat_or_spec4: "<b>Auto Router:</b> Automatic selection of best free model with <code>openrouter/free</code>",
      free_plat_or_foot1: "OpenRouter Free Models Live",
      free_plat_or_foot2: "REST API Compatible",

      free_plat_cmd_badge: "4 Free Models",
      free_plat_cmd_desc: "Terminal AI coding agent providing stealth preview models at $0 with proprietary <b>taste-1</b> fine-tuning.",
      free_plat_cmd_spec1: "<b>Top Models:</b> Ox Alpha (GLM-5.3 Flash identity), Space Bunny, Glyph Cluster",
      free_plat_cmd_spec2: "<b>Pricing:</b> $0 promotional preview on free tier",
      free_plat_cmd_spec3: "<b>Rate Limits:</b> Ox Alpha (100T/day effectively unlimited), Glyph (100 req/day)",
      free_plat_cmd_spec4: "<b>Terminal CLI:</b> Instant call with <code>cmd --model stealth/ox-alpha</code>",
      free_plat_cmd_foot1: "CommandCode Official Web",
      free_plat_cmd_foot2: "CLI & Desktop Studio",

      // Accordion 1
      free_acc1_title: "⚡ 30 Free API Providers & Base URL Quick Reference",
      free_acc1_sub: "(via awesome-free-llm-apis)",
      free_acc1_desc: "Verified list of <b>30 LLM API Providers</b> offering free API keys with email signup (no credit card required), with OpenAI-compatible Base URLs and key links. Click <code>Copy Base URL</code> to paste into your tools.",
      th_prov_name: "Provider",
      th_prov_models: "Free Models",
      th_prov_cc: "Credit Card?",
      th_prov_ctx: "Max Context",
      th_prov_url: "OpenAI-compatible Base URL",
      th_prov_best: "Recommended Model",
      th_prov_key: "API Key",

      // Accordion 2
      free_acc2_title: "🛠️ 1-Click Free API Setup Guide for Popular Developer Tools",
      free_acc2_sub: "(Claude Code, Cursor, Codex, OpenCode, Aider)",
      tab_groq_cursor: "Cursor (Groq Free Key)",
      tab_claudecode: "Claude Code (OpenRouter)",
      tab_codex: "Codex CLI (Groq)",
      tab_cmdcode: "CommandCode CLI (Ox Alpha)",
      tab_python: "Python (OpenAI SDK)",

      // Filters & Search
      lbl_filter_platform: "Platform:",
      plat_all: "All",
      ph_free_search: "Search model name, identity, provider… (e.g. GLM, Llama, 1M)",
      lbl_filter_category: "Specialty:",
      cat_all: "All",
      cat_coding: "💻 Coding",
      cat_reasoning: "🧠 Reasoning",
      cat_long_context: "📜 1M Large Context",
      cat_lightweight: "⚡ Fast / Lightweight",
      lbl_filter_safe_only: "🛡️ Show Safe / No Training (ZDR) Only",
      sort_intel_desc: "Intelligence: High to Low (Recommended)",
      sort_coding_desc: "Coding Index: High to Low",
      sort_context_desc: "Context Size: Large to Small",
      sort_name_asc: "Model Name: A to Z",
      view_card: "🗂️ Card View",
      view_table: "📋 Table View",

      // Table Headers
      th_cat_name: "Model & Identity",
      th_cat_platform: "Platform",
      th_cat_category: "Category",
      th_cat_intel: "Intelligence (AA)",
      th_cat_coding: "Coding (AA)",
      th_cat_context: "Context",
      th_cat_privacy: "Data Privacy",
      th_cat_limit: "Rate Limits / Notes",
      th_cat_links: "Run CLI & Links",

      // Dynamic Card Labels
      lbl_true_identity: "💡 True Identity:",
      lbl_recommended_for: "🎯 Recommended For:",
      tag_safe_model: "🛡️ Safe (No Training · ZDR)",
      tag_train_model: "⚠️ Model Training / Contributor",
      tag_general_cat: "🌐 General Intelligence",
      btn_copy: "Copy",
      btn_copied: "Copied!",
      msg_no_free_models: "No free models match your search criteria.",
      msg_no_free_hint: "Try resetting filters or changing your search terms.",
      msg_catalog_count: "Showing <b>{count}</b> free models (total {total})",
      msg_aa_intel_note: "※ Intelligence scores are sourced from official Artificial Analysis Intelligence Index.",
      acc_toggle_open: "▼ Click to open",
      acc_toggle_close: "▲ Close"
    },

    ko: {
      // Banner
      banner_notice_tag: "안내",
      banner_vibe_tag: "🤖 100% AI 바이브코딩",
      banner_notice_text: "AI로 바이브코딩된 개인 연구용 비공식 프로젝트입니다 (공개 API 데이터 기반) · UI는 <a href=\"https://bestmodelforyourbudget.terrydjony.com/\" target=\"_blank\" rel=\"noopener\">Terry Djony</a> 참고.",

      // Header
      h1_title: "OpenCode Go Value Frontier",
      badge_go: "공식 Go 카탈로그",
      hdr_sub: "OpenCode Go($10/월) 가치 프론티어 분석기. 월간 한도($15/$30/$60), API 정가, 지능 벤치마크를 결합해 최적의 가성비 모델을 선별합니다.",
      meta_loading: "데이터 로딩 중…",
      meta_loaded: "{goCount}개 Go 모델 (전체 {totalCount}개) · 출처: opencode.ai + models.dev + artificialanalysis.ai · 🕒 <b>{lastUpdated}</b> (매일 자동 갱신)",
      free_last_updated: "🕒 <b>{lastUpdated}</b> (매일 자동 갱신)",

      // Free models page navigation & hero
      nav_free_hub_badge: "무료 모델 허브",
      nav_link_frontier: "📊 OpenCode Go 가치 프론티어",
      nav_link_free: "🎁 무료 AI 모델 가이드",
      hero_free_h1: "🎁 무료 AI 모델 가이드 & 벤치마크",
      hero_free_desc: "OpenCode, OpenRouter, CommandCode, Groq, Gemini의 $0 무료 모델 디렉토리. 원본 모델의 실체, 벤치마크 지능 지수, 데이터 프라이버시를 비교합니다.",
      hero_free_credits_label: "⭐ 데이터 출처:",

      // Buttons
      btn_free_models: "🎁 무료 AI 모델",
      btn_about_sources: "ℹ️ 데이터 출처",
      btn_save_preset: "프리셋 저장",
      btn_copy_link: "링크 복사",
      btn_more_filters: "상세 필터",
      btn_hide_filters: "상세 필터 접기",
      btn_mode_all: "전체 모델 표시",
      btn_mode_custom: "내 선택 모델만 비교",
      btn_open_sections: "제조사별 모델 열기",
      btn_select_all: "전체 선택",
      btn_clear_all: "선택 해제",

      // Filters
      cost_go_effective: "🚀 Go 체감 $/1M",
      cost_go_task: "🎯 Go 체감 /task",
      cost_task: "🎯 정가 /task",
      cost_go_quota: "📊 월 쿼터 소모율 %",
      cost_blended: "💵 API 정가 $/1M",
      scope_go_only: "OpenCode Go 모델만",
      scope_all: "전체 모델 포함",

      mode_indicator_effective: "⚡ 기준: <b>Go 체감 단가</b> ($10/월 플랜 가치 배율 반영)",
      mode_indicator_go_task: "🎯 기준: <b>태스크당 Go 체감 비용</b> (추론 토큰 및 Go 배율 반영)",
      mode_indicator_task: "🎯 기준: <b>태스크당 정가</b> (1회 태스크 완료당 원본 API 비용)",
      mode_indicator_quota: "📊 기준: <b>월 쿼터 소모율 %</b> (100만 토큰당 월 한도 차감 비율)",
      mode_indicator_blended: "💵 기준: <b>공식 API 정가</b> (할인 전 원본 가격)",

      lbl_min_idx: "최소 지능 지수",
      lbl_collapse: "1 모델당 1행",
      lbl_maker: "제조사",
      opt_all_makers: "전체 제조사",
      ph_search: "모델 검색…",
      lbl_frontier_only: "프론티어만 보기",
      lbl_labels_all: "모든 점 라벨 표시",
      lbl_presets: "💾 프리셋:",
      lbl_selection_mode: "🎯 선택 모드:",
      lbl_privacy_policy: "🛡️ 데이터 프라이버시:",
      lbl_no_train: "학습 미사용 (Safe)",
      lbl_train: "학습 활용 (기여자)",
      lbl_privacy_hint: "※ 학습 활용 모델은 기본 제외됩니다.",
      drawer_help_text: "제조사 헤더 클릭 시 그룹 토글, 칩 클릭 시 개별 선택.",
      ph_drawer_search: "섹션 내 모델 검색…",
      selected_count_label: "{n}개 선택됨",

      // Scatter Chart
      scatter_title: "지능 지수 vs {costTitle}: {metric}",
      scatter_cap: "{costCap} 주황색 최적선(Frontier Edge)은 비용 대비 최고 지능을 갖춘 파레토 최적 모델입니다.",
      leg_frontier: "가치 프론티어 (파레토 최적)",
      leg_dominated: "열위 (더 싼 모델이 더 우수)",
      leg_edge: "최적선 (Frontier Edge)",
      leg_tier60: "$60 티어 (x6.0)",
      leg_tier30: "$30 티어 (x3.0)",
      leg_tier15: "$15 티어 (x1.5)",
      leg_training: "학습 활용: Yes",

      // Strategy Guide
      guide_hdr: "OpenCode Go 실전 모델 가이드",
      guide_cap: "공식 $10/월 OpenCode Go 플랜 기준 최적 모델 운용 전략:",
      guide_box1_h: "1. 일상 코딩 메인: $60/월 티어 (x6.0 배율)",
      guide_box1_p: "<b>GLM-5.3-Flash</b> (점수 41.8)는 체감 <b>$0.040</b>/1M에 6,320건/5h를 제공합니다. 대량 처리용으로는 <b>MiMo-V2.6-Flash</b> (점수 37.9, $0.029, 30,100건/5h)가 독보적입니다.",
      guide_box2_h: "2. $15/월 티어의 저가 함정 (GPT-6 Luna 탈락)",
      guide_box2_p: "정가($0.20)가 싸 보이는 <b>GPT 6 Luna</b>는 Go에서 $15 한도(x1.5)에 묶여 체감 단가가 <b>$0.133</b>입니다. <b>GLM-5.3-Flash</b>($0.040, 41.8점)에 밀려 프론티어에서 탈락합니다.",
      guide_box3_h: "3. 고난도 추론 / 에이전틱 작업",
      guide_box3_p: "복잡한 리팩토링에는 <b>MiMo-V2.6-Pro</b> (점수 46.3, 체감 $0.362)가 최적이며, <b>Grok 4.7</b>(체감 $2.000, 169건/5h) 대비 쿼터를 1/5 이하로 절약합니다.",
      guide_box4_h: "4. 5시간 롤링 한도 관리",
      guide_box4_p: "$15 티어의 <b>Kimi K3</b>(110건/5h), <b>Grok 4.7</b>(169건/5h)은 집중 작업 시 금방 잠깁니다. 대량 코딩은 $60 티어 모델로 라우팅하는 것이 안전합니다.",

      // Budget Table
      budget_title: "예산별 추천 모델 (Best Model for Your Budget)",
      budget_cap: "예산 구간별 최적의 추천 모델과 차선책(Runner-up) 목록입니다.",
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
      free_section_h2: "🎁 OpenCode Zen & Go 무료 모델 ($0)",
      free_section_cap: "OpenCode Zen 및 Go에서 토큰 비용이 <b>$0(Free)</b>로 제공되는 특별 모델입니다.",
      free_section_hint: "💡 $0 무료 모델은 로그 스케일 차트 표현이 불가하여 별도 목록으로 제공합니다.",
      btn_free_integrated: "🎁 OpenRouter & CommandCode 포함 통합 가이드 ↗",
      lbl_free_include_train: "학습 활용 모델 포함",
      th_free_name: "무료 모델명",
      th_free_id: "OpenCode 모델 ID",
      th_free_creator: "제조사",
      th_free_platform: "플랫폼",
      th_free_index: "지능 점수 (AA)",
      th_free_coding: "코딩 점수 (AA)",
      th_free_privacy: "데이터 프라이버시",
      th_free_price: "비용",
      free_section_note: "※ <b>Zen Only</b>: Zen API 키로 $0 호출 가능. <b>Zen & Go</b>: Go 플랜에서 한도 차감 없이 무료.<br>※ <b>주의</b>: 무료/프로모션 모델은 프롬프트가 학습에 활용될 수 있습니다.",

      // All Models Table
      all_models_h2: "전체 유료 모델 데이터 (OpenCode Go)",
      all_models_cap: "열 제목을 클릭하면 정렬됩니다. 공식 모델 ID와 5시간당 요청 제한을 확인하세요.",
      th_all_select: "선택",
      th_all_model: "모델 (OpenCode ID)",
      th_all_creator: "제조사",
      th_all_index: "지능 점수",
      th_all_privacy: "데이터 프라이버시",
      th_all_allowance: "Go 월간 한도",
      th_all_multiplier: "가치 배율",
      th_all_limit: "5시간 제한",
      th_all_eff_task: "Go 체감/task",
      th_all_raw_task: "정가/task",
      th_all_eff_price: "Go 체감 $/1M",
      th_all_quota: "월 쿼터 소모율",
      th_all_raw_price: "API 정가 $/1M",

      // About & Data Sources Modal
      modal_sources_h2: "ℹ️ 데이터 및 출처 안내",
      modal_sources_h: "📊 데이터 출처",
      modal_src1: "<b>OpenCode Go</b>: <code>opencode.ai/go</code> (공식 모델 목록, $15/$30/$60 월간 한도, 5시간 요청 제한)",
      modal_src2: "<b>시장 원본 API 정가</b>: <code>models.dev</code> (할인 전 표준 시장 가격)",
      modal_src3: "<b>지능 벤치마크 지표</b>: <code>artificialanalysis.ai</code> (공인 Intelligence Index & Coding Index)",
      modal_sync_h: "🕒 갱신 주기",
      modal_sync_p: "매일 09:37 UTC에 GitHub Actions를 통해 최신 데이터가 자동으로 동기화됩니다.",
      modal_credit_h: "🎨 시각화 및 안내",
      modal_credit_p: "AI로 100% 바이브 코딩된 개인 연구 프로젝트입니다. UI 시각화는 Terry Djony의 <a href=\"https://bestmodelforyourbudget.terrydjony.com/\" target=\"_blank\" rel=\"noopener\">Best Model For Your Budget</a>을 참고했습니다.",
      btn_confirm: "확인",

      // Tooltips & Toasts
      tip_frontier: "★ 가치 프론티어 (파레토 최적)",
      tip_dominated: "열위 모델 (더 싼 모델이 더 우수)",
      toast_preset_saved: "'{name}' 셋이 브라우저에 저장되었습니다!",
      toast_url_copied: "현재 분석 상태가 담긴 URL 링크가 복사되었습니다!",
      toast_url_failed: "URL 복사 실패 (주소창 URL을 직접 복사하세요)",

      // Free Models Cards
      free_plat_oc_badge: "14개 무료 모델",
      free_plat_oc_desc: "OpenCode Zen API(<code>/zen/v1/</code>) 및 Go 플랜에서 $0으로 지원하는 프리뷰 및 기여자 모델들입니다.",
      free_plat_oc_spec1: "<b>대표 모델:</b> Space Bunny Free, LongCat 2.0, MiMo Flash, Muse Spark",
      free_plat_oc_spec2: "<b>과금 정책:</b> 토큰당 $0.00 (Input / Output / Cache 모두 Free)",
      free_plat_oc_spec3: "<b>요청 한도:</b> 표준 롤링 5시간 한도 적용 (일부 무제한)",
      free_plat_oc_spec4: "<b>주의점:</b> Contributor 모델은 데이터 개선 학습에 수집될 수 있음",
      free_plat_oc_foot1: "OpenCode 모델 카탈로그",
      free_plat_oc_foot2: "API & Go 구독",

      free_plat_or_badge: "17개 무료 모델",
      free_plat_or_desc: "<code>:free</code> 태그가 붙은 엔드포인트로 전 세계 최상위 오픈 웨이트 모델들을 무료 서빙합니다.",
      free_plat_or_spec1: "<b>대표 모델:</b> Ling 3.1 Flash (지능 41.1), Nemotron 3 Ultra (550B), Inkling (1M)",
      free_plat_or_spec2: "<b>과금 정책:</b> $0 / 토큰, 신용카드 등록 없이 사용 가능",
      free_plat_or_spec3: "<b>요청 한도:</b> 분당 20회(20 RPM), 미결제 50 RPD, 결제 계정 1,000 RPD",
      free_plat_or_spec4: "<b>자동 라우터:</b> <code>openrouter/free</code> 호출 시 최적 무료 모델 자동 선택",
      free_plat_or_foot1: "OpenRouter Free Models 실시간",
      free_plat_or_foot2: "REST API 호환",

      free_plat_cmd_badge: "4개 무료 모델",
      free_plat_cmd_desc: "터미널 AI 코딩 에이전트로, 독자적인 <b>taste-1</b> 스타일 학습과 함께 스텔스 프리뷰 모델을 $0 제공합니다.",
      free_plat_cmd_spec1: "<b>대표 모델:</b> Ox Alpha (GLM-5.3 Flash 실체), Space Bunny, Glyph Cluster",
      free_plat_cmd_spec2: "<b>과금 정책:</b> 무료 플랜에서도 프로모션 기간 동안 $0 제공",
      free_plat_cmd_spec3: "<b>요청 한도:</b> Ox Alpha (100T/day 한도 없음), Glyph (100 req/day)",
      free_plat_cmd_spec4: "<b>터미널 실행:</b> <code>cmd --model stealth/ox-alpha</code> 즉시 호출",
      free_plat_cmd_foot1: "CommandCode 공식 웹",
      free_plat_cmd_foot2: "CLI & Desktop Studio",

      // Accordion 1
      free_acc1_title: "⚡ 30개 무료 API 제공사 & Base URL 퀵 레퍼런스",
      free_acc1_sub: "(awesome-free-llm-apis 연동)",
      free_acc1_desc: "신용카드 없이 이메일 가입만으로 무료 키를 발급해주는 <b>30개 검증된 LLM API 프로바이더</b>의 OpenAI 호환 Base URL과 키 발급 링크 목록입니다. <code>Base URL 복사</code> 후 바로 도구에 붙여넣으세요.",
      th_prov_name: "제공사 (Provider)",
      th_prov_models: "무료 모델 수",
      th_prov_cc: "신용카드 요구?",
      th_prov_ctx: "최대 컨텍스트",
      th_prov_url: "OpenAI 호환 Base URL",
      th_prov_best: "추천 베스트 모델",
      th_prov_key: "API Key 발급",

      // Accordion 2
      free_acc2_title: "🛠️ 인기 개발 도구별 1클릭 무료 API 연동 가이드",
      free_acc2_sub: "(Claude Code, Cursor, Codex, OpenCode, Aider)",
      tab_groq_cursor: "Cursor (Groq 무료 키)",
      tab_claudecode: "Claude Code (OpenRouter)",
      tab_codex: "Codex CLI (Groq)",
      tab_cmdcode: "CommandCode CLI (Ox Alpha)",
      tab_python: "Python (OpenAI SDK)",

      // Filters & Search
      lbl_filter_platform: "플랫폼:",
      plat_all: "전체",
      ph_free_search: "모델명, 정체, 제조사 검색… (예: GLM, Llama, 1M)",
      lbl_filter_category: "특기/분류:",
      cat_all: "전체",
      cat_coding: "💻 코딩 특화",
      cat_reasoning: "🧠 고난도 추론",
      cat_long_context: "📜 1M 대용량 컨텍스트",
      cat_lightweight: "⚡ 고속/경량",
      lbl_filter_safe_only: "🛡️ 학습 미사용(Safe/ZDR)만 보기",
      sort_intel_desc: "지능 지수 높은 순 (추천)",
      sort_coding_desc: "코딩 지수 높은 순",
      sort_context_desc: "컨텍스트 크기 큰 순",
      sort_name_asc: "모델 이름 가나다순",
      view_card: "🗂️ 카드 뷰",
      view_table: "📋 테이블 뷰",

      // Table Headers
      th_cat_name: "모델명 & 정체",
      th_cat_platform: "제공 플랫폼",
      th_cat_category: "분류",
      th_cat_intel: "지능 지수 (AA)",
      th_cat_coding: "코딩 지수 (AA)",
      th_cat_context: "컨텍스트",
      th_cat_privacy: "프라이버시 (학습 여부)",
      th_cat_limit: "요청 한도 / 비고",
      th_cat_links: "호출 및 링크",

      // Dynamic Card Labels
      lbl_true_identity: "💡 모델의 실체:",
      lbl_recommended_for: "🎯 추천 용도:",
      tag_safe_model: "🛡️ 학습 미사용 (Safe)",
      tag_train_model: "⚠️ 학습 활용 / 기여자",
      tag_general_cat: "🌐 범용 지능",
      btn_copy: "복사",
      btn_copied: "복사됨!",
      msg_no_free_models: "검색 조건에 맞는 무료 모델이 없습니다.",
      msg_no_free_hint: "필터를 초기화하거나 검색어를 변경해보세요.",
      msg_catalog_count: "조건에 맞는 무료 모델 <b>{count}개</b> 표시 중 (전체 {total}개)",
      msg_aa_intel_note: "※ 지능 점수는 Artificial Analysis 공인 Intelligence Index 기준입니다.",
      acc_toggle_open: "▼ 클릭하여 열기",
      acc_toggle_close: "▲ 닫기"
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
      // Skip template strings with un-interpolated variables
      if (text.includes("{") && text.includes("}")) return;
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

    // Check banner dismissed state
    try {
      if (localStorage.getItem("banner_dismissed") === "1") {
        const b = document.getElementById("topNoticeBanner");
        if (b) b.style.display = "none";
      }
    } catch(e) {}
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
