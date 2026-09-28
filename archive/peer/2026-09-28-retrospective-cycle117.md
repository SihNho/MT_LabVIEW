# retrospective-cycle117

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.1630  in 42 / out 25712 / cache-create 147289 / cache-read 2351203  (260s, 36 turn(s))
- **date:** 2026-09-28 11:48:07
- **outcome:** ANSWERED (262s)
- **verdict-card:** VERDICT-CARD retrospective-cycle117 verdict=none -> tools\bench\cards\verdict_retrospective-cycle117.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle117, role retrospective) ---
CLAIM: Cycle 117 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 117 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-28 09:58:44  ..  2026-09-28 11:43:42   (105 min)
    basis: start = archive/peer/2026-09-28-retrospective-cycle116.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-28 09:58 .. 2026-09-28 11:43 (105 min, an explicit cycle window): 90 build logs, 12 peer logs, 32 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 33/90 ok; NO BGRUN line in ['selftest_audit_c7_p1after.log', 'selftest_audit_c7_p1before.log', 'selftest_c103d_hooks_p1after.log', 'selftest_c103d_hooks_p1before.log', 'selftest_c110_launchgate_p1after.log', 'selftest_c110_launchgate_p1before.log', 'selftest_chat_p1_p1after.log', 'selftest_cycle_runner_ladder_p1after.log', 'selftest_cycle_runner_ladder_p1before.log', 'selftest_cycle_runner_p1after.log', 'selftest_cycle_runner_p1before.log', 'selftest_guard_cycle_fixed_p1after.log', 'selftest_guard_cycle_fixed_p1before.log', 'selftest_guard_cycle_offline_p1after.log', 'selftest_guard_cycle_offline_p1before.log', 'selftest_guard_cycle_rerun_p1after.log', 'selftest_guard_cycle_rerun_p1before.log', 'selftest_guard_peer_budget_p1after.log', 'selftest_guard_peer_budget_p1before.log', 'selftest_guard_peer_failre_p1after.log', 'selftest_guard_peer_failre_p1before.log', 'selftest_guard_peer_ladder_p1after.log', 'selftest_guard_peer_ladder_p1before.log', 'selftest_guard_peer_scan_tmp_p1after.log', 'selftest_guard_peer_scan_tmp_p1before.log', 'selftest_guard_session_p1after.log', 'selftest_guard_session_p1before.log', 'selftest_launch_gate_p1after.log', 'selftest_launch_gate_p1before.log', 'selftest_next_gate_jev_p1after.log', 'selftest_next_gate_jev_p1before.log', 'selftest_protocol_p1after.log', 'selftest_protocol_p1before.log', 'selftest_protocol_wiring_p1after.log', 'selftest_protocol_wiring_p1before.log', 'selftest_stage_prerun_c103_p1after.log', 'selftest_stage_prerun_c103_p1before.log', 'selftest_stage_prerun_c106c_p1after.log', 'selftest_stage_prerun_c106c_p1before.log', 'selftest_stage_prerun_c106e_p1after.log', 'selftest_stage_prerun_c106e_p1before.log', 'selftest_stage_prerun_c110g_p1after.log', 'selftest_stage_prerun_c110g_p1before.log', 'selftest_stage_prerun_c114d_p1after.log', 'selftest_stage_prerun_c114d_p1before.log', 'selftest_stage_prerun_c114_p1after.log', 'selftest_stage_prerun_c114_p1before.log', 'selftest_stage_prerun_c115a_p1after.log', 'selftest_stage_prerun_c115a_p1before.log', 'selftest_stage_prerun_c115c_p1after.log', 'selftest_stage_prerun_c115c_p1before.log', 'selftest_stage_prerun_graphload_p1after.log', 'selftest_stage_prerun_graphload_p1before.log', 'selftest_stage_prerun_headcmp_79-6_p1after.log', 'selftest_stage_prerun_headcmp_79-6_p1before.log', 'selftest_stage_prerun_stageplan_p1after.log', 'selftest_stage_prerun_stageplan_p1before.log']
  FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['selftest_guard_peer_77_measure_p1after.log', 'selftest_guard_peer_77_measure_p1before.log', 'selftest_guard_peer_jev_p1after.log', 'selftest_guard_peer_jev_p1before.log', 'selftest_guard_peer_samerow_p1after.log', 'selftest_guard_peer_samerow_p1before.log']
  PASS  A3 every failing log is followed by an archived review: 9 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 31/32 annotated; blank: ['2026-09-28-outcome-review-20260928.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 6294 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 4 log(s) with a run that printed none: ['selftest_audit_c4c_split_c117c.log', 'selftest_audit_cost_window_c117c.log', 'selftest_protocol_wiring_p1after.log', 'selftest_protocol_wiring_p1before.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 20/21 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 39, failure markers 63, logs carrying a failure 9
  C2 peer reviews dispatched 12, archived 32
  C3 wall-clock inside bgrun, BUILDS ONLY 116 min 31 s
  C4 wall-clock inside bgrun, REVIEWS 10 min 12 s; cost $7.2061 from 5 log(s) that report one
  C4b cost lines seen 5 / parsed 5
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 126 min 43 s  (builds 91%, reviews 8%, judgement session 0%)

  C6 material-marked recipe/bench runs 25, judgement-session attempts refused 6  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 210 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/diag_c117a_cmp.py, tools/bench/diag_c117a_hyg.py, tools/bench/diag_c117a_joints.py, tools/bench/diag_c117a_opv1.py, tools/bench/diag_c117b_qrt.py, tools/bench/diag_c117d_rows.py, tools/bench/errorlist_shots/113109_before_ctrl_e.png, tools/bench/errorlist_shots/113113_after_ctrl_e.png, tools/bench/errorlist_shots/113114_before_ctrl_l.png, tools/bench/errorlist_shots/113122_after_ctrl_l.png??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 342/887 ok; 545 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2607 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:513 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 654 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A2 every bgrun ended (END or TIMEOUT), A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (91; read them directly, they are the primary record) ===
tools/bench/diag_c117a_cmp.log  (2026-09-28 11:28:21)
tools/bench/diag_c117a_el.log  (2026-09-28 11:41:52)
tools/bench/diag_c117a_hyg.log  (2026-09-28 11:05:29)
tools/bench/diag_c117a_joints.log  (2026-09-28 11:25:34)
tools/bench/diag_c117a_opv1.log  (2026-09-28 10:46:38)
tools/bench/diag_c117a_opv1b.log  (2026-09-28 10:53:35)
tools/bench/diag_c117b_qrt.log  (2026-09-28 10:43:35)
tools/bench/diag_c117d_rows.log  (2026-09-28 10:51:52)
tools/bench/finish_orphan_116.log  (2026-09-28 09:58:53)
tools/bench/jev_gate.log  (2026-09-28 11:43:41)
tools/bench/motor_session_end_cycle116.log  (2026-09-28 09:58:52)
tools/bench/motor_session_start_cycle116.log  (2026-09-28 10:32:19)
tools/bench/motor_session_start_cycle117.log  (2026-09-28 10:33:29)
tools/bench/prerun_x14_check_p1.log  (2026-09-28 10:30:22)
tools/bench/run_selftests_chat_p1_after.log  (2026-09-28 10:29:36)
tools/bench/run_selftests_chat_p1_before.log  (2026-09-28 10:08:00)
tools/bench/selftest_audit_a9_witness.log  (2026-09-28 11:41:11)
tools/bench/selftest_audit_c116a_landed_c117c.log  (2026-09-28 11:35:22)
tools/bench/selftest_audit_c116a_landed_c117c2.log  (2026-09-28 11:41:18)
tools/bench/selftest_audit_c4c_split_c117c.log  (2026-09-28 11:36:14)
tools/bench/selftest_audit_c7_c117c.log  (2026-09-28 11:35:14)
tools/bench/selftest_audit_c7_p1after.log  (2026-09-28 10:22:55)
tools/bench/selftest_audit_c7_p1before.log  (2026-09-28 10:01:26)
tools/bench/selftest_audit_cost_window_c117c.log  (2026-09-28 11:35:19)
tools/bench/selftest_c103d_hooks_p1after.log  (2026-09-28 10:22:08)
tools/bench/selftest_c103d_hooks_p1before.log  (2026-09-28 10:00:40)
tools/bench/selftest_c110_launchgate_p1after.log  (2026-09-28 10:22:13)
tools/bench/selftest_c110_launchgate_p1before.log  (2026-09-28 10:00:45)
tools/bench/selftest_chat_p1.log  (2026-09-28 10:21:22)
tools/bench/selftest_chat_p1_p1after.log  (2026-09-28 10:22:59)
tools/bench/selftest_cycle_runner_ladder_p1after.log  (2026-09-28 10:22:55)
tools/bench/selftest_cycle_runner_ladder_p1before.log  (2026-09-28 10:01:25)
tools/bench/selftest_cycle_runner_p1after.log  (2026-09-28 10:22:33)
tools/bench/selftest_cycle_runner_p1before.log  (2026-09-28 10:01:04)
tools/bench/selftest_guard_cycle_fixed_p1after.log  (2026-09-28 10:22:07)
tools/bench/selftest_guard_cycle_fixed_p1before.log  (2026-09-28 10:00:39)
tools/bench/selftest_guard_cycle_offline_p1after.log  (2026-09-28 10:22:08)
tools/bench/selftest_guard_cycle_offline_p1before.log  (2026-09-28 10:00:40)
tools/bench/selftest_guard_cycle_rerun_p1after.log  (2026-09-28 10:22:08)
tools/bench/selftest_guard_cycle_rerun_p1before.log  (2026-09-28 10:00:40)
tools/bench/selftest_guard_peer_77_measure_p1after.log  (2026-09-28 10:22:59)
tools/bench/selftest_guard_peer_77_measure_p1before.log  (2026-09-28 10:01:26)
tools/bench/selftest_guard_peer_budget_p1after.log  (2026-09-28 10:23:24)
tools/bench/selftest_guard_peer_budget_p1before.log  (2026-09-28 10:01:50)
tools/bench/selftest_guard_peer_failre_p1after.log  (2026-09-28 10:23:28)
tools/bench/selftest_guard_peer_failre_p1before.log  (2026-09-28 10:01:55)
tools/bench/selftest_guard_peer_jev_p1after.log  (2026-09-28 10:23:42)
tools/bench/selftest_guard_peer_jev_p1before.log  (2026-09-28 10:02:08)
tools/bench/selftest_guard_peer_ladder_p1after.log  (2026-09-28 10:23:43)
tools/bench/selftest_guard_peer_ladder_p1before.log  (2026-09-28 10:02:10)
tools/bench/selftest_guard_peer_samerow_p1after.log  (2026-09-28 10:23:43)
tools/bench/selftest_guard_peer_samerow_p1before.log  (2026-09-28 10:02:10)
tools/bench/selftest_guard_peer_scan_tmp_p1after.log  (2026-09-28 10:23:43)
tools/bench/selftest_guard_peer_scan_tmp_p1before.log  (2026-09-28 10:02:10)
tools/bench/selftest_guard_session_p1after.log  (2026-09-28 10:21:54)
tools/bench/selftest_guard_session_p1before.log  (2026-09-28 10:00:25)
tools/bench/selftest_launch_gate_p1after.log  (2026-09-28 10:22:13)
tools/bench/selftest_launch_gate_p1before.log  (2026-09-28 10:00:45)
tools/bench/selftest_next_gate_jev_p1after.log  (2026-09-28 10:22:13)
tools/bench/selftest_next_gate_jev_p1before.log  (2026-09-28 10:00:45)
tools/bench/selftest_op_hygiene.log  (2026-09-28 11:34:19)
tools/bench/selftest_protocol_p1after.log  (2026-09-28 10:21:58)
tools/bench/selftest_protocol_p1before.log  (2026-09-28 10:00:30)
tools/bench/selftest_protocol_wiring_p1after.log  (2026-09-28 10:22:07)
tools/bench/selftest_protocol_wiring_p1before.log  (2026-09-28 10:00:39)
tools/bench/selftest_stage_prerun_c103_p1after.log  (2026-09-28 10:25:53)
tools/bench/selftest_stage_prerun_c103_p1before.log  (2026-09-28 10:04:19)
tools/bench/selftest_stage_prerun_c106c_p1after.log  (2026-09-28 10:28:12)
tools/bench/selftest_stage_prerun_c106c_p1before.log  (2026-09-28 10:06:37)
tools/bench/selftest_stage_prerun_c106e_p1after.log  (2026-09-28 10:28:45)
tools/bench/selftest_stage_prerun_c106e_p1before.log  (2026-09-28 10:07:10)
tools/bench/selftest_stage_prerun_c110g_p1after.log  (2026-09-28 10:28:45)
tools/bench/selftest_stage_prerun_c110g_p1before.log  (2026-09-28 10:07:10)
tools/bench/selftest_stage_prerun_c114_p1after.log  (2026-09-28 10:28:58)
tools/bench/selftest_stage_prerun_c114_p1before.log  (2026-09-28 10:07:24)
tools/bench/selftest_stage_prerun_c114d_p1after.log  (2026-09-28 10:29:00)
tools/bench/selftest_stage_prerun_c114d_p1before.log  (2026-09-28 10:07:26)
tools/bench/selftest_stage_prerun_c115a_p1after.log  (2026-09-28 10:29:03)
tools/bench/selftest_stage_prerun_c115a_p1before.log  (2026-09-28 10:07:29)
tools/bench/selftest_stage_prerun_c115c_p1after.log  (2026-09-28 10:29:17)
tools/bench/selftest_stage_prerun_c115c_p1before.log  (2026-09-28 10:07:42)
tools/bench/selftest_stage_prerun_graphload_p1after.log  (2026-09-28 10:29:18)
tools/bench/selftest_stage_prerun_graphload_p1before.log  (2026-09-28 10:07:43)
tools/bench/selftest_stage_prerun_headcmp_79-6_p1after.log  (2026-09-28 10:29:23)
tools/bench/selftest_stage_prerun_headcmp_79-6_p1before.log  (2026-09-28 10:07:48)
tools/bench/selftest_stage_prerun_stageplan_p1after.log  (2026-09-28 10:29:36)
tools/bench/selftest_stage_prerun_stageplan_p1before.log  (2026-09-28 10:08:00)
tools/bench/stage_d1_l2r2.log  (2026-09-28 11:24:06)
tools/bench/stage_d1_l2r2_dry_c117.log  (2026-09-28 11:07:11)
tools/bench/stage_d1_l2r2_prerun_c117.log  (2026-09-28 11:07:43)
tools/bench/wait_runner_event.log  (2026-09-28 11:34:51)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (12) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_117.log  (2026-09-28 10:35:32)
tools/bench/cycle_runner.log  (2026-09-28 10:35:32)
tools/bench/cycle_runner_main_20260928_1032.log  (2026-09-28 10:33:22)
tools/bench/cycle_runner_main_20260928_1033.log  (2026-09-28 10:35:32)
tools/bench/cycle_runner_main_20260928a.log  (2026-09-28 09:58:53)
tools/bench/outcome_review_cycle116.log  (2026-09-28 10:33:22)
tools/bench/outcome_review_cycle117.log  (2026-09-28 10:35:32)
tools/bench/peer_c117a-joints.log  (2026-09-28 11:28:03)
tools/bench/peer_c117a-opv1.log  (2026-09-28 10:49:49)
tools/bench/peer_c117c_a9.log  (2026-09-28 11:39:25)
tools/bench/peer_c117d-rows.log  (2026-09-28 11:00:21)
tools/bench/retro.log  (2026-09-28 11:43:41)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle117","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 117 (outcome review)

**Summary.** This cycle achieved its goal. The L2-R2 stage saved `D1_l2_r2_20260928_110756.vi` (md5 `7dac9f04`) in one launch with 43 gates passing and none failing (`stage_d1_l2r2.log:305,336`). Its full Error List passed: loose ends 22, matching the pin, and the expected file re-checks OK (`diag_c117a_el.log:114-117`). It is now the bed (`STATUS.md:62-64`). Alongside it, the cycle measured the QRT facts, drafted the QRT-W plan, and built the device that was due for `rule-evaded`. `next.json` names a deliverable build and follows the steering card (`next.json:4,23-26`).

I looked for a fault that changed what the cycle cost or produced, and found none. Every fault below is a few minutes, or one to three dollars of reviews, and none of them moved the cycle's end.

**The evidence window contradicts the cycle.** The judgement session started at 10:35:32 (`cycle_117.log:1`), not at 09:58:44.
- From 09:58 to 10:33 the chat was relaunching the runner for the acceleration changes (`run_selftests_chat_p1_*.log`, `cycle_runner_main_20260928_1032.log`).
- All 57 logs that fail audit A1 and all 6 that fail A2 are those `_p1before`/`_p1after` self-tests. They are not cycle 117's.
- C3 (116 min) and C5 (127 min) are longer than the 105-min window. They add up parallel cards and include the chat's work.
- Cycle 117's own reviews cost $4.82: `peer_c117a-opv1.log:4` $1.4631, `peer_c117d-rows.log:4` $1.0741, `peer_c117a-joints.log:4` $0.9719, `peer_c117c_a9.log:4` $1.3090. The remaining $2.388 of C4 is the outcome review that the runner ran before the session (`outcome_review_cycle117.log:7`).
- The judgement session's own cost is unknown. C4c is empty because the session was still open when the window closed.

**Timeline of the LabVIEW work:**

| Time | Step | Result |
|---|---|---|
| 10:44 | opv1 run 1 | FAIL |
| 10:47–10:49 | hypothesis review | |
| 10:50–10:53 | opv1b | PASS |
| 10:53:48 → 11:00:44 | hygiene sweep | held back ~7 min (see finding 5) |
| 11:05 | hygiene sweep | PASS |
| 11:05:53 | launch | refused by fp-1 |
| 11:07:51–11:24 | stage launch | PASS |
| 11:24 | joints check | FAIL |
| 11:26–11:28 | review, then offline comparison | |
| 11:30:39–11:41:52 | Error List read (card 117-5) | PASS |

## FINDINGS

**1. Repeated failure.** Three different diagnostic scripts each failed on a bug in their own checks:
- `diag_c117a_opv1.log:15`: steps run in the wrong order.
- `diag_c117d_rows.log:45,167-171`: terminals were looked up by owner, so they could never be found (`c117d-rows.md:58-60`).
- `diag_c117a_joints.log:25`: tuples from COM were compared with lists from JSON. The line prints `(6,10,2)` against `(6,10,2)` and still fails.

The Jev ladder classified all three as `new-problem` (`jev_gate.log:2564,2571,2589`), never as `our-script-bug`. So each one bought an Opus review, about $3.51 in total. The pattern was visible by the second failure (10:53): an offline check script written from scratch, outside stagekit (`jev_gate.log:2562,2568,2587`, all "stagekit=False"). That is the point where diagnostics should have moved onto shared helpers. This is not a recurring class: no earlier record of the tuple-vs-list bug exists.

**2. Missing tool.**
- A shared helper that normalises a COM read before comparing it with a JSON reference would have prevented the joints FAIL. That failure spent card 117-1's last failure, which forced L4 into a separate card (about 4 min and $0.97).
- guard_peer exempts an offline card from the LabVIEW card's failing log, but not the reverse (`guard_peer.py:901-905`). A symmetric exemption would have removed the 7-minute hold in finding 5.

**3. Unmeasured steps.** One small inference was accepted. The review said that w25225/w25238 differ only because joints are renumbered when a net is re-joined, and that this was "inferred, not measured" (`c117a-joints.md:54,75`). It does not matter, because the measured Error List (L4) settles acceptance. The tuple-vs-list reading itself was measured (`diag_c117a_cmp.log:22`).

**4. Rule compliance.**
- **stagekit rule.** CLAUDE.md requires every new diagnostic to be a file of 120 lines or fewer on stagekit. That was broken: `diag_c117d_rows.py` was 155–174 lines and `diag_c117b_qrt.py` 161 lines, both off stagekit (`jev_gate.log:2560,2568,2572`).
- **Gate routed around.** fp-2 was "routed around" by loading gscript through `importlib` with fake COM modules, then asking judgement afterwards whether that is allowed (`result_117-3.json:26`, `gate_fp_queue.jsonl:2`). That is a way past the gate, not "an equivalent form the gate accepts".
- **Outcome review not annotated.** A4 fails because the outcome review's "What was done with it" section is still blank (`outcome-review-20260928.md:229`), even though its steering card was followed.
- **What the audit does not cover:**
  - one card blocking another card's launch;
  - who annotated a review (material or judgement);
  - review dispatches killed by a runner relaunch (`outcome_review_cycle116.log:6`);
  - wrong card IDs in result cards;
  - C7's 210-file list, which is too broad to be useful.

**5. Ordering.** The order was defensible and followed the rules: STEP 0 hygiene before the launch (PD233), prep and device work on the offline slot, and L4 before accepting the bed.

The one cost was the hold. The LabVIEW card's hygiene launch was queued at 10:53:48 but only started at 11:00:44 (`material_marker.log:2686-2687`, `diag_c117a_hyg.log:1`). guard_peer's global failing-log rule held it on the offline card 117-4's throwaway draft script, which had no peer and so could not buy its own review. It stayed held until the judgement session paid for the c117d-rows review ($1.0741). This did not move the cycle's end: the offline card 117-3 finished last (`c117c-a9.md:114`, 11:43).

**6. What was not reported.**
- `result_117-1.json:23` blames "card 117-2's failing log" for the hold. It was 117-4's log; 117-2's diagnostic passed (`diag_c117b_qrt.log:36`). STATUS never mentions the 7-minute hold.
- `result_117-4.json:2` says only "rerun refused". The rerun it tried had removed the failing gate instead of fixing the lookup (`diag_c117d_rows.py:30` `INFO_ONLY`; `c117d-rows.md:81`).
- The gate_fp logging command was itself refused by the prerun gate (`material_marker.log:2689`).
- 117-4's result reads PASS 6/0 while its own diagnostic FAILED 25/4. STATUS does disclose this (`STATUS.md:77`).

**7. Judgement inside a material session.**
- Material sessions wrote "ACCEPTED" on three reviews: `c117a-opv1.md:88`, `c117a-joints.md:71` and `c117c-a9.md:115`.
  - **opv1:** fixing its own script within budget is material's job.
  - **joints:** only formal. The acceptance was still returned to judgement (`result_117-1.json:25`) and judgement accepted it (`STATUS.md:73`).
  - **c117c-a9:** this one belongs to judgement. The material session adopted a design change to audit A9's witness rule (per-bullet scope) because a review suggested it.
- The INFO_ONLY attempt, which changed what counts as a pass after a FAIL, is also a judgement act. guard_peer refused it, so it had no effect.

## DEVICE EFFECT

**Worked:**
- The bgrun FAIL scan and the rc guarantee: `diag_c117d_rows.log:419` was forced to rc=1 although the process exited 0.
- Cost regex: C4b parsed 5 of 5.
- The adversarial instruction is appended to every review (`c117a-joints.md:26-32`).
- guard_peer refused 117-4's gate-stripped rerun (`jev_gate.log:2571-2573`; no `_r2` log exists).
- bgrun_reap marked the killed pre-session runs (`cycle_runner_main_20260928_1032.log:7`).
- The cycle card carried `gates_due` (`cycle_117.json:31-52`).

**Misfired once, handled as designed:** the prerun decision-4 check refused the launch at 11:05:53 (`material_marker.log:2688`). The refusal was queued as fp-1 (`gate_fp_queue.jsonl:1`) and routed around by re-running dry and prerun, costing about 2 minutes. It was not bypassed routinely.

**guard_peer holding card 117-1:** this was the intended one-way design, pinned by a self-test (`selftest_chat_p1.py:199`). It is a flaw in the pipeline's design, not a device that failed its own purpose.

**The new op-hygiene device (10:37 decision):** the fault it exists to stop did not occur. OpWireJoints_v1 was accepted on 2,066 calls, 0 errors and flat handles (`diag_c117a_hyg.log:15-18`), not on the handle count alone. It has known holes:
- about 20 scripts call `GetVIReference` directly and bypass it (`result_117-3.json:13`);
- all 138 existing ops are grandfathered (`:16`);
- A9 is now 20 of 21 absent, "only grows", and its regression self-test fails 15/3 (`:2,24`).

**Not exercised in this window:** prior-art, stop record, SimReader, sink gates, NI-VISA, MEMSTOP, rename flagging, opmodels replay, graph shape and SendMessage refusal. No evidence shows any of them letting its own fault through.

**Total minor loss:** about 7 min (the hold, which did not change when the cycle ended), about 2 min (fp-1), about 4 min (L4 moved to a new card), and $3.51 of reviews spent on the three script bugs.

VIOLATION: none
VERDICT {"schema":"verdict/1","id":"retrospective-cycle117","verdict":"none","alternative":"Candidate device-failed: guard_peer held LabVIEW card 117-1 on offline card 117-4's failing log for 7 min (10:53:48 to 11:00:44) plus a $1.07 review; the one-way exemption was by design and the tail was card 117-3, so the cycle end did not move.","discriminating_test":"Replay the 10:53:48 hyg launch against guard_peer with diag_c117d_rows.log newest; a symmetric RULE-OFFLINE-CARD (LV card not held by a labview:none card's offline-command log) should return 0. Then check whether the cycle end (11:43) changes.","violations":[],"sources":["tools/bench/cycle_117.log:1","tools/bench/stage_d1_l2r2.log:305","tools/bench/diag_c117a_el.log:114","tools/hooks/material_marker.log:2686","tools/hooks/guard_peer.py:901","tools/bench/jev_gate.log:2589","tools/bench/cards/result_117-1.json:23","archive/peer/2026-09-28-c117d-rows.md:81"],"note":"Window starts 37 min before the session (chat relaunch); A1/A2 FAILs are chat-P1 self-tests. Deliverable R2 saved and L4 PASS. Minor: 3 own-script diag bugs all Jev-labelled new-problem ($3.51 reviews); stagekit/120-line rule broken on 2 diags."}

## Sources

(extract from answer)

## What was done with it

Annotated 2026-09-28 by the cycle-117 judgement session. `VIOLATION: none` ACCEPTED; the deliverable (L2-R2) was saved and accepted.
- Finding 1/2 (three own-script diag bugs, each a Jev `new-problem`, $3.51) ACCEPTED as a carry for a tooling card: (a) a shared
  COM-vs-JSON normalising compare in stagekit, (b) new diagnostics on stagekit ≤ 120 lines is already the rule. Next cards carry
  it as a card rule.
- Finding 2 / verdict alternative (guard_peer held LabVIEW card 117-1 on offline card 117-4's failing log for 7 min) ACCEPTED as a
  carry: a symmetric RULE-OFFLINE-CARD (a LabVIEW card is not held by a `labview: none` card's offline-command log), with the
  verdict's replay as its self-test. Queued with the gate-fp batch (fp-1, fp-2), not built mid-deliverable.
- Finding 4 (fp-2 routed around through importlib with fake COM) ACCEPTED: this is not an "equivalent form". The op-hygiene
  self-test stays, but fp-2 is decided in the gate-fp drain, and until then that route is not used again.
- Finding 7 (c117c-a9 per-bullet A9 scope adopted in material) RATIFIED by judgement in split plan PD233(j); ownership noted.
- Finding 6: the hold was 117-4's log, not 117-2's (result_117-1.json:23 mis-cites); recorded in STATUS.
- The outcome review's blank disposition (A4) was annotated in the same pass (steer_116 followed).
