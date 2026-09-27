# retrospective-cycle112

- **agent:** claude
- **role:** outcome
- **model:** claude-opus-5-5 (effort high; pinned by -Model/-Effort (role outcome))
- **kind:** fact
- **cost:** $2.7574  in 42 / out 45165 / cache-create 168452 / cache-read 2531348  (453s, 41 turn(s))
- **date:** 2026-09-28 00:47:09
- **outcome:** ANSWERED (454s)
- **verdict-card:** VERDICT-CARD retrospective-cycle112 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle112.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle112, role retrospective) ---
CLAIM: Cycle 112 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 112 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-27 22:12:57  ..  2026-09-28 00:39:31   (147 min)
    basis: start = archive/peer/2026-09-27-retrospective-cycle111.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-27 22:12 .. 2026-09-28 00:39 (147 min, an explicit cycle window): 67 build logs, 15 peer logs, 70 archived reviews, 1 Jev ledger(s) not counted as builds
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 67/67 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 18 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 68/70 annotated; blank: ['2026-09-27-c103-scratch-selftest.md', '2026-09-27-outcome-review-20260927.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 5403 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 3 log(s) with a run that printed none: ['selftest_guard_cycle_fixed_c112a.log', 'selftest_guard_cycle_rerun_c112a.log', 'selftest_stagekit_c112d.log']

  C1 builds run 71, failure markers 19, logs carrying a failure 18
  C2 peer reviews dispatched 15, archived 70
  C3 wall-clock inside bgrun, BUILDS ONLY 39 min 54 s
  C4 wall-clock inside bgrun, REVIEWS 20 min 49 s; cost $14.4568 from 10 log(s) that report one
  C4b cost lines seen 10 / parsed 10
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 60 min 43 s  (builds 65%, reviews 34%, judgement session 0%)

  C6 material-marked recipe/bench runs 39, judgement-session attempts refused 3  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 324 - STATUS.md, tools/bench/.stall_samples.txt, tools/bench/cards/plan_112-4_d4.md, tools/bench/diag_c112a_b2a_route.py, tools/bench/diag_c112a_ctltun.py, tools/bench/diag_c112a_fixgraph.py, tools/bench/diag_c112a_fixture.py, tools/bench/diag_c112a_peek.py, tools/bench/diag_c112a_regs.py, tools/bench/diag_c112a_u2seed.py, tools/bench/diag_c112b_addr.py, tools/bench/diag_c112b_final.py??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/856 ok; 515 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2531 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:388 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 640 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (68; read them directly, they are the primary record) ===
tools/bench/diag_c112a_b2a_route.log  (2026-09-27 22:33:22)
tools/bench/diag_c112a_b2a_route2.log  (2026-09-27 22:38:42)
tools/bench/diag_c112a_ctltun_dry.log  (2026-09-27 22:40:35)
tools/bench/diag_c112a_ctltun_dry2.log  (2026-09-27 22:41:19)
tools/bench/diag_c112a_ctltun_dry3.log  (2026-09-27 22:41:32)
tools/bench/diag_c112a_fixgraph.log  (2026-09-27 22:41:31)
tools/bench/diag_c112a_fixture.log  (2026-09-27 22:32:46)
tools/bench/diag_c112a_peek.log  (2026-09-27 22:23:00)
tools/bench/diag_c112a_regs.log  (2026-09-27 22:30:23)
tools/bench/diag_c112a_u2seed.log  (2026-09-27 22:47:06)
tools/bench/diag_c112b_addr.log  (2026-09-27 23:10:49)
tools/bench/diag_c112b_final.log  (2026-09-27 23:06:28)
tools/bench/diag_c112b_insp.log  (2026-09-27 22:56:10)
tools/bench/diag_c112b_opuid.log  (2026-09-27 23:08:04)
tools/bench/diag_c112b_route.log  (2026-09-27 23:04:43)
tools/bench/diag_c112c_errorlist.log  (2026-09-28 00:36:51)
tools/bench/diag_c112c_fixture.log  (2026-09-27 23:22:27)
tools/bench/diag_c112c_md5.log  (2026-09-27 23:49:31)
tools/bench/diag_c112c_plan.log  (2026-09-27 23:34:19)
tools/bench/diag_c112c_release.log  (2026-09-27 23:38:30)
tools/bench/diag_c112c_rows.log  (2026-09-27 23:30:42)
tools/bench/diag_c112c_scan.log  (2026-09-27 23:19:11)
tools/bench/diag_c112c_scan2.log  (2026-09-27 23:16:39)
tools/bench/diag_c112c_scan3.log  (2026-09-27 23:17:33)
tools/bench/diag_c112c_scan4.log  (2026-09-27 23:20:01)
tools/bench/diag_c112c_scan5.log  (2026-09-27 23:20:12)
tools/bench/diag_c112c_scan6.log  (2026-09-27 23:20:14)
tools/bench/diag_c112c_scan7.log  (2026-09-27 23:20:16)
tools/bench/diag_c112c_t1t2.log  (2026-09-27 23:39:53)
tools/bench/diag_c112c_t1t2_dry.log  (2026-09-27 23:35:08)
tools/bench/diag_c112c_t1t2_dry2.log  (2026-09-27 23:35:53)
tools/bench/diag_c112c_t1t2_prerun.log  (2026-09-27 23:35:22)
tools/bench/diag_c112c_t1t2_prerun2.log  (2026-09-27 23:35:59)
tools/bench/jev_gate.log  (2026-09-28 00:39:26)
tools/bench/motor_session_end_cycle111.log  (2026-09-27 22:14:35)
tools/bench/motor_session_start_cycle112.log  (2026-09-27 22:14:43)
tools/bench/selftest_d4_l2b2a.log  (2026-09-28 00:02:46)
tools/bench/selftest_d4_l2b2a_r2.log  (2026-09-28 00:06:40)
tools/bench/selftest_d4_l2b2a_r3.log  (2026-09-28 00:12:18)
tools/bench/selftest_guard_cycle_fixed_c112a.log  (2026-09-27 22:42:26)
tools/bench/selftest_guard_cycle_offline.log  (2026-09-27 22:26:34)
tools/bench/selftest_guard_cycle_rerun_c112a.log  (2026-09-27 22:42:28)
tools/bench/selftest_stagekit_c112d.log  (2026-09-28 00:03:01)
tools/bench/selftest_stagesim_c112a.log  (2026-09-27 22:28:20)
tools/bench/selftest_stagesim_c112b.log  (2026-09-27 22:28:32)
tools/bench/selftest_stagesim_c112c.log  (2026-09-27 22:28:55)
tools/bench/selftest_stagesim_c112d.log  (2026-09-27 22:29:17)
tools/bench/selftest_stagesim_c112e.log  (2026-09-27 22:36:46)
tools/bench/selftest_stagesim_c112f.log  (2026-09-27 23:04:04)
tools/bench/selftest_stagesim_k79_c112a.log  (2026-09-27 22:42:31)
tools/bench/selftest_stagesim_l2a1_80_c112a.log  (2026-09-27 22:42:38)
tools/bench/selftest_stagesim_unflip_81_c112a.log  (2026-09-27 22:44:35)
tools/bench/selftest_stagexec_c112a.log  (2026-09-27 22:36:44)
tools/bench/selftest_stagexec_c112b.log  (2026-09-27 22:37:21)
tools/bench/selftest_stagexec_c112c.log  (2026-09-27 22:38:25)
tools/bench/selftest_stagexec_c112f.log  (2026-09-27 23:04:13)
tools/bench/selftest_stagexec_c112g.log  (2026-09-27 23:04:41)
tools/bench/selftest_stagexec_gate_c112a.log  (2026-09-27 22:47:22)
tools/bench/selftest_stagexec_gate_c112b.log  (2026-09-27 23:06:48)
tools/bench/stage_d1_l2b2a.log  (2026-09-27 23:44:03)
tools/bench/stage_d1_l2b2a_checklaunch_c112d.log  (2026-09-28 00:13:58)
tools/bench/stage_d1_l2b2a_dry_c112c.log  (2026-09-27 23:37:27)
tools/bench/stage_d1_l2b2a_dry_c112d.log  (2026-09-28 00:07:03)
tools/bench/stage_d1_l2b2a_dry_c112d2.log  (2026-09-28 00:13:20)
tools/bench/stage_d1_l2b2a_prerun_c112c.log  (2026-09-27 23:37:46)
tools/bench/stage_d1_l2b2a_prerun_c112d.log  (2026-09-28 00:07:23)
tools/bench/stage_d1_l2b2a_prerun_c112d2.log  (2026-09-28 00:13:45)
tools/bench/stage_d1_l2b2a_r2.log  (2026-09-28 00:17:59)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (15) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_111.log  (2026-09-27 22:14:28)
tools/bench/cycle_112.log  (2026-09-27 22:17:13)
tools/bench/cycle_runner.log  (2026-09-27 22:17:13)
tools/bench/cycle_runner_main_20260927c.log  (2026-09-27 22:17:13)
tools/bench/outcome_review_cycle112.log  (2026-09-27 22:17:13)
tools/bench/peer_c112a_b2aroute.log  (2026-09-27 22:36:07)
tools/bench/peer_c112a_l2a1reg.log  (2026-09-27 22:44:00)
tools/bench/peer_c112a_md5.log  (2026-09-27 22:22:30)
tools/bench/peer_c112a_unflip81.log  (2026-09-27 22:46:14)
tools/bench/peer_c112c_b2a.log  (2026-09-27 23:48:46)
tools/bench/peer_c112c_fixture.log  (2026-09-27 23:29:43)
tools/bench/peer_c112c_rows.log  (2026-09-27 23:33:03)
tools/bench/peer_c112d-selftest.log  (2026-09-28 00:05:45)
tools/bench/peer_priorart_c112d_l2b2a.log  (2026-09-28 00:10:21)
tools/bench/retro.log  (2026-09-28 00:39:30)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle112","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

# Retrospective, cycle 112 (22:12:57 to 00:39:31)

**Outcome:** the cycle delivered. Launch 2 of `stage_d1_l2b2a.py` passed 23/0 and saved `D1_l2_b2a_20260928_001426.vi` (md5 `107a3ef1…`) (`tools/bench/stage_d1_l2b2a_r2.log:240-244`). Its Error List was read and matched the expected file (`result_112-4.json:18`), and STATUS moved the bed to it (`STATUS.md:61`). The steering card was followed (`tools/bench/next.json:22-25`).

The review claim ("run without a costly structural fault") does not hold. There is one structural fault, below.

**Timeline, from log and marker timestamps:**

| Card | Wall clock | What happened |
|---|---|---|
| Start | 22:17 | Session starts |
| 112-1 | 22:20–22:48 | Tooling |
| 112-2 (Opus max) | 22:56–23:11 | `material_marker.log:2528-2533` |
| 112-3 | 23:16–23:50 | Launch 1 FAIL at 23:44 |
| 112-4 (Opus max) | about 23:52–00:37 | Launch 2 PASS at 00:18 |
| Retrospective | 00:39 | |

The window is consistent with the evidence. The only item from the previous cycle inside it is `motor_session_end_cycle111.log` at 22:14, which costs nothing.

## The structural fault: launch 1's allow set ignored the cycle's own written prediction

- **Slug:** `inference-over-measurement`.
- **What was decided:** card 112-3 declared allow-either only for #8634/#29625 (`tools/bench/cards/task_112-3.json:87`). "Allow-either" meant a terminal diff on those two nodes was accepted whichever way it went.
- **What the split page already said:**
  - It listed IndexArray #8741/#30331 among the cascade pairs of the saved B1 file (`split_plan_111_l2b2.md:48-50`).
  - It predicted that LabVIEW would "likely restore the cascade terminals → E1/PB would diverge" (`:53-54`).
  - S1's terminal names for those nodes were on disk, offline, in `docs/wiki/subvi/D1_s1_copy.json:34485-34550`, as the later review showed (`c112c-b2a-e1.md:73`).
- **What happened:** launch 1 stopped at E1 on exactly #8741/#30331 (`stage_d1_l2b2a.log:122`). Launch 2 then accepted the same six terminals under rule D4 (`stage_d1_l2b2a_r2.log:119-125`). The real graph did not change between the two runs; only the rule did. The judgement session admits this itself: "The card's allow set was too narrow (judgement fault)" (`task_112-4.json:9`).
- **Loss in time:** about 17 min.
  - Launch 1 took 221 s and review c112c-b2a-e1 took 229 s, plus a judgement turn, a re-dispatch and two repeated dry/pre-run pairs.
  - The passing launch started at 00:14:26. Had D4 been coded in 112-3, the passing launch would have started about 23:57: 23:40 plus roughly 15 min of D4 coding, measured in 112-4 as 00:02:35→00:07:23, plus the count-cap round.
- **Loss in money:** $1.67 (`peer_c112c_b2a.log:4`). This is a floor. The material and judgement sessions log no cost (audit C4c, and `"usd": null` in every result card).
- **Second-order cost:** it used launch slot 2 of 2. The deliverable went out on its last permitted launch.
- **Counterfactual:** had card 112-3 (written about 23:12) scoped E1/PB to the split page's own eight cascade nodes, checked against S1's names, launch 1 at 23:40:23 would have passed. The cycle would have closed about 00:22 instead of 00:39.

## Findings

**1. Repeated failure.**
- **Main case:** the live T1/T2 wiring check took three cards.
  - 112-1 tried it through the offline dry run, which cannot emulate the fixture. It got the same "no graph JSON for input md5" error twice (`diag_c112a_ctltun_dry.log:21`, `dry2.log:21`), then a third failure (`dry3.log:24`).
  - 112-2 did not attempt it (`result_112-2.json:2`).
  - 112-3 spent 23:16–23:34 looking for a fixture: seven scans, `diag_c112c_fixture.log:39` FAIL, `diag_c112c_rows.log:10` FAIL, and reviews costing $2.20 + $1.04. It then used a byte copy of the bed, which passed (`diag_c112c_t1t2.log:99`).
  - 112-2 had already opened that same bed copy read-only at 23:08 (`diag_c112b_addr.log:33-41`).
  - The approach should have changed inside 112-2, once uid addressing existed (23:04). The card's rule D3, "build + save the scratch VI" (`task_112-2.json:82`), pushed toward a separate fixture instead.
  - This is my second-ranked fault: about 14–18 min and $3.24. I kept it below the main fault because its causes are mixed (the card's wording and the material session's search).
- **Second case:** the "saved-file cascade terminals the simulation does not model" class carried over from L2-B1 into B2a unchanged. The split page describes it for B1 (`split_plan_111_l2b2.md:47-50`).

**2. Missing tool.**
- stagesim has no model of polymorphic terminal growth, and E1 compares uid sets only, so renames are invisible to it (`c112c-b2a-e1.md:73`, citing `stagexec.py:465-481`). D4 is a gate against S1, not a prediction. B2b will meet the same cascade blind.
- Nothing checks a task card's input md5 values when the card is bound (`result_112-1.json:26`). The stale pin cost the opening H0 review ($1.02, `peer_c112a_md5.log:17`).
- Nothing derives a card's minutes from bgrun wall clock (see finding 6).

**3. Unmeasured steps.**
- The allow set (the fault above).
- The failed-prediction review ended with a 4-minute test that would tell its explanations apart (`c112c-b2a-e1.md:93-106`). Card 112-4 forbade it: "no ordering scratch" (`task_112-4.json:80`). So confounder (B), the `connect_from_wire` purge, is still not separated. B2b will use that same operation.
- Budget exhaustion was claimed, not measured. 112-2 said "~80 of 75 min", but its logs span about 15 min of commands, in a card of about 24 min.

**4. Rule compliance.**
- **Failure budget of 2 (`CLAUDE.md:328`), broken:**
  - 112-3 failed twice (fixture at 23:22, rows at 23:30) and went on to launch.
  - 112-4 had a budget of 1 (`task_112-4.json:76`) and failed twice: `selftest_d4_l2b2a.log:26` and the `selftest_stagekit_c112d` crash.
- **Cheapest separator (`CLAUDE.md:662-664`), satisfied only on paper:** the review was dispatched and annotated, but its separating test was never run.
- **Brief states the measurement, not the action (`CLAUDE.md:344-348`), evaded:** see finding 7.
- **A4, broken:** `archive/peer/2026-09-27-outcome-review-20260927.md:219-221` still says "(Claude fills in)". That review ran in this window (22:14) and produced the steering card that was followed. The other blank file, `c103-scratch-selftest`, comes from an earlier cycle; A4 counts by day, so it pulled that file in.
- **What the audit does not cover:**
  - Whether result-card claims (minutes, budget spent) agree with log wall clock.
  - Judgement taken inside material sessions.
  - C6 labels three refusals as "judgement-session attempts", but all three came from material sessions (`material_marker.log:2522`, `:2545`, `:2555`).
  - C7's list of 324 files is noise and cannot show scope.

**5. Ordering.** Mostly defensible. The owed H0 review and the tooling-first order came from STATUS NEXT (the PD225(h) item). The indefensible step is launching before checking the allow set against the split page. There was also a smaller detour: 112-1 re-ran two self-tests that have been failing since cycle 101 (`result_112-1.json:22`). Those runs armed `guard_peer` and cost two reviews ($0.66 + $0.85).

**6. Not reported.**
- Result cards overstate minutes about threefold:
  - 112-2 says 80, against about 24 min of wall clock.
  - 112-3 says 115, against about 38 min (`result_112-3.json:28`; marker lines 2534–2545).
  - STATUS repeats "over its minutes" (`STATUS.md:72`).
- 112-3's claim that its "90-min budget is spent" was the stated reason for skipping the 4-minute test (`c112c-b2a-e1.md:126`).
- STATUS calls self-test case J only a "stale stub" (`STATUS.md:69`). It omits that the stub made a real COM call (`result_112-4.json:24`).
- The c111e FIXED release text described allow-either code that no longer exists. Prior-art review c112d caught it (`priorart-c112d-l2b2a.md:514-518`), not the session.

**7. Judgement inside a material session: yes.**
- Prior-art c112d came back `contradicted`. The material session accepted finding A3.1, added a count cap that changes what D4 accepts, wrote its own FIXED release, and launched (`priorart-c112d-l2b2a.md:541-545`). It then asked "Keep it?" afterwards (`result_112-4.json:26`).
- The brief had pre-scripted this: "prior-art ANSWERED + annotated if the launch gate asks; launch gate ALLOW" (`task_112-4.json:35`).
- Likewise, 112-3's material session wrote five FIXED lines releasing c111e (`result_112-3.json:17`), as its card required (`task_112-3.json:38`). One of them was stale by the next card.
- Measured cost is zero: the cap only narrows the rule and did not change launch 2. That makes it a finding, not the top fault.

## Device effect

No device on file failed inside the window.

- **bgrun forces rc=1 on an inner FAIL:** fired correctly (`diag_c112a_b2a_route.log:25`, `diag_c112c_rows.log:11`, `selftest_stagesim_unflip_81_c112a.log:15`).
- **COST regex:** 10 of 10 lines parsed (C4b).
- **Stop record / launch gate:**
  - It let the dry and pre-run of the unreleased recipe through at 00:06–00:07 (`material_marker.log:2553-2554`). That is the 22:20 repair working.
  - It refused `--check-launch` before release (`:2555`). That argv is outside the offline-checker scope by design (`stop_record.py:134-136`), and the check itself answered ALLOW after release (`stage_d1_l2b2a_checklaunch_c112d.log:3`).
- **Pre-run gate:** refused a LabVIEW diagnostic launch that had no dry run (`material_marker.log:2522`). Correct.
- **Stagexec PARITY check:** 0 (`stage_d1_l2b2a_r2.log:39`).
- **Route report lists all rows:** all 7 rows reported (`result_112-1.json:19`).
- **`gates_due` on the cycle card:** present (`cycle_112.json:31-47`).
- **peer.ps1 card validation:** refused an over-long claim (`peer_c112a_md5.log:3`). Correct.
- **Remaining devices** (motor, VISA, SendMessage, reaper, graph-shape and others): not exercised in the window.
- **`md5sum` refusal:** `guard_bash`'s material gate refused a read-only `md5sum` (`material_marker.log:2545`; 22 s, worked around with `diag_c112c_md5.py`). That gate is not a listed device. It is only a finding: `md5sum` is missing from `MATERIAL_EXEMPT_RE` (`guard_bash.py:63-66`).

VIOLATION: inference-over-measurement | loss_min=17 | loss_usd=1.67 | evidence=tools/bench/cards/task_112-3.json:87
VERDICT {"schema":"verdict/1","id":"retrospective-cycle112","verdict":"refuted","alternative":"Launch 1 was a legitimate first measurement: the split page said 'likely', and the toward-S1 rule needed review c112c-b2a-e1 to be seen.","discriminating_test":"Before 23:40, diff the bed's terminal names on the 8 split-page s3 cascade nodes against D1_s1_copy.json offline (seconds). If #8741/#30331 differ toward S1, the allow set was knowable before launch 1.","violations":[{"slug":"inference-over-measurement","loss_min":17,"loss_usd":1.67,"evidence":"tools/bench/cards/task_112-3.json:87"}],"sources":["tools/bench/cards/split_plan_111_l2b2.md:48","tools/bench/cards/split_plan_111_l2b2.md:53","tools/bench/stage_d1_l2b2a.log:122","tools/bench/stage_d1_l2b2a_r2.log:119","tools/bench/cards/task_112-4.json:9","tools/bench/peer_c112c_b2a.log:4"],"note":"$1.67 is a floor (material/judgement cost unlogged). Second-ranked: T1/T2 live check spread over 3 cards, ~14-18 min, $3.24. Judgement-in-material (D4 count cap, priorart-c112d:541-545) at 0 measured cost. No device failed."}

## Sources

(extract from answer)

## What was done with it

Annotated by the cycle-112 judgement session, 2026-09-28 00:5x.

- **`inference-over-measurement` (17 min, $1.67 floor): ACCEPTED, and the fault is mine.**
  - Card 112-3's allow set named only `#8634`/`#29625`, although the split page listed `#8741`/`#30331` and predicted the divergence.
  - Remedy already in code: rule D4 (`tools/stagekit.py:1273,1298`) replaces hand-typed allow sets with a check against S1's graph. It is recorded in `docs/d1-loop12-17-split-plan.md` PD226(c).
  - The reviewer's discriminating test becomes a card rule for B2b (STATUS NEXT): before the launch, diff the bed's terminal names on B2b's cascade nodes against `docs/wiki/subvi/D1_s1_copy.json` offline, and set D4's scope from that diff.
  - No new device. This is the slug's first count in the D4 era; `violations.py` counts it.
- **Finding 1 (T1/T2 live check spread over 3 cards): ACCEPTED as a finding.** My rule D3 in card 112-2 ("build + save the scratch VI") pushed the session toward a separate fixture. A byte copy of the bed is an acceptable scratch fixture from now on.
- **Finding 3 (the separator between the review's explanations, confounder (B) `connect_from_wire` purge, never run): ACCEPTED as a carry.** Under D4 it is not blocking, because D4 is a gate, not a prediction. If B2b's run shows a terminal loss on a `connect_from_wire` op, the separator is run first.
- **Finding 4 (failure budgets exceeded in 112-3/112-4):** ACCEPTED as a finding. Card budgets now count fixture and self-test failures as failures.
- **Finding 6 (result-card minutes overstated about 3×): ACCEPTED.** STATUS's "over its minutes" for 112-2 stands corrected to about 24 min of wall clock. The claim of case J's real COM call is added to the PD226(f) carry.
- **Finding 7 (judgement inside a material session: the D4 count cap and FIXED lines written by material): ACCEPTED.**
  - The count cap is ratified (PD226(c)), because it only narrows D4.
  - Card rule from 113: a prior-art `contradicted` verdict returns BLOCKED to judgement unless every fix only narrows an existing gate.
- **Device effect: none failed.** The `md5sum` refusal (`MATERIAL_EXEMPT_RE`, `guard_bash.py:63-66`) is a carry for a tooling card.
- **A4 (outcome-review-20260927 without an annotation):** carry. That review was already annotated and ACCEPTED in the cycle-107 STATUS entry. Its blank section is filled in the next doc pass.
