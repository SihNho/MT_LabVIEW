---
name: offline-prerun-and-error-list-before-labview
description: "The user's 2026-09-24 rules after the L7 stage failed 6 of 9 runs on problems knowable without LabVIEW — every stage script is dry-run and offline-pre-checked before any LabVIEW run, error/accumulator chains are copied from the original by rule, and every cycle starts by reading the bed's LabVIEW Error List through the GUI"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-24T08:53:41.377Z
type: decision
status: in-force
date: 2026-09-24
source: memory/offline_prerun_and_error_list_before_labview.md
---

# Offline pre-run before LabVIEW; read the Error List at cycle start (2026-09-24)

Overnight on 2026-09-23/24 the loop-1.7 split scripts failed 6 of 9 LabVIEW runs (about 49 minutes of LabVIEW
time, two to three times that in diagnosis, reviews and firefighter cycles). Every failure was knowable without
LabVIEW: Jev rows left undecided, a terminal the address rule could not reach, a plain Python type error. The user
decided, in a structure discussion:

> "순수 파이썬 버그 같은 경우는 드라이런을 강제해야할듯 · 오프라인 사전 실행 추가 필요 · 에러 누적 체인은 제안대로
> 변경 · 스크립트가 같은 이유로 실패하면 오프라인 사전 실행 · 사이클 시작하기 전에 LabVIEW 컴파일 에러 창은 반드시
> 확인해야할듯. GUI로 에러 내용 확인하고 각 에러 더블클릭하면 에러 위치로 이동해서 보여주거든"

## How I apply it

- A stage script never opens LabVIEW before a DRY-RUN of its whole Python path and an OFFLINE PRE-RUN passes:
  decision record complete, every row's terminal addressable from the graph JSON, every Jev row decided.
- Error-cluster (`error in`/`error out`) and accumulator chains are copied from the original's chain order by rule,
  not asked of Jev — there is nothing to judge, and asking produced low-confidence stops.
- The same script failing for the same reason sends it back through the offline pre-run before the next LabVIEW run.
- At every cycle start the bed's LabVIEW Error List is read through the GUI, each item double-clicked to its
  block-diagram location and recorded; a broken-by-design intermediate is checked as "errors == the rows left open".
- Later in the same discussion the user widened this into the working method: "미리 사전계획 해서 옮길 vi들 미리
  정리하고 만들 struct 미리 계산한 다음 그 결과 어떻게 될지 미리 예측 … Sequential하게 각 단계들을 시뮬레이션 하여
  temporary 파일로 저장한 후에 각 사이클의 finalized 플랜을 두는게 맞는듯." So a stage is never built by
  move → look → wire inside LabVIEW. It is simulated action by action on the graph (temporary graph file per step,
  symbolic ids for new objects), finalized when the simulated end state has computation_diff 0, then executed once
  with the real graph compared to the simulated one after every action. Cut sets and S1 partners are Python; Jev
  picks per-row mechanisms and ambiguous pairs; the LLM designs what moves where.
- The user does not know LabVIEW scripting jargon or my row labels (err_R, acc_L …): explain what a thing IS in the
  diagram before using its label.
