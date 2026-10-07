# Brief chat-A1 - purpose-based cycles run by an ASSIGNMENT session (Sonnet 5.5 high) with mechanical hand-back

User 2026-10-04: "사이클 기준은 작업지시로 훅을 걸지 말고 목적에 따라서 나누는게 맞는듯. 다만, 판단 사이클이 독자적으로 쪼갤
것이 아니라 싸이클 업무 배정 에이전트를 운용하여 유동성을 확보하는게 좋을듯" -> cloud bench -> "세션 규칙 설정은 그렇게 하고".
Bench (tools/bench/assignbench/report_cloud.md, 21 known-answer decision points x 2): Sonnet 5.5 high action match 0.74,
blind 0.714, $0.20/decision, 0 forbidden; Opus 5.5 high (today's judgement) 0.62 / 0.643 / $0.35. Weak spot for EVERY arm:
HANDBACK (Opus 0.17, Sonnet high 0.42) - so hand-back must be enforced by code, not left to the model.

## Design to implement (approved)
1. Cycle = one PURPOSE. The judgement session (Opus 5.5 high, unchanged) only sets the purpose (next.json act + pass, plan
   path+md5) and judges what is handed back; it does not dispatch build cards any more.
2. A new ASSIGNMENT session - claude-sonnet-5-5, effort high, a top-level `claude -p` spawned by cycle_runner.py with
   CYCLE_SESSION=1 (+ a role env var) - reads the purpose and issues task/1 cards to the existing material agents
   (material / material-opus-max / material-fable-low), retries, escalates on the existing ladder, runs offline prep beside
   a LabVIEW card (existing limits: <= 2 live, <= 1 touching LabVIEW), and ends with a result when every pass item is met.
   FIRST measure (external search + a local stub test) whether a subagent can itself use the Agent tool; the design above
   assumes the assignment session is top-level for that reason - keep it top-level unless measured otherwise.
3. MAX_DISPATCHES=6 is removed as the cycle limit. Limits instead, checked between cards: wall-clock 3 h and USD 60 per
   assignment session (config file, user-changeable), plus a large runaway backstop (e.g. 30 cards) in guard_session.
4. HAND-BACK is mechanical (a hook on the assignment session's Agent dispatch + the runner): the session cannot dispatch
   another card, and must exit with a handback record, when (a) a card FAILs with a first_fail that the existing
   classifiers (gateclass soft path, addrcheck address/format, errorlist_check by_design) do not explain, after its one
   retry; (b) the same failure class appears twice; (c) a card would change the plan file, a memory limit
   (memory_model.json / X10 / MEMSTOP), a user rule, or anything outside next.json's plan; (d) a card asks a question
   only the user can answer (decisions_pending). The runner then spawns a judgement session with the handback record.
5. Runner flow: judgement(purpose) -> assignment -> [handback -> judgement -> assignment ...] -> purpose met -> retro_due /
   retrospective as today -> next cycle. Motor limits, Error List hook, LabVIEW-close hook, STOP marker, graceful end,
   usage-limit protocol, report HEARTBEAT lines: all unchanged (add ASSIGN / HANDBACK lines to the runner log).

## Do
Implement in tools/cycle_runner.py, tools/hooks/guard_session.py, a new .claude/agents or prompt file for the assignment
session, config in tools/bench/; self-tests with a stub claude (purpose met; each hand-back trigger a-d; time and USD caps;
backstop; existing cycle_runner/guard_session self-tests green or explained). NO real runner run (the runner stays
stopped). Do NOT edit tools/protocol.py, guard_bash.py, guard_peer.py, guard_cycle.py, stage_prerun.py or
.claude/settings.json (a parallel card chat-E3 owns them); if a schema change is needed, add a new schema file under
docs/protocol/ and note it. Do NOT edit CLAUDE.md (the chat does). Commit only your own files by explicit path.
Edit tool only. Return one result/1 JSON object.
