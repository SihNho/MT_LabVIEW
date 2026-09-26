# retrospective-cycle107

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $1.6830  in 40 / out 26603 / cache-create 100552 / cache-read 1731830  (265s, 31 turn(s))
- **date:** 2026-09-27 08:24:35
- **outcome:** ANSWERED (267s)
- **verdict-card:** VERDICT-CARD retrospective-cycle107 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle107.json
- **why asked:** end-of-cycle retrospective, cycle 107 (CLAUDE.md §3).
- **verdict:** ACCEPTED (cycle 107 judgement). `device-failed` 36 min: the wrong-ordering gates_due device was never built, and I did not run `outcome_review.py --due` before dispatching. Finding 6 (the impossible 07:50 header) is also accepted and corrected.

## Question

--- REVIEW CARD (review/1, id retrospective-cycle107, role retrospective) ---
CLAIM: Cycle 107 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 107 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-27 07:45:00  ..  2026-09-27 08:20:05   (35 min)
    basis: start = archive/peer/2026-09-27-retrospective-cycle106.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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
  - `device-failed` (decided 2026-09-27 07:50): `stage_prerun --dry|--prerun <recipe>` through (they are offline checks that precede a release) and still refuses every launch; negatives `material_marker.log:2335`/`:2338` must pass, a real launch argv must still be refused; acceptance = a RECORDED top-level dry of the display recipe (sha `d62f876d`). Plus a card rule (no hook): a gate refusal is returned as BLOCKED, never re-run through a self-t??

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

