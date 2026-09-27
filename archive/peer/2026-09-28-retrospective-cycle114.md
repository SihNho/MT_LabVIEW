# retrospective-cycle114

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.2511  in 40 / out 31525 / cache-create 152186 / cache-read 2014917  (319s, 38 turn(s))
- **date:** 2026-09-28 04:25:44
- **outcome:** ANSWERED (321s)
- **verdict-card:** VERDICT-CARD retrospective-cycle114 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle114.json
- **why asked:** cycle-114 close (CLAUDE.md §3 retrospective)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle114, role retrospective) ---
CLAIM: Cycle 114 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 114 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-28 02:19:04  ..  2026-09-28 04:20:20   (121 min)
    basis: start = archive/peer/2026-09-28-retrospective-cycle113.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-27 22:20): through by the shared `tools/launchunit.py` / `stop_record.offline_checker` route, and still refuses launches. Test cases: the 22:01:39 argv (`bgrun -- py -u tools/stage_prerun.py --dry tools/recipes/stage_d1_l2b2a.py`) must pass, and `py -u tools/recipes/stage_d1_l2b2a.py` must still be refused while the prior-art verdict is unreleased.
  - `repeated-failure-class` (decided 2026-09-28 02:25): open row at the stage's end is FLAGGED as a predicted name change. The card must then either declare the renamed pair or defer the row. Acceptance: replayed on `tools/bench/plan_l2b1*.json` and `tools/bench/plan_l2b2b_9row.json`, it flags `#2626` and `#11261` and nothing else. It is built first in cycle 114's card (`docs/d1-loop12-17-split-plan.md` PD227(j)).

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

== cycle audit, 2026-09-28 02:19 .. 2026-09-28 04:20 (121 min, an explicit cycle window): 47 build logs, 10 peer logs, 13 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 33/47 ok; NO BGRUN line in ['selftest_control_path_lint_c114d.log', 'selftest_stagesim_c114d.log', 'selftest_stagesim_k79_c114d.log', 'selftest_stagesim_l2a1_80_c114d.log', 'selftest_stagesim_unflip_81_c114d.log', 'selftest_stage_prerun_c103_c114d.log', 'selftest_stage_prerun_c106c_c114d.log', 'selftest_stage_prerun_c106e_c114d.log', 'selftest_stage_prerun_c110g_c114d.log', 'selftest_stage_prerun_c114d_c114d.log', 'selftest_stage_prerun_c114_c114d.log', 'selftest_stage_prerun_graphload_c114d.log', 'selftest_stage_prerun_headcmp_79-6_c114d.log', 'selftest_stage_prerun_stageplan_c114d.log']
  FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['runner_supervisor.log']
  FAIL  A3 every failing log is followed by an archived review: 5 logs recorded a failure; unreviewed: ['selftest_stage_prerun_stageplan_c114d.log']
  PASS  A4 every archived review says what was done with it: 13/13 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 5789 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 4 log(s) with a run that printed none: ['diag_c114_md5.log', 'diag_c114_peek1.log', 'diag_c114_peek2.log', 'diag_c114_peek3.log']

  C1 builds run 33, failure markers 31, logs carrying a failure 5
  C2 peer reviews dispatched 10, archived 13
  C3 wall-clock inside bgrun, BUILDS ONLY 51 min 1 s
  C4 wall-clock inside bgrun, REVIEWS 9 min 15 s; cost $5.6969 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 60 min 16 s  (builds 84%, reviews 15%, judgement session 0%)

  C6 material-marked recipe/bench runs 18, judgement-session attempts refused 10  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 230 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/cards/plan_114-1_l2b3.md, tools/bench/diag_c114_b2bgraph.py, tools/bench/diag_c114_errorlist.py, tools/bench/diag_c114_md5.py, tools/bench/diag_c114_peek.py, tools/bench/diag_c114_plan.py, tools/bench/diag_c114c_b3graph.py, tools/bench/diag_c114c_peek.py, tools/bench/diag_c114d_regress.py, tools/bench/diag_c114d_replay.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/867 ok; 526 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2553 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:430 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 643 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A2 every bgrun ended (END or TIMEOUT), A3 every failing log is followed by an archived review


