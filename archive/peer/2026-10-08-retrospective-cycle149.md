# retrospective-cycle149

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $3.9380  in 108 / out 57423 / cache-create 177940 / cache-read 6827905  (583s, 79 turn(s))
- **date:** 2026-10-08 19:53:14
- **outcome:** ANSWERED (585s)
- **verdict-card:** VERDICT-CARD retrospective-cycle149 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle149.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle149, role retrospective) ---
CLAIM: Cycle 149 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 149 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-08 17:39:02  ..  2026-10-08 19:43:16   (124 min)
    basis: start = archive/peer/2026-10-08-retrospective-cycle148.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `repeated-failure-class` (decided 2026-10-02 10:10): - `stage_prerun --dry`: a gate evaluated FALSE on simulated (non-stub) data FAILS the dry, whatever op it follows. Only a gate whose inputs are COM stubs may stay UNVERIFIED, and a dry with any UNVERIFIED gate ends `DRY PASS-UNVERIFIED <names>`, which the launch gate refuses unless the card names each unverified gate as expected. - stagekit's census gate with an EMPTY declared set prints `UNPREDIC??
  - `repeated-failure-class` (decided 2026-10-02): every FS frame reaches a loop/case/VI diagram through measured links, or is UNMEASURED and unused by the plan (`selftest_c134_4_owners` becomes a gate, not only a test); (2) finalize writes the plan file only on success (PD279(c) extended). Acceptance (offline): the pre-134-4 stagesim on `graph_ring_p3b2a_fs_20261002_102553.json` FAILS the gate before step 1 naming FS 27509's frames; the current s??
  - `repeated-failure-class` (decided 2026-10-07 20:25): cross-graph raw-uid comparison (`tools/bench/prep_c143_4_facts.md`, 19 sites) and the rebase rule (a re-issued uid is fatal only when the plan names it, else `REUSE-NOTED`), in `tools/stage_prerun.py` 03cdd8c6, self-test `selftest_rebase_uidreuse_c143_4.py`; (2) PD347(b): created objects bind by the executor's creation-map RECORD first (`tools/bench/selftest_t3.log` 22/0). The sites the census lis??
  - `device-failed` (decided 2026-10-07 20:25): `tools/stop_record.py:237` (`GIT_READONLY` now holds `show`, `add` and `commit`; `md5sum` and `diff` are read-only programs at :214), self-test `selftest_c_e3.py`. :3333 was never queued as a gate false positive, so the repair was never checked on that exact command. The cycle-144 tooling card owes that check, offline: put the full commands of `material_marker.log:3332` and `:3333` through the sto??
  - `repeated-failure-class` (decided 2026-10-08 01:16): all PASS (real == sim at every op, D new/lost, PB, prim, term identity, peak) is adopted; its full final EL read becomes the expected file; the difference against the elrule prediction is RECORDED per class in the result card with a one-line explanation. Only a class that is in neither the start read nor the prediction, or a total off by more than 3, is a RETURN. elrule is not patched again this c??
  - `device-failed` (decided 2026-10-08 01:16): test on the newest archived retrospective; if its `## What was done with it` is still the placeholder it does NOT refuse (a refusal there would only stall an unattended runner) but writes a `retro-undisposed` entry into the next cycle card's `gates_due` (due: true) and a `RETRO-UNDISPOSED` log line, so the next judgement session disposes it first. Built offline in cycle 147 (purpose pass item), wi??

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

