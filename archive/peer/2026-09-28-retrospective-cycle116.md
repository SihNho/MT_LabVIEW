# retrospective-cycle116

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.5822  in 58 / out 48802 / cache-create 131311 / cache-read 2777341  (496s, 48 turn(s))
- **date:** 2026-09-28 09:58:44
- **outcome:** ANSWERED (498s)
- **verdict-card:** VERDICT-CARD retrospective-cycle116 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle116.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle116, role retrospective) ---
CLAIM: Cycle 116 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 116 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-28 06:54:12  ..  2026-09-28 09:50:22   (176 min)
    basis: start = archive/peer/2026-09-28-retrospective-cycle115.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-28 06:54 .. 2026-09-28 09:50 (176 min, an explicit cycle window): 84 build logs, 11 peer logs, 26 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 52/84 ok; NO BGRUN line in ['selftest_audit_c4c_split_c116a_after.log', 'selftest_audit_c4c_split_c116a_before.log', 'selftest_audit_c7_c116a_after.log', 'selftest_audit_c7_c116a_before.log', 'selftest_c103d_hooks_c116a_after.log', 'selftest_c103d_hooks_c116a_before.log', 'selftest_c106d_tools_c116a_after.log', 'selftest_c106d_tools_c116a_before.log', 'selftest_c108e_tools_c116a_after.log', 'selftest_c108e_tools_c116a_before.log', 'selftest_c110_launchgate_c116a_after.log', 'selftest_c110_launchgate_c116a_before.log', 'selftest_c111c_launchunit_c116a_after.log', 'selftest_c111c_launchunit_c116a_before.log', 'selftest_c116a_landed_c116a_after.log', 'selftest_errorlist_reuse_81_c116a_after.log', 'selftest_errorlist_reuse_81_c116a_before.log', 'selftest_launch_gate_c116a_after.log', 'selftest_launch_gate_c116a_before.log', 'selftest_stage_prerun_headcmp_79-6_c116a_after.log', 'selftest_stage_prerun_headcmp_79-6_c116a_before.log', 'selftest_stoprecord_bgrun_c116a_after.log', 'selftest_stoprecord_bgrun_c116a_before.log', 'selftest_stoprecord_c116a_c116a_after.log', 'selftest_stoprecord_eqform_c116a_after.log', 'selftest_stoprecord_eqform_c116a_before.log', 'selftest_stoprecord_offline_c107_c116a_after.log', 'selftest_stoprecord_offline_c107_c116a_before.log', 'selftest_stoprecord_supersession_c116a_after.log', 'selftest_stoprecord_supersession_c116a_before.log', 'selftest_stoprecord_table_c116a_after.log', 'selftest_stoprecord_table_c116a_before.log']
  FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['finish_orphan_116.log', 'selftest_audit_cost_window_c116a_after.log', 'selftest_audit_cost_window_c116a_before.log']; KILLED from outside, closed by bgrun_reap (flagged): ['diag_c116d_j3.log', 'runner_supervisor.log']
  PASS  A3 every failing log is followed by an archived review: 17 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 26/26 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 6128 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 4 log(s) with a run that printed none: ['diag_c116b_p0.log', 'diag_c116d_gchk.log', 'diag_c116d_restart.log', 'selftest_c116a_landed.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 13/21 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit', '2026-09-26-c92-unstamped-clickprobe', '2026-09-26-retrospective-cycle92', '2026-09-26-retrospective-cycle98']??

  C1 builds run 67, failure markers 17, logs carrying a failure 17
  C2 peer reviews dispatched 11, archived 26
  C3 wall-clock inside bgrun, BUILDS ONLY 200 min 39 s
  C4 wall-clock inside bgrun, REVIEWS 17 min 30 s; cost $9.0701 from 6 log(s) that report one
  C4b cost lines seen 6 / parsed 6
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 218 min 9 s  (builds 91%, reviews 8%, judgement session 0%)

  C6 material-marked recipe/bench runs 29, judgement-session attempts refused 6  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 276 - STATUS.md, tools/audit_cycle.py, tools/bench/.stall_samples.txt, tools/bench/cards/brief_chat-P1.md, tools/bench/cards/plan_116-2_l2r2.md, tools/bench/diag_c116a_regress.py, tools/bench/diag_c116a_replay.py, tools/bench/diag_c116b_cmp.xml, tools/bench/diag_c116b_cmp_files/0_0_1.png, tools/bench/diag_c116b_cmp_files/0_0_2.png, tools/bench/diag_c116b_cmp_files/0_1_1142_0_1.png, tools/bench/diag_c116b_cmp_files/0_1_1142_0_2.png??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/880 ok; 539 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2574 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:495 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 647 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A2 every bgrun ended (END or TIMEOUT)


