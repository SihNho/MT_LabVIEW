---
type: plan
status: done
date: 2026-09-18
cycle: 19
kind: delivery
tags: [plan, motor-limit, check-A, P1]
supersedes: [docs/cycle18-plan.md]
decided_by: cycle-18 judgement session, closing the `device-failed` device and returning to the user's P1 order
---

# Cycle 19 — P1 step 2: **check A** of the motor-limit assurance plan

## The step

`docs/motor-limit-assurance-plan.md` **§A (check A)** — the next step in the user's standing P1 order
(census ✅ → **A** → B → broken-VI proof → C + record hook), one step per cycle. Read §A there; it is not
restated here.

Two things cycle 17 already settled, so do not re-open them:

- The census is closed: `docs/motor-call-site-census.md`, 97 sites, kinds `COMMAND` / `QUERY` / `CONFIGURE`,
  `ASSUMED_MOTION` replacing the abolished `UNKNOWN`.
- **Check A carries all 43 in-scope sites — there is no demotion pass.** Check A's own output is the recorded
  measurement that demotes the eight vi.lib GUI/error sites, for free.

## Pre-step, and it is BOUNDED: measure the T6 regression, do not fix it

`tools/bench/selftest_guard_cycle_fixed.py` **T6 fails**: `guard_cycle.premature_build` returns `None` (allows)
when the review is newer than the recipe, where T6 expects REFUSED. Cycle 18 measured it (`T1..T5 PASS`,
`T6 FAIL expected=REFUSED got=ALLOWED`) and dispatched the mandatory dual review — both arms ANSWERED,
`archive/peer/2026-09-18-cycle18-t6-regression-{codex,opus}.md` — which established that the cycle-18 refactor
**cannot reach that path**, and codex refuted the claim that T6 has failed since it was written, citing
`archive/2026-09-17-status-d1-phase-full-narrative.md:254` recording 6/6 with T4/T5/T6 named.

Why it is at the head of this cycle rather than filed: `premature_build`'s "review newer than the recipe" case is
the check route-B run 3 evaded. If it has stopped refusing, the stop record + launch gate built in cycle 18 is the
**only** thing now binding a launch to a verdict — a single point of failure in the device that answers
`device-failed`.

**Bound (do not exceed):** ONE material or log-reader dispatch, measurement only. The two competing explanations
are (a) the archived 6/6 line records something other than a passing T6, (b) `guard_cycle` drifted after
2026-09-17. The discriminating evidence is on disk and needs no rebuild: the last `tools/bench/*.log` line in
which T6 PASSED, against when the allowing branch appeared in `guard_cycle.py`. **If a fix is required, the fix is
cycle 20** — this cycle records which explanation the machine supports and moves on to check A.

## Pre-decided (apply, cite the number, do not re-ask)

1. **Hardware, and it is stricter than the rig state: P1 wins.** Rig state is `조립`. **No motor moves and no motor
   port opened for writing** — `motor_gate.py --execute` is not to be called at all. LabVIEW and the camera are
   allowed. Stubs and fake-motor runs only.
2. **The independent checker certifies, never the builder.** `.claude/agents/motor-limit-checker.md` is written;
   its input is ONE VI path, never the builder's explanation. A session that builds a limit does not certify it.
3. **Every prior-art dispatch now passes `--recipe <path>`** — `tools/prior_art_review.py` REFUSES (rc 2) without
   it, unless `--no-recipe "<reason>"` is given with a real reason, which is archived as a `NO-RECIPE:` line. A
   verdict other than `novel` plants a stop record and the launch gate will refuse the recipe until a valid
   `FIXED:` / `REFUTED:` release line stands. This is the cycle-18 device working as intended; do not route around
   it, and `CYCLE_GUARD_OFF` is never the answer.
4. **A gate that passes only its happy path is not accepted** (carried over from cycle 18, Pre-decided 4, and the
   motor plan's §D.4). Anything check A produces that can refuse must be proven to refuse on a deliberately bad
   input, not only to pass on a good one.
5. **Do not write a `DECISION:` block for a slug whose device is not yet running** — a promise is not a fix.
6. **The closing session writes `docs/cycle20-plan.md`** with its own `## Pre-decided`, and flips this file off
   `status: current`.

## Done means

- Check A is run and its output recorded where `docs/motor-limit-assurance-plan.md` §A says it belongs, covering
  all 43 in-scope sites.
- The T6 pre-step has named which explanation the evidence supports, in one paragraph, with the file:line.
- `py tools/doc_lint.py` shows no NEW fail (L6's 39 undisposed archived reviews are pre-existing — STATUS OPEN 42).

## Standing above this cycle

**OPEN 32 — the second consecutive outcome review returned six `OUTCOME-VIOLATION`s, which by CLAUDE.md stops the
work for a re-plan with the USER.** It is not answerable by a device and it is not answerable by this plan. P1 runs
because the user ordered it explicitly ("모터 작동 체크 전까지는 모든 세션 돌려볼 것"); OPEN 32 is what the user is
owed when they return.
