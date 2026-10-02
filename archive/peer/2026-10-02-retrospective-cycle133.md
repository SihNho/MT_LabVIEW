# retrospective-cycle133

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.6709  in 48 / out 46024 / cache-create 150156 / cache-read 2745052  (460s, 49 turn(s))
- **date:** 2026-10-02 10:06:30
- **outcome:** ANSWERED (462s)
- **verdict-card:** VERDICT-CARD retrospective-cycle133 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle133.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle133, role retrospective) ---
CLAIM: Cycle 133 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 133 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-02 08:09:54  ..  2026-10-02 09:58:43   (109 min)
    basis: start = archive/peer/2026-10-02-retrospective-cycle132.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `wrong-ordering` (decided 2026-10-02 08:25): the cycle's LabVIEW card (pipeline prep slot, disjoint write list; deliverable first, so it is never the cycle's first act): - The live-card record keeps the card's `flags.write` globs. A dispatch is REFUSED when one of the two cards has `flags.labview` != `none` and the other card's `flags.write` matches a stage pre-check tool: `tools/stage_prerun.py`, `tools/stagexec.py`, `tools/stagesim.py`, `t??

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

== cycle audit, 2026-10-02 08:09 .. 2026-10-02 09:58 (109 min, an explicit cycle window): 58 build logs, 8 peer logs, 26 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 58/58 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 14 logs recorded a failure; unreviewed: ['stage_prerun_c133_6_graph_dry.log', 'stage_prerun_c133_6_rebase_p3b2b.log', 'wait_runner_event.log']
  FAIL  A4 every archived review says what was done with it: 22/26 annotated; blank: ['2026-10-02-hyp-c130-3-x10-selftest.md', '2026-10-02-hyp-c130-4-c128b.md', '2026-10-02-hyp-c130-4-suite-gb.md', '2026-10-02-outcome-review-20261002.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8608 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 6 log(s) with a run that printed none: ['diag_c133_4_base_gs.log', 'diag_c133_4_cand_gs.log', 'diag_c133_4_live_gs.log', 'diag_c133_5_backup.log', 'selftest_rebase_c132_6_c133_3.log', 'selftest_rebind_c132_5_c133_3.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 61, failure markers 13, logs carrying a failure 14
  C2 peer reviews dispatched 8, archived 26
  C3 wall-clock inside bgrun, BUILDS ONLY 130 min 22 s
  C4 wall-clock inside bgrun, REVIEWS 6 min 15 s; cost $5.8950 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 136 min 37 s  (builds 95%, reviews 4%, judgement session 0%)

  C6 material-marked recipe/bench runs 21, judgement-session attempts refused 3  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/INDEX.md [tools/bench/next.json plan.path]: 39 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/cards/launches.jsonl, tools/bench/diag_c133_1_peek.py, tools/bench/diag_c133_1_pred_p3b2.py, tools/bench/diag_c133_3_peek.py, tools/bench/diag_c133_5_backup.py, tools/bench/diag_c133_5_graph_p3b2a.py, tools/bench/diag_c133_5_pred_p3b2b.py, tools/bench/diag_c133_6_fsframes.py, tools/bench/gate_fp_queue.jsonl, tools/bench/heartbeat_latest.md??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 349/1137 ok; 788 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2682 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 103 lines (limit 110)
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


=== BUILD LOGS INSIDE THE WINDOW (59; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure_c133_1.log  (2026-10-02 08:36:52)
tools/bench/c125_1_offline_measure_c133_3.log  (2026-10-02 09:01:21)
tools/bench/diag_c131_5_stubs_c133_3.log  (2026-10-02 09:00:12)
tools/bench/diag_c133_1_peek.log  (2026-10-02 08:29:46)
tools/bench/diag_c133_1_pred_p3b2.log  (2026-10-02 08:37:51)
tools/bench/diag_c133_3_peek.log  (2026-10-02 08:51:04)
tools/bench/diag_c133_4_base_gs.log  (2026-10-02 08:51:13)
tools/bench/diag_c133_4_base_p1.log  (2026-10-02 08:51:18)
tools/bench/diag_c133_4_base_p2.log  (2026-10-02 08:51:24)
tools/bench/diag_c133_4_cand_gs.log  (2026-10-02 08:53:30)
tools/bench/diag_c133_4_cand_pair.log  (2026-10-02 08:53:24)
tools/bench/diag_c133_4_cand_pair2.log  (2026-10-02 08:53:57)
tools/bench/diag_c133_4_live_gs.log  (2026-10-02 08:54:39)
tools/bench/diag_c133_4_live_p1.log  (2026-10-02 08:54:48)
tools/bench/diag_c133_4_live_p2.log  (2026-10-02 08:54:53)
tools/bench/diag_c133_4_live_pair.log  (2026-10-02 08:54:42)
tools/bench/diag_c133_5_backup.log  (2026-10-02 09:12:24)
tools/bench/diag_c133_6_fsframes.log  (2026-10-02 09:31:03)
tools/bench/diag_c133_6_graph_p3b2a.log  (2026-10-02 09:52:10)
tools/bench/jev_gate.log  (2026-10-02 09:58:42)
tools/bench/motor_session_end_cycle132.log  (2026-10-02 08:11:10)
tools/bench/motor_session_start_cycle133.log  (2026-10-02 08:11:19)
tools/bench/plan_ring_p3b_split_p3b2_c133_3.log  (2026-10-02 08:56:12)
tools/bench/selftest_c133_1_fsroutes.log  (2026-10-02 08:35:03)
tools/bench/selftest_c133_1_gatefp_close.log  (2026-10-02 08:34:02)
tools/bench/selftest_c133_6_fr.log  (2026-10-02 09:32:23)
tools/bench/selftest_chat_p1_c133_1.log  (2026-10-02 08:35:40)
tools/bench/selftest_chat_p1_c133_3.log  (2026-10-02 09:01:22)
tools/bench/selftest_chat_p1_c133_5.log  (2026-10-02 09:09:23)
tools/bench/selftest_rebase_c132_6_c133_3.log  (2026-10-02 09:01:10)
tools/bench/selftest_rebase_c133_1.log  (2026-10-02 08:35:28)
tools/bench/selftest_rebase_c133_3.log  (2026-10-02 08:57:51)
tools/bench/selftest_rebind_c132_5_c133_3.log  (2026-10-02 09:01:11)
tools/bench/selftest_rebind_c133_1.log  (2026-10-02 08:35:32)
tools/bench/selftest_x10_c130_1_c133_3.log  (2026-10-02 09:00:00)
tools/bench/selftest_x10_c130_1_c133_3r.log  (2026-10-02 09:01:11)
tools/bench/selftest_x10_c132_1_c133_3.log  (2026-10-02 09:00:05)
tools/bench/selftest_x10_c132_1_c133_3r.log  (2026-10-02 09:01:19)
tools/bench/selftest_x10_c132_4_c133_3.log  (2026-10-02 09:00:11)
tools/bench/stage_d1_ring_p3b2a_scratch.log  (2026-10-02 09:26:05)
tools/bench/stage_d1_ring_p3b2a_scratch_c133_6.log  (2026-10-02 09:47:55)
tools/bench/stage_prerun_c133_1_p3b2_dry.log  (2026-10-02 08:38:09)
tools/bench/stage_prerun_c133_1_rebase_p3b2.log  (2026-10-02 08:36:47)
tools/bench/stage_prerun_c133_3_p3b2a_dry.log  (2026-10-02 08:58:23)
tools/bench/stage_prerun_c133_3_p3b2a_prerun.log  (2026-10-02 08:59:11)
tools/bench/stage_prerun_c133_5_p3b2a_scr_dry.log  (2026-10-02 09:09:48)
tools/bench/stage_prerun_c133_5_p3b2a_scr_dry2.log  (2026-10-02 09:10:44)
tools/bench/stage_prerun_c133_5_p3b2a_scr_prerun.log  (2026-10-02 09:10:07)
tools/bench/stage_prerun_c133_5_p3b2a_scr_prerun2.log  (2026-10-02 09:11:03)
tools/bench/stage_prerun_c133_6_graph_dry.log  (2026-10-02 09:48:24)
tools/bench/stage_prerun_c133_6_graph_dry2.log  (2026-10-02 09:49:03)
tools/bench/stage_prerun_c133_6_graph_prerun.log  (2026-10-02 09:49:16)
tools/bench/stage_prerun_c133_6_p3b2a_dry.log  (2026-10-02 09:36:53)
tools/bench/stage_prerun_c133_6_p3b2a_prerun.log  (2026-10-02 09:37:33)
tools/bench/stage_prerun_c133_6_p3b2a_scr_dry.log  (2026-10-02 09:38:00)
tools/bench/stage_prerun_c133_6_p3b2a_scr_prerun.log  (2026-10-02 09:38:27)
tools/bench/stage_prerun_c133_6_rebase_p3b2b.log  (2026-10-02 09:52:28)
tools/bench/stagesim_selftest_c133_1.log  (2026-10-02 08:35:25)
tools/bench/wait_runner_event.log  (2026-10-02 09:43:21)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (8) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_132.log  (2026-10-02 08:11:03)
tools/bench/cycle_133.log  (2026-10-02 08:13:29)
tools/bench/cycle_runner.log  (2026-10-02 08:13:29)
tools/bench/cycle_runner_main_20261002_0312.log  (2026-10-02 08:13:29)
tools/bench/outcome_review_cycle133.log  (2026-10-02 08:13:29)
tools/bench/peer_c133_5_chatp1.log  (2026-10-02 09:08:26)
tools/bench/peer_c133_6_fr.log  (2026-10-02 09:36:02)
tools/bench/retro.log  (2026-10-02 09:58:42)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle133","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective: cycle 133 (window 08:09:54 to 09:58:43)

**Window check.** The evidence fits the window. The judgement session started at 08:13:29 (`tools/bench/cycle_133.log:1`). The first card was bound at 08:26:28 and the last at 09:30:14 (`tools/bench/cards/guard_card.log:616-622`). The last fact is the rebase refusal at 09:52 (`tools/bench/stage_prerun_c133_6_rebase_p3b2b.log:4`). The four blank reviews A4 lists are not this cycle's work: three are cycle-130 files, charged here because A4 counts by day. Only the outcome review (written 08:1x, before the session) falls inside the window.

**The claim is refuted.** The cycle ended on the six-dispatch cap with session b not run (`docs/d1/ring-p3b.md:228`). Two faults each used up one of those six slots, and they are of the same size.

## Fault 1 (largest): the dry run saw the FR failure, labelled it UNVERIFIED and passed anyway; third time this class has occurred

**What happened**
- At 08:58 the dry run of recipe a computed the FR gate as **false**. Because this came after the first edit operation, the dry's rule (`tools/stage_prerun.py:726-730`) relabels any false gate as UNVERIFIED (`stage_prerun_c133_3_p3b2a_dry.log:73`). It then printed `DRY PASS … unverified 1` (`:83`).
- The same line appears in the prerun and in all four wrapper dry/prerun logs of card 133-5 (`stage_prerun_c133_5_p3b2a_scr_*.log:85`).
- The run itself did not need LabVIEW to show this: the other gates evaluated on the same simulated state (D, TD, PB) passed. After the fix, the dry shows FR as PASS (`result_133-6.json:16`).
- Card 133-5 then ran 21 LabVIEW edits (all matching the simulation) and stopped on exactly that gate: `FAIL FR` (`stage_d1_ring_p3b2a_scratch.log:350`), ending `rc=1 after 891s` (`:379`).
- The failing log then required a hypothesis review: $1.3199, 154 s (`peer_c133_6_fr.log:4,58`). The scratch run was repeated: 559 s (`stage_d1_ring_p3b2a_scratch_c133_6.log:394`).
- The fix's own self-test reproduced the failure offline in 1 s (`archive/peer/2026-10-02-c133-6-fr-p3b2a.md:76`).

**Why this is a repeated class.** The same relabelling hid a real failure twice before:
- Card 108-5: an unroutable row (`tools/stage_prerun.py:906-910`).
- Card 130-5: the executor stopped at op 48 of 63 (`:911-915`; `docs/d1/tooling.md:27-29`).

Each time, only that one symptom was patched. The relabelling rule itself has never changed. The approach should have changed at the second occurrence (130-5): a gate that is false on data that is not a stub should fail the dry, or at least block the launch until a card records a decision on it.

**It is still unfixed and unrecorded.** Card 133-6 reported it (`result_133-6.json:16`), but decision PD286 carries no fix (`ring-p3b.md:228-255`). Session b's dry next cycle will run under the same rule.

- **Slug:** repeated-failure-class
- **Loss:** about 20 min (891 s of LabVIEW, 154 s of review, about 2 min repeating dry/prerun). The only logged dollar figure is the $1.32 review, which is a floor. The material-session time has no cost line, so the dollar loss is unknown.
- **Counterfactual:** had the 08:58 dry failed on FR, the fix would have been step 0 of card 133-5. Scratch a would have passed around 09:21, and the graph read and rebase of b would have been reached around 09:35. The −30 refusal would then have arrived in the fifth dispatch, not the sixth. That leaves the sixth for the rebind + scratch-b card (PD286(c)), which is now cycle 134's first act (`STATUS.md:57`).

## Fault 2 (same size): the new guard_session device card used a main dispatch slot instead of a prep slot

**What the cycle's own decisions said.** Both say to build the guard_session pairing device "in an OFFLINE card … BESIDE the cycle's LabVIEW card (pipeline prep slot)" (`docs/violation-decisions.md:1828-1829`, and PD282(d) at `ring-p3b.md:153-154`).

**What happened instead**
- Card 133-4 was dispatched at 08:49:04 beside 133-3, which is also an offline card (`guard_card.log:620`).
- So it counted toward the cap of six (`tools/hooks/guard_session.py:60`) instead of the separate budget of three for prep cards (`:71`, `:434-442`).
- No reason is recorded in PD283 or PD284.

**Consequence.** The cycle closed on the six-dispatch cap (`ring-p3b.md:228`) about 75 minutes into its 180-minute budget.

- **Slug:** wrong-ordering
- **Loss:** about 13 min, used as a stand-in. That is what this cycle spent before its first dispatch (08:13:29 to 08:26:28), and the deferred card now pays it again in cycle 134. No log carries a dollar figure.
- **Counterfactual:** had 133-4 been dispatched together with 133-5 at 09:05:28, the count at 09:5x would have been 5 of 6. The PD286(c) card could then have been dispatched around 09:55, inside this cycle.

## Findings

1. **Repeated failure**
   - (a) Fault 1 above.
   - (b) The rebase step has hit five different gaps in two cycles. PD286(b) calls them "each closed, none repeated" (`ring-p3b.md:239-240`). As a class they are one thing: four of the five, plus the FR bug, are facts about the Flat Sequence (FS) frame and border structure that the graph reader does not record.
     - The reader got error 1055 on the frame owner (`diag_c132_2_graph_p3b1.log:82`).
     - The frame map is filled in by `carry_fs` by elimination (review `:43-51`).
   - The approach should have changed at 133-1, the third FS-related gap. The next act is a sixth binder patch (`STATUS.md:57`).
2. **Missing tool.** A graph reader that records FS frames and border tunnels (one `OpFsDiagrams_v0` read, about 1 minute of LabVIEW, review `:82`). It would have answered:
   - FR's proxy: base frames taken from terminal rows only (`stage_d1_ring_p3b2a.py:55-57` before the fix).
   - Whether frame f0 is really 27641 (review `:45`).
   - Probably the −30 FS-CARRY refusal.

   CLAUDE.md:480-481 ("second time … by inference … the next build is the READER") applies. PD286(e) defers it again to "after the deliverable".
3. **Decided without measuring**
   - Frame f0 = 27641 is still assigned by elimination. The 1-minute read could have been folded into 133-6's scratch run at 09:38, as the review suggested; it was not.
   - The census gate CEN2 passed while comparing two empty sets (`measured {} == declared {}`, `stage_d1_ring_p3b2a_scratch_c133_6.log:354`), even though the run created 8 objects. It checked nothing.
4. **Rule compliance**
   - Broken: CLAUDE.md:480-481 (build the reader after a second guess) and CLAUDE.md:553 (a rule broken twice goes into a hook); fault 1 is the third occurrence.
   - Satisfied only formally:
     - The PRERUN-GATE refusal at 09:48:11 (`material_marker.log:3094`) was cleared by passing a stand-in graph with a different md5 (`stage_prerun_c133_6_graph_dry2.log:1,7`, 22 of 54 lines covered). It was not queued as a gate false positive; `gate_fp_queue.jsonl` ends at fp-29. The same stand-in was used in cycle 132 (`diag_c132_2_graph_p3b1_prerun.log:1`).
     - The steer was followed in form: the next act is labelled `build`, but its first step is a binder tool fix.
   - Kept: the retry cap, returning at the first unexpected result (all four FAIL cards did), the USER-RULES lines, the 40-row rule for P3b (CLAUDE.md:519), and LabVIEW was closed each time.
   - Audit A3: `wait_runner_event.log` is the chat's watcher, not a build, so A3 counts it wrongly.
   - **What the audit does not cover:**
     - DRY PASS results that carry UNVERIFIED gates (this cycle's main fault is invisible to it).
     - Whether a card used a main dispatch slot or a prep slot.
     - Gates that pass on nothing (CEN2).
     - Stand-in graphs.
     - Whether a judgement decision (PD282(d)) was actually carried out.
5. **Ordering.** Otherwise defensible: offline work came before LabVIEW, the memory split before the scratch run, and the deliverable first. The exception is fault 2.
6. **What the summaries hid**
   - Card 133-3's result reports "dry PASS 21/21; prerun 15/0" with no mention of "unverified 1" (`result_133-3.json:19`).
   - STATUS (`STATUS.md:62`) says only that "our FR gate refused" and leaves out both the 891 s of LabVIEW and the fact that the dry had already seen the failure.
   - The review itself wrongly says the gate "was never evaluated against the simulated end state" (`:76`).
   - The judgement session's own cost is not in the window (C4c shows 0), so C5 understates total cost.
7. **Judgement inside a material session**
   - 133-4: the material session left a live hook in place that turned a self-test red, and called it a "judgement call" (`result_133-4.json:1`, note). It was ratified afterwards in PD284(d).
   - 133-6: the material session wrote "Class ACCEPTED as our-script-bug" (review `:98`). It then went on to the LabVIEW scratch run without returning to judgement, because the brief scripted review-then-run in sequence (`task_133-6.json:39-40`). It correctly declined the review's 1-minute test because it was outside the card's scope (`:104`).
   - Neither cost anything (judgement agreed in PD286(a)), so these are findings, not faults.

## Device effect

No listed device failed within its decided scope inside the window:
- **Pairing check (08:25):** after it was built, 133-5 and 133-6 each ran alone (`guard_card.log:621-622`).
- **No SendMessage resume:** none in `guard_card.log`.
- **X10 memory gate:** it fired correctly on the unsplit plan (701.9 MB > 690, `diag_c133_1_pred_p3b2.log`), and both scratch peaks stayed under its prediction (646.7 and 650.9 MB vs 671.8). Its known hole, falling back to 570 MB when the input load is unmeasured (PD284(b)), was never used for a launch.
- **bgrun failure codes:** they worked (`rc=1` at `:379`, `rc=2` on the rebase).
- **Stop record, prior-art and launch gates:** there was no recipe launch, only scratch wrappers.
- **Dry-run "collect every failure" device (2026-09-25 / 2026-09-27 20:20):** its decided scope is address, checkpoint and routing failures. FR is a recipe gate, so fault 1 falls outside the letter of that device and is reported as a repeated class, not a device failure.
- **Prerun gate:** it was cleared formally through its own `--graph` option, which caused no loss. It is recorded under finding 4.

VIOLATION: repeated-failure-class | loss_min=20 | loss_usd=? | evidence=tools/bench/stage_prerun_c133_3_p3b2a_dry.log:73
VIOLATION: wrong-ordering | loss_min=13 | loss_usd=? | evidence=tools/bench/cards/guard_card.log:620
VERDICT {"schema":"verdict/1","id":"retrospective-cycle133","verdict":"refuted","alternative":"FR was an ordinary recipe bug that the mandated scratch run exists to catch, and the dry is not designed to judge gates after an edit; the cycle still ended on the cap because the -30 rebase gap was unknowable until a's real file existed.","discriminating_test":"Re-run stage_prerun --dry on stage_d1_ring_p3b2a.py md5 ababd4ed with the after-edit relabelling disabled for gates computed on non-stub data: if FR alone FAILs offline in seconds, the 891 s LabVIEW run was avoidable.","violations":[{"slug":"repeated-failure-class","loss_min":20,"loss_usd":"?","evidence":"tools/bench/stage_prerun_c133_3_p3b2a_dry.log:73"},{"slug":"wrong-ordering","loss_min":13,"loss_usd":"?","evidence":"tools/bench/cards/guard_card.log:620"}],"sources":["tools/bench/stage_prerun_c133_3_p3b2a_dry.log:73","tools/bench/stage_d1_ring_p3b2a_scratch.log:350","tools/bench/stage_d1_ring_p3b2a_scratch.log:379","tools/stage_prerun.py:726","tools/stage_prerun.py:906","docs/d1/tooling.md:27","tools/bench/peer_c133_6_fr.log:4","docs/violation-decisions.md:1828","tools/bench/cards/guard_card.log:620","tools/hooks/guard_session.py:71","docs/d1/ring-p3b.md:228"],"note":"Unfixed: the after-edit relabelling (stage_prerun.py:726-730) will apply to session b's dry in cycle 134; PD286 carries no fix. FS frame/border reader still deferred despite CLAUDE.md:480 reader rule."}

## Sources

(extract from answer)

## What was done with it

- **Fault 1 `repeated-failure-class` ACCEPTED** (cycle 133 judgement, 10:10). The rule, not the symptom, is fixed: a gate
  FALSE on simulated data fails the dry; only stub-input gates may be UNVERIFIED and they block the launch unless named; an
  empty declared census prints UNPREDICTED (finding 3's CEN2 case, same class). `docs/violation-decisions.md`
  `## repeated-failure-class — 2026-10-02 10:10` (DECISION: device), built as cycle 134 card 1's first offline step
  (`docs/d1/ring-p3b.md` PD287(a)); acceptance = 133-3's session-a bytes FAIL on FR offline.
