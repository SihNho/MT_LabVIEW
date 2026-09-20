---
type: reference
status: current
date: 2026-09-05
tags: [docs, benchmark]
---

# LabVIEW GUI 자동화 벤치마크 보고서 — 2026-09-04

목적: LabVIEW 코딩 툴킷에서 **GUI 조작이 불가피한 자리(t4: 화면 위치 파악)** 를 누가·어떻게 맡을지 근거를 만든다.
두 벤치를 돌렸다: (1) 오프라인 그라운딩 — 같은 스크린샷·같은 질문에 모델만 교체; (2) 라이브 클릭 — 같은
마이크로-op를 "COM 좌표 산술(모델 없음)" vs "Sonnet 비전 실행자"로 수행. 모델×effort 매트릭스는 **미실행**.

원시 데이터·스크립트·스크린샷 사본: `archive/bench-2026-09-04/` (이 폴더). 측정 스크립트는 그대로 재실행 가능.

## 1. 오프라인 그라운딩 벤치 (모델 교체, 알고리즘 고정)

**기준**
- 대상 19개: 다이어그램 노드 4(정답 = COM `report()` 좌표 + 창 오프셋, 산술), 팔레트 항목 5·메뉴 항목 5·다이얼로그 5
  (정답 = 이 세션에서 실제 클릭해 성공한 좌표, `tools/gui_actions.log`). 스크린샷 12장(1920×1080 11장, 1400×900 1장).
- 질문: "이 항목의 중심 픽셀 좌표는?" — 모든 모델에 동일 문장. 정답은 모델에 비공개(`ground_targets.jsonl`).
- 히트 판정("클릭이 착지했을까"): |dy| ≤ tol(노드 10–12, 메뉴 10, 팔레트 15, 다이얼로그 12–15) 이고 |dx| ≤ 종류별 여유(메뉴 80, 다이얼로그 30, 팔레트 18, 노드 tol).
- 호출 경로: Claude 3종 = 하위 세션 1개가 19개 일괄(Agent 도구 `model` 지정, effort 기본값); GPT = `codex exec -i`(ChatGPT 구독, API 키 없음); UI-TARS-1.5-7B = 로컬 Ollama, 줌 2패스, `--image` 오프라인.
- 지표: 히트율, px 오차 중앙값, 질의당 초, 질의당 토큰.

**결과**

| 그라운더 | 히트 | px 중앙값 | 초/질의 | 토큰/질의 | 종류별 |
|---|---|---|---|---|---|
| sonnet | 19/19 | 1.0 | 3.7 | 5704 | dialog 5/5 menu 5/5 node 4/4 palette 5/5 |
| opus | 19/19 | 1.0 | 4.4 | 5319 | dialog 5/5 menu 5/5 node 4/4 palette 5/5 |
| gpt | 17/19 | 2.0 | 5.9 | 0 | dialog 5/5 menu 5/5 node 2/4 palette 5/5 |
| uitars_warm | 16/19 | 5.7 | 4.7 | 0 | dialog 4/5 menu 5/5 node 2/4 palette 5/5 |
| uitars | 16/19 | 3.2 | 22.5 | 0 | dialog 4/5 menu 5/5 node 2/4 palette 5/5 |
| haiku_cal | 10/19 | 13.3 | 4.4 | 4073 | dialog 4/5 menu 5/5 node 0/4 palette 1/5 |
| haiku | 0/19 | 297.7 | 4.4 | 4073 | dialog 0/5 menu 0/5 node 0/4 palette 0/5 |
| sonnet_single | 1/1 | 1.0 | 5.3 | 68093 | menu 1/1 |

주석: `uitars`=콜드·경합 조건(다른 런 4개와 동시), `uitars_warm`=워밍·순차(공정 수치). `haiku`=원답(축소 좌표계), `haiku_cal`=이미지 크기별 최소제곱 보정 후(상한). `sonnet_single`=새 하위 세션에서 질의 1개만: 68,093 토큰 → **세션 기동 고정비 ≈ 60k 토큰**. GPT 토큰은 수동 표본(5,966)에서 추정, 하네스 파싱 실패로 표에는 0.

