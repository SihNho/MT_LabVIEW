# retrospective-cycle77

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.9605  in 194 / out 26821 / cache-create 171703 / cache-read 733777  (351s, 47 turn(s))
- **date:** 2026-09-25 07:04:53
- **outcome:** ANSWERED (353s)
- **verdict-card:** NO-VERDICT: $.note: 316 chars > limit 300
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle77, role retrospective) ---
CLAIM: Cycle 77 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 77 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-25 05:41:59  ..  2026-09-25 06:58:57   (77 min)
    basis: start = archive/peer/2026-09-25-retrospective-cycle76.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-25 07:05): when it actually starts ??record in `tools/bgrun.py` at child start (the line carries the card), not in the PreToolUse hook. Self-test: a launch refused by guard_cycle and one refused by the permission layer leave the count unchanged; a started run increments it.

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

== cycle audit, 2026-09-25 05:41 .. 2026-09-25 06:58 (77 min, an explicit cycle window): 15 build logs, 10 peer logs, 17 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 14/15 ok; NO BGRUN line in ['jev_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 6 logs recorded a failure; unreviewed: ['jev_gate.log']
  FAIL  A4 every archived review says what was done with it: 15/17 annotated; blank: ['2026-09-25-const-loopterm-77.md', '2026-09-25-const-loopterm-77c.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 2180 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 4 log(s) with a run that printed none: ['selftest_guard_peer_77.log', 'selftest_guard_peer_77_failre.log', 'selftest_guard_peer_77_ladder.log', 'selftest_guard_peer_77_samerow.log']

  C1 builds run 20, failure markers 7, logs carrying a failure 6
  C2 peer reviews dispatched 10, archived 17
  C3 wall-clock inside bgrun, BUILDS ONLY 25 min 25 s
  C4 wall-clock inside bgrun, REVIEWS 9 min 45 s; cost $8.6746 from 5 log(s) that report one
  C4b cost lines seen 5 / parsed 5
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 74 min 36 s; cost $26.0346 from 1 log(s) - cycle_77.log
  C5 total wall-clock 109 min 46 s  (builds 23%, reviews 8%, judgement session 67%)

  C6 material-marked recipe/bench runs 14, judgement-session attempts refused 8  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 107 - docs/m8-real-run-plan.md, tools/bench/.stall_samples.txt, tools/bench/build_op_const_loopterm_77.py, tools/bench/diag_replay_graph77.py, tools/bench/diag_replay_lib.py, tools/bench/diag_replay_test77.py, tools/bench/drive_m8.py, tools/bench/drive_m8_s1s3.py, tools/bench/errorlist_shots/054342_before_ctrl_e.png, tools/bench/errorlist_shots/054347_after_ctrl_e.png, tools/bench/errorlist_shots/054347_before_ctrl_l.png, tools/bench/errorlist_shots/054356_after_ctrl_l.png??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 292/680 ok; 388 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 3 DANGLING of 2188 citations checked:
       docs/m3a1-severed-rows.md:87 -> tools/bench/m3a1_severed_arith.json
       docs/m3a1-severed-rows.md:89 -> tools/bench/m3a1_severed_rows.log
       docs/session-protocol.md:167 -> tools/bench/steer_state.json

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:136 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 603 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, A4 every archived review says what was done with it, L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (15; read them directly, they are the primary record) ===
tools/bench/const_loopterm_77.log  (2026-09-25 05:59:43)
tools/bench/const_loopterm_77c.log  (2026-09-25 06:04:36)
tools/bench/const_loopterm_77d.log  (2026-09-25 06:10:57)
tools/bench/errorlist_check_cycle77.log  (2026-09-25 05:44:15)
tools/bench/jev_gate.log  (2026-09-25 06:58:41)
tools/bench/m8_s1s3_77.log  (2026-09-25 06:52:14)
tools/bench/m8_s1s3_77_dry.log  (2026-09-25 06:33:53)
tools/bench/motor_session_end_cycle76.log  (2026-09-25 05:43:13)
tools/bench/motor_session_start_cycle77.log  (2026-09-25 05:44:20)
tools/bench/replay_graph77.log  (2026-09-25 06:12:13)
tools/bench/selftest_guard_peer_77.log  (2026-09-25 05:49:43)
tools/bench/selftest_guard_peer_77_failre.log  (2026-09-25 05:49:38)
tools/bench/selftest_guard_peer_77_ladder.log  (2026-09-25 05:49:38)
tools/bench/selftest_guard_peer_77_measure.log  (2026-09-25 05:50:17)
tools/bench/selftest_guard_peer_77_samerow.log  (2026-09-25 05:49:37)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (10) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_76.log  (2026-09-25 05:43:08)
tools/bench/cycle_77.log  (2026-09-25 06:58:57)
tools/bench/cycle_runner.log  (2026-09-25 05:44:20)
tools/bench/cycle_runner_main_20260925b.log  (2026-09-25 05:44:20)
tools/bench/outcome_77.log  (2026-09-25 06:29:54)
tools/bench/peer_const_loopterm_77.log  (2026-09-25 05:56:48)
tools/bench/peer_const_loopterm_77c.log  (2026-09-25 06:08:57)
tools/bench/peer_replay_graph77.log  (2026-09-25 06:21:33)
tools/bench/priorart_replay_77.log  (2026-09-25 06:18:44)
tools/bench/retro.log  (2026-09-25 06:58:57)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle77","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

Reading is done. Writing the review now: the top fault is the retry-cap ledger, and everything else goes into findings.

# RETROSPECTIVE, cycle 77 (05:41:59–06:58:57)

## Verdict in one paragraph

Cycle 77 produced real things: a `guard_peer` repair with a 25/0 self-test, a cold-verified constant verb, a ready stand-in stage, and six real rig runs of S1 versus S3 with INDEX rows and a user question. It also ended with its own plan's first act at zero runs because a mechanical device counted three launches that never happened. That is the one structural fault. It is `device-failed`, threshold 1.

## THE FAULT: the retry-cap ledger counts launches that a later gate refuses

**What happened, on the clock.**

| time | event | source |
|---|---|---|
| 06:22:18 | card 77-4 launches `stage_replay_standins.py`; guard_bash allows and RECORDS it; guard_cycle then refuses (three DUE slugs) | `tools/hooks/material_marker.log:1455`, `tools/bench/stage_runs.jsonl:3`, `result_77-4.json:3` |
| 06:26:04 | card 77-5 relaunches; recorded again; guard_cycle refuses (outcome review overdue) | `material_marker.log:1457`, `stage_runs.jsonl:4`, `result_77-5.json:3` |
| 06:55:36 | card 77-7 relaunches; cap says 2 of 2 used; refused | `material_marker.log:1465`, `result_77-7.json:3` |
| 06:56:53 | card 77-8 with RETRY_CARD, compound Bash form; recorded (card 77-8 spent); permission layer refuses | `stage_runs.jsonl:5`, `result_77-8.json:8-10` |
| 06:57:00 | same launch in PowerShell; cap says 3 runs and card 77-8 already spent; refused | `material_marker.log:1467`, `result_77-8.json:10` |
| 06:58:41 | retrospective launched; stage never ran, `stage_replay_77.log` does not exist | `jev_gate.log:918`, `result_77-8.json:9` |

The device's own docstring admits the hole: a launch refused by a later hook or the permission layer "is over-counted (logged as a known limit)" (`tools/hooks/guard_bash.py:387-389`). A known limit in a cap that consumes judgement cards is not a limit, it is a defect, and this cycle it consumed the cycle's deliverable act. The judgement session recorded it correctly at `docs/violation-decisions.md:1236-1246` and scheduled the repair after cycle 78's run. That scheduling is defensible under steer_77; the fault still happened inside this window.

**Two contributing device misfires, same slug.** First, the 06:22 refusal was on a decision that already existed: card 77-1 had written the `device-failed` block at 05:58 with the time "05:5x", the gate's regex needs HH:MM, and the block silently read as undecided (`docs/violation-decisions.md:1194`, `result_77-4.json:3`). Without that misfire only one refused launch would have been counted and the 06:55 launch would have passed with no retry card at all. Second, the stop record refused a read-only `wc -l` and `grep` on the stopped recipe at 06:19:17 (`material_marker.log:1454`), which is exactly the hole the 2026-09-24 05:54 decision said was "still to repair" and the 27-row decision table was supposed to close.

**Loss.** Measured waste inside the window: cards 77-7 and 77-8, 3 + 4 minutes by their own `cost.minutes` (`result_77-7.json:16`, `result_77-8.json:17`), plus the judgement turns between 06:53 and 06:58. No log prices those turns separately; `cycle_77.log:119` gives only the session total of $26.03. Deferred, not lost: a stage run budgeted at 40 minutes plus a 30-minute test.

**Counterfactual.** Had `stage_runs.jsonl` been written at bgrun child start instead of in the PreToolUse hook, the 06:55:36 launch would have found 0 of 2 used and started the stage at 06:56; the cycle would have ended around 07:40–07:50 with PD18(a) numbers or a measured failure. Instead it ended at 06:58 with the act carried to cycle 78, which must pay a fresh judgement session to reach the same launch line.

## FINDINGS

**1. Repeated failure.** Two classes recurred. (a) `build_op_const_loopterm_77.py` ran four times on three different own-script bugs: unbranched wire at 05:57 (`const_loopterm_77.log:8`), stale diagram index at 05:58 (`:25`), teardown 1149 at 06:03 (`const_loopterm_77c.log:15`), clean at 06:09 (`const_loopterm_77d.log:19`). Total LabVIEW time 4.5 minutes, so not structural, but run 3 needed a judgement card and run 4 existed only to produce a clean record after the review said the try/except was too broad (`archive/peer/2026-09-25-const-loopterm-77c.md:44`). At run 2 the approach should have become an offline dry pass of the script's own gates before any further launch; the rule that says so (CLAUDE.md "Stages are SIMULATED", decision 1) covers stages, not bench builds, and the cycle used the gap. (b) The compound-command permission refusal recurred in 77-5 (`result_77-5.json:6`), 77-7 (`:6`), 77-8 (`:8`) and 27 times in the judgement session's own denial list (`cycle_77.log:119`, `permission_denials`). It should have changed at the first material refusal at 06:25: write the working launch shape into the card. STATUS NEXT finally does that at line 73, after the last refusal burned the retry card.

**2. Missing tool.** Three, none built. (a) A header lint for `docs/violation-decisions.md`: one line in `doc_lint` saying "block at :1193 has no parseable HH:MM" would have prevented the 06:22 refusal. (b) An enum-constant reader: `#581` is an EnumConstant and `read_const` returns text '' repr 0 (`replay_graph77.log:25-26`); the FIXED release at `archive/peer/2026-09-25-priorart-priorart-c77-replay.md:272` concedes "the value may stay unread by the existing reader", so PD20(c) bullet 4 will be satisfied formally in cycle 78 unless this is built. (c) A BooleanConstant value reader for the conditional terminal, accepted as "wired + class" only (`result_77-2.json:12`, `task_77-3.json:20`).

**3. Unmeasured steps.** (a) The cycle's headline conclusion, "no measurable split gain at this load", rests on one run per cell with differences of 0–3 frames in about 3,075 (`m8_s1s3_77.log:42,83,124,165,206,247`); the material session itself asked whether repeat legs are needed (`result_77-6.json:12`). The judgement did not repeat a leg (3 minutes each) and instead wrote the load question to the user (`decisions_pending.json:39-51`), which is the right question but does not replace the measurement. (b) The three DUE slugs and the overdue outcome cadence were both readable at 05:44 from files (`violations.py`, the retrospective count); they were discovered by launching a recipe into the gate at 06:22 and 06:26. (c) The retry-cap loss "≈30 min" at `violation-decisions.md:1241` is an estimate, not a log figure.

**4. Rule compliance.** Kept: rule 1 (A5, every leg's G1/G91 md5 lines), motor rule 1b (G0 and G93 on all six legs with FRF=1 POS=0, `m8_s1s3_77.log:5,30`), LabVIEW verified gone per leg, NEXT before retrospective, steer answered in `next.json`. Broken or formal: (a) "never end a message expecting to be resumed": the session's final text reads "Its completion notification will bring me back" after its Monitor call was permission-denied (`cycle_77.log:119`, last denial entry and `result`). The retrospective survived only because bgrun detaches; this is session 68's shape verbatim. (b) Rule 4: STATUS is 136 lines against a ~100 line limit (audit L3), unchanged for several cycles. (c) A4: two reviews left blank (`2026-09-25-const-loopterm-77.md:69-71`, `-77c.md:84-86`) although 77c's disposition was in fact applied (`result_77-4.json:14`). (d) A6 says "this cycle used no GUI if the retrospective agrees". I do not agree: six legs of bead picks, done button, bandpass panels and save dialog ran through the approved exception (`m8_s1s3_77.log:16-22`). That is rule-compliant, and the audit line is wrong about it. What the audit does not cover: sub-agent permission denials, the ledger-versus-real-runs gap, whether the C7 baseline plan is the plan the cycle actually used, and whether a steer was followed in substance or by relabelling.

**5. Ordering.** Defensible in outline, wrong in one place. The `guard_peer` repair first was mandated by retro-76 at threshold 1. But the outcome review was overdue since cycle 75 (7 retrospectives, cadence 5, `outcome_77.log:2`) and fires only on a recipe launch; had the judgement run it at 05:45 (195 s), the steer would have been in hand before 77-2 and 77-3 spent about 47 minutes and two reviews on the constant verb, and the S1/S3 legs could have started around 05:55 with the cap untouched. The verb was still needed for the stage, so this is a finding, not the fault.

**6. What was not reported.** (a) The judgement session's own `subagent_stats` and `permission_denials` show 27 denials across 42 turns (`cycle_77.log:119`); the summary at STATUS:74 says "8 dispatches" and nothing about the denials. (b) `m8_s1s3_77_dry.log:23` has a FAIL on G93 with a PASS RESULT line and rc=0; the inner-FAIL scan matches only line-start `FAIL`, and the table cells `| FAIL |` in `m8_s1s3_77.log:98,103,139,144,185,226` also pass it. Here the design intent was PASS and result_77-6 says why (`facts[8]`), so nothing was hidden, but the scan can be evaded by a table. (c) The JEV ladder timed out three times on one log within three minutes (`jev_gate.log:901,902,904`), each "BLOCK stands (fail closed)", while the material dispatched the hypothesis review in parallel; the ladder added no information to that decision.

**7. Judgement inside a material session.** Two instances, both small. (a) Card 77-4 material wrote the two FIXED release lines on the prior-art review (`archive/peer/2026-09-25-priorart-priorart-c77-replay.md:271-272`), which is accepting a review's findings and releasing a stop record; the card's pass line pre-scripted it ("released (FIXED/REFUTED) before the LabVIEW run", `task_77-4.json:21`). The material did return the PD20(c) route deviation as OPEN, which is correct, but the release itself was judgement's. (b) The same session narrowed the teardown guard to 0x47D "per review 77c" (`result_77-4.json:14`), a design change taken on a review's recommendation without a judgement disposition on file; the review's own file stays blank.

## DEVICE EFFECT

- **`unreported-fact` (bgrun rc=1 on inner FAIL)**: worked on the constant-verb logs (rc=1 at `const_loopterm_77.log:13,30`, `77c.log:20`). Evaded by table-cell FAIL text, see finding 6(b); not a failure this cycle because the RESULT lines were honest.
- **`rule-evaded` (confirm-bait refusal, adversarial append)**: worked; both hypothesis prompts carry the ATTACK block (`2026-09-25-const-loopterm-77c.md:32-38`).
- **`tool-not-built` (prior-art review)**: worked; found the unmeasured Q&R.y route and the unread #581 (`priorart_replay_77.log:16-21`).
- **`repeated-failure-class` (refuse priorart/retro while newest review of that kind is blank)**: did not need to fire; retro-76 was annotated (`2026-09-25-retrospective-cycle76.md:286-292`).
- **`unreported-fact` (C3/C4 cost lines)**: worked, 5 of 5 parsed.
- **`premature-build` (guard_cycle recipe refusal)**: FAILED by misfire. It refused at 06:22 on a decision block that existed but carried "05:5x" (`violation-decisions.md:1194`), and that refusal was the first of the two counted against the cap.
- **`scope-creep` (C7 out-of-plan list)**: FAILED by firing on everything. It lists 107 files against `docs/cycle27-plan.md`, which is not the plan this cycle worked from (`next.json` names `docs/m8-real-run-plan.md`), so the list is unreadable and routinely ignored.
- **`device-failed` (COST regex, cost lines seen/parsed)**: worked.
- **`device-failed` (bgrun FAIL scan on build logs)**: worked on builds.
- **`repeated-failure-class` (OpLoopEndRef_v0 reader)**: used, `cond_wire_uid 260` at `const_loopterm_77d.log:4`.
- **`device-failed` (stop record + launch gate)**: armed correctly at `priorart_replay_77.log:42`, released by FIXED lines; FAILED on the read-only half, refusing `wc -l` and `grep` at `material_marker.log:1454`, the hole the 2026-09-24 05:54 and table decisions were meant to close.
- **`device-failed` (motor_gate FAIL printing)**: worked; session start and end verified (`cycle_runner.log:217,223`).
- **`repeated-failure-class` (guard_peer retry path)** and **`device-failed` (Jev command scoping)**: no triggering event this cycle; `jev_gate.log` still trips audit A1/A3 every window.
- **`repeated-failure-class` (guard_session SendMessage refusal)**: inert by STATUS:97; not exercised, all 8 dispatches foreground (`cycle_77.log:119` `subagent_stats`).
- **`device-failed` (write_novel_record / decision table)**: the novel-plus-contradicted verdict was handled by FIXED release; the table's read-only row failed as above.
- **`device-failed` (guard_peer `selftest_exempt`, 05:58)**: built and measured this cycle (`result_77-1.json:13-16`); it now gates `selftest_make_default.log`, bound by its review.
- **`device-failed` (retry-cap recorder, 07:05)**: this is the decision written after the failure described above; the device it repairs is the user's RETRY CAP of 2026-09-24, and that device failed three times in this window (`stage_runs.jsonl:3-5`).

VIOLATION: device-failed | loss_min=7 | loss_usd=? | evidence=tools/bench/stage_runs.jsonl:3

VERDICT {"schema":"verdict/1","id":"retrospective-cycle77","verdict":"refuted","alternative":"The stage was correctly held back by steer_77 (no tooling before delivery) and the cap only enforced that; under this reading cycle 77 delivered the S1/S3 measurement and the deferral was judgement, not a device fault.","discriminating_test":"Replay the 06:55:36 launch offline against stage_prerun.check_cap with stage_runs.jsonl lines 3-5 removed: if it allows with no retry card, the ledger alone blocked the run; the retro-77 repair self-test (refused launches leave the count unchanged) settles it.","violations":[{"slug":"device-failed","loss_min":7,"loss_usd":null,"evidence":"tools/bench/stage_runs.jsonl:3"}],"sources":["tools/bench/stage_runs.jsonl:3","tools/hooks/guard_bash.py:387","tools/hooks/material_marker.log:1455","tools/hooks/material_marker.log:1467","tools/bench/cards/result_77-7.json:3","tools/bench/cards/result_77-8.json:8","docs/violation-decisions.md:1194","docs/violation-decisions.md:1236","tools/bench/m8_s1s3_77.log:42","tools/bench/cycle_77.log:119"],"note":"One structural fault: the retry-cap ledger counted three refused launches (two guard_cycle, one permission layer), spent the judgement retry card and left the plan's first act at 0 runs. Also failed this window: guard_cycle on an unparsed '05:5x' header, stop record on read-only commands, C7 against the wrong plan."}

## Sources

(extract from answer)

## What was done with it

Cycle-78 judgement, 2026-09-25 (this disposition was the one owed by cycle 77's close).

- **THE FAULT, `device-failed` (retry-cap ledger): ACCEPTED, FIXED.** It fired again at the start of cycle 78: 78-1's
  two refused launches were counted (`stage_runs.jsonl:6-7`). Card 78-2 moved the recording into `tools/bgrun.py` at
  child start; the hook now only checks. Self-test `tools/bench/selftest_retry_cap.log` 8/0: launches refused by a
  hook, and children that never start, leave the count unchanged, and the old hook-written lines no longer count.
  Outcome line: `docs/violation-decisions.md:1248`. The stage then ran (`stage_replay_78.log` 35/0).
- F1(b) the launch shape: ACCEPTED, applied. The accepted form, measured on a harmless child, is written into
  `docs/m8-real-run-plan.md` PD22(a) and STATUS NEXT.
- F2(a) header lint for `violation-decisions.md` HH:MM: ACCEPTED as a finding, not built this cycle (deliverable
  first under steer_77). F2(b)(c) enum/boolean constant readers: not needed. PD21(c) replaced the #581 read with the
  wire-source gate, which passed.
- F3(a) one run per cell: ACCEPTED. The lost-frame comparison stays "no measurable gain at this load" and is
  labelled one run per cell. M3 is justified by rule 1c, not by those numbers (m8 plan PD21(a)).
- F4(a) "expecting to be resumed": ACCEPTED. Cycle 78 dispatched everything in the foreground. F4(b) STATUS
  length: carried. F4(c) blank reviews: the 78 reviews are dispositioned.
- F5 ordering, F6 denials/table-cell FAIL scan, F7 judgement-in-material (FIXED release written by material):
  recorded as findings. In cycle 78 the prior-art and hypothesis dispositions were written by judgement
  (`2026-09-25-priorart-replay-swap-78.md`, `2026-09-25-78-3-selftest-endian.md`).
- DEVICE EFFECT C7 (scope-creep list against the wrong plan): finding, not repaired this cycle.