=== BUILD LOGS INSIDE THE WINDOW (85; read them directly, they are the primary record) ===
tools/bench/diag_c116a_regress_after.log  (2026-09-28 07:32:41)
tools/bench/diag_c116a_regress_before.log  (2026-09-28 07:11:20)
tools/bench/diag_c116a_regress_before2.log  (2026-09-28 07:20:54)
tools/bench/diag_c116a_regress_before3.log  (2026-09-28 07:22:23)
tools/bench/diag_c116a_replay.log  (2026-09-28 07:04:32)
tools/bench/diag_c116b_keys.log  (2026-09-28 07:40:07)
tools/bench/diag_c116b_p0.log  (2026-09-28 07:57:01)
tools/bench/diag_c116b_props.log  (2026-09-28 07:51:18)
tools/bench/diag_c116b_props_dry.log  (2026-09-28 07:44:39)
tools/bench/diag_c116b_props_prerun.log  (2026-09-28 07:44:48)
tools/bench/diag_c116b_scratch.log  (2026-09-28 08:19:02)
tools/bench/diag_c116b_scratch_dry.log  (2026-09-28 08:00:19)
tools/bench/diag_c116b_scratch_el.log  (2026-09-28 08:30:36)
tools/bench/diag_c116b_scratch_prerun.log  (2026-09-28 08:01:19)
tools/bench/diag_c116c_probe.log  (2026-09-28 07:25:59)
tools/bench/diag_c116c_probe2.log  (2026-09-28 07:26:46)
tools/bench/diag_c116d_decode.log  (2026-09-28 09:33:15)
tools/bench/diag_c116d_decode_before.log  (2026-09-28 09:13:11)
tools/bench/diag_c116d_dry.log  (2026-09-28 08:52:17)
tools/bench/diag_c116d_dry2.log  (2026-09-28 08:52:40)
tools/bench/diag_c116d_dry3.log  (2026-09-28 08:53:14)
tools/bench/diag_c116d_dry4.log  (2026-09-28 08:55:26)
tools/bench/diag_c116d_dry_j3.log  (2026-09-28 08:53:36)
tools/bench/diag_c116d_dry_j3b.log  (2026-09-28 08:55:47)
tools/bench/diag_c116d_dry_j3c.log  (2026-09-28 09:16:48)
tools/bench/diag_c116d_gchk.log  (2026-09-28 08:51:48)
tools/bench/diag_c116d_j1.log  (2026-09-28 08:58:17)
tools/bench/diag_c116d_j1_dry.log  (2026-09-28 08:50:47)
tools/bench/diag_c116d_j3.log  (2026-09-28 09:15:17)
tools/bench/diag_c116d_j3b.log  (2026-09-28 09:46:51)
tools/bench/diag_c116d_opbuild.log  (2026-09-28 08:50:27)
tools/bench/diag_c116d_prerun_j1.log  (2026-09-28 08:53:16)
tools/bench/diag_c116d_prerun_j1b.log  (2026-09-28 08:55:27)
tools/bench/diag_c116d_prerun_j3.log  (2026-09-28 08:53:57)
tools/bench/diag_c116d_prerun_j3b.log  (2026-09-28 08:56:08)
tools/bench/diag_c116d_prerun_j3c.log  (2026-09-28 09:17:09)
tools/bench/diag_c116d_restart.log  (2026-09-28 09:14:56)
tools/bench/finish_orphan_116.log  (2026-09-28 09:15:17)
tools/bench/jev_gate.log  (2026-09-28 09:49:33)
tools/bench/motor_session_end_cycle115.log  (2026-09-28 07:00:54)
tools/bench/motor_session_start_cycle116.log  (2026-09-28 07:01:02)
tools/bench/plan_l2r2_make.log  (2026-09-28 07:53:07)
tools/bench/plan_l2r2_sim.log  (2026-09-28 07:53:42)
tools/bench/runner_supervisor.log  (2026-09-28 09:15:17)
tools/bench/selftest_audit_c4c_split_c116a_after.log  (2026-09-28 07:32:40)
tools/bench/selftest_audit_c4c_split_c116a_before.log  (2026-09-28 07:22:23)
tools/bench/selftest_audit_c7_c116a_after.log  (2026-09-28 07:32:03)
tools/bench/selftest_audit_c7_c116a_before.log  (2026-09-28 07:21:46)
tools/bench/selftest_audit_cost_window_c116a_after.log  (2026-09-28 07:32:03)
tools/bench/selftest_audit_cost_window_c116a_before.log  (2026-09-28 07:21:46)
tools/bench/selftest_c103d_hooks_c116a_after.log  (2026-09-28 07:31:50)
tools/bench/selftest_c103d_hooks_c116a_before.log  (2026-09-28 07:21:29)
tools/bench/selftest_c106d_tools_c116a_after.log  (2026-09-28 07:31:51)
tools/bench/selftest_c106d_tools_c116a_before.log  (2026-09-28 07:21:30)
tools/bench/selftest_c108e_tools_c116a_after.log  (2026-09-28 07:31:58)
tools/bench/selftest_c108e_tools_c116a_before.log  (2026-09-28 07:21:37)
tools/bench/selftest_c110_launchgate_c116a_after.log  (2026-09-28 07:31:59)
tools/bench/selftest_c110_launchgate_c116a_before.log  (2026-09-28 07:21:38)
tools/bench/selftest_c111c_launchunit_c116a_after.log  (2026-09-28 07:31:59)
tools/bench/selftest_c111c_launchunit_c116a_before.log  (2026-09-28 07:21:38)
tools/bench/selftest_c116a_landed.log  (2026-09-28 07:30:52)
tools/bench/selftest_c116a_landed_c116a_after.log  (2026-09-28 07:32:41)
tools/bench/selftest_errorlist_reuse_81_c116a_after.log  (2026-09-28 07:32:03)
tools/bench/selftest_errorlist_reuse_81_c116a_before.log  (2026-09-28 07:21:46)
tools/bench/selftest_launch_gate_c116a_after.log  (2026-09-28 07:31:59)
tools/bench/selftest_launch_gate_c116a_before.log  (2026-09-28 07:21:42)
tools/bench/selftest_launch_gate_c116c_r1.log  (2026-09-28 07:31:19)
tools/bench/selftest_launch_gate_c116c_r2.log  (2026-09-28 07:31:20)
tools/bench/selftest_stage_prerun_headcmp_79-6_c116a_after.log  (2026-09-28 07:32:00)
tools/bench/selftest_stage_prerun_headcmp_79-6_c116a_before.log  (2026-09-28 07:21:43)
tools/bench/selftest_stoprecord_bgrun_c116a_after.log  (2026-09-28 07:31:45)
tools/bench/selftest_stoprecord_bgrun_c116a_before.log  (2026-09-28 07:21:25)
tools/bench/selftest_stoprecord_c116a.log  (2026-09-28 07:24:57)
tools/bench/selftest_stoprecord_c116a_c116a_after.log  (2026-09-28 07:32:41)
tools/bench/selftest_stoprecord_eqform_c116a_after.log  (2026-09-28 07:31:47)
tools/bench/selftest_stoprecord_eqform_c116a_before.log  (2026-09-28 07:21:26)
tools/bench/selftest_stoprecord_offline_c107_c116a_after.log  (2026-09-28 07:31:49)
tools/bench/selftest_stoprecord_offline_c107_c116a_before.log  (2026-09-28 07:21:28)
tools/bench/selftest_stoprecord_supersession_c116a_after.log  (2026-09-28 07:31:49)
tools/bench/selftest_stoprecord_supersession_c116a_before.log  (2026-09-28 07:21:28)
tools/bench/selftest_stoprecord_table_c116a_after.log  (2026-09-28 07:31:45)
tools/bench/selftest_stoprecord_table_c116a_before.log  (2026-09-28 07:21:24)
tools/bench/stage_d1_l2r2_dry.log  (2026-09-28 07:59:50)
tools/bench/stage_d1_l2r2_prerun.log  (2026-09-28 08:00:25)
tools/bench/wait_runner_event.log  (2026-09-28 09:15:17)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (11) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_115.log  (2026-09-28 07:00:43)
tools/bench/cycle_116.log  (2026-09-28 09:15:17)
tools/bench/cycle_runner.log  (2026-09-28 07:01:03)
tools/bench/cycle_runner_main_20260928a.log  (2026-09-28 09:15:17)
tools/bench/peer_c116b_keys.log  (2026-09-28 07:39:17)
tools/bench/peer_c116b_pin.log  (2026-09-28 08:36:20)
tools/bench/peer_c116b_plan.log  (2026-09-28 07:51:15)
tools/bench/peer_c116c_regress.log  (2026-09-28 07:18:54)
tools/bench/peer_c116d-sweep.log  (2026-09-28 09:20:59)
tools/bench/peer_priorart_c116b_l2r2.log  (2026-09-28 08:02:25)
tools/bench/retro.log  (2026-09-28 09:50:21)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle116","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The claim is **refuted**. Cycle 116 was mostly well run, but it had one real structural fault, plus one failed device that the threshold-1 rule requires me to report.

