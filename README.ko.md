# OpenCode Go Model Value Frontier (가치 최적선 분석)

[🇺🇸 English](README.md) | **[🇰🇷 한국어](README.ko.md)**

> ⚠️ **개인 참고용 비공식 프로젝트**: 본 프로젝트는 개인 연구 및 편의를 위해 만들어진 비공식 도구입니다. 데이터는 공개 사이트 및 API에서 실시간/자동 스크래핑되므로 실제 제공업체의 최신 요금제나 제한 정책과 차이가 있을 수 있습니다. 가볍게 참고용으로만 활용해 주세요!
>
> 🤖 **100% AI 바이브 코딩**: 이 프로젝트는 AI(Google DeepMind Antigravity & Gemini)와 페어 프로그래밍(바이브 코딩)으로 빠르게 구축되었습니다. 재미와 실용성을 목적으로 만들었으니 감안하고 봐주세요! ㅎㅎㅎ
>
> 🎨 **디자인 및 시각화 출처 (솔직한 고백)**: [Terry Djony의 Best Model For Your Budget](https://bestmodelforyourbudget.terrydjony.com/)의 시각화 컨셉과 전반적인 Look & Feel을 솔직하게 상당 부분 차용(클론)하여 제작되었습니다. 원작자의 훌륭한 시각화 디자인에 깊은 감사를 표합니다.

---

## 📌 프로젝트 소개

**OpenCode Go** 공식 웹(`opencode.ai/go`)에 등록된 모델과 월간 한도(\$15, \$30, \$60), 5시간 롤링 요청 제한, `models.dev`의 API 정가, 그리고 `Artificial Analysis`의 벤치마크 지수를 결합하여 **어떤 모델이 진짜 가성비(파레토 최적)인지** 분석하는 대화형 대시보드입니다.

또한 **OpenCode Zen/Go, OpenRouter, CommandCode, Groq, Gemini** 등의 $0 무료 AI 모델 카탈로그(`free_models.html`)를 함께 제공합니다.

---

## 🎯 데이터 수집 파이프라인 (Data Pipeline)

1. **모델 목록 및 월간 한도 / 5시간 제한**:
   * 출처: [https://opencode.ai/go](https://opencode.ai/go) 및 [https://opencode.ai/v2/docs/console/go/](https://opencode.ai/v2/docs/console/go/)
   * 40개+ 공식 지원 모델, 월간 한도(\$15/\$30/\$60), 5시간 롤링 요청 제한
2. **모델별 토큰 비용**:
   * 출처: [https://models.dev/api.json](https://models.dev/api.json) (`opencode-go` provider)
   * 입력 토큰, 출력 토큰, 캐시 읽기 단가 및 3:1 Blended Price
3. **벤치마크 지수 (지능 및 코딩 점수)**:
   * 출처: [Artificial Analysis](https://artificialanalysis.ai/) Intelligence Index
4. **무료 모델 카탈로그**:
   * OpenCode Zen, OpenRouter 무료 API(`:free`), CommandCode, awesome-free-llm-apis 등

---

## 📊 OpenCode Go 티어별 가중치 계산식

월 \$10 구독 요금 기준:

$$\text{체감 단가 (Effective Price)} = \frac{\text{API Blended Price}}{\text{가치 배율 (Multiplier)}} = \text{API Blended Price} \times \left(\frac{\$10}{\text{티어 한도}}\right)$$

$$\text{월 쿼터 소모율 (Quota Burn \%)} = \frac{\text{API Blended Price}}{\text{티어 한도}} \times 100\% \quad (\text{100만 토큰당})$$

| 티어 (Monthly Cap) | 가치 배율 | 체감 단가 가중치 | 100만 토큰당 소모 | 대표 모델 |
| :--- | :---: | :---: | :---: | :--- |
| **\$60/월 티어** | **x6.0** | **÷ 6.0** (`× 0.167`) | $\frac{\text{Price}}{60} \times 100\%$ | GLM-5.3-Flash, MiMo-V2.6-Flash, Kimi K2.7 Code, MiniMax M3 등 |
| **\$30/월 티어** | **x3.0** | **÷ 3.0** (`× 0.333`) | $\frac{\text{Price}}{30} \times 100\%$ | Qwen3.8 Flash, Space Bunny, Hy4 preview 등 |
| **\$15/월 티어** | **x1.5** | **÷ 1.5** (`× 0.667`) | $\frac{\text{Price}}{15} \times 100\%$ | MiMo-V2.6-Pro, Grok 4.7/4.6, GPT 6 Luna, Kimi K3, Qwen3.8 Max 등 |

---

## 💡 주요 발견 및 추천 가이드

1. **주력 코딩 추천 모델**:
   * **GLM-5.3-Flash** (점수 41.8 / 체감 \$0.040 / 6,320건 per 5h): 준수한 성능과 여유로운 5시간 제한.
   * **MiMo-V2.6-Flash** (점수 37.9 / 체감 \$0.029 / 30,100건 per 5h): 대용량 작업용 극저비용 모델.
2. **고난도 추론 / 디버깅 추천**:
   * **MiMo-V2.6-Pro** (점수 46.3 / 체감 \$0.362 / 3,250건 per 5h): 동급 점수인 Grok 4.7(체감 \$2.000) 대비 쿼터를 1/5만 소모하면서 최적의 성능을 냄.
3. **피해야 할 모델**:
   * **GPT 6 Luna**: API 정가(\$0.20)만 보면 저렴해 보이지만, \$15 티어에 묶여 체감 단가가 \$0.133로 상승. 점수 41.8점인 GLM-5.3-Flash(\$0.040)보다 3배 이상 비싸 프론티어에서 탈락함.
   * **Kimi K3**: 점수 30.1점 대비 체감 \$4.000에 5시간 제한이 110건에 불과해 가성비 열위.

---

## 🚀 로컬 실행 & 자동화

### 1. 브라우저에서 열기
```bash
open index.html
# 또는 무료 모델 전용 가이드
open free_models.html
```

### 2. 최신 데이터 갱신 (터미널)
```bash
./update.sh
```

### 3. GitHub Actions & GitHub Pages 자동 배포
* 워크플로우 파일: `.github/workflows/deploy.yml`
* **자동 실행**: 매일 핀란드 낮 12시경 (09:37 UTC = 12:37 EEST / 11:37 EET). 미국 자정 시간대로 GitHub 서버가 가장 한산하며, 정각 대기열 혼잡을 피하기 위해 37분으로 지정.
* **수동 즉시 갱신**: GitHub 저장소 `Actions` 탭 → `Update Data and Deploy to GitHub Pages` → `Run workflow`
