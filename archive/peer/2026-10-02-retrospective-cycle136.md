# retrospective-cycle136

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.4000  in 58 / out 44166 / cache-create 123706 / cache-read 2634217  (461s, 47 turn(s))
- **date:** 2026-10-02 15:04:01
- **outcome:** ANSWERED (463s)
- **verdict-card:** VERDICT-CARD retrospective-cycle136 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle136.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle136, role retrospective) ---
CLAIM: Cycle 136 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 136 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-02 12:14:25  ..  2026-10-02 14:56:12   (162 min)
    basis: start = archive/peer/2026-10-02-retrospective-cycle134.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-10-02 12:14 .. 2026-10-02 14:56 (162 min, an explicit cycle window): 56 build logs, 12 peer logs, 39 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 56/56 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 17 logs recorded a failure; unreviewed: ['diag_c136_3_routes.log', 'diag_c136_4_prerun.log', 'wait_runner_event.log']
  FAIL  A4 every archived review says what was done with it: 32/39 annotated; blank: ['2026-10-02-c136-2-condterm-mode-claude.md', '2026-10-02-c136-2-condterm-mode-gemini.md', '2026-10-02-c136-3-c135e-elmismatch.md', '2026-10-02-hyp-c130-3-x10-selftest.md', '2026-10-02-hyp-c130-4-c128b.md', '2026-10-02-hyp-c130-4-suite-gb.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8985 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  PASS  A8 recipe/bench runs ended with a RESULT line (C6): every scoped run in the window printed one (or predates the mark)
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 62, failure markers 17, logs carrying a failure 17
  C2 peer reviews dispatched 12, archived 39
  C3 wall-clock inside bgrun, BUILDS ONLY 232 min 25 s
  C4 wall-clock inside bgrun, REVIEWS 15 min 19 s; cost $4.5604 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 160 min 22 s; cost $71.0550 from 2 log(s) - cycle_135.log, cycle_136.log
  C5 total wall-clock 408 min 6 s  (builds 56%, reviews 3%, judgement session 39%)

  C6 material-marked recipe/bench runs 22, judgement-session attempts refused 1  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/ring-p4.md [tools/bench/next.json plan.path]: 219 - STATUS.md, docs/chat-handoff.md, docs/d1/ring-p3b.md, docs/violation-decisions.md, logs_usage_stop_watch.log, tools/bench/.stall_samples.txt, tools/bench/cards/brief_136.md, tools/bench/cards/launches.jsonl, tools/bench/diag_c134_1_finalize_b.py, tools/bench/diag_c135_2_compare.py, tools/bench/diag_c135_2_resim.py, tools/bench/diag_c135_2_restore.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 349/1150 ok; 801 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  FAIL  L2 every cited project path exists: 2 DANGLING of 2716 citations checked:
       docs/d1/ring-p4.md:131 -> tools/bench/build_oploopendref_v0.py
       STATUS.md:57 -> tools/bench/build_oploopendref_v0.py

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:124 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 698 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  FAIL  L8 decision headers carry HH:MM: 1 header(s) dated >= 2026-09-28 without a parseable HH:MM (violations.py DEC_RE reads them as bare dates): ['docs/violation-decisions.md:1875']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one
  FAIL  L10 active docs stay <= 400 lines: 1 doc(s) over the cap: ['docs/d1/ring-p3b.md 419']. Freeze in place (`status: frozen` + footer, tools/bench/freeze_docs_d1.py) and index what is in force, or split into linked topic files.
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1395; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 864
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  PASS  L11 frozen docs carry a FROZEN footer: 5 frozen doc(s), all with a footer

AUDIT VIOLATIONS: A3 every failing log is followed by an archived review, A4 every archived review says what was done with it, L2 every cited project path exists, L8 decision headers carry HH:MM, L10 active docs stay <= 400 lines


=== BUILD LOGS INSIDE THE WINDOW (57; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure_c135_2.log  (2026-10-02 12:50:09)
tools/bench/diag_c135_2_compare.log  (2026-10-02 12:41:06)
tools/bench/diag_c135_2_resim.log  (2026-10-02 12:41:16)
tools/bench/diag_c135_2_restore.log  (2026-10-02 12:38:18)
tools/bench/diag_c135_3_plandiff.log  (2026-10-02 12:53:22)
tools/bench/diag_c135_4_summarydiff.log  (2026-10-02 12:59:52)
tools/bench/diag_c135_5_delete.log  (2026-10-02 13:24:09)
tools/bench/diag_c135_5_measure.log  (2026-10-02 13:23:26)
tools/bench/diag_c135_5_measure2.log  (2026-10-02 13:23:45)
tools/bench/diag_c135_5_status.log  (2026-10-02 13:24:03)
tools/bench/diag_c135_5_write.log  (2026-10-02 13:23:51)
tools/bench/diag_c136_1_graph.log  (2026-10-02 13:41:13)
tools/bench/diag_c136_2_prerun.log  (2026-10-02 13:55:58)
tools/bench/diag_c136_3_prerun.log  (2026-10-02 14:14:03)
tools/bench/diag_c136_3_routes.log  (2026-10-02 14:20:24)
tools/bench/diag_c136_4_dry.log  (2026-10-02 14:26:12)
tools/bench/diag_c136_4_mem.log  (2026-10-02 14:53:14)
tools/bench/diag_c136_4_prerun.log  (2026-10-02 14:26:15)
tools/bench/jev_gate.log  (2026-10-02 14:55:54)
tools/bench/launch_p3b2_c135.log  (2026-10-02 12:33:33)
tools/bench/launch_p3b2_c135_a.log  (2026-10-02 12:30:06)
tools/bench/launch_p3b2_c135_b.log  (2026-10-02 13:08:29)
tools/bench/launch_p3b2_c135_e.log  (2026-10-02 13:19:43)
tools/bench/launch_p3b2_c135_f.log  (2026-10-02 12:33:29)
tools/bench/launch_p3b2_c135_g.log  (2026-10-02 12:33:00)
tools/bench/launch_p3b2_c135_wait.log  (2026-10-02 12:29:58)
tools/bench/launch_p3b2_resume_c135.log  (2026-10-02 13:19:52)
tools/bench/launch_p3b2_resume_c135_dry.log  (2026-10-02 12:48:00)
tools/bench/launch_p3b2_resume_c135_wait.log  (2026-10-02 13:09:43)
tools/bench/launch_p3b2_resume_c135_wait2.log  (2026-10-02 13:19:52)
tools/bench/motor_session_end_cycle134.log  (2026-10-02 12:15:21)
tools/bench/motor_session_end_cycle135.log  (2026-10-02 13:26:40)
tools/bench/motor_session_start_cycle135.log  (2026-10-02 12:15:30)
tools/bench/motor_session_start_cycle136.log  (2026-10-02 13:26:48)
tools/bench/prep_c136_p1_sim.log  (2026-10-02 13:50:15)
tools/bench/prep_c136_p2_sim.log  (2026-10-02 14:10:39)
tools/bench/prep_c136_p2_sim_noexit.log  (2026-10-02 14:11:21)
tools/bench/selftest_c134_1_dry_c136_p1_diag.log  (2026-10-02 13:34:51)
tools/bench/selftest_c134_1_dry_c136_p1_diag3.log  (2026-10-02 13:35:06)
tools/bench/selftest_c134_1_dry_c136_p1_diag3b.log  (2026-10-02 13:35:31)
tools/bench/selftest_c134_1_dry_c136_p1_diag46.log  (2026-10-02 13:36:06)
tools/bench/selftest_c134_1_dry_c136_p1_t2.log  (2026-10-02 13:33:48)
tools/bench/selftest_c134_1_dry_c136_p2_measure.log  (2026-10-02 14:11:05)
tools/bench/selftest_c135_2_compare.log  (2026-10-02 12:41:06)
tools/bench/selftest_c135_2_device.log  (2026-10-02 12:47:37)
tools/bench/selftest_stage_prerun_c106c_c136_2.log  (2026-10-02 13:55:34)
tools/bench/selftest_x10_c130_1_c136_2.log  (2026-10-02 13:53:06)
tools/bench/selftest_x10_c132_1_c136_2.log  (2026-10-02 13:53:07)
tools/bench/selftest_x10_c132_4_c136_2.log  (2026-10-02 13:52:28)
tools/bench/selftest_x10_c136_2.log  (2026-10-02 13:52:25)
tools/bench/stage_prerun_c135_2_dry_b.log  (2026-10-02 12:38:29)
tools/bench/stage_prerun_c135_2_dry_b2.log  (2026-10-02 12:41:44)
tools/bench/stage_prerun_c135_2_prerun_b.log  (2026-10-02 12:42:39)
tools/bench/wait_c135_1.log  (2026-10-02 12:34:30)
tools/bench/wait_c135_p1.log  (2026-10-02 12:29:29)
tools/bench/wait_c135_p2.log  (2026-10-02 12:36:31)
tools/bench/wait_runner_event.log  (2026-10-02 14:29:03)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (12) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_134.log  (2026-10-02 12:15:13)
tools/bench/cycle_135.log  (2026-10-02 13:26:32)
tools/bench/cycle_136.log  (2026-10-02 14:56:12)
tools/bench/cycle_runner.log  (2026-10-02 13:26:49)
tools/bench/cycle_runner_main_20261002_0312.log  (2026-10-02 12:15:23)
tools/bench/cycle_runner_main_20261002_1215.log  (2026-10-02 13:26:49)
tools/bench/diag_c136_2_peer_fact.log  (2026-10-02 14:03:42)
tools/bench/diag_c136_3_peer_c135e.log  (2026-10-02 14:17:42)
tools/bench/peer_c135_2_launch_compare.log  (2026-10-02 12:46:43)
tools/bench/peer_c135_2_launch_compare2.log  (2026-10-02 12:48:55)
tools/bench/peer_c135_3_plandiff.log  (2026-10-02 12:56:54)
tools/bench/retro.log  (2026-10-02 14:56:12)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle136","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

I traced every cycle-136 card to its log. One fault changed how the cycle ended, and the X10 memory gate counts as a failed device in this window.

**The window covers two cycles.** The window starts at 12:14:25, but cycle 135 ran from 12:15:23 to 13:26:32 (`cycle_runner_main_20261002_1215.log:3-8`). Cycle 136 ran from 13:26:50 to 14:56:12 (`cycle_136.log:1,215`). All `*_c135*` logs, `motor_session_*_cycle135`, and `cycle_135.log`'s $28.29 belong to cycle 135. The audit's C4c figure of $71.06 adds the two cycles together. Cycle 136's judgement session alone cost **$42.76 over 5362 s** (`cycle_136.log:214-215`). C3's 232 build-minutes are also mostly cycle 135. I charge only cycle 136 below.

## The most costly structural fault: the deliverable was ordered behind a measurement that could not answer its question, and the session then stopped with budget left

The cycle's job was the P4 route checks: routes U1–U3, U5, U6 and the W1 `Or` (`brief_136.md:3-13`). Card 136-3 ran them at 14:18. It crashed on op 3 with `#29466 is not in Diagram[22].Nodes[]` (`diag_c136_3_routes.log:36-46`). The material session named the fix as a lookup patch in our own script (`result_136-3.json:24`).

At 14:21 the judgement session did not dispatch that patch and rerun. It dispatched 136-4, a 40-read memory run (`guard_card.log:649`), on the strength of PD300(c): "MEMORY IS THE BINDING CONSTRAINT" (`docs/d1/ring-p4.md:111-116`). That premise was a fit of 0.543 MB/op with SD 10.6. The material's own result next to it said that one file loaded twice differed by 28.8 MB (`result_136-P2.json:19`). Thirty minutes later the session itself called the fit "baseline noise" (`ring-p4.md:121`).

136-4 was also unable to answer the question it was sent for. Its goal was "until error 2 or 1300 MB" (`task_136-4.json:5`), but its stop conditions were 40 reads or 20 minutes (`:22`). From a 576.5 MB start, 40 reads at the model's 2.53 MB per read reaches about 677 MB, not the ~770 MB where error 2 was once seen. The run ended at 653.5 MB, "NOT REACHED" (`diag_c136_4_mem.log:84`).

Then the session ended at 14:56, 89 minutes into a 180-minute budget (`cycle_136.json:20`). It had used 5 of 6 dispatches (`session_8c25435c-….json:1`; `guard_session.py:60`). It wrote the work it had not done into the next cycle's first act (`next.json:4`).

- **Slug:** `wrong-ordering`. It also has an inference component: an unexamined fit set the order, and the read cap was not checked against its target.
- **Loss:** 33 min. That is 136-4's slot from 14:21 to 14:53 (`result_136-4.json:15`), which went ahead of the deliverable, plus a full cycle's deferral. No log ties a dollar figure to this fault, so `loss_usd=?`.
- **Counterfactual:** had the patch-and-rerun gone out at 14:21, the routes would have had verdicts by about 14:40. 136-3's whole card took 15 min, and its run took 125 s (`diag_c136_3_routes.log:72`). 136-4 could then have run from about 14:41 to 15:15. The cycle would have ended about 15:20 with U1–U6 and W1 measured, still 66 minutes inside its budget. Even without reordering, one dispatch and about 90 minutes were left at 14:54. Instead the cycle ended with zero routes measured.

## Device effect

**X10 failed** (`device-failed`, decided 2026-10-02 02:57, "X10 predicts the step's peak"). It failed two ways inside the window.

- **It refused the wrong thing.** At 13:45 it blocked 136-1 as UNMEASURED. It had no branch for stagekit edit diagnostics, a form the card prescribed and "X10 can never pass" (`gate_fp_queue.jsonl:33`). This is the second refusal of the same class after fp-29 (`:29`), and each was patched on its own branch (`stage_prerun.py:1978`, then `:2083`). That is the "one patch per hole" pattern the 2026-09-24 decision rejected.
- **The patch it got is blind to reads, and judgement worked around it by hand.** After 136-2's patch, X10 judged 136-3 with "R 1 reads … 0 executed whole-VI read(s)", predicting 661.9 MB (`diag_c136_3_prerun.log:90-91`). The script has 10 read call sites, which comes to 687.2 MB (`diag_c136_3_routes.py:4-5`). On 136-4 it predicted 592.5 MB with R 2 (`diag_c136_4_prerun.log:105-106`); the run made 40 reads and measured 653.5 MB. Judgement replaced the device's read count with a hand count (PD299(b), `ring-p4.md:96-99`).

Cost: card 136-2, about 15 of its 17 minutes. The $0.48 in that card was the unrelated Stop-If-True fact peer, so `loss_usd=?`. Counterfactual: had fp-29's drain at 07:32 modelled any non-Executor script with reads counted from source, 136-1's prerun at 13:45 would have returned a numeric FAIL inside 136-1. That is about 50 reads, roughly 760 MB on my arithmetic. The reads would have been cut in the same card, and the 136-2 dispatch would not have existed.

The other devices held or were not exercised:
- **bgrun inner-FAIL → rc=1:** worked (`diag_c136_3_routes.log:70-72`).
- **peer.ps1 adversarial set:** worked (`archive/peer/2026-10-02-c136-3-c135e-elmismatch.md:34-40`).
- **guard_peer refusal while a review is owed:** fired correctly at 136-3 (`result_136-3.json:21`), but it was satisfied by dispatching the review alone; the disposition is still blank.
- **Cost regex:** worked (C4b 4/4).
- **LabVIEW-card-beside-tool-writer refusal:** held. 136-2 wrote `stage_prerun.py` only after 136-1 had returned.
- **C7 scope counter:** saturated at 219 files, so it carries no signal. It is a counter by design, so I record this as a finding.
- **Prior-art review, guard_cycle and the stop record:** no recipe build this cycle, so not exercised.

## FINDINGS

**1. Repeated failure.**
- X10 refused a non-Executor script as UNMEASURED twice: fp-29 in cycle 132, read-only, and fp-33 in cycle 136, edit (`gate_fp_queue.jsonl:29,33`). The approach should have changed at fp-29, the first occurrence: model any script from its source call sites instead of adding a branch per script kind.
- The same offline self-test was refused by two gates on two occasions: fp-30 in guard_bash, then fp-32 in guard_peer (`gate_fp_queue.jsonl:30,32`; `guard_card.log:643-644`, refused at 13:32 and 13:36).
- The two plan-replay stops have different causes, so they are not a repeat: P1 at action 64 (`prep_c136_p1_sim.log:78-80`) and P2 at step 102 (`prep_c136_p2_sim.log:105`).

**2. Missing tool.**
- **A source-counted read meter for X10.** Its absence produced fp-33 and the blind PASSes on 136-3 and 136-4.
- **A Stop-If-True / Mechanical Action reader.** It was asked for in three cards and delivered in none: 136-1 item 4, 136-2 item 5 (where building it was forbidden, `task_136-2.json:53`), and 136-3 item 4 (permitted but not reached). PD298(e) depends on it.
- **A wrong citation in the cycle's own documents.** `ring-p4.md:131` and `STATUS.md:57` cite the reader's pattern at `tools/bench/build_oploopendref_v0.py`. The file is at `tools/recipes/` (audit L2).

**3. Unmeasured steps.**
- PD300(c) was accepted against its own evidence. The discriminating measurement, a fresh-start memory read, took about 60 s (`diag_c136_4_mem.log:114`). A 40-read run was not needed for it.
- 136-4's read cap was never checked against its 770 MB target.
- The bed load entered into the memory model as 600.2 MB (`diag_c136_1_graph.log:24`) is one reading. The same file loaded at 576.5 MB in 136-4 (`diag_c136_4_mem.log:85`).

**4. Rule compliance.**
- **Ended a turn expecting to be resumed.** The session's last message reads "The retrospective is running in the background. I'll wait for it and record what it finds." (`cycle_136.log:214`). That breaks the session's own rule at `cycle_136.log:183-187`.
- **A3, failing log not reviewed.** `diag_c136_3_routes.log` failed with rc=1 and has no review. PD301(c) waives one ("no review owed"), so it complies only on paper, and guard_peer may refuse cycle 137's first LabVIEW card on it.
- **A4, dispositions left blank.** The c135e review says the bed's expected Error List was "fitted to the result it is supposed to judge" (`elmismatch.md:65`). Its disposition is blank (`:91-93`), and so are both condterm reviews.
- **Doc limits:** STATUS is 124 lines, over the 110 cap; `ring-p3b.md` is 419 lines, over the 400 cap.
- **Not done:** 136-P2's "delete v2 step files" rule; the permission layer refused it, and the card reported that.
- **What the audit does not cover:**
  - whether the cycle delivered its act;
  - unused budget and dispatches;
  - X10's predicted peak against the measured peak;
  - whether a review's substance was acted on;
  - that the window spans two cycles;
  - the session's final message.

**5. Ordering.** Not defensible, as set out in the fault above. Also, 136-1 was written in a form that, by `result_136-1.json:20`, no edit diagnostic had passed prerun in since card 130. The X10 edit branch should have come first.

**6. What was not reported.**
- **"Memory wall … refuted" overstates.** STATUS line 58 says this, but error 2 was never reached and the 690/700 stops are unchanged (`ring-p4.md:125-126`). Only the cumulative-growth premise was refuted.
- **"P4 feasible in fresh sessions" is not measured.** STATUS line 64 says this, but v3's session table is still owed (`next.json:11`).
- **X10's 61 MB under-prediction is not reported as an X10 miss.**
- **The c135e finding is reduced to a "carry".** The review questions the current bed's acceptance; STATUS:57 lists it only as a carry.
- **Unused budget and cycle cost are not stated:** 89 of 180 minutes, 5 of 6 dispatches, and $42.76.
- **A dropped measurement is mentioned only in a note:** 136-3 stopped reading the TS index_mode (`result_136-3.json:28`).

**7. Judgement inside a material session.**
- **136-3** reordered its parts and dropped the index_mode read (`result_136-3.json:28`). That is a measurement-scope decision.
- **136-P1** deferred PD293(b)'s "to 1.7 only when valid" clause to P5 (`result_136-P1.json:22`). I found no ratification in PD298 (`ring-p4.md:63-91`).
- **136-P2** chose t5111 for the n2 source. It flagged the choice, and PD300(b) ratified it (`ring-p4.md:109-110`), so that one is acceptable.

VIOLATION: wrong-ordering | loss_min=33 | loss_usd=? | evidence=tools/bench/cards/task_136-4.json:22
VIOLATION: device-failed | loss_min=15 | loss_usd=? | evidence=tools/bench/diag_c136_3_prerun.log:90
VERDICT {"schema":"verdict/1","id":"retrospective-cycle136","verdict":"refuted","alternative":"The session ended at 14:56 because something not in the files forced it (an unlogged guard refusal of a 6th dispatch, or a budget it misread), so the order of 136-4 before the route rerun cost nothing.","discriminating_test":"Look in the cycle-136 session transcript and the guard_session/guard_card logs after 14:53 for a refused dispatch. If one exists, the early end was forced and the wrong-ordering loss falls to the 136-4 slot alone.","violations":[{"slug":"wrong-ordering","loss_min":33,"loss_usd":"?","evidence":"tools/bench/cards/task_136-4.json:22"},{"slug":"device-failed","loss_min":15,"loss_usd":"?","evidence":"tools/bench/diag_c136_3_prerun.log:90"}],"sources":["tools/bench/diag_c136_3_routes.log:36-46","tools/bench/session_8c25435c-d4a0-451f-a71a-3c8f8910def2.json:1","tools/bench/cycle_136.log:214-215","docs/d1/ring-p4.md:111-126","tools/bench/cards/result_136-P2.json:19","tools/bench/diag_c136_4_mem.log:84-86","tools/bench/diag_c136_4_prerun.log:105","tools/bench/gate_fp_queue.jsonl:29,33"],"note":"The window also covers cycle 135 (12:15-13:26). Cycle 136 alone: 13:26:50-14:56:12, judgement $42.76. X10 refused wrongly (fp-33), and after its patch it counts 0 of 10 reads; PD299(b) replaced its count with a hand count."}

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
