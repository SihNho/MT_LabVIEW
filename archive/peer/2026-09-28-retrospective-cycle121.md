# retrospective-cycle121

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $3.0181  in 34 / out 47395 / cache-create 200510 / cache-read 2329965  (487s, 35 turn(s))
- **date:** 2026-09-28 19:45:47
- **outcome:** ANSWERED (489s)
- **verdict-card:** VERDICT-CARD retrospective-cycle121 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle121.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle121, role retrospective) ---
CLAIM: Cycle 121 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 121 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-28 11:48:07  ..  2026-09-28 19:37:33   (469 min)
    basis: start = archive/peer/2026-09-28-retrospective-cycle117.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-28 07:05): - **(1)** The stop record splits a command on `;`, `&&`, `||` and `|` and refuses only a segment that EXECUTES the recipe. - Its self-test replays the literal commands at `material_marker.log:2614` and `:2615`, which must pass. - A real launch must still be refused, including one hidden after a `;`. - **(2)** The follow-on device of the 04:35 decision is now due. Card 115-1's C1 grep found two mor??
  - `rule-evaded` (decided 2026-09-28 10:37): - **(1) Record.** `tools/bench/op_hygiene/<op>.json`, schema `op-hygiene/1`: op, path, md5, calls, errors, error_codes, handles_before/after, log `file:line`, date. A NEW op VI is accepted only on ??2,000 consecutive calls (or a whole-graph sweep, whichever is larger) with 0 errors AND handles flat 짹100. The handle count alone is no longer the proof. - **(2) Refusal.** gscript's op-VI call path re??

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