**해석**: 정밀도 Sonnet = Opus > GPT > UI-TARS ≫ Haiku. 메뉴·팔레트·다이얼로그(산술이 못 하는 곳)에서는 Haiku를 제외한 전부 ~100%. Haiku는 좌표 계약 보정 후에도 부적합. UI-TARS의 유일한 장점은 토큰 0; 워밍 시 4.7초로 속도는 대등하나 정밀도가 낮다(84%).

## 2. 라이브 클릭 벤치 (방법 비교; 모델 비교 아님)

**기준**
- 대상 VI: `claudeDev\GUIBENCH_v0.vi`(OpFP_v0 복사본, 한 화면). 트라이얼마다 `gscript.revert()`로 동일 출발.
- 마이크로-op: U1 노드 드래그 이동(+100,+50; `report()` 위치 차분으로 검증, ±6px) / U2 팔레트에서 Index Array를 지정 좌표에 배치(새 uid + 위치, ±12px) / U4 Property Node 항목 우클릭 → Change To Write(ExecState 1→0).
- 방법: M3 = 파이썬 스크립트, 좌표는 `report()` + 창당 1회 보정(스크린샷 1장), LLM 없음. vision-sonnet = 실행자 하위 세션(Sonnet, effort 기본), 스크린샷을 보고 위치 결정, COM 검증. 각 3회.
- 지표: 통과, 중앙값 초, 게이트 액션 수, 판독 스크린샷 수, px 오차.

**결과**

| 방법 | op | 통과 | 중앙값 초 | 액션 | 판독 스크린샷 | px |
|---|---|---|---|---|---|---|
| M3 | U1_move | 2/6 | 2.0 | 1 | 0 | 0.0 |
| M3 | U2_place | 3/3 | 8.5 | 5 | 0 | 6.1 |
| M3 | U4_menu | 3/3 | 3.4 | 2 | 0 | nan |
| vision-sonnet | U1_move | 3/3 | 9.7 | 1 | 1 | 0.0 |
| vision-sonnet | U2_place | 3/3 | 23.9 | 5 | 2 | 6.1 |
| vision-sonnet | U4_menu | 3/3 | 10.5 | 2 | 1 | nan |

주석: M3 U1은 6회 중 2회 통과 — 앞 3회는 노드 중심을 잡아 메서드 선택기가 열린 도구 결함(0/3), 헤더 잡기로 고친 뒤 2/3(첫 회는 창 활성화 직후 첫 마우스다운 소실; 사전 클릭 추가, 미검증). Sonnet 실행자 세션 합계: 157,088 토큰, 79 도구호출, 569초(9회; 회당 ≈17.5k 토큰·63초). M3 토큰 0.

**해석**: M3가 3–5배 빠르고 비용 0, 착지 정확도 동일. 단 **M3는 아직 일반 도구가 아니라 손으로 좌표를 박은 3개 케이스**이므로 "M3가 GUI를 얼마나 없애는가"의 판정은 도구 완성 후로 미룬다(사용자 지적 2026-09-04).

## 3. 세션 시간 분해 (트랜스크립트 기반, 9/1 이후, 30분↑ 공백 제외)

판단(도구 결과→다음 행동) 1.80 h / n=546 / 중앙값 7.8 s; 도구 대기 0.68 h. 3분 넘는 판단 공백 0건 → 비용의 정체는 긴 숙고가 아니라 **왕복 횟수**. 스크린샷 판독 139회(회당 ≈9 s + 캡처 5 s). COM 행 3건 ≈ 10분.

## 4. 결정 사항과 미결

- (2026-09-05 추가) GUI 실행자 모델·effort: **opus-low 기본, sonnet-low 예산 대안, Haiku 제외** — 근거는 §8 매트릭스.

결정: 실행자 비전 = Sonnet 5, 배치당 1세션(질의당 스폰 금지). UI-TARS 보관(오프라인 대량용). GPT(codex)는 세션 없을 때 단발 폴백. Haiku 제외. 다이어그램 객체는 산술(M3) — 도구 완성 후 판정.
미실행: **모델×effort 매트릭스**(셀 정의 6개 생성됨, 과제는 GUI 불가피 마이크로-op + 다이얼로그 판단으로 재정의 예정), 5px 터미널 정답 세트(라이브 `probe` 필요), Claude 단일 호출 지연(1건만 측정).
실패한 시도: UI-TARS `num_ctx` 요청 옵션 가속 — 2048은 HTTP 400, 4096은 질의당 180초(원인 미상), 원복. 35분 손실.

