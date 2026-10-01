# retrospective-cycle128

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $1.9024  in 38 / out 30383 / cache-create 116920 / cache-read 1796337  (320s, 34 turn(s))
- **date:** 2026-10-02 00:56:06
- **outcome:** ANSWERED (322s)
- **verdict-card:** VERDICT-CARD retrospective-cycle128 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle128.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle128, role retrospective) ---
CLAIM: Cycle 128 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 128 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-01 23:46:14  ..  2026-10-02 00:50:39   (64 min)
    basis: start = archive/peer/2026-10-01-retrospective-cycle127.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `repeated-failure-class` (decided 2026-10-01 20:12): `gscript.hygiene_run(op, workload, recycle=True)` that wraps `hygiene_probe`, closes every VI copy without saving at a fixed call count, and records handles before the calls, after the calls and after the close, plus GDI/USER counts, at the SAME VI state. Every later op hygiene check goes through it only; a brief for one quotes PD242(b)'s equal-state clause verbatim. - Acceptance: a self-test show??

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

== cycle audit, 2026-10-01 23:46 .. 2026-10-02 00:50 (64 min, an explicit cycle window): 36 build logs, 12 peer logs, 35 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 20/36 ok; NO BGRUN line in ['c125_1_offline_measure_c128_4.log', 'selftest_c128_4_case_frame_c124.log', 'selftest_c128_4_census_predict.log', 'selftest_c128_4_stage_prerun_c103.log', 'selftest_c128_4_stage_prerun_c106c.log', 'selftest_c128_4_stage_prerun_c106e.log', 'selftest_c128_4_stage_prerun_c110g.log', 'selftest_c128_4_stage_prerun_c114.log', 'selftest_c128_4_stage_prerun_c114d.log', 'selftest_c128_4_stage_prerun_c115a.log', 'selftest_c128_4_stage_prerun_c115c.log', 'selftest_c128_4_stage_prerun_c128.log', 'selftest_c128_4_stage_prerun_c128b.log', 'selftest_c128_4_stage_prerun_graphload.log', 'selftest_c128_4_stage_prerun_headcmp_79-6.log', 'selftest_c128_4_stage_prerun_stageplan.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 8 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 30/35 annotated; blank: ['2026-10-01-g6-call-a-gemini.md', '2026-10-01-g6-call-b-claude.md', '2026-10-01-g6-call-b-gemini.md', '2026-10-01-outcome-review-20261001.md', '2026-10-01-priorart-c124-6-ring-p3a.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8217 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  PASS  A8 recipe/bench runs ended with a RESULT line (C6): every scoped run in the window printed one (or predates the mark)
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 20, failure markers 34, logs carrying a failure 8
  C2 peer reviews dispatched 12, archived 35
  C3 wall-clock inside bgrun, BUILDS ONLY 20 min 44 s
  C4 wall-clock inside bgrun, REVIEWS 18 min 27 s; cost $12.8730 from 7 log(s) that report one
  C4b cost lines seen 7 / parsed 7
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 54 min 18 s; cost $26.4525 from 1 log(s) - cycle_128.log
  C5 total wall-clock 93 min 29 s  (builds 22%, reviews 19%, judgement session 58%)

  C6 material-marked recipe/bench runs 15, judgement-session attempts refused 2  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 46 - docs/chat-handoff.md, tools/bench/.stall_samples.txt, tools/bench/cards/brief_128-2.md, tools/bench/cards/brief_128-3.md, tools/bench/cards/brief_128-4.md, tools/bench/diag_c128_1_checks.py, tools/bench/diag_c128_2_bedcensus.py, tools/bench/diag_c128_2_donors.py, tools/bench/diag_c128_3_x5.py, tools/bench/diag_c128_4_checks.py, tools/bench/errorlist_shots/001841_before_ctrl_e.png, tools/bench/errorlist_shots/001845_after_ctrl_e.png??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 345/1113 ok; 768 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2586 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:113 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  WARN  L5 superseded documents are not still current: docs/ring-buffer-design.md supersedes docs/d1-build-plan.md, which is still `status: current`
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 661 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one

AUDIT VIOLATIONS: A1 every build log came from bgrun, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (37; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure_c128_1.log  (2026-10-02 00:06:06)
tools/bench/c125_1_offline_measure_c128_4.log  (2026-10-02 00:37:11)
tools/bench/diag_c128_1_checks.log  (2026-10-02 00:09:08)
tools/bench/diag_c128_1_selftest.log  (2026-10-02 00:03:44)
tools/bench/diag_c128_1_stagesim_selftest.log  (2026-10-02 00:04:43)
tools/bench/diag_c128_2_bedcensus.log  (2026-10-02 00:02:49)
tools/bench/diag_c128_2_bedcensus_run2.log  (2026-10-02 00:07:49)
tools/bench/diag_c128_2_donors.log  (2026-10-02 00:21:07)
tools/bench/diag_c128_2_dry.log  (2026-10-02 00:07:50)
tools/bench/diag_c128_2_prerun.log  (2026-10-02 00:08:07)
tools/bench/diag_c128_2_prerun2.log  (2026-10-02 00:09:48)
tools/bench/diag_c128_3_recipe_dry.log  (2026-10-02 00:14:14)
tools/bench/diag_c128_3_x5.log  (2026-10-02 00:19:00)
tools/bench/diag_c128_4_checks.log  (2026-10-02 00:37:11)
tools/bench/jev_gate.log  (2026-10-02 00:50:25)
tools/bench/motor_session_end_cycle127.log  (2026-10-01 23:51:53)
tools/bench/motor_session_start_cycle128.log  (2026-10-01 23:52:01)
tools/bench/plan_ring_p3b_make_c128_5.log  (2026-10-02 00:48:28)
tools/bench/selftest_c128_4_case_frame_c124.log  (2026-10-02 00:35:48)
tools/bench/selftest_c128_4_census_predict.log  (2026-10-02 00:34:38)
tools/bench/selftest_c128_4_stage_prerun_c103.log  (2026-10-02 00:33:23)
tools/bench/selftest_c128_4_stage_prerun_c106c.log  (2026-10-02 00:33:34)
tools/bench/selftest_c128_4_stage_prerun_c106e.log  (2026-10-02 00:33:59)
tools/bench/selftest_c128_4_stage_prerun_c110g.log  (2026-10-02 00:33:34)
tools/bench/selftest_c128_4_stage_prerun_c114.log  (2026-10-02 00:33:53)
tools/bench/selftest_c128_4_stage_prerun_c114d.log  (2026-10-02 00:33:55)
tools/bench/selftest_c128_4_stage_prerun_c115a.log  (2026-10-02 00:33:59)
tools/bench/selftest_c128_4_stage_prerun_c115c.log  (2026-10-02 00:34:14)
tools/bench/selftest_c128_4_stage_prerun_c128.log  (2026-10-02 00:34:12)
tools/bench/selftest_c128_4_stage_prerun_c128b.log  (2026-10-02 00:35:48)
tools/bench/selftest_c128_4_stage_prerun_graphload.log  (2026-10-02 00:34:15)
tools/bench/selftest_c128_4_stage_prerun_headcmp_79-6.log  (2026-10-02 00:34:21)
tools/bench/selftest_c128_4_stage_prerun_stageplan.log  (2026-10-02 00:34:37)
tools/bench/selftest_stage_prerun_c128.log  (2026-10-02 00:17:38)
tools/bench/selftest_stage_prerun_c128b.log  (2026-10-02 00:29:49)
tools/bench/selftest_stagesim_c128_5.log  (2026-10-02 00:44:07)
tools/bench/selftest_stagexec_c128_5.log  (2026-10-02 00:44:54)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (12) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_127.log  (2026-10-01 23:51:45)
tools/bench/cycle_128.log  (2026-10-02 00:50:38)
tools/bench/cycle_runner.log  (2026-10-01 23:56:21)
tools/bench/cycle_runner_main_20261001_2213.log  (2026-10-01 23:56:21)
tools/bench/outcome_review_cycle128.log  (2026-10-01 23:56:21)
tools/bench/peer_c128_1_errsel.log  (2026-10-02 00:02:09)
tools/bench/peer_c128_2_bedcensus.log  (2026-10-02 00:06:16)
tools/bench/peer_c128_2_errsel.log  (2026-10-02 00:06:27)
tools/bench/peer_c128_3_x5.log  (2026-10-02 00:17:00)
tools/bench/peer_c128_4_c106e.log  (2026-10-02 00:39:33)
tools/bench/peer_c128_4_c2frame0.log  (2026-10-02 00:27:19)
tools/bench/retro.log  (2026-10-02 00:50:39)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle128","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 128 (window 2026-10-01 23:46:14 – 2026-10-02 00:50:39)

**The cycle.** The judgement session ran from 23:56:21 to about 00:50 (`tools/bench/cycle_128.log:1,211`) and cost $26.45. It ran five cards, and all five came back FAIL:

| Card | Kind | Bound at (`guard_card.log`) | Returned by | Claimed minutes |
|---|---|---|---|---|
| 128-1 | offline | 00:00:06 (:570) | about 00:09 | 16 |
| 128-2 | LabVIEW | 00:00:07 (:571) | about 00:21 | 30 |
| 128-3 | offline | 00:12:05 (:573) | about 00:20 | 24 |
| 128-4 | offline | 00:24:43 (:574) | about 00:40 | 50 |
| 128-5 | offline | 00:41:33 (:575) | about 00:49 | 45 |

- No VI was saved and no stage was launched.
- What the cycle did produce was real: the guard's donor nodes were found (`diag_c128_2_donors.log:29-38`), a gate false positive (fp-19, check X5) was fixed with a self-test, `name#k` addressing for repeated terminal names was built, and a 70-action P3b plan input now replays end to end.
- Cycle 129 still has to split that plan, write the recipes and prior-art review it, before the one LabVIEW launch.

## The structural fault: `inference-over-measurement` (card 128-5 was not out of budget)

**What happened**
- Card 128-5 returned FAIL with `first_fail: "budget: 50-min card budget spent after pass criteria 1-2"` and `minutes: 45` (`tools/bench/cards/result_128-5.json:2,26`).
- The logs say otherwise:
  - The card bound at 00:41:33 (`guard_card.log:575`).
  - It could not have started before 128-4's last review ended at 00:39:33 (`peer_c128_4_c106e.log:25`).
  - Its last work ended at 00:48:28 (`plan_ring_p3b_make_c128_5.log`).
  - The judgement session was already starting the retrospective at 00:50:25 (`jev_gate.log:3317`).
- So the card ran 8 to 11 minutes of its 50 and then stopped, leaving pass items 3–5 undone: the split, the recipes, dry + prerun, the prior-art review, the c106e rerun and the fp-19 drain.
- The judgement session took the claim at face value. Its PD263 header reads "card budget spent" (`docs/d1-loop12-17-split-plan.md:2877`), STATUS repeats "(budget)" (`STATUS.md:61`), and the session closed the cycle.
- Checking the claim would have cost nothing. The bind time sits in the same `guard_card.log` the session's own hooks write. The runner prompt also says never to infer an outcome from wording (`cycle_128.log:17-18`).

**What it cost**
- About 42 minutes of card budget went unused (50 minus about 8), so the plan's remainder moves to cycle 129.
- That remainder is exactly the next cycle's card 1 (`STATUS.md:56`), so cycle 129 again opens on an offline card instead of the deliverable launch.
- The steering card (`steer_127.json:12`) asks for that launch.
- The session stopped with about 126 of its 180 minutes and one of its six dispatches still unused (5 sub-agents were spawned, `cycle_128.log:210`).
- No log records a dollar figure for this, so the dollar loss is unknown.

**Counterfactual**
- At about 00:49 the session could have compared `result_128-5.json:2` with `guard_card.log:575`. It could then have re-dispatched the remainder (or sent 128-5 back) as its sixth and last dispatch.
- The work involved is a split, two recipes, offline dry and prerun runs (seconds each), and a prior-art review (about 10 minutes).
- The cycle would then have ended at about 01:35 with P3b-1 ready to launch, instead of at 00:50 without it. Cycle 129 would have opened with the LabVIEW scratch run and the one launch.

**Slug.** I filed this as `inference-over-measurement`: the decision to stop was made on a stated budget when a measured one was available. It could also be read as `unreported-fact`, because a false fact reached PD263 and STATUS. I see no second fault of the same size.

## Findings

**1. Repeated failure**
- The X5 refusal mixed two problems:
  - A real false positive: the pattern at `stage_prerun.py:109` counts `wire_remove_loose_ends` but the plan-side count at `:901` does not, giving 41 against 26.
  - A test-harness artefact that tripled the count: 128-1 ran `--dry` and `--prerun` in one process (`diag_c128_3_x5.log:12`).
- The same harness also caused the "pred file NOT written" fault, because the replaced `open` was never restored (`result_128-1.json:21`).
- Both are the same class: hidden module state in `stage_prerun`. The approach should have changed at attempt 1. 128-1 should have run its checks out of process, which brief 128-4 later made the rule.
- Fixing one defect per card came back:
  - 128-1 found the X5 false positive.
  - 128-4 found that the new Unbundler's three outputs all read `element` (`result_128-4.json:23-24`).
  - 128-5 then built `name#k`.
- Cycle 127's disposition had promised to audit every row at once (`retrospective-cycle127.md:377-378`).

**2. Missing tool**
- No check compares the minutes a card claims with its bind and return times.
- That check would have caught 128-5's false budget claim and the inflated minutes on every card. For example, 128-4 claims 50 minutes for about 15 actual (`guard_card.log:574` to `peer_c128_4_c106e.log:25`).
- The time-budget prerun check from cycle 127 is also still unbuilt (`retrospective-cycle127.md:379`).

**3. Unmeasured steps**
- The fault above.
- Brief 128-4 §3 said terminal names would come "from 128-2's measured rows only" (`brief_128-4.md:24`). Those rows already showed all three outputs named `element` (`diag_c128_2_donors.log:57,83`, written about 00:21). The brief was written about 00:24 without reading them, so the binder gap cost a card round-trip.

**4. Rule compliance**
- **Time arithmetic in briefs.** The cycle-127 disposition says "every brief I write from cycle 128 states its time arithmetic" (`retrospective-cycle127.md:372-373`).
  - Only `brief_128-2.md:44-46` does.
  - `brief_128-3.md` and `brief_128-4.md` do not; brief 128-4 packs five sections into 55 minutes.
  - Card 128-5 has no brief at all.
- **120-line limit.** `diag_c128_2_donors.py` is 124 lines (limit at `STATUS.md:106`).
- **Retrospective last.** This was satisfied, but not by the session: its `retro_due` and `retrospective` commands were permission-denied (`cycle_128.log:210`), and the runner ran the retrospective afterwards (`retro.log:5442`).
- **What the audit does not cover:**
  - A1 flags 16 child self-test logs that ran inside the bgrun of `diag_c128_4_checks` (rc=1 at `:23`).
  - A3 is met by any later archived review. The M1 failure in `diag_c128_3_x5.log:10` was the card's own arithmetic slip (42 against 41), and no review addresses it.
  - A4 lists blank reviews from earlier days.
  - C6 calls `material_marker.log:2975,2977` "judgement-session attempts", but both were material commands.
  - C7's 46 files include the cycle's own briefs.
  - Nothing checks claimed card minutes or brief time arithmetic.

**5. Ordering**
- Running 128-1 and 128-2 in parallel was sound.
- But both inherited guard_peer's debt on 127-5, so two reviews attacked the same claim: `peer_c128_1_errsel.log:4` ($1.01) and `peer_c128_2_errsel.log:4` ($2.63).
- The binder limit should have been checked before 128-4 was briefed (Finding 3).

**6. What was not reported**
- 128-5's false budget claim.
- Inflated `minutes` on every result card.
- `selftest_stage_prerun_c106e` has been red since X16 was added in cycle 125 (`result_128-4.json:22`). Three cycles passed it unnoticed.
- The session's final message says "The retrospective is running in the background. I'll stay in this turn", yet the command was denied and the turn ended (`cycle_128.log:210`).
- The plan md5 in `next.json:6` was not recomputed by the session, because its hash command was denied (same line).

**7. Judgement inside a material session**
- 128-5's material session decided to stop with about 40 minutes left (`result_128-5.json:2`).
- Brief 128-2 handed the annotation of a review to the material session (`brief_128-2.md:13`, "Wait for ANSWERED, archive, annotate"). That review's annotation, which accepts its finding, was written there (`result_128-2.json:17`). Judgement only ratified it afterwards, in PD261(a).
- Brief 128-3's Step 0 is the sanctioned Jev-ladder "if review owed, dispatch" step, so it is not counted.

## Device effect

No listed device let its own fault through inside the window.
- **Working:**
  - Inner-failure rc: the failing diagnostics ended rc=1 (`diag_c128_1_checks.log:42`, `diag_c128_4_checks.log:23`).
  - Cost-line parsing: 7 seen, 7 parsed.
  - `gates_due` (`cycle_128.json:31-52`).
  - The prerun gate refused a recipe launch under an offline card (`material_marker.log:2975`).
- **Not exercised:** the stop record, the prior-art gate, the memory prediction and `hygiene_run`.
- **Near misses that are not failures:**
  - `BGRUN STAGE-RUN ... card=None` again (`diag_c128_2_donors.log:3`); the run was still counted.
  - guard_peer held 128-2 for about 3 minutes on an offline card's log, a known carry from cycle 122.
  - The census-prediction device reported CENSUS-UNPREDICTED, and PD261(c) replaced it with the mandatory scratch measurement. No prediction was typed by inference.

VIOLATION: inference-over-measurement | loss_min=42 | loss_usd=? | evidence=tools/bench/cards/result_128-5.json:2

VERDICT {"schema":"verdict/1","id":"retrospective-cycle128","verdict":"refuted","alternative":"128-5's 'budget spent' was a unit error (agent counted from an earlier spawn or a token budget), and the session would have closed anyway to keep P3b-1's remainder and launch in one cycle under the 6-dispatch cap.","discriminating_test":"Compare 128-5's first tool timestamp in its agent transcript with result_128-5.json's write time: a start >=00:39:33 and a return <=00:50 means <=11 of 50 min used, so the stop was unforced.","violations":[{"slug":"inference-over-measurement","loss_min":42,"loss_usd":"?","evidence":"tools/bench/cards/result_128-5.json:2"}],"sources":["tools/bench/cards/result_128-5.json:2","tools/bench/cards/guard_card.log:575","tools/bench/peer_c128_4_c106e.log:25","tools/bench/jev_gate.log:3317","docs/d1-loop12-17-split-plan.md:2877","STATUS.md:61","tools/bench/cycle_128.log:210"],"note":"Card 128-5 claimed its 50-min budget spent after ~8-11 min (bound 00:41:33); judgement accepted it and closed at 00:50 with 1 dispatch and ~126 min left, deferring split/recipes/dry/prerun/prior-art to cycle 129. No listed device failed."}

## Sources

(extract from answer)

## What was done with it

(cycle 129 judgement, 2026-10-02 01:0x)
- **ACCEPTED: `inference-over-measurement`**, re-measured first: 128-5 bound 00:41:33 (`tools/bench/cards/guard_card.log:575`),
  result written 00:49:02 (mtime) — about 8 of 50 minutes against a claimed 45 and "budget spent". The verdict's alternative
  (a unit error, and a session that would have closed anyway) does not survive the two timestamps: the stop was unforced.
  Device decided in `docs/violation-decisions.md` (2026-10-02 01:01): `protocol.py validate` prints a CLOCK line from the
  bind line and the result mtime and fails a result whose budget/minutes claim the files contradict. Built in this cycle's
  offline tooling card, after the P3b-1 LabVIEW card returns.
- The unfinished remainder of 128-5 is cycle 129's first card (129-1: split, finalize, predictions, recipes, dry + prerun,
  prior-art), then 129-2 (P3b-1 scratch run + ONE launch), as PD263(b) orders.
- Finding 4 (time arithmetic): every cycle-129 brief opens with its time arithmetic.
- Finding 6 (`selftest_stage_prerun_c106e` red since cycle 125): the c106e E1 rerun listing every FAIL line and the fp-19 /
  fp-20 drains go into the gate-fp tooling card (the queue is DUE: 6 open).
- Finding 7 (a review's annotation written inside a material session, `brief_128-2.md:13`): from cycle 129 a material session
  dispatches a review and returns its verdict; the annotation and any `REFUTED:` / `FIXED:` release lines are written by the
  judgement session.
- Finding 2's other half (a time-budget prerun check; `Stage(deadline_min)` stopping nothing) stays tooling debt, not built now.
