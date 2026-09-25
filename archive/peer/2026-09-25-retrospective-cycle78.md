# retrospective-cycle78

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.4406  in 130 / out 23477 / cache-create 158780 / cache-read 359400  (309s, 38 turn(s))
- **date:** 2026-09-25 08:26:40
- **outcome:** ANSWERED (311s)
- **verdict-card:** VERDICT-CARD retrospective-cycle78 verdict=none -> tools\bench\cards\verdict_retrospective-cycle78.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle78, role retrospective) ---
CLAIM: Cycle 78 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 78 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-25 07:04:53  ..  2026-09-25 08:21:27   (77 min)
    basis: start = archive/peer/2026-09-25-retrospective-cycle77.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-24 03:20): **What was built:** `tools/motor_gate.py:611` prints `FAIL: motor_gate exit N - <meaning>` on every non-zero exit, the PI/ASI senders print `FAIL:` on REJECTED / NOT-at-target, `tools/bgrun.py` + `tools/audit_cycle.py` FAILURE_RE match `^RESULT: REJECTED|NOT at target` and a non-zero `ERR?=`; `tools/bench/selftest_motor_fail_exit.py` 10/10.
  - `repeated-failure-class` (decided 2026-09-24 03:53): The no-new-device order was lifted on 2026-09-24 03:1x (the user: "猷⑦봽 ?먮떒???곕씪 ?꾩슂???꾧뎄??留뚮뱶??嫄??덉슜?좉쾶"). The device that already exists for this class is `guard_peer.py`, and on this occasion it let the retry through. The repair has two steps, in order: 1. Replay the 03:25:55 launch against `guard_peer` with the same logs, offline, and record which code path returned 0. 2. Fix that path. The self-test m??
  - `device-failed` (decided 2026-09-24 03:53): The scan is to be scoped by COMMAND, as `guard_peer` was on 2026-09-24 (STATUS OPEN 57): a run whose command is a Jev script (`tools/jev*.py`, `tools/bench/jev_*.py`) is exempt, which is the other half of the user's 2026-09-22 exemption ("Jev??硫댁젣"). The exemption goes by the command, never by the filename. Required self-test: - a Jev survey that quotes `FAIL` ends rc=0; - a non-Jev build that prin??
  - `repeated-failure-class` (decided 2026-09-24 05:54): `tools/hooks/guard_session.py` refuses `SendMessage` to a `material` or `log-reader` agent inside a cycle session (`CYCLE_SESSION=1`), with the message "dispatch a NEW foreground Agent". Every re-dispatch then blocks until it returns. Self-test: the refusal fires under `CYCLE_SESSION=1`, and the interactive chat is untouched. Scheduled after L7-1b run 3 (deliverable first).
  - `device-failed` (decided 2026-09-24 05:54): - The prior-art dispatch half is REPAIRED (05:31, bgrun `--` parsing, `selftest_stoprecord_bgrun.py` 6/0). This also CLOSES the `--recipe=` gap named in the 03:53 block above. - Still to repair: the stop record also refuses READ-ONLY commands on a stopped recipe (`wc -l`, `sed -n`, an AST parse; `material_marker.log:1256,1263,1274`). Refuse only commands that EXECUTE the recipe, and self-test both??
  - `device-failed` (decided 2026-09-24): - `stop_record.write_novel_record(recipe, review)` appends a later same-path record pre-released for the reviewed bytes; honoured only while the review file's ANSWER still reads purely `PRIOR-ART: novel` (`novel_in_answer`, re-read at every check, so a hand-edited record or a tampered review does not launder). `prior_art_review.py` writes it automatically on a novel verdict with `--recipe`; CLI `s??
  - `device-failed` (decided 2026-09-24): Three holes in three consecutive cycles (70: the prior-art dispatch; 71: dispatch under bgrun + read-only commands; 72: the launch after a novel review), each patched on its own code path. Next is not a fourth patch: the release logic is written once as a table ??record kind (blocking / novel) 횞 verdict state (undisposed / released / novel / sha-mismatch / superseded) 횞 command class (build launch??
  - `device-failed` (decided 2026-09-25 05:58): `logclass.command_kind` (card 76-2) and the Jev half (STATUS OPEN 57) already follow: `guard_peer.selftest_exempt()` excludes a run only when every in-scope script in python command position is a `selftest_*.py` whose import closure (`script_touches_labview`, transitive over tools/ and tools/bench/) never imports gscript/stagekit/pythoncom/win32com/ comtypes or calls `Dispatch("LabVIEW.Application??
  - `device-failed` (decided 2026-09-25 07:05): when it actually starts ??record in `tools/bgrun.py` at child start (the line carries the card), not in the PreToolUse hook. Self-test: a launch refused by guard_cycle and one refused by the permission layer leave the count unchanged; a started run increments it. OUTCOME (2026-09-25 07:1x, card 78-2, moved ahead of the deliverable because it blocked it: result_78-1.json): BUILT. `tools/bgrun.py` r??

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

== cycle audit, 2026-09-25 07:04 .. 2026-09-25 08:21 (77 min, an explicit cycle window): 19 build logs, 5 peer logs, 20 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 18/19 ok; NO BGRUN line in ['jev_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 8 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 18/20 annotated; blank: ['2026-09-25-const-loopterm-77.md', '2026-09-25-const-loopterm-77c.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 2207 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['drive_m8_replay_s1_78.log', 'm8b_replay_selftest78b.log', 'selftest_retry_cap.log']

  C1 builds run 19, failure markers 8, logs carrying a failure 8
  C2 peer reviews dispatched 5, archived 20
  C3 wall-clock inside bgrun, BUILDS ONLY 49 min 4 s
  C4 wall-clock inside bgrun, REVIEWS 3 min 28 s; cost $2.2749 from 2 log(s) that report one
  C4b cost lines seen 2 / parsed 2
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 52 min 32 s  (builds 93%, reviews 6%, judgement session 0%)

  C6 material-marked recipe/bench runs 26, judgement-session attempts refused 2  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 55 - docs/goalmap.json, docs/m8-real-run-plan.md, tools/bench/cards/peer_78-3_selftest_task.md, tools/bench/diag_replay_gbtest.py, tools/bench/diag_replay_slice78.py, tools/bench/drive_m8.py, tools/bench/errorlist_shots/070529_before_ctrl_e.png, tools/bench/errorlist_shots/070533_after_ctrl_e.png, tools/bench/errorlist_shots/070533_before_ctrl_l.png, tools/bench/errorlist_shots/070542_after_ctrl_l.png, tools/bench/errorlist_shots/070556_after_esc.png, tools/bench/errorlist_shots/errwin_070542.png??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 292/683 ok; 391 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 3 DANGLING of 2207 citations checked:
       docs/m3a1-severed-rows.md:87 -> tools/bench/m3a1_severed_arith.json
       docs/m3a1-severed-rows.md:89 -> tools/bench/m3a1_severed_rows.log
       docs/session-protocol.md:167 -> tools/bench/steer_state.json

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:138 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 604 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A4 every archived review says what was done with it, L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (19; read them directly, they are the primary record) ===
tools/bench/diag_replay_slice78.log  (2026-09-25 07:31:48)
tools/bench/drive_m8_replay_dry78.log  (2026-09-25 08:05:24)
tools/bench/drive_m8_replay_s1_78.log  (2026-09-25 08:10:16)
tools/bench/drive_m8_replay_s1_78b.log  (2026-09-25 08:13:35)
tools/bench/drive_m8_replay_s3_78.log  (2026-09-25 08:16:44)
tools/bench/errorlist_check_cycle78.log  (2026-09-25 07:06:00)
tools/bench/jev_gate.log  (2026-09-25 08:21:04)
tools/bench/m8b_replay_78.log  (2026-09-25 08:17:06)
tools/bench/m8b_replay_md5_78.log  (2026-09-25 08:18:48)
tools/bench/m8b_replay_selftest78.log  (2026-09-25 07:49:46)
tools/bench/m8b_replay_selftest78b.log  (2026-09-25 07:53:54)
tools/bench/m8b_replay_selftest78c.log  (2026-09-25 07:54:06)
tools/bench/motor_session_end_cycle77.log  (2026-09-25 07:04:59)
tools/bench/motor_session_start_cycle78.log  (2026-09-25 07:06:06)
tools/bench/replay_test78.log  (2026-09-25 07:30:30)
tools/bench/replay_test78b.log  (2026-09-25 07:41:23)
tools/bench/selftest_retry_cap.log  (2026-09-25 07:12:10)
tools/bench/stage_replay_78.log  (2026-09-25 07:20:53)
tools/bench/stage_replay_swap_78.log  (2026-09-25 08:04:55)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (6) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_78.log  (2026-09-25 07:06:06)
tools/bench/cycle_runner.log  (2026-09-25 07:06:06)
tools/bench/cycle_runner_main_20260925b.log  (2026-09-25 07:06:06)
tools/bench/peer_78-3-selftest.log  (2026-09-25 07:53:09)
tools/bench/priorart_replay_swap_78.log  (2026-09-25 07:52:06)
tools/bench/retro.log  (2026-09-25 08:21:27)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle78","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Cycle 78 outcome, read from the logs:** the cycle delivered what steer_77 required. The stand-in stage ran 35/0 (`tools/bench/stage_replay_78.log:136`), the swap stage ran 29/0 (`tools/bench/stage_replay_swap_78.log:81`), both replay runs passed 8/0 (`drive_m8_replay_s1_78b.log:767`, `drive_m8_replay_s3_78.log:767`) and the comparer reports 10,310 of 10,310 common rows X/Y/Z bit-identical with a non-vacuous negative control (`m8b_replay_78.log:5`, `m8b_replay_selftest78c.log:5`). The retry-cap recorder was repaired and self-tested 8/0 (`selftest_retry_cap.log:28`). Wall clock 77 min, reviews $2.27 (audit C4). I find no structural fault. The avoidable losses add up to about 19 minutes and $1.13, spread over four small items, none of which changed what the cycle produced.

## FINDINGS

**1. Repeated failure.** `diag_replay_test77.py` failed identically twice: 16 pass / 6 fail with the same first failing gate at 07:30 (`replay_test78.log:86`) and at 07:41 (`replay_test78b.log:91`). Between the two runs the offline slice diagnostic had already shown that the harness read equals column 0 of the source frame for all three calls (`diag_replay_slice78.log:3-8`, 07:31:47). The second LabVIEW run was launched 20 s later (`material_marker.log:1479`) carrying a "row-wise fix" aimed at hypothesis (a) in `result_78-2.json:29`, and it changed nothing (`replay_test78b.log:38` still reads 1024 ints). The approach should have changed at attempt 2: either a different read route (IMAQ Write File to a scratch PNG, the route PD22(c) itself names at `docs/m8-real-run-plan.md:305-307`) or the acceptance-on-column-0 ruling that judgement made anyway. Cost 556 s of LabVIEW (`replay_test78b.log:94`), about 9 min. The second row: `m8b_replay_compare.py` failed three times in a row (`m8b_replay_selftest78.log:2` endianness, `m8b_replay_selftest78b.log:9` a mistyped directory, `m8b_replay_selftest78c.log:4` the intended negative control), each in 0 s, so no cost.

**2. Missing tool.** Two absences cost money this cycle. (a) A full-frame pixel reader for the harness: the COM `GetControlValue` on the 2-D U8 indicator returns one column (`replay_test78b.log:38`), so all six PD18(a) gates failed on both runs and the requirement was later dropped rather than met (`docs/m8-real-run-plan.md:326-328`). (b) A shared tra-file reader: `drive_m8.tra_rows` already parsed these files correctly (cited in the peer task, `archive/peer/2026-09-25-78-3-selftest-endian.md:26`), but `m8b_replay_compare.py` re-implemented the parse big-endian, failed, and the Jev ladder classed it new-problem p=0.718 (`jev_gate.log:942`), buying a $1.1317 hypothesis review (`peer_78-3-selftest.log:3`) for a question a 4-byte read answers. The review said as much (`endian.md:66-68`). Also (c): the dry run of `drive_m8.py` passed with a forward-slash `--src` path (`drive_m8_replay_dry78.log:1,128`) because COM is stubbed, and the real run died 283 s later at `GetVIReference` with LabVIEW error 7 (`drive_m8_replay_s1_78.log:361-364`). A path check in the launcher or dry run would have caught it offline. Cost about 5 min plus one motor session start.

**3. Unmeasured steps.** PD23(c) drops the full-frame pixel check by inference: column 0 matches and the tracking output is identical between S1 and S3 (`m8-real-run-plan.md:326-328`). Bit-identical X/Y/Z between two replay paths shows both paths fed the kernel the same bytes; it does not show those bytes equal the source frame beyond column 0. The measurement (one harness run writing PNGs, about 10 min of LabVIEW) was named in PD22(c) and not made. Hypothesis (a) versus (b) in `result_78-2.json:29` was likewise never separated by a measurement (a 1-D reshape before the indicator would do it); the requirement was retired instead. Low risk, but it is an inference standing where a cheap measurement was specified.

**4. Rule compliance.** Broken or formal: (a) The failure budget of 2 was applied by convention in 78-3. The material session logged three failing runs plus the crash (`m8b_replay_selftest78.log`, `78b`, `78c`, `drive_m8_replay_s1_78.log`) and reported "failure 1 of 2" (`result_78-3.json:22`) by not counting offline self-tests. 78-2 counted more strictly and stopped at 2 (`result_78-2.json:23`). Two sessions, two budgets. (b) The brief rule "A brief states the MEASUREMENT, never the result-dependent ACTION" is bent by `task_78-3.json:66` ("full-frame pixel check only if no extra LabVIEW launch") and `task_78-2.json:68` ("this card is the RETRY_CARD ... if the repaired cap still needs one"). Both harmless in effect. (c) Three attempts to run `m8b_replay_compare.py` directly, outside bgrun, at 07:49:21-32 (`material_marker.log:1481-1483`) left no log; the script touches no LabVIEW so the hook allowed it, but it is the pattern the bgrun rule exists to remove. Satisfied: rule 1 (A5 md5 unchanged), rule 1a acceptance is numeric and non-vacuous, motor sessions started and ended with readback (`motor_session_start_cycle78.log:23`), LabVIEW verified gone in every run's H9, prior art before the swap build (`priorart_replay_swap_78.log:35` END 07:52:06, stage START 07:54:22).
What the audit does not cover: the judgement session's own cost (C4c reports nothing); GUI actions inside `drive_m8` bead picks and the cycle-start Error List screenshots (`errorlist_shots/070529_*` in C7), so A6 "used no GUI" is wrong for this cycle; whether SAME-ROW discharges cite a relevant review (see finding 6); whether dry runs can see launch-path faults; A1's FAIL is noise (`jev_gate.log` is not a build log); A4's two blanks are cycle-77 files (`const-loopterm-77*.md`) charged here by date granularity; C7 measures scope against `docs/cycle27-plan.md`, which is not this cycle's plan, so its 55-file list says nothing.

**5. Ordering.** Defensible, and better than the schedule it inherited. The 07:05 decision deferred the recorder repair until after the deliverable (`docs/violation-decisions.md:1243`); the very first launch at 07:07 hit that defect (`stage_runs.jsonl:6-7`, refused launches recorded; `material_marker.log:1470` PRERUN-GATE refusal) and 78-1 returned BLOCKED in 4 min. 78-2 flipped the order, and the stage was running by 07:12:33 (`stage_replay_78.log:1`). The prior-art and hypothesis reviews ran in parallel (07:50:53 and 07:50:54). The swap stage waited for the prior-art END as required. The one ordering error is inside finding 1: the second harness run before reading the slice result.

**6. What was not reported.** `next.json:6` reads "Stand-ins built 35/0. M8(b) PASS". Understated: the PD18(a) pixel gates failed 12 of 12 across two runs and the requirement was dropped, not passed; the first S1 replay launch crashed after 283 s. Not reported anywhere in the session's outputs: the SAME-ROW discharge of `drive_m8_replay_s1_78.log` cites the endianness review (`jev_gate.log:952`, "same script drive_m8"), which was about `m8b_replay_compare.py` and mentions `drive_m8` only in passing (`endian.md:26`). The failed-prediction gate was therefore released by a review of a different script and a different problem. It cost nothing this time, since the crash was a path bug fixed on the rerun, but a matcher that accepts any review mentioning the script name discharges the gate for any script named in any recent review. Also unreported: 78b's failure was a mistyped directory, not a defect (`m8b_replay_selftest78b.log:9`); and the S3 replay produced 275 more rows than S1 (`m8b_replay_78.log:5`), reported as run length without a cause.

**7. Judgement inside a material session.** Three instances, all small. (a) The material agent applied the endianness review's discriminating tests to gate G1 within 57 s of the answer (review ANSWERED 07:53:09, `peer_78-3-selftest.log:2`; G1 already carries "LE header length prefix, exponent byte at pos 7" at 07:54:06, `m8b_replay_selftest78c.log:2`). Judgement's acceptance was written afterwards (`endian.md:90`). Applying a review's prescribed measurement is material work; deciding the review was right is not, and here the order was inverted. (b) The choice between explanations (a) and (b) for the 1024-int read was acted on in material by patching the harness and re-running (`result_78-2.json:21`), under a SAME-ROW discharge rather than an our-script-bug classification (`jev_gate.log:926`). (c) Pre-scripted actions in the briefs, `task_78-3.json:66` and `task_78-2.json:68`.

## DEVICE EFFECT

- `unreported-fact` (rc guarantee): held. Every crashed run ended rc=1 (`drive_m8_replay_s1_78.log:364`, `selftest_retry_cap.log:18`, `m8b_replay_selftest78b.log:10`).
- `rule-evaded` (confirm-bait refusal): held; the one review task carried no bait and the adversarial set was appended (`endian.md:34-40`).
- `tool-not-built` (prior-art review): fired, verdict novel, and it surfaced the PD13(c) contradiction that judgement then ruled on (`priorart_replay_swap_78.log:17`, `m8-real-run-plan.md:324`).
- `repeated-failure-class` (blank "What was done with it"): both cycle-78 reviews are annotated (`endian.md:88-94`, `priorart-replay-swap-78.md:267-273`).
- `unreported-fact` (C3/C4 cost lines): 2 of 2 cost lines parsed.
- `premature-build` (guard_cycle order): held; stage after prior-art END.
- `scope-creep` (C7 list): produced, but against `docs/cycle27-plan.md`, so it flags this cycle's own plan files as out of plan. Blind, but no unjudged scope change slipped past it this cycle, so it did not fail in the sense asked.
- `device-failed` (COST regex): held. `device-failed` (bgrun FAIL scan): the logs with FAIL lines were rc=1 anyway.
- `repeated-failure-class` (OpLoopEndRef reader): not exercised.
- `device-failed` (stop record + gate, write_novel_record, release table): held; novel record written and the launch released (`priorart_replay_swap_78.log:33-34`).
- `device-failed` (motor_gate FAIL exit): not exercised; both sessions passed.
- `repeated-failure-class` (guard_peer retry path) and `device-failed` (Jev command scoping): not exercised.
- `repeated-failure-class` (guard_session refuses SendMessage): no re-dispatch attempted; all three cards were fresh foreground dispatches.
- `device-failed` (selftest_exempt closure): the failing `selftest_retry_cap.log` got a ladder line, our-script-bug p=0.964 (`jev_gate.log:923`), and was patched and rerun without a review, as designed.
- `device-failed` (recorder at bgrun child start, decided 07:05): the fault occurred once more at 07:07, before the device existed (`stage_runs.jsonl:6-7`), because the 07:05 decision scheduled it after the deliverable. Once built at 07:12 it recorded only started runs (`stage_runs.jsonl:8-9`, both `"by": "bgrun"`). A device cannot fail before it is built; the deferral cost about 5 min and was corrected inside the cycle.

None of the listed devices failed inside the window. The one mechanism that misfired, the SAME-ROW matcher in `guard_peer` (finding 6), is not on the device list and cost nothing this cycle. It should be tightened to match on the review's task script, not on any mention.

## VERDICT

The avoidable cost is 9 min (second harness run) + 5 min (path crash) + 5 min (78-1 block) + $1.13 (a review for a byte-order question). None of these changed what the cycle produced, and each was corrected on the next attempt. That is a well-run cycle with findings, not a structural fault.

VIOLATION: none

VERDICT {"schema":"verdict/1","id":"retrospective-cycle78","verdict":"none","alternative":"The second diag_replay_test77 run (556 s, identical 16/6) could be read as repeated-failure-class, but it was one attempt, refuted a named hypothesis, and did not change what the cycle produced.","discriminating_test":"Tighten guard_peer SAME-ROW to match the review's task script, then re-run the 08:10:42 discharge offline: drive_m8_replay_s1_78.log must NOT be discharged by 2026-09-25-78-3-selftest-endian.md.","violations":[],"sources":["tools/bench/replay_test78b.log:91","tools/bench/diag_replay_slice78.log:8","tools/bench/drive_m8_replay_s1_78.log:363","tools/bench/jev_gate.log:952","tools/bench/m8b_replay_78.log:5","tools/bench/stage_runs.jsonl:8","docs/m8-real-run-plan.md:326","tools/bench/peer_78-3-selftest.log:3"],"note":"Avoidable: ~19 min and $1.13 across four small items. SAME-ROW matcher discharged a drive_m8 crash with a review about m8b_replay_compare; no cost this cycle, but a hole."}

## Sources

(extract from answer)

## What was done with it

Cycle-78 judgement, 2026-09-25. **ACCEPTED: `VIOLATION: none`.** Avoidable cost ≈19 min + $1.13 across four small
items, each corrected on the next attempt. **Finding carried as a tool item, not built this cycle:** the
`guard_peer` RULE-SAME-ROW matcher discharged the `drive_m8_replay_s1_78.log` crash with a review about the
comparer (`jev_gate.log:952`). It must match the reviewed task's script. Its test is the review's own offline
re-run of the 08:10:42 discharge, which must NOT discharge. It is listed in STATUS NEXT after stage K
(deliverable first, steer_77).

FIXED: finding-6-same-row-matcher - tools/hooks/guard_peer.py:537 - RULE-SAME-ROW now matches only the review's SUBJECT script (a `Script:` line, else the first path-qualified tools/(recipes|bench)/X.py in `## Question`, exact stem after `_v\d+` strip); the offline re-run of the 08:10:42 pair no longer discharges (tools/bench/selftest_guard_peer_sameRow.log, S11, 21/0; card 79-2).
