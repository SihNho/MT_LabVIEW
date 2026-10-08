## PURPOSE FLOW (card chat-A1, user 2026-10-04) — this section OVERRIDES the dispatch and close rules above

User: *"사이클 기준은 작업지시로 훅을 걸지 말고 목적에 따라서 나누는게 맞는듯. 다만, 판단 사이클이 독자적으로 쪼갤 것이 아니라
싸이클 업무 배정 에이전트를 운용하여 유동성을 확보하는게 좋을듯"* → *"세션 규칙 설정은 그렇게 하고"*.

A cycle is ONE PURPOSE. You **set the purpose and judge what is handed back**; you do **not** dispatch build cards.
After you exit, the runner spawns an ASSIGNMENT session (claude-sonnet-5-5 high) that turns the purpose into `task/1`
cards for `material` / `material-opus-max` / `material-fable-low`, retries and escalates on the existing ladder, and runs
the pipeline. `guard_session` refuses any material dispatch from you (CYCLE_ROLE=judgement); `log-reader` stays available
for facts. So the bullets above about delegating every piece of material work, the six-dispatch cap and "Close the
cycle" do not apply to you in this flow.

**Your output is `tools/bench/next.json` = THIS cycle's purpose** (`next/1`, `cycle` = this cycle's number): `act` (what
the purpose is), `pass` (each item one checkable condition — the assignment session must show evidence for EVERY item,
and the runner refuses PURPOSE_MET otherwise), `plan` `{path, md5}`, `advances`/`unblocks`. Every card the assignment
session issues must stay inside this: its goal ids must meet yours, and a card that would write the plan file, a user rule
(CLAUDE.md, docs/user-rules.md, Requests.md, settings, agents, hooks), `tools/bench/memory_model.json` or change a memory
limit (X10 / MEMSTOP) is HANDED BACK to you unless your `act`/`pass` names it. Write those into the purpose when they are
part of it; leave them out when they are your decision to make later. Also rewrite STATUS.md's prose `## NEXT`.
**Do NOT run `retrospective.py` or `retro_due.py --close`** — the runner runs the retrospective when it is due, after the
purpose is met or the cycle closes. Write next.json, validate it, end your turn.

**DELIVERABLE FIRST — user 2026-10-08 ("두 가지 모두 적용하자", after cycles 147-149 spent 3 cycles and $130 for one
adopted file, mostly on gate clean-up):** when the purpose has a LabVIEW deliverable (a build / scratch / adopt), its
pass items come FIRST and no tooling item may gate it — a tooling item ("drain fp-…", "re-run the suites", "prove the
fix did not regress") runs AFTER the LabVIEW card, never "FIRST, ALONE" before it. Put a tooling item before the
deliverable only when the deliverable's own launch is refused by that very gate, and say so in `act`. **Never name
`tools/hooks/**` in a runner purpose:** hook edits are not made inside runner cycles (guard_assign refuses them even when
named); a hook false positive is queued with `tools/gate_fp.py` and the chat drains it between runs, with the user told.

**Lines at the end of this prompt:**
- `ASSIGN-RESULT <path>` — the previous assignment's `assign-result/1` (PURPOSE_MET with evidence, or HANDBACK). Judge it
  first: accept the evidence or not, then set the next purpose.
- `HANDBACK <path>` — you are in a HAND-BACK round of THIS cycle. Read that `handback/1` record (trigger a = an unexplained
  failure after its one retry, b = the same failure class twice, c = a card outside the purpose / plan / memory limit /
  user rule, d = a question only the user can answer, cap-time / cap-usd / backstop = the limits, no-result / session /
  purpose-unproven = what the session left) and its card rows, read the named result cards (not whole logs), and decide:
  (1) a REVISED `next.json` (new bytes) — the runner starts a new assignment round on it; (2) `next.json` UNCHANGED — the
  cycle closes and the next cycle starts from it; (3) a user question — append it to `decisions_pending.json`, set
  `stop_requested: true` and `blocked_by`, put `STOP` near the top of STATUS.md. At most
  `max_handbacks_per_cycle` (tools/bench/assign/assign_config.json) rounds per cycle.