== cycle audit, 2026-09-27 07:45 .. 2026-09-27 08:20 (35 min, an explicit cycle window): 11 build logs, 10 peer logs, 32 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 11/11 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 3 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 31/32 annotated; blank: ['2026-09-27-c103-scratch-selftest.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 4138 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  PASS  A8 recipe/bench runs ended with a RESULT line (C6): every scoped run in the window printed one (or predates the mark)

  C1 builds run 12, failure markers 3, logs carrying a failure 3
  C2 peer reviews dispatched 10, archived 32
  C3 wall-clock inside bgrun, BUILDS ONLY 13 min 44 s
  C4 wall-clock inside bgrun, REVIEWS 7 min 57 s; cost $7.1859 from 5 log(s) that report one
  C4b cost lines seen 5 / parsed 5
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 21 min 41 s  (builds 63%, reviews 36%, judgement session 0%)

  C6 material-marked recipe/bench runs 19, judgement-session attempts refused 4  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 12 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/cards/split_plan_107_l2a2.md, tools/bench/diag_c107a_regress.py, tools/bench/diag_c107b_bedgraph.py, tools/bench/diag_c107c_plan.md, tools/bench/heartbeat_latest.md, tools/bench/jev_ladder_cache.jsonl, tools/bench/jev_usage.jsonl, tools/bench/next_snapshot.md5, tools/bench/peer_c107a_l4_task.md, tools/bench/selftest_stoprecord_offline_c107.py

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/818 ok; 477 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2439 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:328 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 631 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (12; read them directly, they are the primary record) ===
tools/bench/diag_c107a_regress.log  (2026-09-27 08:04:31)
tools/bench/diag_c107b_bedgraph.log  (2026-09-27 08:11:52)
tools/bench/diag_c107b_dry.log  (2026-09-27 08:15:16)
tools/bench/diag_c107b_dry2.log  (2026-09-27 08:17:42)
tools/bench/diag_c107b_prerun.log  (2026-09-27 08:15:34)
tools/bench/diag_c107b_prerun2.log  (2026-09-27 08:18:00)
tools/bench/disp_107_abba.log  (2026-09-27 07:50:56)
tools/bench/jev_gate.log  (2026-09-27 08:20:04)
tools/bench/motor_session_end_cycle106.log  (2026-09-27 07:46:11)
tools/bench/motor_session_start_cycle107.log  (2026-09-27 07:46:18)
tools/bench/plan_l2a2_sim.log  (2026-09-27 08:12:15)
tools/bench/selftest_stoprecord_offline_c107.log  (2026-09-27 07:58:01)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (10) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_106.log  (2026-09-27 07:46:04)
tools/bench/cycle_107.log  (2026-09-27 07:46:18)
tools/bench/cycle_runner.log  (2026-09-27 07:46:18)
tools/bench/cycle_runner_main_20260927a.log  (2026-09-27 07:46:18)
tools/bench/diag_c107c_priorart.log  (2026-09-27 08:09:27)
tools/bench/outcome_review_c107.log  (2026-09-27 08:12:31)
tools/bench/peer_c107a_l4.log  (2026-09-27 07:57:24)
tools/bench/peer_priorart_c107b_l2a2.log  (2026-09-27 08:14:43)
tools/bench/peer_priorart_c107b_l2a2_r2.log  (2026-09-27 08:17:18)
tools/bench/retro.log  (2026-09-27 08:20:05)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle107","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: cycle 107 had one costly structural fault.** A device decided on 2026-09-26 was never built, and its manual stand-in was dropped. So the outcome review, overdue since before the cycle began, ran only at 08:10. By then three cards were already out, and two of them were stopped by that review's gate and by another "due" gate. Everything else in the cycle was minor, and most devices worked.

**Evidence window.** The attached evidence matches the 07:45–08:20 window. Two items in it belong to the close of cycle 106 and are not charged here: `tools/bench/cycle_106.log:147` (it ended at 07:46:03) and `motor_session_end_cycle106.log`.

## The structural fault

**Slug: `device-failed`.** The device that failed is the one from the 2026-09-26 14:10 `wrong-ordering` decision (`docs/violation-decisions.md:1407-1410`). It was meant to make `cycle_runner.py` run `violations.py --due` and `outcome_review.py --due` before the cycle and record the result in the cycle card. It was never built:
- `tools/cycle_runner.py` contains no `gates_due`, and `tools/bench/cards/cycle_107.json` has no such field.
- Until it existed, STATUS NEXT was supposed to say "run both `--due` checks before the first card". Cycle 107's first-act text (`STATUS.md:65`) does not say it.

**What happened, in order:**
- The outcome review was already due when the cycle started. `outcome_review.py:100-111` counts retrospectives newer than the last outcome review, and there were 7 (cycles 100–106), so it had been due since retrospective 104.
- **107-2** was dispatched early: the L2-A2 plan, recipe, one LabVIEW read of the bed, and two prior-art reviews. It took 36 min, and its two prior-art reviews cost $2.64 (`result_107-2.json:25`; `peer_priorart_c107b_l2a2.log:6` $1.2301, `_r2.log:6` $1.4080).
- **107-1 B2**, the recorded dry run, was refused at 08:04:40 by the `violations --due` gate (`material_marker.log:2357`, `result_107-1.json:2-3`).
- The judgement session then fixed the decision-file headers. It checked only `violations --due` before sending **107-3** (`task_107-3.json:6`).
- **107-3 D1** was refused at 08:07:15 by the outcome-review gate (`material_marker.log:2360`, `result_107-3.json:2-3`).
- The outcome review then ran from 08:10:40 to 08:12:31 and cost $2.1203 (`outcome_review_c107.log:1,7,139`). Its first finding was that L2-A2 is "the wrong fallback" and should be abandoned (`archive/peer/2026-09-27-outcome-review-20260927.md:155,197`). The judgement session accepted that (`:226`), after 107-2 had already done the work.
- The display recipe's recorded dry run was never produced. That dry run is the acceptance test for the 07:50 stop-record repair (`violation-decisions.md:1521-1522`). It is still owed (`STATUS.md:59`).

**Loss.**
- 36 material-minutes and $2.64 logged, on work the accepted outcome review said to drop. The L2-A2 files are kept, so this is at risk rather than certainly lost: user decision D-04 could revive them.
- Plus 107-3's blocked D1 attempt, within its 12 min (`result_107-3.json:22`). Its $1.3753 prior-art review was owed anyway.
- The dollar figure is a lower bound: the material sessions' own cost is not logged.

**Counterfactual.** At about 07:47, both `--due` checks (seconds each) would have shown two gates due. Fix the headers, run the 111-second outcome review, and its verdict lands by about 07:50, before any dispatch:
- 107-2 is not sent as L2-A2.
- 107-1's B2 dry at 08:04 passes and is recorded; the same command took 6 s when it ran (`diag_c107b_dry2.log:47`).
- 107-3 shrinks to its 92-second prior-art review.

The cycle ends around 08:10 with the 07:50 repair accepted, instead of 08:20 with the acceptance still owed.

## Findings

1. **Repeated failure.**
   - The same class hit twice: a card stopped by a `guard_cycle` "due" gate (`material_marker.log:2357`, then `:2360`).
   - The approach should have changed at the second dispatch (107-3). `guard_cycle.py:551-582` stops at the first gate that blocks, so passing `violations --due` said nothing about the outcome gate behind it.
   - Inside 107-2, the L2-A2 dry run was refused twice before it ran: tried at 08:13:14 and 08:16:02, started at 08:15:10 and 08:17:36 (`material_marker.log:2362,2365`; `diag_c107b_dry.log:1`, `dry2.log:1`). Each time a prior-art review started seconds later, which points to the premature-build gate working. It cost seconds.
2. **Missing tool.** The pre-dispatch `gates_due` reader, in effect a dry run of every `guard_cycle` gate at once. It would have answered both refusals above. `guard_cycle` reports only the first gate that blocks, which is how the outcome gate stayed hidden behind the stop-record and violations gates for cycles 105–106.
3. **Unmeasured steps.** 107-3 was sent on the belief that `violations --due` was the only blocker (`task_107-3.json:6`). `outcome_review.py --due` was one command away. That is the same fault as above.
4. **Rule compliance.**
   - The outcome layer ("every 5 cycles", `CLAUDE.md:580`) ran two cycles late. That was satisfied only formally: the gate enforces it only when a build command happens to reach it.
   - STATUS.md is 328 lines against the one-screen limit (audit L3; CLAUDE.md §4).
   - The audit's A4 blank belongs to an earlier cycle.
   - What the audit does not cover:
     - It cannot see gates that were due but untriggered.
     - C6 counts hook self-test fixtures as judgement-session refusals (`material_marker.log:2354-2356` came from the regression run).
     - C7 flags outputs that the cards authorised (e.g. `selftest_stoprecord_offline_c107.py`), because it does not read card write-globs.
5. **Ordering.** Not defensible. The outcome review should have come first, since it was due and it overturned 107-2. The rest of the order (ABBA guard first, offline work before any LabVIEW read) was sound.
6. **What was not reported.**
   - `STATUS.md:63` says 107-3's dry run "was refused because the outcome review was due". It does not say that the gate was clear from 08:12:31, that the 6-second dry run was never re-issued, and that `next.json` leaves it out of `pass`.
   - The rewritten header "07:50" on the cycle-106 decision (`violation-decisions.md:1513`) states a time after the cycle-106 session had exited (`cycle_106.log:147`, 07:46:03). It is labelled a lower bound, but it is factually impossible.
7. **Judgement inside a material session.** The 107-1 material session wrote "ACCEPTED (card 107-1, material session)" on the c107a-l4 review (`archive/peer/2026-09-27-c107a-l4-selftest_stoprecord_offline_c107.md:113`), accepting a finding and changing the self-test's negative case. It was narrow: the decision that costs something (the newline false positive) went back to judgement (`result_107-1.json:27`). A finding, not a violation.

## Device effect

The `wrong-ordering` device of 2026-09-26 14:10 **failed**: never built, its manual form dropped, and the fault recurred twice (above).

The devices that were exercised in this window worked:
- **Leg guard (07:40):** refused leg 1 in 13 s with LabVIEW never started (`disp_107_abba.log:5-8,27`).
- **Stop record `--dry` pass (07:50):** worked live (`result_107-1.json:19`), and gate refusals came back BLOCKED, not bypassed (`result_107-3.json:12`). Its acceptance is unmet because of the failure above, not its own.
- **bgrun rc and cost parsing:** the rc=1 logs match their inner failures, and cost lines parsed 5/5 (audit C4b).
- **Prior-art review gate:** ran 3 times with dispositions written.
- **Verb-precondition check X9:** PASS (`diag_c107b_prerun2.log:52-57`).
- **Stop-record read-only refusals:** none. The two REFUSED lines at `material_marker.log:2345,2361` are the material gate, not the stop record.

The remaining devices on file were not exercised in this window.

VIOLATION: device-failed | loss_min=36 | loss_usd=2.64 | evidence=tools/bench/cards/result_107-3.json:3
VERDICT {"schema":"verdict/1","id":"retrospective-cycle107","verdict":"refuted","alternative":"The late outcome review was unavoidable: guard_cycle checks it only when a build is attempted, and STATUS NEXT never told the session to check it, so the session could not have known it was due.","discriminating_test":"Run py tools/outcome_review.py --due against the file state at 07:46; if it prints due (7 retrospectives, cycles 100-106, >= 5), the 107-2 dispatch went ahead with a known, cheap check skipped.","violations":[{"slug":"device-failed","loss_min":36,"loss_usd":2.64,"evidence":"tools/bench/cards/result_107-3.json:3"}],"sources":["docs/violation-decisions.md:1407","tools/bench/cards/result_107-3.json:3","tools/bench/cards/result_107-1.json:3","tools/hooks/material_marker.log:2360","archive/peer/2026-09-27-outcome-review-20260927.md:155","tools/bench/outcome_review_c107.log:1","STATUS.md:65"],"note":"Device = the 2026-09-26 14:10 wrong-ordering gates_due device: never built in cycle_runner.py and its manual form was missing from STATUS NEXT. loss_usd = the two L2-A2 prior-art reviews only, a lower bound; the L2-A2 files are kept pending D-04."}

## Sources

(extract from answer)

## What was done with it

- `device-failed` ACCEPTED → device decided in `docs/violation-decisions.md` (device-failed 08:30): `cycle_runner.py` runs every guard_cycle "due" check at cycle start and puts the list (`gates_due`) in the cycle card; a due outcome review runs before the judgement session. It is the FIRST card after the runner restarts, and it is in STATUS NEXT.
- Finding 6: the cycle-106 device-failed header was rewritten 07:50 → 07:46 (the session's exit minute, `docs/violation-decisions.md:1513`); the '03:30'/'07:40' lower bounds stay, since each is inside its session.
- Finding 6 (unreported): the display recipe's recorded top-level dry is still owed; after 08:12:31 the gate was clear, and I did not re-issue it. It is now named in STATUS NEXT as owed before any display-recipe launch.
- Finding 4 (STATUS 328 lines): not relocated this cycle; it is a carry for the next doc pass (rule 4).
- Finding 7 (107-1's material session accepted a narrow review finding): noted, no action; the costly choice came back as an open.
- The alternative in the VERDICT ("the session could not have known it was due") is refuted: `outcome_review.py --due` is one command, and I did not run it.