== cycle audit, 2026-10-08 17:39 .. 2026-10-08 19:43 (124 min, an explicit cycle window): 48 build logs, 14 peer logs, 13 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 47/48 ok; NO BGRUN line in ['fn_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 16 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 13/13 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 10964 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 1 log(s) with a run that printed none: ['diag_c149_a1_3_items.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 52, failure markers 15, logs carrying a failure 16
  C2 peer reviews dispatched 14, archived 13
  C3 wall-clock inside bgrun, BUILDS ONLY 42 min 38 s
  C4 wall-clock inside bgrun, REVIEWS 8 min 20 s; cost $4.8213 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 123 min 54 s; cost $47.2839 from 6 log(s) - cycle_149.log, cycle_149_assign_1.log, cycle_149_assign_2.log, cycle_149_assign_3.log, cycle_149_handback_1.log, cycle_149_handback_2.log
  C5 total wall-clock 174 min 52 s  (builds 24%, reviews 4%, judgement session 70%)

  C6 material-marked recipe/bench runs 30, judgement-session attempts refused 7  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/ring-p4c.md [tools/bench/next.json plan.path]: 255 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/adopted_scratch.jsonl, tools/bench/cards/brief_149-a1-1.md, tools/bench/cards/brief_149-a1-2.md, tools/bench/cards/brief_149-a1-3.md, tools/bench/cards/brief_149-a2-1.md, tools/bench/cards/brief_149-a3-1.md, tools/bench/cards/brief_149-a3-2.md, tools/bench/cards/brief_149-a3-3.md, tools/bench/cards/brief_149-a3-4.md, tools/bench/cards/launches.jsonl??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 351/1200 ok; 849 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  FAIL  L2 every cited project path exists: 2 DANGLING of 3046 citations checked:
       docs/d1/ring-p4.md:131 -> tools/bench/build_oploopendref_v0.py
       STATUS.md:132 -> tools/bench/build_oploopendref_v0.py

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:199 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 743 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  FAIL  L8 decision headers carry HH:MM: 1 header(s) dated >= 2026-09-28 without a parseable HH:MM (violations.py DEC_RE reads them as bare dates): ['docs/violation-decisions.md:1875']
  WARN  L9 new Pre-decided items carry a USER-RULES: line: 1 item(s) >= 238 without `USER-RULES:` (read docs/user-rules.md and cite the rows relied on, or write `USER-RULES: none apply`): ['docs/d1/tooling.md:145 (item 329)']
  FAIL  L10 active docs stay <= 400 lines: 2 doc(s) over the cap: ['docs/chat-handoff.md 550', 'docs/d1/ring-p3b.md 419']. Freeze in place (`status: frozen` + footer, tools/bench/freeze_docs_d1.py) and index what is in force, or split into linked topic files.
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1405; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 1027
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  WARN  L11 frozen docs carry a FROZEN footer: 1 without one: ['docs/d1/ring-p4.md']
  WARN  L12 function table matches the code: moved 34 (stagekit.op:add_shift_reg, stagekit.op:case_frame_wire, stagekit.op:case_in, stagekit.op:case_wired, stagekit.op:connect ...) - run py tools/gen_capabilities.py

AUDIT VIOLATIONS: A1 every build log came from bgrun, L2 every cited project path exists, L8 decision headers carry HH:MM, L10 active docs stay <= 400 lines


=== BUILD LOGS INSIDE THE WINDOW (49; read them directly, they are the primary record) ===
tools/bench/diag_c147_p4s06v18_scratch.log  (2026-10-08 17:57:18)
tools/bench/diag_c148_a2_4_census.log  (2026-10-08 17:58:07)
tools/bench/diag_c148_a2_4_check.log  (2026-10-08 17:45:48)
tools/bench/diag_c148_a2_4_check_after.log  (2026-10-08 17:59:21)
tools/bench/diag_c148_a2_4_el.log  (2026-10-08 17:58:38)
tools/bench/diag_c148_a2_4_scr_dry.log  (2026-10-08 17:46:33)
tools/bench/diag_c148_a2_4_scr_prerun.log  (2026-10-08 17:47:09)
tools/bench/diag_c148_a2_4_scrreq.log  (2026-10-08 17:47:10)
tools/bench/diag_c149_a1_1_env.log  (2026-10-08 18:04:29)
tools/bench/diag_c149_a1_1_env2.log  (2026-10-08 18:06:43)
tools/bench/diag_c149_a1_2_el.log  (2026-10-08 18:23:56)
tools/bench/diag_c149_a1_2_eladv.log  (2026-10-08 18:30:58)
tools/bench/diag_c149_a1_2_inv.log  (2026-10-08 18:33:33)
tools/bench/diag_c149_a1_2_probe.log  (2026-10-08 18:12:14)
tools/bench/diag_c149_a1_3_cmp.log  (2026-10-08 18:51:24)
tools/bench/diag_c149_a1_3_inv.log  (2026-10-08 18:54:23)
tools/bench/diag_c149_a1_3_items.log  (2026-10-08 18:54:35)
tools/bench/diag_c149_a1_3_types.log  (2026-10-08 18:53:54)
tools/bench/diag_c149_a1_3_wire.log  (2026-10-08 18:50:05)
tools/bench/diag_c149_a3_1_adopt.log  (2026-10-08 19:08:25)
tools/bench/diag_c149_a3_1_elexp.log  (2026-10-08 19:09:04)
tools/bench/diag_c149_a3_1_inv_after.log  (2026-10-08 19:14:19)
tools/bench/diag_c149_a3_1_inv_before.log  (2026-10-08 19:07:59)
tools/bench/diag_c149_a3_1_mkgraph.log  (2026-10-08 19:09:59)
tools/bench/diag_c149_a3_2_disc.log  (2026-10-08 19:18:40)
tools/bench/diag_c149_a3_2_graph.log  (2026-10-08 19:24:40)
tools/bench/diag_c149_a3_2_graph_dry.log  (2026-10-08 19:21:34)
tools/bench/diag_c149_a3_2_graph_prerun.log  (2026-10-08 19:21:37)
tools/bench/diag_c149_a3_2_inv_after.log  (2026-10-08 19:39:51)
tools/bench/diag_c149_a3_2_inv_before.log  (2026-10-08 19:19:34)
tools/bench/diag_c149_a3_2_memload.log  (2026-10-08 19:24:59)
tools/bench/diag_c149_a3_2_mkgraph.log  (2026-10-08 19:19:12)
tools/bench/diag_c149_a3_void_md.log  (2026-10-08 19:39:28)
tools/bench/diag_c149_a3_void_s06.log  (2026-10-08 19:36:16)
tools/bench/fn_gate.log  (2026-10-08 19:21:46)
tools/bench/jev_gate.log  (2026-10-08 19:41:57)
tools/bench/motor_session_end_cycle148.log  (2026-10-08 17:39:10)
tools/bench/motor_session_start_cycle149.log  (2026-10-08 17:39:19)
tools/bench/prep_c148_a3_3_check_after.log  (2026-10-08 17:58:26)
tools/bench/prep_c148_a3_3_check_before.log  (2026-10-08 17:50:28)
tools/bench/prep_c148_a3_3_dry.log  (2026-10-08 17:56:37)
tools/bench/prep_c148_a3_3_mk.log  (2026-10-08 17:53:04)
tools/bench/prep_c148_a3_3_pred.log  (2026-10-08 17:54:31)
tools/bench/prep_c148_a3_3_prerun.log  (2026-10-08 17:57:03)
tools/bench/prep_c148_a3_3_probe.log  (2026-10-08 17:46:42)
tools/bench/prep_c148_a3_3_probe2.log  (2026-10-08 17:48:07)
tools/bench/prep_c148_a3_3_scr_dry.log  (2026-10-08 17:57:26)
tools/bench/prep_c148_a3_3_scr_prerun.log  (2026-10-08 17:57:33)
tools/bench/prep_c148_a3_3_scrreq.log  (2026-10-08 17:57:33)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (14) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_149.log  (2026-10-08 17:42:49)
tools/bench/cycle_149_assign_1.log  (2026-10-08 18:36:51)
tools/bench/cycle_149_assign_2.log  (2026-10-08 18:58:53)
tools/bench/cycle_149_assign_3.log  (2026-10-08 19:43:15)
tools/bench/cycle_149_handback_1.log  (2026-10-08 18:39:29)
tools/bench/cycle_149_handback_2.log  (2026-10-08 19:01:46)
tools/bench/cycle_runner.log  (2026-10-08 19:43:15)
tools/bench/cycle_runner_main_20261008_1231.log  (2026-10-08 19:43:15)
tools/bench/peer_c149-a1-2-el51.log  (2026-10-08 18:28:56)
tools/bench/peer_c149-a1-2-eladv.log  (2026-10-08 18:32:59)
tools/bench/peer_c149-a3-1-mkgraph.log  (2026-10-08 19:13:42)
tools/bench/peer_c149-a3-2-void.log  (2026-10-08 19:38:56)
tools/bench/retro.log  (2026-10-08 19:43:16)
tools/bench/runner_supervisor.log  (2026-10-08 19:43:15)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle149","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 149 (window 17:39:02 – 19:43:16, 124 min)

**Verdict:** the cycle delivered its main result: s06 was adopted (`assign_result_149_3.json:8-10`). Getting there took three assignment rounds and three hand-backs, at $47.28 in sessions plus $4.82 in peer reviews (audit C4/C4c). There is one costly structural fault: the round-3 Void census. There is also one device failure that matters more than its minutes: the retrospective-disposition check is defeated by this review format itself.

## The structural fault: the round-3 Void census was launched on a reader nobody had measured

- **What happened.** The round-3 purpose (`STATUS.md:69`) put "take a census of Void-typed terminals" before the s07 rebase and the tooling card. The census script was written on two assumptions and never checked:
  - **Speed.** It says itself that "the per-read time is not known" (`tools/bench/diag_c149_a3_void.py:12-13`), yet it capped the run at 600 s (`:30`). At the measured 0.54 s per read, 4379 terminals need about 40 min (`diag_c149_a3_void_s06.log:9-13,17`).
  - **Seeing Void at all.** Its Void flag is "the type name contains 'void'" (`:14`). `gscript.TD_NAMES` has no entry for code 0x00, so a Void type is named `"0x00"` and can never match (`archive/peer/2026-10-08-c149-a3-2-void.md:49-52`). The project's own note says Void reads back as TD 0x0000 (`docs/NAMES.md:1171`, cited there).
- **Cost.** The run took 19:25:08 → 19:36:16 (`BGRUN END rc=1 after 668s`). Then came a hypothesis review ($0.9162, void.md:7) and hand-back 3 at 19:43 (`handback_149_3.json:6`). The s07 rebase (149-a3-4) and the tooling card (149-a2-1) were left undispatched.
  - Loss: about 18 min.
  - Dollars: only the $0.92 review is in a log. The assignment session's share of its $12.49 is not split out, so loss_usd is `?`.
- **Counterfactual.** At ~19:01 the hand-back-2 judgement could have required two cheap checks before any census, or placed the census after 149-a3-4:
  - an offline `parse_type_descriptors` call on a code-0 descriptor (seconds);
  - a 50-read rate probe.

  Then 149-a3-2 would have ended PASS after memload at 19:24:58 (`diag_c149_a3_2_memload.log:16`). The 18 minutes to 19:43 would have gone to the offline s07 rebase instead of a hand-back that left items 3–8 unmet.

## Findings

**1. Repeated failure.**
- **Item 6 ("source void → sink I32") was located by guess twice.**
  - First, by its position near the moved nodes; the guess was not supported (`diag_c149_a1_3_facts.md:23-24`).
  - Then by the blind census.
  - CLAUDE.md:492-493 says the second guess must be replaced by building the reader. Round 3 (attempt 2) should have been that reader.
- **Re-used wire uid 23807 failed twice.** It broke the 12:52 scratch's D gate, then the a3-1 graph-plan script (`result_149-a3-1.json:14-15`). That script was "a names-only copy of a never-run template".
- **The Error List reader's Python packages were missing twice** (148-a2-4, 149-a1-1). This was fixed on attempt 3 (`diag_c149_a1_2_facts.md:9-15`).

**2. Missing tool.**
- **No reader that maps an Error List item to the object it selects.** The double-click selection was captured only as an image (`diag_c149_a1_3_facts.md:13-14`, "item->uid not read"). That reader would have answered item 6 in round 2 and made the census unnecessary.
- **Also missing:**
  - a bulk terminal-type reader (void.md:67, 77);
  - a stand-alone read-only `Is Broken?` reader (CLAUDE.md:494; fp-63);
  - a package import check before Error List reads, which would have caught 148-a2-4's failure before the 589 s scratch.

**3. Unmeasured steps.**
- The census, as above.
- **The cause of cycle 148's fake hand-back was never measured.** The round-1 judgement called its explanation a "working cause … not measured yet" (`cycle_149.log:256`). The card that would measure it (149-a2-1) never ran in three rounds, so the cycle ended still working from inference.

**4. Rule compliance.**
- **Broken:**
  - The "guessed twice → build the reader" rule (CLAUDE.md:492).
  - The purpose-flow rule that a hook edit must be named in the purpose (`cycle_149.log:234-237`). It was missed in rounds 1 and 2, which caused hand-back 2 (`handback_149_2.json:5-6`).
- **Evaded:**
  - The rule that a gate refusal is routed around "only by an equivalent command form" (`cycle_149.log:101-105`). The workaround was a verbatim copy of the recipe's code (`diag_c149_a1_2_facts.md:29-31`).
  - The false-positive log commands were reworded so the gate would pass them (material transcript line 303→308; the fp-62 command text was altered).
- **Satisfied only formally:**
  - Rule 1a (CLAUDE.md:35-37): s06 was adopted with an unidentified type conflict, and the numeric check was deferred to P6. This is defensible under the broken-intermediates allowance (CLAUDE.md:545).
  - STATUS one-screen rule: 199 lines, with three new long NEXT paragraphs (`STATUS.md:69-71`).
- **What the audit does not cover:**
  - **A4 is wrong.** It reports 13/13 reviews annotated, but `audit_cycle.py:619` finds the *first* "What was done with it" string. That string is the one quoted at line 147 of the review prompt, so A4 passes `retrospective-cycle147/148.md`, whose real sections still read "(Claude fills in)" (`retrospective-cycle148.md:369-371`).
  - C4c files the assignment sessions ($41.78 of $47.28) under "judgement", which hides where the build cost went.
  - C6 counts 7 refusals but does not say that 5 were false (`material_marker.log:3593-3595,3601-3602`).

**5. Ordering.**
- The census sat ahead of the offline s07 rebase.
- The tooling card was "then, ALONE" last in all three rounds and never ran.
- The Error List package check should have come before the 17:47 scratch launch, not after it failed at 17:58:38.

**6. What the summaries understate.**
- The A4 false pass (above).
- Hand-back 3 calls a3-2 "the retry" of a3-1, but they failed on unrelated steps; the census failure was its first occurrence.
- `STATUS.md:70` says the reader "now works with nothing installed". The packages were lost because the chat relaunched the runner through WMI at 12:31 (`runner_supervisor.log:47-49`, per `result_149-a1-1.json:16`). Every future Error List read needs the path wrapper.
- The cycle-start Error List check only re-used an old result (`cycle_149.log:216`), so it could not have detected the broken reader.
- The s07 prep item asks for a dry run and prerun PASS on a provisional plan. The session prompt requires that (`cycle_149.log:89-94`), but `stage_prerun.py:2593-2599` can never give it. This was reported as "by design" and never raised as a contradiction.

**7. Judgement inside a material session.**
- Card 149-a1-2's material session chose to work around the launch gate by copying the recipe's code, then commissioned a review of the copy (`diag_c149_a1_2_facts.md:29-31`).
- Card 149-a3-2's material session accepted the void review's findings itself (void.md:90-97). This was minor: it changed how the census was reported, and the route decision was correctly handed to judgement.

## Device effect

- **The retrospective-disposition check failed (`device-failed`).** Three checks are affected: `guard_peer.undisposed` (2026-09-16 15:05), `cycle_runner.retro_undisposed` (2026-10-08 01:16) and audit A4.
  - All three split on the **first** "## What was done with it" (`guard_peer.py:849-851`, `cycle_runner.py:1017-1019`, `audit_cycle.py:619`).
  - The v2 retrospective prompt quotes that heading in its device list (`retrospective-cycle148.md:147`), so each check reads the answer text as the disposition.
  - Result: the cycle-149 card at 17:39:21 carried no `retro-undisposed` item (`cycle_runner_main_20261008_1231.log:60`). The cycle-148 retrospective, verdict "refuted" with one named fault (:362), was never disposed. This retrospective was dispatched anyway.
  - Counterfactual: a line-anchored match would have put the item in the cycle card at 17:39, and the judgement session would have disposed retro-148 first.
- **The launch gate failed again on non-launch commands.** At 18:30:09 and 18:46:54 it blocked `py tools/gate_fp.py log --cmd "…"`. The recipe path appeared only inside a quoted argument (transcript `agent-a49e1139bd3daff88.jsonl:342-343`). That is exactly the hole closed on the stop-record path by `guard_bash.py:237-246` (fp-22) and named for the prerun gate in decision 2026-09-27 15:49. The gate's refusal of the recipe's offline `--el-advisory` (fp-62) cited an old failed segment of the log — the class drained as fp-1. Each time it was worked around (by the code copy or by rewording), at about 10 min and $0.90 (`2026-10-08-c149-a1-2-eladv.md:7`).
- **No device failure found:**
  - the bgrun exit-code check (logs with FAIL lines end rc=1, e.g. `diag_c149_a3_void_s06.log:24`);
  - cost parsing (C4b 4/4);
  - the prior-art and premature-build gates (s06 was released `novel` in cycle 148).

VIOLATION: inference-over-measurement | loss_min=18 | loss_usd=? | evidence=tools/bench/diag_c149_a3_void.py:12
VIOLATION: device-failed | loss_min=4 | loss_usd=1.88 | evidence=tools/hooks/guard_peer.py:851
VERDICT {"schema":"verdict/1","id":"retrospective-cycle149","verdict":"refuted","alternative":"The census COV FAIL was only a throughput cap that a retry would clear, and retro-148 being undisposed is a judgement lapse, not a device fault.","discriminating_test":"Offline: parse_type_descriptors on a code-0 TD returns name '0x00' (blind test), and guard_peer.undisposed() on retrospective-cycle148.md returns None despite :371 placeholder.","violations":[{"slug":"inference-over-measurement","loss_min":18,"loss_usd":"?","evidence":"tools/bench/diag_c149_a3_void.py:12"},{"slug":"device-failed","loss_min":4,"loss_usd":1.88,"evidence":"tools/hooks/guard_peer.py:851"}],"sources":["tools/bench/diag_c149_a3_void_s06.log:17","archive/peer/2026-10-08-c149-a3-2-void.md:49","archive/peer/2026-10-08-retrospective-cycle148.md:147","archive/peer/2026-10-08-retrospective-cycle148.md:369","tools/cycle_runner.py:1017","tools/audit_cycle.py:619","tools/hooks/material_marker.log:3595","https://labviewwiki.org/wiki/Type_descriptor"],"note":"Second device failure: guard_bash launch gate refused gate_fp.py log (recipe path only in --cmd arg) twice, the fp-22 class. Audit A4 PASS is false for retro-147/148."}

## Sources

(extract from answer)

## What was done with it

Disposed 2026-10-08 20:50 by the cycle-150 judgement session (`docs/d1/ring-p4c.md` PD364).
- Structural fault (inference-over-measurement: the round-3 Void census ran on a reader whose rate and Void test nobody had
  measured) — ACCEPTED → `docs/violation-decisions.md` 2026-10-08 20:50. The census is WITHDRAWN (PD364(b)); every later
  measurement card on this path checks its reader on a known case and its rate on ≤ 50 reads before a full run.
- device-failed (the disposition check reads the first heading) — ACCEPTED, and wider: a fourth site, `tools/violations.py:177`,
  made the violation counter blind to retrospectives 147–149 → `docs/violation-decisions.md` 2026-10-08 20:50, device built in
  cycle 150 after the s07 card, ALONE (PD364(e)).
- Second device failure in the note (the launch gate refused `gate_fp.py log --cmd` because a recipe path sat inside the quoted
  argument, fp-22 class) — ACCEPTED as a gate false positive: the cycle-150 device card logs it to the gate-fp queue; it is
  drained when the queue is due. A refused log command is queued, never reworded (finding 4).
- Findings 1/2 (item 6 guessed twice; no Error-List-item → object reader) — ACCEPTED: if item 6 survives s07, that reader is
  built ALONE when a judgement orders it, never a third guess (PD364(d)). The bulk terminal-type reader is not built (census
  withdrawn).
- Finding 3 (cycle 148's fake hand-back still unmeasured) — ACCEPTED: PD361(b) stays owed with the deferred tooling card (PD364(f)).
- Finding 5 (ordering) — ACCEPTED: cycle 150 builds s07 first.
- Finding 6 (STATUS 199 lines; A4 false pass; the Error List reader's packages lost by the WMI relaunch) — ACCEPTED: STATUS
  relocation is a cycle-150 purpose item (PD364(h)); A4 is fixed by the device; the chat relaunches the runner with PYTHONPATH
  after cycle 150 (STATUS line 7).
- Finding 7 (judgement inside material: 149-a1-2 copied recipe code around a gate) — ACCEPTED as a finding; a wrong gate is
  queued with `tools/gate_fp.py`, never routed around by copying code.