=== BUILD LOGS INSIDE THE WINDOW (48; read them directly, they are the primary record) ===
tools/bench/diag_c114_b2bgraph.log  (2026-09-28 03:21:48)
tools/bench/diag_c114_md5.log  (2026-09-28 03:37:43)
tools/bench/diag_c114_peek1.log  (2026-09-28 03:08:11)
tools/bench/diag_c114_peek2.log  (2026-09-28 03:08:12)
tools/bench/diag_c114_peek3.log  (2026-09-28 03:22:58)
tools/bench/diag_c114_plan.log  (2026-09-28 03:22:37)
tools/bench/diag_c114c_b3graph.log  (2026-09-28 03:51:43)
tools/bench/diag_c114c_errorlist.log  (2026-09-28 04:04:41)
tools/bench/diag_c114c_peek.log  (2026-09-28 03:41:36)
tools/bench/diag_c114d_regress.log  (2026-09-28 03:53:08)
tools/bench/diag_c114d_regress_r2.log  (2026-09-28 04:17:34)
tools/bench/diag_c114d_replay_post.log  (2026-09-28 03:47:30)
tools/bench/diag_c114d_replay_post2.log  (2026-09-28 04:12:16)
tools/bench/diag_c114d_replay_pre.log  (2026-09-28 03:43:31)
tools/bench/diag_c114e_inventory.log  (2026-09-28 04:12:07)
tools/bench/diag_c114e_inventory2.log  (2026-09-28 04:12:55)
tools/bench/jev_gate.log  (2026-09-28 04:20:14)
tools/bench/motor_session_end_cycle113.log  (2026-09-28 02:20:19)
tools/bench/motor_session_start_cycle114.log  (2026-09-28 03:05:01)
tools/bench/runner_supervisor.log  (2026-09-28 03:07:34)
tools/bench/selftest_control_path_lint_c114.log  (2026-09-28 03:19:33)
tools/bench/selftest_control_path_lint_c114d.log  (2026-09-28 04:11:59)
tools/bench/selftest_stage_prerun_c103_c114.log  (2026-09-28 03:18:51)
tools/bench/selftest_stage_prerun_c103_c114d.log  (2026-09-28 04:14:24)
tools/bench/selftest_stage_prerun_c106c_c114.log  (2026-09-28 03:16:35)
tools/bench/selftest_stage_prerun_c106c_c114d.log  (2026-09-28 04:16:42)
tools/bench/selftest_stage_prerun_c106e_c114.log  (2026-09-28 03:19:25)
tools/bench/selftest_stage_prerun_c106e_c114d.log  (2026-09-28 04:17:15)
tools/bench/selftest_stage_prerun_c110g_c114.log  (2026-09-28 03:16:36)
tools/bench/selftest_stage_prerun_c110g_c114d.log  (2026-09-28 04:17:15)
tools/bench/selftest_stage_prerun_c114.log  (2026-09-28 03:10:28)
tools/bench/selftest_stage_prerun_c114_c114d.log  (2026-09-28 04:17:32)
tools/bench/selftest_stage_prerun_c114b.log  (2026-09-28 03:13:30)
tools/bench/selftest_stage_prerun_c114d_c114d.log  (2026-09-28 04:17:34)
tools/bench/selftest_stage_prerun_graphload_c114.log  (2026-09-28 03:19:27)
tools/bench/selftest_stage_prerun_graphload_c114d.log  (2026-09-28 04:17:15)
tools/bench/selftest_stage_prerun_headcmp_79-6_c114d.log  (2026-09-28 04:17:21)
tools/bench/selftest_stage_prerun_headcmp_c114.log  (2026-09-28 03:19:32)
tools/bench/selftest_stage_prerun_stageplan_c114.log  (2026-09-28 03:14:12)
tools/bench/selftest_stage_prerun_stageplan_c114d.log  (2026-09-28 04:12:16)
tools/bench/selftest_stagesim_c114d.log  (2026-09-28 04:11:38)
tools/bench/selftest_stagesim_c114d_pre.log  (2026-09-28 03:42:59)
tools/bench/selftest_stagesim_k79_c114d.log  (2026-09-28 04:11:39)
tools/bench/selftest_stagesim_l2a1_80_c114d.log  (2026-09-28 04:11:46)
tools/bench/selftest_stagesim_unflip_81_c114d.log  (2026-09-28 04:11:59)
tools/bench/stage_d1_l2b3.log  (2026-09-28 03:30:51)
tools/bench/stage_d1_l2b3_dry.log  (2026-09-28 03:24:09)
tools/bench/stage_d1_l2b3_prerun.log  (2026-09-28 03:24:31)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (10) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_113.log  (2026-09-28 02:20:13)
tools/bench/cycle_114.log  (2026-09-28 03:05:02)
tools/bench/cycle_runner.log  (2026-09-28 03:05:02)
tools/bench/cycle_runner_main_20260927c.log  (2026-09-28 02:20:20)
tools/bench/cycle_runner_main_20260928a.log  (2026-09-28 03:05:02)
tools/bench/peer_c114a_selftest.log  (2026-09-28 03:12:42)
tools/bench/peer_c114b_l2b3d.log  (2026-09-28 03:36:52)
tools/bench/peer_c114d_regress.log  (2026-09-28 04:10:16)
tools/bench/peer_priorart_c114a_l2b3.log  (2026-09-28 03:26:31)
tools/bench/retro.log  (2026-09-28 04:20:19)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle114","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Retrospective of cycle 114 (02:19:04 – 04:20:20)**

