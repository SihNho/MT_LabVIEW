# retrospective-cycle47

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.4906  in 12 / out 26060 / cache-create 131795 / cache-read 551596  (358s, 13 turn(s))
- **date:** 2026-09-19 23:49:30
- **outcome:** ANSWERED (360s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 47 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-19 19:20:53  ..  2026-09-19 23:43:29   (263 min)
    basis: start = archive/peer/2026-09-19-retrospective-cycle43.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-19 19:20 .. 2026-09-19 23:43 (263 min, an explicit cycle window): 16 build logs, 18 peer logs, 29 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 14/16 ok; NO BGRUN line in ['t2_rsrc_blockdiff.log', 't2_rsrc_probe.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 6 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 28/29 annotated; blank: ['2026-09-19-stall-selftest-c39-g78.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 21, failure markers 37, logs carrying a failure 6
  C2 peer reviews dispatched 18, archived 29
  C3 wall-clock inside bgrun, BUILDS ONLY 28 min 45 s
  C4 wall-clock inside bgrun, REVIEWS 305 min 43 s; cost $156.5358 from 11 log(s) that report one
  C4b cost lines seen 11 / parsed 11
  C5 total wall-clock 334 min 28 s  (reviews are 91% of it)

  C6 material-marked recipe/bench runs 50, judgement-session attempts refused 10  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 17 - STATUS.md, tools/bench/peer_census_notfail_task.md, tools/bench/s0_op_census.py, tools/bench/s1_savedcopy_census.py, tools/bench/s1_subvi_paths.py, tools/bench/selftest_stoprecord_supersession.py, tools/bench/static_audit_recipe.py, tools/bench/t2_rsrc_blockdiff.py, tools/bench/t2_rsrc_probe.py, tools/bench/task_s1_savedcopy.md, tools/bench/task_t2_rsrc_format.md, tools/bench/wait_bgrun_end.py??


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 282/499 ok; 217 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 1065 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  WARN  L2b cited line numbers are in range: 1 citation(s) point past the end of the file: ['docs/NAMES.md:1022 -> docs/toolkit-capabilities.md:775 (file has 675 lines)']
  WARN  L3 STATUS.md stays one screen: STATUS.md:112 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 257 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:597', 'docs/NAMES.md:870', 'docs/NAMES.md:884', 'docs/NAMES.md:902', 'docs/NAMES.md:929']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (16; read them directly, they are the primary record) ===
tools/bench/census_syntax.log  (2026-09-19 20:36:17)
tools/bench/s0_op_census.log  (2026-09-19 20:37:35)
tools/bench/s0b_mutonly_profile.log  (2026-09-19 21:01:20)
tools/bench/s0b_refleak_profile.log  (2026-09-19 20:51:08)
tools/bench/s1_savedcopy_census.log  (2026-09-19 22:11:32)
tools/bench/s1_subvi_paths.log  (2026-09-19 22:33:15)
tools/bench/selftest_stoprecord_exempt.log  (2026-09-19 22:51:21)
tools/bench/selftest_stoprecord_supersession_post.log  (2026-09-19 19:31:27)
tools/bench/selftest_stoprecord_supersession_pre.log  (2026-09-19 19:31:02)
tools/bench/stage_d1_s1.log  (2026-09-19 21:51:04)
tools/bench/static_audit_s1.log  (2026-09-19 22:55:00)
tools/bench/static_audit_s1_v2.log  (2026-09-19 23:03:50)
tools/bench/t2_rsrc_blockdiff.log  (2026-09-19 23:29:28)
tools/bench/t2_rsrc_probe.log  (2026-09-19 23:25:04)
tools/bench/t2_rsrc_probe_run.log  (2026-09-19 23:25:04)
tools/bench/t2_rsrc_run.log  (2026-09-19 23:27:08)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (18) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_29.log  (2026-09-19 19:22:34)
tools/bench/cycle_30.log  (2026-09-19 19:51:54)
tools/bench/cycle_31.log  (2026-09-19 21:08:15)
tools/bench/cycle_32.log  (2026-09-19 23:11:59)
tools/bench/cycle_33.log  (2026-09-19 23:40:04)
tools/bench/cycle_34.log  (2026-09-19 23:40:05)
tools/bench/cycle_runner.log  (2026-09-19 23:40:04)
tools/bench/cycle_runner_main_20260919a.log  (2026-09-19 23:40:04)
tools/bench/cycle_runner_main_20260919b.log  (2026-09-19 23:43:28)
tools/bench/peer_census_notfail.log  (2026-09-19 20:34:10)
tools/bench/peer_s1_savedcopy.log  (2026-09-19 22:09:38)
tools/bench/peer_staticaudit_falsepos.log  (2026-09-19 23:02:24)
tools/bench/peer_t2_rsrc_format.log  (2026-09-19 23:27:55)
tools/bench/priorart_d1_s1_stage.log  (2026-09-19 21:33:09)
tools/bench/priorart_s0_decomp.log  (2026-09-19 19:35:38)
tools/bench/priorart_s0_gamma1.log  (2026-09-19 20:23:52)
tools/bench/retro.log  (2026-09-19 23:43:28)
tools/bench/retro_c43.log  (2026-09-19 19:20:53)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle47-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

All evidence is in hand. Here is the retrospective of cycle 47 (window 2026-09-19 19:20:53 → 23:43:29).

## Verdict first

This window did real work: the stop-record release deadlock was repaired and self-tested (30/0 + 29/0, `tools/bench/selftest_stoprecord_exempt.log`), S0 was closed on a three-arm measurement, S1 phases A/B ran and produced the cold-link finding (`tools/bench/stage_d1_s1.log:83`), the saved-copy and subVI-path censuses landed, and T2's offline RSRC block diff discharged Pre-decided 29(h) with the original's md5 unchanged (`tools/bench/t2_rsrc_run.log:406-414`). But the cycle ended with its deliverable foreclosed: the fully released, ALLOW-stamped, 6/0-audited S1 CD launch was refused at 23:16 by `guard_cycle`'s stale-retrospective branch (`archive/2026-09-19-status-cycle47-relocate.md:16`), and `claudeDev\D1_s1_copy.vi` still does not exist — the second consecutive cycle to lose the same launch to the same hook (STATUS.md:82).

**The one structural fault is a recorded failure class recurring for the fourth, fifth and SIXTH time: a backgrounded `retrospective.py` dispatch killed by its spawning session's exit.** `tools/bench/retro.log:380-388` shows three in-window dispatches with no `BGRUN END`: `--cycle 45` at 21:05:16 (the cycle_31 judgement cell exited at 21:08:15, `tools/bench/cycle_31.log:62`), `--cycle 46` at 23:06:43 (cycle_32 exited 23:11:59, `cycle_32.log:62`), and `--cycle 47` at 23:37:14 (cycle_33 exited 23:40:04, `cycle_33.log:62`). This is the exact class the cycle-39 retrospective named as its Fault 1 with the rule quoted in capitals (`retro.log:231`), and OPEN 54(b) already prescribed the fix. The third in-window kill is the damning one: it was performed by the same session that had, minutes earlier, written the remedy down — the relocate file's §5 table of what a session may use to wait, including the working `Monitor` route (`archive/2026-09-19-status-cycle47-relocate.md:129-138`) — and then dispatched at 23:37 and exited anyway. The class only ended when the runner itself launched the retrospective from its own process at 23:43:28 (`retro.log:389`), the shape that should have been adopted at the first in-window attempt. Because kills #4/#5 left nothing archived, the newest retrospective at 23:16 was still cycle 43's, and the gate refused the launch exactly as designed.

Counterfactual, on the clock: a completed retrospective of this vintage takes 287–365 s (`retro.log:119`, `:169`, `:215`). Had the 21:05:16 dispatch been held open ~6 minutes, `retrospective-cycle45.md` lands ~21:12; the 23:16 CD launch then passes the gate, and — phases A/B having taken 351 s (`stage_d1_s1.log:117`) — `D1_s1_copy.vi` plausibly exists before the 23:43 window end instead of the cycle closing on "S1 HAS STILL NEVER RUN". The measurable in-window loss is the 27-minute tail from the 23:16 refusal to window end, spent on salvage work; the real loss is the deliverable deferred a full further cycle. No log prices the kills — a killed cell writes no COST line, the known blind spot — so the dollar figure is honestly unknown.

## FINDINGS

**1. Repeated failure.** The killed-retro class, above. The approach should have changed at the 21:05:16 dispatch — attempt #4 of a class whose fix was already written in OPEN 54(b) after attempts #1–3 (STATUS.md:63-72) — to either holding the turn open on `Monitor` or handing the launch to the runner, as 23:43:28 finally did. A second, derived repetition: cycle 46 lost the same S1 launch to the budget branch and cycle 47 to the stale branch of the same hook (`archive/2026-09-19-status-cycle47-relocate.md:112-116`) — two consecutive cycles ending at `guard_cycle` for want of an archived retrospective.

**2. Missing tool.** A retrospective launcher owned by a process that outlives the judgement session. `tools/bench/wait_bgrun_end.py` was written in-window but a judgement session is refused from running it by `guard_bash`'s judgement-vs-material gate (relocate §5 table, line 136); the `Monitor` route was only verified in the window's last hour. The runner-owned launch at `retro.log:389` is precisely the missing op, demonstrated one cycle too late; its absence is what converted three cheap 6-minute waits into a lost deliverable.

**3. Unmeasured steps.** Two inferences where measurement was cheap, both corrected in-window by measurement, to the cycle's credit: (a) the first material session's "the ORIGINAL cannot be read", inferred from three refusals and falsified by measuring a fourth route (relocate §4) — it was nearly carried into NEXT as a blocker; (b) the prior NEXT's claim that the launch blocker was `CYCLE_BUILD_BUDGET` and that "the retrospective just archived resets that count" — reading `retro.log` for END lines showed no retrospective had been archived at all (relocate §1). The +920 B LIvi/LIbd cause remains an inference but is honestly recorded as OPEN with its discriminating test named (relocate §3).

**4. Rule compliance.** The audit's A1 FAIL is a false positive, not a breach: `t2_rsrc_blockdiff.py` and `t2_rsrc_probe.py` ran under bgrun — the BGRUN lines are in the wrapper logs `t2_rsrc_run.log:420` and `t2_rsrc_probe_run.log:1`; the two flagged files are the scripts' own artefact logs. A4's blank `2026-09-19-stall-selftest-c39-g78.md` is a real annotation miss, minor, outside the disposal device's priorart/retrospective scope. The genuinely broken rule is OPEN 54(b)/rule 2c's "hold the turn open", three times (the violation). What the audit does NOT cover: killed machinery dispatches — A2 scans build logs only, so it printed "all runs accounted for" over three dead retrospectives; and C4's "REVIEWS" bucket is mostly not reviews — $132.59 of its $156.54 is the four judgement cells themselves (`cycle_30..33.log`, `total_cost_usd` 18.17 + 45.42 + 53.93 + 15.07), with peers and prior-art only $23.94, and cycle_29's $58.91 straddling the window boundary counted nowhere. "Reviews are 91% of wall-clock" is really "orchestration sessions are".

**5. Ordering.** Defensible. The stop-record repair (19:31) had to precede the release, the release the static audit, the audit the launch; S0 closure and the S1 A/B measurements in between were plan work; T2 after the 23:16 refusal was the correct salvage — gate-free, offline, and it discharged 29(h). The only true inversion is the violation restated: the retro debt should have been retired the moment it was first dispatched, since every subsequent build log re-armed the stale branch.

**6. What was not reported.** (a) The record everywhere says FIVE retrospectives have died (relocate §5, STATUS.md:63); by window end it was six — the 23:37:14 kill postdates that text and appears in no summary, only in `retro.log:386-388`. (b) No narrative states that judgement-cell spend now dominates peer spend roughly 8:1 in this window ($191.50 across cycle_29–33 vs $23.94). (c) STATUS presents S1 phases A/B as proven while the machine record of that run is `BGRUN END rc=1` at a fatal gate (`stage_d1_s1.log:117-118`) — the gate text itself licenses reading the difference as the sought finding, but a reader reconciling failure counts will hit the contradiction. (d) T2's first two blockdiff attempts failed their own parser self-checks (rc=1 twice, `t2_rsrc_run.log:20-29`, `:237-246`) before the clean third run; STATUS reports only the final "14 self-checks 0 fail".

**7. Judgement inside a material session.** None found. C6 shows the boundary device active in the right direction (50 material-marked runs, 10 judgement-session attempts refused). The T2 disposition — 29(h) discharged, promotion deliberately not widened — is signed as the cycle-47 judgement session's (relocate §3), and the S6-unsound finding from `peer_staticaudit_falsepos` was left OPEN and flagged rather than accepted in a material cell (relocate §2).

## DEVICE EFFECT

- **`unreported-fact` (rc-wrapper scan):** held — no rc=0-over-failure in-window; both T2 parser failures and stage B's gate FAIL forced rc=1 honestly.
- **`rule-evaded` (confirm-bait refusal):** not exercised; the three hypothesis dispatches went out under the adversarial role (`peer_census_notfail.log:1`).
- **`tool-not-built` (prior-art review):** worked — three dispatches, and `priorart-d1-s1-stage` was released through six `FIXED:` citations rather than bypassed (relocate §2).
- **`repeated-failure-class` (blank-disposition refusal):** held within its scope; A4's one blank is a stall-selftest kind the device does not gate — the same scope leak prior retrospectives noted.
- **`unreported-fact` (C3/C4 cost split):** worked, C4b 11/11 — it is what makes this review's cost argument possible at all.
- **`premature-build` (`guard_cycle`):** fired at 23:16 exactly per spec — three dead retrospectives upstream meant no archived review existed; refusing was its design, not a wrong-thing fire.
- **`scope-creep` (C7):** worked for the first time on record — a 17-file out-of-plan list against `docs/cycle27-plan.md`, after cycles of blindness to the plan-numbering scheme.
- **`device-failed` (cost-regex self-test):** held (11/11 parsed).
- **`device-failed` (bgrun FAIL-scan):** held — every in-window rc=1 was a genuine failure.
- **`repeated-failure-class` (`OpLoopEndRef_v0`):** not exercised — no loop replacement in-window.
- **`device-failed` (stop record + launch gate):** borderline but not failed in this window: the second half of its release deadlock was repaired at 19:31 (30/0 + 29/0) and the gate then printed ALLOW through its documented supersession route; the refusal that necessitated the repair predates this window's start (relocate §2), and charging it here would violate the evidence-window rule.

No device met the failure bar inside the window. The mechanism behind the violation is unguarded by design — the user's 2026-09-18 08:53 no-new-devices order stands, so the killed-retro class has only a prose rule between it and a seventh recurrence; the runner-owned launch at `retro.log:389` is the first shape that removes the session from the loop, and whether it becomes the standing shape is the judgement question this review hands forward.

VIOLATION: repeated-failure-class | loss_min=27 | loss_usd=? | evidence=tools/bench/retro.log:386

## Sources

(extract from answer)

## What was done with it

Written 2026-09-20 by the cycle-48 judgement session, which `guard_peer.py:237-242` blocked until this section
existed — the same block is what cost runner-cycle 34 its whole cycle ($3.93, 11 min, STATUS NEXT unchanged,
`tools/bench/cycle_runner.log`). Per finding: accepted and where it landed, or refuted with the reason.

| finding | disposition |
|---|---|
| **Structural fault / 1. Repeated failure** — a backgrounded `retrospective.py` killed by its spawning session's exit, 6th recurrence (`--cycle 45` 21:05:16, `--cycle 46` 23:06:43, `--cycle 47` 23:37:14) | **ACCEPTED, and already CLOSED by a repair of an existing device, not by a new one.** `tools/cycle_runner.py land_retrospective()` (2026-09-19 23:43) re-runs any `--cycle N` START that has no END, from the runner process, which outlives the session. Its first firing is this review's own existence: `tools/bench/retro.log:389` START → `:439 BGRUN END rc=0 after 362s`, logged `RETRO-LANDED` at `tools/bench/cycle_runner.log:56`. The slug `repeated-failure-class` is recorded in `docs/violation-decisions.md`; the 3-of-a-slug device threshold is SUSPENDED by the user's 2026-09-18 08:53 standing order, so **no device is built**. |
| **2. Missing tool** — a retrospective launcher owned by a process outliving the judgement session | **ACCEPTED; it exists, and it is that same repair.** `tools/bench/wait_bgrun_end.py` stays refused to judgement sessions by `guard_bash`'s judgement-vs-material gate, and that is now right rather than a gap: with `land_retrospective()` in place a session no longer holds its turn open for the retrospective at all — it launches under bgrun, writes NEXT, exits. |
| **3. Unmeasured steps** — "the ORIGINAL cannot be read" and "the blocker is `CYCLE_BUILD_BUDGET`", both falsified in-window | **ACCEPTED.** Both corrections are already carried in STATUS: the ORIGINAL *is* readable via `py tools/bgrun.py --material … -- python -u <script>` (`archive/2026-09-19-status-cycle47-relocate.md` §4) and the budget was the wrong branch (§3). The standing rule that answers this class is Pre-decided 21(f) — a claim about our own code quotes the CALLEE, not the call site. No device (2026-09-18 08:53). |
| **4. Rule compliance** — A1's FAIL is a false positive; the real breach is OPEN 54(b) "hold the turn open", three times; `audit_cycle` C4 charges judgement cells to the REVIEWS bucket ($132.59 of $156.54, peers/prior-art only $23.94) | **ACCEPTED in full; none of it is repaired.** The C4 mis-attribution was already on record (retrospective-cycle31 F4, carried as a rider on STATUS OPEN 44) and stays a known-weak check under the no-more-devices order. 54(b) is answered for the retrospective specifically by `land_retrospective()`; it still binds every OTHER backgrounded dispatch, and this cycle follows it for the S1 run. |
| **5. Ordering** — "the only true inversion is the retro debt not being retired at its first dispatch" | **REFUTED for a SESSION; accepted for the RUNNER.** A session cannot retire that debt: `tools/hooks/guard_bash.py:226-227` calls `mark_retro_done()` on ANY `retrospective.py` in command position — before the allow/deny decision, so even a REFUSED call ends the session's ability to dispatch — and `guard_session.py` then refuses every `material`/`log-reader` dispatch for the rest of it. That is exactly how cycle 47 lost its cycle (STATUS OPEN 54(a)). The debt belongs to the RUNNER, which is what `land_retrospective()` now does. Acted on literally, this finding reproduces the failure it describes. |
| **6. What was not reported** — (a) the sixth kill at 23:37:14 appears in no summary; (b) judgement-cell spend dominates peer spend ~8:1 ($191.50 vs $23.94); (c) STATUS presents S1 A/B as proven while the record is `BGRUN END rc=1` at a fatal gate (`stage_d1_s1.log:117-118`); (d) T2's first two blockdiff attempts failed rc=1 twice | **ACCEPTED (a), (b), (d); (c) ACCEPTED AS A WORDING DEFECT ONLY.** (a) is now on record here. (b) goes to the user in STATUS NEXT — a cost fact only they can act on, not a process fault. (c) the arm's substantive claim does not rest on that runner's exit code: `claudeDev\D1_s1arm_savetest.vi` exists and was measured independently by T2's offline RSRC block diff against the ORIGINAL (45 blocks each side, 43 byte-identical, 2 differing = `LIvi`/`LIbd` only), so "a COM save under preload produced a file" is measured; "phases A/B passed" is a different sentence and STATUS must not carry it as the same one. Recorded as an OPEN wording item; it does not block the CD launch. (d) recorded. |
| **7. Judgement inside a material session** — none found; the boundary device works in the right direction (50 material runs, 10 judgement attempts refused) | **NOTED. Nothing owed.** |
| **DEVICE EFFECT** — no device met the failure bar in the window; `guard_cycle` fired exactly per spec at 23:16; `scope-creep` (C7) worked for the first time on record | **ACCEPTED.** The 23:16 refusal was `guard_cycle` working correctly; the cost belonged to the runner not yet owning the retrospective launch, and that is the gap now closed. No `device-failed` slug is owed. |

**Device effect, as disposed:** one slug named (`repeated-failure-class`), already answered by an existing repair.
The user's 2026-09-18 08:53 order suspends the 3-of-a-slug threshold, so it is recorded as a FINDING in
`docs/violation-decisions.md` and **no device is built this cycle**.