## 5. 재현 방법
```
py toolsench\ground_bench.py run --grounder gpt|uitars   # 오프라인, LabVIEW 불필요
py toolsench\ground_bench.py report
py toolsench\gui_bench.py m3 --trials 3                 # 라이브, GUIBENCH_v0 필요
py toolsench\gui_report.py
```
Claude 셀은 `tools/bench/EXECUTOR_TASK.md`를 하위 세션에 주고 결과를 `record_claude.py`/`gui_results.jsonl`로 기록.


## 6. 환경 (다른 환경에서 재현·비교할 때 대조할 것)

| 항목 | 값 |
|---|---|
| OS | Windows 10 Home 10.0.19045 |
| GPU | NVIDIA GeForce RTX 2060, 6144 MiB, driver 457.51 — UI-TARS 모델(≈6.0–6.3 GB)이 다 안 들어가 33–37% 레이어 CPU 오프로드 |
| Ollama | 0.33.2 (`ollama ps` 기준); 모델 `ui-tars-1.5-7b:latest` = UI-TARS-1.5-7B Q4_K_M GGUF + mmproj (mradermacher), 컨텍스트 기본 8192 |
| LabVIEW | 2026 (26.3.1f1), 단일 인스턴스, VI Scripting 활성 |
| Claude | claude-haiku-4-5-20251001, claude-sonnet-5, claude-opus-5 — Claude Code 하위 세션(Agent 도구 `model` 지정, effort 기본값); 메인 세션 모델은 세션 중 opus-5/fable-5.1 혼재 |
| GPT | OpenAI codex CLI 0.150.1 (ChatGPT 로그인, API 키 없음), `codex exec -i <png>` |
| Python | 3.10, pywin32, Pillow 10.3 (OpenCV 없음) |
| GUI 도구 | `tools/lv_gui.ps1`(스크린샷·클릭·probe), `tools/gscript.py`(COM op fleet), `tools/uitars_grounder.py` |
| 화면 | 1920×1080 단일 모니터, 100% 배율 — 픽셀 정답은 이 배율 기준 |

## 7. 다른 환경에서 재현하는 법

1. 전제: LabVIEW + VI Scripting, `labview-automation` 스킬 폴더(`lv_gui.ps1` 포함) 복사, Python 3.10 + pywin32 + Pillow,
   erdosmiller lv-scripting(VIPM), 선택: Ollama + UI-TARS 모델, codex CLI 로그인.
2. 오프라인 그라운딩(LabVIEW 불필요): `archive/bench-2026-09-04/`의 `ground_truth.jsonl`·`screenshots/`를 `tools/bench/`에 두고
   `py toolsench\ground_bench.py run --grounder gpt|uitars` → `report`. Claude 셀은 `ground_targets.jsonl`을 하위 세션에 주고
   답을 `record_claude.py <name> <answers.jsonl> <seconds> <tokens>`로 기록. **다른 해상도/배율이면 정답표를 새로 만들어야 함.**
3. 라이브 클릭(LabVIEW 필요): `GUIBENCH_v0.vi`(OpFP_v0 복사본)를 claudeDev에 두고 BD를 열어 창 rect를 고정한 뒤 스크린샷 1장으로
   `OFF`(diagram→screen 오프셋)를 보정하고 `py toolsench\gui_bench.py m3 --trials 3`; 비전 셀은 `EXECUTOR_TASK.md`를 하위 세션에.
4. 결과 표: `ground_bench.py report`, `gui_report.py`, `matrix_record.py report`.

## 8. GUI-executor 모델 × effort 매트릭스 (2026-09-05 밤샘 실행)

**질문.** GUI 클릭을 피할 수 없을 때, 실행자(executor) 자리에 어떤 모델·effort를 쓰는 것이
가장 싼가? 정확도가 같다면 토큰(비용)과 시간이 결정 기준(사용자 지정).

