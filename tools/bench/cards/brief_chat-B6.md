# Brief chat-B6 - bench for a CYCLE ASSIGNMENT AGENT (purpose-based cycles), to be run in a cloud session

User 2026-10-03/04: "사이클 기준은 작업지시로 훅을 걸지 말고 목적에 따라서 나누는게 맞는듯. 다만, 판단 사이클이 독자적으로
쪼갤 것이 아니라 싸이클 업무 배정 에이전트를 운용하여 유동성을 확보하는게 좋을듯" -> "1번은 클라우드 벤치 돌려볼 것".

Design under test: the judgement agent sets a cycle PURPOSE (next.json act + pass); an ASSIGNMENT agent issues task/1
cards, retries, escalates, runs offline prep beside a LabVIEW card, and ends the cycle when the purpose is met; it hands
back to judgement on an unexplained failure or a design question; no card-count cap (time/cost caps instead). Evidence it
matters: cycle 143 used exactly MAX_DISPATCHES=6 numbered cards and ended with session 3 ready but not launched.

## Build (locally, offline, on the decbench infrastructure - import, do not copy; tools/bench/decbench/decbench.py)
1. Cases from cycles 130-143 (tools/bench/cards/{cycle,task,result,next}_*.json, runner logs): ~20 decision points
   INSIDE a cycle. Each case = purpose + cards done so far (their result/1 objects, as they arrived) + minutes/USD used;
   question = the next action, from a FIXED menu: issue <card goal> | retry same card | escalate (Opus max / Fable low) |
   start offline prep beside | close cycle: purpose met | hand back to judgement: <reason>.
2. Known answers from what history PROVED (later cards/cycles), stated with the file:line that proves them; cases whose
   right answer history does not settle are dropped, not guessed. Include the cycle-143 cap case (right = launch s03),
   cases where hand-back was right (a real design question), and false-failure cases (S1's replay: 143-3/4/5).
3. Arms: claude-opus-5-5 medium, opus-5-5 high (= today's judgement agent, the baseline), claude-sonnet-5-5 medium and
   high. Score: action match (mechanical) + blind scorer for the free-text part, as decbench does; USD and minutes per case.
4. Stub dry run locally (decbench --stub) to prove the harness; NO real model cells locally.
5. Put the bench on a new branch assign-bench-20261004 (commit only the bench files + this card's outputs), push it to
   origin, and write a cloud prompt file tools/bench/assignbench/cloud_prompt.md that runs the full bench (reps 2) in the
   cloud and commits the report tools/bench/assignbench/report_cloud.md to that branch. The CHAT launches the cloud
   session (same way as the Sonnet bench, tools/bench/decbench/report_sonnet_cloud.md); you do not.

## Limits
labview none, no hardware, no GUI. Runner is stopped. Edit tool only. git commit + push of the bench branch allowed
(nothing else pushed). Return one result/1 JSON object.
