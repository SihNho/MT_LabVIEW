# retrospective-cycle125

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $1.4275  in 24 / out 18787 / cache-create 106212 / cache-read 1009903  (189s, 32 turn(s))
- **date:** 2026-10-01 20:01:45
- **outcome:** ANSWERED (191s)
- **verdict-card:** VERDICT-CARD retrospective-cycle125 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle125.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle125, role retrospective) ---
CLAIM: Cycle 125 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 125 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-01 13:42:20  ..  2026-10-01 19:58:29   (376 min)
    basis: start = archive/peer/2026-10-01-retrospective-cycle122.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `inference-over-measurement` (decided 2026-10-01 13:56): is edited while a LabVIEW card is live, retrospective-cycle121 disposition): - **(1) The census prediction is computed, not typed.** `stage_prerun --prerun` derives each create row's class-count delta from the op's MEASURED samples (a `created_classes` field in `tools/bench/opmodels/<op>.json`; the first sample for `OpConstInd_v0` is taken from `stage_d1_ring_p2b_scratch_pin.log:60-132`: an array ??

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

== cycle audit, 2026-10-01 13:42 .. 2026-10-01 19:58 (376 min, an explicit cycle window): 114 build logs, 18 peer logs, 19 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 114/114 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 26 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 15/19 annotated; blank: ['2026-10-01-g6-call-a-gemini.md', '2026-10-01-g6-call-b-claude.md', '2026-10-01-g6-call-b-gemini.md', '2026-10-01-priorart-c124-6-ring-p3a.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 7652 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 4 log(s) with a run that printed none: ['c125_1_probe.log', 'diag_c123_ring_p3_facts.log', 'plan_ring_p3a_make_v3b.log', 'selftest_c120_routes_c123_7.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 152, failure markers 31, logs carrying a failure 26
  C2 peer reviews dispatched 18, archived 19
  C3 wall-clock inside bgrun, BUILDS ONLY 464 min 49 s
  C4 wall-clock inside bgrun, REVIEWS 32 min 38 s; cost $12.8192 from 9 log(s) that report one
  C4b cost lines seen 9 / parsed 9
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 283 min 24 s; cost $112.7463 from 2 log(s) - cycle_123.log, cycle_124.log
  C5 total wall-clock 780 min 51 s  (builds 59%, reviews 4%, judgement session 36%)

  C6 material-marked recipe/bench runs 60, judgement-session attempts refused 2  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 796 - tools/bench/.stall_samples.txt, tools/bench/c125_1_probe.py, tools/bench/c125_1_regress.py, tools/bench/c125_5_fsscan.py, tools/bench/c125_5_md5.py, tools/bench/cards/brief_123-1.md, tools/bench/cards/brief_123-2.md, tools/bench/cards/brief_123-3.md, tools/bench/cards/brief_123-4.md, tools/bench/cards/brief_123-6.md, tools/bench/cards/brief_123-7.md, tools/bench/cards/brief_123-8.md??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 345/1097 ok; 752 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2570 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:112 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  WARN  L5 superseded documents are not still current: docs/ring-buffer-design.md supersedes docs/d1-build-plan.md, which is still `status: current`
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 653 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (115; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure.log  (2026-10-01 18:44:46)
tools/bench/c125_1_probe.log  (2026-10-01 18:36:33)
tools/bench/c125_1_regress.log  (2026-10-01 18:59:19)
tools/bench/c125_5_cs.log  (2026-10-01 19:45:27)
tools/bench/c125_5_cs2.log  (2026-10-01 19:45:33)
tools/bench/c125_5_donors.log  (2026-10-01 19:37:43)
tools/bench/c125_5_fsscan.log  (2026-10-01 19:35:58)
tools/bench/c125_5_fsscan2.log  (2026-10-01 19:36:16)
tools/bench/c125_5_md5.log  (2026-10-01 19:56:07)
tools/bench/diag_c123_casetun.log  (2026-10-01 16:03:29)
tools/bench/diag_c123_casetun_dry.log  (2026-10-01 16:00:09)
tools/bench/diag_c123_casetun_prerun.log  (2026-10-01 16:00:12)
tools/bench/diag_c123_graph_p2b.log  (2026-10-01 15:48:28)
tools/bench/diag_c123_imgtype.log  (2026-10-01 14:29:50)
tools/bench/diag_c123_imgtype_offline.log  (2026-10-01 14:15:16)
tools/bench/diag_c123_q1.log  (2026-10-01 14:47:58)
tools/bench/diag_c123_ring_p3_facts.log  (2026-10-01 14:02:29)
tools/bench/diag_c123_ring_p3_routes.log  (2026-10-01 14:06:08)
tools/bench/diag_c123_routes.log  (2026-10-01 14:59:50)
tools/bench/diag_c123_routes_dry.log  (2026-10-01 14:55:45)
tools/bench/diag_c123_routes_prerun.log  (2026-10-01 14:55:48)
tools/bench/diag_c123_struct.log  (2026-10-01 15:16:08)
tools/bench/diag_c123_struct_dry.log  (2026-10-01 15:13:19)
tools/bench/diag_c123_struct_prerun.log  (2026-10-01 15:13:21)
tools/bench/diag_c123_wired.log  (2026-10-01 15:31:19)
tools/bench/diag_c123_wired_dry.log  (2026-10-01 15:28:08)
tools/bench/diag_c123_wired_prerun.log  (2026-10-01 15:28:29)
tools/bench/diag_c123_x15_p2b_prerun.log  (2026-10-01 15:37:14)
tools/bench/diag_c124_opconnecttermuid.log  (2026-10-01 16:26:15)
tools/bench/diag_c124_opconnecttermuid_r2.log  (2026-10-01 16:33:06)
tools/bench/diag_c124_opctu_hyg.log  (2026-10-01 16:42:17)
tools/bench/diag_c124_p3a_scratch.log  (2026-10-01 16:53:20)
tools/bench/diag_c124_p3a_scratch_dry.log  (2026-10-01 16:43:18)
tools/bench/diag_c124_p3a_scratch_prerun.log  (2026-10-01 16:43:21)
tools/bench/diag_c125_4fsm.log  (2026-10-01 19:27:08)
tools/bench/diag_c125_5_fsfind.log  (2026-10-01 19:40:39)
tools/bench/diag_c125_5_opfs.log  (2026-10-01 19:47:23)
tools/bench/diag_c125_5_stub.log  (2026-10-01 19:51:26)
tools/bench/diag_c125_graph_p3a.log  (2026-10-01 19:04:41)
tools/bench/diag_c125_graph_p3a_dry.log  (2026-10-01 19:01:40)
tools/bench/diag_c125_graph_p3a_prerun.log  (2026-10-01 19:01:48)
tools/bench/diag_c125_joints.log  (2026-10-01 19:28:36)
tools/bench/diag_c125_loose.log  (2026-10-01 19:06:09)
tools/bench/jev_gate.log  (2026-10-01 19:58:24)
tools/bench/motor_session_end_cycle122.log  (2026-10-01 13:48:24)
tools/bench/motor_session_end_cycle123.log  (2026-10-01 16:06:37)
tools/bench/motor_session_end_cycle124.log  (2026-10-01 18:32:24)
tools/bench/motor_session_start_cycle123.log  (2026-10-01 13:48:32)
tools/bench/motor_session_start_cycle124.log  (2026-10-01 16:06:44)
tools/bench/motor_session_start_cycle125.log  (2026-10-01 18:32:32)
tools/bench/plan_ring_p3a_make.log  (2026-10-01 15:51:07)
tools/bench/plan_ring_p3a_make_v3.log  (2026-10-01 17:06:05)
tools/bench/plan_ring_p3a_make_v3b.log  (2026-10-01 17:29:43)
tools/bench/plan_ring_p3a_sim.log  (2026-10-01 15:51:08)
tools/bench/plan_ring_p3a_sim_v2.log  (2026-10-01 16:17:09)
tools/bench/plan_ring_p3a_sim_v3.log  (2026-10-01 17:06:52)
tools/bench/plan_ring_p3a_sim_v3b.log  (2026-10-01 17:30:21)
tools/bench/selftest_c120_routes_c123_7.log  (2026-10-01 15:36:50)
tools/bench/selftest_c120_routes_c124_1.log  (2026-10-01 16:27:04)
tools/bench/selftest_c120_routes_c124_4.log  (2026-10-01 16:34:50)
tools/bench/selftest_c120_routes_c124_5.log  (2026-10-01 16:54:27)
tools/bench/selftest_c125_1.log  (2026-10-01 18:42:46)
tools/bench/selftest_case_frame_c124.log  (2026-10-01 16:22:53)
tools/bench/selftest_case_frame_c124_6.log  (2026-10-01 17:05:29)
tools/bench/selftest_case_frame_c124_6b.log  (2026-10-01 17:10:45)
tools/bench/selftest_case_frame_c124_reg_c120_routes.log  (2026-10-01 16:21:27)
tools/bench/selftest_case_frame_c124_reg_case_wired.log  (2026-10-01 16:21:21)
tools/bench/selftest_case_frame_c124_reg_census_predict.log  (2026-10-01 16:21:28)
tools/bench/selftest_case_frame_c124_reg_launch_gate.log  (2026-10-01 16:21:30)
tools/bench/selftest_case_wired_c123.log  (2026-10-01 15:35:17)
tools/bench/selftest_case_wired_c124_1.log  (2026-10-01 16:26:58)
tools/bench/selftest_case_wired_c124_4.log  (2026-10-01 16:34:46)
tools/bench/selftest_case_wired_c124_5.log  (2026-10-01 16:54:24)
tools/bench/selftest_census_hookin_c123.log  (2026-10-01 15:36:04)
tools/bench/selftest_census_hookin_c124_1.log  (2026-10-01 16:27:00)
tools/bench/selftest_census_hookin_c124_4.log  (2026-10-01 16:34:48)
tools/bench/selftest_census_hookin_c124_5.log  (2026-10-01 16:54:25)
tools/bench/selftest_census_predict.log  (2026-10-01 14:43:41)
tools/bench/selftest_census_predict_c123_7.log  (2026-10-01 15:36:38)
tools/bench/selftest_census_predict_c124_1.log  (2026-10-01 16:27:01)
tools/bench/selftest_census_predict_c124_4.log  (2026-10-01 16:34:49)
tools/bench/selftest_census_predict_c124_5.log  (2026-10-01 16:54:26)
tools/bench/selftest_launch_gate_c123_7.log  (2026-10-01 15:36:38)
tools/bench/selftest_launch_gate_c124_1.log  (2026-10-01 16:27:07)
tools/bench/selftest_launch_gate_c124_4.log  (2026-10-01 16:34:56)
tools/bench/selftest_launch_gate_c124_5.log  (2026-10-01 16:54:34)
tools/bench/selftest_launch_gate_c124_6.log  (2026-10-01 17:10:52)
tools/bench/selftest_sr_init_c123.log  (2026-10-01 15:00:16)
tools/bench/selftest_sr_init_c123_c123_7.log  (2026-10-01 15:36:35)
tools/bench/selftest_sr_init_c123_stagexec.log  (2026-10-01 14:56:28)
tools/bench/selftest_stagesim_c124.log  (2026-10-01 16:21:13)
tools/bench/selftest_stagexec_c123_7.log  (2026-10-01 15:36:47)
tools/bench/selftest_stagexec_c124.log  (2026-10-01 16:21:30)
tools/bench/selftest_stagexec_c124_4.log  (2026-10-01 16:35:11)
tools/bench/selftest_stagexec_c124_5.log  (2026-10-01 16:54:48)
tools/bench/selftest_stagexec_c124_6.log  (2026-10-01 17:09:33)
tools/bench/stage_d1_ring_p2b.log  (2026-10-01 14:14:28)
tools/bench/stage_d1_ring_p2b_el_final.log  (2026-10-01 14:26:02)
tools/bench/stage_d1_ring_p2b_el_scratch.log  (2026-10-01 14:06:31)
tools/bench/stage_d1_ring_p3a.log  (2026-10-01 18:17:40)
tools/bench/stage_d1_ring_p3a_dry.log  (2026-10-01 17:09:49)
tools/bench/stage_d1_ring_p3a_dry2.log  (2026-10-01 17:31:11)
tools/bench/stage_d1_ring_p3a_el_final.log  (2026-10-01 18:29:24)
tools/bench/stage_d1_ring_p3a_el_scratch.log  (2026-10-01 18:05:10)
tools/bench/stage_d1_ring_p3a_prerun.log  (2026-10-01 17:10:17)
tools/bench/stage_d1_ring_p3a_prerun2.log  (2026-10-01 17:31:39)
tools/bench/stage_d1_ring_p3a_scratch_dry.log  (2026-10-01 17:17:38)
tools/bench/stage_d1_ring_p3a_scratch_dry2.log  (2026-10-01 17:32:04)
tools/bench/stage_d1_ring_p3a_scratch_pin.log  (2026-10-01 17:21:33)
tools/bench/stage_d1_ring_p3a_scratch_pin2.log  (2026-10-01 17:46:16)
tools/bench/stage_d1_ring_p3a_scratch_prerun.log  (2026-10-01 17:18:11)
tools/bench/stage_d1_ring_p3a_scratch_prerun2.log  (2026-10-01 17:32:52)
tools/bench/stage_d1_ring_p3a_scratchreq.log  (2026-10-01 17:11:18)
tools/bench/stage_d1_ring_p3a_scratchreq2.log  (2026-10-01 17:31:40)
tools/bench/wait_runner_event.log  (2026-10-01 19:33:44)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (18) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_122.log  (2026-10-01 13:48:18)
tools/bench/cycle_123.log  (2026-10-01 16:06:30)
tools/bench/cycle_124.log  (2026-10-01 18:32:14)
tools/bench/cycle_125.log  (2026-10-01 18:32:33)
tools/bench/cycle_runner.log  (2026-10-01 18:32:33)
tools/bench/cycle_runner_main_20261001_1227.log  (2026-10-01 18:32:33)
tools/bench/peer_c123-3-t8.log  (2026-10-01 14:54:47)
tools/bench/peer_c123_5_s1a.log  (2026-10-01 15:19:37)
tools/bench/peer_c124_1_casetun_fact.log  (2026-10-01 16:18:56)
tools/bench/peer_c124_1_casetun_hyp.log  (2026-10-01 16:15:45)
tools/bench/peer_c124_8_p3a_termclass_hyp.log  (2026-10-01 17:28:31)
tools/bench/peer_c125-1-x16.log  (2026-10-01 18:53:28)
tools/bench/peer_c125_2_flatseq.log  (2026-10-01 19:06:30)
tools/bench/peer_c125_2_loose_hyp.log  (2026-10-01 19:16:05)
tools/bench/peer_c125_5_addframe_hyg.log  (2026-10-01 19:49:49)
tools/bench/peer_c125_5_stub.log  (2026-10-01 19:55:25)
tools/bench/priorart_c124_6_ring_p3a.log  (2026-10-01 17:10:40)
tools/bench/retro.log  (2026-10-01 19:58:28)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle125","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The fault is that card 125-5's hygiene test was invalid, so the new Add Frame op can't be used yet. It ranks first because it set how the cycle ended; the full review follows.

**Window note.** The 13:42–19:58 window covers three cycles, not one: cycle 123 (`cycle_123.log`), cycle 124 (`cycle_124.log`) and cycle 125, which starts at 18:32:33 (`tools/bench/cycle_125.log:1`). The audit's C3 (465 min), C4c ($112.75, from cycle_123/124 only) and C5 therefore add up three cycles. Cycle 125's own judgement-session cost is unknown: `cycle_125.log` has no END line. Below, "this cycle" means 18:32–19:58 (86 min, five cards). Cycle 124's facts are used only where they show a recurrence.

## Verdict on the claim
The claim is "Cycle 125 was run without a costly structural fault." I refute it, narrowly. The cycle was tight: five cards in 86 min, failures returned quickly, and reviews cost $0.99–$2.44 each. But one fault decided how it ended.

**The fault.** Card 125-5's hygiene test for `OpFsAddFrame_v0` broke the plan's own equal-VI-state rule, PD242(b) (`docs/d1-loop12-17-split-plan.md:2339-2342`).
- `hyg_adder` opened a fresh copy every round and never closed it (`tools/bench/diag_c125_5_opfs.py:136-142`).
- Handles rose +116 and the gate failed (`diag_c125_5_opfs.log:64`).
- The review accepted that this reading is invalid, not a measured leak (`archive/peer/2026-10-01-c125-5-addframe-hyg.md:55-61, 100-107`).
- Consequences:
  - The op's record says FAIL, so `gscript.op` refuses it.
  - The already-written 3-frame scratch (`diag_c125_5_fsscr.py`) never ran.
  - Cycle 126's first act is the rerun (`tools/bench/next.json:4`).
- The correct pattern already existed: `diag_c122_hyg.py:66-74` closes the copy every round (`s.drop_scratch`) and measures at equal state.
- Why it is a repeat, not a one-off:
  - Card 124-4 also failed on its hand-written hygiene script, which called the op outside `hygiene_probe`. Its note says "Second failure of the same build script" (`tools/bench/cards/result_124-4.json:2,23`).
  - So 125-5 is the third hand-written hygiene script, and the second in a row to fail on the script rather than the op.
- The brief made it easier: `brief_125-5.md:13-14` gives "2,000 calls, 0 errors, ±100" but leaves out PD242(b)'s equal-state clause.

**Loss.**
- Logged: the review, $0.996 / 89 s (`peer_c125_5_addframe_hyg.log:4,48`), plus the invalid AH block inside a 222 s run (`diag_c125_5_opfs.log:75`).
- Not logged: a LabVIEW card in cycle 126 spent on the rerun. The review puts the rerun itself under 4 min; with card setup, about 15 min in total.
- No log carries the full dollar figure, so it is `?`.

**Counterfactual.** Suppose `hyg_adder` had copied `diag_c122_hyg.py:74`'s per-round `drop_scratch` at the 19:43:41 launch.
- AH would have been a valid reading by about 19:47.
- If it passed, `diag_c125_5_fsscr.py` could have run inside the same card: the card used 30 of its 60 budgeted minutes (`result_125-5.json`).
- The cycle would have ended around 20:05 with the Flat Sequence creator verified, and cycle 126 would open on card B instead of a rerun.
- If the op really leaks, the cycle would have ended with a genuine FAIL rather than an unreadable one. Either way the rerun card is waste.

## FINDINGS

**1. Repeated failure.** Hand-written hygiene scripts failed on the script itself twice running: 124-4 (`result_124-4.json:2`) and 125-5 (`diag_c125_5_opfs.log:64`). The approach should have changed at 124-4, the second such failure: one shared hygiene runner instead of a new loop per op. A smaller repeat: `c125_1_offline_measure.py` run 1 failed on its own harness, which pre-imported win32com (`c125_1_offline_measure.log:6-10`), and was fixed and rerun inside the card.

**2. Missing tool.** A shared runner, e.g. `gscript.hygiene_run(op, workload, recycle=True)`: it wraps `hygiene_probe`, closes each copy without saving, samples handles before and after the calls and after the close, and adds GDI/USER counts. That would have caught both 124-4 (op called outside the probe) and 125-5 (no equal-state recycle). Three separate scripts exist today: `diag_c122_hyg.py`, `diag_c124_opctu_hyg.py`, `diag_c125_5_opfs.py`.

**3. Unmeasured steps.** Second-ranked candidate, below the threshold.
- The judgement session predicted "exactly one new loose wire" by counting terminal rows. The plan admits this was "wrong before it ran" (`d1-loop12-17-split-plan.md:2583`).
- The right measurement already existed: `wire_joints` (`OpWireJoints_v1`, already passed its hygiene check), which pinned `w27378` in about 20 min in card 125-4 (`diag_c125_joints.log:26,39`).
- Cost: a $2.44 / 425 s review (`peer_c125_2_loose_hyp.log:4,52`). The Flat Sequence creator (STEP B) never started in 125-2 (`result_125-2.json`), so the creator took three cards (125-2, 125-4, 125-5).
- Also inferred: the stub reproduction used an untyped, unwired shift register, unlike P3a. It could not reproduce P3a's case, and it cost a $1.36 review (`peer_c125_5_stub.log:4`; `diag_c125_5_stub.log:12`).

**4. Rule compliance.**
- PD242(b) was met only formally: the call count was right, the equal-state condition was dropped.
- The ≤120-line rule was broken by `diag_c125_5_opfs.py` (203 lines; `jev_gate.log:3125`, flagged as advisory only) and by `selftest_c125_1.py` (241 lines; `jev_gate.log:3103`).
- "Return at the first unexpected result" was bent in 125-1, which fixed and reran its offline measure inside the card (`c125_1_offline_measure.log:10-11`). It cost about 2 min.
- The audit's A4 FAIL entries are not this cycle's: three are chat G6 files, and `priorart-c124-6-ring-p3a.md:1234-1236` is blank from cycle 124 (its verdict was `novel`, so nothing was blocked).
- What the audit does not check:
  - whether a probe met its own acceptance conditions (A8 only checks that a RESULT line exists);
  - script length;
  - briefs that drop part of a Pre-decided item;
  - the fact that the window spans three cycles.

**5. Ordering.** Mostly defensible: gate-fp was DUE (`cycle_125.json:45-48`) and was drained first, offline. The weak point was putting the deliverable-path Flat Sequence step behind a speculative trace in the same card (125-2), so one failed prediction stalled both. PD251(d) set this order, but the trace and the creator should have been separate cards.

**6. What was not reported.**
- STATUS reports "hygiene FAIL until rerun" (`STATUS.md:59,65`). It does not say the probe was invalid by our own rule. Nor does it say this is the second hygiene-script failure in a row.
- `c125_1_probe.log:15` ended "rc=0 (NO RESULT LINE)" and was left in `tools/bench`.
- `c125_1_regress.py` has stayed red 18/3 since card 125-1, on companion files that are not real plans (`result_125-3.json`). STATUS mentions it, but as expected-red, so a real failure there would be easy to miss.

**7. Judgement inside a material session.**
- Card 125-5's material session replaced the brief's decided addressing route (`brief_125-5.md:9-10`: uid → GObject) with lookup by Traverse index plus a UID echo, and built both ops that way (`result_125-5.json` facts[0], open[2]). Judgement accepted it afterwards (PD253(a), `d1-loop12-17-split-plan.md:2615-2617`). That was a design change taken inside a material session.
- The brief also pre-scripted a branch ("If it appears: measure ONE candidate removal", `brief_125-5.md:29`). It did not fire, because the stub did not reproduce.
- In 125-1, material corrected the brief's premise about fp-10 and designed the launch ledger itself (`result_125-1.json` facts[1]). That is within a tooling brief that invited it (`brief_125-1.md:19-20`).

## Device effect
No device failed inside 18:32–19:58:
- **Inner-failure rc** (bgrun): worked. `diag_c125_5_opfs.log:75` shows rc=1 matching FAIL, and the missing RESULT line was flagged at `c125_1_probe.log:15`.
- **Confirm-bait refusal** (peer.ps1): worked. The reviews were framed "ATTACK this claim" (`c125-5-addframe-hyg.md:16`).
- **Cost-line parsing**: worked. C4b parsed 9 of 9 lines.
- **Op-hygiene record and refusal** (2026-09-28 10:37): worked. It is what stopped the faulty op from being used (`result_125-5.json` facts[3]).
- **Gate-fp queue**: worked. fp-10 to fp-13 were drained, and fp-14 was logged and drained within the cycle (`result_125-3.json`).
- **Prior-art disposition gate**: not exercised. No prior-art review was dispatched after the blank c124-6 one.
- **Census-prediction device**: not exercised in cycle 125 (no stage ran).
- **Stop-record and launch gates**: not exercised (no stage launched).

VIOLATION: repeated-failure-class | loss_min=15 | loss_usd=? | evidence=tools/bench/diag_c125_5_opfs.log:64

VERDICT {"schema":"verdict/1","id":"retrospective-cycle125","verdict":"refuted","alternative":"The +116 handles may be a real per-call leak in OpFsAddFrame_v0, in which case the rerun only confirms a FAIL; the waste is then the unreadable first probe, not a lost PASS.","discriminating_test":"Rerun AH with each round's copy closed without save, sampling h_pre/h_post/h_closed + GDI/USER (review c125-5-addframe-hyg.md:82-92); flat h_closed => harness fault confirmed.","violations":[{"slug":"repeated-failure-class","loss_min":15,"loss_usd":"?","evidence":"tools/bench/diag_c125_5_opfs.log:64"}],"sources":["tools/bench/diag_c125_5_opfs.log:64","tools/bench/diag_c125_5_opfs.py:136","tools/bench/diag_c122_hyg.py:74","tools/bench/cards/result_124-4.json:2","docs/d1-loop12-17-split-plan.md:2339","tools/bench/next.json:4"],"note":"Window spans cycles 123-125; cycle 125 = 18:32-19:58. Second candidate (125-2 inferred loose-wire count, $2.44 review) ranked below. No device failed."}

## Sources

(extract from answer)

## What was done with it

ACCEPTED (cycle 125 judgement, 2026-10-01). The fault is mine as brief writer: `brief_125-5.md:13-14` restated the
hygiene numbers but dropped PD242(b)'s equal-VI-state clause, the same class as 124-4 (an op exercised outside the
agreed harness). FINDING 2 is adopted as the device: card A of cycle 126 first builds ONE shared hygiene runner
(`gscript.hygiene_run(op, workload, recycle=True)`: wraps `hygiene_probe`, closes each copy without saving, samples
handles before/after the calls and after the close, plus GDI/USER) and runs the `OpFsAddFrame_v0` rerun THROUGH it;
later hygiene checks use only that runner. Recorded in `docs/d1-loop12-17-split-plan.md` Pre-decided 253(b) and in
STATUS.md `## NEXT`. The verdict's alternative (a real per-call leak) is exactly what the rerun's flat-or-not
`h_closed` decides; no PASS is assumed. The second candidate (125-2's inferred count) is covered by PD252(b).
