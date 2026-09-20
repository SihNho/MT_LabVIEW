---
type: archive
status: archived
date: 2026-09-18
tags: [status-narrative, cycle-18, device-failed, stop-record, launch-gate, census]
---

# Relocated from STATUS.md at the close of cycle 18 (rule 4: narrative moves down a layer, it is never rewritten)

STATUS.md had reached 126 lines. The three blocks below were moved here verbatim; STATUS now carries a pointer to
each. Nothing is deleted.

## §1 — Cycle 18: the STOP RECORD + LAUNCH GATE (the `device-failed` answer)

🆕 **CYCLE 18 CLOSED the `device-failed` hole — the STOP RECORD + LAUNCH GATE is BUILT and PROVEN.**
`tools/stop_record.py` (store `tools/bench/stop_records.json`) + call sites `guard_bash.py:156` (before any
`LV_GUARD_OFF`/`BENCH_CELL` escape) and `guard_cycle.py:462`. **Refusal by PATH, release qualified by HASH**: a
re-save cannot evade a record, and a byte change after a release is refused again as *unreviewed*. Releases stay the
existing two (`FIXED:` / `REFUTED:`), validator **imported** from `guard_cycle` (`stop_record.py:256-257`), never
reimplemented. Fail-closed on a corrupt store, scoped to `tools/recipes/*.py`. **An omission can no longer leave it
un-armed:** `prior_art_review.py` REFUSES (rc 2) without `--recipe`, unless `--no-recipe "<reason>"` — archived as a
`NO-RECIPE:` line that cannot parse as a release or a disposition. **29/29 self-test gates**
(`tools/bench/stop_record_selftest.py`), real store measured untouched; logs `cycle18_stopgate.log`,
`cycle18_arming.log`, both `BGRUN END rc=0`. Decision block: `docs/violation-decisions.md`, round 6.

Supporting detail not in STATUS: the `REFUTED:` half of the release validator was an inline `re.findall` inside
`guard_cycle.main()` and was refactored out to `guard_cycle.py:172 released_slugs()`, now used by both `main()`
(`:521`) and `stop_record` (lazy import, because `guard_cycle.py:63` imports `stop_record` — a module-level import
would be circular). `prior_art_review.py` gained `--recipe` (`:214-217`), `--no-recipe REASON` (`:218-223`), the
refusals `REFUSE_NO_RECIPE` (`:141`) and `REFUSE_BOTH` (`:155`) both returning 2, and `record_opt_out()` (`:161`).
A whitespace-only reason is not an opt-out. Self-test cases C0–C6f, 29 gates, in
`tools/bench/stop_record_selftest.py`; the two drivers are `tools/bench/cycle18_stopgate_driver.py` and
`tools/bench/cycle18_arming_driver.py`.

## §2 — P1 step 1, the census (cycle 17), relocated from "Where things stand"

🆕 **P1 step 1 (CENSUS) IS CLOSED — `tools/motor_census.py` (a READER) → `docs/motor-call-site-census.md`.**
Run 3, **7/7 gates**, `BGRUN END rc=0`, both originals' md5 unchanged, nothing run or saved. ORIGINAL = 97 sites,
**41 MOTION**, labelled by the cycle-17 decisions: **COMMAND 31 · QUERY 9 · CONFIGURE 1 · ASSUMED_MOTION 11 ·
NONE 45 ⇒ IN SCOPE 43, undecided 0** (`UNKNOWN` abolished; untraversable ⇒ ASSUMED_MOTION, in scope; a name-list
checker would have missed 14). Decisions + demotion rule: that doc. 🔴 **Rule 1c fact:** `ASI_adjust
focus-subvi.vi` (COMMAND) is called on **diagram 43 = the FRAME LOOP** — the ORIGINAL already puts serial traffic
on the frame acquisition path. Recorded, nothing changed.

## §3 — OPEN 43 in full: the `premature_build` / T6 regression

🔴 **`guard_cycle.premature_build` ALLOWS where `selftest_guard_cycle_fixed.py` T6 expects REFUSED** (review
newer than the recipe — the very case route-B run 3 evaded). Measured, not inferred: `T1..T5 PASS`,
`T6 FAIL expected=REFUSED got=ALLOWED`. Dual review BOTH ANSWERED
(`archive/peer/2026-09-18-cycle18-t6-regression-{codex,opus}.md`): the cycle-18 refactor **cannot reach that
path**, and codex refuted "T6 always failed", citing `archive/2026-09-17-status-d1-phase-full-narrative.md:254`
(6/6, T4/T5/T6 named). Two live explanations — (a) the archived 6/6 line records something other than a passing
T6, (b) `guard_cycle` drifted after 2026-09-17 — and the discriminating evidence is already on disk: the last
`tools/bench/*.log` line in which T6 PASSED, against when the allowing branch appeared in `guard_cycle.py`.
**Cycle 19 measures, cycle 20 fixes** (`docs/cycle19-plan.md`). Until then the cycle-18 launch gate is the ONLY
thing binding a launch to a verdict.

The cycle-18 driver reports T6 as a `KNOWN` line rather than a gate, so it does not re-arm `guard_peer` on the
next cycle's first build. The cycle-18 judgement session accepted that: T6 is pre-existing, is not reachable from
the cycle-18 refactor, and its mandatory dual review has already been dispatched, archived and disposed.

## §4 — relocated VERBATIM from STATUS.md, 2026-09-18 (rule 4: STATUS stood at 120 lines, threshold 110)

### Cycle-18 close, as STATUS carried it

Cycle 18 is CLOSED and its gate is DISCHARGED: `py tools/violations.py` now reports **"0 slug(s) awaiting a
response"** (`device-failed` answered 2026-09-18 00:53, `docs/violation-decisions.md` round 6), so `guard_cycle`
will not refuse cycle 19's build on a slug at threshold. The device itself is in "Where things stand" above; its
rationale stays in `docs/cycle18-plan.md` (`status: done`). **The date-granularity bug at
`docs/violation-decisions.md:197-207` did NOT bite — same-day answers parse; that note is now stale, and only the
user should decide whether to delete it.**

### OPEN 43 (the `guard_cycle.premature_build` T6 regression), as STATUS carried it

43. 🔴 **`guard_cycle.premature_build` ALLOWS where `selftest_guard_cycle_fixed.py` T6 expects REFUSED.**
   **MEASURED AND DIAGNOSED, cycle 19** (annotation: `archive/peer/2026-09-18-cycle18-t6-regression-codex.md`
   §"Cycle 19"): **T6 has NEVER passed** — no `selftest_guard_cycle_fixed.log` exists and no log names it PASS;
   the "6/6" at `archive/2026-09-17-status-d1-phase-full-narrative.md:254-256` states each test's *expected*
   verdict in prose, so codex's refutation rested on intent, not output; no older `guard_cycle.py` exists, so
   "drift" is unevidenced. `guard_cycle.py:379`'s `if not newer:` **inverts** CLAUDE.md:449 condition (b) — a
   review newer than the recipe suppresses the very check it should trigger. **So route-B run 3 evaded nothing;
   the branch never enforced.** 🔧 **CYCLE 20 FIXES `:379`** — first enforcement, not a repair; every recipe
   launched down that branch to date went unchecked. Until then the cycle-18 launch gate is the ONLY thing
   binding a launch to a verdict. Detail → §3 of this file.
