# retrospective-cycle31

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $3.3687  in 12 / out 20882 / cache-create 97744 / cache-read 369633  (285s, 18 turn(s))
- **date:** 2026-09-18 18:30:54
- **outcome:** ANSWERED (287s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 31 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-18 16:52:33  ..  2026-09-18 18:26:05   (94 min)
    basis: start = archive/peer/2026-09-18-retrospective-cycle29.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
The compliance audit below was run over that window (--from/--to), and the build-log list is the logs
whose mtime falls inside it. Earlier work belongs to an earlier cycle: do not attribute its cost here,
and say so if the attached evidence contradicts the window.

=== OUTPUT CONTRACT - read this before you read anything else ===

This review has run seven times before. Five slugs fired in 7 of 7 runs, and the last three cycles each fired ALL
NINE. That is saturation, not measurement: the format asked seven questions, offered nine slugs, and got one slug
per question. A tally that always reads "nine" cannot tell a bad cycle from a good one, and the device rule built
on it turned into "build a device every cycle". So the contract has changed, and it is the part of this prompt
that matters most.

1. NAME THE ONE MOST COSTLY STRUCTURAL FAULT OF THIS CYCLE. At most TWO, and a second only if it is genuinely of
   the same magnitude as the first. Not a list. Not one per question. If you find yourself with five candidates,
   your job is to rank them and report the top one - the ranking IS the review.

2. `VIOLATION: none` IS A LEGITIMATE ANSWER, and it is the expected answer for a cycle that was run well. A cycle
   whose faults are all minor - a slow log read, a slightly wide scope, a sentence that could have been clearer -
   has NO structural fault, and saying so is a correct review, not a failed one. Do not manufacture a violation to
   look thorough. Do not treat "something could have been better" as a structural fault; a structural fault is one
   that changed how the cycle ENDED - what it cost, what it produced, or whether it produced anything.

3. FOR EACH FAULT YOU NAME, give all three of:
   (a) THE SLUG, from the fixed list at the bottom. Map to the closest one; do not invent slugs.
   (b) A LOSS ESTIMATE, in minutes AND in dollars where the logs carry the number. The logs that carry cost:
       `COST: $<n>` lines in tools/bench/priorart_*.log and peer_*.log; `BGRUN END rc=<n> after <n>s` in every
       bgrun log; the audit's C3 (build wall-clock), C4 (review wall-clock and cost) and C5 (total) lines. If no
       log carries a dollar figure for this fault, write `loss_usd=?` - a guessed number is worse than an honest
       unknown, and this project has been burned by exactly that (a cost argument made against a figure an order
       of magnitude too small).
   (c) A COUNTERFACTUAL, concrete and on the clock: "had X been done at attempt N / at HH:MM, the cycle would have
       ended at T instead of T'". If you cannot construct one, the fault is probably a FINDING, not a violation.

4. EVERYTHING ELSE YOU OBSERVE GOES IN THE PROSE, UNDER `FINDINGS`. Findings are wanted - the seven questions
   below exist to produce them. They simply do not each produce a slug, and they never did deserve one.

=== FINDINGS - answer all seven in prose. These do NOT each produce a slug. ===

Be concrete about which log or file shows each one (file:line).

1. REPEATED FAILURE. Did the same class of failure recur? On which attempt should the approach have changed, and
   to what? Name the attempt number.
2. MISSING TOOL. Is there a reader or op that was NOT built and whose absence made the cycle more expensive? Say
   which failures it would have answered.
3. UNMEASURED STEPS. Was anything decided by inference where a measurement was available and cheap?
4. RULE COMPLIANCE. Read the attached CLAUDE.md. Which of its rules were broken, evaded, or satisfied only
   formally? The compliance audit output is attached - say also what the audit does NOT cover.
5. ORDERING. Was the cycle's order of work defensible, or should some later step have come first?
6. WHAT WAS NOT REPORTED. From the raw logs, is there anything the session's own summary would have hidden or
   understated?
7. JUDGEMENT INSIDE A MATERIAL SESSION. Was any decision taken inside a MATERIAL sub-session (agent `material`,
   `log-reader`, `reporter`, or any `claude -p` cell) that belonged to the judgement session: a design change, a
   choice between explanations, accepting/rejecting a review finding, a change of plan direction, or an action
   pre-scripted in the brief as "if X then do Y"? Cite the log or archive file and line.

=== DEVICE EFFECT - the question nobody has ever asked ===

Every list below is a MECHANICAL DEVICE this project built because a slug reached its threshold. The list is
generated from docs/violation-decisions.md, not written by the session under review. Seven cycles of devices have
been built and no reviewer has ever been asked whether one of them WORKED.

For EACH device: did the fault it exists to stop occur ANYWAY, inside this cycle's evidence window? Cite
file:line. A device can fail three ways and all three count: it never fired when it should have; it fired and was
worked around; or it fired on the wrong thing so often that it is now routinely bypassed.

If any device failed, emit `VIOLATION: device-failed` with the device named in the `evidence=` field.
ITS THRESHOLD IS 1, NOT 3 - a device that failed once is a broken device, and waiting for two more cycles of
evidence to say so is the same patience that produced the saturation this format replaces.

Devices on file (docs/violation-decisions.md, machine-extracted):
  - `unreported-fact` (decided 2026-09-16): The only one of the six with a concrete, unfixed defect behind it, and it hides failures rather than merely costing time: a PowerShell runner reported `rc=0` while the probe it wrapped exited 1 (`tools/bench/probe_relocate_route_run2.log:25` ??"outer runner ended rc=0 although the embedded probe says probe exit=1"). A batch that fails can therefore look like a batch that passed. Fixed by making ev??
  - `rule-evaded` (decided 2026-09-16): `peer.ps1 -Kind review` now REFUSES a task carrying confirm-bait ("please confirm", "sanity check", "do you agree", "?뺤씤 遺??) and APPENDS the adversarial instruction set. Cycle 7's retrospective had found prompts saying "BRIEF CONFIRM" ??the opposite of rule 5. The device exists and predates this decision; recorded here so the gate can see it.
  - `tool-not-built` (decided 2026-09-16): The prior-art review (`tools/prior_art_review.py`) asks, before any new build: has this been built, measured, or tried and failed, and does a helper already exist? On its first real use it found four defects in a pending recipe, one of them a repeat of a recorded failure. Benchmarked at 6.5/8 on real prior-art items (`tools/bench/priorart_scores.md`). Note what the cycle-9 retrospective actually s??
  - `repeated-failure-class` (decided 2026-09-16 15:05): `peer.ps1` / `guard_peer.py` refuse a new `priorart` or `retrospective` dispatch while the newest archived review of that kind still has an empty *"What was done with it"* section. It attacks the exact loop that cost $28.55, and it cannot be satisfied by a token edit the way a "cite a census log" rule could.
  - `unreported-fact` (decided 2026-09-16 15:05): C3 counts `tools/bench/peer_*.log` and `priorart_*.log` wall time and the usage/cost lines the claude peer already records, and reports build cost and review cost as two separate lines. Small, and it makes the cost argument possible instead of rhetorical.
  - `premature-build` (decided 2026-09-16 19:16): `tools/hooks/guard_cycle.py` refuses a RECIPE build while (a) any `tools/bench/priorart_*.log` for the current cycle has no `BGRUN END|TIMEOUT` line, or (b) no `archive/peer/*priorart*.md` is newer than the recipe file being run. Diagnostics (`tools/bench`) stay open. Reason: the violation is a *timing* fact the machine can see; a rule about patience is the kind that fades after compaction.
  - `scope-creep` (decided 2026-09-16 19:16): `tools/audit_cycle.py` gains a line listing every file modified in the cycle window that is not named in the cycle's plan document (`docs/cycle<N>-plan.md`), so the retrospective judges scope from a machine-made list rather than from Claude's summary. A counter, not a refusal, by design: out-of-plan changes are sometimes right (a measured bug fix), so the verdict stays with the retrospective; only??
  - `device-failed` (decided 2026-09-16 21:07): repair the regex (that IS the device), add a self-test line that asserts the regex matches the literal `COST: $5.1157` form, and make `audit_cycle` print `cost lines seen / cost lines parsed` so a silent miss is visible.
  - `device-failed` (decided 2026-09-17 03:38): `tools/bgrun.py` adds `^\s*(?:->\s*)?FAIL\b` (the same form audit_cycle/guard_peer use) to the inner-failure scan for build/diagnostic logs (review logs stay excluded via logclass), and forces `rc=1` on a match; self-test on the literal line above.
  - `repeated-failure-class` (decided 2026-09-17 03:38): build the reader `OpLoopEndRef_v0` (`WhileLoop.Loop End Ref` 0x06362C00 ??the conditional terminal ??its connected wire/source), functionally verified on the main VI's #637 (read-only), so "how does the original stop" is measured before D1 replaces that loop. It is also D1's S4 gate.
  - `device-failed` (decided 2026-09-18 00:53): Device, built and proven this cycle: a **stop record + launch gate**. - `tools/stop_record.py` ??record store `tools/bench/stop_records.json`; a prior-art verdict other than `novel` plants a record keyed to the recipe's **path + sha256**. Refusal is by PATH (re-saving cannot evade it); release is qualified by HASH (the gate stamps the hash at the first launch after a valid release, and a later byt??

=== END YOUR ANSWER WITH MACHINE-READABLE LINES ===
One line per structural fault you named - normally ONE, at most two - in exactly this form:
  VIOLATION: <slug> | loss_min=<number> | loss_usd=<number or ?> | evidence=<file:line>
or, if the cycle had no structural fault:
  VIOLATION: none
Slugs: repeated-failure-class 쨌 tool-not-built 쨌 inference-over-measurement 쨌 rule-evaded 쨌 wrong-ordering 쨌 unreported-fact 쨌 scope-creep 쨌 premature-build 쨌 judgement-in-material 쨌 device-failed
Do not invent new slugs; map to the closest one and explain in the prose. `loss_min` is a whole number
of minutes. `loss_usd` is a number only when a log carries it, otherwise `?`. `evidence` is one
file:line that a reader can open.
WRITE A `VIOLATION:` LINE ONLY AS YOUR OWN FINAL VERDICT. Do not quote, restate, echo or illustrate this
format anywhere in your answer - not in the prose, not while explaining what you are about to do. Every
`VIOLATION:` line in your answer is read by a parser as a real occurrence.

=== COMPLIANCE AUDIT (tools/audit_cycle.py --from/--to, machine-generated) ===

== cycle audit, 2026-09-18 16:52 .. 2026-09-18 18:26 (94 min, an explicit cycle window): 14 build logs, 8 peer logs, 45 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 14/14 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 6 logs recorded a failure; unreviewed: ['tmx_selftest.log']
  FAIL  A4 every archived review says what was done with it: 37/45 annotated; blank: ['2026-09-18-asi-soft-limits-sl-su.md', '2026-09-18-ff-selftest-bgrun-start-regex-codex.md', '2026-09-18-ff-selftest-bgrun-start-regex-opus.md', '2026-09-18-ff-selftest-drycmd-split-codex.md', '2026-09-18-ff-selftest-drycmd-split-opus.md', '2026-09-18-pi-c863-soft-limits.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 20, failure markers 10, logs carrying a failure 6
  C2 peer reviews dispatched 8, archived 45
  C3 wall-clock inside bgrun, BUILDS ONLY 23 min 22 s
  C4 wall-clock inside bgrun, REVIEWS 44 min 12 s; cost $19.4252 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C5 total wall-clock 67 min 34 s  (reviews are 65% of it)

  C6 material-marked recipe/bench runs 17, judgement-session attempts refused 5  <- delegate to the `material` agent instead

  C7 out-of-plan files: no docs/cycle<N>-plan.md found - scope cannot be checked mechanically


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 281/454 ok; 173 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 777 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:131 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 178 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:915']

AUDIT VIOLATIONS: A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (14; read them directly, they are the primary record) ===
tools/bench/compile_v4.log  (2026-09-18 17:25:06)
tools/bench/d0_locate_selftest.log  (2026-09-18 18:04:50)
tools/bench/d0v4_tmx_recheck.log  (2026-09-18 17:34:48)
tools/bench/diag_d0_gate_probe.log  (2026-09-18 17:13:02)
tools/bench/diag_d0_inventory.log  (2026-09-18 17:03:28)
tools/bench/diag_d0_pickloop_liveness.log  (2026-09-18 17:51:41)
tools/bench/diag_d0_trace_path.log  (2026-09-18 17:05:34)
tools/bench/drive_original_copy_v4.log  (2026-09-18 17:33:39)
tools/bench/drive_original_copy_v5.log  (2026-09-18 18:13:02)
tools/bench/liveness_tmx_recheck.log  (2026-09-18 17:52:18)
tools/bench/p3_pi_query_after_d0.log  (2026-09-18 17:49:10)
tools/bench/syntax_check_liveness.log  (2026-09-18 17:45:23)
tools/bench/tmx_selftest.log  (2026-09-18 18:25:57)
tools/bench/wait_peer.log  (2026-09-18 17:52:19)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (9) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_16.log  (2026-09-18 16:55:36)
tools/bench/cycle_17.log  (2026-09-18 17:07:15)
tools/bench/cycle_18.log  (2026-09-18 17:07:15)
tools/bench/cycle_runner.log  (2026-09-18 17:07:15)
tools/bench/cycle_runner_main_20260918d.log  (2026-09-18 17:07:15)
tools/bench/peer_d0v4.log  (2026-09-18 17:49:11)
tools/bench/peer_tmx_lastfield.log  (2026-09-18 18:24:23)
tools/bench/priorart_d0_harness.log  (2026-09-18 17:06:00)
tools/bench/retro.log  (2026-09-18 18:26:05)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle31-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

I have what I need. This window (16:52–18:26) is the cycle that finally closed D0 — prior-art (16:58–17:06) killed the planned recipe as already-built, the v4 driver failed on a blindly inherited click point (17:25–17:33), the failure was diagnosed, reviewed, and fixed with a capture-based locator, and v5 (18:08–18:13) met D0's done-when on both legs, with the one residual FAIL being a parser false red that was itself fixed and self-tested to 10/10 by 18:25. Here is the retrospective.

## Overall judgement

This cycle produced the thing three consecutive outcome reviews said the project had never produced: a harness that drives the unmodified original's copy through pick → done → bandpass → save → experiment loop → own-control stop → trace file, twice, unattended (`tools/bench/drive_original_copy_v5.log`, 39 pass / 1 fail, `BGRUN END rc=1 after 290s`, trace files 285 KB under `tools/bench/d0_out/v5_20260918_180813/`, frame counter advancing, original md5 identical before and after — v4 log lines 781/794 and the v5 summary in STATUS.md:34). The work was worth doing, and it ended done. The cycle has exactly one structural fault, and it is the fault the user had to catch from the chair.

## FINDINGS

**1. REPEATED FAILURE.** The same class recurred twice inside the window: *trusting an inherited value where the live value was capturable*. Instance 1: v4 STEP 7 derived every click from v3's V6-copy offsets — `done=(1114,915)` (`tools/bench/drive_original_copy_v4.log:160`) — on a *different* VI copy, and the pick loop then sat 303 s un-ended (`drive_original_copy_v4.log:286`). Instance 2: the v5 TMX gate parser split `TMX?=1=39.00000` on the first `=` and reported None (`drive_original_copy_v5.log:439`) — even though the per-axis reply form was already sitting in this window's own `d0v4_tmx_recheck.log` output at 17:34 (quoted verbatim in STATUS.md:35). The approach should have changed at v4's *design* time, attempt 1 — the locate primitive that fixed it (`tools/bench/d0_locate.py`, template score 0.00 vs next-best 28.35) was built in under 30 minutes once the miss was seen. To the cycle's credit, attempt 2 (v5) did change the approach, for every click class at once (done button, bandpass Yes, all `CLICKPROBE`-verified, `drive_original_copy_v5.log:456,460`).

**2. MISSING TOOL.** `d0_locate.py` itself — the capture-and-locate primitive. It was built mid-cycle *after* the failure it would have prevented; had it existed before 17:25 it would have answered v4's R4 FAIL, the restart-leg FAIL, and made the $3.28 hypothesis review unnecessary. Secondarily: a PI-reply parser with a selftest. The `tmx_from` parser shipped inside v5 with no selftest; the selftest written after the failure immediately reproduced it (`tools/bench/tmx_selftest.log:2`, 8/1 → then 10/0 after the fix, `tmx_selftest.log:24-25`).

**3. UNMEASURED STEPS.** Two, both cheap: (a) the done-button position — a screenshot + template match was available (proven at 17:28, `tools/bench/p3_done_check.png`, referenced in STATUS.md:80-81) and was skipped in favour of v3's offsets; (b) the TMX reply's per-axis format — already measured and on disk at 17:34 in `d0v4_tmx_recheck.log`, unread when the v5 parser was written ~25 min later. Both are textbook cases of the CLAUDE.md "guessed twice → build the reader" clause, and both readers were in fact built inside the cycle, just one run too late.

**4. RULE COMPLIANCE.** Largely genuine, not formal: every GUI act logged with `Approved` + the user's 2026-09-17 evidence string (`tools/gui_actions.log:1776-1790`); originals untouched (audit A5 PASS; md5 `c39f36e0…` before and after in both driver logs); all runs under bgrun (A1/A2 PASS); the failed prediction discharged by the amended single-arm claude/hypothesis route (`archive/peer/2026-09-18-d0v4-picking-loop-frozen.md`, ANSWERED, annotated). Broken or misleading: v4's gate 7 was a **formally-passing gate verifying the wrong invariant** — it compared window rects (delta 0,0) and PASSed while the control positions differed, which v5's own gate 7 now says explicitly (`drive_original_copy_v5.log:154`). The audit's A3 FAIL on `tmx_selftest.log` is a **false positive**: the failing run (18:16:30) *was* followed by an archived review (`archive/peer/2026-09-18-tmx-lastfield-parse.md`, 18:24) — but the fixed rerun then touched the same log at 18:25:57, making the log's mtime newer than the review. A4's six blanks are all files whose kinds don't gate anything in this window. What the audit does NOT cover: (a) **C7 is dead** — it looks for `docs/cycle31-plan.md`, but the plan scheme changed to one plan spanning cycles 27+ (`docs/cycle27-plan.md`, "Cycle 27+"), so scope has been mechanically uncheckable for several cycles; (b) C4's $19.43 counts only peer-log COST lines — the `claude -p` judgement sessions themselves (`cycle_17.log`, `cycle_18.log`) carry no COST line at all, so the cycle's true spend is understated by an unknown amount; (c) no audit line can detect a PASS gate that verifies the wrong thing.

**5. ORDERING.** Defensible, and better than most prior cycles: prior-art ran first (16:58–17:06) and its verdict — seven non-novel slugs, "the harness exists as v3; what is new is a four-item delta" (`archive/peer/2026-09-18-priorart-d0-harness.md:14-17`) — was accepted and actually changed the work (the planned recipe was abandoned, v3 extended instead). Diagnostics preceded the driver; the retrospective ran last. The one ordering error is Finding 1 restated: locate-before-click should have preceded the first driver run.

**6. WHAT WAS NOT REPORTED.** STATUS.md:34 is unusually honest (it reports its own FAIL and calls it a parser false red, correctly). Three things a summary reader would still miss: (a) v4's *first* launch died in 1 s on the motor gate (`drive_original_copy_v4.log:5-7`, exit=2, run refused) and was relaunched 30 s later — correct behaviour, but unmentioned anywhere; (b) the `Count` indicator mystery is quietly dropped: in v4 *and* v5, three clicks produced `Count` 0→1→1→1 (`drive_original_copy_v4.log:790`; v5 L7 "Count 1 -> 1", `drive_original_copy_v5.log:181`) — v5 switched the verification to the three red markers and passes, but *why* Count reads 1 after 3 registered picks is unexplained and could matter for D1; (c) the review cost attributable to the v4 miss ($3.2775, `tools/bench/peer_d0v4.log:3`) appears in no narrative.

**7. JUDGEMENT INSIDE A MATERIAL SESSION.** Discipline held where it matters: the material session that dispatched the d0v4 review explicitly wrote "Acceptance is a judgement call, not made in this material session" (`archive/peer/2026-09-18-d0v4-picking-loop-frozen.md:14`) and ran only the prescribed discriminating measurement. One borderline instance: `docs/cycle27-plan.md:59` records that Pre-decided 7 was "corrected by the cycle-32 material session" — a material session edited a Pre-decided rule line. The content was a consistency fix to match a decision CLAUDE.md already records (the 2026-09-18 D3 amendment), so no *new* judgement was taken there; it stays a finding, not a violation.

## DEVICE EFFECT

- **stop record + launch gate / prior-art**: WORKED — the verdict was non-novel and the planned recipe (`build_d0_harness_v0.py`) was genuinely abandoned, released through the `FIXED:` mechanism in the review file itself (`archive/peer/2026-09-18-priorart-d0-harness.md:17`). No bypass.
- **premature-build guard**: WORKED — prior-art (17:06) preceded every build in the window.
- **bgrun FAIL-scan / rc-forcing (both `device-failed` repairs and `unreported-fact`)**: WORKED — v4 ended rc=1 on 3 real FAILs, v5 ended rc=1 on its 1 FAIL, the selftest ended rc=1 then rc=0; nothing failed silently. C4b: 4/4 cost lines parsed.
- **confirm-bait refusal (`rule-evaded`)**: not triggered; both hypothesis dispatches were adversarial-role.
- **A4 annotation gate (`repeated-failure-class`)**: not bypassed — the six blanks are neither priorart nor retrospective kind, the only kinds it gates.
- **C7 out-of-plan counter (`scope-creep`)**: DEGRADED, not failed — it could not run at all ("no docs/cycle<N>-plan.md found", audit C7) because the plan scheme changed under it. However, the fault it exists to stop did not occur in this window: every file touched (v4/v5 drivers, d0_locate, the diagnostics, the plan and STATUS edits) serves D0, which is the plan. A counter that cannot count is a defect to fix, but no fault got through it this cycle, so it does not meet the device-failed bar. It should be repointed at the `status: current` plan rather than at a per-cycle filename.
- **OpLoopEndRef_v0 reader**: not exercised (D0 replaces no loop). N/A.

## The one structural fault

**Inference-over-measurement.** v4 clicked a done-button coordinate inherited from another VI copy's measured geometry instead of locating the button on *this* panel's live capture — a measurement proven to cost minutes and to be unambiguous (template score 0.00 vs next-best 28.35) the moment it was actually taken. The gate meant to protect the derivation (STEP 7) verified only the window rect and passed while the control positions differed. Counterfactual, on the clock: v5 with located clicks completed its full double-leg run in 290 s; had v4 (launched 17:25:48) located its clicks the same way, D0's done-when would have been met by ~17:31 instead of 18:13:02 — 42 minutes of the 94-minute cycle spent on the miss, its diagnosis chain (`d0v4_tmx_recheck`, `diag_d0_pickloop_liveness`, `p3_pi_query_after_d0`), and the hypothesis review the failed prediction mandated ($3.2775, `tools/bench/peer_d0v4.log:3`). The TMX-parser echo (same class, ~15 min + $2.6711) is not of the same magnitude and is not named separately. The user catching the miss live (STATUS.md:79-83) — the exact health-check failure CLAUDE.md's devil's-advocate section names — is what makes this structural rather than bad luck; the corrective rule now exists as cycle27-plan Pre-decided 9.

VIOLATION: inference-over-measurement | loss_min=42 | loss_usd=3.28 | evidence=tools/bench/drive_original_copy_v4.log:160

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-18 by the cycle-34 judgement session, per finding.

**VIOLATION `inference-over-measurement` — ACCEPTED, remedy already in force when the review was written.**
The corrective is `docs/cycle27-plan.md` Pre-decided 9 (capture → locate → act → capture → confirm; derived or
remembered coordinates are never clicked blind), implemented by `tools/bench/d0_locate.py` + `clickprobe`. It is
what turned v4's 13 pass / 3 fail into v5's 39 pass / 1 fail. The user issued the rule from the chair
(2026-09-18 17:5x) — the review is right that this is the health-check failure CLAUDE.md's devil's-advocate
section names, not bad luck. No further action; the loss figure (42 min, $3.28) stands and is counted.

**F1 REPEATED FAILURE — ACCEPTED, both instances closed.** Instance 1 (inherited click point) → Pre-decided 9
above. Instance 2 (the `TMX?=1=39.00000` parser) → closed this cycle: a normalised `PRELIMITS TMN=/TMX=` token is
now emitted at `tools/motor_send_pi.ps1:67` and consumed first in `tmx_from`'s precedence, and the parser now
carries a 16-case self-test, green (`tools/bench/tmx_selftest2.log`, `SELFTEST tmx_from: 16 pass / 0 fail`).

**F2 MISSING TOOL — ACCEPTED, both tools now exist.** `tools/bench/d0_locate.py` (built mid-cycle, one run too
late, as the review says). The PI-reply parser self-test the review asked for is `selftest_tmx`
(`tools/bench/drive_original_copy_v4.py`, `--selftest`), 16/16 as of this cycle.

**F3 UNMEASURED STEPS — ACCEPTED.** Same two instances as F1; no separate remedy.

**F4 RULE COMPLIANCE — ACCEPTED in all five parts, three of them now on record as OPEN items.**
(a) v4's gate 7 verified the wrong invariant (window rects, delta 0,0, while the control sat 63 px left and 53 px
below) — accepted; v5's gate 7 states the distinction explicitly. (b) The A3 FAIL on `tmx_selftest.log` is a
FALSE POSITIVE, as the review says: the review existed at 18:24 and the fixed rerun touched the log at 18:25:57,
making the log newer than its own review. Accepted — recorded here rather than patched, because the mtime
ordering is the audit's whole mechanism and a change to it is a device change (Pre-decided 2). (c) **C7 is
dead** — accepted, already carried as STATUS OPEN 56, and confirmed again this cycle ("C7 out-of-plan files: no
docs/cycle<N>-plan.md found"). The review's own remedy — repoint it at the `status: current` plan rather than a
per-cycle filename — is a REPAIR of an existing device, not a new one, so Pre-decided 2 does not block it; it is
in NEXT. (d) C4 understates spend because `claude -p` judgement sessions carry no COST line — accepted, OPEN 56.
(e) "No audit line can detect a PASS gate that verifies the wrong thing" — accepted as an inherent limit of
mechanical auditing, with no remedy proposed or built; it is the standing reason the retrospective layer exists.

**F5 ORDERING — ACCEPTED, no action.** The review finds the order defensible and its single ordering error is F1
restated. Prior-art ran first and actually changed the work; the retrospective ran last.

**F6 WHAT WAS NOT REPORTED — ACCEPTED, all three; (b) is escalated.**
(a) v4's first launch died in 1 s on the motor gate (`drive_original_copy_v4.log:5-7`, exit=2, run refused) and
was relaunched 30 s later — correct behaviour, unreported anywhere; recorded here.
(b) **The `Count` indicator reads 1 after three registered picks, in v4 AND v5** — v5 passes by verifying the
three red markers the VI drew instead, so the indicator's meaning was never established. The review flags that it
"could matter for D1". I agree, and D1 was unblocked this cycle, so this is now a **D1 precondition**: it is the
first measurement in STATUS `## NEXT`. Escalated, not merely noted.
(c) The $3.2775 review cost attributable to the v4 miss (`tools/bench/peer_d0v4.log:3`) appeared in no narrative;
it is now in the violation line above and counted by `violations.py`.

**F7 JUDGEMENT INSIDE A MATERIAL SESSION — the peer's own judgement ACCEPTED.** A material session edited a
Pre-decided line (`docs/cycle27-plan.md:59`), but the content was a consistency fix to a decision CLAUDE.md
already records (the 2026-09-18 D3 amendment), so no new judgement was taken. Finding, not violation, as the peer
concluded. Standing expectation restated for future cycles: `## Pre-decided` lines are edited by judgement
sessions; a material session that believes one is stale reports it and stops.

**DEVICE EFFECT — ACCEPTED as written, including the non-escalation.** Five devices worked, two were not
exercised, and C7 is DEGRADED rather than failed. I accept the reasoning that a counter which cannot count is a
defect to repair but not a `device-failed` occurrence, because no fault got through it in that window: every file
touched served D0, which was the plan. `VIOLATION: device-failed` was correctly not emitted.