**Window check.** The window matches the evidence, but it has one idle stretch. From 02:20 to 03:04 nothing belongs to cycle 114. The runner stopped gracefully on its 480-min budget (`tools/bench/cycle_runner.log:709`) and was relaunched at 03:04 (`:711-715`). Cycle 114's judgement session started at 03:05:02 (`tools/bench/cycle_114.log:1`). Those 44 minutes are not charged here.

A2's "unfinished `runner_supervisor.log`" is not a fault either. It is a supervisor with a 7-day limit that is still running (`tools/bench/runner_supervisor.log:1`).

**Outcome.** The cycle delivered:
- The device owed from cycle 113 (gate X11).
- L2-B3, measured and accepted as the new bed (`docs/d1-loop12-17-split-plan.md:2023-2028`).
- The simulator taught the rule that a `connect_from_wire` across a structure border re-creates the source wire, plus a new pre-run gate X12.
- The L2-R inventory and its decisions (`:2035-2048`).

That is good work for about 75 active minutes. Two faults of similar size cost roughly a third of it.

---

## The most costly structural fault: stale count checks, paid for a third time (repeated-failure-class)

**What happened**
- Card 114-3's regression run failed 12/2 at 03:53:08 (`tools/bench/diag_c114d_regress.log:5-6,17-18`).
- The cause was two self-test checks, E1 and U3, that require the simulator self-test to report exactly 42 pass / 0 fail. The simulator had grown to 75 gates.
- The same two failures are on record at cycle 101 and cycle 112 (`archive/peer/2026-09-28-c114d-regress.md:92`).
- On 2026-09-27 the cycle-112 review said "the only fix needed is to replace the pinned counts with fail == 0 and pass ≥ the old count" (`tools/bench/peer_c112a_unflip81.log:28`). Its disposition accepted the diagnosis but never applied the fix (`archive/peer/2026-09-27-c112a-unflip81.md:81-88`).
- The judgement session then wrote card 114-3 as follows:
  - It required "stagesim and stage_prerun self-tests 0 failures" (`tools/bench/cards/task_114-3.json:28`).
  - It set `peers: []` (`:54`), so the card could not dispatch a review.
  - It said "no existing gate or check is loosened" (`:59`), so the card could not re-pin the checks either.
- The failure was therefore certain before the card started, and the card could not clear it. 114-3 came back BLOCKED (`tools/bench/cards/result_114-3.json:1-3`).

**What it cost**
- Review c114d: $1.1637, 105 s (`archive/peer/2026-09-28-c114d-regress.md:7`).
- A whole extra material card, 114-4, 27 min (`tools/bench/cards/result_114-4.json:31`). That was the 5th of 6 allowed material dispatches.
- guard_peer refused 114-5's first run because of the other card's failing log (`tools/bench/cards/result_114-5.json:25`).
- The review found nothing new. Its new-looking findings (no frozen label check, U3 never checks the exit code) came back as OPEN and were not applied (`tools/bench/cards/result_114-4.json:28`).

**Counterfactual**
- Suppose E1/U3 had been re-pinned when the cycle-112 review said so (2026-09-27 22:46), or 114-3's pass criterion had exempted the two failures already on record.
- Then `diag_c114d_regress.log` would have passed at 03:53:08, and card 114-4 would not have existed.
- 114-5 is a 1-second offline run (`tools/bench/diag_c114e_inventory2.log`). It could have been dispatched around 03:55 and finished beside 114-2, which ended at 04:04:41 (`tools/bench/diag_c114c_errorlist.log:127`).
- The retrospective would have started around 04:08 instead of 04:20:19, about 12 minutes earlier.
- `loss_usd` is 1.16, the review only. No material session logs a cost (`cost.usd: null` in all five result cards).

