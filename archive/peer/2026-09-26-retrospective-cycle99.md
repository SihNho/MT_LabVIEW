# retrospective-cycle99

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.1601  in 130 / out 18837 / cache-create 156888 / cache-read 316781  (246s, 35 turn(s))
- **date:** 2026-09-26 20:59:03
- **outcome:** ANSWERED (248s)
- **verdict-card:** VERDICT-CARD retrospective-cycle99 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle99.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle99, role retrospective) ---
CLAIM: Cycle 99 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 99 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-26 19:25:08  ..  2026-09-26 20:54:51   (90 min)
    basis: start = archive/peer/2026-09-26-retrospective-cycle98.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `repeated-failure-class` (decided 2026-09-25 14:28): (`tools/bench/cards/result_82-1.json`). `tools/stagexec.py` md5 `209d5e57?? compares SimReader's `Nodes[]` membership with a REAL read at PRIME, per touched diagram, and fails on any class listed by one side only. SimReader's listing rule (`stagexec.py:282-294`) is fitted to the real read of D1_k: 231 SimReader-only entries before the fit, 0 after, and a 173-diagram holdout also reaches 0 after on??
  - `device-failed` (decided 2026-09-25 14:28): cycle's act) and falls back to `current_plans()` only when that is absent. It needs a self-test with a two-current-plans case. Scheduled after this cycle's L2-A1 deliverable run (deliverable first); if not reached, it is carried in STATUS NEXT.
  - `repeated-failure-class` (decided 2026-09-25 16:10): reports them all, then fails. Self-test: a plan with two unroutable rows reports both. It is built as the FIRST step when L2-A1 resumes (`docs/d1-loop12-17-split-plan.md` Pre-decided 188(c)/(d)), before any real replay. Cycle 83 is the load measurement and runs no stage.
  - `device-failed` (decided 2026-09-25): op error now stops the run (`ExecStop`) unless the recipe passes `LVBackend(s, fs, sink_gates=[{"gate", "sink": [owner_uid, term_name]}], gates={label: reader})` naming a gate it owns for that exact sink (`tools/stagexec.py:590` check_sink_gates refuses an absent gate; `:607` sink_gate_for refuses another sink; `:725` the indicator path; `:635` run_deferred makes each declared gate READ its sink a??
  - `device-failed` (decided 2026-09-26): on the line after START (START's shape unchanged, because jev.py:222 / protocol.py:63 parse it exactly) and reaps at every start; `tools/bgrun_reap.py` appends `BGRUN KILLED (external) pid=<n>` to a log whose last segment has a PID line, no END/TIMEOUT/KILLED, and a pid absent from tasklist (never a live pid; tasklist failure => nothing touched; pre-92-4 logs with no PID line are left alone as `un??
  - `device-failed` (decided 2026-09-26 13:47): now checks graph shape (`graph_shape_error`, :123-147), `find_graph` returns only terminal-list graphs, and a wrong-shape graph is a clean gate FAIL, not a crash. Self-test `tools/bench/selftest_stage_prerun_graphload.py` 18/0 including malformed-graph negatives; launch_gate 28/0 and control-lint 10/0 are unchanged; the four earlier crashers re-run with 0 KeyError.
  - `wrong-ordering` (decided 2026-09-26 14:10): judgement session and writes the result into the cycle card (`gates_due`). It is to be built in a tooling slot after cycle 96's deliverable run (steer_95, deliverable-first). Until it exists, STATUS NEXT carries the manual form: run both `--due` checks before the first card.

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

