# 현재 조건 분석: 구현 및 검토 예시

2026-10-24 로컬 카탈로그와 Chromium에서 확인했다. 아래 수치는 해당 스냅샷의 계산 결과다. 원본 벤치마크·가격의 정확성이나 실제 작업 성능을 새로 검증했다는 의미는 아니다.

## 동작

- `data/frontier_analysis.js`의 순수 계산 함수가 그래프와 분석에 같은 Frontier를 제공한다. 제작사와 검색도 Frontier 계산 전에 적용한다.
- 비용 축, 범위, 학습 여부 필터, 배율, 최소 점수, 사용자 선택, 중복 접기 조건을 반영한다. `Frontier only`는 표시만 바꾸고 분석 근거는 유지한다.
- 가중 Frontier와 엄밀한 파레토 열위를 구분한다. 같은 모델 ID의 컨텍스트별 가격 구간도 별도 점으로 처리하며, 비싼 구간이 싼 구간의 Frontier 표시를 물려받지 않는다.
- 무료 모델은 별도 영역에서 수와 최고 관측 점수를 안내한다. 무료 표시는 외부 API 사용 가능성이나 실제 서비스 가용성을 보장하지 않는다.
- AI 문장과 모델 API 호출은 사용하지 않는다. 무료 페이지의 기존 AI 가이드와 두 페이지의 생성 요약 파일 의존을 제거하고, `update.sh`에서 요약 생성을 중단했다. 기존 생성기 및 Python 테스트는 보존했다. Console 수집용 키 전달도 유지한다.

## 실제 표시 예시

기본 조건: Go 범위, 체감 단가 축, 최소 점수 20, 학습 미사용 필터, 중복 접기, 기본 가중치 k=0.1.

- 유료 22개 중 Frontier 3개, 별도 무료 후보 10개.
- MiMo-V2.6-Flash: 체감 $0.02917/1M, 지능 지수 37.9.
- DeepSeek V4.1 Flash (Off-Peak): 체감 $0.03281/1M, 45.1점. 이전 단계보다 비용 1.125배, 점수 +7.2점.
- MiMo-V2.6-Pro: 체감 $0.3625/1M, 46.3점. DeepSeek 단계보다 비용 11.05배, 점수 +1.2점.
- 열위 사례는 같은 축에서 Kimi K3보다 DeepSeek의 비용이 $3.967/1M 낮고 점수가 1.5점 높다는 비교를 제시한다.

제작사를 Xiaomi로 제한하면 유료 후보 4개, Frontier 2개로 바뀐다. MiMo Flash → Pro는 체감 비용 12.43배에 지능 지수 +8.4점이다. 전체 시장의 DeepSeek을 이 조건의 비교 대상으로 끌어오지 않는다.

Go /task 축으로 바꾸면 Frontier가 4개다. MiMo-V2.5 → MiMo-V2.6-Flash의 체감 태스크 비용은 1.153배, 점수는 +11.9점이다. 최고점 MiMo Pro는 바로 이전 Frontier인 DeepSeek과 비교해 태스크 비용 2.711배, 점수 +1.2점으로 표시한다. 이 태스크 비용은 카탈로그의 AA 벤치마크 비용이며 사용자 작업당 실제 비용이 아니다.

## 재현과 검증

```bash
node --test tests/test_frontier_analysis.cjs
python3 -B -m unittest discover -s tests -v
CHROMIUM_BIN=/path/to/chrome node tests/check_frontier_ui.cjs
bash -n update.sh
git diff --check
```

고정 입력 테스트는 생성 카탈로그와 API 키 없이 실행된다. 브라우저 테스트는 로컬 실제 카탈로그로 다음을 확인한다.

- 5개 비용 축에서 그래프 마커·선과 분석의 Frontier ID 일치.
- 주요 필터, 사용자 선택, 검색 변경과 `Frontier only` 전후 근거 유지.
- 후보 없음·하나인 경우, 한국어·영어 전환, 제작사 선택 유지, `fk=0`, 좁은 화면의 긴 모델명.
- 생성 요약 요청 없음, 무료 페이지의 AI 박스 제거, 페이지 실행 예외 없음.

브라우저 검증은 Node 24와 로컬 Chromium으로 실행했으며 별도 npm 패키지는 필요 없다. 테스트 서버는 localhost에서 HTML과 공개 data 파일만 제공한다. 실제 GitHub Actions 실행이나 배포는 이번 변경에서 수행하지 않았다.