## Second fault, of about the same size: the prior-art device missed a contradiction it exists to catch (device-failed)

**What happened**
- The L2-B3 plan asserted that the three source wires w28392, w5174 and w5336 were "source-only", having "lost their sinks" (`archive/peer/2026-09-28-priorart-c114a-l2b3.md:99`).
- The graph the plan itself cites, `graph_l2b2b_20260928.json`, shows each of them still carrying sinks (`archive/peer/2026-09-28-c114b-l2b3d.md:43-49`).
- The measured behaviour for exactly that case was already on file: `tools/bench/opmodels/connect_from_wire.json:266` records that "the SOURCE's wire is RE-CREATED under a new uid". The simulator ignored that and applied its own "join" rule (`connect_from_wire.json:4`).
- The prior-art review reported no contradictions (A3, "None found", `priorart-c114a-l2b3.md:539`). It admitted "What I did not check: whether the … source wires had already lost their sinks" (`:544`) and still returned `novel` (`:553`).
- The material session then declined the review's offline test. Its reason was that "the one launch's per-op step diff measures this case directly" (`:566`).
- The launch at 03:27 failed gate D: 6 new / 3 lost wires against a prediction of 3 / 0 (`tools/bench/cards/result_114-1.json:2`). That used up 114-1's failure budget, so the Error List step (P7) did not run.

**What it cost**
- Review c114b: $2.0165, 276 s (`c114b-l2b3d.md:7`).
- A verification read of the saved B3 file: 409 s (`tools/bench/diag_c114c_b3graph.log:317`).
- Wall-clock at the end of the cycle barely moved, because 114-2 ran in parallel with the simulator fix, and that fix was needed either way.

**Counterfactual**
- At 03:26:31, a read of the plan's own graph for sinks on those three wires (seconds, offline) would have removed the premise.
- The simulator fix (114-3, C1–C4) would have come first. The launch would have passed gate D and run P7 in the same card.
- That would have saved about 11 minutes of machine time and $2.02, with the end of the cycle roughly unchanged.

---

## FINDINGS

**1. Repeated failure.**
- The count-check failure is at its third occurrence: cycle 101, cycle 112, and now 114 (`c114d-regress.md:92,103`).
- The approach should have changed at occurrence 2, cycle 112. The fix was named there (`peer_c112a_unflip81.log:28`).
- Inside this cycle, the card should have changed at the moment it was written. The material session saw the failure was pre-existing (`result_114-3.json:21`), but the card left no way to act on that.
- The "wire uid changes after `connect_from_wire`" class is also a repeat. The retrospective of cycle 112 had already flagged the connect-from-wire purge as an unseparated confounder that "B2b will use" (`archive/peer/2026-09-28-retrospective-cycle112.md:344`).

**2. Missing tool.**
- Nothing checks that an accepted review's named fix was actually applied. A4 only checks that the "What was done" section is non-empty, and c112a's section is non-empty.
- The simulator does not derive its rules from `opmodels/*.json`. The join rule at `connect_from_wire.json:4` contradicted `:266` in the same file. 114-3 fixed only this one op (`result_114-3.json:16`).
- There is still no read-only `Wire.Is Broken?` reader. B3 was accepted without it, with other evidence standing in (`result_114-2.json:21`; `d1-loop12-17-split-plan.md:2029`).

**3. Unmeasured steps.**
- The source-wire sink check was declined (`priorart-c114a-l2b3.md:566`).
- 114-3 predicted "0 failures" against logs that already showed two.
- The review's two discriminating tests were not run: the git diff of G01–G42 and a real-graph replay of the new re-create path (`result_114-4.json:29-30`).
- `border_source_wire` is now switched on for every real plan with no check against a real read (`c114d-regress.md:73`).

