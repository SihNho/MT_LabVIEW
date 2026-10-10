# Card chat-X10 - GPT vs Claude benchmark on the SAME material cards (subscription decision 2026-10-16)

User 2026-10-11: "사실 이 모든 시작은 GPT와 클로드 둘 사이에 벤치를 돌려보는게 목적이었지" -> "진행". The user decides after
2026-10-16 which subscription to hold for a month (Claude Max 20x + ChatGPT Plus now; options include Max 5x + ChatGPT
Pro, docs/decisions/backend_agnostic_project_goal.md). Claude and GPT have EQUAL weight. Agreed measures (discussion
token-efficiency-01): same conditions, success, time, errors, retries, tokens read, and weekly usage % per unit of work.
No LabVIEW, no hardware: offline cards only. Read docs/script-writing.md; new scripts carry the header block at the TOP.

## Reuse, do not rebuild
The material replay bench already exists: tools/bench/matbench/ (report_v1.md; its driver and task set T1-T6; each task
is a replayed real card with a fixed start point and a scoring key). Read it first and ADD a Codex arm to the same driver
(shared code, not a copy). If a task needs LabVIEW, drop it and say so.
- Claude arm: what matbench used for the current default material model (claude-opus-5-5, effort high), same as before.
- GPT arm: `node <codex.js> exec --json --skip-git-repo-check -m gpt-6.1-sol -c model_reasoning_effort="high"
  -s danger-full-access -C <the task's isolated start directory> -` (codex.js: tools/debate_relay.py codex_js();
  full access per docs/decisions/codex_sessions_run_full_access.md; the trusted project hooks guard it). The GPT arm gets
  the SAME task text and the same start point; give it docs/START.md as its start instruction (it reads AGENTS.md itself).
- Each task x arm x 2 repeats if the time allows (matbench used 2); every call bounded (<= 20 min) under bgrun.

## Measure per run
score by matbench's own key (blind: write outputs as A/B with a recorded random mapping before scoring), wall minutes,
retries / failed tool calls, tokens (Claude: usage from the json result; GPT: codex json token_count events), cost
(Claude total_cost_usd; GPT: none - record tokens), and the PLAN-LIMIT movement:
- GPT: the `rate_limits` primary/secondary used_percent in codex json token_count events, first vs last of each run;
- Claude: no per-run plan % in claude -p output - record tokens and USD; the chat reads the Claude weekly % before and
  after the whole bench and reports it separately (state this limitation).
Any hook refusal of a GPT tool call: quote it from tools/hooks/guardcore.log (it is data: a missing allowance or a real
block), never work around it.

## Output
Return the full report as TEXT (sub-agents cannot write report files; the chat writes tools/bench/matbench/report_x10.md):
per task x arm x repeat: score, minutes, retries, tokens, $ / limit-%; totals per arm; what the numbers do not show
(task age - T1-T6 are September cards; n; one model setting each; scorer). Commit the driver change, raw outputs and
logs under tools/bench/matbench/.
