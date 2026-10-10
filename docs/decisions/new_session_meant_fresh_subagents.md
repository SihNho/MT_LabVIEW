---
name: new-session-per-cycle-confirmed-cap-is-for-runner-only
description: "The user's 2026-09-29 clarification — a fresh JUDGEMENT session per cycle (the cycle runner's design) is what they want, and fresh sub-agents too; the per-session dispatch cap exists for runner cycle sessions, and its hitting the interactive chat was not their intent"
metadata:
  node_type: memory
  pinned: false
  originSessionId: aa054aba-9e4f-48b1-9e24-88ad783da19a
  modified: 2026-09-29T08:52:46.896Z
type: decision
status: in-force
date: 2026-09-29
source: memory/new_session_meant_fresh_subagents.md
---

On 2026-09-29 the chat hit `guard_session.py`'s 6-dispatch cap while delegating offline benchmarks, and the user
asked why the cap and the runner sessions exist. They first said they had pictured "fresh sub-agents after each
cycle" (`"내가 생각한 새 세션은 싸이클 종료 이후 서브 에이전트 새로 여는 걸 말한 것 같은데"`). After I explained the layers
(runner = Python script, judgement session = the Claude session it spawns per cycle, material sessions = sub-agents,
chat = this conversation), they confirmed: "그렇다면 판단 세션도 새로 가동하는게 맞음." So the runner's
one-fresh-judgement-session-per-cycle design matches their intent (origin: 2026-09-14 cost from growing context,
2026-09-17 "2번으로 가자" after a 15-hour session).

## How I apply it

- Keep the cycle runner spawning a fresh judgement session per cycle; do not propose a persistent judgement session.
- The dispatch cap is meant for runner cycle sessions; the interactive chat delegating offline work (benches,
  measurements) is not "carrying a second cycle". Scoping the cap to runner sessions was proposed on 2026-09-29 and
  awaits the user's go-ahead.
- When the user uses "session", say which layer I mean (runner script / judgement session / sub-agent / chat) —
  the ambiguity is what produced this detour.