**고정.** 과제 = `tools/bench/EXECUTOR_TASK.md`(4개 마이크로-op × 3회: U1 노드 드래그, U2 팔레트에서
Index Array 배치, U4 우클릭 메뉴 Change To Write, U5 Ctrl+F Find 대화상자를 Cancel로 닫기),
대상 VI = `GUIBENCH_v0.vi`, 도구 = `lv_gui.ps1`(스크린샷/클릭) + `verify_op.py`(초기화/판정),
LabVIEW 2026, 같은 창 배치. 각 셀은 `claude -p --model M --effort E` 단발 세션 하나.
**변수.** 모델 4종(haiku, sonnet, opus, fable) × effort 5단계(low, medium, high, xhigh, max) = 20셀,
sonnet-medium은 반복 측정.

**판정 규칙(프로토콜 v2).** 트라이얼마다 `verify_op.py revert`(디스크에서 VI 되돌리기, BD 전면화,
시계 시작) → 셀이 스크린샷을 읽고 클릭 → `verify_op.py verify`가 COM으로 상태를 읽어 PASS/FAIL을
기록. U1 = Invoke 노드 위치 변화 (100,50)±6 px, U2 = 새 Index Array 정확히 1개, 목표 12 px 이내,
U4 = ExecState 1→0, U5 = Find 창이 있었다가 없어짐. 셀은 자기 트라이얼을 통과로 표시할 수 없다.
v1(셀 자기 보고)은 haiku가 미래 시각이 찍힌 가짜 라인을 답변에 써낸 것이 확인되어 폐기.

**측정 지표.** 검증 통과 수(/12), 셀 실행 wall time, `claude -p` JSON의 총 비용(list price),
turns, 출력 토큰, 기계 기록된 GUI 동작 수(`gui_actions.log`).

<!-- MATRIX_TABLE_BEGIN -->
### Model x effort matrix (protocol v2, verified by verify_op.py; n = attempts per cell)

| model | effort | pass /12 | U1 | U2 | U4 | U5 | min | cost $ | turns | out tok | GUI acts | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku | low | 2/12 | 2 | 0 | 0 | 0 | 9.8 | 0.94 | 91 | 25794 | 46 | 1 |
| haiku | medium | 3/12 | 3 | 0 | 0 | 0 | 6.8 | 0.55 | 63 | 16206 | 20 | 1 |
| haiku | high | 3/12 | 3 | 0 | 0 | 0 | 14.4 | 0.70 | 68 | 21531 | 32 | 1 |
| haiku | xhigh | 3/12 | 3 | 0 | 0 | 0 | 8.4 | 0.71 | 80 | 16736 | 25 | 1 |
| haiku | max | 3/12 | 3 | 0 | 0 | 0 | 9.4 | 0.86 | 86 | 24832 | 45 | 1 |
| sonnet | low | 12/12 | 3 | 3 | 3 | 3 | 15.8 | 3.16 | 110 | 24975 | 47 | 1 |
| sonnet | medium | 11.7/12 | 3.0 | 2.7 | 3.0 | 3.0 | 14.9 | 3.59 | 132.0 | 25816 | 45.7 | 3 |
| sonnet | high | 12/12 | 3 | 3 | 3 | 3 | 13.8 | 4.73 | 156 | 30333 | 45 | 1 |
| sonnet | xhigh | 12/12 | 3 | 3 | 3 | 3 | 13.6 | 5.10 | 156 | 33524 | 43 | 1 |
| sonnet | max | 12/12 | 3 | 3 | 3 | 3 | 20.6 | 5.72 | 169 | 65501 | 44 | 1 |
| opus | low | 12/12 | 3 | 3 | 3 | 3 | 9.3 | 3.53 | 66 | 14134 | 43 | 1 |
| opus | medium | 12/12 | 3 | 3 | 3 | 3 | 12.2 | 5.92 | 97 | 22935 | 44 | 1 |
| opus | high | 12/12 | 3 | 3 | 3 | 3 | 13.3 | 7.77 | 132 | 25209 | 43 | 1 |
| opus | xhigh | 12/12 | 3 | 3 | 3 | 3 | 13.3 | 7.06 | 115 | 27073 | 43 | 1 |
| opus | max | 12/12 | 3 | 3 | 3 | 3 | 11.3 | 4.84 | 80 | 22700 | 43 | 1 |
| fable | low | 12/12 | 3 | 3 | 3 | 3 | 10.3 | 9.95 | 83 | 17310 | 45 | 1 |
| fable | medium | 12/12 | 3 | 3 | 3 | 3 | 9.4 | 7.52 | 65 | 15639 | 43 | 1 |
| fable | high | 12/12 | 3 | 3 | 3 | 3 | 12.0 | 9.53 | 79 | 22213 | 54 | 1 |
| fable | xhigh | 11/12 | 3 | 2 | 3 | 3 | 9.2 | 9.84 | 77 | 24508 | 44 | 1 |
| fable | max | 12/12 | 3 | 3 | 3 | 3 | 27.1 | 18.63 | 113 | 63510 | 45 | 1 |

