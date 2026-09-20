---
type: plan
status: superseded
date: 2026-09-18
cycle: 20
kind: build
tags: [plan, guard-cycle, tunnel-reader, motor-limit, P1]
supersedes: [docs/cycle19-plan.md]
decided_by: cycle-19 judgement session, after the check-A prior-art release and the flat-sequence measurements
---

# Cycle 20 — the two devices check A cannot be built without

Check A is **not** this cycle. Cycle 19 established, by measurement, that it needs one primitive that does not
exist, and that the gate meant to bind a launch to a verdict has never enforced. Both are small, both are
prerequisites, and building check A before them repeats the cycle that was just stopped.

## Step 1 — fix `guard_cycle.py:379` and make its self-test produce a log for the first time

`guard_cycle.premature_build` returns `None` (allows) where `tools/bench/selftest_guard_cycle_fixed.py` **T6**
expects REFUSED. Cycle 19 measured why (STATUS OPEN 43): `:379`'s `if not newer:` **inverts** CLAUDE.md:449
condition (b) — a review NEWER than the recipe suppresses the very check it should trigger. The inversion is read
from the code and T6's failure is measured, **so step 1 stands regardless of how the history is read**.

The history itself is disputed and does not need resolving to act, so do not spend the cycle on it: no
`selftest_guard_cycle_fixed.log` exists and no log names T6 PASS, so the archived "6/6"
(`archive/2026-09-17-status-d1-phase-full-narrative.md:254-256`) records each test's *expected* verdict in prose
— which is why codex's refutation quoted at `docs/cycle19-plan.md:33-34` rested on intent rather than an outcome.
Absence of a log is not proof that T6 never passed. What IS proven: it fails now, and no recipe launched down
that branch has ever been checked. Treat step 1 as a first enforcement, not a repair.

Done when: `:379` implements CLAUDE.md:449 (b) as written; the full self-test runs and **writes
`tools/bench/selftest_guard_cycle_fixed.log`**, T1–T6 all PASS; and the fixed branch is shown to REFUSE a
deliberately bad input as well as to allow a good one (Pre-decided 3).

## Step 2 — build the UID-addressed tunnel reader

The one primitive between the measured facts and a backward trace that crosses a flat sequence:
`UID → TMSC(FlatSequence*Tunnel) → OuterTerminal / InnerTerminal` (and the inner-tunnel `LeftTerm` / `RightTerm`).
The property ids are **measured, not hypothesised** — `FlatSequenceOuterTunnel` `3195B800/1/2`,
`FlatSequenceInnerTunnel` `1C3A9000-3` (`tools/bench/probe_flatseq_walk_run2.log`,
`tools/bench/probe_flatseq_outer.log`; codex corroborated as a fact exchange). What is NOT yet measured is a
**live read on an instance** — attaching an id to a class is not a read. That is what this op establishes.

Done when: the op returns, for a real tunnel uid on a real VI, the terminal reference and its owner; the
known-good fixture resolves (`LoopTunnel #28343 → Max Trans Pos.vi · Magnet position output`,
`docs/frame-loop-wire-graph.md:264`); and the walk from the startup ASI move (d10 uid 44036) advances past the
border that stopped it in cycle 19, with the hop count recorded.

## Pre-decided (apply, cite the number, do not re-ask)

1. **Hardware, stricter than the rig state — P1 wins.** Rig state is `조립`. **No motor moves, no motor port
   opened for writing**; `motor_gate.py --execute` is not to be called at all. LabVIEW and camera allowed.
   Originals are read-only: md5 before AND after every run, never save, Don't Save on every prompt.
2. **Check A's method is settled — `docs/motor-limit-assurance-plan.md` §A.1.** Do not redesign it, do not
   re-open the prior-art release (`archive/peer/2026-09-18-priorart-check-a-wiring.md`, four `FIXED:` lines).
   §A.1 item 3 is why step 2 exists; item 8 fixes the baseline as the 3StateClamping ORIGINAL.
3. **A gate that passes only its happy path is not accepted.** Anything built here that can refuse is proven to
   refuse on a deliberately bad input, not only to pass on a good one. For step 1 this is the whole point.
4. **Every prior-art dispatch passes `--recipe <path>`.** A verdict other than `novel` plants a stop record and
   the launch gate refuses that recipe until a valid `FIXED:` / `REFUTED:` line stands. Do not route around it;
   `CYCLE_GUARD_OFF` is never the answer. Writing the release line is the judgement session's call, never the
   material session's.
5. **Do not re-run a peer question already in `archive/peer/`** — check there first (rule 5's one exception to
   rule 4). Cycle 19 lost a full material dispatch to a prior-art review that was already on disk and already
   armed.
6. **The closing session writes `docs/cycle21-plan.md`** with its own `## Pre-decided`, and flips this file off
   `status: current`.

## Done means

- Step 1's log exists and shows T1–T6 PASS, plus the deliberate-bad-input refusal.
- Step 2's op reads a live instance and the d10 walk advances, with hop counts recorded.
- `py tools/doc_lint.py` shows no NEW fail (L6's undisposed archived reviews are pre-existing — STATUS OPEN 42).

## Next cycle, so it is not re-derived

Cycle 21 is **check A itself**, per §A.1: the ORIGINAL's read-only node/terminal sweep (~11 min, it has no
cache), then the forward reachability test from the three coerce nodes, then the control **Data Entry range**
read (§A.1 item 7 — a limit that is not a node), then the three comparator mutation negatives.

## Standing above this cycle

**OPEN 32 — the second consecutive outcome review returned six `OUTCOME-VIOLATION`s, which by CLAUDE.md stops
the work for a re-plan with the USER.** Not answerable by a device and not answerable by this plan. P1 runs
because the user ordered it explicitly ("모터 작동 체크 전까지는 모든 세션 돌려볼 것"); OPEN 32 is what the user
is owed when they return.