**4. Rule compliance (CLAUDE.md).**
- The devil's-advocate pass "must end in a discriminating test … run the cheapest separator" (CLAUDE.md:662-664). The prior-art review supplied one and it was not run.
- Rule 4, STATUS stays one screen, is broken: 430 lines (audit L3).
- Failed-prediction review was satisfied on every failure (c114a, c114b, c114d). All three used the attack framing.
- RETRY_CAP held: one launch.
- The verification level is stated as STRUCTURAL (`:2028`).
- Audit false positives:
  - A1's 14 files are child logs of a batch that did run under bgrun (`diag_c114d_regress.log:1`).
  - A3's "unreviewed failure" `selftest_stage_prerun_stageplan_c114d.log` is a PASSING self-test (12/0, `:111-112`) whose FAIL rows are intended negative cases.
- What the audit does not cover:
  - Whether review fixes were applied.
  - Declined discriminating tests.
  - Material and judgement spend. C4's $5.70 is reviews only. C5's 60 min counts only time inside bgrun.
  - Blocks that one parallel card causes another.
  - C7 lists 230 files, mostly runner and Jev state files, so it cannot show scope.

**5. Ordering.**
- Doing the owed device first (S0) and running 114-2 and 114-3 in parallel were both good calls.
- The indefensible order was launch-then-model. `connect_from_wire.json:266` was on disk, and the simulator's cfw rule should have been reconciled with it before a gate that compares wire uids went live.

**6. What was not reported.**
- `result_114-2.json` does not record that its own peek run failed: rc=1, malformed RESULT line (`tools/bench/diag_c114c_peek.log:20`). The Jev ladder classed it as our-script-bug (`jev_gate.log:2350`).
- 114-4's rerun overwrote 114-3's failing per-child logs. This appears only in a note (`result_114-4.json:32`).
- The Jev ladder classed the count-pin failure as `new-problem p=0.730` (`jev_gate.log:2362`) although the class had been reviewed at c112a. That misclassification is what forced the review and the block, and no summary says so.
- `md5sum` over `tools/bench/*.py` was refused as a script run and worked around with Get-FileHash (`result_114-4.json:23`). This is a known carry (`STATUS.md:108`).

**7. Judgement inside a material session.**
- `priorart-c114a-l2b3.md:563-566`: the material session decided which discriminating experiment to run, and chose the launch itself. CLAUDE.md:327 reserves that decision for judgement. This is the root of the second fault.
- `c114b-l2b3d.md:130`: the material session "accepted as the corrected explanation" a choice between explanations. Low consequence, because it took no action and returned the question as OPEN.
- `c114a-selftest.md:74-75`: the material session narrowed the new device's own self-test (R4 limited to top-level files, `sim/**` reported as INFO only), although the reviewer said `sim/**` probably holds another #2626 case (`:62`). That is a design change to a device, taken inside material.
- `task_114-1.json:105` pre-scripts a conditional: "contradicted ⇒ BLOCKED unless every fix only narrows an existing gate". Deciding whether a fix only narrows a gate is a judgement call left to the material session. It did not trigger this cycle.

## DEVICE EFFECT
- **unreported-fact (bgrun exit code):** held. `selftest_stage_prerun_c114.log:16` and `diag_c114c_peek.log:20` forced rc=1 over "the process itself said 0". `unflip_81` still exits 0 on failure (`c114d-regress.md:99`), but the batch caught it.
- **rule-evaded (confirm-bait):** held. The attack set is present in all three hypothesis reviews.
- **tool-not-built (prior-art review):** **failed.** It never fired when it should have: no contradiction reported and a `novel` verdict against the plan's own graph and `connect_from_wire.json:266` (`priorart-c114a-l2b3.md:539,553`). Its partial answer was then set aside (`:566`).
- **repeated-failure-class (empty "What was done" block on dispatches):** held formally (A4 13/13). It cannot see that c112a's recorded fix was never applied.
- **C3/C4 cost split and COST regex:** held (C4b 4/4).
- **premature-build (guard_cycle):** held. Prior-art ended at 03:26:31 and the launch was at 03:27:02.
- **scope-creep counter (C7):** fired on the wrong thing: 230 entries, mostly state files. It is noise, but no scope creep occurred.
- **Stop record / launch gate, read-only pass-through:**
  - The stop record held: released by the novel record (`:567`).
  - The md5sum refusal (`result_114-4.json:23`) comes from guard_bash's material-exemption list, not from the stop_record/prerun code path that device covers. So it is a known carry here, not a device failure.
- **The 2026-09-28 02:25 Build Array device (X11):** built and held. The replay flagged only #2626 and #11261 (`result_114-1.json:19-20`).
- **The other devices** (motor fail-exit, the Jev scope, the SendMessage refusal, the graph-shape check, the other launch-gate carve-outs) had no occasion to fire in this window. No occurrence was found.

