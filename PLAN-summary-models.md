# AI 요약 — 구현 및 재검증 기록

검증일: 2026-10-18. 이전 문서의 성공 표시와 기존 생성 파일은 증거로 사용하지 않았다.
아래 결과는 이 환경에서 직접 관측한 표본이며 향후 가용성·성공률을 보장하지 않는다.

## 최종 동작

- 기본 체인: `go:muse-spark-1.3-contributor` → `nim:z-ai/glm-5.3-flash` → `go:glm-5.3-flash` → `go:mimo-v2.6-flash` → `go:deepseek-v4.1-flash`.
- Muse는 Go `/responses`, NIM 및 Go 백업은 `/chat/completions`로 직접 호출한다. 두 프로토콜 모두 출력 상한은 8,000토큰이다. 실제 소모량과는 다르다.
- `OPENCODE_API_KEY` 하나를 사용한다. 환경변수가 `.env`보다 우선한다. `SUMMARY_MODELS`, 레거시 `SUMMARY_MODEL`, `SUMMARY_BASE_URL`, `SUMMARY_SESSION_ID`, `SUMMARY_NIM_CONN`, `SUMMARY_NIM_KEY`를 유지한다. 알 수 없는 경로 접두사는 설정 오류다.
- NIM 연결 ID는 고정하지 않는다. Console provider 배열에서 `configKey`와 `enabled: true`로 유일한 연결을 찾는다. 명시적인 `SUMMARY_NIM_CONN`도 지원한다.
- Linux CI의 절대 타이머로 요청의 헤더와 본문 전체를 90초로 제한한다. 네트워크 오류·타임아웃·429·5xx만 한 번 재시도한다. 전체 생성은 15분으로 제한한다.
- 응답 종료 상태와 본문을 따로 검증한다. 잘림·잘못된 JSON·공백 요약·잘못된 스키마·언어별 500자 초과는 실패다. 문자열 자르기나 JSON 복구는 하지 않는다.
- 매번 빈 결과에서 시작한다. 실패한 세트는 이전 내용도 제거한다. 키 없음·전체 실패는 JSON과 JS 모두 빈 객체다. 모델 실패는 배포를 막지 않지만 입력·저장 오류는 작업을 실패시킨다.
- 두 출력 파일을 모두 임시 파일에 준비한 뒤 파일별로 교체한다. 두 파일을 묶은 원자적 교체는 아니다. 중간 교체 오류가 나면 CI가 실패해 배포되지 않는다.
- 세트 ID와 `{title, ko, en}` 인터페이스는 유지했다. 가격 미상 정렬·표현, Go 페이지 요약의 언어 변경 누락도 수정했다.

## 새로 확인한 API 증거

- `GET https://opencode.ai/console/api/providers`: 실제 응답은 배열이다. `console-nvidia` 연결이 활성 상태였다. 이 응답에는 모델별 목록이 없으므로 특정 모델 활성 여부를 목록 조회만으로 주장하지 않는다. NIM의 실제 생성 성공으로 대상 모델 접근을 확인했다.
- Muse: `https://opencode.ai/inference/go/openai/v1/responses`에서 실제 요약 프롬프트 3회 통과(3.4 / 5.1 / 5.8초).
- Muse Chat Completions: HTTP 400과 `ModelProtocolUnsupported`를 직접 확인했다.
- Muse 세션 헤더 생략: HTTP 400. 실제 생성 성공 요청에는 `x-opencode-session`을 포함했다.
- Muse 1,500토큰 실험: `status=incomplete`, `reason=max_output_tokens`; 출력 1,500토큰 중 reasoning 1,497토큰. 기존 한도가 부족한 사례를 재현했다.
- NIM: discovery로 얻은 `https://opencode.ai/inference/custom/<connection-id>/chat/completions`에서 8,000토큰 상한으로 3회 통과(139.8 / 61.2 / 41.4초). 이는 최종 절대 타이머 보강 전 표본이다. 최초 구현은 소켓 타임아웃만으로 헤더+본문 총 90초를 보장하지 못했다. 이 수치를 요청별 90초 준수 증거로 사용하지 않는다.
- NIM 1,500토큰 실험: 36.4초 후 `finish_reason=length`; completion 1,500토큰 모두 reasoning. 새 검증기는 이를 `response-length`로 거절했다. 기존 JSON 오류의 한 원인 후보인 토큰 부족은 재현했지만, 과거 `Unterminated string` 사례 자체의 원인은 확정하지 않았다.
- 최종 절대 타이머 코드의 NIM 8,000토큰 메타데이터 실험: 첫 요청이 정확히 90.0초에 타임아웃되어 한 번 재시도한 뒤 총 171.6초에 성공했다. `finish_reason=stop`, completion 1,634토큰 중 reasoning 1,304토큰, ko/en 각 309/467자였다. 요청당 상한과 호출 전체 시간은 구별해야 한다.
- 최종 코드의 NIM 추가 3표본은 171.6 / 80.7 / 54.2초에 모두 통과했다. 첫 표본은 재시도를 포함한다. 일부 추가 probe는 동시 실행되었으므로 직렬 지연 벤치마크나 안정성 보장으로 해석하지 않는다.
- Go 백업 강제 호출: GLM 4.8초, MiMo 15.1초, DeepSeek 7.3초에 모두 유효한 ko/en JSON을 반환했다.

## 최종 검증

- 실제 파이프라인의 `/usr/bin/python3`로 9세트 전체 생성: 9 성공 / 0 실패. 전부 Muse 사용, 세트당 3.7~7.4초.
- 생성 파일의 9개 ID, ko/en 스키마, 언어별 500자 제한, JSON/JS 내용 일치를 확인했다. 생성 데이터는 기존처럼 Git 제외 대상이다.
- 오프라인 회귀 테스트 14개 통과: 프로토콜별 응답, 잘림, 빈 값, 잘못된 JSON, 토큰 한도, 가격 정렬, 재시도, 백업 전환, discovery, 전체 시간 제한, 오래된 결과 제거, 입력·저장 오류.
- 실제 Chromium에서 Go 3세트와 무료 6세트를 각각 선택해 한국어·영어 표시를 확인했다. 두 페이지에서 누락 요약 숨김과 복원 후 재표시도 통과했다.
- CI에 오프라인 테스트 단계를 추가했다. 로컬 셸 구문 및 `git diff --check`도 통과했다. 커밋·푸시·배포는 수행하지 않았다.

재현 명령:

```bash
/usr/bin/python3 -B -m unittest discover -s tests -v
/usr/bin/python3 -B build_summaries.py
CHROMIUM_BIN=/path/to/chrome node tests/check_summaries_ui.cjs
bash -n update.sh
git diff --check
```

브라우저 테스트는 Node의 내장 WebSocket을 사용하며 이 환경에서는 Node 24로 실행했다. 별도 npm 패키지는 필요 없다. 테스트 서버는 localhost에만 열고 HTML 및 공개 data 파일만 제공한다.

## 남은 한계

- NIM은 생성 성공과 별개로 지연 편차가 크다. 작은 표본만으로 안정화 완료라고 표현하지 않는다.
- 입력 카탈로그의 원본 벤치마크·가격 전체는 이번 검증 대상이 아니다.
- 실제 GitHub Actions 및 공개 Pages 배포는 실행하지 않았다.
