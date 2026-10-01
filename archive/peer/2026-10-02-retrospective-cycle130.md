# retrospective-cycle130

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $1.9137  in 40 / out 30555 / cache-create 115841 / cache-read 1878764  (363s, 31 turn(s))
- **date:** 2026-10-02 04:52:31
- **outcome:** ANSWERED (365s)
- **verdict-card:** VERDICT-CARD retrospective-cycle130 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle130.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle130, role retrospective) ---
CLAIM: Cycle 130 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 130 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-02 02:55:23  ..  2026-10-02 04:46:21   (111 min)
    basis: start = archive/peer/2026-10-02-retrospective-cycle129.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `inference-over-measurement` (decided 2026-10-02 01:01): code is edited while a LabVIEW card is live, retrospective-cycle121 disposition): - **`py tools/protocol.py validate <result_X.json>` prints a CLOCK line computed from files only**: the card's bind time (the newest `BOUND ... (id X)` line in `tools/bench/cards/guard_card.log`), the result file's mtime, the measured minutes between them, the result's `cost.minutes` and the task card's `budget.minut??
  - `device-failed` (decided 2026-10-02 02:57): - X10 predicts the step's peak from the COMPILED plan, across recipes: peak = start + R 횞 read + N 횞 (edit + other), with R = whole-VI reads in the recipe's checkpoint set (incl. 0 and the end) and N = ops; the coefficients come from a model file with citations (start 570 = `stage_d1_ring_p3b1_scratch_pin2.log:55`; read 2.53 and edit 0.58 = `diag_c129_6_mem.log:55,87`; other 0.8 = pin2's 3.9/op mi??

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

== cycle audit, 2026-10-02 02:55 .. 2026-10-02 04:46 (111 min, an explicit cycle window): 36 build logs, 11 peer logs, 17 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 35/36 ok; NO BGRUN line in ['motor_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 13 logs recorded a failure; unreviewed: ['wait_runner_event.log']
  FAIL  A4 every archived review says what was done with it: 14/17 annotated; blank: ['2026-10-02-hyp-c130-3-x10-selftest.md', '2026-10-02-hyp-c130-4-c128b.md', '2026-10-02-hyp-c130-4-suite-gb.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8217 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 1 log(s) with a run that printed none: ['plan_ring_p3b_split_c130_4.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 40, failure markers 13, logs carrying a failure 13
  C2 peer reviews dispatched 11, archived 17
  C3 wall-clock inside bgrun, BUILDS ONLY 96 min 17 s
  C4 wall-clock inside bgrun, REVIEWS 9 min 28 s; cost $5.6922 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 105 min 45 s  (builds 91%, reviews 8%, judgement session 0%)

  C6 material-marked recipe/bench runs 21, judgement-session attempts refused 10  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/INDEX.md [tools/bench/next.json plan.path]: 39 - STATUS.md, docs/chat-handoff.md, tools/bench/.stall_samples.txt, tools/bench/cards/brief_130-1.md, tools/bench/cards/brief_130-2.md, tools/bench/cards/brief_130-6.md, tools/bench/cards/launches.jsonl, tools/bench/diag_c106e_dryB.txt, tools/bench/diag_c130_2_baseline.py, tools/bench/diag_c130_2_md5.py, tools/bench/diag_c130_2_suite.py, tools/bench/diag_c130_5_frames.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 349/1128 ok; 779 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2665 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:111 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 682 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one
  PASS  L10 active docs stay <= 400 lines: none over the cap (5 frozen doc(s) not capped)
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1395; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 864
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  PASS  L11 frozen docs carry a FROZEN footer: 5 frozen doc(s), all with a footer

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (37; read them directly, they are the primary record) ===
tools/bench/diag_c130_2_baseline.log  (2026-10-02 03:21:55)
tools/bench/diag_c130_2_md5.log  (2026-10-02 03:40:34)
tools/bench/diag_c130_2_suite_all.log  (2026-10-02 03:39:48)
tools/bench/diag_c130_2_suite_gb.log  (2026-10-02 03:28:13)
tools/bench/diag_c130_3_wait.log  (2026-10-02 03:41:50)
tools/bench/diag_c130_4_c128b.log  (2026-10-02 03:57:16)
tools/bench/diag_c130_4_spsuite.log  (2026-10-02 03:55:24)
tools/bench/diag_c130_5_frames.log  (2026-10-02 04:12:55)
tools/bench/diag_c130_5_peek.log  (2026-10-02 04:05:05)
tools/bench/diag_c130_6_spsuite.log  (2026-10-02 04:25:42)
tools/bench/freeze_docs_d1.log  (2026-10-02 03:03:54)
tools/bench/jev_gate.log  (2026-10-02 04:46:16)
tools/bench/motor_gate.log  (2026-10-02 03:34:29)
tools/bench/motor_session_end_cycle129.log  (2026-10-02 02:59:04)
tools/bench/motor_session_start_cycle130.log  (2026-10-02 03:12:33)
tools/bench/plan_ring_p3b_split_c130_4.log  (2026-10-02 03:56:12)
tools/bench/plan_ring_p3b_split_c130_5.log  (2026-10-02 04:11:10)
tools/bench/selftest_audit_c7_d1.log  (2026-10-02 03:09:47)
tools/bench/selftest_c116a_landed_d1.log  (2026-10-02 03:09:54)
tools/bench/selftest_c130_2_peerfact.log  (2026-10-02 03:29:29)
tools/bench/selftest_c130_2_tools.log  (2026-10-02 03:27:08)
tools/bench/selftest_chat_p2_d1.log  (2026-10-02 03:09:53)
tools/bench/selftest_cycle_runner_d1.log  (2026-10-02 03:09:40)
tools/bench/selftest_doc_lint_d1.log  (2026-10-02 03:08:03)
tools/bench/selftest_dry_c130_5.log  (2026-10-02 04:08:01)
tools/bench/selftest_stage_prerun_c128b_mktrace.log  (2026-10-02 04:12:28)
tools/bench/selftest_stoprecord_c130_2.log  (2026-10-02 03:22:21)
tools/bench/selftest_x10_c130_1.log  (2026-10-02 03:22:52)
tools/bench/selftest_x10_c130_4.log  (2026-10-02 03:47:30)
tools/bench/selftest_x10_c130_5.log  (2026-10-02 04:08:20)
tools/bench/stage_d1_ring_p3b1_scratch_pin3.log  (2026-10-02 04:43:04)
tools/bench/stage_prerun_c130_5_p3b1_dry.log  (2026-10-02 04:11:57)
tools/bench/stage_prerun_c130_6_p3b1_dry.log  (2026-10-02 04:17:48)
tools/bench/stage_prerun_c130_6_p3b1_prerun.log  (2026-10-02 04:18:26)
tools/bench/stage_prerun_c130_6_p3b1_scratch_dry.log  (2026-10-02 04:17:50)
tools/bench/stage_prerun_c130_6_p3b1_scratch_prerun.log  (2026-10-02 04:18:29)
tools/bench/wait_runner_event.log  (2026-10-02 04:44:36)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (11) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/c130_2_doclint.log  (2026-10-02 03:30:16)
tools/bench/cycle_129.log  (2026-10-02 02:58:57)
tools/bench/cycle_130.log  (2026-10-02 03:12:35)
tools/bench/cycle_runner.log  (2026-10-02 03:12:35)
tools/bench/cycle_runner_main_20261001_2213.log  (2026-10-02 02:59:06)
tools/bench/cycle_runner_main_20261002_0312.log  (2026-10-02 03:12:35)
tools/bench/peer_hyp_c130_3_x10_selftest.log  (2026-10-02 03:31:05)
tools/bench/peer_hyp_c130_4_c128b.log  (2026-10-02 04:01:00)
tools/bench/peer_hyp_c130_4_suite_gb.log  (2026-10-02 03:47:10)
tools/bench/priorart_c130_6_ring_p3b1.log  (2026-10-02 04:19:53)
tools/bench/retro.log  (2026-10-02 04:46:20)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle130","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 130 (window 02:55:23 – 04:46:21)

**Window caveat.** The cycle itself began at 03:12:35 (`tools/bench/cycle_130.log:1`). The first 17 minutes of the window belong to other work, and their cost should not be counted against cycle 130:
- cycle 129's close (`motor_session_end_cycle129.log`, 02:59);
- the chat's card chat-D1 (`freeze_docs_d1.log` 03:03, the `selftest_*_d1.log` set 03:08–03:09, and the refusals at `guard_card.log:586-588`);
- the chat's own watcher crash (`wait_runner_event.log:223-227`, cp949 error at 02:58).

The audit's A3 failure is that watcher crash, not cycle 130's work. Its A1 failure (`motor_gate.log`) is fixture output from `selftest_motor_gate2` inside card 130-2's suite (`motor_gate.log:149,151`, DRY refusals). That is not a build.

**Outcome.** No new VI was produced. The X10 memory model went live with its self-test passing 9/0. P3b was re-cut to 663.4 / 664.3 MB. Scratch run pin3 stopped at op 26 on a tunnel name. The six-dispatch budget was fully used: `brief_130-6.md:4` says "This is the cycle's LAST dispatch".

## The most costly structural fault

**`guard_peer` held an unrelated offline card on a sibling card's failing log. Neither card was allowed to clear that log.**

1. Card 130-2 (gate tooling) ran its own hook suite while it was editing `protocol.py`. The run timed out: `diag_c130_2_suite_gb.log:13,28`. The review later found it was not a real result (`result_130-4.json` facts[0]).
2. 130-2's card had `peers: []` (`task_130-2.json:63`). The hook therefore refused, three times, to let it dispatch the review its log needed (`guard_card.log:591,595,598`).
3. At 03:32:22, card 130-3's rerun of the fixed X10 self-test was refused by `guard_peer`. The reason was 130-2's log, not anything 130-3 did. The session logged this as false positive fp-24 (`gate_fp_queue.jsonl:24`).
4. 130-3 then waited 8 minutes for a review that could never come (`diag_c130_3_wait.log:1-4`, "NOT FOUND after 481 s") and returned BLOCKED (`result_130-3.json`).
5. Card 130-4 had to be issued just to review 130-2's log ($1.3121, `peer_hyp_c130_4_suite_gb.log:4`). The same self-test then passed 9/0 at 03:47:30 (`selftest_x10_c130_4.log`).

The judgement session made this possible: it wrote cards 130-1 and 130-2 without `hypothesis` in their peers, against the standing rule "card `peers` = hypothesis, outcome, priorart" (`STATUS.md:99`; `task_130-1.json:72`). That omission is also why 130-1 itself came back BLOCKED (`result_130-1.json` blocked_by).

- **Loss:** about 15 minutes of wall-clock (03:32:22 to 03:47:30) and one of the six material dispatches (130-3 produced only a review that 130-1 could have dispatched itself). No log carries the material sessions' dollar cost. The only logged figure is the $1.31 review, and that review was owed anyway under rule A3, so the dollar loss is unknown.
- **Counterfactual:** suppose card 130-2 had carried `peers: ["hypothesis"]` at 03:15, or `guard_peer` had not held an offline card on a sibling's log at 03:32.
  - The X10 self-test would have passed at about 03:33 instead of 03:47.
  - Card 130-3 would not have been needed as a re-issue.
  - Pin3 would still have failed at op 26, about 15 minutes earlier.
  - One dispatch would have been left for the PD270(b) offline naming table (`docs/d1/tooling.md:46-51`). Cycle 130 would then have ended at about 05:00 with the naming rule measured, instead of 04:46 with it owed to cycle 131.

## FINDINGS

**1. Repeated failure.** Two classes recurred.
- **Tunnel names (simulator vs LabVIEW).** The simulator named a new Flat Sequence tunnel `''` where LabVIEW named it from the source. First seen at 129-4 op 33, then again in 130-5's dry run of the stale plan (`selftest_dry_c130_5.log:4`, the same sample), and then a new case at pin3 op 26 (`stage_d1_ring_p3b1_scratch_pin3.log:370`). PD265(a) said this rule was fitted to one net and that "the next scratch tests it" (`docs/d1/INDEX.md:134`). So pin3 was the planned test, and the response (build the reader next, `tooling.md:44-45`) came at the second failure, as `CLAUDE.md:480` requires. That is compliant, and not this cycle's fault.
- **`guard_peer` holds.** These hit three cards in a row: 130-1, 130-3, and 130-4's split rerun (`result_130-4.json` facts[6]). The approach should have changed when 130-3 was written at 03:26: give 130-2 the `hypothesis` peer, or stop running the gate-editing card alongside the others.

**2. Missing tool.**
- A crossing-name table built from already-recorded crossings (PD270(b)). It might have answered pin3's op-26 failure offline, although pin2's `''` rows mean no trivial rule was obviously available.
- A bounded `close_panel` in stagekit's failure path. Pin3's close hung for about 7 minutes (`pin3.log:374-394`; pin2 took about 16).

**3. Unmeasured steps.**
- The pin3 brief predicted a tunnel name for the BufNum net only (`brief_130-6.md:21-22`). The `Image Out` crossing was left to the simulator's unmeasured default.
- Timestamps were typed rather than read. Card 130-6 says "return ~04:48" and PD270 is stamped "04:5x" (`tooling.md:39`). But pin3 ended at 04:43:03 (`pin3.log:395`), and both stamps are later than this review's own window end (04:46:21). This happened in the same cycle that wired `card_clock` into `protocol validate`. I could not check whether its CLOCK line flagged it.

**4. Rule compliance.**
- The standing peers rule was broken (`STATUS.md:99`).
- Three hypothesis reviews were acted on (PD268) but never annotated (audit A4; the cards say "not annotated").
- Card 130-2 ran self-tests while it was editing the very tool they test.
- In card 130-6, `taskkill` was refused by the permission layer and LabVIEW was killed with `Stop-Process` instead (`result_130-6.json:29`). That routes around a permission refusal, even though closing LabVIEW at cycle end is required.
- `STATUS.md` is 111 lines, over the 110-line limit (L3).
- The gate-fp queue was due at cycle start (`cycle_130.log:211`). Five entries were drained, but three new ones were logged (fp-22, fp-24, fp-25).
- **What the audit does not cover:** card peers against the standing rule; typed clocks against log stamps; one card holding another; how a permission refusal was routed around; and work by the chat that falls inside the window.

**5. Ordering.** Running 130-2 (which edited `guard_peer`, `protocol.py` and `peer.ps1`) at the same time as 130-1 (which runs under those gates) was not defensible. The pipeline rule pairs one LabVIEW card with one prep card (`cycle_130.log:80`), not two offline cards where one edits the other's gates. 130-2 should have run first or alone.

**6. What was not reported.**
- STATUS says "~2 dispatches" were lost to review holds. It does not say that this used up the sixth dispatch slot, so the measured next act could not run in this cycle.
- STATUS says "LabVIEW killed". It omits that `taskkill` was denied and `Stop-Process` was used to get around it.
- The window includes about 17 minutes of chat work.

**7. Judgement inside a material session.** I found no violation.
- Card 130-3's fp-24 classification and its bounded wait follow the gate-fp card rule (`cycle_130.log:93-96`).
- Card 130-4's `x10_of` fix is implementation work inside its build step.
- The "if" lines in brief 130-6 (`:14`, `:26-27`) are time and pass gates, not choices between explanations.
- The `Stop-Process` kill (point 4) is the closest case. It is a hygiene action, not a design decision.

## DEVICE EFFECT

**One device failed: `guard_peer`'s self-test exemption (decided 2026-09-25 05:58).** In this window it refused offline commands twice:
- fp-22 at 03:21:49: it followed a function-local import into a pure-Python diagnostic (`gate_fp_queue.jsonl:22`; `result_130-2.json` facts[1]).
- fp-24 at 03:32:22: it judged the DRY X10 self-test to be LabVIEW-touching and held it on a sibling card's log (`gate_fp_queue.jsonl:24`).

Fp-16, fp-17 and fp-18, drained by 130-2 in this same cycle, were also `guard_peer` false positives. This device now fires on the wrong target often enough that working around it through the false-positive queue is routine. That is the third failure mode the contract lists.

The other devices either worked or had nothing to fire on in this window:
- **bgrun failure scan:** it forced rc=1 over a child process that exited 0 (`diag_c130_2_suite_gb.log:28`).
- **Cost-line parsing:** 4 of 4 cost lines seen were parsed (C4b).
- **Prior-art review and launch gate:** the gate refused the new recipe bytes until the prior-art review came back `novel` (`result_130-6.json` facts[3]).
- **`gates_due`:** carried on the cycle card (`cycle_130.log:211`).
- **X10 memory model:** it predicted 663.4 MB; pin3 measured 650.4 MB at op 26 (`pin3.log:369`). This is consistent so far but untested beyond op 26.
- **Unannotated-review refusal:** it only covers priorart and retrospective reviews, which is why three hypothesis reviews stayed blank.
- **Stop record:** fp-23 (the cycle-129 case) is fixed, and I found no recurrence in the window. The other half of that device, `guard_cycle.py:40` BUILD_RE, is still unbuilt because the card's write list excluded it (`result_130-2.json` facts[2]).

VIOLATION: device-failed | loss_min=15 | loss_usd=? | evidence=tools/bench/gate_fp_queue.jsonl:24

VERDICT {"schema":"verdict/1","id":"retrospective-cycle130","verdict":"refuted","alternative":"The 03:32 hold was correct by guard_peer's spec (X10 self-test import closure reaches gscript; suite_gb was a real unreviewed failing log); the loss is the judgement session's peers omission (task_130-2.json:63 vs STATUS.md:99), i.e. rule-evaded, not device-failed.","discriminating_test":"Replay the fp-24 argv (03:32:22) offline against guard_peer twice: (1) with diag_c130_2_suite_gb.log marked reviewed, (2) with only the X10 self-test classed offline. Whichever alone releases it names the cause.","violations":[{"slug":"device-failed","loss_min":15,"loss_usd":"?","evidence":"tools/bench/gate_fp_queue.jsonl:24"}],"sources":["tools/bench/gate_fp_queue.jsonl:24","tools/bench/cards/guard_card.log:591","tools/bench/diag_c130_3_wait.log:3","tools/bench/cards/result_130-3.json:1","tools/bench/cards/task_130-2.json:63","STATUS.md:99","tools/bench/cards/brief_130-6.md:4"],"note":"Device = guard_peer selftest_exempt/offline_command (decided 2026-09-25 05:58); also fp-22. Cost: 1 of 6 dispatches + ~15 min; PD270(b) slid to cycle 131. Pin3 naming FAIL was PD265(a)'s planned test, not a fault."}

## Sources

(extract from answer)

## What was done with it

- `device-failed` (guard_peer offline classification, fp-24/fp-22) ACCEPTED; the peer's alternative (card 130-2 dispatched
  with `peers: []`) ACCEPTED as a second, judgement cause. Decision appended: `docs/violation-decisions.md` "device-failed —
  2026-10-02 04:52" — cycle 131 runs the guard_peer fix as an offline card beside the deliverable's offline card; cards that
  edit hooks or run suites carry the `hypothesis` peer.
- The pin3 naming FAIL is PD270 (`docs/d1/tooling.md:39`): the rule is measured from every recorded crossing before a third
  scratch run. X10's 650.4 MB at op 26 vs 663.4 predicted is recorded in PD270(d); it is tested in full only by pin4.
- Three hypothesis reviews left unannotated (c130-3, c130-4 ×2): their findings were acted on in PD268(b)(c) (dry
  completeness, c128b re-pin) and in card 130-5.