The evidence window starts at 06:54:12, but cycle 116's session only began at 07:01:03 (`tools/bench/cycle_116.log:1`). The 06:54–07:01 logs (`cycle_115.log`, `motor_session_end_cycle115.log`) belong to cycle 115 and are not counted here. The task text names `docs/cycle27-plan.md` as this cycle's plan, which is also wrong: the cycle worked from `docs/d1-loop12-17-split-plan.md` (`tools/bench/next.json:7`). The audit's C7 already uses the right plan.

## The most costly structural fault

**A new reader VI broke the reference-hygiene rule, and its proof test passed only on paper.** Slug: rule-evaded.

- **What happened.** CLAUDE.md:218-219 says op VIs must close "every ref they create (… Traverse arrays …)". Card 116-4 repeated this (`task_116-4.json:25,64`). The new `OpWireJoints_v0` closed only the property node's reference (`tools/bench/diag_c116d_opbuild.log:34-35`). Its `error in` was left unwired (`:27`), so any Traverse error was thrown away.
- **Why the proof missed it.** The op passed the rule's "20 calls, handles flat" test (`result_116-4.json:15`). The code already says that test can't see this leak: `tools/gscript.py:247-249` states the counters "CANNOT see refnum-class exhaustion inside an op VI" (measured in cycle 38).
- **What it broke.**
  - The R1 sweep failed from read 536 onward (`diag_c116d_j3.log:84,108`).
  - LabVIEW hung at 37,034 handles and had to be restarted (`diag_c116d_restart.log:3`).
  - A $2.17 hypothesis review followed (`peer_c116d-sweep.log:4`).
  - Only 536 of 1,945 wires were read, so R1's 24th loose-ends item is still unexplained (`result_116-4.json:18`).
  - Cycle 117 now opens with an op-repair step before the L2-R2 launch (`next.json:4`, plan PD231(e) at `docs/d1-loop12-17-split-plan.md:2109`).
