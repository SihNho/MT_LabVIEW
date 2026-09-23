# retrospective-cycle73

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $7.6161  in 226 / out 29632 / cache-create 287712 / cache-read 1511850  (377s, 57 turn(s))
- **date:** 2026-09-24 07:29:29
- **outcome:** ANSWERED (378s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 73 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-24 06:22:26  ..  2026-09-24 07:23:09   (61 min)
    basis: start = archive/peer/2026-09-24-retrospective-cycle72.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-24 06:22 .. 2026-09-24 07:23 (61 min, an explicit cycle window): 18 build logs, 7 peer logs, 25 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 17/18 ok; NO BGRUN line in ['jev_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 6 logs recorded a failure; unreviewed: ['jev_gate.log']
  PASS  A4 every archived review says what was done with it: 25/25 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1942 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 23, failure markers 12, logs carrying a failure 6
  C2 peer reviews dispatched 7, archived 25
  C3 wall-clock inside bgrun, BUILDS ONLY 21 min 27 s
  C4 wall-clock inside bgrun, REVIEWS 8 min 21 s; cost $5.6130 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 29 min 48 s  (builds 71%, reviews 28%, judgement session 0%)

  C6 material-marked recipe/bench runs 22, judgement-session attempts refused 3  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 18 - tools/bench/c73_l7r_facts.py, tools/bench/c73_l7r_live.py, tools/bench/c73_l7r_probe0.py, tools/bench/dryrun_l7_r_address.py, tools/bench/jev_ladder_cache.jsonl, tools/bench/l7_r_20260924_071320_after_save.png, tools/bench/l7_r_20260924_071320_before_save.png, tools/bench/l7_r_predict.py, tools/bench/next_snapshot.md5, tools/bench/peer_task_c73_l7r_dryrun.txt, tools/bench/relocate_status_c72.py, tools/bench/relocate_status_c72b.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 289/654 ok; 365 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 2 DANGLING of 2069 citations checked:
       docs/m3a1-severed-rows.md:87 -> tools/bench/m3a1_severed_arith.json
       docs/m3a1-severed-rows.md:89 -> tools/bench/m3a1_severed_rows.log

  WARN  L2c plan documents cite files that do not exist yet: 17 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:113 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 587 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:394', 'docs/NAMES.md:411', 'docs/NAMES.md:445', 'docs/NAMES.md:584', 'docs/NAMES.md:706']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (18; read them directly, they are the primary record) ===
tools/bench/c73_l7r_facts.log  (2026-09-24 06:26:49)
tools/bench/c73_l7r_live.log  (2026-09-24 06:40:18)
tools/bench/c73_l7r_probe0.log  (2026-09-24 06:25:42)
tools/bench/dryrun_l7_r_address.log  (2026-09-24 06:56:15)
tools/bench/jev_gate.log  (2026-09-24 07:23:05)
tools/bench/l7_r_predict.log  (2026-09-24 07:13:00)
tools/bench/motor_session_end_cycle71.log  (2026-09-24 06:23:36)
tools/bench/motor_session_start_cycle72.log  (2026-09-24 06:23:42)
tools/bench/relocate_status_c72.log  (2026-09-24 06:30:34)
tools/bench/relocate_status_c72b.log  (2026-09-24 06:30:55)
tools/bench/selftest_guard_session_c73.log  (2026-09-24 06:27:34)
tools/bench/selftest_stoprecord_bgrun_c73.log  (2026-09-24 06:29:32)
tools/bench/selftest_stoprecord_eqform_c73.log  (2026-09-24 06:29:46)
tools/bench/selftest_stoprecord_supersession_c73.log  (2026-09-24 06:29:39)
tools/bench/selftest_stoprecord_table.log  (2026-09-24 06:29:24)
tools/bench/stage_d1_l7_r.log  (2026-09-24 07:07:40)
tools/bench/stage_d1_l7_r_r2.log  (2026-09-24 07:20:59)
tools/bench/stop_record_selftest_c73.log  (2026-09-24 06:29:32)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (8) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_71.log  (2026-09-24 06:23:33)
tools/bench/cycle_72.log  (2026-09-24 06:23:45)
tools/bench/cycle_runner.log  (2026-09-24 06:23:42)
tools/bench/cycle_runner_main_20260924a.log  (2026-09-24 06:23:42)
tools/bench/peer_c73_l7r_dryrun.log  (2026-09-24 06:51:23)
tools/bench/priorart_c73_l7r.log  (2026-09-24 06:53:22)
tools/bench/priorart_c73_l7r_r2.log  (2026-09-24 07:11:33)
tools/bench/retro.log  (2026-09-24 07:23:09)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

I've read the full evidence: both stage logs, the three review logs and their archived dispositions, the dry-run and contract logs, the material marker journal, the Jev gate journal, the stop-record store, the self-test logs, plan entries 175 and 176, STATUS and CLAUDE.md. Here is the review.

## Verdict first

The cycle delivered L7-R: `claudeDev\D1_s4_loop17.vi`, 61 gates pass / 0 fail, ExecState 1 warm and after the scripted save (`tools/bench/stage_d1_l7_r_r2.log:466-467,487`). That is the deliverable STATUS asked for. Two things changed how the cycle ended.

**Fault 1, the costly one.** Run 1 died after 599 s on the recipe's own Python: `sorted()` over edge tuples that mix `'TFP'` strings with ints (`tools/bench/stage_d1_l7_r.log:454-462`), after every LabVIEW gate including PB had passed (`:451`). Nothing was saved (`:479`). The same lists live in `tools/bench/l7_r_prediction.json` and were on disk at 06:45; `sorted(P["added"])` raises the identical TypeError in 0 s with no LabVIEW. The offline dry run at 06:48 exercised only `Stage.address` (`tools/bench/dryrun_l7_r_address.log:2-23`), not the gate arithmetic. This is the class cycle 72 already paid for twice, r1 and r2 of L7-1b, both "script defects with measured causes" (`docs/d1-loop12-17-split-plan.md:407-409`), and the class retrospective-cycle71 F2a/F3 answered with "dry run before LabVIEW" (STATUS.md:82). The remedy was applied to one code path and not the other. The edit then changed the recipe's bytes, so the stop record refused the relaunch (`tools/hooks/material_marker.log:1306`) and a second prior-art review had to be bought to release it (`tools/bench/priorart_c73_l7r_r2.log:4`, $2.0871, 173 s). Counterfactual on the clock: had the diff comparison been run over the prediction JSON at 06:56 before launch, run 1 (start 06:56:50) reaches the save at about 07:07 and the artefact exists then. Actual artefact time is 07:20:59 (`stage_d1_l7_r_r2.log:489`). The retrospective launched 2 min after the artefact, so the cycle would have ended near 07:10 instead of 07:23. Loss 13 min and $2.09. Caveat stated honestly: run 1 carried a non-fatal handle gate that would have failed at +479 (`stage_d1_l7_r.log:468`), producing a failing log, which RULE-SAME-ROW would have discharged exactly as it discharged run 1's real failure (`tools/bench/jev_gate.log:678`).

**Fault 2, a broken device.** The bgrun inner-failure scan (decided 2026-09-17 03:38) fired twice on non-failures and was worked around both times by editing printed text. At 06:48:29 the dry run's deliberate negative test D3 printed the recipe's real gate `FAIL` line; the scan forced rc=1 (`tools/bench/dryrun_l7_r_address.log:15,24-25`), the Jev ladder classed it `new-problem` and blocked (`tools/bench/jev_gate.log:673-674`), and a hypothesis review was bought (`tools/bench/peer_c73_l7r_dryrun.log:3`, $1.0984, 122 s) whose verdict was "the claim holds" (`archive/peer/2026-09-24-c73-l7r-dryrun-negtest.md:36`). The fix was to silence the gate's print with a stub (`dryrun_l7_r_address.log:40`). At 07:12:48 the scan flagged a FACT line because it quoted "rc=1" (`tools/bench/l7_r_predict.log:73-74`); the fix was to reword the sentence to "ended by a Python TypeError" (`:93`). STATUS already carried "bgrun's scan flags rc=2 text in passing self-tests" as a candidate repair (STATUS.md:95), so this is routine bypass, the contract's third failure mode. Counterfactual: without the false rc=1 at 06:48:29, the dry run is green at 06:48 and the recipe launch does not wait for the review and harness rewrite until 06:56:50. Loss 8 min and $1.10. I note the review did produce gate A0, which was adopted; that is value, but it was value bought by a device misfire.

## Findings

**1. Repeated failure.** Yes, one class recurred across cycles: an own-script defect first discovered inside a LabVIEW run (fault 1 above). The approach should have changed at the dry run, attempt 1 of the offline stage at 06:48, by extending it to every non-LabVIEW gate expression in the recipe. Within the cycle a smaller repeat: the `MATERIAL=1` prefix was tried in three spellings, refused once, then `--material` used (`material_marker.log:1286-1290`); the same three wrong spellings were tried again at 06:37 (`:1295-1298`). About 1 min each time. Also the contract script was launched three times at 07:12 for a syntax error and the scan misfire (`l7_r_predict.log:44-49,73-75`).

**2. Missing tool.** An offline rehearsal of a recipe's gate arithmetic against its prediction JSON. It would have answered run 1's TypeError before any LabVIEW time. Second: a negative-test marker the bgrun scan respects, so a harness can print an expected refusal without forcing rc=1. Judgement already named a third and it is real: `computation_diff` cannot see diagram-terminal sources, so w3268's removal never showed (`stage_d1_l7_r_r2.log:450`; plan 176(c) at `docs/d1-loop12-17-split-plan.md:465-473`). Every later stage gates on a "0 rows" that can be false.

**3. Unmeasured steps.** The handle criterion. At 06:56 the material session set the gate to "no growth, at most +100" by inference from a read-only census that showed a decrease (`l7_r_predict.log:40`), while editing-stage growth to about 54,400 was already on disk in `stage_d1_m3a4.log:118` and `stage_d1_m4b.log:117`, as the r2 review pointed out (`archive/peer/2026-09-24-priorart-c73-l7r-r2.md:202`). A grep would have shown the gate could not pass. It was then demoted to a recorded fact (`stage_d1_l7_r.py:112`). Also inferred rather than measured: the PMV prediction first rested on a weaker source than the six-terminal precedent the r1 review found (`archive/peer/2026-09-24-priorart-c73-l7r.md:242-245`). Both were caught by reviews, at review cost.

**4. Rule compliance.** Mostly kept. The retrospective was last (07:23:09, `retro.log:1688`). Split-and-save held: a dated artefact with md5 (`stage_d1_l7_r_r2.log:463`). Prior-art before build held both times (launches 06:56:50 and 07:13:15 follow review ends 06:53:22 and 07:11:33). Weak spots: (a) "one review per row" was satisfied formally and not substantively. Run 1's TypeError was discharged by a review whose subject was the dry-run harness, not the recipe (`jev_gate.log:678`); the r2 prior-art review is the only peer that ever looked at that failure (`priorart-c73-l7r-r2.md:217-219`). This is the wrong-subject match STATUS.md:94 already lists. (b) Deliverable-first was inverted: STATUS.md:150 scheduled the carried devices "after the deliverable", but the self-tests ran 06:27 to 06:30 (`selftest_stoprecord_table.log:1`, `selftest_guard_session_c73.log:1`) before the L7-R census began at 06:37:40. About 4 min. (c) Rule 4: STATUS is 113 lines after the relocation (lint L3). (d) The guard_session SendMessage device was built but is inert because the settings matcher edit was refused (STATUS.md:78; G12/G13 red in `selftest_guard_session_c73.log:13-14`). What the audit does not cover: the judgement session's own cost (C4c reads 0 because the runner's cost line lands after the window; cycle 71's was $10.58, `cycle_runner.log:182`), so C5's $5.61 is well under half the real spend; C7 compares against `docs/cycle27-plan.md`, not the plan the cycle worked from, so its 18-file list is noise; A1 and A3 fail on `jev_gate.log`, the standing false positive STATUS.md:105(b) names; the material brief text is not on disk, so pre-scripted actions cannot be audited from files.

**5. Ordering.** The deliverable path itself was in a defensible order: facts, design, census, contract, recipe, prior-art, dry run, run. Two things should have moved. The devices should have followed the deliverable as STATUS said. And the gate-arithmetic rehearsal belonged beside the address dry run, before run 1.

**6. Not reported.** The STATUS lock note is accurate on the headline numbers (STATUS.md:26). It omits: run 1's failure was discharged by a harness review, not examined; two of the six retire "live consumers" gates were vacuous because #1929 and #5020 vanished with their wires at step 3 (`stage_d1_l7_r.log:439,442`; the contract records it, `l7_r_predict.log:94`); the fp_ind row has no `Is Broken?` second pass and its gate passes on the wrapper's own error text (`stage_d1_l7_r_r2.log:223-225`, recipe line 92), with the edge confirmed only indirectly by PC2 and RBW (`:453-455`); LabVIEW reused deleted uids 4337 and 1397 during the run (`:125,:64`), harmless today, a trap for any future gate keyed on a wire uid; and the plan §3 pass criterion for L7-R was changed twice by the material session before judgement ratified it as 176(a).

**7. Judgement inside a material session.** Yes, three instances, all in `archive/peer/2026-09-24-c73-l7r-dryrun-negtest.md:77-81` and the two prior-art dispositions. The material session accepted the review's tests 1 and 2, adding gate A0 and reordering the rows so tun_fp runs first (a change to the recipe's execution order), and rejected the review's PMV-scratch dump "outside Pre-decided 175" (`:81`). It also rewrote the handle criterion from a gate to a record (`priorart-c73-l7r-r2.md:245`), a plan §3 criterion, and refuted r1's "contradicted" by ruling which plan text governs (`priorart-c73-l7r.md:263`). Each was flagged OPEN and judgement ratified them in 176(a) and 176(b) (`docs/d1-loop12-17-split-plan.md:457-464`). Since the outcome was ratified and nothing was lost, these are findings, not the fault.

## Device effect

Per device, inside the window: the rc-masking fix held, every bgrun log ends with END and run 1 reports rc=1 (`stage_d1_l7_r.log:486`). Confirm-bait refusal: not triggered, the task said "ATTACK" (`c73-l7r-dryrun-negtest.md:15`). Prior-art review: worked, two rounds found four real items (stale §3 rows, handle gate, vacuous gates, uid reuse) for $4.51. Undisposed-review refusal: A4 25/25, not triggered. Cost lines: 3/3 parsed. Premature-build gate: respected both launches. Scope-creep counter: fired against the wrong plan, its list is ignored, degraded but it is a counter by design. Cost regex: fine. **bgrun inner-failure scan: FAILED, twice, worked around both times, named above.** OpLoopEndRef reader: not exercised. Stop record and launch gate: worked as designed at 07:08:24, and one false refusal of a non-executing `py -c` probe at 07:08:19 (`material_marker.log:1305`) after the 06:29 decision table claimed the read-only hole closed (`selftest_stoprecord_table.log:5-10`); cost 5 s, so I name it here and not in the verdict line. Motor FAIL exit: session start and end rc=0 (`motor_session_start_cycle72.log:23`). guard_peer replay: not exercised. Jev command-scoped exemption: the audit half still classes `jev_gate.log` as an unreviewed failing build every window (A1, A3), a standing misfire that readers ignore. SendMessage refusal: built, self-test green for G15 to G18, inert in production; no evidence in the session file of a SendMessage, 3 dispatches recorded (`tools/bench/session_dc6bfe56-c9cc-4114-bb4a-e0f2997911b6.json:1`). Read-only refusal repair: the 07:08:19 refusal above shows one command shape it does not cover. write_novel_record: not exercised, both verdicts were non-novel. Decision table: built, 107/0, same 07:08:19 gap.

VIOLATION: repeated-failure-class | loss_min=13 | loss_usd=2.09 | evidence=tools/bench/stage_d1_l7_r.log:460
VIOLATION: device-failed | loss_min=8 | loss_usd=1.10 | evidence=bgrun-inner-failure-scan@tools/bench/dryrun_l7_r_address.log:24

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
