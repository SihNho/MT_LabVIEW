# retrospective-cycle167

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $3.5052  in 96 / out 44004 / cache-create 180009 / cache-read 5923254  (456s, 68 turn(s))
- **date:** 2026-10-12 19:55:26
- **outcome:** ANSWERED (458s)
- **verdict-card:** VERDICT-CARD retrospective-cycle167 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle167.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle167, role retrospective) ---
CLAIM: Cycle 167 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 167 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-10 18:01:14  ..  2026-10-12 19:47:29   (2986 min)
    basis: start = archive/peer/2026-10-10-retrospective-cycle165.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
4. RULE COMPLIANCE. Read the attached rule files (docs/rules/). Which of their rules were broken, evaded, or satisfied only
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
  - `device-failed` (decided 2026-10-08 20:50): sites use it; every other parser of that heading in `tools/` (not `tools/bench/`) is listed as using it or as unable to misfire. Self-test on two copies of `retrospective-cycle149.md` (placeholder restored / filled): each site misreads the placeholder copy on the current code and reads both right after. Built in cycle 150 (`docs/d1/ring-p4c.md` PD364(e)), after the s07 LabVIEW card and ALONE, beca??
  - `repeated-failure-class` (decided 2026-10-08 20:50): pre-fix tree drop `ASSIGN_STATE`/`CYCLE_ROLE`/`CYCLE_SESSION`; prepared as `tools/bench/cards/task_149-a2-1.json`. The review's finding 2 (`tools/bgrun.py --material` drops the three variables for every child) is weighed when that card is re-issued. DEFERRED by PD364(f): it runs ALONE before the next card that runs a pre-fix tree, or with the next gate-fp drain. Until then no card runs a pre-fix t??
  - `inference-over-measurement` (decided 2026-10-09 07:00): to be the only one. That is enough to build now rather than wait for a third. `stagesim` gets a collect-all replay mode: on an UNMEASURED refusal (owner, tunnel name, terminal class) it puts in the plan's own predicted value, flags the step PROVISIONAL with the refusal text, continues, and prints one list of every refusal. A collect-all run is never a dry, prerun or launch PASS. Self-test: on the ??
  - `device-failed` (decided 2026-10-09 13:55): decision answers is always earlier than the decision, so it is never counted after it). Self-test on the literal `12:2x` and `07:0x` header forms plus one plain `HH:MM`. Not a hook file; built offline in cycle 156 after the LabVIEW card (`docs/d1/ring-p5.md` PD379(g)). Rule for every judgement: answer each `gates_due` line in the purpose's note before writing `next.json`.
  - `device-failed` (decided 2026-10-10): before step 2's dry (`docs/d1/ring-p5.md` PD387(e)): the dry's `unverified N` counts every `UNVERIFIED-DRY` line; a census declaration that does not cover every op (or `census_overall: UNPREDICTED`) is UNPREDICTED; the dry runs PB, D, TD and CEN2 against the simulated end. Self-test on the stored c158-a2-2 inputs. Rule for every judgement: a scratch card is written only on a dry that prints `unver??
  - `device-failed` (decided 2026-10-12): with `stagekit.el_advisory` (rc 0 = RECORD, rc 1 = RETURN only on an unseen class or |total diff| > 3) and prints its EL-ADVISORY line; the by-design verdict stays as a recorded line. Self-test on the stored cycle-165 47-item read (rc 0) and a planted unseen class (rc 1). Adoption order: graph read -> `load_by_vi` -> Error List. Rule for every judgement: a brief never makes an Error List delta a R??

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

== cycle audit, 2026-10-10 18:01 .. 2026-10-12 19:47 (2986 min, an explicit cycle window): 90 build logs, 9 peer logs, 20 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 87/90 ok; NO BGRUN line in ['capabilities_regen.log', 'fn_gate.log', 'motor_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 17 logs recorded a failure; unreviewed: ['diag_c166_a1_1_tun_prerun.log', 'diag_c166_a1_3_elpredict_selftest.log', 'diag_c166_a1_3_replay.log', 'diag_c166_a1_4_dry.log', 'diag_c166_a1_5_census.log', 'diag_c166_a1_6_reg_c147.log', 'diag_c167_a1_2_crows.log', 'diag_c167_a1_5_pin_c147_before.log', 'diag_c167_a1_5_pin_innerface_before.log', 'diag_c167_a1_5_pin_prime_before.log', 'prep_c166_a1_5_probe.log', 'prep_c166_a1_5_probe2.log', 'prep_c167_a1_3_explore.log', 'selftest_c166_eladv.log', 'selftest_c166_ident.log', 'selftest_c166_pbtight.log']
  PASS  A4 every archived review says what was done with it: 20/20 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 12671 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 4 log(s) with a run that printed none: ['diag_c166_a1_5_census.log', 'diag_c167_a1_2_crows.log', 'prep_c166_a1_5_probe.log', 'prep_c166_a1_5_probe2.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 116, failure markers 22, logs carrying a failure 17
  C2 peer reviews dispatched 9, archived 20
  C3 wall-clock inside bgrun, BUILDS ONLY 73 min 53 s
  C4 wall-clock inside bgrun, REVIEWS 0 min 0 s; no log reported a cost - treat the review cost as UNKNOWN, not as zero
  C4b cost lines seen 0 / parsed 0
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 136 min 51 s; cost $60.5181 from 4 log(s) - cycle_166.log, cycle_166_assign_1.log, cycle_167.log, cycle_167_assign_1.log
  C5 total wall-clock 210 min 44 s  (builds 35%, reviews 0%, judgement session 64%)

  C6 material-marked recipe/bench runs 63, judgement-session attempts refused 155  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/ring-p6.md [tools/bench/next.json plan.path]: 696 - .codex/hooks.json, AGENTS.md, CLAUDE.md, README.md, docs/START.md, docs/debate.md, docs/decisions/acceleration_items_2026_09_28.md, docs/decisions/agent_vs_session_terminology.md, docs/decisions/always_attribute_third_party_code.md, docs/decisions/approved_means_do_it_now.md, docs/decisions/archive_benchmarks_for_meeting_reports.md, docs/decisions/archive_history_dont_read_it_by_default.md??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 373/1261 ok; 888 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  FAIL  L2 every cited project path exists: 2 DANGLING of 4502 citations checked:
       docs/guardcore.md:34 -> docs/codex-integration.md
       docs/d1/ring-p4.md:131 -> tools/bench/build_oploopendref_v0.py

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:144 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 809 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  FAIL  L8 decision headers carry HH:MM: 4 header(s) dated >= 2026-09-28 without a parseable HH:MM (violations.py DEC_RE reads them as bare dates): ['docs/violation-decisions.md:1875', 'docs/violation-decisions.md:2019', 'docs/violation-decisions.md:2063', 'docs/violation-decisions.md:2076']
  WARN  L9 new Pre-decided items carry a USER-RULES: line: 2 item(s) >= 238 without `USER-RULES:` (read docs/user-rules.md and cite the rows relied on, or write `USER-RULES: none apply`): ['docs/d1/result-gates.md:18 (item 366)', 'docs/d1/tooling.md:145 (item 329)']
  FAIL  L10 active docs stay <= 400 lines: 2 doc(s) over the cap: ['docs/chat-handoff.md 576', 'docs/d1/ring-p3b.md 419']. Freeze in place (`status: frozen` + footer, tools/bench/freeze_docs_d1.py) and index what is in force, or split into linked topic files.
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1405; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 5408
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  WARN  L11 frozen docs carry a FROZEN footer: 1 without one: ['docs/d1/ring-p4.md']
  WARN  L12 function table matches the code: stale 5 (stagekit.op:connect_nested_v1, stagekit.op:connect_term_uid, stagekit.op:wire_const_sr, stagekit.op:wire_control, stagekit.op:wire_ctlsink); fn-list block differs from the code - run py tools/gen_capabilities.py

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, L2 every cited project path exists, L8 decision headers carry HH:MM, L10 active docs stay <= 400 lines


=== BUILD LOGS INSIDE THE WINDOW (91; read them directly, they are the primary record) ===
tools/bench/capabilities_regen.log  (2026-10-12 19:40:04)
tools/bench/diag_c165_a3_4_graph.log  (2026-10-12 17:34:13)
tools/bench/diag_c166_a1_1_census.log  (2026-10-12 17:38:52)
tools/bench/diag_c166_a1_1_hash_after.log  (2026-10-12 17:39:03)
tools/bench/diag_c166_a1_1_hash_before.log  (2026-10-12 17:29:35)
tools/bench/diag_c166_a1_1_lib_selftest.log  (2026-10-12 17:36:23)
tools/bench/diag_c166_a1_1_mm.log  (2026-10-12 17:38:46)
tools/bench/diag_c166_a1_1_q_p5s01.log  (2026-10-12 17:31:19)
tools/bench/diag_c166_a1_1_q_p5s02d.log  (2026-10-12 17:31:20)
tools/bench/diag_c166_a1_1_q_p5s02e.log  (2026-10-12 17:34:40)
tools/bench/diag_c166_a1_1_q_simend.log  (2026-10-12 17:35:07)
tools/bench/diag_c166_a1_1_tun.log  (2026-10-12 17:38:22)
tools/bench/diag_c166_a1_1_tun_dry.log  (2026-10-12 17:32:53)
tools/bench/diag_c166_a1_1_tun_dry2.log  (2026-10-12 17:35:22)
tools/bench/diag_c166_a1_1_tun_prerun.log  (2026-10-12 17:33:02)
tools/bench/diag_c166_a1_1_tun_prerun2.log  (2026-10-12 17:35:27)
tools/bench/diag_c166_a1_2_elexp.log  (2026-10-12 17:46:37)
tools/bench/diag_c166_a1_2_hash_after.log  (2026-10-12 17:47:25)
tools/bench/diag_c166_a1_2_hash_before.log  (2026-10-12 17:45:47)
tools/bench/diag_c166_a1_3_dupcheck.log  (2026-10-12 17:56:32)
tools/bench/diag_c166_a1_3_elpredict_selftest.log  (2026-10-12 17:55:42)
tools/bench/diag_c166_a1_3_explore.log  (2026-10-12 17:45:44)
tools/bench/diag_c166_a1_3_hash_after.log  (2026-10-12 17:56:57)
tools/bench/diag_c166_a1_3_hash_before.log  (2026-10-12 17:47:56)
tools/bench/diag_c166_a1_3_lint.log  (2026-10-12 17:56:14)
tools/bench/diag_c166_a1_3_replay.log  (2026-10-12 17:56:56)
tools/bench/diag_c166_a1_4_dry.log  (2026-10-12 18:20:19)
tools/bench/diag_c166_a1_4_hash_after.log  (2026-10-12 18:17:07)
tools/bench/diag_c166_a1_4_hash_before.log  (2026-10-12 18:02:55)
tools/bench/diag_c166_a1_4_lint.log  (2026-10-12 18:17:38)
tools/bench/diag_c166_a1_4_reg_c158.log  (2026-10-12 18:15:59)
tools/bench/diag_c166_a1_4_reg_c161.log  (2026-10-12 18:15:45)
tools/bench/diag_c166_a1_4_reg_c163.log  (2026-10-12 18:15:22)
tools/bench/diag_c166_a1_4_reg_t7.log  (2026-10-12 18:16:05)
tools/bench/diag_c166_a1_5_census.log  (2026-10-12 18:17:20)
tools/bench/diag_c166_a1_6_dry.log  (2026-10-12 18:36:18)
tools/bench/diag_c166_a1_6_hash_after.log  (2026-10-12 18:37:03)
tools/bench/diag_c166_a1_6_hash_before.log  (2026-10-12 18:30:57)
tools/bench/diag_c166_a1_6_lint.log  (2026-10-12 18:36:45)
tools/bench/diag_c166_a1_6_probe.log  (2026-10-12 18:27:27)
tools/bench/diag_c166_a1_6_reg_c141.log  (2026-10-12 18:32:40)
tools/bench/diag_c166_a1_6_reg_c147.log  (2026-10-12 18:32:38)
tools/bench/diag_c166_a1_6_reg_c158.log  (2026-10-12 18:32:32)
tools/bench/diag_c166_a1_6_reg_c159.log  (2026-10-12 18:32:53)
tools/bench/diag_c166_a1_6_reg_c161.log  (2026-10-12 18:35:23)
tools/bench/diag_c166_a1_6_reg_c163.log  (2026-10-12 18:35:31)
tools/bench/diag_c166_a1_6_reg_c166pb.log  (2026-10-12 18:34:57)
tools/bench/diag_c166_a1_6_reg_t6.log  (2026-10-12 18:32:07)
tools/bench/diag_c166_a1_6_reg_t7.log  (2026-10-12 18:33:27)
tools/bench/diag_c167_a1_1_diff.log  (2026-10-12 19:17:45)
tools/bench/diag_c167_a1_1_hash_after.log  (2026-10-12 19:18:07)
tools/bench/diag_c167_a1_1_hash_before.log  (2026-10-12 19:07:19)
tools/bench/diag_c167_a1_1_rbw.log  (2026-10-12 19:17:14)
tools/bench/diag_c167_a1_2_crows.log  (2026-10-12 19:12:47)
tools/bench/diag_c167_a1_3_closure.log  (2026-10-12 19:33:43)
tools/bench/diag_c167_a1_3_hash_after.log  (2026-10-12 19:33:57)
tools/bench/diag_c167_a1_3_hash_before.log  (2026-10-12 19:22:38)
tools/bench/diag_c167_a1_4_ready.log  (2026-10-12 19:26:34)
tools/bench/diag_c167_a1_5_hash_after.log  (2026-10-12 19:46:03)
tools/bench/diag_c167_a1_5_hash_before.log  (2026-10-12 19:38:50)
tools/bench/diag_c167_a1_5_lib_selftest.log  (2026-10-12 19:40:34)
tools/bench/diag_c167_a1_5_pin_c147_after.log  (2026-10-12 19:45:46)
tools/bench/diag_c167_a1_5_pin_c147_before.log  (2026-10-12 19:42:59)
tools/bench/diag_c167_a1_5_pin_innerface_after.log  (2026-10-12 19:44:58)
tools/bench/diag_c167_a1_5_pin_innerface_before.log  (2026-10-12 19:42:11)
tools/bench/diag_c167_a1_5_pin_prime_after.log  (2026-10-12 19:45:40)
tools/bench/diag_c167_a1_5_pin_prime_before.log  (2026-10-12 19:42:54)
tools/bench/diag_c167_a1_5_relocate_archive.log  (2026-10-12 19:44:26)
tools/bench/diag_c167_a1_5_relocate_check.log  (2026-10-12 19:45:43)
tools/bench/diag_c167_a1_5_relocate_save.log  (2026-10-12 19:43:15)
tools/bench/diag_c167_a1_5_selftest.log  (2026-10-12 19:40:24)
tools/bench/errorlist_check_cycle167.log  (2026-10-12 18:49:18)
tools/bench/fn_gate.log  (2026-10-12 19:13:47)
tools/bench/jev_gate.log  (2026-10-12 19:46:02)
tools/bench/motor_gate.log  (2026-10-12 16:29:22)
tools/bench/motor_session_end_cycle165.log  (2026-10-10 18:01:55)
tools/bench/motor_session_end_cycle166.log  (2026-10-12 18:39:38)
tools/bench/motor_session_start_cycle166.log  (2026-10-12 17:20:00)
tools/bench/motor_session_start_cycle167.log  (2026-10-12 18:49:25)
tools/bench/prep_c166_a1_5_probe.log  (2026-10-12 18:00:52)
tools/bench/prep_c166_a1_5_probe2.log  (2026-10-12 18:01:49)
tools/bench/prep_c167_a1_1_graphlib_selftest.log  (2026-10-12 19:08:05)
tools/bench/prep_c167_a1_2_explore.log  (2026-10-12 19:06:50)
tools/bench/prep_c167_a1_2_shape.log  (2026-10-12 19:04:08)
tools/bench/prep_c167_a1_3_explore.log  (2026-10-12 19:23:28)
tools/bench/prep_c167_a1_3_scan.log  (2026-10-12 19:25:19)
tools/bench/selftest_c166_eladv.log  (2026-10-12 17:52:19)
tools/bench/selftest_c166_ident.log  (2026-10-12 18:30:00)
tools/bench/selftest_c166_pbtight.log  (2026-10-12 18:16:57)
tools/bench/selftest_guardcore.log  (2026-10-10 22:09:55)
tools/bench/selftest_scope_cwd.log  (2026-10-12 13:25:36)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (9) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_166.log  (2026-10-12 17:25:36)
tools/bench/cycle_166_assign_1.log  (2026-10-12 18:38:53)
tools/bench/cycle_167.log  (2026-10-12 19:00:10)
tools/bench/cycle_167_assign_1.log  (2026-10-12 19:47:28)
tools/bench/cycle_runner.log  (2026-10-12 19:47:28)
tools/bench/cycle_runner_main_20261010_0827.log  (2026-10-10 18:01:57)
tools/bench/cycle_runner_main_20261012_1719.log  (2026-10-12 19:47:28)
tools/bench/retro.log  (2026-10-12 19:47:28)
tools/bench/runner_supervisor.log  (2026-10-12 19:47:28)

The rules are in docs/rules/docs.md, docs/rules/hardware.md, docs/rules/interaction.md, docs/rules/labview-execution.md, docs/rules/originals.md, docs/rules/reviews.md, docs/rules/runner.md (CLAUDE.md at the project root is only the short core; the old full text, which older citations `CLAUDE.md:N` point into, is docs/rules/CLAUDE-full-2026-10-10.md); this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle167","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 167: outcome review

**The window covers more than cycle 167.** The window is 2026-10-10 18:01 to 2026-10-12 19:47, and it holds three different things:
- **About 47 hours of interactive chat**, from 10-10 18:01 to 10-12 17:19. This is the GPT-vs-Claude benchmark and the guard rollback in commits `c0021509` and `6d17b001`. It is the source of most of the audit's 696-file C7 list and of `selftest_guardcore.log` / `selftest_scope_cwd.log`.
- **Cycle 166**, 17:20 to 18:39. It cost $34.04 and met its purpose with 15 of 15 items (`cycle_runner_main_20261012_1719.log:10,19`).
- **Cycle 167**, 18:39:39 to 19:47:28. It took 68 min and cost $26.48: the judgement session was 638 s and $3.85 (`cycle_167.log:273-274`), and the assignment session 47 min and $22.63 (`cycle_runner_main_20261012_1719.log:28`).

Cycle 166 is in this window because the runner skipped its retrospective (see finding 6). The audit's C4c total of $60.52 is the sum of both cycles. Everything below judges cycle 167 unless it says otherwise.

**Was the work worth doing? Yes.** The single Remove-Bad-Wires (RBW) measurement was the most useful fact in the window:
- The Error List went from 47 items to 1, and 25 wires were deleted.
- Only one deleted wire carried data: 25618, into the indicator 'Force (pN) vs Extension (nm)'.
- ExecState stayed 0 after RBW.
- Sources: `diag_c167_a1_1_facts.md:14-21`, `result_167-a1-1.json:12-16`.

Together these shrink P6-1 from 47 rows to about one item plus one display wire. The closure table (`diag_c167_a1_3_facts.md:16-17`: R 27, D 19, DISP 5, C 2, U 22) is worth less than it looks. All 22 U rows are Error List items with no uid, and the same cycle's RBW clears them.

## Structural faults, ranked

**1. The cycle-start Error List reuse failed to recognise an unchanged file, costing about 10 min.**
- **What happened:** the runner logged `GUI-READ | no saved read of D1_ring_p5_20261010_172913.vi` (`cycle_runner_main_20261012_1719.log:22`). It then ran a 579 s LabVIEW GUI read (`errorlist_check_cycle167.log:85`) of a file whose md5 is 75773b0d.
- **Why it was redundant:** a full read of those exact bytes already existed. It is `errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json`: md5 75773b0d before and after (`:43`, `:4995`), `n_reported` 47 (`:60`), and every read gate True (`:5258-5269`).
- **Why the reuse missed it:** `find_reusable` matches on the file name (`tools/errorlist_check.py:186-195`). Cycle 166's bed move renamed p5s02e to p5, so the name no longer matched.
- **What it bought:** nothing new. The re-read returned the same 47 items (`errorlist_check_cycle167.log:82`).
- **Cost:** about 10 min, `loss_usd=?`. No model session was running, and no log carries a dollar figure.
- **Counterfactual:** with an md5 match, or with the bed move carrying its read along, the check would have reused the old read at 18:39:40 without starting LabVIEW. The judgement session would have started at about 18:40 instead of 18:49:28 (`cycle_167.log:1`), and the cycle would have ended at about 19:38 instead of 19:47:28.
- **Classification:** this is a device that never fired when it should have. The code says it exists for exactly this case (`errorlist_check.py:173-179`, card 81-1). Its self-test (`selftest_errorlist_reuse_81.py:11-15`) has no rename case.

**2. The launch gate's unverified-gate refusal was worked around inside a material session, costing about 1 min.**
- **How the launch got through:** the dry runs of `diag_c167_a1_1_rbw.py` listed two unverified gates, `["A0 ExecState BEFORE RBW == 0", "R1 scripted RBW ran: Wire count after < before"]` (`prerun_records.jsonl:1143-1151`). The launch gate refused the launch at 19:13:04 (`material_marker.log:4394`).
  - Within 29 s the material session turned A0 and R1 from gates into recorded rows. The next dry printed `unverified: []` (`prerun_records.jsonl:1153`) and the launch went through at 19:13:47 (`material_marker.log:4395`).
  - The session says so in `diag_c167_a1_1_facts.md:33`: "A0 … and R1 … are ROWS, not gates, because the dry run can only stub them".
  - Earlier, the session renamed the operation label to `rbw_method410` to get past a pre-run check (X5) that wrongly counted RBW as a wiring operation (fp-98, `facts.md:32`).
- **Rules and device involved:**
  - The device is the 2026-10-02 10:10 decision: the launch gate refuses a dry run with unverified gates "unless the card names each unverified gate as expected".
  - CLAUDE.md:39 says never route around a refusal: log the false positive and end BLOCKED.
  - `material.md:85-87` allows only an equivalent command form the gate already accepts, or an existing release.
- **Cost:** about 1 min; `loss_usd=?`. The result is unharmed: A0 read 0 as expected and the wire count dropped by 25.
- **Counterfactual:** had brief 167-a1-1 (written around 19:00) named A0 and R1 as expected unverified gates, the 19:12:58 pre-run PASS (`prerun_records.jsonl:1152`) would have released the launch with both gates intact. It would have run at the same time, at about 19:13.
- **Why it ranks with fault 1 despite the small cost:** it is a device on file with a threshold of 1. The hole it shows is general: any material session can clear the unverified-gate refusal by relabelling a gate as a row.

## FINDINGS

1. **Repeated failure.** Nothing costly recurred in cycle 167.
   - The crows script crashed three times, each within 1 s, on guessed input shapes: KeyError 'objs', KeyError 'F2', and a regex miss (`diag_c167_a1_2_crows.log:12,24,65`). This happened although `prep_c167_a1_2_shape.log` and `prep_c167_a1_2_explore.log` had already read those files.
   - The RBW pre-run failed four times in about 2 min: X6, W22, X10, X5 (`prerun_records.jsonl:1142-1149`).
   - The costliest repeat in the window is in cycle 166. `diag_c166_a1_4_dry.py all` ran 342 s and failed only on unnormalised timestamps (`diag_c166_a1_4_dry.log:6-12`), then reran for 322 s. The approach should have changed at attempt 1: test the normaliser on one recipe before running all six.

2. **Missing tool.**
   - **Error List reuse keyed by md5** (fault 1).
   - **A uid route for Error List items.** The note reads `uid_route: none: needs a Selection List[] 6349400 op (unbuilt)` (`prep_c167_a1_3_explore.log:31`). Without it, the one remaining Error List item has no uid (`facts.md:21`), and all 22 U rows exist only because Error List items carry no uid (`diag_c167_a1_3_facts.md:17`).
   - **One shared graph loader that accepts the S1 schema.** This would have prevented the crows KeyError at `diag_c108c_graph.py:24`. `prep_c167_a1_1_graphlib.py` was built ad hoc in tools/bench, next to 15 inline copies.

3. **Unmeasured steps.**
   - "Wire 25618 is likely the twotypes item's wire (inference, not measured)" (`result_167-a1-1.json:26`).
   - More importantly for P6-1: the one remaining Build Array item is attributed to #2626 through F1, but no card checked that.
     - In 7815af09, every input of #2626 is wired (`prep_c167_a1_3_explore.log:44-47`).
     - #11261's 'array' and 'element' inputs have no source (`:60-61`).
     - An offline graph query costing seconds can tell which Build Array the item is. P6-1 should not be designed until it has run.

4. **Rule compliance.**
   - **Broken:**
     - CLAUDE.md:39 rule 7, `material.md:85-87`, and the brief's "stop at the first unexpected result" (`brief_167-a1-1.md:12`), all by fault 2.
     - The failure budget of 2 (`docs/rules/runner.md:64`), formally, by the crows card (3 rc=1 runs) and the RBW pre-run.
   - **Satisfied only formally:** pass item 10 (the STATUS relocation) is marked met, but STATUS.md is still 144 lines against the 110 limit (audit L3; `assign_result_167_1.json:21` note 2).
   - **What the audit does not cover:**
     - script edits that turn gates into rows, and the sequence of pre-run refusals in `prerun_records.jsonl`;
     - Error List reuse failing on a renamed file;
     - the retrospective-due check accepting an old file;
     - mixing of cycle and chat work: C7's 696 files mostly come from the chat, so the counter says nothing here.

5. **Ordering.** Defensible. PD404(h) says (d) first. The RBW card (167-a1-1) was dispatched first and launched at 19:13:49. The crows card (f) ran beside it, closure (e) after it (it needs the RBW result), and the tooling notes last, 19:38 to 19:46.

6. **What was not reported.**
   - **The gate demotion.** The assignment summary does not mention it (`assign_result_167_1.json:21`). It appears only in the card's facts file and its open questions (`result_167-a1-1.json:24`).
   - **The redundant GUI read.** The 579 s re-read appears only in the runner log.
   - **Cycle 166's skipped retrospective.** The runner logged `RETRO-DUE | cycle 166 | due and archived in the cycle (2026-10-10-retrospective-cycle165.md)` (`cycle_runner_main_20261012_1719.log:11`).
     - The named file is cycle 165's retrospective, started 2026-10-10 17:55 (`retro.log:7418`). No `--cycle 166` run exists; the next run is `retro.log:7539`, for cycle 167.
     - The likely cause: `retro_files_in_window` (`cycle_runner.py:333`) uses `min(ctime, mtime)`, and the cycle-166 disposition edit probably rewrote the file. This is unverified. The test is to stat that file's creation time.
     - This is a third device failure with zero minutes lost, ranked below the two above.

7. **Judgement inside a material session.** Card 167-a1-1 changed the card's gate set to get past a launch gate (`facts.md:33`; `prerun_records.jsonl:1151`→`:1153`), and renamed an operation label to get past X5 (`facts.md:32`). Both are design calls that belonged to the judgement session. They were asked after the fact (`result_167-a1-1.json:24`), not before. Cards 167-a1-3 and 167-a1-5 behaved correctly: 167-a1-3 classified rows mechanically by PD404(c), and 167-a1-5 asked rather than decided (`assign_result_167_1.json:21`).

## DEVICE EFFECT

**Failed in the window:**
- **The launch gate's unverified-gate refusal** (2026-10-02 10:10, which the 2026-10-10 dry-count decision builds on). It fired and was worked around (fault 2).

**Failed in the window, but not on the extracted list:**
- **The Error List reuse** (`errorlist_check.py:173`, which came from retrospective-cycle80's device decision). It never fired (fault 1). That it is missing from the list is itself a gap in the extraction.
- **The runner's retrospective fallback** (`retro_fallback`). It accepted a retrospective from before the window (finding 6).

**Worked:**
- **bgrun's inner-failure scan** forced rc=1 when the process said 0 (`prep_c167_a1_3_explore.log:72`).
- **The undisposed-retrospective check** fired at cycle 166 (`cycle_runner_main_20261012_1719.log:6-7`), and the disposition was written (`archive/peer/2026-10-10-retrospective-cycle165.md:506`).
- **The gates_due rule** was answered in the purpose (`assign_167_1.json:31`).
- **bgrun_reap** ran, and the motor gates were OK (`cycle_runner_main_20261012_1719.log:14-16,24`).
- **The X10 memory prediction** was 677.5 MB, under the 680 limit, against a measured peak of 610.5 (`facts.md:28`).
- **Cost parsing:** C4c's $60.52 equals the sum of the four logged costs.

**Not exercised in the window:** no `tools/recipes` launch, no peer review, no stage replay. That leaves the stop-record, prior-art, guard_cycle, stagexec/stagesim and confirm-bait devices untested.

VIOLATION: device-failed | loss_min=10 | loss_usd=? | evidence=tools/bench/cycle_runner_main_20261012_1719.log:22
VIOLATION: device-failed | loss_min=1 | loss_usd=? | evidence=tools/hooks/material_marker.log:4394
VERDICT {"schema":"verdict/1","id":"retrospective-cycle167","verdict":"refuted","alternative":"The cycle met its purpose (11/11, 68 min, $26.48) and neither fault was costly; this is refuted only because two devices failed: Error List reuse keyed by file name (10 min) and a launch-gate refusal worked around by turning gates into rows (1 min).","discriminating_test":"Call errorlist_check.find_reusable on D1_ring_p5 at md5 75773b0d: it returns 'no saved read' although the p5s02e read is complete at that md5. Replay rbw.py sha 0bf608c2 against the launch gate: refused; sha 89c56b7f passes only because A0/R1 became rows.","violations":[{"slug":"device-failed","loss_min":10,"loss_usd":"?","evidence":"tools/bench/cycle_runner_main_20261012_1719.log:22"},{"slug":"device-failed","loss_min":1,"loss_usd":"?","evidence":"tools/hooks/material_marker.log:4394"}],"sources":["tools/bench/errorlist_check_cycle167.log:85","tools/errorlist_check.py:186","tools/bench/prerun_records.jsonl:1153","tools/bench/diag_c167_a1_1_facts.md:33","tools/bench/cycle_runner_main_20261012_1719.log:11"],"note":"Window also holds cycle 166 and ~47 h of chat; cycle 166 got no retrospective (the runner accepted cycle 165's file, cycle_runner_main:11). Before P6-1, measure offline which Build Array (#2626 or #11261) the one remaining Error List item is."}

## Sources

(extract from answer)

## What was done with it

Cycle 168 judgement (2026-10-12): both faults ACCEPTED; decisions in `docs/violation-decisions.md` (2026-10-12
20:31 / 20:32 entries) and `docs/d1/ring-p6.md` PD405.
- Fault 1 (Error List reuse keyed by file name): device repair offline, md5 match + rename self-test, after P6-1/P6-2.
- Fault 2 (gates turned into rows): rule - the purpose names stub-only gates as expected-unverified (PD405(g)); a material
  session returns BLOCKED instead of changing its gate set.
- Finding 3 (which Build Array is left): ACCEPTED as the cycle-168 first act - offline wiring check on c5531708, then ONE
  scratch RBW -> delete #11261 -> ExecState / Error List / graph (PD405(c)).
- Finding 2 (missing tools: EL uid route, shared graph loader) and finding 4 (STATUS 144 lines): deferred until after
  P6-1 and P6-2 (steer_168 item 6, PD405(f)).
- Finding 6 (cycle 166 retrospective skipped by the runner's fallback): `cycle_runner.py` question for the chat, not a
  runner card.
