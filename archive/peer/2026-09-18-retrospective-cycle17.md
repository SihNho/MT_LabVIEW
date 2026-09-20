# retrospective-cycle17

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-18 00:02:53
- **outcome:** ANSWERED (352s)
- **why asked:** mandatory end-of-cycle retrospective, cycle 17 (first cycle run by `tools/cycle_runner.py`).
- **verdict:** ACCEPTED

## What was done with it

Disposed by the cycle-17 JUDGEMENT session, 2026-09-18.

**`VIOLATION: device-failed | loss_min=23 | loss_usd=4.8500` — ACCEPTED, not contested.** The evidence is
concrete: the prior-art review said route-B run 3 "was NOT executed" because it could not pass its own gate, and
the recipe launched six seconds after that disposition anyway, with the flagged branches disabled while its
success gate still required them. `py tools/violations.py` now reports **device-failed = 4, threshold 1,
"DUE, no decision on file"** — the only slug awaiting a response.

**The named fault is the one that is actionable: the prior-art device can check that a review HAPPENED and was
disposed, but nothing binds the recipe LAUNCH to the review's verdict.** `FIXED:`/`REFUTED:` release lines exist
and are machine-checked, but no gate requires a launch to be covered by one. That is the hole, and closing it is
cycle 18's first task (STATUS `## NEXT`).

**No `DECISION: device` block was written into `docs/violation-decisions.md` today, deliberately.** That file
discharges a slug, and the device does not exist yet; writing the block now would be exactly the "a promise is
not a fix" laundering CLAUDE.md warns about. The block gets written by the cycle that builds the device, citing it.

Findings accepted without a slug, and where each went:
- **F6, the contradiction in STATUS's hardware block** (human header still read "분해 ← WE ARE HERE" while the
  paragraph and the machine key `rig-state:` read 조립) — **FIXED in STATUS.md this cycle.** Safety-relevant: a
  cold session reading the header alone would have concluded motors were unrestricted.
- **Device effect "scope counter: failed observably because no cycle-17 plan existed"** — correct and now fixed
  forward: `docs/cycle18-plan.md` created, `docs/cycle15-plan.md` demoted to `status: paused` so exactly one
  cycle plan is current. The runner's cycles previously had no `docs/cycle<N>-plan.md` at all, so C7 could never
  check scope for any of them.
- **F6's second half, the census progression not being reported** (51–52 unknown callees → 11 UNKNOWN → 11
  `ASSUMED_MOTION`) — accepted; the progression is recorded in `docs/motor-call-site-census.md`.
- **F1's stamp-window self-test point and F4's two unreviewed failing logs** (`read_motor_anchor` exit 6, the
  motor-gate self-test misclassified) — accepted as accurate. Both predate this cycle's work and are not
  re-opened here; the misclassification itself was already repaired (`rc` → `code`).
