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

- **PD383 (2026-10-09, user in the chat: "합의한 내용들 적용해서 러너 돌리자") - the 'overall plan' Claude-GPT discussion is applied.**
  Discussion `tools/bench/debate/plan-overall-02` (rounds mode, 5 rounds, converged, doc
  https://docs.google.com/document/d/1ftVOqFhHvaqaQ30_1XfZ_Kf4ArCUMuY8qVLv1ieYTOM/edit), summary `summary.json` there.
     - **(a)** Applied through the runner's own channel (`debate_loop.apply`): steer card `tools/bench/cards/steer_158.json`
       (13 agreed items, item `debate:plan-overall-02`) - the judgement session of cycle 158 follows it or refuses it
       with evidence in next.json; outcome archive `archive/peer/2026-10-09-outcome-review-debate-c158.md`.
     - **(b)** In substance: P5 -> P6 unchanged; keep original protection, hardware safety, timeout hooks and the replay
       X/Y/Z acceptance; gates split into BLOCK (computation / save / safety invariants) vs RECORD (names, uids, order -
       representation LabVIEW decides, read after the run); a mutation table of the gates on a stored ring graph runs as a
       small offline card BESIDE P5 and never delays it; P6 adds a frame-number-gap test and an overload test (test delay
       in 1.2: no loss at normal load, exact loss count and 0 damaged rows under overload; discard never seen = 'not
       verified'); the new-skeleton comparison is a candidate after P6.
     USER-RULES: U1 unchanged (no computation change), hardware rules unchanged.

417. **(chat ingest, 2026-10-15 — the lean runner as it now runs; decision record
     `docs/decisions/lean_operation_and_buffer_number_accuracy.md`)**
     - **(a) Cycle = EXECUTE → REVIEW → PLAN** (user 2026-10-13 "실행 에이전트 --> 리뷰 에이전트 (토론) --> 플랜"):
       `V6_lean/tools/bench/lean_bench/lean_queue.ps1` (user-started; the chat may launch it on the user's word through WMI),
       one Opus execute session per task, a read-only Claude-GPT review that re-computes the acceptance from raw files
       (VERDICT; PASS needs the session's PASS too; PASS-BY-REVIEW only with the user's approved source; no verdict twice →
       HOLD), a plan session that writes at most one task (same-tag retry ≤ 2 failures, or the plan's next step; a revision
       keeps the original's queue place unless the review says `ORDER: <tag> first`). Failed cycles do not stop the run.
       The run stops at run_limit.txt (5) with an evaluation discussion, on an empty queue, on STOP, or on a failed hook.
     - **(b) Cycle hooks** (user 2026-10-13 "모터 움직임 제한을 위한 훅은 사이클 시작 시점에 걸고, 사이클 종료 시점에
       풀리도록"): start = motor_gate session (PI reference + limits + readback) and the START-WINDOW check; end = LabVIEW
       closed and verified, limits released + readback, and the start-vs-end POSITION check (PI 0.001 mm, ASI 2 units).
       A lean session never runs `--session` itself (guard_lean); v5 G0's per-leg session start is approved (2026-10-14).
     - **(c) ASI window is RELATIVE** (user 2026-10-15 "그냥 실행 당시 위치를 기준으로 하자", after the joystick-set X
       -5.29 mm was found outside the fixed 2026-09-18 window): session start reads ASI X/Y (read-only) and sets SL/SU =
       position ± 2.0 mm, recorded in motor_session.json (motor_gate 817def14; first live use 2026-10-15 09:41, readback OK).
     - **(d) Bead-less frame-rate legs run with Auto-Reset OFF** in every leg copy (2026-09-16 decision, re-applied 2026-10-15).
     - **(e) Notes for sessions:** the user's own words live in `lean_bench/user_notes.md` (chat-checked facts in a separate
       section); lean sessions cannot web-search - the chat does web checks; never end a `claude -p` reply while a background
       job runs; the chat's direct ASI move was refused by the auto-mode classifier [Real-World Transactions] - the user moves
       the stage. Branches: current code on master; the lean worktree branch differs only by its session rules (merge with
       `--no-commit`, then restore CLAUDE.md / AGENTS.md / .claude/settings.json from HEAD).

420. **(chat ingest, 2026-10-19 — runner rules added in lean runs 7-15, all user-approved; code
     `V6_lean/tools/bench/lean_bench/lean_review.py` selftest 55/0, mock queue 20/0; lean commits through ba766fbe)**
     USER-RULES: hardware rules unchanged; runner cards never edit `tools/hooks/**`.
     - **(a) Conditions open an evaluation discussion and do NOT stop the run:** budget 10 h / $150 (`run_budget.json`,
       spend summed per session id), same task FAIL twice (fail2), INCOMPLETE twice (inc2), empty queue, repeated
       question (both sides yes). Only the 10-cycle ceiling (`run_limit.txt`) writes STOP. `fail_reset.json` restarts
       the failure count when the user resumes a task.
     - **(b) Cycle outcomes:** PASS / FAIL / INCOMPLETE / PASS-BY-REVIEW; a task marked `EXPECT: INCOMPLETE` that the
       review passes is an ANALYSIS cycle (not counted).
     - **(c) Both reviewers end with `CONFIRM: VERDICT|NEXT|KIND|SCOPE|TARGET|END`;** SCOPE is fixed words compared as a
       set, TARGET by category, END only recorded. A mismatch gets one re-agreement, then HOLD with only the common steps
       planned. NEXT is read only from upper-case `NEXT:` lines. `USERQ: yes|no`. A verdict change is logged.
     - **(d) Gate lock:** `gate_lock.py lock <tag>` freezes `gates/<tag>.json` before execution; the review FAILs the
       cycle if the gate file changed. The launch prompt forbids hand-set gates and narrowing the scope.
     - **(e) Plan conflict check:** a planned task that conflicts with a queued one is parked as `.conflict`; HOLDs on
       the same tag merge into one user question.