- **Loss.** About 18 min on the critical path: attempt 1 started at 08:58:40 (`diag_c116d_j3.log:1`) and attempt 2 at 09:17:15 (`tools/hooks/material_marker.log:2669`). Plus $2.17.
- **Counterfactual.** Had the op build at 08:46 also closed the Traverse array and wired its error, as CLAUDE.md:218-219 requires, the 08:58 run would have finished both phases in one go. Card 116-4 would have ended around 09:29 instead of 09:47, with the sweep covering whatever its time cap allowed rather than stopping at 536. The 24th item would most likely have been named, and cycle 117 could open with the L2-R2 launch.

**The second line is a device failure, reported under the threshold-1 rule, not because it is as costly.** The audit A9 "disposition landed" check (decision 2026-09-28 07:05, part 2) had one acceptance test: flag `guard_card.py:44` before the fix and show 0 after (`docs/violation-decisions.md:1655`).
- On the unfixed code it did not flag the `guard_card` hole. The self-test that pins that hole cites the review, and the check counted that citation as proof the fix had landed (`result_116-3.json:2,26`).
- After the fixes it still showed 12, not 0.
- The judgement session declined it ("Not accepted as a device", `docs/d1-loop12-17-split-plan.md:2096`) and left the repair as an unscheduled carry (STATUS.md:82). It is not in `next.json`.
- **Loss this cycle:** 0 min, because both fixes were landed by hand. The cost is forward: this class of fault is still unguarded.
- **Counterfactual:** the material agent itself proposed, around 07:13, that only a file outside `tools/bench` should count as a witness (`result_116-1.json:25`). Had 116-3 built that, instead of also counting `tools/bench/selftest_*`, A9 would have met its acceptance inside 116-3, which ended around 07:36.