VIOLATION: repeated-failure-class | loss_min=12 | loss_usd=1.16 | evidence=tools/bench/peer_c112a_unflip81.log:28
VIOLATION: device-failed | loss_min=11 | loss_usd=2.02 | evidence=archive/peer/2026-09-28-priorart-c114a-l2b3.md:539

VERDICT {"schema":"verdict/1","id":"retrospective-cycle114","verdict":"refuted","alternative":"Both losses are small against a cycle that delivered B3 as bed plus X11/X12 and the sim fix; the pin failure could be read as normal regression hygiene and the prior-art miss as within the reviewer's measured 6.5/8 accuracy.","discriminating_test":"Grep all archived reviews for a fix named in an accepted disposition and check the code for it: if c112a's E1/U3 re-pin is the only unapplied one, fault 1 is a one-off; if several recur, it is a missing check-that-fixes-landed device.","violations":[{"slug":"repeated-failure-class","loss_min":12,"loss_usd":1.16,"evidence":"tools/bench/peer_c112a_unflip81.log:28"},{"slug":"device-failed","loss_min":11,"loss_usd":2.02,"evidence":"archive/peer/2026-09-28-priorart-c114a-l2b3.md:539"}],"sources":["tools/bench/diag_c114d_regress.log:5-6","tools/bench/cards/task_114-3.json:28","tools/bench/cards/task_114-3.json:54","archive/peer/2026-09-28-c114d-regress.md:92","archive/peer/2026-09-28-c114d-regress.md:103","archive/peer/2026-09-28-priorart-c114a-l2b3.md:544","archive/peer/2026-09-28-priorart-c114a-l2b3.md:566","archive/peer/2026-09-28-c114b-l2b3d.md:43-56","tools/bench/opmodels/connect_from_wire.json:266","tools/bench/jev_gate.log:2362","tools/bench/cards/result_114-4.json:31"],"note":"Cycle delivered (B3 accepted, PD228). Device-failed = prior-art review (tool-not-built device) missed A3 contradiction vs graph_l2b2b and cfw_2 model; material declined its offline test. Material/judgement spend unlogged; USD figures are review cost only."}

## Sources

(extract from answer)

## What was done with it

Annotated by the cycle-114 judgement session, 2026-09-28 04:3x.

- `repeated-failure-class` | 12 min: **ACCEPTED, mine.** I wrote card 114-3 with a "0 failures" regression pass, `peers: []`, and a
  no-loosening rule, while the E1/U3 count-pin failures were already on record (c101-4, c112a) with an accepted but unapplied fix.
  - Already applied in this cycle: card 114-4 re-pinned E1/U3 to a 0-fail assertion (`tools/bench/diag_c114d_regress_r2.log:17`, 14/0).
  - Owed in cycle 115's STEP 0 (PD229(b)): the rest of the c112a/c114d fix — a pass-count floor, the frozen G01-G42 label check, and an rc/`sys.exit(1)` in unflip_81 — plus the reviewer's discriminating test (grep accepted dispositions for named fixes and check the code for them).
  - Card rule from 115: a regression pass criterion lists the failures already on record and exempts them by name, or the card carries the peer it needs.
  - The slug's threshold count is left to `violations.py --due` at the next cycle start.
- `device-failed` | 11 min: **ACCEPTED** (threshold 1). The prior-art review returned `novel` while writing that it had not checked the premise, and `connect_from_wire.json:266` already recorded the behaviour the simulator ignored.
  - The specific hole is closed: stagesim `cfw_border_rule` and prerun X12 (114-3/114-4; the replay reproduces the real launch).
  - DEVICE owed FIRST in cycle 115 (`docs/violation-decisions.md` 2026-09-28 04:3x): an opmodel conformance check. `stage_prerun --prerun` replays every recorded sample in `tools/bench/opmodels/<op>.json` for each op the plan uses through stagesim's rule, and FAILS the pre-run on any sample whose measured wire outcome (new/lost uids, sinks kept) the simulator does not reproduce.
  - Acceptance: the check passes on `connect_from_wire.json` with the current stagesim and FAILS with `cfw_border_rule` disabled.
  - Card rule from 115: a review's offline test marked "not checked" is either run or returned `open` to judgement; the material session does not waive it.
