# retrospective-cycle115

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $1.5345  in 44 / out 21951 / cache-create 90054 / cache-read 1775813  (232s, 34 turn(s))
- **date:** 2026-09-28 06:54:12
- **outcome:** ANSWERED (234s)
- **verdict-card:** VERDICT-CARD retrospective-cycle115 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle115.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle115, role retrospective) ---
CLAIM: Cycle 115 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 115 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-28 04:25:44  ..  2026-09-28 06:50:14   (145 min)
    basis: start = archive/peer/2026-09-28-retrospective-cycle114.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-28 04:35): `tools/bench/opmodels/<op>.json` are replayed through stagesim's rule. The pre-run FAILS on any sample whose measured wire outcome (new/lost uids, sinks kept) stagesim does not reproduce. Acceptance: PASS on `connect_from_wire.json` with the current stagesim, FAIL with `cfw_border_rule` disabled. Built first in cycle 115's card (`docs/d1-loop12-17-split-plan.md` PD229(a)).

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

== cycle audit, 2026-09-28 04:25 .. 2026-09-28 06:50 (145 min, an explicit cycle window): 81 build logs, 11 peer logs, 19 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 40/81 ok; NO BGRUN line in ['diag_c115a_replay.log', 'selftest_control_path_lint_c115a.log', 'selftest_control_path_lint_c115c_after.log', 'selftest_control_path_lint_c115c_before.log', 'selftest_stagesim_c115a.log', 'selftest_stagesim_k79_c115a.log', 'selftest_stagesim_l2a1_80_c115a.log', 'selftest_stagesim_pin_c115a.log', 'selftest_stagesim_unflip_81_c115a.log', 'selftest_stagesim_unflip_81_neg_c115a.log', 'selftest_stage_prerun_c103_c115a.log', 'selftest_stage_prerun_c103_c115c_after.log', 'selftest_stage_prerun_c103_c115c_before.log', 'selftest_stage_prerun_c106c_c115a.log', 'selftest_stage_prerun_c106c_c115c_after.log', 'selftest_stage_prerun_c106c_c115c_before.log', 'selftest_stage_prerun_c106e_c115a.log', 'selftest_stage_prerun_c106e_c115c_after.log', 'selftest_stage_prerun_c106e_c115c_before.log', 'selftest_stage_prerun_c110g_c115a.log', 'selftest_stage_prerun_c110g_c115c_after.log', 'selftest_stage_prerun_c110g_c115c_before.log', 'selftest_stage_prerun_c114d_c115a.log', 'selftest_stage_prerun_c114d_c115c_after.log', 'selftest_stage_prerun_c114d_c115c_before.log', 'selftest_stage_prerun_c114_c115a.log', 'selftest_stage_prerun_c114_c115c_after.log', 'selftest_stage_prerun_c114_c115c_before.log', 'selftest_stage_prerun_c115a_c115a.log', 'selftest_stage_prerun_c115a_c115c_after.log', 'selftest_stage_prerun_c115a_c115c_before.log', 'selftest_stage_prerun_c115c_c115c_after.log', 'selftest_stage_prerun_graphload_c115a.log', 'selftest_stage_prerun_graphload_c115c_after.log', 'selftest_stage_prerun_graphload_c115c_before.log', 'selftest_stage_prerun_headcmp_79-6_c115a.log', 'selftest_stage_prerun_headcmp_79-6_c115c_after.log', 'selftest_stage_prerun_headcmp_79-6_c115c_before.log', 'selftest_stage_prerun_stageplan_c115a.log', 'selftest_stage_prerun_stageplan_c115c_after.log', 'selftest_stage_prerun_stageplan_c115c_before.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 13 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 19/19 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 5961 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  PASS  A8 recipe/bench runs ended with a RESULT line (C6): every scoped run in the window printed one (or predates the mark)

  C1 builds run 49, failure markers 93, logs carrying a failure 13
  C2 peer reviews dispatched 11, archived 19
  C3 wall-clock inside bgrun, BUILDS ONLY 79 min 2 s
  C4 wall-clock inside bgrun, REVIEWS 11 min 10 s; cost $6.9183 from 5 log(s) that report one
  C4b cost lines seen 5 / parsed 5
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 90 min 12 s  (builds 87%, reviews 12%, judgement session 0%)

  C6 material-marked recipe/bench runs 18, judgement-session attempts refused 9  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 269 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/cards/peer_task_c115c_errorlist.txt, tools/bench/cards/peer_task_c115c_headcmp.txt, tools/bench/cards/peer_task_c115e_sel.txt, tools/bench/cards/plan_115-2_l2r1.md, tools/bench/diag_c115a_dispositions.py, tools/bench/diag_c115a_regress.py, tools/bench/diag_c115b_errorlist.py, tools/bench/diag_c115b_graph.py, tools/bench/diag_c115b_inv.py, tools/bench/diag_c115b_md5.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/873 ok; 532 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2562 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:466 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 644 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun


=== BUILD LOGS INSIDE THE WINDOW (82; read them directly, they are the primary record) ===
tools/bench/diag_c115a_dispositions.log  (2026-09-28 04:38:07)
tools/bench/diag_c115a_regress.log  (2026-09-28 04:44:19)
tools/bench/diag_c115a_replay.log  (2026-09-28 04:44:19)
tools/bench/diag_c115a_x13_all.log  (2026-09-28 04:45:03)
tools/bench/diag_c115a_x13_cfw.log  (2026-09-28 04:35:23)
tools/bench/diag_c115a_x13_cfw_disabled.log  (2026-09-28 04:35:24)
tools/bench/diag_c115b_errorlist.log  (2026-09-28 06:17:17)
tools/bench/diag_c115b_graph.log  (2026-09-28 04:51:28)
tools/bench/diag_c115b_inv.log  (2026-09-28 04:48:30)
tools/bench/diag_c115b_md5.log  (2026-09-28 05:16:28)
tools/bench/diag_c115b_r1.log  (2026-09-28 05:12:31)
tools/bench/diag_c115b_raw.log  (2026-09-28 04:49:20)
tools/bench/diag_c115b_scratch.log  (2026-09-28 05:10:28)
tools/bench/diag_c115b_scratch_dry.log  (2026-09-28 05:02:19)
tools/bench/diag_c115b_scratch_dry_c115c.log  (2026-09-28 05:28:31)
tools/bench/diag_c115b_scratch_prerun.log  (2026-09-28 05:02:29)
tools/bench/diag_c115b_scratch_prerun_c115c.log  (2026-09-28 05:28:46)
tools/bench/diag_c115b_scratch_v2.log  (2026-09-28 05:54:16)
tools/bench/diag_c115b_x13_all.log  (2026-09-28 04:54:04)
tools/bench/diag_c115b_x13_del.log  (2026-09-28 04:53:51)
tools/bench/diag_c115b_x13_del_neg.log  (2026-09-28 04:53:59)
tools/bench/diag_c115c_headcmp_disc.log  (2026-09-28 05:38:40)
tools/bench/diag_c115c_regress_after.log  (2026-09-28 05:33:34)
tools/bench/diag_c115c_regress_before.log  (2026-09-28 05:25:42)
tools/bench/diag_c115d_graph.log  (2026-09-28 06:28:54)
tools/bench/diag_c115d_m1.log  (2026-09-28 06:25:18)
tools/bench/diag_c115d_sel.log  (2026-09-28 06:38:03)
tools/bench/diag_c115e_reverdict.log  (2026-09-28 06:48:11)
tools/bench/jev_gate.log  (2026-09-28 06:50:10)
tools/bench/motor_session_end_cycle114.log  (2026-09-28 04:28:13)
tools/bench/motor_session_start_cycle115.log  (2026-09-28 04:28:20)
tools/bench/plan_l2r1_sim.log  (2026-09-28 05:11:34)
tools/bench/selftest_control_path_lint_c115a.log  (2026-09-28 04:37:55)
tools/bench/selftest_control_path_lint_c115c_after.log  (2026-09-28 05:27:40)
tools/bench/selftest_control_path_lint_c115c_before.log  (2026-09-28 05:20:03)
tools/bench/selftest_stage_prerun_c103_c115a.log  (2026-09-28 04:40:21)
tools/bench/selftest_stage_prerun_c103_c115c_after.log  (2026-09-28 05:30:08)
tools/bench/selftest_stage_prerun_c103_c115c_before.log  (2026-09-28 05:22:27)
tools/bench/selftest_stage_prerun_c106c_c115a.log  (2026-09-28 04:42:39)
tools/bench/selftest_stage_prerun_c106c_c115c_after.log  (2026-09-28 05:32:26)
tools/bench/selftest_stage_prerun_c106c_c115c_before.log  (2026-09-28 05:24:45)
tools/bench/selftest_stage_prerun_c106e_c115a.log  (2026-09-28 04:43:11)
tools/bench/selftest_stage_prerun_c106e_c115c_after.log  (2026-09-28 05:32:58)
tools/bench/selftest_stage_prerun_c106e_c115c_before.log  (2026-09-28 05:25:19)
tools/bench/selftest_stage_prerun_c110g_c115a.log  (2026-09-28 04:43:11)
tools/bench/selftest_stage_prerun_c110g_c115c_after.log  (2026-09-28 05:32:58)
tools/bench/selftest_stage_prerun_c110g_c115c_before.log  (2026-09-28 05:25:19)
tools/bench/selftest_stage_prerun_c114_c115a.log  (2026-09-28 04:43:29)
tools/bench/selftest_stage_prerun_c114_c115c_after.log  (2026-09-28 05:33:17)
tools/bench/selftest_stage_prerun_c114_c115c_before.log  (2026-09-28 05:25:37)
tools/bench/selftest_stage_prerun_c114d_c115a.log  (2026-09-28 04:43:30)
tools/bench/selftest_stage_prerun_c114d_c115c_after.log  (2026-09-28 05:33:18)
tools/bench/selftest_stage_prerun_c114d_c115c_before.log  (2026-09-28 05:25:39)
tools/bench/selftest_stage_prerun_c115a.log  (2026-09-28 04:37:00)
tools/bench/selftest_stage_prerun_c115a_c115a.log  (2026-09-28 04:43:33)
tools/bench/selftest_stage_prerun_c115a_c115b.log  (2026-09-28 05:16:06)
tools/bench/selftest_stage_prerun_c115a_c115c_after.log  (2026-09-28 05:33:21)
tools/bench/selftest_stage_prerun_c115a_c115c_before.log  (2026-09-28 05:25:42)
tools/bench/selftest_stage_prerun_c115c.log  (2026-09-28 05:27:33)
tools/bench/selftest_stage_prerun_c115c_c115c_after.log  (2026-09-28 05:33:34)
tools/bench/selftest_stage_prerun_graphload_c115a.log  (2026-09-28 04:43:12)
tools/bench/selftest_stage_prerun_graphload_c115c_after.log  (2026-09-28 05:32:59)
tools/bench/selftest_stage_prerun_graphload_c115c_before.log  (2026-09-28 05:25:19)
tools/bench/selftest_stage_prerun_headcmp_79-6_c115a.log  (2026-09-28 04:43:17)
tools/bench/selftest_stage_prerun_headcmp_79-6_c115c_after.log  (2026-09-28 05:33:04)
tools/bench/selftest_stage_prerun_headcmp_79-6_c115c_before.log  (2026-09-28 05:25:24)
tools/bench/selftest_stage_prerun_headcmp_79-6_c115c_rerun.log  (2026-09-28 05:38:59)
tools/bench/selftest_stage_prerun_stageplan_c115a.log  (2026-09-28 04:38:13)
tools/bench/selftest_stage_prerun_stageplan_c115c_after.log  (2026-09-28 05:27:58)
tools/bench/selftest_stage_prerun_stageplan_c115c_before.log  (2026-09-28 05:20:20)
tools/bench/selftest_stagesim_c115a.log  (2026-09-28 04:37:36)
tools/bench/selftest_stagesim_k79_c115a.log  (2026-09-28 04:37:37)
tools/bench/selftest_stagesim_l2a1_80_c115a.log  (2026-09-28 04:37:43)
tools/bench/selftest_stagesim_pin.log  (2026-09-28 04:36:56)
tools/bench/selftest_stagesim_pin_c115a.log  (2026-09-28 04:37:55)
tools/bench/selftest_stagesim_unflip_81_c115a.log  (2026-09-28 04:37:55)
tools/bench/selftest_stagesim_unflip_81_neg_c115a.log  (2026-09-28 04:43:44)
tools/bench/stage_d1_l2r1.log  (2026-09-28 06:05:37)
tools/bench/stage_d1_l2r1_dry.log  (2026-09-28 05:15:06)
tools/bench/stage_d1_l2r1_dry_c115c.log  (2026-09-28 05:27:55)
tools/bench/stage_d1_l2r1_prerun.log  (2026-09-28 05:15:20)
tools/bench/stage_d1_l2r1_prerun_c115c.log  (2026-09-28 05:28:10)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (11) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_114.log  (2026-09-28 04:28:00)
tools/bench/cycle_115.log  (2026-09-28 04:28:21)
tools/bench/cycle_runner.log  (2026-09-28 04:28:21)
tools/bench/cycle_runner_main_20260928a.log  (2026-09-28 04:28:21)
tools/bench/peer_c115c_errorlist.log  (2026-09-28 06:20:54)
tools/bench/peer_c115c_headcmp.log  (2026-09-28 05:37:33)
tools/bench/peer_c115e_sel.log  (2026-09-28 06:46:08)
tools/bench/peer_priorart_c115b_l2r1.log  (2026-09-28 05:03:36)
tools/bench/peer_priorart_c115b_l2r1_v2.log  (2026-09-28 05:13:10)
tools/bench/peer_priorart_c115b_l2r1_v3.log  (2026-09-28 05:14:29)
tools/bench/retro.log  (2026-09-28 06:50:14)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle115","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 115 (04:25:44 – 06:50:14)

**Outcome.** The cycle produced what it was for, and I found no costly structural fault. It built the X13 opmodel-conformance device first, as PD229(a) ordered (`tools/bench/cards/result_115-1.json:19-22`). It made exactly one stage launch, which passed 35/0 and saved bed `D1_l2_r1_20260928_055441.vi` (`result_115-3.json:18`). It resolved one failed Error-List prediction through two peer reviews and ended with an expected file whose reverdict came back OK (`result_115-5.json:19`). It then handed the next cycle a `next.json` that adopts the review's hardening: loose ends pinned at exactly 24, a whole-graph terminal diff and no carried licence (`tools/bench/next.json:4,15`).

Costs:
- 5 material cards, under the 6-dispatch cap.
- Review cost $6.92 across 5 cost lines, all 5 parsed (audit C4/C4b).
- Build wall-clock 79 min (audit C3).

The contract's device rule (threshold 1) still requires one line at the end, for the device that fired wrongly. That line costs 2 minutes; it is not a costly fault.

## Findings

**1. Repeated failure.** There was no repeated class. Four gate failures had four different causes:
- **Our own recipe bug:** the first prerun at 05:00 failed X5 and X6 because the recipe named two plan files (`stage_d1_l2r1_prerun.log:75,83-84`). It was fixed in 53 s and passed at `:175`.
- **X5 false positive:** X5 counted `delete_wire` as a wiring op (`stage_d1_l2r1_prerun.log:288`).
- **Flaky selftest sandbox:** the headcmp selftest failed on a stale, PID-named `%TEMP%` sandbox. This is its only FAIL on record (`selftest_stage_prerun_headcmp_79-6_c115c_after.log:6`).
- **Error List F7:** one extra loose-ends item (`diag_c115b_errorlist.log:121`).

No attempt should have changed approach sooner than it did.

**2. Missing tool.** Two readers were missing:
- **Selection List / item→wire reader:** there is no `TopLevelDiagram.Selection List[]` reader. Card 115-4 therefore tied Error List items to nets by screenshot masks, and 2 of 47 shots failed, which triggered a review (`result_115-4.json:22,27`). The last card also had to license the 7 new items with an *inferred* location (`archive/peer/2026-09-28-c115e-sel.md:153-156`).
- **Selftest sandbox cleanup:** `selftest_launch_gate` never deletes its PID-named sandboxes (86 were left over). This cost one hypothesis review, $1.2775 (`peer_c115c_headcmp.log:4,14`). The fix was left unapplied (`result_115-3.json:26`).

**3. Unmeasured steps.** This is the most expensive item of the cycle, but I rank it as a finding, not a fault:
- Prior-art Q2 asked whether deleting a register leaves loose ends on a branched net. Its disposition said this would be "measured instead by the R2 scratch run and by the R7 full Error List read" (`archive/peer/2026-09-28-priorart-c115b-l2r1.md:609-610`).
- Neither scratch log reads the Error List (grep over `diag_c115b_scratch*.log` finds no Error List read).
- The first measurement was therefore after the launch, where F7 failed at 06:17. The detour ran from 06:17 to 06:48 (31 min, $1.3095 + $1.3604 of review).
- Q2 was answered from local records only ("nothing on record", `:585`). NI documents "Wire has loose ends" as its own error class, and documents a per-wire [Remove Loose Ends](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/wire/removelooseends.html) method ([error page](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/wire-has-loose-ends.html)).
- Why it is not a fault: measuring on the scratch copy would mostly have **moved** the rule-1a analysis (graph M2/M5, review) ahead of the launch, not removed it. I cannot build a counterfactual that ends the cycle much earlier.

**4. Rule compliance.**
- **Followed:**
  - Failed-prediction review: F7 at 06:17 went to review at 06:18 (`peer_c115c_errorlist.log:1`).
  - ONE launch, as the card's rule required.
  - Adversarial framing: "REFUTE PD230, never confirm" (`task_115-5.json:60`).
  - Gate refusal returned as BLOCKED, not bypassed (`result_115-2.json:3`).
- **Broken:** STATUS.md is 466 lines, against the rule-4 limit of 110 (doc-lint L3). This is standing debt, not new.
- **External search:** CLAUDE.md:628-636 requires one for any factual tool question. It was not run for Q2 (see finding 3).
- **Audit A1 is a false positive:** the 41 flagged logs are children of bgrun-wrapped regression runners, for example `diag_c115a_regress.log:1-3`.
- **Audit C7 has no discrimination:** 269 "out-of-plan" files, including this cycle's own cards. It cannot show scope creep; I judged scope from the task cards myself.
- **What the audit does not cover:** read-only hook refusals (`material_marker.log`), and whether a disposition's promised measurement was ever made (finding 3).

**5. Ordering.** Defensible:
- The device was built first.
- The prior-art review ran before the launch, and was re-reviewed on the changed bytes (recipe md5 1d3fce95 equals the rev3 attachment, `result_115-3.json:16`).
- The scratch copy was re-run on the v2 bytes before the one launch.

The one step that belonged earlier is the Error List read on the scratch copy (finding 3).

**6. What was not reported.**
- `result_115-2.json` omits the first X5/X6 prerun failure at 05:00 (`stage_d1_l2r1_prerun.log:91`).
- It gives the killed rev2 prior-art dispatch as "stopped because recipe was 123 lines" (`:22`). It omits that two read-only line-count commands were refused just before (`material_marker.log:2614-2615`), which is why rev2 was launched on a 123-line recipe.

**7. Judgement inside a material session.**
- **Plan v1→v2 change by `material` (borderline, acceptable):** the material agent added 11 `delete_wire` rows (`plan_115-2_l2r1.md:8-16`). The card's own R2 spelled out "both halves, their wires" (`task_115-2.json:41`), so this implements the card rather than redesigns it.
- **Card 115-5's V3 gate:** V3 is pre-scripted as "counter-case → BLOCKED" (`task_115-5.json:29`). It is a gate, and the material session returned every design finding (Q2 swap, Q3 b–d, PD230(d)) as open (`c115e-sel.md:153-167`).
- **Clean:** acceptance of R1 was decided by the judgement session (PD230, `task_115-5.json:6`).

**Other structural observations:**
- Card 115-4 was written with `peers=[]` for a diagnosis of a failed prediction. It was therefore bound to block on any new failed prediction, and it did (`result_115-4.json:3`). That cost one extra card boundary, about 5 min.
- The X5 block cost about 23 min (05:16 → 05:39) and was resolved correctly: a narrow fix, selftests before and after.

## Device effect

Every device that had occasion to fire in this window worked, except one:
- **bgrun inner-FAIL → rc:** worked (`diag_c115b_errorlist.log:127`).
- **Cost-line parsing:** worked (C4b 5/5).
- **Prior-art before build / stop record by sha:** worked; rev3 ran on the changed bytes (`peer_priorart_c115b_l2r1_v3.log:1`).
- **bgrun reap:** worked (`peer_priorart_c115b_l2r1_v2.log:5`).
- **guard_peer failed-prediction lock:** held and refused `diag_c115d_sel2.py` (`result_115-4.json:3`).
- **`gates_due` in the cycle card:** present (`cycle_115.json:28-44`).
- **X13 (PD229(a)):** its fail case was shown (`result_115-1.json:20`), and sim and real lost sets matched (`result_115-3.json:19`).
- **Failed:** the stop record's read-only exemption. It was decided 2026-09-24 05:54 and re-repaired 2026-09-27 (01:15, 22:20). `violation-decisions.md:1488-1489` says any further read-only refusal means the repair failed. At 05:13:02 it refused the purely read-only `wc -l tools/recipes/stage_d1_l2r1.py; awk 'length > 250' … | wc -l` as STOPPED-RECIPE (`tools/hooks/material_marker.log:2615`; also `:2614`). The likely gap is the `;` segment separator.
  - **Loss:** rev2 was launched blind at 05:12:27 on a 123-line recipe and was killed after 43 s with no cost line. About 2 min.
  - **Counterfactual:** had `wc -l` passed at 05:12:12, the recipe would have been trimmed first, and only one re-review launched (at about 05:12:30 rather than 05:13:09). That saves about 1–2 min and one killed dispatch.

VIOLATION: device-failed | loss_min=2 | loss_usd=? | evidence=tools/hooks/material_marker.log:2615
VERDICT {"schema":"verdict/1","id":"retrospective-cycle115","verdict":"refuted","alternative":"No costly structural fault: the cycle delivered bed D1_l2_r1 + reverdicted expected file; the device-rule line is emitted only because stop_record's read-only exemption refused `wc -l …; awk …` (2 min), and the 31-min F7 detour moved rather than wasted work.","discriminating_test":"Replay the literal argv at material_marker.log:2615 through stop_record/launchunit offline: if it is still refused, the read-only exemption misses `;`-separated segments.","violations":[{"slug":"device-failed","loss_min":2,"loss_usd":"?","evidence":"tools/hooks/material_marker.log:2615"}],"sources":["tools/hooks/material_marker.log:2615","docs/violation-decisions.md:1488","tools/bench/cards/result_115-2.json:22","archive/peer/2026-09-28-priorart-c115b-l2r1.md:609","tools/bench/diag_c115b_errorlist.log:121","tools/bench/cards/result_115-5.json:19","https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/wire-has-loose-ends.html"],"note":"Largest cost was the F7 detour 06:17-06:48 ($2.67): the prior-art Q2 disposition promised a scratch Error List read that was never made; a finding, not a fault. 115-4 peers=[] cost one card boundary."}

## Sources

(extract from answer)

## What was done with it

- `device-failed` (stop record's read-only exemption misses `;` segments, `material_marker.log:2615`): **ACCEPTED**, threshold 1.
  - Device decided in `docs/violation-decisions.md` 2026-09-28 07:05 (1).
  - It is built first in cycle 116's card: `docs/d1-loop12-17-split-plan.md` PD230(g).
- Finding 2 (missing tools):
  - The selftest sandbox cleanup is folded into cycle 116's STEP 0.
  - The Selection List reader is NOT built. PD230(d) rests rule 1a on the terminal-list diff, not on item location, so the reader would not change a decision.
- Finding 3 (a disposition promised a scratch Error List read that was never made): **accepted as a card rule**. L2-R2's scratch run reads the Error List and pins the loose-ends count BEFORE its launch (PD230(g)). The disposition-landed check (`violation-decisions.md` 07:05 (2)) is the device for accepted fixes that never land.
- Finding 4 (external search not run for Q2): noted. NI documents a per-wire `Remove Loose Ends`, and PD230(e) already names it for the QRT wiring stage.
- Finding 6 (not reported): the refused read-only commands are the device above.
- Finding 7 / 115-4 `peers=[]`: card rule from 116 on. A diagnosis card of a failed prediction carries `hypothesis` in `peers`.
