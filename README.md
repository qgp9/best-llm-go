# OpenCode Go Model Value Frontier (가치 최적선 분석)

> **공식 opencode.ai/go 모델 카탈로그 및 한도 + models.dev API 단가 + Artificial Analysis 벤치마크 기반 파레토 프론티어 분석기**

[https://bestmodelforyourbudget.terrydjony.com/](https://bestmodelforyourbudget.terrydjony.com/)의 시각화 원리를 바탕으로, **OpenCode Go** 공식 웹(`opencode.ai/go`)에 등록된 모델과 월간 한도(\$15, \$30, \$60), 5시간 롤링 요청 제한, `models.dev`의 API 단가를 직접 가져와 가중치 프론티어를 분석하는 도구입니다.

---

## 🎯 데이터 수집 경로 (Data Pipeline)

1. **모델 목록 및 월간 한도 / 5시간 제한**:
   * 출처: [https://opencode.ai/go](https://opencode.ai/go)
   * 31개 공식 지원 모델 (`goModels` 카탈로그), 모델별 월간 한도(\$15/\$30/\$60) 및 5시간당 요청 제한(Est. requests / 5h)
2. **모델별 토큰 비용**:
   * 출처: [https://models.dev/api.json](https://models.dev/api.json) (`opencode-go` provider)
   * 입력 토큰, 출력 토큰, 캐시 읽기 단가 및 3:1 Blended Price
3. **벤치마크 지수 (지능 및 코딩 점수)**:
   * 출처: [Artificial Analysis](https://artificialanalysis.ai/) Intelligence Index

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

1. **일상 코딩 챔피언**:
   * **GLM-5.3-Flash** (점수 41.8 / 체감 \$0.040 / 6,320건 per 5h): 준수한 성능과 여유로운 5시간 제한.
   * **MiMo-V2.6-Flash** (점수 37.9 / 체감 \$0.029 / 30,100건 per 5h): 대용량 작업용 극저비용 모델.
2. **고난도 추론 / 디버깅 추천**:
   * **MiMo-V2.6-Pro** (점수 46.3 / 체감 \$0.362 / 3,250건 per 5h): 동급 점수인 Grok 4.7(체감 \$2.000) 대비 쿼터를 1/5만 소모하면서 최적의 성능을 냄.
3. **피해야 할 모델**:
   * **GPT 6 Luna**: API 정가(\$0.20)만 보면 싸 보이지만, \$15 티어에 묶여 체감 단가가 \$0.133로 올라감. 점수 41.8점인 GLM-5.3-Flash(\$0.040)보다 3배 이상 비싸 프론티어에서 탈락함.
   * **Kimi K3**: 점수 30.1점 대비 체감 \$4.000에 5시간 제한이 110건에 불과해 가성비 열위.

---

## 🚀 빠른 시작

### 1. 브라우저에서 바로 열기
```bash
open index.html
```

### 2. 데이터 최신 업데이트 (언제든 실행 가능)
OpenCode 공식 사이트나 models.dev에서 새로운 모델이나 가격 변동이 있을 때:
```bash
python3 update_data.py
```
