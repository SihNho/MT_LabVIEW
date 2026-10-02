# retrospective-cycle134

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.2076  in 50 / out 32671 / cache-create 126076 / cache-read 2726977  (340s, 38 turn(s))
- **date:** 2026-10-02 12:14:25
- **outcome:** ANSWERED (342s)
- **verdict-card:** VERDICT-CARD retrospective-cycle134 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle134.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle134, role retrospective) ---
CLAIM: Cycle 134 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 134 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-02 10:06:30  ..  2026-10-02 12:08:39   (122 min)
    basis: start = archive/peer/2026-10-02-retrospective-cycle133.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-10-02 10:06 .. 2026-10-02 12:08 (122 min, an explicit cycle window): 55 build logs, 10 peer logs, 32 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 55/55 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 15 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 28/32 annotated; blank: ['2026-10-02-hyp-c130-3-x10-selftest.md', '2026-10-02-hyp-c130-4-c128b.md', '2026-10-02-hyp-c130-4-suite-gb.md', '2026-10-02-outcome-review-20261002.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8821 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['diag_c134_6_compile.log', 'selftest_c134_p1_probe.log', 'selftest_stage_prerun_stageplan_c134_2.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 67, failure markers 15, logs carrying a failure 15
  C2 peer reviews dispatched 10, archived 32
  C3 wall-clock inside bgrun, BUILDS ONLY 156 min 41 s
  C4 wall-clock inside bgrun, REVIEWS 11 min 19 s; cost $6.6941 from 5 log(s) that report one
  C4b cost lines seen 5 / parsed 5
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 168 min 0 s  (builds 93%, reviews 6%, judgement session 0%)

  C6 material-marked recipe/bench runs 34, judgement-session attempts refused 7  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/INDEX.md [tools/bench/next.json plan.path]: 300 - STATUS.md, docs/chat-handoff.md, tools/bench/.stall_samples.txt, tools/bench/cards/launches.jsonl, tools/bench/diag_c106e_dryB.txt, tools/bench/diag_c134_1_finalize_b.py, tools/bench/diag_c134_1_graph.py, tools/bench/diag_c134_1_keys.py, tools/bench/diag_c134_3_fsrow.py, tools/bench/diag_c134_3_owners.py, tools/bench/diag_c134_4_chain.py, tools/bench/diag_c134_4_chk.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 349/1143 ok; 794 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2689 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 108 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 691 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one
  PASS  L10 active docs stay <= 400 lines: none over the cap (5 frozen doc(s) not capped)
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1395; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 864
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  PASS  L11 frozen docs carry a FROZEN footer: 5 frozen doc(s), all with a footer

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (56; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure_c134_2.log  (2026-10-02 10:43:37)
tools/bench/c125_1_offline_measure_c134_4.log  (2026-10-02 11:15:16)
tools/bench/diag_c134_1_graph.log  (2026-10-02 10:28:44)
tools/bench/diag_c134_2_finalize_b.log  (2026-10-02 10:56:42)
tools/bench/diag_c134_3_fsrow.log  (2026-10-02 11:00:15)
tools/bench/diag_c134_3_owners.log  (2026-10-02 11:00:41)
tools/bench/diag_c134_3_owners2.log  (2026-10-02 11:01:18)
tools/bench/diag_c134_4_chain.log  (2026-10-02 11:04:47)
tools/bench/diag_c134_4_chk.log  (2026-10-02 11:13:03)
tools/bench/diag_c134_4_crosscheck.log  (2026-10-02 11:11:06)
tools/bench/diag_c134_4_finalize_b.log  (2026-10-02 11:15:59)
tools/bench/diag_c134_4_objdiff.log  (2026-10-02 11:16:45)
tools/bench/diag_c134_4_objdiff2.log  (2026-10-02 11:21:21)
tools/bench/diag_c134_4_restore_b.log  (2026-10-02 11:11:21)
tools/bench/diag_c134_5_census.log  (2026-10-02 11:38:16)
tools/bench/diag_c134_5_cleanup.log  (2026-10-02 11:58:48)
tools/bench/diag_c134_5_el.log  (2026-10-02 11:55:29)
tools/bench/diag_c134_5_el2.log  (2026-10-02 11:58:38)
tools/bench/diag_c134_6_census.log  (2026-10-02 12:03:35)
tools/bench/diag_c134_6_compile.log  (2026-10-02 12:07:03)
tools/bench/diag_c134_6_el_items.log  (2026-10-02 12:04:18)
tools/bench/errorlist_c134_5_scratch_b.log  (2026-10-02 11:55:13)
tools/bench/jev_gate.log  (2026-10-02 12:08:34)
tools/bench/launch_p3b2_c135_dry.log  (2026-10-02 11:34:31)
tools/bench/launch_p3b2_c135_dry_c134_6.log  (2026-10-02 12:06:46)
tools/bench/motor_session_end_cycle133.log  (2026-10-02 10:10:13)
tools/bench/motor_session_start_cycle134.log  (2026-10-02 10:10:22)
tools/bench/selftest_c134_1_a4.log  (2026-10-02 10:34:54)
tools/bench/selftest_c134_1_dry.log  (2026-10-02 10:23:53)
tools/bench/selftest_c134_1_dry_c134_5.log  (2026-10-02 11:28:27)
tools/bench/selftest_c134_1_fsmap.log  (2026-10-02 10:24:38)
tools/bench/selftest_c134_1_fsmap_c134_4.log  (2026-10-02 11:13:51)
tools/bench/selftest_c134_2_gates.log  (2026-10-02 10:44:59)
tools/bench/selftest_c134_2_gates_c134_4.log  (2026-10-02 11:13:50)
tools/bench/selftest_c134_2_regress.log  (2026-10-02 10:55:41)
tools/bench/selftest_c134_4_owners.log  (2026-10-02 11:06:01)
tools/bench/selftest_c134_p1.log  (2026-10-02 11:34:10)
tools/bench/selftest_c134_p1_c134_6.log  (2026-10-02 12:06:34)
tools/bench/selftest_c134_p1_probe.log  (2026-10-02 11:27:15)
tools/bench/selftest_dry_c130_5_c134_2.log  (2026-10-02 10:41:53)
tools/bench/selftest_stage_prerun_stageplan_c134_2.log  (2026-10-02 10:41:43)
tools/bench/selftest_stage_prerun_stageplan_c134_2b.log  (2026-10-02 10:56:19)
tools/bench/stage_d1_ring_p3b2b_scratch_c134_5.log  (2026-10-02 11:37:54)
tools/bench/stage_prerun_c134_1_graph_dry.log  (2026-10-02 10:25:31)
tools/bench/stage_prerun_c134_1_graph_prerun.log  (2026-10-02 10:25:34)
tools/bench/stage_prerun_c134_4_p3b2b_dry.log  (2026-10-02 11:17:26)
tools/bench/stage_prerun_c134_4_p3b2b_prerun.log  (2026-10-02 11:17:50)
tools/bench/stage_prerun_c134_5_p3b2b_dry.log  (2026-10-02 11:38:52)
tools/bench/stage_prerun_c134_5_p3b2b_prerun.log  (2026-10-02 11:39:18)
tools/bench/stage_prerun_c134_5_p3b2b_scr_dry.log  (2026-10-02 11:28:56)
tools/bench/stage_prerun_c134_5_p3b2b_scr_prerun.log  (2026-10-02 11:29:13)
tools/bench/stage_prerun_c134_p1_child_a_dry.log  (2026-10-02 11:34:41)
tools/bench/stage_prerun_c134_p1_child_b_dry.log  (2026-10-02 11:34:42)
tools/bench/stage_prerun_c134_p1_p3b2a_dry.log  (2026-10-02 11:30:05)
tools/bench/stage_prerun_c134_p1_p3b2a_prerun.log  (2026-10-02 11:31:12)
tools/bench/wait_runner_event.log  (2026-10-02 11:42:16)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (10) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_133.log  (2026-10-02 10:10:05)
tools/bench/cycle_134.log  (2026-10-02 10:10:24)
tools/bench/cycle_runner.log  (2026-10-02 10:10:24)
tools/bench/cycle_runner_main_20261002_0312.log  (2026-10-02 10:10:24)
tools/bench/peer_c134_1_dry.log  (2026-10-02 10:22:16)
tools/bench/peer_c134_1_graph.log  (2026-10-02 10:37:44)
tools/bench/peer_c134_4_fs_chain.log  (2026-10-02 11:10:14)
tools/bench/peer_c134_4_objdiff.log  (2026-10-02 11:20:37)
tools/bench/peer_c134_5_el.log  (2026-10-02 11:57:58)
tools/bench/retro.log  (2026-10-02 12:08:38)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle134","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 134 (10:06:30 – 12:08:39)

**Verdict: one structural fault, `repeated-failure-class`.** Session b was finalized on the measured graph two dispatches late. It stopped on a Flat Sequence (FS) owner fact that the plan had already recorded in cycle 132.

Cycle 134 is sound work: it made P3b-2 launch-ready, and its two hypothesis reviews caught real defects. But it closed on the six-dispatch cap without a new bed (`STATUS.md:58`). Two of those six dispatches went to a gap that was knowable before the cycle started.

## The fault

**What happened.** Session b's finalize stopped at action 15 of 18: "no common diagram of #639 and #32464" (`tools/bench/diag_c134_2_finalize_b.log:6`). The cause was that the FS 27509 frames carry owner `['FlatSequenceFrame', 0]` and FS 27509 has no owner entry (`tools/bench/cards/result_134-2.json:22`).

**This fact was already in the plan.** In cycle 132, PD279(b) recorded that "the real graph JSON has no `fs_frames` and frame owners `['FlatSequenceFrame', 0]`" and that stagesim routes FS borders through `owners[frame]` (`docs/d1/ring-p3b.md:99-101`). The rebase path covered it at the time: `carry_fs` set the owners (`ring-p3b.md:110`).

**How it got lost.** PD287(c) dropped the rebase and finalized b directly on the real graph. The FS reader spec that replaced it records frames and borders only (`ring-p3b.md:265-266`; `task_134-1.json:36-37`). Its acceptance fixture compared only the carried map's 6 entries (`result_134-1.json:20`). The owner half of `carry_fs` was dropped and nothing checked for it.

**The plan itself calls it a repeat.** PD289(b) says "Sixth gap, and the same kind as the five before it" (`ring-p3b.md:303`).

**What it cost:**
- The step-4 failure of 134-2.
- All of 134-3: 3 minutes, which ended with "if absent, RETURN" (`result_134-3.json:1`).
- Most of 134-4 (bound 11:02:51). Its first job was the owner fix plus a plan restore. The restore was only needed because the failed finalize had overwritten `plan_ring_p3b2b.json` (`result_134-2.json:23`).
- Finalize then passed in 134-4 (`diag_c134_4_finalize_b.log`, 11:15:59). The next build dispatch bound at 11:24:23 (`guard_card.log:632`). Without the gap it would have bound at about 11:00.

**Loss:** about 24 minutes and 2 of the 6 dispatch slots. The only dollar figure a log carries is the review this gap caused, c134-4-fs-chain, at $1.7334 (`peer_c134_4_fs_chain.log:4`). Material and judgement time carry no cost line, so the dollar loss is unknown.

**Counterfactual.** Suppose 134-1's step b2, or 134-2's step 4, had included the owner conversion that 134-4 later did offline: frame→FS from `fs_frames`, FS→diagram from agreeing outer faces (`ring-p3b.md:313-320`). Then:
- Finalize b would have passed in 134-2 at about 10:58.
- 134-5 and the prep card P1 would have bound at about 11:00 instead of 11:24.
- 134-6 would have been finished by about 11:45, as dispatch 4.
- Dispatch 5 could then have been the one P3b-2 launch. 134-5's scratch b plus its full Error List read took 11:24 → 11:55 (`errorlist_c134_5_scratch_b.log`), and session a is similar, so the launch would have ended around 12:45.

12:45 is inside the 180-minute session cap (13:10), though past the "NEXT by minute 150" guideline. So at best the cycle would have ended with the bed moved to P3b-2 instead of only launch-ready. This is tight but realistic.

## Findings

**1. Repeated failure.**
- The FS-owner gap above: the attempt that should have caught it was 134-1. Step b2's acceptance should have asserted that every FS owner chain closes. That is exactly what `selftest_c134_4_owners` (7/0) checked later.
- A second repeat: the failed finalize overwrote the plan file (`result_134-2.json:23`). PD279(c) had fixed this for rebase only (`ring-p3b.md:103`); finalize has no equivalent protection. Restoring it took a git restore that needed approval and wasn't done (134-2/134-3), then a scripted `cat-file` in 134-4 (`diag_c134_4_restore_b.log`).

**2. Missing tool.**
- A base-graph completeness check: every FS and frame reaches a loop, case or VI diagram. It would have answered 134-2's F1 failure and made 134-3 unnecessary. It now exists as a self-test (`selftest_c134_4_owners`), not as a gate.
- A finalize that does not write the plan on failure.
- An Error List item→uid reader (a `Selection List[]` op). Without it, which 2 items vanished is accepted at class level only (`result_134-6.json:16-17`, PD292(b)).

**3. Unmeasured steps.**
- 134-5's pass list required a *measured* census of session a, but none existed. The CEN2 gate had measured an empty set, `{}`, in cycle 133 (`stage_d1_ring_p3b2a_scratch_c133_6.log:354`), and the retrospective for cycle 133 named that. As a result 134-5 returned FAIL 4/1 (`result_134-5.json:2`), and the item moved to dispatch 6.
- Recipe b writes P3b-1's 53-item list as the expected Error List file. That made the scratch's count-only read fall through to a 1025 s full read by construction (`result_134-5.json:18,27`). This was predictable from the recipe (`stage_d1_ring_p3b2b.py:83-92`).

**4. Rule compliance.**
- CLAUDE.md "guessed twice, build the reader" (`CLAUDE.md:475-481`) is met only formally. The reader was built, but its acceptance omitted a fact the plan had recorded. FS→diagram was then taken from outer-face terminal rows rather than an FS Owner read (PD289(f)). Those rows are LabVIEW-read, so this is defensible.
- Card 134-4 tried the fp-30-refused command 4 times in 7 minutes (`guard_card.log:627-630`), then returned BLOCKED. Chat-P1 item 3 allows equivalent command forms, so this is borderline, not a breach.
- Audit gaps:
  - A4's four blank reviews are cycle-130 files. A4 is day-granular, so it charges them here; all five cycle-134 reviews are annotated.
  - C3 (156 min) and C5 (168 min) exceed the 122-minute window, so nested or parallel bgrun time is double-counted.
  - The audit does not see dispatch-slot use, a plan file overwritten by a failed run, or how much of a recipe a dry actually covered.

**5. Ordering.** 134-2 put the finalize last (step 4), after the a4 debts, gate scoping and `dry_rule`. Yet the finalize is a 15 s offline run (`diag_c134_2_finalize_b.log:9`) and it was the cycle's real unknown. Run first, it would have exposed the gap about 15 minutes earlier, at roughly 10:41 instead of 10:56. Otherwise the order was defensible: the dry-rule device came first, the LabVIEW scratch beside the offline prep card, and the launch deferred because of the cap (PD290(d)).

**6. Not reported.**
- STATUS gives 134-2 → 134-3 → 134-4 as a sequence. It does not say the failure was a fact recorded in PD279(b) (cycle 132).
- It does not say the plan file was overwritten again.
- It presents the 53-item expected file as "not used", which hides its 1025 s cost.
- The PD headers carry impossible clock times: PD290 "12:1x" and PD291 "12:5x" (`ring-p3b.md:321,338`), for decisions dispatched at 11:24 (`guard_card.log:631-632`). PD291's time is after this window ended.

**7. Judgement inside a material session.**
- In card 134-1, the material session accepted all three points of the review of its dry self-test, and changed how the dry gate scopes taint (`archive/peer/2026-10-02-c134-1-dry-selftest.md:122-125`). That is accepting a review finding and changing gate behaviour, which belongs to the judgement session. PD288(a) ratified it afterwards (`ring-p3b.md:280-281`); no cost observed.
- 134-4 chose the "representation, not computation" explanation for the +29 objects (`result_134-4.json:22`). It did so through a hypothesis review, and PD290(b) re-decided it.
- 134-3's "if absent, RETURN" is a scripted conditional, but its action is the protocol default, so it is acceptable.

## Device effect

No device on file failed inside the window.

- **Gate-editing card beside a LabVIEW card (08:25 device):** held. P1's write list holds no stage tool (`task_134-P1.json:40-51`).
- **Dry-rule device (10:10):** no LabVIEW run failed on a gate its dry had computed FALSE. Scratch b passed 20/0 (`stage_d1_ring_p3b2b_scratch_c134_5.log:360-366`). The 134-1 graph read did fail on gate B (`diag_c134_1_graph.log:324`). Its dry never evaluated that gate: coverage 21/83, "unverified 0" (`stage_prerun_c134_1_graph_dry.log:9`). That breaks the spirit but not the letter, and costs nothing, because the read produced the graph that was used later.
- **Offline-classification device (04:52):** it is guard_peer's. fp-30 came from `protocol.check_command`'s deliberately measured named list (`protocol.py:389-398`), was queued as designed, and cost about 7 minutes.
- **Retrospective-debt device:** satisfied. The cycle-133 retrospective is annotated (`retrospective-cycle133.md:394`).
- **rc masking (`unreported-fact`):** the failing self-test in 134-2 ended rc=1 (`selftest_stage_prerun_stageplan_c134_2.log:12`).

VIOLATION: repeated-failure-class | loss_min=24 | loss_usd=? | evidence=tools/bench/diag_c134_2_finalize_b.log:6
VERDICT {"schema":"verdict/1","id":"retrospective-cycle134","verdict":"refuted","alternative":"The FS owner gap was new: the reader spec could not foresee FS 27509 had no owner entry, and 134-3's measure-then-decide was protocol-correct, so the two dispatches were the protocol's price, not a fault.","discriminating_test":"Read ring-p3b.md:99-103 and :110 (PD279(b)/PD280(a), cycle 132): frame owners ['FlatSequenceFrame',0] recorded and set by carry_fs; then task_134-1.json:36-37 - reader spec omits owners. Recorded+omitted => fault.","violations":[{"slug":"repeated-failure-class","loss_min":24,"loss_usd":"?","evidence":"tools/bench/diag_c134_2_finalize_b.log:6"}],"sources":["tools/bench/diag_c134_2_finalize_b.log:6","docs/d1/ring-p3b.md:100","docs/d1/ring-p3b.md:303","tools/bench/cards/result_134-2.json:22","tools/bench/cards/guard_card.log:625","tools/bench/cards/guard_card.log:632","tools/bench/peer_c134_4_fs_chain.log:4"],"note":"Only logged $ for this fault is the fs-chain review $1.7334; material/judgement cost unlogged. Counterfactual launch at ~11:50 ending ~12:45 is tight vs minute-150 NEXT rule."}

## Sources

(extract from answer)

## What was done with it

- **Fault `repeated-failure-class` ACCEPTED** (cycle 134 judgement, close). The discriminating test holds: PD279(b) recorded
  the broken frame owners in cycle 132 and `carry_fs` set them; PD287(c)'s reader spec dropped that half and its acceptance
  never checked owner chains. `docs/violation-decisions.md` `## repeated-failure-class — 2026-10-02 12:2x (cycle 134)`
  (DECISION: device): a base-graph COMPLETENESS gate in finalize and rebase (every FS and frame owner chain reaches a
  loop/case/VI diagram, or is UNMEASURED and unused — `selftest_c134_4_owners` promoted to a gate) + finalize writes the plan
  only on success (PD279(c)'s rule extended from rebase). Built in cycle 135 AFTER the P3b-2 launch (deliverable first);
  before it if the launch runner takes its re-finalize branch.
- Finding 3 (recipe b's 53-item expected file → forced 1025 s full read): accepted; the launch runner gates the range and the
  new bed's expected file comes from the launch's final read (PD291(d)); recipe fix is a carry.
- Finding 5 (finalize last in 134-2): accepted as an ordering lesson — the cycle's real unknown runs first in a card.
- Finding 6 (PD290/291 header times): accepted; those times were estimates, the decisions were taken ~11:2x–12:0x. Not
  rewritten (decision records are not edited); noted here.
- Finding 7 (134-1 material accepted its own review's gate change): ratified by PD288(a); no cost; no device.
- Finding 2 (Error List item→uid reader): not built for this step (PD292(b), class-level acceptance with PD274 precedent).
