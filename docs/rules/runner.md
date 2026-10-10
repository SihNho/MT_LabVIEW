---
type: rules
status: current
date: 2026-10-10
tags: [rules, runner, sessions, models]
---

# Rules - the runner, sessions, roles and models

Restated briefly from `docs/rules/CLAUDE-full-2026-10-10.md` (cited ranges = full wording and quotes). Session
protocol details: `docs/session-protocol.md`; runner details: `docs/d1/runner.md`.

## Turns and cycles

- **Fewer turns: one LabVIEW batch = one runner = one notification** (2026-09-14). The burn is turns x context. Chain
  build -> test -> bookkeeping in one Python runner under one `bgrun`; dispatch the peer review and prepare the fix in
  the same turn; read logs with a targeted grep; never re-read what is in context. `docs/rules/CLAUDE-full-2026-10-10.md:280-288`
- **Session = one cycle, enforced by a runner** (2026-09-17). `tools/cycle_runner.py` spawns a fresh `claude -p`
  judgement session per cycle (model pinned by id, `claude-opus-5-5`, effort per the model table below; the alias
  `opus` is no longer used), which reads STATUS + the current plan only, runs ONE cycle, exits; the runner checks the
  exit and NEXT and spawns the next. Needs Claude Code >= 2.1.280. `docs/rules/CLAUDE-full-2026-10-10.md:289-295`
- **Purpose flow is the default (2026-10-04):** a cycle is ONE PURPOSE. The judgement session (Opus 5.5 high) writes
  the purpose (`next.json` act + pass) and judges hand-backs; it dispatches no build cards. An ASSIGNMENT session
  (`claude-sonnet-5-5` high, spawned by the runner) issues cards, retries, escalates, runs the pipeline and ends when
  every pass item has evidence. **Hand-back to judgement is CODE:** `tools/hooks/guard_assign.py` stops dispatch on an
  unexplained failure after one retry, the same failure class twice, a card outside purpose/plan/limits/user rules, or
  a question only the user can answer. Limits per round: 3 h and $60 (`tools/bench/assign/assign_config.json`), a
  30-card backstop, process-level hard stops. `docs/rules/CLAUDE-full-2026-10-10.md:296-306`
- **Deliverable first; hooks never in a runner cycle** (2026-10-08): a purpose's LabVIEW deliverable card runs before
  any tooling card unless that gate refuses the deliverable's launch; `tools/hooks/**` is never changed by a runner
  card (`guard_assign` `never_in_runner_globs`) - hook false positives are queued and drained by the chat between
  runs. **Stuck -> Claude-GPT discussion** (2026-10-09, PD382): on `HANDBACK-LIMIT` or a firefighter trigger the
  runner holds a discussion before the next cycle (`tools/debate_loop.py`, <= 6 rounds, <= 40 min); agreed items
  become a `steer/1` card the judgement session follows or refuses with evidence; `user_needed` items go to
  `decisions_pending.json`; the firefighter rung still runs after it (`docs/debate.md`). `docs/rules/CLAUDE-full-2026-10-10.md:307-317`
- **Runner stops and caps.** The six-dispatch cap applies only to `--flow legacy`. Stop conditions: a `STOP` marker in
  STATUS.md (written by the user), the same failure two cycles running, the usage-limit rule. `guard_session.py`
  refuses material dispatches after the retrospective and above `MAX_DISPATCHES` in RUNNER sessions only
  (`CYCLE_SESSION=1`); the chat has no dispatch cap and no context bound (`CHAT_CONTEXT_LIMIT = None`, it relies on
  compaction; keep `docs/chat-handoff.md` current); the Workflow tool counts as one dispatch; 3 offline prep cards may
  run beside a LabVIEW card; at most 2 cards live, at most one touching LabVIEW. A ROUTINE runner end (budget / cycle
  count) starts the next runner automatically (`tools/runner_supervisor.py`). **The interactive chat is for talking
  with the user only** - it answers from STATUS and the latest retrospective, redirects by editing STATUS NEXT/STOP,
  and never runs a cycle itself. Every cycle plan carries a `## Pre-decided` section (`doc_lint` warns).
  `docs/rules/CLAUDE-full-2026-10-10.md:318-333`
- **Firefighter cycles, decided by the runner from bgrun logs:** the same recipe ending `rc != 0`/`TIMEOUT` in two
  consecutive cycles, or the SAME MISTAKE under another name (same first failing GATE line, a renamed recipe, or a
  retrospective carrying `VIOLATION: repeated-failure-class`) => the next cycle is a firefighter. Model per the model
  table: ONE Opus max cycle, then `RUNNER STOP` and a user decision (the old fable low -> fable medium ladder is
  replaced). Every other rule holds inside it. Self-test `tools/bench/selftest_cycle_runner_ff.py`.
  `docs/rules/CLAUDE-full-2026-10-10.md:334-346`
- **A deadline ends the runner BETWEEN cycles, never mid-cycle** (2026-09-21): `--budget-min` is checked only between
  cycles; the outer `bgrun --max-min` is a last resort set well above budget + the longest cycle (e.g. 720).
  `docs/rules/CLAUDE-full-2026-10-10.md:347-347`
