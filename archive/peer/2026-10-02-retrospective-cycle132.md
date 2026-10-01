# retrospective-cycle132

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.7157  in 44 / out 33042 / cache-create 187903 / cache-read 2757245  (336s, 40 turn(s))
- **date:** 2026-10-02 08:09:54
- **outcome:** ANSWERED (338s)
- **verdict-card:** VERDICT-CARD retrospective-cycle132 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle132.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle132, role retrospective) ---
CLAIM: Cycle 132 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 132 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-02 06:50:33  ..  2026-10-02 08:04:11   (74 min)
    basis: start = archive/peer/2026-10-02-retrospective-cycle131.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-10-02 04:52): card (pipeline, two live offline cards, disjoint write lists; deliverable-first holds because the deliverable card is dispatched in the same message): - A command is OFFLINE when every module it runs is in `protocol.OFFLINE_SELFTESTS` or is a stage_prerun `--dry`/`--prerun`/ self-test whose COM is stubbed; an import that merely REACHES `gscript` without calling COM does not make it LabVIEW-touchin??

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

== cycle audit, 2026-10-02 06:50 .. 2026-10-02 08:04 (74 min, an explicit cycle window): 44 build logs, 5 peer logs, 22 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 44/44 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 13 logs recorded a failure; unreviewed: ['diag_c132_2_graph_p3b1_dry.log', 'diag_c132_2_graph_p3b1_prerun.log', 'selftest_namegate_c132_1.log', 'selftest_rebase_c132_6.log', 'selftest_rebind_c132_5.log', 'selftest_rebind_c132_6.log', 'selftest_stage_prerun_c106e_c132_1.log', 'stagesim_c132_6_recover_p3b2.log', 'stage_prerun_c132_1_p3b2_dry.log', 'stage_prerun_c132_4_rebase_p3b2.log', 'stage_prerun_c132_5_rebase_p3b2.log', 'stage_prerun_c132_6_rebase_p3b2.log', 'wait_runner_event.log']
  FAIL  A4 every archived review says what was done with it: 19/22 annotated; blank: ['2026-10-02-hyp-c130-3-x10-selftest.md', '2026-10-02-hyp-c130-4-c128b.md', '2026-10-02-hyp-c130-4-suite-gb.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8604 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['diag_c132_6_actions.log', 'diag_c132_6_fsmap.log', 'diag_c132_6_fspairs.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 58, failure markers 13, logs carrying a failure 13
  C2 peer reviews dispatched 5, archived 22
  C3 wall-clock inside bgrun, BUILDS ONLY 80 min 23 s
  C4 wall-clock inside bgrun, REVIEWS 0 min 0 s; no log reported a cost - treat the review cost as UNKNOWN, not as zero
  C4b cost lines seen 0 / parsed 0
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 80 min 23 s  (builds 100%, reviews 0%, judgement session 0%)

  C6 material-marked recipe/bench runs 26, judgement-session attempts refused 3  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/INDEX.md [tools/bench/next.json plan.path]: 41 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/cards/brief_132-1.md, tools/bench/cards/brief_132-2.md, tools/bench/cards/launches.jsonl, tools/bench/diag_c106e_dryB.txt, tools/bench/diag_c131_5_stubs.py, tools/bench/diag_c132_1_fp21.py, tools/bench/diag_c132_1_lost.py, tools/bench/diag_c132_1_m1.py, tools/bench/diag_c132_1_peek.py, tools/bench/diag_c132_1_steps.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 349/1133 ok; 784 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2667 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:121 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 683 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one
  PASS  L10 active docs stay <= 400 lines: none over the cap (5 frozen doc(s) not capped)
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1395; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 864
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  PASS  L11 frozen docs carry a FROZEN footer: 5 frozen doc(s), all with a footer

AUDIT VIOLATIONS: A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (45; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure_c132_1.log  (2026-10-02 07:11:20)
tools/bench/diag_c132_1_fp21.log  (2026-10-02 07:07:31)
tools/bench/diag_c132_1_lost.log  (2026-10-02 07:03:56)
tools/bench/diag_c132_1_m1.log  (2026-10-02 07:01:01)
tools/bench/diag_c132_1_peek.log  (2026-10-02 07:06:50)
tools/bench/diag_c132_1_steps_p3b1.log  (2026-10-02 07:01:36)
tools/bench/diag_c132_1_suite.log  (2026-10-02 07:18:19)
tools/bench/diag_c132_2_graph_p3b1.log  (2026-10-02 07:35:13)
tools/bench/diag_c132_2_graph_p3b1_dry.log  (2026-10-02 07:22:13)
tools/bench/diag_c132_2_graph_p3b1_prerun.log  (2026-10-02 07:22:27)
tools/bench/diag_c132_4_diff.log  (2026-10-02 07:35:57)
tools/bench/diag_c132_4_graph_p3b1_dry.log  (2026-10-02 07:30:27)
tools/bench/diag_c132_4_graph_p3b1_prerun.log  (2026-10-02 07:31:11)
tools/bench/diag_c132_4_rebind_keys.log  (2026-10-02 07:36:58)
tools/bench/diag_c132_5_frames.log  (2026-10-02 07:41:40)
tools/bench/diag_c132_5_rows.log  (2026-10-02 07:40:41)
tools/bench/diag_c132_5_unbound.log  (2026-10-02 07:46:19)
tools/bench/diag_c132_6_actions.log  (2026-10-02 08:01:11)
tools/bench/diag_c132_6_fsmap.log  (2026-10-02 07:52:01)
tools/bench/diag_c132_6_fspairs.log  (2026-10-02 07:58:44)
tools/bench/errorlist_expect_p3b2.log  (2026-10-02 07:04:56)
tools/bench/jev_gate.log  (2026-10-02 08:04:07)
tools/bench/motor_session_end_cycle131.log  (2026-10-02 06:51:34)
tools/bench/motor_session_start_cycle132.log  (2026-10-02 06:51:42)
tools/bench/selftest_chat_p1_c132_5.log  (2026-10-02 07:47:07)
tools/bench/selftest_chat_p1_c132_6.log  (2026-10-02 07:59:45)
tools/bench/selftest_namegate_c132_1.log  (2026-10-02 07:02:40)
tools/bench/selftest_rebase_c132_6.log  (2026-10-02 07:59:23)
tools/bench/selftest_rebase_c132_6_r2.log  (2026-10-02 08:01:30)
tools/bench/selftest_rebind_c132_5.log  (2026-10-02 07:46:50)
tools/bench/selftest_rebind_c132_6.log  (2026-10-02 07:59:39)
tools/bench/selftest_stage_prerun_c106c_c132_4.log  (2026-10-02 07:31:38)
tools/bench/selftest_stage_prerun_c106e_c132_1.log  (2026-10-02 07:07:14)
tools/bench/selftest_stage_prerun_c106e_c132_4.log  (2026-10-02 07:29:39)
tools/bench/selftest_x10_c130_1_c132.log  (2026-10-02 06:56:48)
tools/bench/selftest_x10_c130_1_r4.log  (2026-10-02 07:29:02)
tools/bench/selftest_x10_c132_1.log  (2026-10-02 06:56:42)
tools/bench/selftest_x10_c132_1_r4.log  (2026-10-02 07:28:55)
tools/bench/selftest_x10_c132_4.log  (2026-10-02 07:28:36)
tools/bench/stage_prerun_c132_1_p3b2_dry.log  (2026-10-02 07:08:29)
tools/bench/stage_prerun_c132_4_rebase_p3b2.log  (2026-10-02 07:36:18)
tools/bench/stage_prerun_c132_5_rebase_p3b2.log  (2026-10-02 07:47:42)
tools/bench/stage_prerun_c132_6_rebase_p3b2.log  (2026-10-02 08:00:40)
tools/bench/stagesim_c132_6_recover_p3b2.log  (2026-10-02 07:55:28)
tools/bench/wait_runner_event.log  (2026-10-02 07:58:25)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (5) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_131.log  (2026-10-02 06:51:27)
tools/bench/cycle_132.log  (2026-10-02 06:51:43)
tools/bench/cycle_runner.log  (2026-10-02 06:51:43)
tools/bench/cycle_runner_main_20261002_0312.log  (2026-10-02 06:51:43)
tools/bench/retro.log  (2026-10-02 08:04:10)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle132","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 132 (06:50:33 – 08:04:11)

**What it produced:** no new VI, and P3b-2 was never dry-run. The cycle used all six material dispatches (`tools/bench/cards/guard_card.log:610-615`), ending at 08:03 with 106 of its 180 budget minutes unused. The limit it hit was dispatches, not time. It did leave six self-tested tool changes and one real graph read of the P3b-1 bed.

## The most costly structural fault: two of six dispatches spent on BLOCKED cards (wrong-ordering)

The plan made at cycle start (PD275, `docs/d1/tooling.md:74-89`) dispatched two cards together at 06:54:31:
- **Card 132-1** (offline) was editing `tools/stage_prerun.py`, including the memory gate X10 (`x10_gate`).
- **Card 132-2** (LabVIEW) was to read the bed's graph. That reader is itself launch-gated by `stage_prerun --dry/--prerun`, because it calls `discard_work`.

The 132-2 brief forbade running `stage_prerun` (`tools/bench/cards/brief_132-2.md:5`). The launch was refused at 06:56:41 (`tools/hooks/material_marker.log:3045`) and the card returned BLOCKED (`tools/bench/cards/result_132-2.json:1`). The judgement session admitted this was its own rule (`docs/d1/tooling.md:101-102`). The template it named already showed the reader needs a prerun record (`tools/bench/diag_c125_graph_p3a_prerun.log`, cited in `result_132-2.json`).

The re-issue, card 132-3, was then refused by X10 itself. Since PD268(a), X10 treats any script with no Executor plan as UNMEASURED and fails it. The judgement session's own cycle-130 rule had broken the read-only reader (`tools/bench/diag_c132_2_graph_p3b1_prerun.log:21,25`, logged as gate false positive fp-29). Card 132-1 was editing that same `x10_gate` function at that very hour.

- **Loss:** 4 + 5 = 9 card-minutes (`result_132-2.json`, `result_132-3.json`, `cost.minutes`). The real cost is two of the cycle's six dispatch slots. No log carries a dollar figure: audit line C4b shows 0 cost lines seen.
- **Counterfactual:** at ~06:53, put the reader exemption into 132-1's part A and dispatch the graph read after 132-1 returned (~07:17). Card 132-4's chain would then have started about 07:17 as the third dispatch, and 132-4/-5/-6 would have finished by about 07:56 with two dispatches left. Those two would have gone to the route-check binding card (now cycle 133's first act, `STATUS.md:57`) and P3b-2's dry/prerun. The cycle would have ended about 08:20 with P3b-2 dry-checked, instead of at 08:03 stuck on the op-24 gap.

## FINDINGS

**1. Repeated failure.** The rebase stopped three times: name keys (`stage_prerun_c132_4_rebase_p3b2.log:3`), the Flat Sequence frame map (`stage_prerun_c132_5_rebase_p3b2.log:35-36`), and route-check binding (`stage_prerun_c132_6_rebase_p3b2.log:76`). PD280(b) calls these three different gaps, and the fixes support that: each was separate code with its own self-test.
- The third stop is close kin to fp-21, which has been open since cycle 129. Both are the "unbound" check in `stagexec.compare` (`tools/stagexec.py:786`) finding negative (simulator-made) object ids with no real binding.
- PD276(b) had declared fp-21 "NOT on P3b-2's path". By attempt 3 (card 132-6) the binding of simulator-created objects should have been treated as one class.
- The route check stops at op 24. Ops 26–38 are also wire connections and were never route-checked, so cycle 133 may find another gap behind this one.

**2. Missing tool.** `--rebase` had never been run end to end across a Flat Sequence created by the previous stage before the cycle depended on it. A rebase against P3b-1's simulator end graph, converted to the real-graph shape, would have surfaced the frame-map and route-check gaps without LabVIEW. Its absence is why the gaps arrived one dispatch at a time.

**3. Unmeasured steps.**
- **Memory model start term.** The brief asked for the memory after loading P3b-1 "so X10's base term… is measured" (`brief_132-2.md:11-12`). It was measured at 584.1 MB (`diag_c132_2_graph_p3b1.log:24`), but `memory_model.json:6` still uses 570.0, which was measured with P3a as the base. That is 14.1 MB higher, and P3b-2's predicted peak is 681.7 MB against a 690 MB limit, a margin of 8.3 MB. Nothing recomputed the prediction.
- **X10 under-predicted the reader.** Predicted peak 592.5 MB (`diag_c132_4_graph_p3b1_prerun.log:21`) against 599.9 MB measured (`diag_c132_2_graph_p3b1.log:271`).
- **PD280(c)'s question is half answered already.** It asks whether the "unbound" refusal predates card 132-1's edit. For the dry path it does: cycle 129 shows the same BASE-unbound refusal (`stage_prerun_c129_1_p3b2_dry.log:23`). The simulator's finalize path is different: it finalized b25c1ecb in cycle 131 but refused at 07:54 (`stagesim_c132_6_recover_p3b2.log:42`). That points to a regression inside this cycle, from 132-1's `stagexec` edit or 132-6's `stagesim` edit.

**4. Rule compliance.**
- **Failed-prediction reviews.** Audit check A3 fails: 13 failing logs, and none has a hypothesis review or a Jev-ladder (failure-triage) row (`jev_gate.log` has only preflight and drift lines for c132). Several are red-to-green self-test iterations, but three rebase runs and the recovery run were real failed predictions. The judgement session decided each one from result cards alone.
- **Check skipped to avoid a failing log.** Card 132-1 did not rerun `diag_c131_5_stubs.py` because it "would write a FAIL log" (`result_132-1.json:24`). Choosing not to run a check because it would fail evades the rule.
- **Audit check A4** (blank dispositions) concerns cycle-130 reviews, not this cycle.
- **What the audit does not cover:** dispatch-slot waste, briefs that contradict a gate, and model coefficients left stale after a fresh measurement.

**5. Ordering.** Draining the gate-false-positive queue first was required (`cycle_132.json:45-47`). Running the gate edit in parallel with a card that needs that gate was not defensible (see the fault above).

**6. Not reported.**
- STATUS says P3b-2 was "recovered 98992a59". The recovery's own finalize was REFUSED, so the plan is final=false (`stagesim_c132_6_recover_p3b2.log:42-44`).
- 132-5's failed rebase destroyed b25c1ecb, which is in neither the working tree nor git (`result_132-5.json:20`).
- The 584.1 MB reading against the model's 570 start term (point 3).

**7. Judgement inside material sessions.** Card 132-1 made several judgement calls itself:
- It narrowed the tunnel-name gate to Flat Sequence border crossings after finding the inner-tunnel naming mismatch (`result_132-1.json:21`).
- It re-pinned the c106e test's E1 expectation to the new X10 (`result_132-1.json:25`).
- It decided not to rerun the stubs check (point 4).

The first two were surfaced as open questions and ratified in PD276(a), so they are minor. Card 132-2 also decided on its own that its refusal was "the gate working as designed" and logged no false positive (`result_132-2.json:1`); that happened to be correct.

## DEVICE EFFECT

No device's target fault occurred in the window:
- **X10 (decided 02:57).** No stage was launched, and the reader stayed under 690 MB. Its one false positive, fp-29, was queued and fixed with a 6/0 self-test within 30 minutes. That is not "routinely bypassed".
- **Offline-command and stop-record exemptions (04:52 and earlier).** `stage_prerun --dry/--prerun` on the reader ran (`diag_c132_2_graph_p3b1_dry.log`). The 07:51:42 refusal (`material_marker.log:3066`) was a foreground diagnostic outside the background runner, re-run under it 7 seconds later.
- **Runner exit-code check.** `rc` matched the FAIL lines in every rebase and self-test log checked.
- **Fresh agent per dispatch (instead of SendMessage).** Each card was a new agent (`guard_card.log:610-615`).
- **Annotated-review gate.** The newest retrospective is annotated (`archive/peer/2026-10-02-retrospective-cycle131.md:357-361`).
- **Prior-art, premature-build and recipe gates.** No recipe build happened.

VIOLATION: wrong-ordering | loss_min=9 | loss_usd=? | evidence=tools/bench/cards/result_132-2.json:1

VERDICT {"schema":"verdict/1","id":"retrospective-cycle132","verdict":"refuted","alternative":"The two BLOCKs were cheap (9 card-min) and the cycle would still have stalled at the op-24 route-check gap, so no structural fault: the dispatch cap, not the ordering, set the end.","discriminating_test":"Replay: with the X10 reader branch in 132-1 and the graph read after it, count dispatches to reach the op-24 refusal (expect 4 of 6); then check whether one card closes the route-check binding (cycle 133 card 1).","violations":[{"slug":"wrong-ordering","loss_min":9,"loss_usd":"?","evidence":"tools/bench/cards/result_132-2.json:1"}],"sources":["tools/bench/cards/result_132-2.json:1","tools/bench/cards/result_132-3.json:1","tools/hooks/material_marker.log:3045","tools/bench/cards/brief_132-2.md:5","docs/d1/tooling.md:101-102","tools/bench/diag_c132_2_graph_p3b1_prerun.log:21","tools/bench/diag_c132_2_graph_p3b1.log:24","tools/bench/memory_model.json:6","tools/bench/stage_prerun_c129_1_p3b2_dry.log:23","tools/bench/stagesim_c132_6_recover_p3b2.log:42"],"note":"Findings: X10 start term 570 vs measured P3b-1 load 584.1 (P3b-2 margin 8.3 MB, not recomputed); recovered plan is final=false; dry-path 'unbound' predates 132-1 (c129 log) but stagesim finalize regressed in-cycle; no device failed."}

## Sources

(extract from answer)

## What was done with it

- **Fault `wrong-ordering` ACCEPTED** (cycle 132 judgement, 08:1x). Card 132-2's brief forbade the pre-check its own launch
  gate required, and it ran beside the card editing that gate. Rule taken: a LabVIEW card that runs a script needing
  `stage_prerun` records is never dispatched beside a card that edits `stage_prerun.py`/`stagexec.py`; it follows it.
  Recorded in `docs/d1/ring-p3b.md` PD281(a).
- **Finding 3 (X10 start term) ACCEPTED as cycle 133's first check:** P3b-1 load measured 584.1 MB vs the model's 570.0;
  P3b-2's 681.7 + 14.1 ≈ 695.8 > 690. PD281(b): recompute X10 with the measured start term before anything else; > 690
  ⇒ PD266(b) (a third half is the user's) → `decisions_pending`.
- **Finding 3/6 (recovered plan final=false; in-cycle stagesim/stagexec finalize regression) ACCEPTED:** STATUS corrected;
  cycle 133's card measures it against git 83dd0e70 (PD280(c) widened to stagesim, PD281(c)).
- **Finding 1 (fp-21 and the op-24 stop are one class) ACCEPTED:** cycle 133 treats simulator-made uid binding as one
  class and route-checks ALL 39 ops, not only to op 24 (PD281(c)).
- **Finding 4 (stubs check not rerun to avoid a FAIL log) ACCEPTED:** it is run in cycle 133 and its FAIL recorded.
- **Finding 4 (A3, no hypothesis review on the rebase failures):** each stop was answered by a measured cause read from
  code + log (PD278(b), PD279(b), PD280(b)); a hypothesis review is owed on the route-check stop if cycle 133's first card
  does not close it.