Pass = trial verified over COM by verify_op.py (position delta / new node / ExecState / window list); the cell cannot mark its own trial. cost $ = list-price API cost reported by `claude -p`; min = wall time of the cell run; turns = num_turns; GUI acts = gated lv_gui actions logged in the run window.

### Non-results (excluded from the table)

| cell | protocol | why |
|---|---|---|
| bench-gui-haiku-medium | v1-selfreport | INVALID: the agent registry served the STALE definition (100-loop VI task) although the GUI task was on disk;  |
| bench-gui-haiku-medium | v1-selfreport | STALE guard fired: registry still served the old definition in the same turn. 47.5k tokens = Haiku spawn fixed |
| bench-gui-haiku-low | v1-selfreport | protocol v1-selfreport |
| bench-gui-haiku-low | v1-selfreport | protocol v1-selfreport |
| bench-gui-sonnet-low | v2-verify_op | INFRA: cell backgrounded its first command and yielded (print-mode run ended after 2 turns); rerun queued |
| bench-gui-fable-xhigh | v2-verify_op | INFRA: revert hung, cell backgrounded it and yielded after 10 turns (print-mode run ended); rerun queued |
| bench-gui-fable-max | v2-verify_op | USAGE LIMIT: interrupted after 708 s at 04:40, rerun from scratch at 06:22 per protocol |
| bench-gui-fable-xhigh | v2-verify_op | ACCOUNTING LOST: 12/12 verified lines exist (gui_results, later tagged #prior) but no cost/time JSON; rerun |
| bench-gui-sonnet-medium | v2-verify_op | ACCOUNTING LOST (driver died mid-cell, 3rd time); rerun |
<!-- MATRIX_TABLE_END -->

**읽는 법과 주의.** n=1 셀이 대부분이라 ±1 트라이얼·±20 % 비용 차이는 잡음이다. cost는 캐시
읽기까지 포함한 API 정가이며 구독 요금과 다르다. 시간에는 셀의 사고·스크린샷 판독과 verify 왕복이
모두 들어간다. U1 1회차 실패(px_error 111.8 = 이동 0)는 창 활성화 직후 첫 마우스다운이 삼켜지는
현상으로 모델과 무관하게 나타날 수 있다.

**사건 기록(비결과 포함).**
- Haiku 셀 두 개(high, xhigh)가 LabVIEW를 강제 재시작했고, 세 셀(haiku-medium, fable-xhigh,
  sonnet-medium 반복)이 벤치 드라이버 프로세스를 `Stop-Process`로 죽였다. 원인은 프로젝트 훅
  `lv_stallcheck.ps1`이 셀 안에서도 실행되어 유휴 드라이버를 "정지된 COM 클라이언트, 작업을 멈춰라"
  라고 보고한 것. 훅을 `BENCH_CELL` 환경변수로 차단하고 과제에 "어떤 프로세스도 죽이지 말 것"을
  명시한 뒤 재실행. 드라이버 사망으로 비용 JSON을 잃은 두 셀(fable-xhigh 07:22, sonnet-medium 10:15)은
  트라이얼 12/12 검증 라인은 남아 있으나 비결과로 분류하고 다시 돌렸다.
- sonnet-low 1차와 fable-xhigh 1차는 첫 명령을 백그라운드로 돌리고 턴을 끝내 46 s/195 s 만에 종료
  (print 모드는 그 순간 실행이 끝남). `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`과 과제 문구로 차단 후 재실행.
- 04:40 fable-max 실행 중 세션 사용량 한도(리셋 06:20). 드라이버가 "session limit" 문구를 인식하지
  못해 대기 대신 오류로 넘어갔다 → 정규식 수정, `--start-at` 추가, 06:21 재실행(규칙: 중단된 셀은 처음부터).
- COM Run 180 s 무응답 3회(준비 단계 revert 2회, verify 1회). 키 입력·전면 창·open_panel 직후 호출·
  open_panel→revert 순서의 네 가설 모두 재현 실험에서 기각; 피어 검토(codex)도 "죽인 클라이언트" 설은
  근거 없음. 위의 셀 재시작 사건이 시간대와 겹쳐 가장 유력한 설명이 되었다.

**결론.**
- **Haiku는 실행자로 쓸 수 없다.** 5개 effort 전부 U1(드래그)만 통과(2~3/12), 팔레트·메뉴·대화상자 0.
  effort를 올려도 나아지지 않는다.
- **Sonnet·Opus·Fable은 effort와 무관하게 사실상 만점**(11~12/12). effort는 정확도가 아니라 비용·시간만
  올린다: sonnet-max 20.6분 $5.72, fable-max 27.1분 $18.63 (사고 토큰 2.5배).
- **만점 셀 중 최저 비용은 sonnet-low $3.16(15.8분)과 opus-low $3.53(9.3분, 66턴).** 시간까지 보면
  opus-low가 가장 유리하다: 가장 적은 턴으로 끝내고 sonnet-low보다 40 % 빠르며 비용 차이는 $0.37.
- **반복 편차**: sonnet-medium 3회 = 12, 11, 12 통과 / $3.95, 3.40, 3.43 / 13.2, 11.9, 19.5분. 통과 ±1,
  비용 ±15 %, 시간은 ±30 %까지 흔들리므로 n=1 셀 간 ±20 % 차이는 순위 근거가 못 된다.
- **트라이얼당 비용 ≈ $0.26~0.30(opus-low, sonnet-low)**, 1회당 45~80초. GUI 클릭 한 번이 이 값이라는
  뜻이므로 "스크립트 우선, GUI는 검증된 불가 지점에만"이라는 기존 결론은 그대로이고, 피할 수 없는
  클릭의 실행자는 **opus-low(기본) / sonnet-low(예산 대안)**, Fable은 계획자 자리에 둔다.


## 9. M3v1 — 데이터 좌표 클릭 툴킷 검증 (2026-09-05 13:xx)

**질문.** 벤치 §2의 M3(COM 위치 + 뷰포트 오프셋으로 좌표 계산, 스크린샷 0)를 벤치 전용 코드가 아닌
일반 도구(`tools/lvclick.py`, 기하 레지스트리 `docs/gui-geometry.json`)로 만들었을 때, 같은 4개
마이크로-op를 시각 실행자와 같은 판정 규칙으로 통과하는가. 피어(codex) 리뷰 반영: 두 객체
캘리브레이션(헤더 색 프로브), 팔레트 오프셋을 팝업 창 rect 기준으로, 메뉴는 (클래스, 항목, 검증기)
등록 삼중항만, 대화상자는 크기 검사 후 클릭.

| op | M3v1 pass | s/trial | GUI acts | screenshots | vision (opus-low) s/trial | vision (sonnet-medium) s/trial |
|---|---|---|---|---|---|---|
| U1_move | 3/3 | 2.4 | 1 | 0 | ~45 | ~27 |
| U2_place | 3/3 | 9.2 | 5 | 0 | ~60 | ~67 |
| U4_menu | 3/3 | 4.6 | 2 | 0 | ~45 | ~33 |
| U5_dialog | 3/3 | 7.4 | 2 | 0 | ~50 | ~40 |

시각 실행자 값은 §8 셀의 트라이얼 라인 평균(대략값). M3v1은 트라이얼당 2~9초, 토큰 0. 전체 과정에서
스크린샷 판독은 Find 대화상자의 Cancel 위치를 측정한 1회뿐이며(등록 좌표가 대화상자 밖이었음),
그 값은 레지스트리에 기록되어 이후 호출은 산술이다 — "모르는 기하는 비전으로 한 번 재고 레지스트리에
적는다"는 확장 경로의 첫 사례.

**부수 발견(재현 4/4).** `OpenFrontPanel(activate=True)` 뒤에 lv_gui `focus`(Alt 탭)가 오면 다음
COM Run이 캔버스 클릭 전까지 멈춘다(H5). activate=False면 멈추지 않는다(H6). gscript.open_panel의
기본값을 activate=False로 바꿈. 밤새 COM 정지의 나머지 절반이 이것이었다.
