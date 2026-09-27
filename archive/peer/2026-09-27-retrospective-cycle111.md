# retrospective-cycle111

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.7836  in 56 / out 45939 / cache-create 152107 / cache-read 3238771  (461s, 50 turn(s))
- **date:** 2026-09-27 22:12:57
- **outcome:** ANSWERED (463s)
- **verdict-card:** VERDICT-CARD retrospective-cycle111 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle111.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle111, role retrospective) ---
CLAIM: Cycle 111 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 111 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-27 20:18:43  ..  2026-09-27 22:05:10   (106 min)
    basis: start = archive/peer/2026-09-27-retrospective-cycle110.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-27 01:15): (`py`/`python` with the recipe in command position, or a bgrun whose `--` command does), and let every read-only / checker command through; `selftest_stagekit.py` is to be classed a self-test, not a stage. Both with a self-test carrying the two failing cases as negatives (`tools/bench/selftest_launch_gate.py`, currently 20/8). Owed in the FIRST tooling card after this cycle's stage run (PD214(e), ??
  - `wrong-ordering` (decided 2026-09-27 01:55): its executor raises on (`copy_in`: work == gscript.MOVE_DST; `primitive`: a registered donor; `local_read/write`: one panel row per label; `const_on_term`: a WhileLoop body), and `stage_prerun --prerun` evaluates each row's precondition against the recipe's work path and the labels/donor registry OFFLINE, failing the row that cannot run. Self-tested with r7's op 41 as the negative case. Built in t??
  - `device-failed` (decided 2026-09-27 01:55): read-only commands through, `selftest_stagekit.py` classed a self-test; negatives = `material_marker.log:2175` and `:2192`. Same owed tooling card as above (first after Part A). No new device beyond that one.
  - `inference-over-measurement` (decided 2026-09-27 03:30): stop (or the save) = the start MB of the most recent run of the same recipe + that run's per-op deltas + the largest per-read cost measured in it, for every read the plan makes that the run did not make. If any predicted value is ??MEMSTOP, the row fails. Ops the last run never reached are charged the worst measured read cost and flagged `extrapolated`. Negative case: r1's op-40 cut (`stage_d1_dis??
  - `repeated-failure-class` (decided 2026-09-27 07:40): (md5 `0e6a743e??) is called from `diag_c104_abba.py` and `drive_original_copy_v5.py`: (1) a NI-VISA open/close of `Rotor` and `ASRL5::INSTR` before any leg starts LabVIEW, refusing the leg on a nonzero status; (2) the leg loop ends on a refused leg or an A leg that fails before pick 1 (v5 no longer starts run2 after a failed run1); (3) a modal-dialog watch from Run to L2 that captures the dialog b??
  - `device-failed` (decided 2026-09-27 07:46): `stage_prerun --dry|--prerun <recipe>` through (they are offline checks that precede a release) and still refuses every launch; negatives `material_marker.log:2335`/`:2338` must pass, a real launch argv must still be refused; acceptance = a RECORDED top-level dry of the display recipe (sha `d62f876d`). Plus a card rule (no hook): a gate refusal is returned as BLOCKED, never re-run through a self-t??
  - `device-failed` (decided 2026-09-27 08:30): judgement session (`violations.py --due`, `outcome_review.py --due`, the retrospective-debt check, the prior-art/stop-record state of the recipe named in `next.json`), and writes the list into the cycle card (`gates_due`). A due outcome review runs BEFORE the judgement session, as the errorlist hook does. Owed as the FIRST card after the runner restarts (the runner is stopped on D-2026-09-27-03/-0??
  - `device-failed` (decided 2026-09-27 15:49): `py -m <module> ?? launches the MODULE, so every following path is an argument, never a launch unit. (2) `prerun_gate` gets the same lint-segment stripping as the stop_record path. The self-test must hold three cases: the literal command at `material_marker.log:2422` returns no launch unit, `py -u tools/recipes/stage_x.py` is still a launch, and `py tools/bgrun.py --material ??-- py -u tools/recip??
  - `device-failed` (decided 2026-09-27 20:20): BEFORE any L2-B2 dry: (1) the dry run's address/checkpoint phase no longer stops before op 1 ??every address, checkpoint and routing failure is collected across all ops and reported together, then the dry FAILs (no PASS record); negative case = replay of plan_l2b1's cycle-110 input (`plan_l2b1_in.json` before the re-cut) must report all 7 failing rows (5 ends + the 2 dead rows) in ONE dry; (2) the??

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

== cycle audit, 2026-09-27 20:18 .. 2026-09-27 22:05 (106 min, an explicit cycle window): 56 build logs, 11 peer logs, 60 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 34/56 ok; NO BGRUN line in ['diag_c111c_regress_selftest_c103d_hooks.log', 'diag_c111c_regress_selftest_c106d_tools.log', 'diag_c111c_regress_selftest_c108e_tools.log', 'diag_c111c_regress_selftest_c110_launchgate.log', 'diag_c111c_regress_selftest_launch_gate.log', 'diag_c111c_regress_selftest_prerun_diag.log', 'diag_c111c_regress_selftest_protocol.log', 'diag_c111c_regress_selftest_protocol_wiring.log', 'diag_c111c_regress_selftest_requires.log', 'diag_c111c_regress_selftest_retry_cap.log', 'diag_c111c_regress_selftest_stagexec_gate.log', 'diag_c111c_regress_selftest_stage_prerun_c103.log', 'diag_c111c_regress_selftest_stage_prerun_c106c.log', 'diag_c111c_regress_selftest_stage_prerun_c106e.log', 'diag_c111c_regress_selftest_stage_prerun_graphload.log', 'diag_c111c_regress_selftest_stage_prerun_headcmp_79-6.log', 'diag_c111c_regress_selftest_stage_prerun_stageplan.log', 'diag_c111c_regress_selftest_stoprecord_bgrun.log', 'diag_c111c_regress_selftest_stoprecord_eqform.log', 'diag_c111c_regress_selftest_stoprecord_offline_c107.log', 'diag_c111c_regress_selftest_stoprecord_supersession.log', 'diag_c111c_regress_selftest_stoprecord_table.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 14 logs recorded a failure; unreviewed: ['diag_c111e_md5.log']
  FAIL  A4 every archived review says what was done with it: 59/60 annotated; blank: ['2026-09-27-c103-scratch-selftest.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 5147 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['diag_c111c_regress_selftest_protocol_wiring.log', 'diag_c111d_items.log', 'diag_c111e_census_dump.log']

  C1 builds run 35, failure markers 40, logs carrying a failure 14
  C2 peer reviews dispatched 11, archived 60
  C3 wall-clock inside bgrun, BUILDS ONLY 53 min 11 s
  C4 wall-clock inside bgrun, REVIEWS 12 min 56 s; cost $7.7517 from 6 log(s) that report one
  C4b cost lines seen 6 / parsed 6
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 66 min 7 s  (builds 80%, reviews 19%, judgement session 0%)

  C6 material-marked recipe/bench runs 38, judgement-session attempts refused 9  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 438 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/diag_c111_b1_errorlist.py, tools/bench/diag_c111b_b1graph.py, tools/bench/diag_c111b_shots.py, tools/bench/diag_c111b_tunnelitems.py, tools/bench/diag_c111c_dry_negative.py, tools/bench/diag_c111c_realstore.py, tools/bench/diag_c111c_regress.py, tools/bench/diag_c111d_items.py, tools/bench/diag_c111d_reverdict.py, tools/bench/diag_c111e_census_dump.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/846 ok; 505 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2516 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:372 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 638 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (57; read them directly, they are the primary record) ===
tools/bench/diag_c111_b1_errorlist.log  (2026-09-27 20:58:40)
tools/bench/diag_c111_b1_errorlist_selfcheck.log  (2026-09-27 20:30:21)
tools/bench/diag_c111_b1_errorlist_selfcheck2.log  (2026-09-27 20:36:12)
tools/bench/diag_c111b_b1graph.log  (2026-09-27 21:15:14)
tools/bench/diag_c111b_b1graph_offline.log  (2026-09-27 21:18:14)
tools/bench/diag_c111b_shots.log  (2026-09-27 21:20:08)
tools/bench/diag_c111b_tunnelitems.log  (2026-09-27 21:27:17)
tools/bench/diag_c111b_tunnelitems_dry.log  (2026-09-27 21:15:41)
tools/bench/diag_c111b_tunnelitems_dry2.log  (2026-09-27 21:16:19)
tools/bench/diag_c111b_tunnelitems_dry3.log  (2026-09-27 21:16:33)
tools/bench/diag_c111b_tunnelitems_dry4.log  (2026-09-27 21:18:28)
tools/bench/diag_c111b_tunnelitems_prerun.log  (2026-09-27 21:16:43)
tools/bench/diag_c111b_tunnelitems_prerun2.log  (2026-09-27 21:18:29)
tools/bench/diag_c111c_dry_negative.log  (2026-09-27 21:16:48)
tools/bench/diag_c111c_realstore.log  (2026-09-27 21:42:31)
tools/bench/diag_c111c_realstore2.log  (2026-09-27 21:42:56)
tools/bench/diag_c111c_regress.log  (2026-09-27 21:26:23)
tools/bench/diag_c111c_regress2.log  (2026-09-27 21:39:25)
tools/bench/diag_c111c_regress_selftest_c103d_hooks.log  (2026-09-27 21:38:50)
tools/bench/diag_c111c_regress_selftest_c106d_tools.log  (2026-09-27 21:38:50)
tools/bench/diag_c111c_regress_selftest_c108e_tools.log  (2026-09-27 21:38:57)
tools/bench/diag_c111c_regress_selftest_c110_launchgate.log  (2026-09-27 21:38:48)
tools/bench/diag_c111c_regress_selftest_launch_gate.log  (2026-09-27 21:38:48)
tools/bench/diag_c111c_regress_selftest_prerun_diag.log  (2026-09-27 21:38:49)
tools/bench/diag_c111c_regress_selftest_protocol.log  (2026-09-27 21:39:06)
tools/bench/diag_c111c_regress_selftest_protocol_wiring.log  (2026-09-27 21:39:15)
tools/bench/diag_c111c_regress_selftest_requires.log  (2026-09-27 21:39:15)
tools/bench/diag_c111c_regress_selftest_retry_cap.log  (2026-09-27 21:39:23)
tools/bench/diag_c111c_regress_selftest_stage_prerun_c103.log  (2026-09-27 21:35:44)
tools/bench/diag_c111c_regress_selftest_stage_prerun_c106c.log  (2026-09-27 21:37:59)
tools/bench/diag_c111c_regress_selftest_stage_prerun_c106e.log  (2026-09-27 21:38:31)
tools/bench/diag_c111c_regress_selftest_stage_prerun_graphload.log  (2026-09-27 21:38:31)
tools/bench/diag_c111c_regress_selftest_stage_prerun_headcmp_79-6.log  (2026-09-27 21:38:36)
tools/bench/diag_c111c_regress_selftest_stage_prerun_stageplan.log  (2026-09-27 21:38:48)
tools/bench/diag_c111c_regress_selftest_stagexec_gate.log  (2026-09-27 21:39:25)
tools/bench/diag_c111c_regress_selftest_stoprecord_bgrun.log  (2026-09-27 21:38:58)
tools/bench/diag_c111c_regress_selftest_stoprecord_eqform.log  (2026-09-27 21:39:00)
tools/bench/diag_c111c_regress_selftest_stoprecord_offline_c107.log  (2026-09-27 21:38:57)
tools/bench/diag_c111c_regress_selftest_stoprecord_supersession.log  (2026-09-27 21:39:02)
tools/bench/diag_c111c_regress_selftest_stoprecord_table.log  (2026-09-27 21:38:58)
tools/bench/diag_c111d_items.log  (2026-09-27 21:49:55)
tools/bench/diag_c111e_census_dump.log  (2026-09-27 21:53:30)
tools/bench/diag_c111e_census_dump2.log  (2026-09-27 21:53:43)
tools/bench/diag_c111e_md5.log  (2026-09-27 22:02:25)
tools/bench/diag_c111e_peek.log  (2026-09-27 21:50:42)
tools/bench/diag_c111e_peek2.log  (2026-09-27 21:52:54)
tools/bench/diag_c111e_peek3.log  (2026-09-27 21:54:36)
tools/bench/diag_c111e_peek4.log  (2026-09-27 21:56:02)
tools/bench/errorlist_check_c111d.log  (2026-09-27 22:00:35)
tools/bench/jev_gate.log  (2026-09-27 22:05:06)
tools/bench/motor_session_end_cycle110.log  (2026-09-27 20:20:04)
tools/bench/motor_session_start_cycle111.log  (2026-09-27 20:20:11)
tools/bench/plan_l2b2a_sim.log  (2026-09-27 21:56:45)
tools/bench/plan_l2b2a_sim2.log  (2026-09-27 21:57:45)
tools/bench/selftest_c111c_launchunit.log  (2026-09-27 21:18:09)
tools/bench/selftest_c111c_launchunit2.log  (2026-09-27 21:33:34)
tools/bench/selftest_stagexec_c111c.log  (2026-09-27 21:19:06)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (11) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_110.log  (2026-09-27 20:19:48)
tools/bench/cycle_111.log  (2026-09-27 20:20:12)
tools/bench/cycle_runner.log  (2026-09-27 20:20:12)
tools/bench/cycle_runner_main_20260927c.log  (2026-09-27 20:20:12)
tools/bench/peer_c111a_selfcheck.log  (2026-09-27 20:34:48)
tools/bench/peer_c111c_realstore.log  (2026-09-27 21:45:43)
tools/bench/peer_c111c_regress.log  (2026-09-27 21:31:52)
tools/bench/peer_c111c_stageplan.log  (2026-09-27 21:41:45)
tools/bench/peer_c111e_peek.log  (2026-09-27 21:52:28)
tools/bench/peer_priorart_c111e_l2b2a.log  (2026-09-27 22:01:09)
tools/bench/retro.log  (2026-09-27 22:05:10)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle111","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 111 (20:18:43 to 22:05:10)

The cycle's outcome was good. L2-B1 became the bed: `result_111-4.json:8-10` shows 99/99 items licensed and a reverdict of OK. The owed dry-run device was built (`diag_c111c_dry_negative.log:24`, 7 of 7 rows reported in one run). It used 5 of 6 dispatches and 106 of 180 minutes. The claim on the card still fails on one fault in the last dispatch. A second line is added only because the device rule says any failed device must be reported.

## The most costly structural fault: `wrong-ordering`, the B2a planning card (111-5) went ahead of the B2 tooling

- **What happened.** Decision PD225(f) (`docs/d1-loop12-17-split-plan.md:1937`) sent card 111-5 at 21:49:10 (`guard_card.log:386`) to make L2-B2a launch-ready. The card included row B2-15.
- **The session already knew B2-15 could not be routed.** The tooling had already been ordered before any B2 work (`brief_110-3.md:12-14`). The judgement session's own card from 47 minutes earlier named `rw_403_2282` (B2-15) as a dead row (`task_111-3.json:30`). The 111-3 negative test had measured that row as UNROUTABLE at 21:16 (`diag_c111c_dry_negative.log:24`).
- **What it cost.** The prior-art review returned already-failed and settled-already (`priorart-c111e-l2b2a.md:506-508, 494-498`). The card ended BLOCKED (`result_111-5.json:1-3`), and the session admits the fault at PD225(h) (`:1942`).
  - Wall-clock: 21:49:10 to 22:02:25, about 13 min, run in parallel with card 111-4.
  - Money: $1.6506 for the prior-art review (`peer_priorart_c111e_l2b2a.log:6`), which was spent only because a recipe that could not be released was written.
  - Side cost: guard_peer held card 111-4 for about 8 min because of 111-5's failing peek log (`result_111-4.json:14`).
  - Not all wasted: the card produced the PD158 crossing and found gap (i), that wiring to shift registers already on the bed is unsupported (`stagexec.py:406-409`). The loss is gross, not net.
- **Counterfactual.** Suppose PD225(f) at about 21:48 had sent the tooling card (brief_110-3 (b)–(e)) alongside 111-4:
  - 111-4 would not have been held and would have ended about 21:52 instead of 22:00:35.
  - The cycle would still have closed around 22:05, but with tooling under way instead of a BLOCKED plan.
  - Cycle 112 would start at PD225(h)4 (re-simulate and dry run) instead of (h)3.

## Device rule (threshold 1): `device-failed`, a gate refused an offline dry run

- **What the 07:46 device promised.** The device decided 2026-09-27 07:46 was meant to let the offline checker `stage_prerun --dry|--prerun <recipe>` through the launch gate, "offline checks that precede a release" (`violation-decisions.md:1519-1521`).
- **It was repaired in stop_record only.** `guard_cycle.py:40`'s `BUILD_RE` matches `\bpy` inside the `.py --dry tools/recipes/…` part of `py -u tools/stage_prerun.py --dry tools/recipes/stage_d1_l2b2a.py`. The prior-art verdict check at `guard_cycle.py:612` has no command-class check, and guard_cycle does not use `launchunit.py` (checked by grep).
- **What happened in this window.**
  - The dry was attempted at 21:58:39 (before the prior-art review) and at 22:01:39 (after it), per `material_marker.log:2516`/`:2518`. No `plan_l2b2a_dry.log` exists.
  - The card's first failure is "--dry refused by guard_cycle.py" (`result_111-5.json:2`).
  - The review had named this dry run as its discriminating test. The collecting dry built this cycle was never run on B2.
  - PD225(h)'s tooling list therefore rests on reading code, not on a measurement ("verbs NOT shown (dry refused)", `result_111-5.json:12`).
- **Cost:** about 3 min; no log carries a dollar figure.
- **Counterfactual.** With guard_cycle classifying launches through `launchunit`, the 22:01:39 dry would have run in about 1 min. It would have returned the measured unroutable list for all 7 rows. The end time would not have changed.
- **The same pattern appeared once more.** At 22:01:59 the stop record refused a read-only PowerShell hash (`$f = @(...)`, `material_marker.log:2519`). The agent reran it as `diag_c111e_md5.py` at 22:02:24 (`:2520`).
- This is the fourth code path in a row to get the read-only repair after the others (`violation-decisions.md:1545, 1564-1565`).

## Findings

**1. Repeated failure.** Eight of the cycle's new diagnostic or self-test scripts failed on their first run (`jev_gate.log:2148, 2158, 2163-2166, 2174, 2188, 2193, 2197`). Five paid hypothesis reviews followed, $6.10 in total. Four of them found real problems (c111a double credit, c111c-regress rule narrowing, stageplan hidden regression, realstore harness mechanism). The peek review ($0.7852) found only the session's own script bug. No attempt needed a change of approach, but the gate threshold did. `diag_c111e_peek.log` scored p=0.666, just over the 0.65 cut-off, and that is what held 111-4.

**2. Missing tool.**
- brief_110-3 (b), "stagesim finalize runs `connect_route`", was not built. Without it, `plan_l2b2a_sim2.log` called a plan with 3 unroutable rows "final, open_rows_match". It would have caught B2-15, B2-11 and B2-14 at plan time.
- `launchunit` is not wired into guard_cycle, which is the second fault above.

**3. Unmeasured steps.**
- The `requires` list on card 111-5 names only files (`task_111-5.json:20-30`). `protocol.py requires` therefore passed without checking anything. Listing the two missing verbs would have come back MISSING in seconds, before any dispatch.
- Gap (i) is inferred from reading `stagexec.py:406-409`, not measured.

**4. Rule compliance.**
- The CLAUDE.md judgement/material split holds. A delegation brief states the measurement, not the action, and cards 111-4 and 111-5 kept the bed and row decisions for the judgement session.
- The card rule "a gate refusal is returned BLOCKED, never re-run via an exempt route" (`task_111-5.json:73`) was bent, harmlessly: the read-only hash refused at `:2519` was rerun through a new script.
- The audit is wrong or blind in three places:
  - A1 FAIL is a false positive. The 22 logs were written by a subprocess of `diag_c111c_regress.py:62`, which itself ran under bgrun (`material_marker.log:2499`).
  - C6's "judgement-session attempts refused 9" is mislabelled. Those lines are refusals of material-agent commands, and four are self-test fixtures (`:2493-2494, 2500-2501`).
  - C7 lists 438 files and has stopped carrying information.
- The audit does not see gate refusals made inside hooks, such as guard_cycle's, which log nowhere. It also does not see self-reported minutes.

**5. Ordering.**
- 111-1 first, then 111-2 alongside 111-3: this order was sound.
- The 21:49 slot should have gone to the tooling card (the main fault above).
- `next.json:10-15` puts five scratch-verified tooling items, a re-simulation, a dry run, a pre-run, prior-art and a launch into one act. Card 111-3 took about 45 min and 3 reviews for two items, so the split rule applies to cycle 112 before it starts.

**6. What was not reported.**
- The self-reported minutes are impossible:
  - `result_111-2.json:28` says 80 min and `result_111-3.json:34` says 105 min, but both cards were bound at 21:02:49–50 (`guard_card.log:380-381`), leaving at most 62 min.
  - `result_111-1.json:28` says 48 min, against at most 40.6 min between 20:22:10 and 21:02:49.
  - Both "over the 60-min budget" notes are false, and that is the trigger for escalation.
- The STATUS summary of 111-5 omits that the dry run was blocked by a gate defect.
- `diag_c111e_md5.log` ended rc=1 because the judgement session pinned an old md5 for `stage_d1_l2b1.py` in the card (`task_111-5.json:16` vs `diag_c111e_md5.log:8`). That log is still unreviewed (audit A3) and may hold cycle 112's first build.

**7. Judgement inside a material session.**
- The 111-3 material session narrowed decision 15:49 (`py -m`: only READONLY_MODULES count as non-launches) and shipped it into three hooks before the judgement session saw it (`result_111-3.json:26`). The judgement session ratified it afterwards at PD225(e). The narrowing fails safe, but it was a design change made in the material session.
- The 111-5 material session wrote "ACCEPTED in full" on the prior-art review (`priorart-c111e-l2b2a.md:532`). The card required the annotation (`task_111-5.json:35`), but it correctly left the row-set choice open.

## Device effect

| Device (decided) | Held in this window? |
|---|---|
| bgrun rc vs inner (09-16), FAIL scan (09-17 03:38) | Yes: `diag_c111e_md5.log:14`, `diag_c111c_realstore2.log:21` forced rc=1 |
| peer confirm-bait (09-16) | Not exercised |
| prior-art review (09-16) | Yes: fired correctly on 111-5 |
| blank-disposition refusal (09-16 15:05) | Yes: all in-window reviews annotated (A4's blank one is c103) |
| C3/C4 cost split, COST regex (09-16 15:05, 21:07) | Yes: C4 $7.7517 = sum of 6 COST lines, 6/6 parsed |
| premature-build timing gate (09-16 19:16) | Fired on the dry checker at 21:58:39; part of the device failure |
| C7 scope counter (09-16 19:16) | No scope creep; counter saturated (438) |
| stop record + launch gate (09-18, 09-24 ×3, 09-27 01:15/01:55) | Launch stop held. Read-only refusal recurred (`material_marker.log:2519`) and was worked around (`:2520`) |
| guard_peer retry gate (09-24 03:53) | Fired on the wrong card (held 111-4 about 8 min, `result_111-4.json:14`); not bypassed |
| selftest_exempt closure (09-25 05:58) | Yes: `guard_card.log:382` |
| collect-all-unroutable dry (09-25 16:10 / 09-27 20:20) | Built (111-3); never run on B2 because the dry was refused |
| gates_due at cycle start (09-26 14:10, 09-27 08:30) | Yes: `cycle_111.json:28-44` |
| next.json plan path (09-25 14:28) | Yes: audit C7 used it |
| **stage_prerun --dry passes the gate (09-27 07:46)** | **Failed:** the same argv shape was refused by `guard_cycle.py:612` (`result_111-5.json:2`) |
| py -m launch unit (09-27 15:49) | Built on 3 paths (33/0); guard_cycle's `BUILD_RE` is an unpatched fourth path |
| retry cap, SimReader, ExecStop sink gates, graph shape, memory prediction, VISA precheck, OpLoopEndRef, Jev exemption, SendMessage refusal, bgrun reap, motor FAIL lines | Not exercised (no stage or real run) or passed (A2) |

VIOLATION: wrong-ordering | loss_min=13 | loss_usd=1.65 | evidence=docs/d1-loop12-17-split-plan.md:1937
VIOLATION: device-failed | loss_min=3 | loss_usd=? | evidence=tools/bench/cards/result_111-5.json:2
VERDICT {"schema":"verdict/1","id":"retrospective-cycle111","verdict":"refuted","alternative":"No structural fault: 111-5 still yielded the PD158 crossing and gap (i) (existing-register route) that a tooling card could not have known, and the dry refusal cost ~3 min without changing the cycle's end.","discriminating_test":"Feed guard_cycle.main() offline the 22:01:39 argv (bgrun -- py -u tools/stage_prerun.py --dry tools/recipes/stage_d1_l2b2a.py): if BUILD_RE matches via '.py --dry' and :612 blocks, the device failure stands.","violations":[{"slug":"wrong-ordering","loss_min":13,"loss_usd":1.65,"evidence":"docs/d1-loop12-17-split-plan.md:1937"},{"slug":"device-failed","loss_min":3,"loss_usd":"?","evidence":"tools/bench/cards/result_111-5.json:2"}],"sources":["tools/bench/cards/brief_110-3.md:12","tools/bench/cards/task_111-3.json:30","tools/bench/diag_c111c_dry_negative.log:24","archive/peer/2026-09-27-priorart-c111e-l2b2a.md:506","tools/bench/peer_priorart_c111e_l2b2a.log:6","tools/hooks/guard_cycle.py:40","tools/hooks/guard_cycle.py:612","docs/violation-decisions.md:1519","tools/hooks/material_marker.log:2519"],"note":"Device named: 07:46 'stage_prerun --dry passes the launch gate', repaired in stop_record only; guard_cycle BUILD_RE/verdict gate still refuses it. Same pattern: read-only hash refused at material_marker.log:2519, rerun as script at :2520."}

## Sources

(extract from answer)

## What was done with it

- `wrong-ordering` (13 min, $1.65, `docs/d1-loop12-17-split-plan.md:1937`): ACCEPTED, and the fault is my judgement.
  - PD225(f) named B2a's rows and dispatched 111-5 to plan them, even though brief_110-3 item 3 had already put the B2 tooling ahead of B2. The prior-art gate caught it.
  - Recorded in PD225(h). Cycle 112's FIRST card is the B2 tooling card (items (i)–(v)), and B2a is re-planned only after it.
  - No new device: 111-5 BLOCKED correctly at the existing prior-art gate, and the card rule stands — a card that plans a stage first lists each row's route (verb) against the existing tooling.
- `device-failed` (3 min, `tools/bench/cards/result_111-5.json:2`): ACCEPTED, threshold 1.
  - The 07:46 decision ("`stage_prerun --dry|--prerun` of an unreleased recipe is an offline check that precedes a release") was applied only in `stop_record`. `guard_cycle`'s prior-art verdict gate (`tools/hooks/guard_cycle.py:612`, via BUILD_RE) still refuses that dry.
  - Device: `guard_cycle` gets the same offline exemption through the shared `tools/launchunit.py` / `stop_record.offline_checker` path, and it still refuses launches. The review's discriminating test (feed `guard_cycle.main()` the 22:01:39 argv) goes first, as the negative.
  - Added to cycle 112's tooling card as item (vi) (`docs/violation-decisions.md` device-failed 2026-09-27 22:20).
- Verdict `refuted` (alternative: "no structural fault, 111-5 still yielded the PD158 crossing and gap (i)"): partly accepted. 111-5's facts are used in PD225(h), but the ordering fault stands, because the gap was already on file in brief_110-3.
