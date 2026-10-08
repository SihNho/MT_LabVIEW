# retrospective-cycle147

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** 
- **date:** 2026-10-08 14:24:32
- **outcome:** TIMEOUT (600s)
- **verdict-card:** NO-VERDICT: outcome TIMEOUT
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle147, role retrospective) ---
CLAIM: Cycle 147 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 147 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-08 01:14:07  ..  2026-10-08 14:14:12   (780 min)
    basis: start = archive/peer/2026-10-08-retrospective-cycle146.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-10-08 01:14 .. 2026-10-08 14:14 (780 min, an explicit cycle window): 93 build logs, 13 peer logs, 4 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 92/93 ok; NO BGRUN line in ['fn_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 14 logs recorded a failure; unreviewed: ['diag_c147_b1_1_rescore.log', 'diag_c147_c3_2_scrreq.log', 'diag_c147_c3_3_scrreq.log', 'selftest_stagekit_c147b13_new.log']
  PASS  A4 every archived review says what was done with it: 4/4 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 10800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['diag_c147_b1_1_probe.log', 'prep_c147_c3_3_card.log', 'selftest_stagekit_c147b13_new.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 100, failure markers 17, logs carrying a failure 14
  C2 peer reviews dispatched 13, archived 4
  C3 wall-clock inside bgrun, BUILDS ONLY 57 min 30 s
  C4 wall-clock inside bgrun, REVIEWS 7 min 13 s; cost $3.9191 from 2 log(s) that report one
  C4b cost lines seen 2 / parsed 2
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 179 min 29 s; cost $66.5128 from 9 log(s) - cycle_147.log, cycle_147_assign_1.log, cycle_147_assign_2.log, cycle_147_assign_3.log, cycle_147_handback_1.log, cycle_147_handback_2.log
  C5 total wall-clock 244 min 12 s  (builds 23%, reviews 2%, judgement session 73%)

  C6 material-marked recipe/bench runs 49, judgement-session attempts refused 10  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1/ring-p4c.md [tools/bench/next.json plan.path]: 280 - STATUS.md, docs/chat-handoff.md, docs/violation-decisions.md, tools/bench/.stall_samples.txt, tools/bench/adopted_scratch.jsonl, tools/bench/cards/brief_147-a1-1.md, tools/bench/cards/brief_147-a1-2.md, tools/bench/cards/brief_147-a1-3.md, tools/bench/cards/brief_147-a1-4.md, tools/bench/cards/brief_147-a1-5.md, tools/bench/cards/brief_147-a1-8.md, tools/bench/cards/brief_147-a2-1.md??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 351/1191 ok; 840 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  FAIL  L2 every cited project path exists: 2 DANGLING of 2989 citations checked:
       docs/d1/ring-p4.md:131 -> tools/bench/build_oploopendref_v0.py
       STATUS.md:126 -> tools/bench/build_oploopendref_v0.py

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:193 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/d1/INDEX.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/d1/INDEX.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 735 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  FAIL  L8 decision headers carry HH:MM: 1 header(s) dated >= 2026-09-28 without a parseable HH:MM (violations.py DEC_RE reads them as bare dates): ['docs/violation-decisions.md:1875']
  WARN  L9 new Pre-decided items carry a USER-RULES: line: 1 item(s) >= 238 without `USER-RULES:` (read docs/user-rules.md and cite the rows relied on, or write `USER-RULES: none apply`): ['docs/d1/tooling.md:145 (item 329)']
  FAIL  L10 active docs stay <= 400 lines: 2 doc(s) over the cap: ['docs/chat-handoff.md 550', 'docs/d1/ring-p3b.md 419']. Freeze in place (`status: frozen` + footer, tools/bench/freeze_docs_d1.py) and index what is in force, or split into linked topic files.
  WARN  L10a reference tables over the cap (exempt): docs/NAMES.md 1405; docs/camera-acquisition-facts.md 759; docs/toolkit-capabilities.md 1027
  WARN  L10b grandfathered docs over the cap (judgement: freeze, split or exempt): docs/frame-loop-wire-graph.md 472; docs/gpu-backend.md 444; docs/keystone-op-spec.md 608; docs/main-vi-panel-map.md 621; docs/restructure-plan-4.6.md 495
  WARN  L11 frozen docs carry a FROZEN footer: 1 without one: ['docs/d1/ring-p4.md']
  WARN  L12 function table matches the code: moved 34 (stagekit.op:add_shift_reg, stagekit.op:case_frame_wire, stagekit.op:case_in, stagekit.op:case_wired, stagekit.op:connect ...) - run py tools/gen_capabilities.py

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review, L2 every cited project path exists, L8 decision headers carry HH:MM, L10 active docs stay <= 400 lines


=== BUILD LOGS INSIDE THE WINDOW (94; read them directly, they are the primary record) ===
tools/bench/diag_c147_a1_1_adopt.log  (2026-10-08 01:22:36)
tools/bench/diag_c147_a1_1_check_after.log  (2026-10-08 01:41:32)
tools/bench/diag_c147_a1_1_check_before.log  (2026-10-08 01:22:10)
tools/bench/diag_c147_a1_1_el.log  (2026-10-08 01:36:26)
tools/bench/diag_c147_a1_1_elexp_final.log  (2026-10-08 01:36:43)
tools/bench/diag_c147_a1_1_elexp_pred.log  (2026-10-08 01:23:10)
tools/bench/diag_c147_a1_1_graph.log  (2026-10-08 01:40:53)
tools/bench/diag_c147_a1_1_graph_dry.log  (2026-10-08 01:37:28)
tools/bench/diag_c147_a1_1_graph_prerun.log  (2026-10-08 01:37:41)
tools/bench/diag_c147_a1_1_memload.log  (2026-10-08 01:41:17)
tools/bench/diag_c147_a1_1_mkgraph.log  (2026-10-08 01:24:01)
tools/bench/diag_c147_a1_1_t2626.log  (2026-10-08 01:41:16)
tools/bench/diag_c147_a1_4_check.log  (2026-10-08 02:05:19)
tools/bench/diag_c147_a1_4_check_after.log  (2026-10-08 02:19:42)
tools/bench/diag_c147_a1_4_jevwarm.log  (2026-10-08 02:15:24)
tools/bench/diag_c147_a1_4_scr_dry.log  (2026-10-08 02:06:02)
tools/bench/diag_c147_a1_4_scr_prerun.log  (2026-10-08 02:06:47)
tools/bench/diag_c147_a1_4_scrreq.log  (2026-10-08 02:07:00)
tools/bench/diag_c147_a1_8_check.log  (2026-10-08 12:50:48)
tools/bench/diag_c147_a1_8_check_after.log  (2026-10-08 13:12:14)
tools/bench/diag_c147_a1_8_jevwarm.log  (2026-10-08 13:06:15)
tools/bench/diag_c147_a1_8_scr_dry.log  (2026-10-08 12:51:32)
tools/bench/diag_c147_a1_8_scr_prerun.log  (2026-10-08 12:52:07)
tools/bench/diag_c147_a1_8_scrreq.log  (2026-10-08 12:52:08)
tools/bench/diag_c147_a2_1_check.log  (2026-10-08 02:42:41)
tools/bench/diag_c147_a2_1_check2.log  (2026-10-08 12:37:41)
tools/bench/diag_c147_a2_1_check3.log  (2026-10-08 12:45:14)
tools/bench/diag_c147_a2_1_dry.log  (2026-10-08 12:38:16)
tools/bench/diag_c147_a2_1_dry3.log  (2026-10-08 12:45:58)
tools/bench/diag_c147_a2_1_peek.log  (2026-10-08 02:37:56)
tools/bench/diag_c147_a2_1_prerun.log  (2026-10-08 12:39:26)
tools/bench/diag_c147_a2_1_prerun3.log  (2026-10-08 12:47:06)
tools/bench/diag_c147_a2_1_scr_dry.log  (2026-10-08 12:38:50)
tools/bench/diag_c147_a2_1_scr_dry3.log  (2026-10-08 12:46:31)
tools/bench/diag_c147_a2_1_scr_prerun.log  (2026-10-08 12:40:03)
tools/bench/diag_c147_a2_1_scr_prerun3.log  (2026-10-08 12:47:41)
tools/bench/diag_c147_a2_1_scrreq.log  (2026-10-08 12:40:04)
tools/bench/diag_c147_a2_1_scrreq3.log  (2026-10-08 12:47:42)
tools/bench/diag_c147_b1_1_probe.log  (2026-10-08 13:20:56)
tools/bench/diag_c147_b1_1_rescore.log  (2026-10-08 13:24:24)
tools/bench/diag_c147_b1_1_rescore2.log  (2026-10-08 13:24:55)
tools/bench/diag_c147_b1_2_t6_d4_after.log  (2026-10-08 13:34:25)
tools/bench/diag_c147_b1_2_t6_d4_before.log  (2026-10-08 13:30:38)
tools/bench/diag_c147_b1_2_t6_rebind_after.log  (2026-10-08 13:34:23)
tools/bench/diag_c147_b1_2_t6_rebind_before.log  (2026-10-08 13:30:37)
tools/bench/diag_c147_b1_4_new_stagekit.log  (2026-10-08 13:48:57)
tools/bench/diag_c147_b1_4_old_stagekit.log  (2026-10-08 13:48:32)
tools/bench/diag_c147_b1_4_old_tdkey.log  (2026-10-08 13:48:58)
tools/bench/diag_c147_b1_4_selftest_c147_b1_2.log  (2026-10-08 13:49:05)
tools/bench/diag_c147_c3_1_blocked.log  (2026-10-08 13:54:05)
tools/bench/diag_c147_c3_1_selftest_c147_b1_2.log  (2026-10-08 13:55:25)
tools/bench/diag_c147_c3_1_selftest_td_key.log  (2026-10-08 13:55:26)
tools/bench/diag_c147_c3_2_before.log  (2026-10-08 13:58:42)
tools/bench/diag_c147_c3_2_check.log  (2026-10-08 13:59:43)
tools/bench/diag_c147_c3_2_check2.log  (2026-10-08 14:00:20)
tools/bench/diag_c147_c3_2_dry.log  (2026-10-08 14:00:54)
tools/bench/diag_c147_c3_2_prerun.log  (2026-10-08 14:02:02)
tools/bench/diag_c147_c3_2_scr_dry.log  (2026-10-08 14:01:27)
tools/bench/diag_c147_c3_2_scr_prerun.log  (2026-10-08 14:02:37)
tools/bench/diag_c147_c3_2_scrreq.log  (2026-10-08 14:03:03)
tools/bench/diag_c147_c3_3_check.log  (2026-10-08 14:07:53)
tools/bench/diag_c147_c3_3_proven.log  (2026-10-08 14:12:21)
tools/bench/diag_c147_c3_3_scr_dry.log  (2026-10-08 14:09:53)
tools/bench/diag_c147_c3_3_scr_prerun.log  (2026-10-08 14:10:29)
tools/bench/diag_c147_c3_3_scrreq.log  (2026-10-08 14:10:30)
tools/bench/diag_c147_p4s06v18_scratch.log  (2026-10-08 13:05:21)
tools/bench/fn_gate.log  (2026-10-08 14:12:42)
tools/bench/jev_gate.log  (2026-10-08 14:13:41)
tools/bench/motor_session_end_20261008_appcrash.log  (2026-10-08 11:47:05)
tools/bench/motor_session_end_cycle146.log  (2026-10-08 01:14:19)
tools/bench/motor_session_start_cycle147.log  (2026-10-08 12:31:48)
tools/bench/prep_c147_a1_2_check_after.log  (2026-10-08 01:28:14)
tools/bench/prep_c147_a1_2_check_before.log  (2026-10-08 01:22:42)
tools/bench/prep_c147_a1_2_mk.log  (2026-10-08 01:26:07)
tools/bench/prep_c147_a1_2_mk_r3.log  (2026-10-08 01:27:40)
tools/bench/prep_c147_a1_2_probe.log  (2026-10-08 01:21:31)
tools/bench/prep_c147_a1_3_check_after.log  (2026-10-08 02:01:06)
tools/bench/prep_c147_a1_3_check_before.log  (2026-10-08 01:48:43)
tools/bench/prep_c147_a1_3_dry.log  (2026-10-08 01:57:44)
tools/bench/prep_c147_a1_3_elselftest.log  (2026-10-08 02:00:13)
tools/bench/prep_c147_a1_3_mk.log  (2026-10-08 01:51:58)
tools/bench/prep_c147_a1_3_pred.log  (2026-10-08 01:55:08)
tools/bench/prep_c147_a1_3_prerun.log  (2026-10-08 01:58:30)
tools/bench/prep_c147_a1_3_probe.log  (2026-10-08 01:53:36)
tools/bench/prep_c147_a1_3_rebase.log  (2026-10-08 01:53:05)
tools/bench/prep_c147_a1_3_scr_dry.log  (2026-10-08 01:59:17)
tools/bench/prep_c147_a1_3_scr_prerun.log  (2026-10-08 01:59:52)
tools/bench/prep_c147_a1_3_scrreq.log  (2026-10-08 02:00:19)
tools/bench/prep_c147_c3_3_card.log  (2026-10-08 14:13:42)
tools/bench/selftest_c147_b1_2.log  (2026-10-08 13:34:12)
tools/bench/selftest_cycle_runner_ff_c147a15.log  (2026-10-08 02:26:06)
tools/bench/selftest_cycle_runner_retro.log  (2026-10-08 02:24:10)
tools/bench/selftest_stagekit_c147b13_new.log  (2026-10-08 13:38:54)
tools/bench/selftest_td_key_c147b13_new.log  (2026-10-08 13:39:02)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (13) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_147.log  (2026-10-08 12:33:38)
tools/bench/cycle_147_assign_1.log  (2026-10-08 13:13:47)
tools/bench/cycle_147_assign_2.log  (2026-10-08 13:42:30)
tools/bench/cycle_147_assign_3.log  (2026-10-08 14:14:11)
tools/bench/cycle_147_handback_1.log  (2026-10-08 13:17:16)
tools/bench/cycle_147_handback_2.log  (2026-10-08 13:44:52)
tools/bench/cycle_runner.log  (2026-10-08 14:14:11)
tools/bench/cycle_runner_main_20261007_2343.log  (2026-10-08 11:47:04)
tools/bench/cycle_runner_main_20261008_1231.log  (2026-10-08 14:14:11)
tools/bench/peer_c147-a1-4-re1.log  (2026-10-08 02:19:08)
tools/bench/peer_c147-a1-8-re1.log  (2026-10-08 13:11:42)
tools/bench/retro.log  (2026-10-08 14:14:11)
tools/bench/runner_supervisor.log  (2026-10-08 14:14:11)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/d1/INDEX.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle147","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

(no answer within 600s — job stopped)

## Sources

(extract from answer)

## What was done with it

Disposed 2026-10-08 20:50 by the cycle-150 judgement session: the review produced no answer (job stopped at 600 s, `## Answer`
above), so there is nothing to accept or refuse. Cycle 147's work was judged in `docs/d1/ring-p4c.md` PD357 and PD358.