## Findings

**1. Repeated failure**
- **Blocked card, same cause as last cycle.** 116-1 came back blocked: a failed prediction armed `guard_peer`, and the card listed no peer (`result_116-1.json:3`, `task_116-1.json:68`). Card 115-4 was blocked the same way one cycle earlier (`result_115-4.json:3`). The carried rule (PD230(g), plan :2088) was read as covering only "diagnosis cards". The change was due when the 116-1 card was written: any card that checks its own diagnostic against a pass contract should carry a hypothesis peer. Cost: one extra dispatch, the baseline rerun twice more, and $1.08.
- **Own-script bugs sent to review.** The Jev ladder labelled two of the cycle's own script bugs as "new-problem" (`jev_gate.log:2435,2479`). Together with c116b-plan, $3.58 of hypothesis reviews went on script bugs.
- **Pre-run checks misfiring on diagnostics.** They demanded stage plans from read-only diagnostic scripts (X2/X3/X5/X9: `diag_c116b_props_prerun.log:28-38`, `diag_c116d_prerun_j1.log:30-40`). This is the same class as 115-2's X5 false positive.
- **Within 116-4 the change came at the right attempt**: attempt 2 was redesigned.

**2. Missing tool**
- **No refnum probe.** Nothing measures VI Server reference consumption, and the only hygiene tool is known to be blind to it. The review's two-minute fixed-index test (`archive/peer/2026-09-28-c116d-sweep.md:67-71,89-95`) would have caught J1's leak before the sweep. It was not run even after the failure (`:112-113`).
- **Read-only `md5sum` refused.** The judgement/material guard in `guard_bash` blocks `md5sum` because it is not on the read-only list (`tools/hooks/guard_bash.py:66`; refusals at `material_marker.log:2654,2671`, and `2616-2617` in cycle 115). The cost is small but it keeps recurring.

**3. Unmeasured steps**
- J1's hygiene was accepted on handle count although the code documents that count as blind (see above).
- The loose-ends pin of 24 came from arithmetic (`plan_l2r2_make.log:44`). That arithmetic did not treat separately the two tunnels with no inner stub (`:26-27`), and those are exactly the two nets that re-joined (`result_116-4.json:21`). The scratch run caught the miss, as designed.
- A9's 12 "absent" items were declared "not owed code" all at once (plan :2096). The result card had asked which of them were owed (`result_116-3.json:29`).

**4. Rule compliance**
- **Broken:** CLAUDE.md:218-219 (Traverse arrays not closed).
- **Satisfied only on paper:**
  - CLAUDE.md:224-225, the handle-count proof.
  - CLAUDE.md:499-500, which says an op that doesn't close its Traverse references is repaired before any staged build uses it. After the leak was known, the unrepaired op was used again in attempt 2, which ran the recipe body on a scratch copy (`diag_c116d_j3b.log`). The review had said this was "not shown safe" (`c116d-sweep.md:73-84`).
  - The failure budget of 2 was counted per script. 116-2 had 7 logs ending rc=1 (for example `plan_l2r2_make.log:22`, `diag_c116b_keys.log:27`, `stage_d1_l2r2_prerun.log:133`); 116-4 had 6.
- **What the audit's two failures actually are.** A1's 32 logs are child logs of the regression runner, whose parent ran under bgrun (`diag_c116a_regress_after.log:73`). A2's "unfinished" cost-window logs are self-test fixture text (`selftest_audit_cost_window_c116a_after.log:8`). The KILLED entries come from an outside kill at 09:12 (`tools/finish_orphan_cycle.py:2-3`).
- **What the audit does not cover:** whether an op VI closes its references, whether a device met its own acceptance, and failure-budget counting.