- **`## NEXT` is written before the retrospective is launched - mechanical:** the runner snapshots NEXT's md5
  (`tools/bench/next_snapshot.md5`); `guard_bash.py next_gate()` refuses `retrospective.py` while NEXT is unchanged.
  `docs/rules/CLAUDE-full-2026-10-10.md:348-348`

## Judgement vs material

- **Split sessions by JUDGEMENT vs MATERIAL** (2026-09-15, re-issued 2026-09-16). MATERIAL (its own session):
  measuring API facts, writing/running recipes on verified patterns, log greps, bookkeeping, dispatching peers,
  extracting facts from a failed run. JUDGEMENT (the scarce model): design decisions, what to accept from a review,
  rule-1a calls, diagnosis when hypotheses diverge, designing the discriminating experiment. **Failure budget = 2**:
  a material session that fails twice stops and hands over. Judgement sessions stay SHORT (STATUS, the plan, a failing
  log's summary). Minimise the scarce model; spawn more sub-sessions rather than do material work in a judgement
  session. **The hand-off is mechanical:** `.claude/agents/material.md` and `.claude/agents/log-reader.md`; a
  judgement session never runs `tools/recipes/*.py` or `tools/bench/*.py` itself and never reads a whole log.
  *Mechanism:* `guard_bash.py` requires `bgrun --material` for those runs. `docs/rules/CLAUDE-full-2026-10-10.md:349-375`
- **A delegation brief states the MEASUREMENT, never the result-dependent ACTION.** The material session measures,
  returns facts and `OPEN:`, and stops; the judgement session decides and delegates again. The retrospective counts
  `judgement-in-material`. `docs/rules/CLAUDE-full-2026-10-10.md:376-383`
- **Reports the user reads are written by a separate writer, not by this session** (2026-09-16): Claude hands a fact
  list to the prose role (`peer.ps1 -Kind prose`, a thin cell; codex at `-Agent codex -Kind prose`), archived under
  `archive/prose/`, shown as-is. The judgement session runs that dispatch itself, in the FOREGROUND (a backgrounded
  sub-agent once killed it); `guard_bash.py` allows exactly that shape. One-line answers and short questions stay
  Claude's. `docs/rules/CLAUDE-full-2026-10-10.md:384-398`

## Model ladders (2026-09-26 / table 2026-09-27) and escalation

- **Material sessions:** `claude-opus-5-5` HIGH (replay bench `tools/bench/matbench/report_v1.md`); escalation rungs
  Opus max -> Fable low -> `decisions_pending`. The Fable-low trial (cycles 89-91) ended. A live-cycle cost comparison
  is context only; the replay bench decides. `docs/rules/CLAUDE-full-2026-10-10.md:400-411`
- **Judgement sessions:** level 0 Opus 5.5 HIGH -> 1 Opus MAX -> 2 Fable low -> RUNNER STOP + decision item. Up one
  level when the last cycle left `next.json` unchanged or its retrospective named a judgement fault; back to 0 after a
  delivering cycle. The recipe firefighter is ONE Opus max cycle, then STOP. Fable medium is on no ladder. Level and
  reason: `JUDGE-LADDER` log line. `docs/rules/CLAUDE-full-2026-10-10.md:412-418`
- **Peers (same table):** retrospective Opus 5.5 high; `fact`/`prose` Opus 5.5 medium thin; outcome review fable/medium
  thin (now a Claude-GPT discussion, see `docs/rules/reviews.md`); hypothesis Opus high; prior-art Opus medium;
  ingest/audit Sonnet. `docs/rules/CLAUDE-full-2026-10-10.md:419-421`
- **Scratch-VI verification before a third try:** a stage run that fails twice on the SAME scripting function is
  followed by a <= 120-line scratch-VI check of that function; `stage_prerun.check_launch` refuses the third launch
  until a newer `tools/bench/scratch_verify/` PASS exists. `docs/rules/CLAUDE-full-2026-10-10.md:422-426`
- (history) the judgement effort A/B (cycles 89-97) is superseded by the table. `docs/rules/CLAUDE-full-2026-10-10.md:427-428`
- **Intra-cycle escalation:** a `task/1` card that returns FAIL with its failure budget spent, or exceeds
  `budget.minutes`, is re-issued (`escalation: 1`, `retry_of_card`) to `.claude/agents/material-opus-max.md`, then
  (`escalation: 2`) to `material-fable-low.md`, then goes to `decisions_pending.json`. Same flags, rules and peers; the
  result carries `escalation`. It bounds Fable to a card Opus already failed twice. `docs/rules/CLAUDE-full-2026-10-10.md:429-442`

Related decisions: `docs/decisions/cycles_run_in_fresh_sessions_via_runner.md`,
`docs/decisions/purpose_cycles_assignment_session.md`, `docs/decisions/judgement_vs_material_session_split.md`,
`docs/decisions/model_table_2026_09_27.md`, `docs/decisions/intra_cycle_escalation_to_fable.md`,
`docs/decisions/deliverable_first_hooks_outside_runner.md`.