== cycle audit, 2026-09-28 11:48 .. 2026-09-28 19:37 (469 min, an explicit cycle window): 161 build logs, 17 peer logs, 41 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 160/161 ok; NO BGRUN line in ['run_mode.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 26 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 41/41 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 7020 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 14 log(s) with a run that printed none: ['diag_c120_lint.log', 'p2run_selftest_guard_cycle_fixed.log', 'p2run_selftest_guard_session.log', 'p2run_selftest_protocol_wiring.log', 'p2run_selftest_stoprecord_bgrun.log', 'p2run_selftest_stoprecord_eqform.log']??
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 186, failure markers 30, logs carrying a failure 26
  C2 peer reviews dispatched 17, archived 41
  C3 wall-clock inside bgrun, BUILDS ONLY 206 min 3 s
  C4 wall-clock inside bgrun, REVIEWS 19 min 9 s; cost $11.4368 from 8 log(s) that report one
  C4b cost lines seen 8 / parsed 8
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 165 min 9 s; cost $69.0161 from 2 log(s) - cycle_118.log, cycle_119.log
  C5 total wall-clock 390 min 21 s  (builds 52%, reviews 4%, judgement session 42%)

  C6 material-marked recipe/bench runs 95, judgement-session attempts refused 18  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 877 - STATUS.md, docs/user-rules.md, tools/bench/.stall_samples.txt, tools/bench/build_op_termtype.py, tools/bench/cards/brief_120-1.md, tools/bench/cards/brief_120-2.md, tools/bench/cards/brief_120-3.md, tools/bench/cards/brief_120-5.md, tools/bench/cards/brief_chat-C0.md, tools/bench/cards/brief_chat-P2.md, tools/bench/cards/brief_chat-P3.md, tools/bench/cards/peer_task_c121_3_l4.md??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 344/898 ok; 554 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2649 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:577 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  WARN  L5 superseded documents are not still current: docs/ring-buffer-design.md supersedes docs/d1-build-plan.md, which is still `status: current`
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 666 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one

AUDIT VIOLATIONS: A1 every build log came from bgrun


=== BUILD LOGS INSIDE THE WINDOW (162; read them directly, they are the primary record) ===
tools/bench/build_op_termtype.log  (2026-09-28 15:16:37)
tools/bench/c121_3_selftest_c111c_launchunit.log  (2026-09-28 18:46:04)
tools/bench/c121_3_selftest_stoprecord_offline_c107.log  (2026-09-28 18:46:02)
tools/bench/c121_3reg_selftest_chat_p3.log  (2026-09-28 18:49:43)
tools/bench/c121_3reg_selftest_cycle_runner.log  (2026-09-28 18:50:11)
tools/bench/c121_3reg_selftest_launch_gate.log  (2026-09-28 18:49:49)
tools/bench/c121_3reg_selftest_protocol.log  (2026-09-28 18:49:51)
tools/bench/c121_5_selftest_c121_3_gatefp.log  (2026-09-28 18:57:55)
tools/bench/c121_5_selftest_launch_gate.log  (2026-09-28 18:57:59)
tools/bench/c121_5reg_c107.log  (2026-09-28 18:58:06)
tools/bench/c121_5reg_c110.log  (2026-09-28 18:58:11)
tools/bench/c121_5reg_c111c.log  (2026-09-28 18:58:08)
tools/bench/c121_5reg_chat_p1.log  (2026-09-28 18:58:14)
tools/bench/c121_5reg_chat_p3.log  (2026-09-28 18:58:10)
tools/bench/c121_5reg_cycle_runner.log  (2026-09-28 18:58:35)
tools/bench/c121_5reg_protocol.log  (2026-09-28 18:58:17)
tools/bench/diag_c118_compile.log  (2026-09-28 12:09:20)
tools/bench/diag_c118_p0.log  (2026-09-28 12:01:31)
tools/bench/diag_c118_p0b.log  (2026-09-28 12:03:46)
tools/bench/diag_c118_p1.log  (2026-09-28 12:30:35)
tools/bench/diag_c118_p1_prerun.log  (2026-09-28 12:29:56)
tools/bench/diag_c118_p1b.log  (2026-09-28 12:49:38)
tools/bench/diag_c118_p1b_prerun.log  (2026-09-28 12:46:58)
tools/bench/diag_c118_p1b_prerun2.log  (2026-09-28 12:47:32)
tools/bench/diag_c118_p1b_prerun3.log  (2026-09-28 12:47:49)
tools/bench/diag_c118_p1b_prerun4.log  (2026-09-28 12:48:27)
tools/bench/diag_c118_p1b_prerun5.log  (2026-09-28 12:48:53)
tools/bench/diag_c118_p1b_prerun6.log  (2026-09-28 12:55:58)
tools/bench/diag_c118_p1b_r2.log  (2026-09-28 12:58:50)
tools/bench/diag_c118_q.log  (2026-09-28 11:54:12)
tools/bench/diag_c118_q2.log  (2026-09-28 12:43:38)
tools/bench/diag_c118_r1_opbuild.log  (2026-09-28 13:14:01)
tools/bench/diag_c118_r1v.log  (2026-09-28 13:19:47)
tools/bench/diag_c119_c1.log  (2026-09-28 13:27:50)
tools/bench/diag_c119_p1b.log  (2026-09-28 13:33:41)
tools/bench/diag_c119_p1b_dry.log  (2026-09-28 13:30:38)
tools/bench/diag_c119_p1b_dry2.log  (2026-09-28 13:35:33)
tools/bench/diag_c119_p1b_prerun.log  (2026-09-28 13:30:52)
tools/bench/diag_c119_p1b_prerun2.log  (2026-09-28 13:35:35)
tools/bench/diag_c119_p1b_r2.log  (2026-09-28 13:38:51)
tools/bench/diag_c120_facts.log  (2026-09-28 14:50:33)
tools/bench/diag_c120_fs.log  (2026-09-28 15:41:05)
tools/bench/diag_c120_fs_dry.log  (2026-09-28 15:14:11)
tools/bench/diag_c120_fs_dry2.log  (2026-09-28 15:38:03)
tools/bench/diag_c120_fs_prerun.log  (2026-09-28 15:14:14)
tools/bench/diag_c120_fs_prerun2.log  (2026-09-28 15:38:06)
tools/bench/diag_c120_g.log  (2026-09-28 14:54:17)
tools/bench/diag_c120_ladder.log  (2026-09-28 14:51:20)
tools/bench/diag_c120_lint.log  (2026-09-28 15:12:27)
tools/bench/diag_c120_parsecheck.log  (2026-09-28 15:24:09)
tools/bench/diag_c120_s0_base.log  (2026-09-28 15:54:35)
tools/bench/diag_c120_s4_peek.log  (2026-09-28 15:52:56)
tools/bench/diag_c120_types.log  (2026-09-28 15:19:36)
tools/bench/diag_c120_types_dry.log  (2026-09-28 15:24:21)
tools/bench/diag_c120_types_prerun.log  (2026-09-28 15:24:23)
tools/bench/diag_c120_types_r2.log  (2026-09-28 15:27:13)
tools/bench/finish_orphan_120.log  (2026-09-28 15:55:13)
tools/bench/jev_gate.log  (2026-09-28 19:37:29)
tools/bench/motor_session_end_cycle117.log  (2026-09-28 11:49:01)
tools/bench/motor_session_end_cycle118.log  (2026-09-28 13:22:57)
tools/bench/motor_session_end_cycle119.log  (2026-09-28 14:34:40)
tools/bench/motor_session_end_cycle120.log  (2026-09-28 15:55:13)
tools/bench/motor_session_start_cycle118.log  (2026-09-28 11:49:09)
tools/bench/motor_session_start_cycle119.log  (2026-09-28 13:23:05)
tools/bench/motor_session_start_cycle120.log  (2026-09-28 14:34:47)
tools/bench/motor_session_start_cycle121.log  (2026-09-28 18:20:39)
tools/bench/p1_bufmode_121.log  (2026-09-28 18:30:55)
tools/bench/p2run_selftest_chat_p1.log  (2026-09-28 18:06:01)
tools/bench/p2run_selftest_cycle_runner_ff.log  (2026-09-28 18:08:46)
tools/bench/p2run_selftest_cycle_runner_ladder.log  (2026-09-28 18:07:05)
tools/bench/p2run_selftest_errorlist_check_header.log  (2026-09-28 18:08:47)
tools/bench/p2run_selftest_errorlist_retry.log  (2026-09-28 18:08:49)
tools/bench/p2run_selftest_errorlist_reuse_81.log  (2026-09-28 18:08:54)
tools/bench/p2run_selftest_guard_cycle_fixed.log  (2026-09-28 18:09:03)
tools/bench/p2run_selftest_guard_cycle_offline.log  (2026-09-28 18:09:09)
tools/bench/p2run_selftest_guard_session.log  (2026-09-28 18:05:12)
tools/bench/p2run_selftest_launch_gate.log  (2026-09-28 18:08:26)
tools/bench/p2run_selftest_protocol.log  (2026-09-28 18:06:14)
tools/bench/p2run_selftest_protocol_wiring.log  (2026-09-28 18:06:30)
tools/bench/p2run_selftest_requires.log  (2026-09-28 18:06:33)
tools/bench/p2run_selftest_retry_cap.log  (2026-09-28 18:08:38)
tools/bench/p2run_selftest_scratch_verify.log  (2026-09-28 18:07:11)
tools/bench/p2run_selftest_stoprecord_bgrun.log  (2026-09-28 18:10:29)
tools/bench/p2run_selftest_stoprecord_eqform.log  (2026-09-28 18:10:34)
tools/bench/p2run_selftest_stoprecord_supersession.log  (2026-09-28 18:10:38)
tools/bench/p3_diag_lvclass.log  (2026-09-28 18:28:27)
tools/bench/p3run_selftest_c103d_hooks.log  (2026-09-28 18:41:40)
tools/bench/p3run_selftest_c110_launchgate.log  (2026-09-28 18:41:38)
tools/bench/p3run_selftest_c111c_launchunit.log  (2026-09-28 18:41:40)
tools/bench/p3run_selftest_chat_p1.log  (2026-09-28 18:42:14)
tools/bench/p3run_selftest_chat_p2.log  (2026-09-28 18:42:19)
tools/bench/p3run_selftest_cycle_runner.log  (2026-09-28 18:42:03)
tools/bench/p3run_selftest_guard_cycle_offline.log  (2026-09-28 18:27:09)
tools/bench/p3run_selftest_guard_cycle_rerun.log  (2026-09-28 18:41:29)
tools/bench/p3run_selftest_prerun_diag.log  (2026-09-28 18:41:37)
tools/bench/p3run_selftest_protocol.log  (2026-09-28 18:42:08)
tools/bench/p3run_selftest_scratch_verify.log  (2026-09-28 18:42:20)
tools/bench/p3run_selftest_stage_prerun_c103.log  (2026-09-28 18:37:33)
tools/bench/p3run_selftest_stage_prerun_c106c.log  (2026-09-28 18:39:57)
tools/bench/p3run_selftest_stage_prerun_c106e.log  (2026-09-28 18:40:31)
tools/bench/p3run_selftest_stage_prerun_c114.log  (2026-09-28 18:40:47)
tools/bench/p3run_selftest_stage_prerun_c114d.log  (2026-09-28 18:40:50)
tools/bench/p3run_selftest_stage_prerun_c115a.log  (2026-09-28 18:40:54)
tools/bench/p3run_selftest_stage_prerun_c115c.log  (2026-09-28 18:41:09)
tools/bench/p3run_selftest_stage_prerun_graphload.log  (2026-09-28 18:35:20)
tools/bench/p3run_selftest_stage_prerun_headcmp_79-6.log  (2026-09-28 18:35:19)
tools/bench/p3run_selftest_stage_prerun_stageplan.log  (2026-09-28 18:35:17)
tools/bench/p3run_selftest_stoprecord_c116a.log  (2026-09-28 18:41:30)
tools/bench/p3run_selftest_stoprecord_offline_c107.log  (2026-09-28 18:41:31)
tools/bench/p3run_selftest_stoprecord_supersession.log  (2026-09-28 18:41:36)
tools/bench/p3run_selftest_stoprecord_table.log  (2026-09-28 18:41:33)
tools/bench/plan_qrt_pool_probe.log  (2026-09-28 13:35:10)
tools/bench/plan_qrt_pool_recipe_dry.log  (2026-09-28 13:41:34)
tools/bench/plan_qrt_pool_recipe_prerun.log  (2026-09-28 13:41:50)
tools/bench/plan_qrt_pool_recipe_prerun_119_4.log  (2026-09-28 13:48:23)
tools/bench/plan_qrt_pool_recipe_prerun_119_4b.log  (2026-09-28 13:50:15)
tools/bench/plan_qrt_pool_sim.log  (2026-09-28 13:40:55)
tools/bench/plan_qrt_pool_sim_119_4.log  (2026-09-28 13:47:56)
tools/bench/plan_qrt_pool_sim_119_4b.log  (2026-09-28 13:49:06)
tools/bench/plan_ring_p2a_make.log  (2026-09-28 18:37:47)
tools/bench/plan_ring_p2a_sim.log  (2026-09-28 18:38:06)
tools/bench/ring_p2a_md5.log  (2026-09-28 18:51:26)
tools/bench/run_mode.log  (2026-09-28 19:22:06)
tools/bench/selftest_c106d_tools_c118d.log  (2026-09-28 13:20:10)
tools/bench/selftest_c118_primnested.log  (2026-09-28 13:13:29)
tools/bench/selftest_c120_caseshape.log  (2026-09-28 15:02:44)
tools/bench/selftest_c120_caseshape2.log  (2026-09-28 15:11:48)
tools/bench/selftest_c120_routes.log  (2026-09-28 15:11:26)
tools/bench/selftest_c121_3_gatefp.log  (2026-09-28 18:49:23)
tools/bench/selftest_chat_p2.log  (2026-09-28 18:03:39)
tools/bench/selftest_chat_p3.log  (2026-09-28 18:33:41)
tools/bench/selftest_op_hygiene_c118d.log  (2026-09-28 13:20:02)
tools/bench/selftest_op_hygiene_c119a.log  (2026-09-28 13:30:42)
tools/bench/selftest_protocol_119_3.log  (2026-09-28 13:40:09)
tools/bench/selftest_protocol_119_4.log  (2026-09-28 13:47:40)
tools/bench/selftest_protocol_120_4.log  (2026-09-28 15:48:17)
tools/bench/selftest_protocol_wiring_119_3.log  (2026-09-28 13:40:18)
tools/bench/selftest_protocol_wiring_119_4.log  (2026-09-28 13:48:00)
tools/bench/selftest_protocol_wiring_120_4.log  (2026-09-28 15:48:22)
tools/bench/selftest_stagesim_c118.log  (2026-09-28 12:09:04)
tools/bench/selftest_stagesim_c118b.log  (2026-09-28 12:55:20)
tools/bench/selftest_stagesim_c118c.log  (2026-09-28 12:59:46)
tools/bench/selftest_stagesim_c118d.log  (2026-09-28 13:16:15)
tools/bench/selftest_stagesim_c120.log  (2026-09-28 15:11:34)
tools/bench/selftest_stagexec_c118.log  (2026-09-28 12:08:56)
tools/bench/selftest_stagexec_c118b.log  (2026-09-28 12:55:34)
tools/bench/selftest_stagexec_c118d.log  (2026-09-28 13:16:34)
tools/bench/selftest_stagexec_c120.log  (2026-09-28 15:08:57)
tools/bench/stage_d1_qrt_pool.log  (2026-09-28 14:18:30)
tools/bench/stage_d1_qrt_pool_el_final.log  (2026-09-28 14:30:06)
tools/bench/stage_d1_qrt_pool_el_scratch.log  (2026-09-28 14:10:40)
tools/bench/stage_d1_qrt_pool_scratch.log  (2026-09-28 13:59:26)
tools/bench/stage_d1_qrt_pool_scratch_prerun.log  (2026-09-28 13:50:39)
tools/bench/stage_d1_ring_p2a.log  (2026-09-28 19:24:05)
tools/bench/stage_d1_ring_p2a_dry.log  (2026-09-28 18:39:42)
tools/bench/stage_d1_ring_p2a_el_final.log  (2026-09-28 19:35:47)
tools/bench/stage_d1_ring_p2a_el_scratch.log  (2026-09-28 19:17:18)
tools/bench/stage_d1_ring_p2a_prerun.log  (2026-09-28 18:40:09)
tools/bench/stage_d1_ring_p2a_scratch_nosave.log  (2026-09-28 18:50:39)
tools/bench/stage_d1_ring_p2a_scratch_pin.log  (2026-09-28 18:59:55)
tools/bench/stage_d1_ring_p2a_scratch_prerun.log  (2026-09-28 18:41:17)
tools/bench/wait_runner_event.log  (2026-09-28 12:50:52)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (17) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_117.log  (2026-09-28 11:48:55)
tools/bench/cycle_118.log  (2026-09-28 13:22:51)
tools/bench/cycle_119.log  (2026-09-28 14:34:34)
tools/bench/cycle_120.log  (2026-09-28 15:55:07)
tools/bench/cycle_121.log  (2026-09-28 18:20:41)
tools/bench/cycle_runner.log  (2026-09-28 18:20:40)
tools/bench/cycle_runner_main_20260928_1033.log  (2026-09-28 15:55:13)
tools/bench/cycle_runner_main_20260928_1820.log  (2026-09-28 18:20:40)
tools/bench/peer_c118p0.log  (2026-09-28 12:08:13)
tools/bench/peer_c118p1.log  (2026-09-28 12:34:24)
tools/bench/peer_c118p1b.log  (2026-09-28 12:53:45)
tools/bench/peer_c120_fs.log  (2026-09-28 15:43:56)
tools/bench/peer_c120_types.log  (2026-09-28 15:23:48)
tools/bench/peer_c121_3_launch_gate_l4.log  (2026-09-28 18:54:09)
tools/bench/peer_p2-offline-fixture.log  (2026-09-28 18:19:52)
tools/bench/priorart_c119_qrt_pool.log  (2026-09-28 13:43:59)
tools/bench/retro.log  (2026-09-28 19:37:32)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle121","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 121: outcome review over the window 11:48–19:37

**Summary.** The window ends with one real deliverable: `D1_ring_p2a_20260928_191739.vi` (md5 `c22a473f`), accepted as the bed (`tools/bench/cards/result_121-4.json:10`). Measured against the goal, that is thin for 469 minutes.
- **What survives.** P2a's output is R2 plus 20 image buffers and their names constant. Around it survive:
  - a constant-value reader (118-4);
  - a terminal-type reader and the FS-crossing route facts (120);
  - the camera buffer-mode measurement (121-1);
  - tooling.
- **What was thrown away.** The queue half of the pool (cycles 118–119), most of cycle 120, and all of P2a, which only undid it. I rank that loss as the biggest in the window, but I do not count it as a structural fault of these cycles (reason below). The one structural fault I name is smaller: cycle 118 spent two attempts, on two escalation rungs, rediscovering a reader limitation that `docs/NAMES.md` had recorded since 2026-09-15.

**The window does not match "cycle 121".** It covers runner cycles 118, 119 and 120, a 145-minute stop, and then cycle 121:
- cycles 118–120: `cycle_runner_main_20260928_1033.log:22-62`;
- the runner was stopped for the user's redirect from 15:55 to 18:20 (`STATUS.md:8`, `cycle_runner_main_20260928_1820.log:1`);
- cycle 121 itself ran from 18:20:41 (`cycle_121.log:1`).

Cycles 118–120 had no retrospective of their own because it was not due (`cycle_runner_main_20260928_1033.log:27,42`), so their cost lands here.

The audit also understates the window's cost:
- **C4c** lists $69.0161 from two logs only: cycle 118 at $42.2459 (`cycle_118.log:170`) and cycle 119 at $26.7702 (`cycle_119.log:170`).
- **Cycle 120** was killed from outside with no cost line (`cycle_120.log:170`, `cycle_runner_main_20260928_1033.log:62` "$?").
- **Cycle 121's** judgement session was still open when the window closed.

## The structural fault: cycle 118 rediscovered a recorded tool limit on two attempts

- **Attempt 118-1.** It failed partly on an IMAQ path inside an LLB, which `NAMES.md:954-956` already records (`result_118-1`, restated at `result_118-2.json:14`).
- **Attempt 118-2 (escalation rung 1, Opus max).** It ran gate A1b with the base-class `Constant.Value` reader. That reader returns void for every non-String constant, as `NAMES.md:1164-1165` has recorded since 2026-09-15.
  - The run failed in 20 s (`result_118-2.json:2,16`).
  - The review said so outright: *"The general rule was already in NAMES.md, and it makes the A1b result a foregone conclusion"* (`archive/peer/2026-09-28-c118p1-names.md:63`).
- **Judgement's response.** PD234(i) chose to run the donor VI instead of building a reader, and escalated to rung 2 (`docs/d1-loop12-17-split-plan.md:2189`).
- **Attempt 118-3 (Fable low).** It failed on the same missing capability: a Constant is not a Node, so no indicator route reaches it. It also hit the one-node rule on the ArrayConstant copy (`result_118-3.json:2,22,24`).
  - The ladder was now spent, so a user question, D-2026-09-28-02, was raised (`decisions_pending.json:251-265`).
- **What finally worked.** Only then did PD234(j) order the reader (`split-plan.md:2198`). Card 118-4 built it and passed in about 20 minutes (13:00→13:20: `selftest_c118_primnested.log` 13:13 … `diag_c118_r1v.log` 13:19).

**Counterfactual.** When the review landed at 12:34 (`peer_c118p1.log`), the next card could have been the reader instead of rung 2's donor track (12:36–12:58: `diag_c118_q2.log` 12:43 … `diag_c118_p1b_r2.log` 12:58).
- The reader would then have existed by about 12:56, and the ArrayConstant gap would have surfaced on the first re-run.
- P1 would have passed at about 13:15, inside cycle 118, instead of at 13:38 in cycle 119 (`diag_c119_p1b_r2.log`).
- One Fable rung and the D-02 user question would not have been spent.

**Loss.** About 25 minutes of wall-clock by my counterfactual. The chat's own measure is larger: "cycle 118: 84 min on one function" (`cycle_121.log:117`). No log carries a per-card dollar figure; cycle 118 as a whole cost $42.25.

**What is already fixed and what is not.** The escalation half is already covered by the device built in chat-P2 item 4, which refuses an escalation when the same function fails twice. The first-attempt half is not covered:
- a VI-modifying diagnostic is outside prior-art;
- `protocol.py requires` checks that an op exists, not what it can read.

## FINDINGS

### 1. Repeated failure
- **Cycle 118.** The same class of failure recurred three times: a VI-modifying diagnostic written against tool behaviour that was already recorded. That is 118-1 (LLB path), 118-2 (void reader) and 118-3 (Constant is not a Node). The approach should have changed after attempt 2 (118-2), as described above.
- **Gate misfires that repeated a queued defect:**
  - **fp-6 (15:37:54).** Decision 4 again read an appended prerun FAIL segment as a failed stage run. That is the same defect as fp-1 from cycle 117 (`gate_fp_queue.jsonl:1,6`).
  - **The read-only md5sum refusal (fp-4's class).** It happened again at 18:24:38, before 121-3's fix (`tools/hooks/material_marker.log:2779`), and was not logged as a new gate false positive.
  - **The one-way RULE-OFFLINE-CARD hold.** It recurred as fp-10 (`gate_fp_queue.jsonl:10`); it had been a carry since retrospective-cycle117 (`:424`).
  - Each of these cost seconds, not minutes.

### 2. Missing tool
- **A reader for non-String constant values.** Its absence answered both 118-2's A1b failure and 118-3's value check. It was built only as the third card (`split-plan.md:2201-2204`).
- **A capability check.** `requires` should check whether an op can read the terminal class in question, not just whether the op exists. A NAMES.md lookup for VI-modifying diagnostics would do the same job.
- **A handle-band reference.** 119-4's only FAIL was a "handles ±100" gate that judgement wrote without the recorded build-step band. Card 119-5 then had to measure +176…+684 after the fact (`split-plan.md:2218`).

### 3. Unmeasured steps
- **PD234(i)** chose "run the donor" by inference. 118-3 measured that no indicator route reaches a Constant (`result_118-3.json:22`).
- **PD236(b)'s ±100 handle gate** was inferred from the per-op hygiene number when build-step records existed. That cost a FAIL plus the read-only card 119-5.
- Both measurements were cheap and were available beforehand.

### 4. Rule compliance
**Broken or satisfied only formally:**
- **CLAUDE.md rule 4.** STATUS.md grew from 513 lines at the start of cycle 117 to 577 now (audit L3). The rule was broken, and more so over the window.
- **Superseded-document rule (audit L5).** `docs/ring-buffer-design.md` supersedes `d1-build-plan.md`, which is still marked current.
- **C6 RESULT-line rule (audit A8).** 14 logs have no RESULT line. chat-P3 admits three of them (`result_chat-P3.json:16`).
- **A1 FAIL.** This is an audit false positive: `run_mode.log` is a mode ledger, not a build log.
- **A9.** 21 of 22 accepted-but-unbuilt dispositions are still uncited by code. It keeps growing.
- **"RUN MODE FIRST".** No mode read appears in `run_mode.log` between 18:20 and 18:51. That is not proven broken, because `get` may not log.

**What the audit does not cover:**
- deliverables that a later redirect supersedes (P2a scores as a clean delivery);
- a killed cycle's missing cost (C4c silently counts 2 logs);
- an offline card editing a gate that the live LabVIEW card is using (below);
- the 145-minute stop counted as cycle time;
- whether a card's self-reported `minutes` is plausible (finding 6).

### 5. Ordering
- **Cycle 118.** Wrong, as above: the reader should have come second, not fourth.
- **Cycle 121.** Defensible: offline tooling ran beside the P1 camera measurement, then P2a. The exception is that 121-3's time-filter patch to the launch gate was live in the working tree while 121-2 was launching (`result_121-3.json:22`). The user's parallelism rule of 19:3x now forbids this (`STATUS.md:63`).
- **121-2 BLOCKED.** It was blocked on judgement's own flag, `gui: false` (`result_121-2.json:2`). The no-save scratch run it did (18:41–18:50) was then repeated as 121-4's pin scratch (386 s, `result_121-4.json:8`). That cost about 10 minutes and the cycle's end moved by about that much. It is minor.

### 6. What the summaries hide or understate
- **The window's net product.** STATUS calls cycle 119 "POOL STAGE DELIVERED" and cycle 121 "P2a DELIVERED". Together, half of the first was undone by the second (`split-plan.md:2254`). Work that was not worth doing:
  - the queue route of 118-3 (`result_118-3.json:18-19`);
  - the two BLOCKED schema cards of 119 and the Obtain/Enqueue half of 119-4;
  - most of cycle 120's 80 minutes: the design of seven more queues (PD237(a)) and the Dequeue/Case routes (120-3);
  - all of P2a (21 + 55 card-minutes, `result_121-2.json:26`, `result_121-4.json:18`).

  That is on the order of 150–190 minutes. Cycle 120's dollars are unknown.
- **Why I do not count the pool reversal as a fault of these cycles.** `docs/decisions.md:22,24` recorded the Q_free pool with "no free slot ⇒ do not read" as the decided frame handoff. When the chat raised the conflict with `:25` at 11:55, it recommended that "the build of the pool itself can proceed" (`decisions_pending.json:242`). The user's final design, U13 at 16:3x, is a new rule, not an old one the cycles evaded (`docs/user-rules.md:38`). The upstream cause is PD233(k) in cycle 117, outside the window, together with that internal conflict in `decisions.md`.
- **Implausible card minutes.** Card 118-2 reports `minutes: 112` and 118-3 `66` (`result_118-2.json:28`, `result_118-3.json:32`). Cycle 118 lasted 94 minutes in total, and the logs show the cards ran one after another. These figures cannot be used as cost.

### 7. Judgement inside a material session
- **The launch-gate time filter.** 121-3, a material card, chose it: a widening of a safety gate (`result_121-3.json:13`). Judgement rejected it (`split-plan.md:2264`) and 121-5 reverted it. It was caught, and it ran in the parallel slot, so it did not move the end.
- **Otherwise clean.** 121-2 and 121-4 returned their acceptance questions (the fifth object gone, the new bed) to judgement (`result_121-2.json:24-25`, `result_121-4.json:17`), which is correct.

## DEVICE EFFECT

- **Worked:**
  - the bgrun FAIL scan, which forced rc=1 (`result_118-2.json:16`);
  - cost parsing, 8 of 8 lines (C4b);
  - A4 disposition, 41 of 41 annotated;
  - the adversarial review: the c121-3 reviewer disagreed with the claim (`peer_c121_3_launch_gate_l4.log:6-20`);
  - guard_cycle's prior-art timing: the review ended at 13:43:59 and the launches came after 13:50;
  - bgrun_reap on the killed runner (`cycle_runner_main_20260928_1033.log:58`);
  - `gates_due`, which carried the gate-fp queue as DUE and led to it being drained (`cycle_runner_main_20260928_1820.log:6`);
  - op-hygiene: new ops came with 2,000-call records (`split-plan.md:2202`).
- **Misfired, then queued and drained as designed:**
  - the launch gate's decision 4 (fp-6);
  - guard_bash MATERIAL_RE (fp-4 and `:2779`);
  - guard_peer (fp-7, fp-10);
  - guard_card (fp-8).

  Each was routed around in seconds (fp-6 at 15:37:54, rerun at 15:38:06) and fixed at 18:42–18:59. None was bypassed routinely, and none let its own fault through.
- **C7 scope counter.** It lists 877 files against a plan that names none of the tools, so it cannot discriminate. No scope creep went through unseen, but as a measure it is dead.
- **Prior-art.** It returned `novel` on the pool recipe (`archive/peer/2026-09-28-priorart-c119-qrt-pool.md:1455`). That recipe only created the queues, and the user-rules question did not exist until chat-P2. This is a gap in its scope, not a failure.

**Verdict on devices:** no device failed at a cost inside the window, so I do not count a device failure.

VIOLATION: repeated-failure-class | loss_min=25 | loss_usd=? | evidence=archive/peer/2026-09-28-c118p1-names.md:63
VERDICT {"schema":"verdict/1","id":"retrospective-cycle121","verdict":"refuted","alternative":"The window's largest loss (~150-190 min: pool queues of 118-120 plus the P2a undo) is a user redirect on a design decisions.md:22,24 recorded and the chat cleared at 11:55 (decisions_pending.json:242), so it is a finding, not this window's fault.","discriminating_test":"Replay 118-2's A1b plan through a NAMES.md capability lookup: if OpConstValue_v1 is flagged void for ArrayConstant (NAMES.md:1164) before launch, the rung-2 attempt and D-2026-09-28-02 disappear; if not, the fault is the lookup's absence, not judgement.","violations":[{"slug":"repeated-failure-class","loss_min":25,"loss_usd":"?","evidence":"archive/peer/2026-09-28-c118p1-names.md:63"}],"sources":["tools/bench/cards/result_118-2.json:2","tools/bench/cards/result_118-3.json:22","docs/NAMES.md:1164","docs/d1-loop12-17-split-plan.md:2189","docs/d1-loop12-17-split-plan.md:2254","tools/bench/decisions_pending.json:242","tools/bench/cycle_118.log:170","tools/bench/cycle_120.log:170","tools/bench/cards/result_121-3.json:22","tools/bench/gate_fp_queue.jsonl:6"],"note":"Window spans cycles 118-121 plus a 145-min stop; C4c omits cycle 120 (killed, $?) and 121. Deliverable: D1_ring_p2a (c22a473f). Device misfires fp-4/6/10 were queued and drained as designed, seconds each; no costly device failure."}

## Sources

(extract from answer)

## What was done with it

Annotated by the cycle-121 judgement session, 2026-09-28 19:4x.
- **`repeated-failure-class` (25 min) — ACCEPTED, and the fault is judgement's (PD234(i), cycle 118).** The escalation half is already covered by chat-P2 item 4 (the escalation route refuses when the same function fails twice). The first-attempt half is NOT yet covered: before a card runs a VI-modifying diagnostic, nothing checks the op's recorded CAPABILITY in `docs/NAMES.md` (e.g. `:1164` void reader). Carry for the next tooling card, as a narrowing of `protocol.py requires`: an op/verb in `requires` may name the terminal/constant class it must handle, and `requires` reports a MISSING capability when NAMES.md records that class as unsupported. If `violations.py` shows the slug at its threshold, the next cycle builds this as its device first.
- **Finding 4 (STATUS.md 577 lines, rule 4):** accepted. The cycle-121 NEXT block is compact, but the history below it needs relocating to `archive/`. That is a doc card, and it comes after the deliverable step.
- **Finding 4 (audit L5, `d1-build-plan.md` still current although `ring-buffer-design.md` supersedes its §9):** accepted. `ring-buffer-design.md` supersedes §9 only, so `d1-build-plan.md` stays current and its §9 gets a SUPERSEDED marker in the same doc card.
- **Finding 5 (an offline card patched the launch gate while a LabVIEW card was launching):** accepted. The user's parallelism rule (STATUS NEXT, 19:3x) now forbids that pairing: the offline slot takes no gate/hook edits while a LabVIEW card is live.
- **Finding 5 (121-2 blocked on judgement's `gui: false`):** accepted, mine. STATUS NEXT for P2b states `gui: true`.
- **Finding 6 (the window's net product; the pool reversal is a user redirect, not a fault):** agreed. Card minutes self-reported over the cycle's own length (118-2: 112) are not used as cost.
