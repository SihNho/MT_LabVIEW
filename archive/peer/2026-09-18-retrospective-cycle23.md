# retrospective-cycle23

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-18 13:27:41
- **outcome:** ANSWERED (279s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 23 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-18 03:42:17  ..  2026-09-18 13:23:01   (581 min)
    basis: start = archive/peer/2026-09-18-retrospective-cycle19.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-18 03:42 .. 2026-09-18 13:23 (581 min, an explicit cycle window): 18 build logs, 25 peer logs, 28 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 18/18 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 8 logs recorded a failure; unreviewed: ['diag_fstunnel_wireterms_panel.log', 'selftest_cycle_runner_ff.log']
  FAIL  A4 every archived review says what was done with it: 23/28 annotated; blank: ['2026-09-18-ff-selftest-bgrun-start-regex-codex.md', '2026-09-18-ff-selftest-bgrun-start-regex-opus.md', '2026-09-18-ff-selftest-drycmd-split-codex.md', '2026-09-18-ff-selftest-drycmd-split-opus.md', '2026-09-18-stopgate-priorart-deadlock-codex.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1775 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 23, failure markers 16, logs carrying a failure 8
  C2 peer reviews dispatched 25, archived 28
  C3 wall-clock inside bgrun, BUILDS ONLY 34 min 52 s
  C4 wall-clock inside bgrun, REVIEWS 620 min 19 s; cost $145.3674 from 13 log(s) that report one
  C4b cost lines seen 13 / parsed 13
  C5 total wall-clock 655 min 11 s  (reviews are 94% of it)

  C6 material-marked recipe/bench runs 64, judgement-session attempts refused 16  <- delegate to the `material` agent instead

  C7 out-of-plan files: no docs/cycle<N>-plan.md found - scope cannot be checked mechanically


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 280/436 ok; 156 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 750 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 11 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 104 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle21-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle21-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 172 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:915']

AUDIT VIOLATIONS: A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (18; read them directly, they are the primary record) ===
tools/bench/build_opfstunnelterm_v0.log  (2026-09-18 09:01:19)
tools/bench/build_opfstunnelterm_v0_run2.log  (2026-09-18 09:03:28)
tools/bench/build_opfstunnelterm_v1_run1.log  (2026-09-18 10:53:22)
tools/bench/c21_release_probe.log  (2026-09-18 09:49:39)
tools/bench/c21_tail.log  (2026-09-18 09:52:50)
tools/bench/c22_gate_probe.log  (2026-09-18 10:28:45)
tools/bench/c22_v1_gate_probe.log  (2026-09-18 10:50:16)
tools/bench/diag_fstunnel_orphan_timeline.log  (2026-09-18 12:39:32)
tools/bench/diag_fstunnel_orphans.log  (2026-09-18 11:05:42)
tools/bench/diag_fstunnel_preclean_twins.log  (2026-09-18 12:33:33)
tools/bench/diag_fstunnel_rbwvictims.log  (2026-09-18 11:56:14)
tools/bench/diag_fstunnel_wire_semantics.log  (2026-09-18 09:24:08)
tools/bench/diag_fstunnel_wirebroken.log  (2026-09-18 11:45:02)
tools/bench/diag_fstunnel_wireterms_panel.log  (2026-09-18 13:14:50)
tools/bench/diag_fstunnel_wireterms_panel_run2.log  (2026-09-18 13:18:12)
tools/bench/ffcompile.log  (2026-09-18 13:04:31)
tools/bench/selftest_cycle_runner_ff.log  (2026-09-18 13:15:50)
tools/bench/sweep_nodeterms_3state.log  (2026-09-18 09:40:49)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (25) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_10.log  (2026-09-18 13:05:22)
tools/bench/cycle_11.log  (2026-09-18 13:05:23)
tools/bench/cycle_5.log  (2026-09-18 03:56:02)
tools/bench/cycle_6.log  (2026-09-18 09:13:20)
tools/bench/cycle_7.log  (2026-09-18 10:24:57)
tools/bench/cycle_8.log  (2026-09-18 11:30:39)
tools/bench/cycle_9.log  (2026-09-18 11:30:39)
tools/bench/cycle_runner.log  (2026-09-18 13:05:22)
tools/bench/cycle_runner_main_20260917.log  (2026-09-18 03:56:02)
tools/bench/cycle_runner_main_20260918.log  (2026-09-18 11:30:39)
tools/bench/cycle_runner_main_20260918b.log  (2026-09-18 13:05:22)
tools/bench/peer_ff_selftest2_dual.log  (2026-09-18 11:46:10)
tools/bench/peer_ff_selftest_dual.log  (2026-09-18 11:37:08)
tools/bench/peer_fstunnel_v1_b4_dual.log  (2026-09-18 11:20:53)
tools/bench/peer_fstunnel_wire_fail.log  (2026-09-18 09:08:18)
tools/bench/peer_fstunnel_wirechecked.log  (2026-09-18 10:21:55)
tools/bench/peer_orphans_empty.log  (2026-09-18 12:50:10)
tools/bench/peer_prose_runner_stop.log  (2026-09-18 03:57:02)
tools/bench/peer_retro_window_semantics.log  (2026-09-18 09:08:55)
tools/bench/peer_stopgate_deadlock.log  (2026-09-18 10:12:54)
tools/bench/priorart_fstunnel-v2-preclean.log  (2026-09-18 12:18:31)
tools/bench/retro.log  (2026-09-18 13:03:08)
tools/bench/retro_cycle18.log  (2026-09-18 03:46:51)
tools/bench/retro_cycle19.log  (2026-09-18 03:42:17)
tools/bench/retro_cycle23.log  (2026-09-18 13:23:01)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle23-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

The cycle’s main structural fault was inference over a cheap existing measurement. After `diag_fstunnel_rbwvictims` saw no **node** endpoint for wires 894/1356, the session promoted that into “the donor ships orphan wires,” designed v2 around pre-cleaning them, and paid for review and firefighter work. The direct endpoint read later showed both wires had node and front-panel ends at the fresh-copy checkpoint; deleting nodes 145/151 created the loose ends (`tools/bench/diag_fstunnel_wireterms_panel_run2.log:37-53`, `:61-69`).

Had `panel_wiring` plus each wire’s own `Wire.Terms[]` been run immediately after the 11:56 rbwvictims result, the measured two-run sequence indicates the answer would have arrived around 12:00. The erroneous direction instead survived until the cycle was killed/replaced at 12:59. Directly attributable priced work was the v2 prior-art review ($4.7805), the failed-prediction review ($5.1740), and the v2 firefighter session ($10.3798): $20.3343 total.

A second, mandatory device finding is the cost-audit device. Although the audit claims an exact 03:42:17–13:23:01 window, it counted all 5,160 seconds of `cycle_5.log`, which began at 02:30:02 (`tools/bench/cycle_5.log:1`, `:53`). That imports 72 minutes from before the stated window. The $39.8614 log cost (`tools/bench/cycle_5.log:52`) cannot safely be time-prorated, so the dollar loss is unknown.

## Findings

1. **Repeated failure.** The v0 wire-count failure occurred identically on attempts 1 and 2 (`tools/bench/build_opfstunnelterm_v0.log:66-80`; `tools/bench/build_opfstunnelterm_v0_run2.log:66-80`). Attempt 2 was the correct change point, and the session did change to a discriminating wire-semantics measurement rather than launching attempt 3. The later v1 B4 failure likewise led to diagnostics, not another blind rebuild.

2. **Missing tool.** No missing reader caused the dominant loss. `Wire.Is Broken?` was already built, and `panel_wiring` was already verified; the peer explicitly identifies the latter as the cheapest existing test (`archive/peer/2026-09-18-fstunnel-orphans-empty-at-ckpt00-opus.md:143-164`). The failure was choosing a node-only reader, not failing to build another tool.

3. **Unmeasured steps.** The load-bearing claim was inferred from `Diagram.Nodes[]`. The raw log even showed `Terminal.Owner = TopLevelDiagram` and an `Indicator` census exception (`tools/bench/diag_fstunnel_rbwvictims.log:75-88`), yet the cycle concluded “no terminal.” The later timeline proved the fresh-copy orphan set was empty and became `{894,1356}` immediately after deleting nodes 145/151 (`tools/bench/diag_fstunnel_orphan_timeline.log:16-27`); the panel read then identified the other endpoints (`tools/bench/diag_fstunnel_wireterms_panel_run2.log:37-53`).

4. **Rule compliance.** Original-file, hardware, checksum, bgrun, failure-budget, and no-GUI rules were respected. The material/judgement split was not clean: the material session produced the 187-line v2 design after its own hand-off said the consequence was “judgement’s call” (`archive/2026-09-18-status-cycle23-close.md:19-20`, `:24`, `:28-40`). Cycle closure was also violated semantically: cycles 6–8 exited while reviews or retrospectives were still pending despite the runner brief requiring retrospective completion before exit (`tools/bench/cycle_6.log:32-38`, `tools/bench/cycle_runner_main_20260918.log:2-4`). The audit does not test decision ownership, whether cycles overlap unfinished reviews, the truth of endpoint interpretations, or exact time clipping within a log.

5. **Ordering.** The endpoint read belonged immediately after rbwvictims attempt 1, before v2 was written or reviewed. Instead, the cycle wrote pre-clean logic and purchased prior-art review first (`archive/2026-09-18-status-cycle23-close.md:28-43`, `:57-67`). The 975-second original-VI sweep occurred before step 2 closed, contrary to the plan’s dependency (`docs/cycle21-plan.md:31-48`), although it ran while the blocked review path was pending and produced reusable evidence, so I do not rank it as structural loss.

6. **What was not reported.** The cycle summary understated that “orphan” meant only “not present in the node-terminal census.” It also did not foreground that the prior-art review found four issues but emitted no machine-readable verdict, leaving the launch gate unarmed (`archive/2026-09-18-status-cycle23-close.md:57-67`). Finally, the audit’s 655-minute/$145.3674 headline includes pre-window work from cycle 5 and therefore is not an exact-window total.

7. **Judgement inside material.** Yes. The stop-gate review disposition says the material session accepted findings and executed the selected dispatch route (`archive/peer/2026-09-18-stopgate-priorart-deadlock-opus.md:169-205`). More consequentially, cycle-23 material designed the v2 pre-clean after the evidence record itself reserved the interpretation for judgement (`archive/2026-09-18-status-cycle23-close.md:19-40`). I do not rank this separately because its measurable loss is already captured by the inference fault.

## Device effect

- Runner inner-exit propagation: no failing build was falsely reported successful in-window.
- Confirm-bait refusal/adversarial review: no evasion found.
- Prior-art checklist: it found four v2 defects before launch, but its absent machine verdict left the stop record unarmed; no prohibited recipe launch followed.
- Undisposed-review gate: A4 found five blank dispositions, but none establishes a later same-kind prior-art/retrospective dispatch that this specific gate should have refused.
- Build/review cost separation: **failed** by importing 72 pre-window minutes from `cycle_5.log`.
- Premature-build gate: worked; v2 never launched before its review completed.
- Scope counter: could not operate because `docs/cycle23-plan.md` does not exist. That is an evidence gap, but the available record does not establish out-of-plan work strongly enough to count a second device failure.
- Cost-regex repair: worked, 13/13 cost lines parsed.
- Inner `FAIL` scanner: no false-success recurrence. Its self-test briefly false-positive-classified a passing line (`tools/bench/selftest_cycle_runner_ff.log:31-36`) and was immediately corrected and rerun (`:37-41`); it was not routinely bypassed.
- `OpLoopEndRef_v0`: the stop-condition fault did not recur.
- Stop-record/launch gate: no recipe launched against a blocking verdict; the v2 arming omission was exposed before launch.

VIOLATION: inference-over-measurement | loss_min=59 | loss_usd=20.3343 | evidence=tools/bench/diag_fstunnel_rbwvictims.log:80
VIOLATION: device-failed | loss_min=72 | loss_usd=? | evidence=tools/bench/cycle_5.log:1

## Sources

(extract from answer)

## What was done with it

(cycle-24 firefighter, 2026-09-18 13:5x)

- `VIOLATION: inference-over-measurement` — ACCEPTED. Answered in `docs/violation-decisions.md` (2026-09-18
  13:45, round 1, `DECISION: no-device` under the user's standing 08:53 no-device order). The behavioural remedy
  had already landed before this disposition: `tools/recipes/build_opfstunnelterm_v2.py` was rewritten around the
  MEASURED timeline (gates A0a/A0h/A0c/A0d assert only machine-read values), and its first run
  (`tools/bench/build_opfstunnelterm_v2_run1.log`, 2026-09-18 13:36, BGRUN END rc=0) passed 38/38 gates — the
  A0h repair removed exactly [894, 1356], terminals unchanged, ExecState 0 → 1, on both ops.
- `VIOLATION: device-failed` (audit cost window imported 72 pre-window minutes from `tools/bench/cycle_5.log`) —
  ACCEPTED AS A FINDING. The fault is real: `audit_cycle` counts a log wholly by its mtime falling in the window,
  not by clipping its own start stamp. Under the standing no-device order the fix is NOT built this cycle; it is
  recorded as an OPEN item in STATUS.md for the user/judgement to schedule (repairing an existing device is a
  bug fix, but the order is read narrowly until the user says otherwise).
- Findings 4/7 (judgement-in-material in cycle 23) — noted; not re-answered here because the firefighter brief
  explicitly suspended the material hand-off for this one cycle, and the slug's count lives in
  `tools/violations.py`, not in this disposition.
