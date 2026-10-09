---
type: decision
kind: topic
status: current
date: 2026-10-09
parent: docs/d1/INDEX.md
tags: [d1, runner, discussion, outcome-review, steer, pre-decided]
---

# Cycle runner — loop-structure decisions from PD382 on

Scope: how `tools/cycle_runner.py` runs the loop that builds D1 (reviews, discussions, steering), as opposed to the stage
tools in `docs/d1/tooling.md` (at its 400-line cap). How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

382. **(chat 2026-10-09, card chat-D2 — user "둘 다 넣자", after two live Claude-GPT discussions: "지금의 디스커션 방식이 너무
     훌륭함")** Claude-GPT discussions run INSIDE the runner, in two places that each REPLACE a single-model judgement (no
     new layer). Code: `tools/debate_loop.py` (topics, run, apply), `tools/cycle_runner.py` `debate_hook` /
     `gates_due_hook`; guide `docs/debate.md` "러너 안에서".
     - **(a) Outcome review = a discussion.** When `outcome_review.is_due()` (5 cycles / 7 days), the runner holds a
       discussion `c<N>-outcome` before the session spawns; `outcome_review.py` runs only when the discussion errors (no
       summary, error end, no round completed). The discussion archives `archive/peer/<date>-outcome-review-debate-c<N>.md`
       so the cadence (and guard_cycle's outcome gate) counts it. `--outcome-by review` restores the old single-model path.
     - **(b) Stuck = a discussion before the next cycle.** A cycle that ends at HANDBACK-LIMIT, or the runner's firefighter
       trigger (same failure two cycles running), gets `c<N>-stuck` before cycle N starts (hand-back records, the failing
       logs' first failing lines, the purpose). The firefighter rung still runs after it. If a stuck discussion ran, a due
       outcome review waits one cycle (one discussion per gap).
     - **(c) Result = existing channels only.** The items BOTH speakers' final STATE lines list as `agreed` become one
       steer/1 card (item `debate:<slug>`, verdict `debate-outcome` / `debate-stuck`; schema widened in
       `docs/protocol/steer.json` and `next.json`'s steer reply); each `user_needed` becomes one decisions_pending item
       (`protocol.add_decision`, de-duplicated while open). The judgement session follows the card or refuses it with
       evidence; two refusals stop the runner as before (measured in the self-test: a stand-in that never answers stops
       the runner after cycle 2).
     - **(d) Bounded and never blocking.** Synchronous, `debate_gdoc.py run --auto-end --max-rounds 6`, deadline
       `--debate-max-min` 40 → relay STOP file → 90 s grace → process-tree kill; the runner continues either way. A Google
       sign-in failure writes the discussion to a local `doc.md`, logs `DEBATE-NO-DOC`, adds a "log in" decisions item.
     - **(e) Reporting.** One `DEBATE | <time> | cycle N | outcome|stuck | doc <url> | rounds r | converged y/n | $x | ended
       …` line; the heartbeat's "Claude-GPT 토론 (문서 링크)" row carries it to the 30-min report; the session prompt gets
       a `DISCUSSION before this cycle` line. The user steps in from the chat with `debate_gdoc.py say --dir
       tools/bench/debate/<slug>/relay "…"`.
     - **(f) Evidence (offline, stub speakers, no model call):** `tools/bench/selftest_chatd2_debate_relay.log` 13/0,
       `selftest_chatd2_debate_gdoc.log` 13/0, `selftest_chatd2_debate_loop.log` 6/0, `selftest_chatd2_runner_debate.log`
       (runner wiring D1–D6). First real discussion in the loop: not yet run.
     USER-RULES: U1 (relied on: runner / review plumbing only - no VI, no stage computation) and U2 (offline only, the
     runner was stopped, no LabVIEW opened).
