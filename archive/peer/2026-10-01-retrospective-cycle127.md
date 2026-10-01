# retrospective-cycle127

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.0676  in 54 / out 29842 / cache-create 118838 / cache-read 2598981  (314s, 46 turn(s))
- **date:** 2026-10-01 23:46:14
- **outcome:** ANSWERED (316s)
- **verdict-card:** VERDICT-CARD retrospective-cycle127 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle127.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle127, role retrospective) ---
CLAIM: Cycle 127 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 127 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-10-01 22:07:43  ..  2026-10-01 23:40:54   (93 min)
    basis: start = archive/peer/2026-10-01-retrospective-cycle126.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-10-01 22:07 .. 2026-10-01 23:40 (93 min, an explicit cycle window): 32 build logs, 9 peer logs, 27 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 32/32 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 12 logs recorded a failure; unreviewed: ['diag_c127_5_errsel.log']
  FAIL  A4 every archived review says what was done with it: 23/27 annotated; blank: ['2026-10-01-g6-call-a-gemini.md', '2026-10-01-g6-call-b-claude.md', '2026-10-01-g6-call-b-gemini.md', '2026-10-01-priorart-c124-6-ring-p3a.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 8206 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['diag_c127_1_compile.log', 'diag_c127_1_tlb.log', 'diag_c127_3_checks.log']
  WARN  A9 accepted-but-unbuilt dispositions are cited by code: 21/22 not cited by a tools/ file or tools/bench/selftest_*: ['2026-09-25-hyp-selftest-elreuse-81', '2026-09-25-retrospective-cycle77', '2026-09-25-retrospective-cycle78', '2026-09-25-retrospective-cycle82', '2026-09-26-c89-profiler-fact', '2026-09-26-c91-smoke-k1', '2026-09-26-c91-step4-t12', '2026-09-26-c91-t0step3c-quit']??

  C1 builds run 34, failure markers 13, logs carrying a failure 12
  C2 peer reviews dispatched 9, archived 27
  C3 wall-clock inside bgrun, BUILDS ONLY 92 min 31 s
  C4 wall-clock inside bgrun, REVIEWS 7 min 21 s; cost $4.0942 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 99 min 52 s  (builds 92%, reviews 7%, judgement session 0%)

  C6 material-marked recipe/bench runs 27, judgement-session attempts refused 2  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 371 - docs/chat-handoff.md, tools/bench/.stall_samples.txt, tools/bench/cards/brief_127-1.md, tools/bench/cards/brief_127-2.md, tools/bench/cards/brief_127-3.md, tools/bench/diag_c127_1_cleanup.py, tools/bench/diag_c127_1_fsinner.py, tools/bench/diag_c127_1_tlb.py, tools/bench/diag_c127_2_chain.py, tools/bench/diag_c127_2_checks.py, tools/bench/diag_c127_2_probe.py, tools/bench/diag_c127_3_checks.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 345/1105 ok; 760 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2582 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 109 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  WARN  L5 superseded documents are not still current: docs/ring-buffer-design.md supersedes docs/d1-build-plan.md, which is still `status: current`
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 661 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:601', 'docs/NAMES.md:723']
  WARN  L8 decision headers carry HH:MM: 8 older header(s) with an unparseable time (historic, not edited): ['docs/violation-decisions.md:350', 'docs/violation-decisions.md:526', 'docs/violation-decisions.md:539', 'docs/violation-decisions.md:874', 'docs/violation-decisions.md:926', 'docs/violation-decisions.md:1161', 'docs/violation-decisions.md:1180', 'docs/violation-decisions.md:1320']
  PASS  L9 new Pre-decided items carry a USER-RULES: line: every item >= 238 carries one

AUDIT VIOLATIONS: A3 every failing log is followed by an archived review, A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (33; read them directly, they are the primary record) ===
tools/bench/c125_1_offline_measure_c127_2.log  (2026-10-01 22:36:48)
tools/bench/c125_1_offline_measure_c127_2b.log  (2026-10-01 22:39:36)
tools/bench/c125_1_offline_measure_c127_4.log  (2026-10-01 23:30:22)
tools/bench/diag_c127_1_cleanup.log  (2026-10-01 23:07:01)
tools/bench/diag_c127_1_compile.log  (2026-10-01 22:21:38)
tools/bench/diag_c127_1_fsinner.log  (2026-10-01 23:02:34)
tools/bench/diag_c127_1_tlb.log  (2026-10-01 22:18:47)
tools/bench/diag_c127_2_chain.log  (2026-10-01 22:26:38)
tools/bench/diag_c127_2_chain2.log  (2026-10-01 22:29:44)
tools/bench/diag_c127_2_chain3.log  (2026-10-01 22:30:20)
tools/bench/diag_c127_2_checks.log  (2026-10-01 22:36:31)
tools/bench/diag_c127_2_probe.log  (2026-10-01 22:18:00)
tools/bench/diag_c127_3_checks.log  (2026-10-01 23:19:09)
tools/bench/diag_c127_3_dry1.log  (2026-10-01 23:13:52)
tools/bench/diag_c127_3_facts.log  (2026-10-01 23:11:38)
tools/bench/diag_c127_4_checks.log  (2026-10-01 23:31:47)
tools/bench/diag_c127_4_selftest.log  (2026-10-01 23:28:36)
tools/bench/diag_c127_5_dry.log  (2026-10-01 23:33:03)
tools/bench/diag_c127_5_errsel.log  (2026-10-01 23:38:12)
tools/bench/diag_c127_5_prerun.log  (2026-10-01 23:33:15)
tools/bench/jev_gate.log  (2026-10-01 23:40:49)
tools/bench/motor_session_end_cycle126.log  (2026-10-01 22:13:02)
tools/bench/motor_session_start_cycle127.log  (2026-10-01 22:13:10)
tools/bench/plan_ring_p3b_make_c127_2.log  (2026-10-01 22:26:10)
tools/bench/plan_ring_p3b_make_c127_2b.log  (2026-10-01 22:29:18)
tools/bench/plan_ring_p3b_make_c127_2c.log  (2026-10-01 22:33:27)
tools/bench/plan_ring_p3b_make_c127_3.log  (2026-10-01 23:17:46)
tools/bench/selftest_case_frame_c124_c127_4.log  (2026-10-01 23:31:51)
tools/bench/selftest_errorlist_check_header_c127.log  (2026-10-01 22:41:44)
tools/bench/selftest_errorlist_ocr_c127.log  (2026-10-01 22:41:26)
tools/bench/selftest_errorlist_reuse_81_c127.log  (2026-10-01 22:41:51)
tools/bench/selftest_errorlist_reuse_81_c127_3.log  (2026-10-01 23:18:40)
tools/bench/wait_runner_event.log  (2026-10-01 22:41:19)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (9) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_126.log  (2026-10-01 22:12:55)
tools/bench/cycle_127.log  (2026-10-01 22:13:12)
tools/bench/cycle_runner.log  (2026-10-01 22:13:11)
tools/bench/cycle_runner_main_20261001_1227.log  (2026-10-01 22:13:03)
tools/bench/cycle_runner_main_20261001_2213.log  (2026-10-01 22:13:11)
tools/bench/peer_c127_1_timeout.log  (2026-10-01 23:06:25)
tools/bench/peer_c127_3_dry_hyp.log  (2026-10-01 23:22:04)
tools/bench/peer_c127_4_dry_pool.log  (2026-10-01 23:36:05)
tools/bench/retro.log  (2026-10-01 23:40:53)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle127","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

I'm naming one structural fault for cycle 127, and the judgement session caused it. The brief told the LabVIEW diagnostic to read the Error List after every wire, although logs on file already showed each such read takes about 6.5 minutes. The run timed out, and about 24 minutes of the 93 were lost to it.

The evidence window is 22:07:43–23:40:54. The judgement session started at 22:13:12 (`tools/bench/cycle_127.log:1`). It ran five cards:

| Card | Kind | Status | Bound at |
|---|---|---|---|
| 127-1 | LabVIEW | FAIL | 22:15:48 |
| 127-2 | offline | PASS | 22:15:49 |
| 127-3 | offline | FAIL | 23:10:08 |
| 127-4 | offline | FAIL | 23:24:34 |
| 127-5 | LabVIEW | FAIL | 23:24:35 |

The bind times are at `tools/bench/cards/guard_card.log:555-568`. The cycle saved no new VI and launched no stage.

## The structural fault: `inference-over-measurement`, card 127-1

**What happened**
- `tools/bench/cards/brief_127-1.md:18` asked for an Error List read (`--count-only --role scratch`) after each second-sink wire. The script also read once after the first crossings, so five reads were planned (`diag_c127_1_fsinner.py:37-44`, log `:79,88,98,108`).
- The cost of one such read was already measured that afternoon: 385.8 s, on 55 items (`tools/bench/stage_d1_ring_p3a_el_scratch.log:89`, run at 17:47). Earlier runs gave the same figure (`stage_d1_ring_p2b_el_scratch.log:88`, `p2a:88`).
- Five reads come to about 32 min of reads alone. Add the LabVIEW restart and about 100 s per wire, and the run needs about 48 min. The card gave it 50 min in total (`task_127-1.json:59`). The run was launched with a 40-min limit (`diag_c127_1_fsinner.log:1`).
- That arithmetic was free, and nobody did it.

**What it cost**
- The run went from 22:22:32 to `BGRUN TIMEOUT killed after 2402s` (`diag_c127_1_fsinner.log:116`).
- The fourth route row, BufNum → `Latest`, never had its census read.
- It needed a hypothesis review costing $1.2944 (`archive/peer/2026-10-01-c127-1-fsinner-timeout.md:7`) and a cleanup script that ran twice, 23:03:33 → 23:06:51 (`tools/hooks/material_marker.log:2954-2955`).
- The three reads after the first one each returned 61 / 24, unchanged (`:88,98,108`). They told us nothing.
- The review estimates the same diagnostic with one read at the end at about 20 min (`:102`).
- My loss estimate is about 24 min: about 20 min of LabVIEW time plus about 4 min of review and cleanup. The session's own figure is about 28 min (`docs/d1-loop12-17-split-plan.md:2822`).

**Why it changed how the cycle ended**
- The offline card 127-2 finished about 22:42. The session dispatched both cards in one message, so it could not continue until 127-1 also returned.
- Card 127-3 was therefore not bound until 23:10:08. Nothing in the offline lane ran for about 28 min.

**Counterfactual:** Suppose the brief had said "one Error List read at the end" at 22:15. That is exactly the rule PD258(a) made afterwards, at `plan:2759`.
- The diagnostic ends about 22:43, with all 4 of 4 rows measured.
- Card 127-3 is dispatched about 22:47 instead of 23:10.
- The 127-3 → 127-4/127-5 chain ends about 23:18 instead of 23:40.
- Alternatively, the multi-object binder card that `next.json:4` now leaves for cycle 128 fits into the freed time.

I see no second fault of the same size.

## Findings

**1. Repeated failure.**
- Three dry runs in a row each stopped at one new simulator defect in code that 127-2 had just added:
  - the IMAQ Copy binding (`diag_c127_2_checks.log:5-8`);
  - a `SimError` that escaped the dry run, renumbering bug, with no RESULT line (`diag_c127_3_checks.log:25-26`);
  - the binding of two new LoopTunnels (`diag_c127_4_checks.log:4-6`). The review for this one already predicts that the 3 FSOT binding fails next.
- In each case `stagesim` simulated the plan cleanly, but the `stagexec` dry run failed.
- The approach should have changed at attempt 2 (127-3): audit every row through the simulated backend before fixing the next one, instead of fixing one defect per card.
- These fixes were real work, though, so I count this as a finding rather than a fault.
- The Error List time sink is also a repeat across cycles. The count-only mode (card chat-P2) still costs about 6.5 min per read.

**2. Missing tool.**
- The pre-run checks predict memory (the 2026-09-27 03:30 device) but not wall-clock time.
- A check that adds up the measured cost of each op and read and compares it with `--max-min` and the card's minutes would have refused 127-1 before launch.
- Separately, `Stage(deadline_min)` stops nothing on its own (`tools/stagekit.py:294-295`, from the review at `:54`). That remains unfixed.

**3. Unmeasured steps.**
- The main one is the fault above.
- 127-5's zero-hit donor search did not log a row count per file (`result_127-5.json:13`). "No such node" and "empty read" cannot be told apart, so a rerun is owed.

**4. Rule compliance (CLAUDE.md).**
- **Failed prediction without review:** `diag_c127_5_errsel.log` failed and got no archived review (audit A3; CLAUDE.md:673). The judgement session dealt with it directly in PD260(c).
- **Return at first unexpected result evaded:** 127-2 ran its plan maker three times, fixing failures 1 and 2 inside the card (`result_127-2.json:32`).
- **"A step leaves a file" broken:** the diagnostic writes OUT only at the end (review `:107`).
- **What the audit does not cover:**
  - A4's four blank reviews belong to earlier cycles. A4 works by date only, so it contradicts the window.
  - C6 calls `material_marker.log:2937,2939` "judgement-session attempts", but both were material-session commands.
  - C7 lists 371 files, including this cycle's own briefs, so it cannot show scope creep.
  - No check compares a run's time against its measured costs.

**5. Ordering.** Running the LabVIEW and offline cards side by side (PD257(e)) was sound. The weak point was batching: the session dispatched both in one message, so the offline lane sat idle behind the slow LabVIEW card.

**6. Not reported.**
- STATUS.md:60 says "MEASURED 3/3". The plan had four rows, so it was 3 of 4; the fourth is deferred to P3b's scratch run.
- STATUS.md:64 states "no creation route" more firmly than the evidence allows, given the unseparated zero-hit read in Finding 3.
- Both `BGRUN STAGE-RUN` lines carry `card=None` (`diag_c127_1_fsinner.log:3`, `diag_c127_5_errsel.log:3`).
- Every result card has `usd: null`. The only dollar figure is the $4.09 spent on reviews.

**7. Judgement inside a material session.**
- 127-1's material session cut the run limit to 40 min, below the script's documented 45 and the Stage's 42 (review `:57`, `:120`).
- 127-2 chose an explanation for FS frames whose owner uid is 0, inferring the parent from FSIT rows (`result_127-2.json:19`).
- 127-3 chose to pair unnamed terminal keys by read order (`result_127-3.json:20`). The 127-4 review later says order-based pairing is wrong for borders.
- The judgement session accepted all three only afterwards, in PD258(d) and PD259(a).

## Device effect

No listed device failed to stop its own fault inside the window.
- **Exercised and working:**
  - `gates_due` (`cycle_127.json:28-49`).
  - Cost-line parsing (C4b 3/3).
  - The bgrun inner-failure rc (the `diag_c127_3_checks.log` and `diag_c127_5_errsel` runs both ended rc=1).
  - The review card's "attack the claim" instructions (review `:39-44`).
  - The pre-run gate refused the launch before its dry run (`material_marker.log:2939`), then allowed it after `prerun_records.jsonl:512-517`.
- **Not exercised:** the stop record, the prior-art gate, the memory prediction and the opmodels replay, because no recipe was launched.
- **Covers a different failure:** the "collect every failure" dry device (2026-09-25 16:10 / 09-27 20:20) covers routing and checkpoint failures. The binding and `SimError` failures in Finding 1 are outside its stated scope.
- **Near misses that are not on the list:**
  - `guard_peer` fired wrongly three times (fp-16 and fp-18 in `gate_fp_queue.jsonl:16,18`, plus 127-5's roughly 3-min hold, `plan:2823`).
  - C7 is saturated at 371 files.

VIOLATION: inference-over-measurement | loss_min=24 | loss_usd=1.2944 | evidence=tools/bench/cards/brief_127-1.md:18

VERDICT {"schema":"verdict/1","id":"retrospective-cycle127","verdict":"refuted","alternative":"The timeout was a LabVIEW hang in S_latest's post-connect census read, not the clock: the kill landed in those reads, 64 s after the last raw file (review :74-79).","discriminating_test":"Rerun fsinner S_latest only, timestamped, one Error List read at the end (dump_tree=False): CENSUS S_latest within ~60 s of its connect and total ~20 min means budget; a stall >3 min means a hang.","violations":[{"slug":"inference-over-measurement","loss_min":24,"loss_usd":1.2944,"evidence":"tools/bench/cards/brief_127-1.md:18"}],"sources":["tools/bench/cards/brief_127-1.md:18","tools/bench/stage_d1_ring_p3a_el_scratch.log:89","tools/bench/diag_c127_1_fsinner.log:116","archive/peer/2026-10-01-c127-1-fsinner-timeout.md:7","tools/bench/cards/guard_card.log:562","docs/d1-loop12-17-split-plan.md:2822"],"note":"Brief ordered 5 per-wire Error List reads at a measured 386 s each into a 50-min card; the 40-min run timed out, 3 reads were uninformative (61/24 unchanged), the offline lane idled ~28 min. No listed device failed."}

## Sources

(extract from answer)

## What was done with it

- **ACCEPTED: `inference-over-measurement`.** My brief (`brief_127-1.md:18`) asked for a per-wire Error List read without
  adding up the measured 386 s per read against the card's minutes. Already answered for the future by PD258(a) (ONE
  Error List read per diagnostic, `docs/d1-loop12-17-split-plan.md` Pre-decided 258(a)); in addition, every brief I write
  from cycle 128 states its time arithmetic (measured cost per op and per Error List read vs `budget.minutes` and
  `--max-min`). The verdict's alternative (a LabVIEW hang in S_latest's census read) stays open: P3b's full scratch run,
  timestamped, reads that row's census and separates budget from hang.
- Finding 6 corrected in STATUS (cycle-127 brief): "3 of 4 measured", and "no route found in the donors searched so far".
- Finding 1 (one simulator defect per card) is taken into cycle 128's offline card: after the multi-object binder, the dry
  run audits EVERY row through the simulated backend and returns all binding failures at once, not the first.
- Finding 2 (a time-budget prerun check; `Stage(deadline_min)` stopping nothing) — carried as tooling debt, not built now.
- Finding 5: the two parallel Agent calls block until both return; noted for the next judgement session.