**5. Ordering**
- Defensible overall: STEP 0a, then 116-2, then measuring the pin gap. PD230(f) forbade carrying a count licence over to L2-R2 (plan :2078), so measuring before re-pinning was correct.
- Two ordering faults:
  - J1's hygiene test ran on a small scratch VI, and the full-size test was left to the measurement run itself.
  - `next.json` makes naming R1's 24th item an acceptance condition for the op repair, and so a gate on L2-R2. But that residual is "unchanged by R2" (`result_116-4.json:24`), so it holds back the deliverable for an unrelated question.

**6. What was not reported**
- **Session cost lost.** The runner was killed at 09:12, so the judgement session's cost for cycle 116 is lost (audit C4c shows 0; `finish_orphan_cycle.py:44` writes `$?`). Cycle 115's session cost $37.41 (`cycle_runner_main_20260928a.log:28`), so the largest cost line of this cycle is missing.
- **STATUS understates 116-4.** STATUS.md:80 says only "the reader op leaks". It omits:
  - the rule breach;
  - the LabVIEW hang and restart;
  - that attempt 2 dropped the whole-graph sweep by the material agent's own decision.
- **Failed runs.** STATUS reports only the P4 failure out of 116-2's seven failed runs.

**7. Judgement inside a material session**
- **Pin model chosen by the material agent.** It picked the per-wire-object counting model from three candidates (24/25/26), which set the pin that later failed, and it declined the review's separating test (`archive/peer/2026-09-28-c116b-plan.md:98-104`).
- **Review accepted and design changed by the material agent.** It accepted the refnum-exhaustion reading. It had already launched a redesigned attempt 2, without the sweep, at 09:17, before the review answered (review 09:15:52–09:21). It also declined the review's falsifier (`c116d-sweep.md:109-114`).
- **Severity chosen by the material agent.** It set A9 to WARN (`result_116-3.json:33`).
- **Correct hand-back:** `c116b-pin.md:105-108` returned its question to judgement as it should.

## Device effect
- **Cost-line parsing:** worked (C4b 6/6).
- **bgrun exit-code propagation:** worked. `diag_c116b_keys.log:27` shows rc=1 although the process itself exited 0.
- **Adversarial review prompts:** worked (`c116d-sweep.md:27-33`).
- **Blank-disposition gate:** worked (A4 26/26).
- **Prior-art and premature-build gates:** worked for the recipe (prior-art 08:00–08:02 came before the scratch run). But an op VI built from a `tools/bench` script falls outside the gate by design, and this cycle's fault came in through that gap.
- **Stop record:** no STOPPED-RECIPE refusal inside the window; self-test 38/0.
- **`guard_peer`:** fired correctly on 116-1.
- **C7 scope counter:** now reads the correct plan, but at 276 files it is noise.
- **A9 disposition-landed check:** failed (second line below).
- **The rest** (motor, reaper, SimReader, send-message guard): not exercised in this window.

VIOLATION: rule-evaded | loss_min=18 | loss_usd=2.17 | evidence=tools/bench/diag_c116d_opbuild.log:35
VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/cards/result_116-3.json:26
VERDICT {"schema":"verdict/1","id":"retrospective-cycle116","verdict":"refuted","alternative":"The leak was unforeseeable: J1's 20-call handle test is the proof CLAUDE.md prescribes, so the op met the rule as written and the cycle had no structural fault.","discriminating_test":"Open OpWireJoints_v0's diagram: a Traverse refnum array with no Close Reference (opbuild.log:35 closes only the PN ref) breaks CLAUDE.md:218-219 whatever the handle count shows.","violations":[{"slug":"rule-evaded","loss_min":18,"loss_usd":2.17,"evidence":"tools/bench/diag_c116d_opbuild.log:35"},{"slug":"device-failed","loss_min":0,"loss_usd":"?","evidence":"tools/bench/cards/result_116-3.json:26"}],"sources":["CLAUDE.md:218","tools/gscript.py:247","tools/bench/diag_c116d_j3.log:84","tools/bench/peer_c116d-sweep.log:4","tools/hooks/material_marker.log:2669","docs/violation-decisions.md:1655","docs/d1-loop12-17-split-plan.md:2096"],"note":"Runner death at 09:12 was an external kill, not this cycle's fault; the judgement-session cost for cycle 116 is unrecorded."}

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
