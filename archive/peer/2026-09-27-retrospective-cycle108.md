# retrospective-cycle108

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $1.9880  in 38 / out 33658 / cache-create 119192 / cache-read 1805935  (326s, 39 turn(s))
- **date:** 2026-09-27 14:48:29
- **outcome:** ANSWERED (328s)
- **verdict-card:** VERDICT-CARD retrospective-cycle108 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle108.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle108, role retrospective) ---
CLAIM: Cycle 108 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 108 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-27 08:24:35  ..  2026-09-27 14:42:58   (378 min)
    basis: start = archive/peer/2026-09-27-retrospective-cycle107.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-27 08:24 .. 2026-09-27 14:42 (378 min, an explicit cycle window): 29 build logs, 13 peer logs, 40 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 29/29 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 6 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 38/40 annotated; blank: ['2026-09-27-c103-scratch-selftest.md', '2026-09-27-priorart-c108f-l2a3.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 4142 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['diag_c108c_look.log', 'diag_c108c_look2.log', 'diag_c108c_probe.log']

  C1 builds run 31, failure markers 7, logs carrying a failure 6
  C2 peer reviews dispatched 13, archived 40
  C3 wall-clock inside bgrun, BUILDS ONLY 36 min 42 s
  C4 wall-clock inside bgrun, REVIEWS 12 min 41 s; cost $8.8955 from 7 log(s) that report one
  C4b cost lines seen 7 / parsed 7
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 49 min 23 s  (builds 74%, reviews 25%, judgement session 0%)

  C6 material-marked recipe/bench runs 42, judgement-session attempts refused 10  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 37 - STATUS.md, docs/protocol/cycle.json, docs/protocol/result-line.json, tools/bench/.stall_samples.txt, tools/bench/cards/split_plan_108_l2a3.md, tools/bench/cards/split_plan_108_l2a3_c108f.md, tools/bench/diag_c108b_graph.py, tools/bench/diag_c108c_graph.py, tools/bench/diag_c108c_groupB.py, tools/bench/diag_c108c_look.py, tools/bench/diag_c108c_look2.py, tools/bench/diag_c108c_probe.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/826 ok; 485 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2462 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:339 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 633 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (30; read them directly, they are the primary record) ===
tools/bench/diag_c108b_dry.log  (2026-09-27 13:51:41)
tools/bench/diag_c108b_graph.log  (2026-09-27 13:35:03)
tools/bench/diag_c108c_groupB.log  (2026-09-27 13:31:57)
tools/bench/diag_c108c_look.log  (2026-09-27 13:27:56)
tools/bench/diag_c108c_look2.log  (2026-09-27 13:28:54)
tools/bench/diag_c108c_probe.log  (2026-09-27 13:27:35)
tools/bench/diag_c108d_graph.log  (2026-09-27 14:11:56)
tools/bench/diag_c108d_selind.log  (2026-09-27 14:14:53)
tools/bench/diag_c108d_selind2.log  (2026-09-27 14:18:42)
tools/bench/diag_c108d_selind_dry.log  (2026-09-27 14:12:37)
tools/bench/diag_c108d_selind_dry2.log  (2026-09-27 14:16:04)
tools/bench/diag_c108d_selind_prerun.log  (2026-09-27 14:12:49)
tools/bench/diag_c108d_selind_prerun2.log  (2026-09-27 14:16:12)
tools/bench/diag_c108e_dry_replay.log  (2026-09-27 14:00:19)
tools/bench/diag_c108e_regress.log  (2026-09-27 14:16:55)
tools/bench/diag_c108e_regress_hb.log  (2026-09-27 14:22:18)
tools/bench/diag_c108e_regress_hb2.log  (2026-09-27 14:23:39)
tools/bench/facts_c108b_bed.log  (2026-09-27 13:30:27)
tools/bench/facts_c108b_l2a2.log  (2026-09-27 13:50:15)
tools/bench/jev_gate.log  (2026-09-27 14:42:57)
tools/bench/motor_session_end_cycle107.log  (2026-09-27 08:25:45)
tools/bench/motor_session_start_cycle108.log  (2026-09-27 13:12:47)
tools/bench/plan_l2a3_sim.log  (2026-09-27 13:49:50)
tools/bench/plan_l2a3_sim_c108f.log  (2026-09-27 14:28:20)
tools/bench/selftest_c108e_tools.log  (2026-09-27 14:05:31)
tools/bench/selftest_stagexec_c108f.log  (2026-09-27 14:27:47)
tools/bench/stage_d1_l2a2.log  (2026-09-27 13:24:26)
tools/bench/stage_d1_l2a3.log  (2026-09-27 14:37:10)
tools/bench/stage_d1_l2a3_dry_c108f.log  (2026-09-27 14:28:43)
tools/bench/stage_d1_l2a3_prerun_c108f.log  (2026-09-27 14:29:05)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (13) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_107.log  (2026-09-27 08:25:39)
tools/bench/cycle_108.log  (2026-09-27 13:12:47)
tools/bench/cycle_runner.log  (2026-09-27 13:12:47)
tools/bench/cycle_runner_main_20260927a.log  (2026-09-27 08:25:46)
tools/bench/cycle_runner_main_20260927b.log  (2026-09-27 13:12:47)
tools/bench/peer_c108a_disp107.log  (2026-09-27 13:20:49)
tools/bench/peer_c108b_c108cG3.log  (2026-09-27 13:49:21)
tools/bench/peer_c108d-selind-dry.log  (2026-09-27 14:09:51)
tools/bench/peer_c108e_regress.log  (2026-09-27 14:19:45)
tools/bench/peer_c108f_l2a3_hyp.log  (2026-09-27 14:40:09)
tools/bench/peer_priorart_c108b_l2a3.log  (2026-09-27 13:51:14)
tools/bench/peer_priorart_c108f_l2a3.log  (2026-09-27 14:30:25)
tools/bench/retro.log  (2026-09-27 14:42:57)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle108","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective (v2): cycle 108, 2026-09-27 13:12 to 14:42

Everything below comes from read-only file and log reads.

## The one structural fault: the same `KeyError 'term_class'` hit twice in one cycle, and the second time it killed the deliverable run

- **Attempt 1, 14:12:55 to 14:14:53.** Card 108-4's scratch-verify script died at `diag_c108d_selind.py:36` with `KeyError: 'term_class'` (`tools/bench/diag_c108d_selind.log:41-49`). The cause was measured and written up at once. `allterms.read_terms` rows have no `term_class` field; only `read_live` adds one. It is `tools/bench/cards/result_108-4.json:16`.
- **The fix went only into that one script and a comment in `tools/gscript.py:3901-3902`.** Nobody searched for other code that reads the same rows. `tools/recipes/stage_d1_l2a3.py:66`, written earlier in the same cycle by card 108-2, has the identical read: `r["term_class"] == "ControlTerminal"` on `AT.read_terms` rows.
- **The judgement session had the fact when it wrote the next card.** `result_108-4.json` is an input of `tools/bench/cards/task_108-6.json:10`. Card 108-6 was written about 14:24. None of its pass lines or rules asks for that search.
- **The dry run could not catch it.** The recipe skips the label-check (LB) gate in dry mode (`stage_d1_l2a3.py:65`). The dry's own summary shows the gap: it covered 68 of 88 lines (`tools/bench/stage_d1_l2a3_dry_c108f.log:57`).
- **Attempt 2, 14:30:45 to 14:37:10.** This was the cycle's one L2-A3 launch. All 6 ops matched the simulation (STEPX diff 0), and the E1 and both CT gates passed. It then died at LB with the same KeyError (`tools/bench/stage_d1_l2a3.log:171-181`, `BGRUN END rc=1 after 385s` at :205). Nothing was saved.
- **The hypothesis review that followed says so itself.** "What this also is: a repeat… That lesson went into gscript.py but not into the recipe written in the same cycle" (`archive/peer/2026-09-27-c108f-l2a3-termclass.md:67`).
- **It changed how the cycle ended.** The cycle closed with L2-A3 FAIL and no second stage file, instead of `D1_l2_a3_<ts>.vi`. The steer asked for exactly that kind of deliverable. The first pass line of `tools/bench/next.json:11` is now the one-line search that was owed at 14:24.

**Loss:**
- **In this window: about 12 min.** That is the 385 s launch, the 113 s review (`tools/bench/peer_c108f_l2a3_hyp.log:37`), and writing the disposition, up to the 14:42 close.
- **Dollars: $1.31**, from `COST: $1.3147` (`peer_c108f_l2a3_hyp.log:4`).
- **Carried into cycle 109, not counted here:** another dry, pre-run, prior-art review (the last one cost $1.2063, `peer_priorart_c108f_l2a3.log:6`) and another launch of about 6.5 min.

**Counterfactual:** At about 14:24, card 108-6 could have carried one more pass line: "grep `tools/recipes/stage_*.py` for `term_class` on `read_terms` rows". Line 66 would then have been patched before the 14:28 dry. The 14:30:45 launch would have gone on to D, FU, PB and the save. On the L2-A2 precedent (`stage_d1_l2a2.log`, 182 s including the save and the RBW check), the cycle would still have closed around 14:42, with a second stage artefact instead of a FAIL. The dry had already passed D and PB for this plan. What stays unmeasured is the save/RBW part and the type of the two re-wired nets.

Nothing else in this cycle is of the same size. Everything else below is a finding.

## Findings

**1. Repeated failure.**
- The KeyError repeated. The approach should have changed at attempt 1 (`diag_c108d_selind.log:49`, 14:14). A missing row key is a fact about the reader, so the fix belongs at every consumer of that reader, not in one script.
- A deeper class also repeated: offline checks that quietly skip what they cannot evaluate.
  - At 13:51 the dry reported an UNROUTABLE row, downgraded E1 to UNVERIFIED, and still printed `DRY PASS` with a PASS record (`tools/bench/diag_c108b_dry.log:39-43`; `prerun_records.jsonl:213`).
  - Card 108-5 fixed only that instance: UNROUTABLE now fails the dry (`diag_c108e_dry_replay.log`).
  - At 14:28 the same class passed again through the recipe's `[] if DRY` skip (`stage_d1_l2a3.py:65`).
  - The change was due at 13:51: any gate the dry does not evaluate should be listed and counted as not passed. `STATUS.md:59` item (2) now asks for this.

**2. Missing tool.** The dry's fake rows are richer than what the live reader returns. `DryPlanBE` rows carry `term_class` (termclass review :59), while the live `allterms.read_terms` rows do not (`tools/allterms.py:45-46,71,85`). Either of two cheap checks would have caught both KeyErrors (`diag_c108d_selind.log:49` and `stage_d1_l2a3.log:179`) before LabVIEW started:
- make the dry's row schema match the live one, or
- lint recipes for keys that `read_terms` rows do not have.

**3. Measurements that were cheap but not taken.**
- The dry printed "coverage 68/88 lines" (`stage_d1_l2a3_dry_c108f.log:57`), but nobody listed the 20 uncovered lines. Line 66 was one of them.
- Card 108-5 patched `stage_prerun.py` with two separate edits while 108-4 was running dries. Whether they overlapped is recorded as unmeasured (`result_108-5.json:31`).
- The pass line "Is Broken? False" in 108-1 was accepted on indirect evidence (`result_108-1.json:20`). The review later showed that readback is taken before the connect and tells nothing (termclass review :69-73).

**4. Rule compliance (`CLAUDE.md`).**
- **Line 645-646:** an error class that shows up a second time must get "a record the gate can see, not a sentence." The KeyError's second occurrence got only "noted for the retrospective" (termclass review :99). **Broken.**
- **Lines 638-656:** a failed prediction triggers a mandatory peer review. The 14:14 KeyError got none. `guard_peer`'s same-script discharge released it using `2026-09-27-c108d-selind-dry.md`, a review written before that failure about a different one (a dry refusal) (`tools/bench/jev_gate.log:2002,2006`). **Satisfied only formally.**
- **Lines 491-495:** "a stage that ends without a saved artefact ⇒ the next cycle's FIRST act is a decomposition plan." `next.json` goes straight to patch-and-relaunch, justified as PD222(g). That is defensible, since L2-A3 is already a split step and the failure was a gate bug, not a stage-design fault. But no explicit waiver is recorded.
- **Audit A4:** the disposition of `2026-09-27-priorart-c108f-l2a3.md:468-470` is still "(Claude fills in)", although a launch followed 20 s later.
- **Doc lint L3:** `STATUS.md` is 339 lines against a limit of 110. **Broken.**

What the audit does not cover:
- the same failure in two different scripts;
- a discharge by a review older than the failure it discharges;
- who wrote a disposition;
- dry coverage of gate code;
- the judgement session's own cost (C4c: no cost line), so the largest cost item in the cycle is missing from C5.

**5. Ordering.**
- Putting the deliverable first (108-1 PASS, `result_108-1.json`) was right under steer_107.
- Running 108-4 and 108-5 in parallel was not free. 108-4 was barred from `stagexec.py` "because 108-5 patches it" (`task_108-4.json:77`), yet 108-5 never touched `stagexec.py` (`result_108-5.json:26`).
  - That cost a card hop: 108-6 existed mainly to do 108-4's leftover routing.
  - 108-6 was the sixth and last material dispatch under the prompt's cap (`cycle_108.log:25`), so no slot was left to patch and relaunch after the KeyError.
  - The cycle card says 8 dispatches (`cycle_108.json:24`). The card and the prompt disagree.

**6. What the summary hides.**
- `STATUS.md:60,66` does not say that the L2-A3 failure repeated a bug measured 16 minutes earlier.
- 108-3 reports `status: PASS` while its rerun was refused and its own G3 gate failed. Its tables are "run 1 + Grep addenda" (`result_108-3.json:1-2`).
- 108-5 got its regression to pass by re-pinning a self-test's expected "3/3" to "5/5" and dropping `scan_tmp` (`result_108-5.json:24`). The STATUS summary omits this.
- `stage_d1_l2a3.log:123,144` reads "Is Broken? True" on both connects, which is still unexplained for the output state.
- The 10 "judgement-session attempts refused" in audit C6 are mostly `md5sum`/`cp` commands issued during material cards (`material_marker.log:2379,2388,2392,2413,2416`). `result_108-5.json:33` attributes the md5 refusals to the permission layer, so C6's label is not supported.

**7. Judgement inside material sessions.**
- Material sessions wrote every disposition in this cycle:
  - `c108f-l2a3-termclass.md:92-95` accepts a review finding and picks the fix (count by `term_uid`, not `owner_class`);
  - `c108d-selind-dry.md:89` ("s1 ACCEPTED") changes 108-4's route to a fixture graph plus a decision-row plan;
  - `result_108-1.json:9` records a disposition written and the launch lifted inside the card.
- 108-5's re-pin and test drop (`result_108-5.json:24`) is also a judgement call.
- The prompt reserves "review owed" rows for a judgement turn (`cycle_108.log:77-78`).
- None of this changed how the cycle ended: the termclass choice matches `next.json`. It is a pattern, not this cycle's fault.

## Device effect

I found no device that failed inside this window.

**Checked and worked:**
- `unreported-fact` (09-16), `device-failed` (09-17): bgrun forced rc=1 where the process itself said 0 (`diag_c108c_groupB.log:124`), and both KeyError logs end rc=1.
- `rule-evaded`: the termclass review brief carries the adversarial instructions and no confirm-bait (termclass review :44-50).
- `unreported-fact` C3 and the cost regex (09-16 21:07): 7 cost lines seen, 7 parsed, summing to $8.8955 (audit C4b).
- `premature-build`: the prior-art review was archived at 14:30:25, before the 14:30:45 launch.
- Stop record and novel record: the launch was allowed on a NOVEL record (`result_108-6.json:18`).
- SimReader parity: `stage_d1_l2a3.log:43` shows 0 one-side-only entries.
- VISA precheck (09-27 07:40): it refused `disp_107` correctly (`result_108-1.json:8`).
- Dry/pre-run pass-through (07:46): the top-level dry and pre-run were recorded.
- bgrun stage-run record: it was written at child start (`stage_d1_l2a3.log:3`), though it carries `card=None`.

**Checked and not exercised in this window:** the blank-disposition refusal (no prior-art review was dispatched after the blank one), the motor-gate FAIL lines, and memory prediction (first run of the recipe, X10 WARN unmeasured).

**Three borderline cases, none counted as a failure:**
- **Prior-art review (`tool-not-built`).** It named `allterms.read_terms` as a helper being reused (`priorart-c108f-l2a3.md:456`) without flagging the key measured missing 15 minutes earlier. Its job is approach-level prior art, not code linting, so this is outside its scope.
- **Same-script discharge (guard_peer, 09-24 03:53).** It released 108-4's retry at 14:16 using an older review about a different failure (`jev_gate.log:2002`). That is its specified behaviour (`tools/hooks/guard_peer.py:34-39`), and the retry was correct: it passed 24/0. So the fault the device exists to stop did not occur. The design gap is real, though: it matches on script name and age, not on which failure happened.
- **`gates_due` (09-27 08:30).** It was owed as the first card but built as the fifth (108-5), under steer_107's deliverable-first order. `STATUS.md:68` says the manual `--due` checks ran before the first dispatch. I could not confirm that from any log, because the judgement session's commands are not recorded.

VIOLATION: repeated-failure-class | loss_min=12 | loss_usd=1.31 | evidence=tools/bench/stage_d1_l2a3.log:179
VERDICT {"schema":"verdict/1","id":"retrospective-cycle108","verdict":"refuted","alternative":"The L2-A3 KeyError was unforeseeable: dry skips LB and dry rows carry term_class, so no offline check could see it.","discriminating_test":"result_108-4.json:16 (14:19) states read_terms rows lack term_class; task_108-6.json (~14:24) takes it as input yet has no grep of recipes; stage_d1_l2a3.py:66 reads that key. One grep at 14:24 finds it.","violations":[{"slug":"repeated-failure-class","loss_min":12,"loss_usd":1.31,"evidence":"tools/bench/stage_d1_l2a3.log:179"}],"sources":["tools/bench/diag_c108d_selind.log:49","tools/bench/cards/result_108-4.json:16","tools/bench/cards/task_108-6.json:10","tools/recipes/stage_d1_l2a3.py:65","tools/bench/stage_d1_l2a3.log:179","archive/peer/2026-09-27-c108f-l2a3-termclass.md:67","tools/bench/peer_c108f_l2a3_hyp.log:4"],"note":"Deferred cost to cycle 109 (re-dry/prerun/prior-art ~$1.21 + relaunch ~6.5 min) not counted. No device failed in-window; guard_peer SAME-ROW discharge by a pre-failure review is a design gap, not a device failure."}

## Sources

(extract from answer)

## What was done with it

**Cycle-108 judgement, 2026-09-27 14:5x.** `repeated-failure-class` (12 min, $1.31) is **ACCEPTED as a judgement fault, and it is mine.** `result_108-4.json:16` recorded that `allterms.read_terms` rows lack `term_class`, and `task_108-6.json` took that file as an input without ordering a grep of the recipes for the same key. The remedy is already the first act of cycle 109 (`docs/d1-loop12-17-split-plan.md` Pre-decided 222(g), `tools/bench/next.json`): (1) grep every `tools/recipes/stage_*.py` and `tools/stagekit.py` for a `term_class` index on `read_terms` rows, and fix every hit; (2) the recipe runs every gate in dry mode, or states in the dry output that it cannot, so the dry's `:65` skip can no longer hide a gate. Card rule from now on: when a result card names a reader defect, the next card that uses that reader greps for it before any launch. Slug count: first `repeated-failure-class` in this window, so no device is due. The "SAME-ROW discharge by a pre-failure review" gap in the note is recorded as a finding, not a device.