- **The window-boundary correction** (run 2's log starts 24 s before the declared boundary) — accepted, noted,
  no action.

Not accepted: nothing. The one thing worth recording against the report is that it is day-granular on A4 and
counts `motor_gate.log` as a launched batch when it is an append-only decision ledger — the report says so itself.

## Question

RETROSPECTIVE (v2) of cycle 17 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-17 16:17:58  ..  2026-09-17 23:56:59   (459 min)
    basis: start = archive/peer/2026-09-17-retrospective-cycle15-routeb.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-17 16:17 .. 2026-09-17 23:57 (459 min, an explicit cycle window): 21 build logs, 10 peer logs, 71 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 20/21 ok; NO BGRUN line in ['motor_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 5 logs recorded a failure; unreviewed: ['read_motor_anchor.log', 'selftest_motor_gate.log']
  FAIL  A4 every archived review says what was done with it: 57/71 annotated; blank: ['2026-09-17-d0-bandpass-click-was-delivered-hwnd-token.md', '2026-09-17-d0-bandpass-hwnd-token-agy.md', '2026-09-17-d1-s1-diagram-count.md', '2026-09-17-d1-s1-stale-in-memory-copy.md', '2026-09-17-d1-s3-stale-traverse-index.md', '2026-09-17-d1-s3b-uid-reuse-after-delete.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1775 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 26, failure markers 17, logs carrying a failure 5
  C2 peer reviews dispatched 10, archived 71
  C3 wall-clock inside bgrun, BUILDS ONLY 76 min 8 s
  C4 wall-clock inside bgrun, REVIEWS 110 min 5 s; cost $22.7543 from 5 log(s) that report one
  C4b cost lines seen 5 / parsed 5
  C5 total wall-clock 186 min 13 s  (reviews are 59% of it)

  C6 material-marked recipe/bench runs 27, judgement-session attempts refused 36  <- delegate to the `material` agent instead

  C7 out-of-plan files: no docs/cycle<N>-plan.md found - scope cannot be checked mechanically


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 276/404 ok; 128 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 675 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 11 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 110 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle15-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle15-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 159 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:901']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (21; read them directly, they are the primary record) ===
tools/bench/asi_xy_check_X.log  (2026-09-17 23:10:44)
tools/bench/asi_xy_check_Y.log  (2026-09-17 23:11:00)
tools/bench/bench_prep_run3.log  (2026-09-17 17:47:54)
tools/bench/build_d1_routeb_v0_run2.log  (2026-09-17 16:27:50)
tools/bench/build_d1_routeb_v0_run3.log  (2026-09-17 18:01:49)
tools/bench/diag_sr_transport.log  (2026-09-17 17:51:20)
tools/bench/motor_census.log  (2026-09-17 23:34:47)
tools/bench/motor_census_run2.log  (2026-09-17 23:40:23)
tools/bench/motor_census_run3.log  (2026-09-17 23:52:37)
tools/bench/motor_gate.log  (2026-09-17 23:11:00)
tools/bench/motor_move_pi_0.log  (2026-09-17 23:09:29)
tools/bench/motor_move_pi_30.log  (2026-09-17 23:07:31)
tools/bench/motor_move_pi_35.log  (2026-09-17 23:07:53)
tools/bench/preexperiment_guard.log  (2026-09-17 18:55:19)
tools/bench/read_motor_anchor.log  (2026-09-17 23:02:47)
tools/bench/read_pi_after.log  (2026-09-17 23:07:58)
tools/bench/selftest_cycle_runner.log  (2026-09-17 20:04:17)
tools/bench/selftest_guard_session.log  (2026-09-17 20:04:07)
tools/bench/selftest_motor_gate.log  (2026-09-17 22:03:21)
tools/bench/selftest_stamp_window.log  (2026-09-17 17:20:25)
tools/bench/visa_class_probe.log  (2026-09-17 23:29:32)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (10) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_1.log  (2026-09-17 23:18:33)
tools/bench/cycle_runner_main_20260917.log  (2026-09-17 23:18:33)
tools/bench/peer_open31_window.log  (2026-09-17 16:57:29)
tools/bench/peer_open31b_stamp.log  (2026-09-17 17:17:18)
tools/bench/peer_stall_preexp.log  (2026-09-17 20:03:18)
tools/bench/peer_zdz_wirecut.log  (2026-09-17 18:16:17)
tools/bench/priorart_opgeterrors.log  (2026-09-17 16:56:00)
tools/bench/priorart_routeb_run3.log  (2026-09-17 17:43:45)
tools/bench/retro.log  (2026-09-17 23:56:59)
tools/bench/stall_pid25164_181319.log  (2026-09-17 18:17:40)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle17-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

The cycle’s dominant structural fault was the failure of the prior-art stop device. The review explicitly said the recipe “was NOT executed” because it could not pass its own gate and would waste roughly 550 seconds ([prior-art disposition:376-380](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-17-priorart-routeb-run3-opus.md:376)). Six seconds after that disposition, route-B run 3 nevertheless started ([run 3:1](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run3.log:1)), reproduced the predicted three no-routes, failed the deliberately disabled queue gate, and ended nonzero ([run 3:407](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run3.log:407), [run 3:541](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run3.log:541)). Its failed-prediction review then consumed another 781 seconds and $4.8500 ([peer log:86](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/peer_zdz_wirecut.log:86), [peer log:152](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/peer_zdz_wirecut.log:152)).

Counterfactual: had the prior-art stop been honored when its disposition completed at approximately 17:52:43, the route-B branch would have ended then instead of after the Z/dZ review at approximately 18:16:17. That saves 23 minutes and the logged $4.8500.

## Findings

1. **Repeated failure.** Route-B attempt 3 was where the approach should have changed—indeed, the prior-art review had already changed it to “hand the register-placement question back to judgement.” Attempt 2 had exhausted the stated two-run budget ([OpGetErrors review:206-211](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-17-priorart-opgeterrors-codex.md:206)); attempt 3 then returned the same 63 wired/3 no-route ledger and added a guaranteed-failing queue gate ([run 3:407-410](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run3.log:407)). The stamp-window self-test also failed on attempts 1 and 2 before a third run passed ([self-test:17-18](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.log:17), [self-test:33-34](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.log:33), [self-test:53-54](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.log:53)); that formally exceeded the material-session failure budget, although the third attempt itself cost under a minute.

2. **Missing tool.** No missing reader was the principal cost driver. `VI.Get Errors` remained unbuilt, but the prior-art device correctly established that it was not authorized before save/F1/F2 and stopped it ([OpGetErrors disposition:377-393](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-17-priorart-opgeterrors-opus.md:377)). `OpLoopEndRef_v0` also answered the original-loop question: loop #637 retained terminal 648 and wire 3457 ([run 3:416](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run3.log:416)). The expensive failure was ignoring existing evidence, not lacking a reader.

3. **Unmeasured steps.** Run 3 inferred a new Z/dZ explanation after the recipe itself already stated that moving a control terminal cuts its wire and moving it back does not restore it ([recipe:35-41](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v0.py:35)). The prior-art review also showed that the proposed type sources were already recorded as unnamed, making the new gate predictably impossible ([prior-art review:285-298](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-17-priorart-routeb-run3-opus.md:285)). A file read should have replaced the build.

4. **Rule compliance.**

   - Broken: the two-failure budget and the rule that review acceptance/design decisions belong to judgement ([CLAUDE.md:256-259](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/CLAUDE.md:256)).
   - Evaded formally: prior art stopped the two new branches, but the whole recipe was then run with those branches disabled while its success gate still required them.
   - Broken formally: two failing logs lacked a newer archived review—`read_motor_anchor` initially exited 6 ([anchor log:1-8](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/read_motor_anchor.log:1)) and the motor-gate self-test was falsely classified as failed ([self-test:145-148](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/selftest_motor_gate.log:145)).
   - Satisfied: original hashes remained unchanged; every bgrun terminated; live moves went through the gate and remained inside its recorded envelope ([motor gate:51-58](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/motor_gate.log:51), [motor gate:67-82](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/motor_gate.log:67)).

   The audit does not cover semantic obedience to a review stop, whether a material session made judgement decisions, computation equivalence, or whether hardware permission text was internally consistent. Its A4 result is also day-granular: the six named blank reviews were written around 02:40–07:29, outside this 16:17–23:56 window. A1 counts `motor_gate.log`, which is an append-only decision ledger rather than a launched batch. C7 could not check scope at all because `docs/cycle17-plan.md` does not exist; `STATUS.md` instead names cycle 15 ([STATUS.md:13](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/STATUS.md:13)).

5. **Ordering.** The early ordering was defensible through the prior-art review. The first indefensible step was running attempt 3 after that review had predicted its failure and handed the open design question to judgement. The correct next step was the judgement decision on register placement or the eight-row queue type-source design—not another baseline replay. Conversely, the later cycle-runner start was reasonably deferred until the experiment ended.

6. **What was not reported.** `STATUS.md` says only that run 3 “changed NOTHING” ([STATUS.md:70-71](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/STATUS.md:70)); it understates that the result was predicted by a stopping review and cost 23 minutes plus $4.8500. It also compresses the motor census’s progression from 51–52 unknown callees ([census:76-116](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/motor_census.log:76)), to 11 unknowns ([run 2:92-103](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/motor_census_run2.log:92)), to 11 conservatively relabelled `ASSUMED_MOTION` ([run 3:97-115](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/motor_census_run3.log:97)). Finally, the human-readable hardware header still says “disassembled/we are here,” while the later paragraph and machine key say assembled ([STATUS.md:38-52](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/STATUS.md:38)); the gate used the machine key, but the hand-off is internally contradictory.

7. **Judgement inside material.** Yes. The open31 material disposition says it “ACCEPTED almost in full,” withdrew an explanation, selected which findings survived, and made four changes ([open31 disposition:176-200](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-17-open31-window-codex.md:176)). The route-B material disposition likewise says findings were “CONFIRMED,” “accepted, and acted on,” changed authorization flags and rewrote the plan, while acknowledging that the remaining choice belonged to judgement ([route-B disposition:383-417](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-17-priorart-routeb-run3-opus.md:383)). Those are acceptance/design decisions reserved by `CLAUDE.md:256-257`, although I do not rank this separately because it is part of the same causal event as the failed prior-art stop.

## Device effect

- **Runner exit propagation:** worked; real build failures ended nonzero.
- **Confirm-bait refusal:** worked; hypothesis prompts carried the adversarial instruction set.
- **Prior-art review:** failed. It fired, correctly predicted the run could not pass, was marked disposed, and was then worked around by executing the recipe anyway.
- **Undisposed-review gate:** no in-window recurrence. The audit’s six blanks predate this window.
- **Separate cost reporting:** worked; the priced logs carried costs and the audit parsed 5/5.
- **Premature-build timing gate:** worked only narrowly—the build began after review completion. It could not enforce the review’s semantic stop.
- **Scope counter:** failed observably because no cycle-17 plan existed, so C7 reported that scope could not be checked.
- **Cost-regex repair:** worked; no silent cost miss was reported.
- **Inner-failure scan:** failed once in the opposite direction. A 70/70 passing test was converted to `rc=1` because expected refusal return codes were mistaken for failures ([self-test:145-148](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/selftest_motor_gate.log:145)); renaming the displayed field from `rc` to `code` made the next identical test pass ([self-test:204-226](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/selftest_motor_gate.log:204)). That is a two-minute workaround, but not comparable to the main 23-minute loss.
- **`OpLoopEndRef_v0`:** the original-stop fault did not recur; the original loop was read directly. The three new loops were correctly recorded as unwired ([run 3:416-420](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run3.log:416)).

One boundary correction: run 2’s log started at 16:17:34, 24 seconds before the declared 16:17:58 boundary ([run 2:1](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/build_d1_routeb_v0_run2.log:1)). Its mtime puts the log in the supplied list, but those first 24 seconds are not cycle-17 cost under the exact-window contract.

VIOLATION: device-failed | loss_min=23 | loss_usd=4.8500 | evidence=prior-art-review-device@tools/bench/build_d1_routeb_v0_run3.log:542

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