- **Fault 2 `wrong-ordering` ACCEPTED.** The deviation from the 08:25 decision (main slot instead of the prep slot beside the
  LabVIEW card) had no recorded reason; the one I had does not hold. `## wrong-ordering — 2026-10-02 10:10`
  (DECISION: no-device, with the condition under which it becomes one); judgement rule PD287(d).
- **Findings 1(b), 2, 3 (FS structure guessed, reader missing) ACCEPTED and acted on:** the next act no longer patches the
  binder (PD286(c) SUPERSEDED). The graph reader records Flat Sequence frames and border tunnels (`OpFsDiagrams_v0`), and
  session b is finalized DIRECTLY on the real graph of a's file, so no simulator uid of a's objects is left to bind
  (PD287(b)(c)). f0 = 27641 becomes a measurement in that read.
- **Finding 4 (stand-in graph for the reader's prerun):** accepted as a gap: the graph reader of an unread file has no graph
  of its own to cite; cycle 134's card 1 queues it with `gate_fp.py` if the PRERUN gate refuses again, instead of a stand-in.
- **Finding 6 (summaries hid "unverified 1" and the 891 s):** accepted; the dry device makes "unverified" a refusal, and the
  STATUS cycle-133 brief now names both scratch runs' costs through PD285/PD286.
- **Finding 7 (judgement in material):** noted; both were ratified (PD284(d), PD286(a)); cards will keep a review step and a
  LabVIEW step apart when the review's class decides whether to run.
- **Steer:** recorded as followed; the reviewer's point that card 1 begins with tools is true — they are the measured
  blockers of the deliverable's next run (`stage_prerun_c133_6_rebase_p3b2b.log:3-4`, `stage_prerun_c133_3_p3b2a_dry.log:73`).
