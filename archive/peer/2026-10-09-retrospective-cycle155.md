# retrospective-cycle155

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.6799  in 80 / out 37683 / cache-create 143674 / cache-read 3882874  (584s, 48 turn(s))
- **date:** 2026-10-09 13:50:04
- **outcome:** ANSWERED (586s)
- **verdict-card:** VERDICT-CARD retrospective-cycle155 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle155.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle155, role retrospective) ---
CLAIM: Cycle 155 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 155 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-09 06:32:49  ..  2026-10-09 13:39:59   (427 min)
    basis: start = archive/peer/2026-10-09-retrospective-cycle152.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-10-08 20:50): sites use it; every other parser of that heading in `tools/` (not `tools/bench/`) is listed as using it or as unable to misfire. Self-test on two copies of `retrospective-cycle149.md` (placeholder restored / filled): each site misreads the placeholder copy on the current code and reads both right after. Built in cycle 150 (`docs/d1/ring-p4c.md` PD364(e)), after the s07 LabVIEW card and ALONE, beca??
  - `repeated-failure-class` (decided 2026-10-08 20:50): pre-fix tree drop `ASSIGN_STATE`/`CYCLE_ROLE`/`CYCLE_SESSION`; prepared as `tools/bench/cards/task_149-a2-1.json`. The review's finding 2 (`tools/bgrun.py --material` drops the three variables for every child) is weighed when that card is re-issued. DEFERRED by PD364(f): it runs ALONE before the next card that runs a pre-fix tree, or with the next gate-fp drain. Until then no card runs a pre-fix t??
  - `inference-over-measurement` (decided 2026-10-09 07:00): to be the only one. That is enough to build now rather than wait for a third. `stagesim` gets a collect-all replay mode: on an UNMEASURED refusal (owner, tunnel name, terminal class) it puts in the plan's own predicted value, flags the step PROVISIONAL with the refusal text, continues, and prints one list of every refusal. A collect-all run is never a dry, prerun or launch PASS. Self-test: on the ??

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