== cycle audit, 2026-09-26 19:25 .. 2026-09-26 20:54 (90 min, an explicit cycle window): 22 build logs, 9 peer logs, 54 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 21/22 ok; NO BGRUN line in ['jev_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 10 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 54/54 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 4134 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 1 log(s) with a run that printed none: ['diag_c99_peek.log']

  C1 builds run 27, failure markers 10, logs carrying a failure 10
  C2 peer reviews dispatched 9, archived 54
  C3 wall-clock inside bgrun, BUILDS ONLY 18 min 34 s
  C4 wall-clock inside bgrun, REVIEWS 8 min 39 s; cost $4.2850 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 27 min 13 s  (builds 68%, reviews 31%, judgement session 0%)

  C6 material-marked recipe/bench runs 30, judgement-session attempts refused 4  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 24 - STATUS.md, docs/GLOSSARY.md, tools/bench/.stall_samples.txt, tools/bench/diag_c99_files.py, tools/bench/diag_c99_files2.py, tools/bench/diag_c99_files3.py, tools/bench/diag_c99_files4.py, tools/bench/diag_c99_files5.py, tools/bench/diag_c99_lvread.py, tools/bench/diag_c99_peek.py, tools/bench/diag_c99b_bench.py, tools/bench/diag_c99b_files.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/776 ok; 435 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2335 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:267 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 625 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun


=== BUILD LOGS INSIDE THE WINDOW (22; read them directly, they are the primary record) ===
tools/bench/diag_c99_files.log  (2026-09-26 19:30:22)
tools/bench/diag_c99_files2.log  (2026-09-26 19:33:41)
tools/bench/diag_c99_files3.log  (2026-09-26 19:34:14)
tools/bench/diag_c99_files4.log  (2026-09-26 19:34:58)
tools/bench/diag_c99_files5.log  (2026-09-26 19:36:30)
tools/bench/diag_c99_lvread.log  (2026-09-26 19:37:45)
tools/bench/diag_c99_lvread2.log  (2026-09-26 19:39:55)
tools/bench/diag_c99_peek.log  (2026-09-26 19:29:30)
tools/bench/diag_c99b_bench.log  (2026-09-26 20:01:02)
tools/bench/diag_c99b_bench2.log  (2026-09-26 20:07:04)
tools/bench/diag_c99b_files.log  (2026-09-26 19:51:44)
tools/bench/diag_c99b_files2.log  (2026-09-26 19:52:09)
tools/bench/diag_c99b_lvread.log  (2026-09-26 19:55:37)
tools/bench/diag_c99c_bench.log  (2026-09-26 20:36:42)
tools/bench/diag_c99c_bench2.log  (2026-09-26 20:50:21)
tools/bench/diag_c99c_dry.log  (2026-09-26 20:31:48)
tools/bench/diag_c99c_prerun.log  (2026-09-26 20:31:56)
tools/bench/diag_c99c_prerun2.log  (2026-09-26 20:32:09)
tools/bench/diag_c99c_prerun3.log  (2026-09-26 20:46:27)
tools/bench/jev_gate.log  (2026-09-26 20:46:23)
tools/bench/motor_session_end_cycle98.log  (2026-09-26 19:26:05)
tools/bench/motor_session_start_cycle99.log  (2026-09-26 19:26:32)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (9) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_98.log  (2026-09-26 19:26:00)
tools/bench/cycle_99.log  (2026-09-26 19:26:32)
tools/bench/cycle_runner.log  (2026-09-26 19:26:32)
tools/bench/cycle_runner_main_20260926b.log  (2026-09-26 19:26:06)
tools/bench/cycle_runner_main_20260926c.log  (2026-09-26 19:26:32)
tools/bench/peer_c99_files_p5.log  (2026-09-26 19:33:13)
tools/bench/peer_c99b_bench.log  (2026-09-26 20:04:04)
tools/bench/peer_c99c_bench.log  (2026-09-26 20:44:29)
tools/bench/retro.log  (2026-09-26 20:54:51)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle99","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Fault named first.** Cycle 99 ended with its go/no-go quantity unmeasured after four consecutive `ExecState 0` failures on a scratch bench, each explained by inference, with the project's own Error List reader never used. Details, findings and device check follow.

## Structural fault

**Repeated failure class: ExecState 0 on a scripted scratch VI, diagnosed by guessing four times in one cycle, while a reader existed.**

The four attempts, all inside the window:

| attempt | log | construction | guessed cause |
|---|---|---|---|
| 1 | `tools/bench/diag_c99b_bench.log:32-33` | CLFN moved into For body, SR wired t6/t7 | t6/t7 were `site` |
| 2 | `tools/bench/diag_c99b_bench2.log:33-35` | same, wired t8/t9 | none read; card stopped |
| 3 | `tools/bench/diag_c99c_bench.log:38-39` | indicator into For body, tunnel | auto-indexed tunnel, 2-D page |
| 4 | `tools/bench/diag_c99c_bench2.log:38-52` | tunnel re-read, then both terminals inside | "a panel terminal moved into a For body" |

Attempt 4 falsified the attempt-3 story by the review's own read-back (IndexMode 1→0, ExecState still 0, `diag_c99c_bench2.log:40`) and then went straight to another construction on a fresh scratch, which also read 0 (`:51`). The cycle then closed with the cause of all four still a guess (`docs/d1-loop12-17-split-plan.md:1671-1672`, `:1677-1678`) and the go/no-go quantity (1) replaced by a named assumption (`:1672-1676`).

Two rules already say what attempt 3 should have been. CLAUDE.md "When a diagnosis is GUESSED twice, build the reader" (CLAUDE.md:444-451), and the standing change cycle 98's judgement accepted minutes before this cycle began: "when a fix card FAILS on a gate whose premise was never measured, the next card is the READ, not a re-designed fix" (`archive/peer/2026-09-26-retrospective-cycle98.md:271-272`). The reader exists: `tools/lv_errorlist.py` reads every Error List item of a broken VI through the GUI and is run by the runner at every cycle start (`tools/bench/cycle_runner_main_20260926c.log:5`). All three cards carried `"gui": false` (`tools/bench/cards/task_99-3.json:41`), so the one instrument that answers "why is this VI broken" was excluded by flag, and card 99-3 was issued as an escalated re-run of the same bench (`task_99-3.json:5-8`) instead of a read.

The c99b review's cheapest test was also skipped: it asked for a read-only terminal read of run 1's scratch, still on disk (`archive/peer/2026-09-26-c99b-bench-t2.md:71`, `diag_c99b_bench.log:47`); run 2 deleted that file at start (`diag_c99b_bench2.log:4`) and re-ran the fix. The disposition line nevertheless reads "ACCEPTED as the test plan" (`c99b-bench-t2.md:91`).

**Loss.** The 99-3 F3 arc after the rule had already triggered: two bench runs (265 s and 228 s, `diag_c99c_bench.log:93`, `diag_c99c_bench2.log:110`, F3 portions plus LabVIEW restarts), one hypothesis review at $1.8853 (`tools/bench/peer_c99c_bench.log:4`, 280 s), and the patch time between 20:39 and 20:46 (`tools/bench/jev_gate.log:1520-1522`). About 25 minutes. The c99b review ($1.1482, `peer_c99b_bench.log:4`) was the legitimate first review and is not counted.

**Counterfactual.** Card 99-2 returned FAIL at about 20:18 (`jev_gate.log:1510-1512`). Had 99-3, cut at about 20:20, been a read card with `gui: true` (rebuild F3-A in 90 s as run 1 did, then one `lv_errorlist` read), the Error List item would have been on disk by about 20:35, F4 alone (ExecState 1, four minutes) would still have run, and the cycle would have ended at the same 20:54 with (1) either measured or its blocker named. Instead it ended with GO on an assumption and a written promise that "no third bench attempt is made" (`d1-loop12-17-split-plan.md:1675`), which is the fourth guess declared final.

## Findings

**1. Repeated failure.** Covered above. The approach should have changed at attempt 3, at the cut of card 99-3, to a read. Note that the four constructions differ (CLFN in body with SR; FP indicator in body via tunnel; both FP terminals in body), so the closing explanation "a panel terminal moved into a For body" (`STATUS.md:83`) covers only attempts 3 and 4, not 1 and 2.

**2. Missing tool.** No stand-alone read-only `Wire.Is Broken?` op exists (CLAUDE.md:451, "ONLY inside the connect ops"). In attempt 4, B2 made one wire 288 on both terminals with 0 tunnels (`diag_c99c_bench2.log:49-50`) and still read ExecState 0. A broken-wire read on 288 would have split "the wire is bad" from "the VI is broken elsewhere" in one call. The Error List reader answers the same question, but only with `gui: true`.

**3. Unmeasured steps.** (a) The go/no-go quantity (1), the per-frame L1 write cost, was replaced by "0.5–1 ms per 4.8 MB copy at memory bandwidth" (`plan:1672-1674`). The threshold needs (1) ≤ 2.94 ms against a lower-bound (2) of 7.94 ms; both halves are open, and GO was written anyway. It is flagged as an assumption and the ABBA measures the net gain, so I count it as a finding, not a second fault. (b) The c99c review noted the 4.8 MB control copy at run start as an alternative for the T15−T1 gap (`c99c-bench-t4.md:100`); the per-call estimate (T15−T1)×15/14 still carries that copy. (c) Panel open tripled every F4 run (`diag_c99c_bench.log:48-62` vs `bench2.log:61-75`); the real display loop will have its plot visible, and no measurement addresses that.

**4. Rule compliance.** Broken: "guessed twice, build the reader" (CLAUDE.md:444-451) and the cycle-98 standing change (retrospective-cycle98.md:271-272). Satisfied only formally: §3's "what to accept from a review" is judgement, yet all three reviews were accepted inside material sessions (`c99-files-p5.md:84`, `c99b-bench-t2.md:91`, `c99c-bench-t4.md:127`), routed by the Jev ladder's "review owed" row. Held: rule 1 (every pin intact, every scratch deleted, LabVIEW gone in every log), rule 1b (motor session start and end verified), dispatch count 3 of 6, failure budget 2 per card, escalation rung used exactly once. What the audit does not cover: whether an accepted review's cheapest test was executed (A4 checks only that the annotation is non-empty); that the four stage runs were recorded with `card=None` (`tools/bench/stage_runs.jsonl:24-27`), so the retry cap cannot tie a run to card 99-2 or 99-3; whether a go/no-go threshold written in the plan was met before GO; and its C7 list includes `docs/GLOSSARY.md`, which came from the chat commit `cdcaa0b`, not from this cycle.

**5. Ordering.** Facts first (99-1), design (PD212 a–g), then the bench, is the PD210(f) order and is defensible. The single misordering is card 99-3: an escalated re-run before a read. Escalating the model (Opus max) does not change what the bench can see.

**6. Not reported.** (a) The judgement session's own cost is absent (audit C4c: no cost line), so the cycle's real cost is unknown; the $4.29 in C4 is reviews only. (b) STATUS.md:82 reports "≥ 7.94 ms per frame at 15 beads" without saying the number omits IndexArray, Subtract, Split, Bundler, BuildArray and the indicator draw, which the result card does say (`result_99-3.json` F4 fact 4). (c) The `diag_c99_peek.py` launch at 19:28 was tried five ways in 30 seconds across shells before the marker refused it (`tools/hooks/material_marker.log:2055-2061`); harmless, but it is the pattern of a session probing a gate rather than reading it.

**7. Judgement inside a material session.** Yes, three times, all review acceptances (citations in finding 4). The most consequential is inside card 99-3: the material session pre-scripted "only if B1 is not ExecState 1 does B2 run, on a FRESH scratch" (`c99c-bench-t4.md:130-132`), which is the "if X then do Y" form CLAUDE.md:344-351 forbids, and it chose the second construction itself. The judgement session's plan section then took the material session's explanation over as fact (`plan:1677-1678`).

## Device effect

Devices whose fault did not occur or that fired correctly in the window: bgrun rc=1 on every FAIL line (all four bench logs end `rc=1`); cost regex 3/3 parsed (audit C4b); A2 all runs ended; A3 every failing log reviewed; A4 54/54 annotated, so the "empty What was done with it" refusal had nothing to refuse; the material marker refused four non-bgrun launches and the sessions complied (`material_marker.log:2060-2061`, `2073-2074`, `2081-2082`); RULE-SAME-ROW discharged run 2 of each bench without a second review (`jev_gate.log:1510`); prerun gate refused a bench launch once and it was satisfied honestly (`material_marker.log:2076-2077`); stop record, prior-art and premature-build gates had no recipe to act on; guard_session had no SendMessage to refuse (three fresh dispatches).

One device fired on the wrong thing again: audit A1 counts `jev_gate.log` as a build log and reads FAIL (audit header, "NO BGRUN line in ['jev_gate.log']"). This is the third cycle it has done so and it is already on the owed tooling card from retrospective-cycle96 (`STATUS.md:85`). It costs nothing and the fault it guards against (a LabVIEW run outside bgrun) did not occur, so I record it here rather than as a second fault of equal magnitude.

The scope counter C7 fired with 24 files, 20 of them the cycle's own `diag_c99*` scripts and facts; it is a counter by design and the verdict is "no scope creep". The Jev ladder classified all four bench failures correctly (two `new-problem`, `jev_gate.log:1507`, `:1520`), which is what let the same-row rule work.

VIOLATION: repeated-failure-class | loss_min=25 | loss_usd=1.8853 | evidence=tools/bench/diag_c99c_bench2.log:51

VERDICT {"schema":"verdict/1","id":"retrospective-cycle99","verdict":"refuted","alternative":"Card 99-3 was a legitimate escalation: F4 (7.94 ms) was delivered there and F3 failed on bench construction that no read could have fixed in the same cycle.","discriminating_test":"Rebuild F3-A (90 s) and run tools/lv_errorlist.py on it with gui:true; if the Error List names a cause in under 10 min, the read card was the cheaper step.","violations":[{"slug":"repeated-failure-class","loss_min":25,"loss_usd":1.8853,"evidence":"tools/bench/diag_c99c_bench2.log:51"}],"sources":["tools/bench/diag_c99b_bench.log:32-33","tools/bench/diag_c99b_bench2.log:4","tools/bench/diag_c99c_bench.log:38-39","tools/bench/diag_c99c_bench2.log:38-52","tools/bench/peer_c99c_bench.log:4","archive/peer/2026-09-26-retrospective-cycle98.md:271-272","archive/peer/2026-09-26-c99b-bench-t2.md:71","tools/bench/cards/task_99-3.json:41","docs/d1-loop12-17-split-plan.md:1671-1676","tools/lv_errorlist.py:1-5"],"note":"Four ExecState-0 guesses in one cycle with the Error List reader excluded by gui:false; cycle closed with the go/no-go quantity assumed. Audit A1 misfire on jev_gate.log is a known owed item, not a second fault."}

## Sources

(extract from answer)

## What was done with it

ACCEPTED (cycle 99 judgement): `repeated-failure-class`. The fault is in my card scoping. 99-2 and 99-3 set `gui: false`, which
excluded `tools/lv_errorlist.py`, and 99-3 escalated the model instead of adding a READ of why the bench was ExecState 0.
**Disposition, written into STATUS NEXT for cycle 100:**
(1) Every card that builds or edits a VI carries `gui: true` for the Error List reader only, and its pass list says: on
ExecState 0, read the Error List before any second construction.
(2) The go/no-go quantity (1) stays an ASSUMPTION, named as such in PD212(i)2. The ABBA measures the net gain. If that gain
is under 5 ms, the first act is the Error-List-backed F3 read, not a rebuild.
The verdict's alternative (99-3 was legitimate for F4) is also true: F4 = 7.94 ms is the measurement the GO rests on.
