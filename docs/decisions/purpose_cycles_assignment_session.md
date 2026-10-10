---
name: purpose-cycles-assignment-session
description: "The user's 2026-10-04 decision — runner cycles are bounded by PURPOSE, not by a card count; an assignment session (Sonnet 5.5 high) dispatches the cards, the Opus judgement session only sets purposes and judges hand-backs, and hand-back is enforced by code"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-04T02:24:20.458Z
type: decision
status: in-force
date: 2026-10-04
source: memory/purpose_cycles_assignment_session.md
---

User, 2026-10-04: "사이클 기준은 작업지시로 훅을 걸지 말고 목적에 따라서 나누는게 맞는듯. 다만, 판단 사이클이 독자적으로
쪼갤 것이 아니라 싸이클 업무 배정 에이전트를 운용하여 유동성을 확보하는게 좋을듯", then after the cloud bench
(tools/bench/assignbench/report_cloud.md) "세션 규칙 설정은 그렇게 하고".

Bench basis (21 known-answer in-cycle decision points x 2 reps): Sonnet 5.5 high matched the right next action 0.74 at
$0.20 per decision; Opus 5.5 high 0.62 at $0.35. Every model was weak at handing a design question back to judgement
(Opus 0.17, Sonnet high 0.42), which is why hand-back is enforced mechanically.

## How I apply it

- The 6-card per-session cap (MAX_DISPATCHES, user 2026-09-26) is superseded as the cycle limit; limits are wall-clock
  and USD per assignment session (proposed 3 h / $60, user-changeable) plus a runaway backstop.
- Hand-back triggers are code, never the model's choice: unexplained failure after one retry, the same failure class
  twice, any change to the plan, memory limits or user rules, or a question only the user can answer.
- Do not move judgement work (purpose setting, design calls) into the assignment session, and do not reopen the model
  choice without a new bench or a user decision.