== cycle audit, 2026-10-09 06:32 .. 2026-10-09 13:40 (427 min, an explicit cycle window): 226 build logs, 27 peer logs, 12 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 208/226 ok; NO BGRUN line in ['capabilities_regen.log', 'diag_c153_a2_3_c147_A.log', 'diag_c153_a2_3_c147_B.log', 'diag_c153_a2_3_compdiff_A.log', 'diag_c153_a2_3_t6_A.log', 'diag_c153_a2_3_t6_B.log', 'diag_c153_a2_4_c147.log', 'diag_c153_a2_4_compdiff.log', 'diag_c153_a2_4_realpb.log', 'diag_c153_a2_4_rescore.log', 'diag_c153_a2_4_t6.log', 'diag_c153_a2_4_vf80_post.log', 'diag_c153_a2_4_vf80_pre.log', 'diag_c153_a2_5_c147.log', 'diag_c153_a2_5_compdiff.log', 'diag_c153_a2_5_t6.log', 'fn_gate.log', 'stop_after_156.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 53 logs recorded a failure; unreviewed: ['prep_c155_a5_1_after_gbjev.log', 'prep_c155_a5_1_before_fnf2.log', 'prep_c155_a5_1_census_diff.log']
  FAIL  A4 every archived review says what was done with it: 11/12 annotated; blank: ['2026-10-09-c151-selftest-c147-b1-2-pindrift.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 11696 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 8 log(s) with a run that printed none: ['diag_c153_a2_4_run.log', 'diag_c153_b1_1_suite_before.log', 'diag_c154_a1_2_keys.log', 'diag_c154_a2_3_census.log', 'diag_c154_a3_3b_diff.log', 'prep_c154_a1_1_dump_p2b.log']??
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 232, failure markers 62, logs carrying a failure 53
  C2 peer reviews dispatched 27, archived 12
  C3 wall-clock inside bgrun, BUILDS ONLY 119 min 51 s
  C4 wall-clock inside bgrun, REVIEWS 13 min 44 s; cost $9.2968 from 7 log(s) that report one
  C4b cost lines seen 7 / parsed 7
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 383 min 44 s; cost $148.1511 from 14 log(s) - cycle_153.log, cycle_153_assign_1.log, cycle_153_assign_2.log, cycle_153_assign_3.log, cycle_153_handback_1.log, cycle_153_handback_2.log, cycle_154.log, cycle_154_assign_1.log, cycle_154_assign_2.log, cycle_154_assign_3.log, cycle_154_handback_1.log, cycle_154_handback_2.log, cycle_155.log, cycle_155_assign_1.log
  C5 total wall-clock 517 min 19 s  (builds 23%, reviews 2%, judgement session 74%)

  C6 material-marked recipe/bench runs 98, judgement-session attempts refused 13  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/ring-p5.md [tools/bench/next.json plan.path]: 522 - STATUS.md, docs/NAMES.md, docs/chat-handoff.md, docs/d1/result-gates.md, docs/fixture-recording.md, docs/fn_descriptions.json, docs/script-writing.md, docs/toolkit-capabilities.md, docs/violation-decisions.md, tools/bench/.stall_samples.txt, tools/bench/adopted_scratch.jsonl, tools/bench/assign/assign_prompt.md??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 355/1219 ok; 864 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  FAIL  L2 every cited project path exists: 1 DANGLING of 3875 citations checked:
       docs/d1/ring-p4.md:131 -> tools/bench/build_oploopendref_v0.py

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:123 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 776 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  FAIL  L8 decision headers carry HH:MM: 1 header(s) dated >= 2026-09-28 without a parseable HH:MM (violations.py DEC_RE reads them as bare dates): ['docs/violation-decisions.md:1875']
  WARN  L9 new Pre-decided items carry a USER-RULES: line: 2 item(s) >= 238 without `USER-RULES:` (read docs/user-rules.md and cite the rows relied on, or write `USER-RULES: none apply`): ['docs/d1/result-gates.md:18 (item 366)', 'docs/d1/tooling.md:145 (item 329)']
  FAIL  L10 active docs stay <= 400 lines: 2 doc(s) over the cap: ['docs/chat-handoff.md 566', 'docs/d1/ring-p3b.md 419']. Freeze in place (`status: frozen` + footer, tools/bench/freeze_docs_d1.py) and index what is in force, or split into linked topic files.
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1405; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 4974
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  WARN  L11 frozen docs carry a FROZEN footer: 1 without one: ['docs/d1/ring-p4.md']
  PASS  L12 function table matches the code: generated block == code + fn_records

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, A4 every archived review says what was done with it, L2 every cited project path exists, L8 decision headers carry HH:MM, L10 active docs stay <= 400 lines


=== BUILD LOGS INSIDE THE WINDOW (227; read them directly, they are the primary record) ===
tools/bench/capabilities_regen.log  (2026-10-09 13:37:57)
tools/bench/diag_c153_a1_1_census.log  (2026-10-09 06:45:08)
tools/bench/diag_c153_a1_1_census2.log  (2026-10-09 06:46:01)
tools/bench/diag_c153_a1_1_census3.log  (2026-10-09 06:48:28)
tools/bench/diag_c153_a1_1_census4.log  (2026-10-09 06:49:03)
tools/bench/diag_c153_a1_1_md5_after.log  (2026-10-09 06:52:12)
tools/bench/diag_c153_a1_1_md5_before.log  (2026-10-09 06:40:42)
tools/bench/diag_c153_a1_1_probe.log  (2026-10-09 06:42:53)
tools/bench/diag_c153_a1_1_schema.log  (2026-10-09 06:41:30)
tools/bench/diag_c153_a2_1_md5_before.log  (2026-10-09 07:17:46)
tools/bench/diag_c153_a2_1_orig_read.log  (2026-10-09 07:16:19)
tools/bench/diag_c153_a2_2_queue_hygiene.log  (2026-10-09 07:49:12)
tools/bench/diag_c153_a2_3_c147_A.log  (2026-10-09 07:21:30)
tools/bench/diag_c153_a2_3_c147_B.log  (2026-10-09 07:22:10)
tools/bench/diag_c153_a2_3_compdiff_A.log  (2026-10-09 07:20:50)
tools/bench/diag_c153_a2_3_run.log  (2026-10-09 07:22:10)
tools/bench/diag_c153_a2_3_t6_A.log  (2026-10-09 07:21:24)
tools/bench/diag_c153_a2_3_t6_B.log  (2026-10-09 07:22:04)
tools/bench/diag_c153_a2_4_c147.log  (2026-10-09 08:05:39)
tools/bench/diag_c153_a2_4_compdiff.log  (2026-10-09 08:04:58)
tools/bench/diag_c153_a2_4_realpb.log  (2026-10-09 08:05:00)
tools/bench/diag_c153_a2_4_rescore.log  (2026-10-09 08:05:49)
tools/bench/diag_c153_a2_4_run.log  (2026-10-09 08:05:49)
tools/bench/diag_c153_a2_4_t6.log  (2026-10-09 08:05:34)
tools/bench/diag_c153_a2_4_vf80_post.log  (2026-10-09 08:04:53)
tools/bench/diag_c153_a2_4_vf80_pre.log  (2026-10-09 08:04:49)
tools/bench/diag_c153_a2_5_c147.log  (2026-10-09 07:27:42)
tools/bench/diag_c153_a2_5_compdiff.log  (2026-10-09 07:27:01)
tools/bench/diag_c153_a2_5_run.log  (2026-10-09 07:27:42)
tools/bench/diag_c153_a2_5_t6.log  (2026-10-09 07:27:36)
tools/bench/diag_c153_a2_6_orig_read.log  (2026-10-09 07:35:29)
tools/bench/diag_c153_a2_6_rsrc.log  (2026-10-09 07:31:43)
tools/bench/diag_c153_a2_8_queue_hygiene.log  (2026-10-09 07:57:09)
tools/bench/diag_c153_a2_8_readout.log  (2026-10-09 07:54:03)
tools/bench/diag_c153_b1_1_default.log  (2026-10-09 06:58:58)
tools/bench/diag_c153_b1_1_plan.log  (2026-10-09 06:55:59)
tools/bench/diag_c153_b1_1_suite_after.log  (2026-10-09 07:02:10)
tools/bench/diag_c153_b1_1_suite_before.log  (2026-10-09 06:58:12)
tools/bench/diag_c153_b2_1_post_c147.log  (2026-10-09 07:03:01)
tools/bench/diag_c153_b2_1_post_cc.log  (2026-10-09 07:00:32)
tools/bench/diag_c153_b2_1_post_t6.log  (2026-10-09 07:02:55)
tools/bench/diag_c153_b2_1_post_vf80.log  (2026-10-09 07:02:19)
tools/bench/diag_c153_b2_1_pre_c147.log  (2026-10-09 06:57:55)
tools/bench/diag_c153_b2_1_pre_cc.log  (2026-10-09 06:57:56)
tools/bench/diag_c153_b2_1_pre_t6.log  (2026-10-09 06:57:49)
tools/bench/diag_c153_b2_1_pre_vf80.log  (2026-10-09 06:57:12)
tools/bench/diag_c153_b2_1_rescore.log  (2026-10-09 07:00:42)
tools/bench/diag_c153_b2_1_s06pos.log  (2026-10-09 07:02:08)
tools/bench/diag_c154_a1_1_targets.log  (2026-10-09 08:24:28)
tools/bench/diag_c154_a1_2_census.log  (2026-10-09 08:23:39)
tools/bench/diag_c154_a1_2_chain.log  (2026-10-09 08:25:27)
tools/bench/diag_c154_a1_2_chain2.log  (2026-10-09 08:25:50)
tools/bench/diag_c154_a1_2_chain3.log  (2026-10-09 08:26:05)
tools/bench/diag_c154_a1_2_keys.log  (2026-10-09 08:21:46)
tools/bench/diag_c154_a1_2_keys2.log  (2026-10-09 08:22:14)
tools/bench/diag_c154_a2_1_donor.log  (2026-10-09 08:42:18)
tools/bench/diag_c154_a2_2_readback.log  (2026-10-09 08:48:09)
tools/bench/diag_c154_a2_3_census.log  (2026-10-09 09:07:08)
tools/bench/diag_c154_a3_1_census.log  (2026-10-09 09:22:39)
tools/bench/diag_c154_a3_1_census_registered.log  (2026-10-09 09:24:32)
tools/bench/diag_c154_a3_1_inv.log  (2026-10-09 09:25:32)
tools/bench/diag_c154_a3_3_adopt.log  (2026-10-09 10:20:51)
tools/bench/diag_c154_a3_3_checklaunch.log  (2026-10-09 10:04:27)
tools/bench/diag_c154_a3_3_dry.log  (2026-10-09 10:03:05)
tools/bench/diag_c154_a3_3_el.log  (2026-10-09 10:31:39)
tools/bench/diag_c154_a3_3_elexp.log  (2026-10-09 10:36:09)
tools/bench/diag_c154_a3_3_graph.log  (2026-10-09 10:39:11)
tools/bench/diag_c154_a3_3_graph_dry.log  (2026-10-09 10:21:35)
tools/bench/diag_c154_a3_3_graph_prerun.log  (2026-10-09 10:21:47)
tools/bench/diag_c154_a3_3_inv_after.log  (2026-10-09 10:06:00)
tools/bench/diag_c154_a3_3_inv_before.log  (2026-10-09 10:02:35)
tools/bench/diag_c154_a3_3_memload.log  (2026-10-09 10:43:54)
tools/bench/diag_c154_a3_3_mkgraph.log  (2026-10-09 10:21:18)
tools/bench/diag_c154_a3_3_nodes.log  (2026-10-09 10:43:36)
tools/bench/diag_c154_a3_3_prerun.log  (2026-10-09 10:04:03)
tools/bench/diag_c154_a3_3_scr_dry.log  (2026-10-09 10:03:25)
tools/bench/diag_c154_a3_3_scr_prerun.log  (2026-10-09 10:04:25)
tools/bench/diag_c154_a3_3_scrreq.log  (2026-10-09 10:04:26)
tools/bench/diag_c154_a3_3b_checklaunch.log  (2026-10-09 10:11:54)
tools/bench/diag_c154_a3_3b_diff.log  (2026-10-09 10:09:40)
tools/bench/diag_c154_a3_3b_dry.log  (2026-10-09 10:11:09)
tools/bench/diag_c154_a3_3b_inv_after.log  (2026-10-09 10:44:13)
tools/bench/diag_c154_a3_3b_inv_before.log  (2026-10-09 10:10:33)
tools/bench/diag_c154_a3_3b_prerun.log  (2026-10-09 10:11:30)
tools/bench/diag_c154_a3_3b_scr_prerun.log  (2026-10-09 10:11:52)
tools/bench/diag_c154_a3_3b_scrreq.log  (2026-10-09 10:11:53)
tools/bench/diag_c154_p5s01a_scratch.log  (2026-10-09 10:20:31)
tools/bench/diag_c155_a3_1_checklaunch.log  (2026-10-09 12:32:59)
tools/bench/diag_c155_a3_1_dry.log  (2026-10-09 12:32:07)
tools/bench/diag_c155_a3_1_inv_after.log  (2026-10-09 12:41:02)
tools/bench/diag_c155_a3_1_inv_before.log  (2026-10-09 12:31:39)
tools/bench/diag_c155_a3_1_peek.log  (2026-10-09 12:34:34)
tools/bench/diag_c155_a3_1_prerun.log  (2026-10-09 12:32:40)
tools/bench/diag_c155_a3_1_scr_dry.log  (2026-10-09 12:32:23)
tools/bench/diag_c155_a3_1_scr_prerun.log  (2026-10-09 12:32:57)
tools/bench/diag_c155_a3_1_scrreq.log  (2026-10-09 12:32:58)
tools/bench/diag_c155_a3_2_adopt.log  (2026-10-09 12:45:42)
tools/bench/diag_c155_a3_2_el.log  (2026-10-09 12:55:34)
tools/bench/diag_c155_a3_2_elexp.log  (2026-10-09 12:56:07)
tools/bench/diag_c155_a3_2_graph.log  (2026-10-09 12:59:25)
tools/bench/diag_c155_a3_2_graph_dry.log  (2026-10-09 12:49:09)
tools/bench/diag_c155_a3_2_graph_prerun.log  (2026-10-09 12:49:22)
tools/bench/diag_c155_a3_2_inv_after.log  (2026-10-09 12:59:53)
tools/bench/diag_c155_a3_2_inv_before.log  (2026-10-09 12:45:08)
tools/bench/diag_c155_a3_2_memload.log  (2026-10-09 12:59:42)
tools/bench/diag_c155_a3_2_mkgraph.log  (2026-10-09 12:48:51)
tools/bench/diag_c155_a3_2_nodes.log  (2026-10-09 12:59:40)
tools/bench/diag_c155_p5s01b_scratch.log  (2026-10-09 12:40:28)
tools/bench/diag_t7_dry2_stage_template_ring.log  (2026-10-09 11:18:54)
tools/bench/diag_t7_dry2_stage_template_ring_scratch.log  (2026-10-09 11:19:37)
tools/bench/diag_t7_dry_stage_d1_ring_p5s01a.log  (2026-10-09 11:09:19)
tools/bench/diag_t7_dry_stage_d1_ring_p5s01a_scratch.log  (2026-10-09 11:10:11)
tools/bench/diag_t7_dry_stage_template_ring.log  (2026-10-09 11:12:37)
tools/bench/diag_t7_dry_stage_template_ring_scratch.log  (2026-10-09 11:13:21)
tools/bench/diag_t7_gencheck.log  (2026-10-09 11:32:55)
tools/bench/diag_t7_prerun2_stage_template_ring.log  (2026-10-09 11:19:16)
tools/bench/diag_t7_prerun2_stage_template_ring_scratch.log  (2026-10-09 11:20:00)
tools/bench/diag_t7_prerun_stage_d1_ring_p5s01a.log  (2026-10-09 11:09:47)
tools/bench/diag_t7_prerun_stage_d1_ring_p5s01a_scratch.log  (2026-10-09 11:10:33)
tools/bench/diag_t7_prerun_stage_template_ring.log  (2026-10-09 11:13:00)
tools/bench/diag_t7_prerun_stage_template_ring_scratch.log  (2026-10-09 11:13:42)
tools/bench/fn_gate.log  (2026-10-09 13:37:12)
tools/bench/jev_gate.log  (2026-10-09 13:39:19)
tools/bench/motor_session_end_cycle152.log  (2026-10-09 06:33:03)
tools/bench/motor_session_end_cycle153.log  (2026-10-09 08:09:35)
tools/bench/motor_session_end_cycle154.log  (2026-10-09 10:55:51)
tools/bench/motor_session_start_cycle153.log  (2026-10-09 06:33:13)
tools/bench/motor_session_start_cycle154.log  (2026-10-09 08:09:43)
tools/bench/motor_session_start_cycle155.log  (2026-10-09 11:38:20)
tools/bench/prep_c154_a1_1_dump_p2b.log  (2026-10-09 08:25:43)
tools/bench/prep_c154_a3_2_inv_after.log  (2026-10-09 09:39:23)
tools/bench/prep_c154_a3_2_inv_before.log  (2026-10-09 09:35:23)
tools/bench/prep_c154_a3_2_mk.log  (2026-10-09 09:38:42)
tools/bench/prep_c154_a3_2b_checklaunch.log  (2026-10-09 09:52:19)
tools/bench/prep_c154_a3_2b_dry.log  (2026-10-09 09:51:14)
tools/bench/prep_c154_a3_2b_inv_after.log  (2026-10-09 09:54:40)
tools/bench/prep_c154_a3_2b_inv_before.log  (2026-10-09 09:46:47)
tools/bench/prep_c154_a3_2b_licence.log  (2026-10-09 09:49:02)
tools/bench/prep_c154_a3_2b_mk.log  (2026-10-09 09:47:42)
tools/bench/prep_c154_a3_2b_pred.log  (2026-10-09 09:48:19)
tools/bench/prep_c154_a3_2b_prerun.log  (2026-10-09 09:51:36)
tools/bench/prep_c154_a3_2b_probe.log  (2026-10-09 09:43:46)
tools/bench/prep_c154_a3_2b_scr_dry.log  (2026-10-09 09:51:55)
tools/bench/prep_c154_a3_2b_scr_prerun.log  (2026-10-09 09:52:17)
tools/bench/prep_c154_a3_2b_scrreq.log  (2026-10-09 09:52:18)
tools/bench/prep_c154_a3_2b_x11.log  (2026-10-09 09:49:01)
tools/bench/prep_c154_a4_1_inv_after.log  (2026-10-09 10:54:12)
tools/bench/prep_c154_a4_1_inv_before.log  (2026-10-09 10:51:23)
tools/bench/prep_c154_a4_1_mk.log  (2026-10-09 10:53:51)
tools/bench/prep_c154_a4_1_mk_r1.log  (2026-10-09 10:53:15)
tools/bench/prep_c155_a1_1_after.log  (2026-10-09 11:59:01)
tools/bench/prep_c155_a1_1_after2.log  (2026-10-09 12:08:51)
tools/bench/prep_c155_a1_1_before.log  (2026-10-09 11:51:00)
tools/bench/prep_c155_a1_1_probe.log  (2026-10-09 12:03:00)
tools/bench/prep_c155_a1_1_suite_after.log  (2026-10-09 12:07:36)
tools/bench/prep_c155_a1_1_suite_after2.log  (2026-10-09 12:13:21)
tools/bench/prep_c155_a1_1_suite_before.log  (2026-10-09 11:55:37)
tools/bench/prep_c155_a1_1_suite_before_c120.log  (2026-10-09 11:56:10)
tools/bench/prep_c155_a2_1_checklaunch.log  (2026-10-09 12:25:12)
tools/bench/prep_c155_a2_1_dry.log  (2026-10-09 12:24:07)
tools/bench/prep_c155_a2_1_inv_after.log  (2026-10-09 12:26:24)
tools/bench/prep_c155_a2_1_inv_before.log  (2026-10-09 12:19:04)
tools/bench/prep_c155_a2_1_licence.log  (2026-10-09 12:22:55)
tools/bench/prep_c155_a2_1_mk.log  (2026-10-09 12:21:29)
tools/bench/prep_c155_a2_1_pred.log  (2026-10-09 12:22:16)
tools/bench/prep_c155_a2_1_prerun.log  (2026-10-09 12:24:24)
tools/bench/prep_c155_a2_1_scr_dry.log  (2026-10-09 12:24:39)
tools/bench/prep_c155_a2_1_scr_prerun.log  (2026-10-09 12:24:56)
tools/bench/prep_c155_a2_1_scrreq.log  (2026-10-09 12:25:11)
tools/bench/prep_c155_a2_1_x11.log  (2026-10-09 12:22:14)
tools/bench/prep_c155_a4_1_checklaunch.log  (2026-10-09 13:21:46)
tools/bench/prep_c155_a4_1_dry.log  (2026-10-09 13:19:54)
tools/bench/prep_c155_a4_1_inv_after.log  (2026-10-09 13:25:38)
tools/bench/prep_c155_a4_1_inv_before.log  (2026-10-09 13:11:00)
tools/bench/prep_c155_a4_1_licence.log  (2026-10-09 13:19:12)
tools/bench/prep_c155_a4_1_mk.log  (2026-10-09 13:17:24)
tools/bench/prep_c155_a4_1_pred.log  (2026-10-09 13:17:44)
tools/bench/prep_c155_a4_1_prerun.log  (2026-10-09 13:20:26)
tools/bench/prep_c155_a4_1_probe.log  (2026-10-09 13:03:41)
tools/bench/prep_c155_a4_1_probe2.log  (2026-10-09 13:05:08)
tools/bench/prep_c155_a4_1_scr_dry.log  (2026-10-09 13:21:12)
tools/bench/prep_c155_a4_1_scr_prerun.log  (2026-10-09 13:21:44)
tools/bench/prep_c155_a4_1_scrreq.log  (2026-10-09 13:21:45)
tools/bench/prep_c155_a4_1_x11.log  (2026-10-09 13:18:04)
tools/bench/prep_c155_a5_1_after_c103d.log  (2026-10-09 13:35:38)
tools/bench/prep_c155_a5_1_after_c121.log  (2026-10-09 13:35:39)
tools/bench/prep_c155_a5_1_after_fnf2.log  (2026-10-09 13:36:55)
tools/bench/prep_c155_a5_1_after_gbjev.log  (2026-10-09 13:37:02)
tools/bench/prep_c155_a5_1_after_prdiag.log  (2026-10-09 13:37:12)
tools/bench/prep_c155_a5_1_before_c103d.log  (2026-10-09 13:33:10)
tools/bench/prep_c155_a5_1_before_c121.log  (2026-10-09 13:33:12)
tools/bench/prep_c155_a5_1_before_fnf2.log  (2026-10-09 13:34:31)
tools/bench/prep_c155_a5_1_before_gbjev.log  (2026-10-09 13:34:38)
tools/bench/prep_c155_a5_1_before_prdiag.log  (2026-10-09 13:34:49)
tools/bench/prep_c155_a5_1_census_after.log  (2026-10-09 13:35:35)
tools/bench/prep_c155_a5_1_census_before.log  (2026-10-09 13:31:01)
tools/bench/prep_c155_a5_1_census_diff.log  (2026-10-09 13:35:36)
tools/bench/selftest_c153_cardclock_quoted.log  (2026-10-09 07:00:31)
tools/bench/selftest_c153_collect_all.log  (2026-10-09 07:01:24)
tools/bench/selftest_c153_compdiff_poskey.log  (2026-10-09 07:02:14)
tools/bench/selftest_c153_poskey_convert.log  (2026-10-09 07:19:18)
tools/bench/selftest_c153_poskey_convert_a2_5.log  (2026-10-09 07:26:38)
tools/bench/selftest_c154_a3_1_x17.log  (2026-10-09 09:24:15)
tools/bench/selftest_c154_a3_1_x17_baseline.log  (2026-10-09 09:23:58)
tools/bench/selftest_c154_a3_1_x17_baseline_after.log  (2026-10-09 09:24:16)
tools/bench/selftest_c155_basecase_frame.log  (2026-10-09 12:08:25)
tools/bench/selftest_c155_gatefp73.log  (2026-10-09 13:35:37)
tools/bench/selftest_t7_assign_flow.log  (2026-10-09 11:20:46)
tools/bench/selftest_t7_base_c147.log  (2026-10-09 11:03:01)
tools/bench/selftest_t7_base_regress.log  (2026-10-09 11:05:27)
tools/bench/selftest_t7_base_t6poskey.log  (2026-10-09 11:02:55)
tools/bench/selftest_t7_c147.log  (2026-10-09 11:18:28)
tools/bench/selftest_t7_c_e3.log  (2026-10-09 11:26:09)
tools/bench/selftest_t7_c_e3_write.log  (2026-10-09 11:25:01)
tools/bench/selftest_t7_capabilities.log  (2026-10-09 11:34:19)
tools/bench/selftest_t7_capabilities_t8.log  (2026-10-09 12:08:56)
tools/bench/selftest_t7_capabilities_t8b.log  (2026-10-09 12:11:05)
tools/bench/selftest_t7_compdiff.log  (2026-10-09 11:08:40)
tools/bench/selftest_t7_convert.log  (2026-10-09 11:07:48)
tools/bench/selftest_t7_fn_f2.log  (2026-10-09 11:35:34)
tools/bench/selftest_t7_genfirst.log  (2026-10-09 11:21:33)
tools/bench/selftest_t7_regress.log  (2026-10-09 11:29:18)
tools/bench/selftest_t7_ring.log  (2026-10-09 11:17:39)
tools/bench/selftest_t7_stagesim.log  (2026-10-09 11:21:10)
tools/bench/selftest_t7_stagexec.log  (2026-10-09 11:21:06)
tools/bench/selftest_t7_t6poskey.log  (2026-10-09 11:18:20)
tools/bench/stop_after_156.log  (2026-10-09 12:46:19)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (27) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_153.log  (2026-10-09 06:38:19)
tools/bench/cycle_153_assign_1.log  (2026-10-09 07:06:09)
tools/bench/cycle_153_assign_2.log  (2026-10-09 07:38:36)
tools/bench/cycle_153_assign_3.log  (2026-10-09 08:09:25)
tools/bench/cycle_153_handback_1.log  (2026-10-09 07:09:17)
tools/bench/cycle_153_handback_2.log  (2026-10-09 07:41:41)
tools/bench/cycle_154.log  (2026-10-09 08:18:20)
tools/bench/cycle_154_assign_1.log  (2026-10-09 08:30:43)
tools/bench/cycle_154_assign_2.log  (2026-10-09 09:12:02)
tools/bench/cycle_154_assign_3.log  (2026-10-09 10:55:48)
tools/bench/cycle_154_handback_1.log  (2026-10-09 08:33:45)
tools/bench/cycle_154_handback_2.log  (2026-10-09 09:15:44)
tools/bench/cycle_155.log  (2026-10-09 11:42:57)
tools/bench/cycle_155_assign_1.log  (2026-10-09 13:39:58)
tools/bench/cycle_runner.log  (2026-10-09 13:39:58)
tools/bench/cycle_runner_main_20261009_0250.log  (2026-10-09 10:55:54)
tools/bench/cycle_runner_main_20261009_1138.log  (2026-10-09 13:39:58)
tools/bench/diag_c154_a3_3_priorart.log  (2026-10-09 10:01:46)
tools/bench/diag_t7_doclint.log  (2026-10-09 11:35:47)
tools/bench/peer_c153-a2-6-origmd5.log  (2026-10-09 07:29:56)
tools/bench/peer_c154-a3-3b-el47.log  (2026-10-09 10:35:35)
tools/bench/peer_c154-a3-3b-nodes.log  (2026-10-09 10:42:36)
tools/bench/prep_c154_a3_2b_priorart.log  (2026-10-09 09:54:07)
tools/bench/prep_c155_a2_1_priorart.log  (2026-10-09 12:26:05)
tools/bench/prep_c155_a4_1_priorart.log  (2026-10-09 13:25:06)
tools/bench/retro.log  (2026-10-09 13:39:58)
tools/bench/runner_supervisor.log  (2026-10-09 13:39:58)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle155","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Window note.** The evidence window (06:32:49–13:39:59) holds three runner cycles, not one: cycle 153 (06:33–08:09), cycle 154 (08:09–10:55) and cycle 155 (11:38–13:40). The source is `tools/bench/cycle_runner.log` lines 1421–1479. Between 10:55 and 11:38 the user stopped the runner for chat cards T7 and T8 (`cycle_runner.log:1471`). That was user-ordered work, not cycle work. This retrospective is every-3-cards, so the span is by design (`cycle_runner.log:1461` "not due"). Per the window rule I judge the whole interval. Cycle 155 on its own (11:38–13:40, `PURPOSE_MET` 11/11, `assign_result_155_1.json:5`) had no structural fault. The fault named below happened in cycle 154.

Spend in the window: cycle 153 $46.65, cycle 154 $63.46 (`cycle_runner.log:1441,1468`), cycle 155's assignment $35.69 (`:1479`), reviews $9.30 (audit C4).

## The one structural fault: a device failed (the gates_due check and the HH:MM header rule)

**What happened.** The 2026-09-27 08:30 decision (`docs/violation-decisions.md:1526-1539`) did two things:
- It built `gates_due`: every "due" gate is computed at cycle start and the judgement is told to answer it "BEFORE the first dispatch that would trip them".
- It accepted the rule "decision-header times are always written HH:MM", because an `HH:Mx` time "silently parsed as 00:00 and kept a slug DUE".

The same fault happened again here:
1. Cycle 153's judgement wrote the heading `07:0x` at `docs/violation-decisions.md:1992`. The original text is shown at `tools/bench/diag_c154_a3_3b_diff.log:7`.
2. At 08:09:45 the cycle-154 card reported `violations: DUE inference-over-measurement` (`tools/bench/cards/cycle_154.json:30-32`). All three cycle-154 judgement sessions got the instruction to answer it first (`cycle_154.log:221`, `cycle_154_handback_1.log:221`, `cycle_154_handback_2.log:221`).
3. The hand-back-2 judgement saw it and only noted that it "still stand[s]" (`cycle_154_handback_2.log:271`).
4. At about 10:05 `guard_cycle` refused the P5-1a scratch launch. The cause was that `07:0x` parsed as 00:00 (`tools/bench/cards/result_154-a3-3.json:1`).

So the device fired correctly, and the judgement ignored it. The header rule exists only as a discipline: `doc_lint` L8 still flags a fifth instance, `12:2x` at `:1875`. Earlier instances were fixed at `:1469`, `:1504` and `:1513`.

- **Loss:** about 8 minutes. The last launch pre-check ended at 10:04:27 (`diag_c154_a3_3_checklaunch.log:1`) and the scratch actually started at 10:12:18 (`diag_c154_p5s01a_scratch.log:1`). `result_154-a3-3.json` records `cost.minutes 8` and `usd null`, so `loss_usd=?`.
- **Counterfactual:** had the cycle-154 judgement (08:09–08:18) or hand-back-2 (09:12–09:15) run `py tools/violations.py` and changed the one token, the scratch would have started at about 10:05, not 10:12. Round 3 would have ended about 8 minutes before 10:55. Nothing else in the outcome changes.
- **Magnitude:** the loss is small. It is reported only because the device threshold is 1.

## FINDINGS

**1. Repeated failure.**
- In cycle 154, stage-tool route gaps were found one hand-back round at a time:
  - round 1: the queue route cannot place Enqueue in a Case frame (`handback_154_1.json:6`);
  - round 2: no route for census rows 9–10 (`handback_154_2.json:6`);
  - round 3: `frame` addressing on a base case (`handback_154_3.json:46`).
- The approach should have changed at round 1. PD374 was written without a route census. PD375(c) added the census only after round 1 (`docs/d1/ring-p5.md:89-93`).
- Separately, fp-70 failed in all three rounds of cycle 153 (`handback_153_1`/`_2`/`_3`). It was finally settled in 154 by declaring the stored P4 recipes superseded (PD373(c), `docs/d1/ring-p4d.md:240-244`). That ruling was available in round 2.

**2. Missing tool.** Two cheap fixes were not built:
- a write-time refusal of an `HH:Mx` decision header, or letting `violations.py:94` DEC_RE read one as its lower bound;
- a gate-fp release path in `guard_cycle` (`diag_c154_a3_3_facts.md:25`).

Either would have stopped the a3-3 refusal.

**3. Unmeasured steps.**
- PD374(e) inferred from F7 that the obtain/enqueue routes were usable. A route census cost minutes and was skipped.
- The P5-1b half was not compiled when the cut was made (a3-2b, about 09:50). It was compiled only at a4-1 (10:53). This is defensible, because PD378(a) cites P5-1a's measured frame order.
- The P5-2 plan has X10 headroom of 0 (680.0 against a limit of 680, `assign_result_155_1.json:21`).

**4. Rule compliance.**
- A1: 18 logs have no BGRUN line. Most are wrapper sub-logs, e.g. `diag_c153_a2_3_*` under `diag_c153_a2_5_run.py`.
- A3: three failing `prep_c155_a5_1_*` logs have no review.
- L3: STATUS.md is 123 lines, over the 110 cap.
- L10: `docs/chat-handoff.md` is 566 lines, over the 400 cap.
- The assignment session edited the append-only `docs/violation-decisions.md` in place (`brief_154-a3-3b.md:11`).
- What the audit does not cover:
  - whether a `gates_due` entry was answered before the dispatch that tripped it (the fault above);
  - whether the judgement read the hand-back notes it was asked to check;
  - C7 lists 522 files against `ring-p5.md`. That is saturated noise, not a scope measurement.

**5. Ordering.** A route census before PD374's round-1 dispatch would have folded rounds 1 and 2 into one. It would have saved about 15 minutes and $8.52 (`handback_154_1.json:25-26`). Cycle 155's tool fix before P5-1b was the correct deliverable-first exception (PD378(b)).

**6. What was not reported.**
- `cycle_runner.log:1462` says "nothing to commit / rc=128". rc=128 is a git fatal error, so cycle 154's work went uncommitted until the chat's lock fix (commit 57e7de7d).
- Audit C4c counts the Sonnet assignment sessions as "judgement session" time. That inflates the reported 74% judgement share.
- The gate-fp queue grew from 11 to 12 open items while it was DUE in all three cycles (`cycle_155.json:47`).

**7. Judgement inside a material session.**
- The cycle-154 round-3 assignment (`claude -p`) chose to rewrite a judgement document's decision timestamp to `07:00` (`brief_154-a3-3b.md:11`, `diag_c154_a3_3b_diff.log:8`). It asked judgement to check the edit (`cycle_154_assign_3.log:60`), but PD378 never answers that request.
- The X10 cut (PD374(e):63) and the fp-73 "returned with reason" (`assign_155_1.json:16`) were both pre-authorised.
- 153-a2-5's open_rows choice was made in material and ratified afterwards (PD372(c)).

## DEVICE EFFECT

- **Failed:** 2026-09-27 08:30, the `gates_due` check plus the HH:MM header rule (above).
- **Fired on a technically by-design case:** the stop record refused a read-only `md5sum` (`tools/hooks/material_marker.log:3790`). The whole command carried `| xargs`, and `stop_record.py:248-249,355` taints every segment of such a command. This is by design and cost nothing, because a review was owed anyway. It is borderline, not counted.
- **Worked:**
  - the X10 memory margin (154-a3-2 stopped before launch);
  - prior-art before builds (4 reviews);
  - the plan dry reports all unroutable rows (a4-1 reported actions 21 and 32 together);
  - the bgrun inner-failure scan (`diag_c154_a3_3b_diff.log:14`);
  - cost-line parsing (7 of 7);
  - retro-undisposed (`cycle_runner.log:1419`);
  - op hygiene (153-a2-8).
- **Built but not triggered:** the collect-all replay.
- **Saturated:** C7, the scope-creep counter.

VIOLATION: device-failed | loss_min=8 | loss_usd=? | evidence=tools/bench/cards/result_154-a3-3.json:1

VERDICT {"schema":"verdict/1","id":"retrospective-cycle155","verdict":"refuted","alternative":"Cycle 155 proper (11:38-13:40) was clean; the only device failure is in cycle 154 inside the same window, and its loss is ~8 min, so the claim fails only on the threshold-1 device rule.","discriminating_test":"Diff docs/violation-decisions.md:1992 at HEAD~ vs HEAD and confirm cycle_154.json gates_due listed violations=DUE at 08:09:45, before the 10:04 refusal in result_154-a3-3.json.","violations":[{"slug":"device-failed","loss_min":8,"loss_usd":"?","evidence":"tools/bench/cards/result_154-a3-3.json:1"}],"sources":["tools/bench/cards/result_154-a3-3.json:1","tools/bench/cards/cycle_154.json:30","tools/bench/cycle_154_handback_2.log:271","docs/violation-decisions.md:1538","tools/bench/diag_c154_p5s01a_scratch.log:1"],"note":"Device = 2026-09-27 08:30 gates_due plus HH:MM header rule; fifth Mx header still at violation-decisions.md:1875."}

## Sources

(extract from answer)

## What was done with it

Cycle 156 judgement, 2026-10-09 13:5x.
- `VIOLATION: device-failed` ACCEPTED (loss 8 min, cycle 154). Device decision appended to `docs/violation-decisions.md`
  (`## device-failed — 2026-10-09 13:55`): `tools/violations.py` DEC_RE reads an `HH:Mx` header as `HH:M9` (the upper
  bound, so the retrospective that prompted a decision is never counted after it), self-tested on the literal `12:2x`
  (`docs/violation-decisions.md:1875`) and `07:0x` forms. Not a hook file, so a runner card may build it; it is pass item 7
  of cycle 156's purpose (`tools/bench/next.json`), after the LabVIEW card. The in-place edit of the append-only file by
  the cycle-154 assignment (finding 7) is ratified as a one-token fix; no further in-place edits.
- Finding 3 (P5-2 X10 margin 0): decided in `docs/d1/ring-p5.md` PD379(c) — cut only at group boundaries, each step's
  planned MAIN ≤ 675.
- Finding 1/5 (route gaps found one round at a time): the P5-2 plan already ran a full route census (155-a4-1); its three
  GAP rows are decided together in PD379(a)(b)(d).
- Finding 6 (gate-fp queue growth): every open entry except fp-73 is a hook gate (the chat's); fp-73 is CLOSED as moot by
  PD379(f).
- Finding 4 (STATUS over cap): only the cycle-155 purpose line was relocated verbatim to
  `archive/2026-10-09-status-cycle156-relocate.md` §1. The cycle 150–154 history lines are still in STATUS, because shell
  line-deletion needs approval in a runner session. They are left for the chat's codebase-lint card (STATUS STOP line,
  2026-10-09).
