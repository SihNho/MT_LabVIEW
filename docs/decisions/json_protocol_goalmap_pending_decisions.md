---
name: json-protocol-goalmap-pending-decisions
description: "The user's 2026-09-24 decision — every channel between sessions (runner, judgement, material, log-reader, peers, scripts) speaks a JSON card protocol with flags enforced by hooks; every task and NEXT names the goal-map requirement/milestone it advances; pending user decisions live in one JSON list the chat shows at every report"
metadata:
  node_type: memory
  pinned: true
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-25T11:22:59.142Z
type: decision
status: in-force
date: 2026-09-25
source: memory/json_protocol_goalmap_pending_decisions.md
---

# JSON cards between sessions, a goal map, and a pending-decisions list (2026-09-24)

The user saw background briefs and returns that were "필요 이상으로 길게 나열" and asked to standardise inter-session
communication and use flags ("세션간의 통신 규약을 규격화하면 시간이나 에러를 크게 줄일 수 있지 않을까 … 플래그도 적극
활용하고"), then chose "전부 적용, JSON". When I pointed out that no device steers cycles toward the overall goal (the
outcome review repeated the same five verdicts nine times with no effect), they approved: "목표지도 넣는 것 아주 유효한
아이디어. 규약 필드 추가 역시 유효함. 4번 사용자 결정도 이렇게 구현하여 적용하도록 하자."

Design: `docs/session-protocol.md` (channels C1–C7), schemas in `docs/protocol/`, validator `tools/protocol.py`,
goal map `docs/goalmap.json`, pending decisions `tools/bench/decisions_pending.json`.

## How I apply it

- A brief to a sub-agent is a `task/1` card file; the prompt is one line pointing at it. Prohibitions are FLAGS
  (labview, gui, hardware, run_vi, write, status_edit, git_commit, peers) that hooks enforce, never sentences.
- A sub-agent's final message is a `result/1` JSON object (PASS/FAIL/BLOCKED, gates, artefacts, ≤10 facts, ≤3 open).
- Scripts end with one `RESULT {...}` line; machinery reads only that line, never scans log text.
- Every `task/1` and `next/1` names `advances` (goal-map ids) or, for tooling, the milestone it `unblocks`.
- Questions only the user can answer go into `decisions_pending.json`; I show the open items at every cycle report
  and whenever the user asks for status. Leaving them unreported is the `decision-starved` fault.
- The outcome-review steering question was deferred by the user to the run-verification discussion (item 3).
- 2026-09-25 verification found that resuming a sub-agent with SendMessage bypassed the per-session dispatch cap;
  `guard_session` now counts SendMessage. One card = one session; a follow-up is a new card and a new dispatch.
- Before the runner resumes after a day of tooling, run the full verification (all self-tests, hook payload
  checks, doc lint, ingest) and fix to green first — the user asked for exactly this ("규율 및 훅을 lint … 검증한
  이후 러너 재개"); the first pass found 11 failing self-tests including a regressed retry cap.
