# OpenCode Go Model Value Frontier (Pareto Analysis)

**[🇺🇸 English](README.md)** | [🇰🇷 한국어](README.ko.md)

> ⚠️ **Personal Sandbox / Reference Only**: This is an unofficial tool created purely for personal research and reference. Data is dynamically scraped from public sources and APIs. Pricing, allowances, and rate limits may differ from actual production terms or change at any time. Use at your own risk!
>
> 🤖 **100% Vibe-Coded with AI**: This entire project was built and rapidly iterated through AI vibe-coding with Google DeepMind Antigravity & Gemini. Take everything with a grain of salt! ㅎㅎㅎ
>
> 🎨 **Design & Look-and-Feel Attribution (Honest Confession)**: The visualization concept and the overall look-and-feel were heavily inspired by (and frankly, largely cloned from) Terry Djony's wonderful project: [Best Model For Your Budget](https://bestmodelforyourbudget.terrydjony.com/). Huge thanks and full credits to the original author for the brilliant aesthetic and Pareto frontier visualization!

---

## 📌 Overview

An interactive Pareto frontier analyzer that evaluates **OpenCode Go** (`opencode.ai/go`) official models against their monthly allowances (\$15, \$30, \$60), 5-hour rolling request limits, raw API pricing from `models.dev`, and intelligence benchmark scores from `Artificial Analysis`.

It also includes a dedicated, searchable **Free AI Models Guide** (`free_models.html`) covering OpenCode Zen/Go, OpenRouter, CommandCode, Groq, Google Gemini, and 30+ free API providers.

---

## 🎯 Data Sources

1. **Model Catalog & Monthly Allowance / 5h Limits**:
   * Sources: [opencode.ai/go](https://opencode.ai/go) and [opencode.ai/v2/docs/console/go/](https://opencode.ai/v2/docs/console/go/)
   * 40+ official models, monthly allowance caps (\$15 / \$30 / \$60), and 5-hour rolling request limits.
2. **Token Pricing**:
   * Source: [models.dev/api.json](https://models.dev/api.json) (`opencode-go` provider)
   * Prompt, completion, cache read prices, and 3:1 blended price.
3. **Benchmarks (Intelligence & Coding)**:
   * Source: [Artificial Analysis](https://artificialanalysis.ai/) Intelligence Index & Coding Index.
4. **Free LLM API Catalog**:
   * OpenCode Zen/Go, OpenRouter (`:free` endpoints), CommandCode, and `awesome-free-llm-apis`.

---

## 📊 OpenCode Go Value Calculation Formula

Assuming the standard \$10/month Go subscription:

$$\text{Effective Price} = \frac{\text{API Blended Price}}{\text{Value Multiplier}} = \text{API Blended Price} \times \left(\frac{\$10}{\text{Tier Allowance}}\right)$$

$$\text{Monthly Quota Burn \%} = \frac{\text{API Blended Price}}{\text{Tier Allowance}} \times 100\% \quad (\text{per 1M tokens})$$

| Tier (Monthly Cap) | Value Multiplier | Effective Cost Weight | Quota Burn / 1M Tokens | Representative Models |
| :--- | :---: | :---: | :---: | :--- |
| **\$60/mo Tier** | **x6.0** | **÷ 6.0** (`× 0.167`) | $\frac{\text{Price}}{60} \times 100\%$ | GLM-5.3-Flash, MiMo-V2.6-Flash, Kimi K2.7 Code, MiniMax M3 |
| **\$30/mo Tier** | **x3.0** | **÷ 3.0** (`× 0.333`) | $\frac{\text{Price}}{30} \times 100\%$ | Qwen3.8 Flash, Space Bunny, Hy4 preview |
| **\$15/mo Tier** | **x1.5** | **÷ 1.5** (`× 0.667`) | $\frac{\text{Price}}{15} \times 100\%$ | MiMo-V2.6-Pro, Grok 4.7/4.6, GPT 6 Luna, Kimi K3, Qwen3.8 Max |

---

## 💡 Key Takeaways

1. **Primary Coding Drivers**:
   * **GLM-5.3-Flash** (Score 41.8 / Effective \$0.040 / 6,320 requests per 5h): Solid performance with generous rate limits.
   * **MiMo-V2.6-Flash** (Score 37.9 / Effective \$0.029 / 30,100 requests per 5h): Ultra-low burn rate for high-volume tasks.
2. **Heavy Reasoning & Complex Tasks**:
   * **MiMo-V2.6-Pro** (Score 46.3 / Effective \$0.362 / 3,250 requests per 5h): Matches Grok 4.7 performance while burning only ~1/5 the quota.
3. **Models to Avoid on Go**:
   * **GPT 6 Luna**: Raw API price seems cheap (\$0.20), but restricted to the \$15 allowance (x1.5 multiplier), driving effective cost up to \$0.133. Beaten soundly by GLM-5.3-Flash (\$0.040, score 41.8).
   * **Kimi K3**: Low score (30.1) but high effective cost (\$4.000) with strict 110 requests / 5h limit.

---

## 🚀 Quick Start

### 1. Open Directly in Browser
```bash
open index.html
# Or open the Free AI Models Catalog
open free_models.html
```

### 2. Update Data Manually
```bash
./update.sh
```

### 3. Automated Daily Deployment via GitHub Actions
* Workflow file: `.github/workflows/deploy.yml`
* **Schedule**: Daily at 09:37 UTC.
* **Manual Run**: GitHub Actions tab → Select `Update Data and Deploy to GitHub Pages` → Click `Run workflow`.
