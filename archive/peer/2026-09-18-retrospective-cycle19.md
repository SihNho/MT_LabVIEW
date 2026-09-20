# retrospective-cycle19

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-18 03:42:17
- **outcome:** ANSWERED (368s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 19 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-18 00:02:53  ..  2026-09-18 03:36:08   (213 min)
    basis: start = archive/peer/2026-09-18-retrospective-cycle17.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-18 00:02 .. 2026-09-18 03:36 (213 min, an explicit cycle window): 17 build logs, 15 peer logs, 12 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 17/17 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 4 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 12/12 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1775 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 22, failure markers 18, logs carrying a failure 4
  C2 peer reviews dispatched 15, archived 12
  C3 wall-clock inside bgrun, BUILDS ONLY 10 min 0 s
  C4 wall-clock inside bgrun, REVIEWS 260 min 47 s; cost $116.8202 from 10 log(s) that report one
  C4b cost lines seen 10 / parsed 10
  C5 total wall-clock 270 min 47 s  (reviews are 96% of it)

  C6 material-marked recipe/bench runs 38, judgement-session attempts refused 4  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs\cycle19-plan.md: 28 - STATUS.md, docs/cycle15-plan.md, docs/vi-server-ids.json, docs/violation-decisions.md, tools/bench/c19_close_release_probe.py, tools/bench/c20_release_probe.py, tools/bench/cycle18_arming_doc_lint.txt, tools/bench/cycle18_arming_driver.py, tools/bench/cycle18_doc_lint.txt, tools/bench/cycle18_stopgate_driver.py, tools/bench/diag_uid_identity.py, tools/bench/peer_task_fsit_props.txt??


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 279/419 ok; 140 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 726 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:111 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle20-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle20-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 169 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:901']

AUDIT PASS


=== BUILD LOGS INSIDE THE WINDOW (17; read them directly, they are the primary record) ===
tools/bench/c19_audit.log  (2026-09-18 02:21:41)
tools/bench/c19_audit2.log  (2026-09-18 02:27:03)
tools/bench/c19_close_release_probe.log  (2026-09-18 02:21:23)
tools/bench/c19_doc_ingest.log  (2026-09-18 02:24:47)
tools/bench/c20_release_probe.log  (2026-09-18 03:33:41)
tools/bench/cycle18_arming.log  (2026-09-18 00:52:18)
tools/bench/cycle18_stopgate.log  (2026-09-18 00:39:33)
tools/bench/diag_uid_identity.log  (2026-09-18 03:16:53)
tools/bench/probe_flatseq_offline.log  (2026-09-18 01:29:42)
tools/bench/probe_flatseq_offline2.log  (2026-09-18 01:30:27)
tools/bench/probe_flatseq_offline3.log  (2026-09-18 01:32:00)
tools/bench/probe_flatseq_outer.log  (2026-09-18 02:06:01)
tools/bench/probe_flatseq_walk.log  (2026-09-18 01:36:29)
tools/bench/probe_flatseq_walk_run2.log  (2026-09-18 01:52:59)
tools/bench/probe_walk_stop_control.log  (2026-09-18 02:07:55)
tools/bench/selftest_guard_cycle_fixed.log  (2026-09-18 02:47:14)
tools/bench/selftest_guard_cycle_rerun.log  (2026-09-18 02:47:29)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (16) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_1.log  (2026-09-18 00:11:53)
tools/bench/cycle_2.log  (2026-09-18 00:59:06)
tools/bench/cycle_3.log  (2026-09-18 01:13:54)
tools/bench/cycle_4.log  (2026-09-18 02:30:02)
tools/bench/cycle_5.log  (2026-09-18 02:30:02)
tools/bench/cycle_runner.log  (2026-09-18 02:30:02)
tools/bench/cycle_runner_main_20260917.log  (2026-09-18 02:30:02)
tools/bench/peer_c20_audit_a1.log  (2026-09-18 02:46:42)
tools/bench/peer_cycle18_t6.log  (2026-09-18 00:38:26)
tools/bench/peer_fsit_props.log  (2026-09-18 01:36:36)
tools/bench/peer_walk_run1_dual.log  (2026-09-18 01:49:50)
tools/bench/peer_walk_run2_dual.log  (2026-09-18 02:03:59)
tools/bench/priorart_check_a_wiring.log  (2026-09-18 01:12:34)
tools/bench/priorart_fstunnel.log  (2026-09-18 03:13:17)
tools/bench/retro.log  (2026-09-18 02:28:21)
tools/bench/retro_cycle19.log  (2026-09-18 03:36:08)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle19-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

The most costly structural fault was cycle-boundary ordering: cycle 20 began at 02:30 while cycle 19’s retrospective, started at 02:28, had produced neither an outcome nor an end marker. The evidence window therefore includes 66 minutes of next-cycle work and at least $8.1295 in priced reviews. A second finding is mandatory because the `premature-build` device demonstrably failed its refusal case.

## Findings

1. **Repeated failure.** The same failure class did not recur unchecked. Walk attempt 1 failed C2 and C5 because its paths were wrong ([probe_flatseq_walk.log:21](tools/bench/probe_flatseq_walk.log:21), [probe_flatseq_walk.log:62](tools/bench/probe_flatseq_walk.log:62)); the approach changed immediately after attempt 1 to an adversarial dual review and an instrumented attempt 2. Attempt 2 passed 9/9 ([probe_flatseq_walk_run2.log:174](tools/bench/probe_flatseq_walk_run2.log:174)). Its interpretation then failed—reaching an outer tunnel was mistaken for crossing it—and again the next action changed to targeted outer-tunnel and stop-object probes rather than a third blind walk ([2026-09-18-walk-run2-flatseq-crossing-codex.md:80](archive/peer/2026-09-18-walk-run2-flatseq-crossing-codex.md:80), [probe_flatseq_outer.log:27](tools/bench/probe_flatseq_outer.log:27)). Attempt 1 was the correct change point, and it was honored.

2. **Missing tool.** The missing primitive was the UID-addressed `FlatSequenceInnerTunnel`/`FlatSequenceOuterTunnel` reader. Its absence stopped 14 of 18 previously measured border walks and affected 32 of 43 in-scope sites ([2026-09-18-priorart-check-a-wiring.md:295](archive/peer/2026-09-18-priorart-check-a-wiring.md:295), [2026-09-18-priorart-check-a-wiring.md:340](archive/peer/2026-09-18-priorart-check-a-wiring.md:340)). It would have answered which tunnel face the walk reached, the continuation wire, and whether the trace genuinely crossed the flat-sequence boundary. That absence changed the cycle’s endpoint: planned done meant check A covering all 43 sites ([cycle19-plan.md:66](docs/cycle19-plan.md:66)), but the hand-off says nothing was built and check A moved to cycle 21 ([STATUS.md:53](STATUS.md:53), [STATUS.md:88](STATUS.md:88)). This is principally an ordering finding: the prior measurement already exposed the missing primitive before check A was scoped.

3. **Unmeasured steps.** The initial check-A design ignored cheap existing measurements: cached terminal data, the three enumerated coerce nodes, and the already-terminating flat-sequence continuation rule ([2026-09-18-priorart-check-a-wiring.md:269](archive/peer/2026-09-18-priorart-check-a-wiring.md:269), [2026-09-18-priorart-check-a-wiring.md:293](archive/peer/2026-09-18-priorart-check-a-wiring.md:293)). The prior-art gate caught this before construction, so no bad check was built. Separately, the claim that T6 had previously passed rested on a prose “6/6” statement rather than per-test output; the later disposition records that T6 had never been measured passing ([2026-09-18-cycle18-t6-regression-codex.md:184](archive/peer/2026-09-18-cycle18-t6-regression-codex.md:184)). After those points, the cycle generally measured rather than inferred: live traversal, class attachment, negative controls, and unchanged hashes were all recorded.

4. **Rule compliance.**

   - Hardware discipline was respected: no motor or serial action appears, and the live diagnostic reports both originals and the donor op byte-identical afterward ([diag_uid_identity.log:54](tools/bench/diag_uid_identity.log:54)).
   - Prior art correctly stopped the proposed check-A build; the material session wrote no release and built nothing ([2026-09-18-priorart-check-a-wiring.md:321](archive/peer/2026-09-18-priorart-check-a-wiring.md:321)).
   - The failure-review rule was followed after both failed predictions.
   - The material/judgement separation was not respected semantically: material dispositions accepted review findings and chose/run result-dependent actions, discussed under finding 7.
   - The one-cycle ordering rule was broken formally: the first cycle-19 retrospective has only a start record ([retro.log:54](tools/bench/retro.log:54)), while the next judgement cycle began two minutes later ([cycle_5.log:1](tools/bench/cycle_5.log:1)).
   - Documentation closure was only formal: final lint still reports STATUS at 111 lines against the 110-line limit in the attached audit.

   The audit does not test whether material sessions made judgement decisions, whether one cycle began before the preceding retrospective completed, whether a regex recognizes decorated failure markers, or whether a review disposition’s reasoning is sound. A4 is also filename-date scoped rather than exact-window scoped, as the audit itself warns.

5. **Ordering.** Running prior art before building was defensible and valuable. The bad ordering was at the cycle boundary: cycle 20 started at 02:30 before cycle 19 had a completed retrospective. Had the runner waited at 02:30, cycle 19 would have ended there instead of absorbing work through 03:36. Within check A, the reader prerequisite should also have been recognized at planning time because the existing border measurement already showed the continuation rule terminating ([2026-09-18-priorart-check-a-wiring.md:295](archive/peer/2026-09-18-priorart-check-a-wiring.md:295)).

6. **What was not reported.** The largest hidden fact is that walk attempt 1 printed two failed gates yet ended `rc=0`: C2 failed at line 22, C5 failed at line 62, and bgrun reported success at line 114 ([probe_flatseq_walk.log:22](tools/bench/probe_flatseq_walk.log:22)). The session still noticed and reviewed the failures, so this did not corrupt the technical conclusion, but the mechanical record falsely classified the batch. The closing summary also understated the boundary problem: it said the retrospective was dispatching, while its log never acquired an outcome/end before the next cycle started.

7. **Judgement inside a material session.** Yes. The run-1 disposition says the review was “accepted in full” and every fix was applied before the next run by the material session ([2026-09-18-walk-run1-path-constants-opus.md:186](archive/peer/2026-09-18-walk-run1-path-constants-opus.md:186)). The run-2 dispositions similarly accepted the central objection and immediately selected and ran the prescribed tests ([2026-09-18-walk-run2-flatseq-crossing-codex.md:163](archive/peer/2026-09-18-walk-run2-flatseq-crossing-codex.md:163), [2026-09-18-walk-run2-flatseq-crossing-opus.md:162](archive/peer/2026-09-18-walk-run2-flatseq-crossing-opus.md:162)). Accepting/rejecting review findings and choosing the next experiment are explicitly reserved to judgement by [CLAUDE.md:287](CLAUDE.md:287). I do not rank this separately because the selected experiments were useful and no independently measurable loss follows.

## Device effect

| Device | Result this window |
|---|---|
| Runner inner-exit propagation | Failed on the decorated `**FAIL` records: the batch still ended `rc=0` ([probe_flatseq_walk.log:22](tools/bench/probe_flatseq_walk.log:22), [probe_flatseq_walk.log:114](tools/bench/probe_flatseq_walk.log:114)). |
| Confirm-bait refusal/adversarial prompt | Worked. Failed-prediction questions explicitly demanded refutation ([2026-09-18-walk-run1-path-constants-codex.md:71](archive/peer/2026-09-18-walk-run1-path-constants-codex.md:71)). |
| Prior-art review | Worked. It found four non-novel conditions and the stopped artifact was not created ([2026-09-18-priorart-check-a-wiring.md:307](archive/peer/2026-09-18-priorart-check-a-wiring.md:307), [2026-09-18-priorart-check-a-wiring.md:321](archive/peer/2026-09-18-priorart-check-a-wiring.md:321)). |
| Undisposed-review gate | Worked for the final audit: all 12 archived reviews were annotated. |
| Build/review cost split | Worked: the attached audit separately reports 10 build minutes and 260:47 review minutes. |
| `premature-build` gate | Failed. T6 expected refusal and got allowance ([cycle18_stopgate.log:102](tools/bench/cycle18_stopgate.log:102)). The later repaired test passes 6/6 with the negative proof ([selftest_guard_cycle_fixed.log:32](tools/bench/selftest_guard_cycle_fixed.log:32)). |
| Scope counter | Worked by exposing 28 out-of-plan files; it did not prevent the scope expansion because it is deliberately advisory. |
| Cost-regex self-check | Worked: the attached audit reports 10 cost lines seen and 10 parsed. |
| `FAIL` inner-failure scan | Failed because its regex did not match `**FAIL`; bgrun consequently returned success ([probe_flatseq_walk.log:112](tools/bench/probe_flatseq_walk.log:112), [probe_flatseq_walk.log:114](tools/bench/probe_flatseq_walk.log:114)). |
| `OpLoopEndRef_v0` reader | Not exercised: no stop-terminal diagnosis occurred in this window. |
| Stop record + launch gate | Worked. The check-A review stopped the unwritten tool, and the later cycle-20 release probe showed a valid release without clearing the stored record ([c20_release_probe.log:8](tools/bench/c20_release_probe.log:8), [c20_release_probe.log:20](tools/bench/c20_release_probe.log:20)). |

For the `premature-build` failure, the directly attributable cycle-19 diagnosis session ran 887 seconds and cost $8.9402475. Had the refusal case worked when exercised at 00:39, the 00:59–01:13 T6 diagnosis session would not have been needed and check-A work could have begun about 15 minutes earlier.

VIOLATION: wrong-ordering | loss_min=66 | loss_usd=8.1295 | evidence=tools/bench/cycle_5.log:1
VIOLATION: device-failed | loss_min=15 | loss_usd=8.9402475 | evidence=premature-build@tools/bench/cycle18_stopgate.log:102

## Sources

(extract from answer)

## What was done with it

**Run by the cycle-20 step-2 MATERIAL session at 03:36-03:42, because `guard_cycle` refused the step-2 build:
17 build logs stood since the cycle-17 retrospective (budget 10) and NO retrospective existed for cycle 18 or
cycle 19** (`tools/bench/retro_cycle19.log`, `BGRUN END rc=0 after 370s`; the gate's own remedy line). **Cycle
18's retrospective is still missing.**

Its two slugs are RECORDED here, not accepted or rejected — that is judgement's call, and this session did not
make it:

- `VIOLATION: wrong-ordering | loss_min=66 | loss_usd=8.1295 | evidence=tools/bench/cycle_5.log:1`
- `VIOLATION: device-failed | loss_min=15 | loss_usd=8.9402475 | evidence=premature-build@tools/bench/cycle18_stopgate.log:102`

**Consequence, measured immediately after:** `py tools/violations.py`'s tally reached **`wrong-ordering` 8
occurrences (threshold 3)**, so `guard_cycle` now refuses the cycle-20 step-2 build a second time and asks for a
dated `DECISION: device` / `DECISION: no-device` block in `docs/violation-decisions.md`. Rounds 1 and 2 both
answered `no-device` (`docs/violation-decisions.md:45-53`, `:165-177`), and round 2 says in writing: *"On a
further repeat, escalate to a re-plan with the user rather than to a device."* Writing that block is JUDGEMENT's,
so the build stayed unlaunched and the question went back up. Nothing else in this review was acted on.
