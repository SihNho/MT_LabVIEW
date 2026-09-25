# retrospective-cycle91

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.9097  in 226 / out 26457 / cache-create 168656 / cache-read 845961  (360s, 39 turn(s))
- **date:** 2026-09-26 08:01:36
- **outcome:** ANSWERED (362s)
- **verdict-card:** VERDICT-CARD retrospective-cycle91 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle91.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle91, role retrospective) ---
CLAIM: Cycle 91 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 91 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-26 05:30:11  ..  2026-09-26 07:55:32   (145 min)
    basis: start = archive/peer/2026-09-26-retrospective-cycle90.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-26 05:30 .. 2026-09-26 07:55 (145 min, an explicit cycle window): 15 build logs, 7 peer logs, 21 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 14/15 ok; NO BGRUN line in ['jev_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 4 logs recorded a failure; unreviewed: ['jev_gate.log']
  PASS  A4 every archived review says what was done with it: 21/21 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 3547 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 5 log(s) with a run that printed none: ['diag_c91_step4_click1.log', 'diag_c91_step4_click1b.log', 'diag_c91_step4_click1c.log', 'diag_c91_step4_md5.log', 'diag_c91_step4_summary.log']

  C1 builds run 14, failure markers 4, logs carrying a failure 4
  C2 peer reviews dispatched 7, archived 21
  C3 wall-clock inside bgrun, BUILDS ONLY 103 min 19 s
  C4 wall-clock inside bgrun, REVIEWS 9 min 5 s; cost $4.5143 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 112 min 24 s  (builds 91%, reviews 8%, judgement session 0%)

  C6 material-marked recipe/bench runs 15, judgement-session attempts refused 1  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/d1-loop12-17-split-plan.md [tools/bench/next.json plan.path]: 268 - STATUS.md, tools/bench/diag_c91_step4.py, tools/bench/diag_c91_step4_click1.py, tools/bench/diag_c91_step4_leg.py, tools/bench/diag_c91_step4_md5.py, tools/bench/diag_c91_step4_stats.py, tools/bench/diag_c91_step4_summary.py, tools/bench/diag_c91_t0_step3c.py, tools/bench/diag_c91_t0_tunnels_offline.py, tools/bench/heartbeat_latest.md, tools/bench/jev_ladder_cache.jsonl, tools/bench/m8_out/replay_s1_20260926_060634/cal001??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 341/743 ok; 402 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-priorart-ownerchain.md', 'archive/peer/2026-09-16-delete-object-noop-failed-prediction.md', 'archive/peer/2026-09-16-delete-silent-noop2.md', 'archive/peer/2026-09-16-flatseq-frame-unreachable.md', 'archive/peer/2026-09-16-load-vs-editmode-23c-r2.md']
  PASS  L2 every cited project path exists: 2230 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:160 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 609 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A3 every failing log is followed by an archived review


=== BUILD LOGS INSIDE THE WINDOW (15; read them directly, they are the primary record) ===
tools/bench/diag_c91_step4.log  (2026-09-26 07:13:40)
tools/bench/diag_c91_step4_b.log  (2026-09-26 07:49:17)
tools/bench/diag_c91_step4_click1.log  (2026-09-26 06:25:37)
tools/bench/diag_c91_step4_click1b.log  (2026-09-26 06:59:13)
tools/bench/diag_c91_step4_click1c.log  (2026-09-26 07:18:14)
tools/bench/diag_c91_step4_dry.log  (2026-09-26 06:26:20)
tools/bench/diag_c91_step4_md5.log  (2026-09-26 07:51:07)
tools/bench/diag_c91_step4_summary.log  (2026-09-26 07:49:47)
tools/bench/diag_c91_t0_smoke.log  (2026-09-26 06:13:09)
tools/bench/diag_c91_t0_step3c.log  (2026-09-26 05:54:32)
tools/bench/diag_c91_t0_step3c_r2.log  (2026-09-26 06:01:39)
tools/bench/diag_c91_t0_tunnels_offline.log  (2026-09-26 05:39:23)
tools/bench/jev_gate.log  (2026-09-26 07:55:28)
tools/bench/motor_session_end_cycle90.log  (2026-09-26 05:35:03)
tools/bench/motor_session_start_cycle91.log  (2026-09-26 05:35:09)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (8) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_90.log  (2026-09-26 05:34:59)
tools/bench/cycle_91.log  (2026-09-26 05:35:09)
tools/bench/cycle_runner.log  (2026-09-26 05:35:09)
tools/bench/cycle_runner_main_20260926a.log  (2026-09-26 05:35:09)
tools/bench/peer_c91_smoke_k1.log  (2026-09-26 06:24:22)
tools/bench/peer_c91_step4_t12.log  (2026-09-26 07:17:19)
tools/bench/peer_c91_t0step3c_quit.log  (2026-09-26 06:05:03)
tools/bench/retro.log  (2026-09-26 07:55:32)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle91","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict first.** Cycle 91 delivered what it set out to deliver: the 12-site stamped copy (step 3) and a step-4 table from 7 legs, both PASS cards. One structural fault is identifiable and it is modest: the step-4 sequencer's registered-pick reader was launched into a 47-minute LabVIEW batch untested against a real trace file that had been on disk, already parsed, for 13 minutes. That bought a needless 12-minute leg, a second launch and a $1.27 review. Nothing else in the window rises to a structural fault; the rest are findings, and one of them (the frame-bound 8-pick baseline) matters more for the NEXT cycle than the fault does.

## The fault

**Slug: inference-over-measurement.** `diag_c91_step4.py` compared the trace-derived bead count with `abs(n - N) < 1e-9`. The smoke run had written `tra001-000` at 06:13 and `m8_replay_s1_r30.json:36-50,107` already carried its header rows and byte size, so the reader could have been run against a file with a known n = 2 in seconds. Instead the only pre-launch check was `diag_c91_step4_dry.log:3`, where the DRY stub hard-codes `picks_registered_tra: 15` and `registered_ok: true`, so the dry run passed vacuously (`diag_c91_step4.py:122`, `if not DRY else True`). Launch 1 then judged a correctly registered 15 a mismatch on leg 2 (`diag_c91_step4.log:81`, "15.000039 != target 15 -> rerun once"), ran a needless rerun from 35.5 to 47.1 min (`:82`, `:110`) that itself lost a click and was discarded, skipped both 8-pick legs (`:110-111`), ended rc=1 after 2831 s (`:150`), and owed a review (`jev_gate.log:1330`, new-problem p=0.784; `peer_c91_step4_t12.log:3`, $1.2698, 162 s). Card 91-3 closed at 95 min against a 75-min budget (`result_91-3.json:29`).

**Loss.** 12 min of leg + 3 min of review + the patch and relaunch: about 15 min; $1.2698 is the only log-carried figure attributable to it.

**Counterfactual.** Had the reader been run on `m8_out/replay_s1_20260926_060634/tra001-000` at 06:25 (the material session was already running offline helpers under bgrun at 06:25:34, `material_marker.log:1886`), the 8-byte prefix would have shown up as 2.00004 ≠ 2, the exact rule would have been in launch 1, leg 2 a1 would have passed T12, and launch 1 would have started the 8-pick legs at 35.5 min instead of skipping them. Card 91-3 would have returned around 07:36 instead of 07:51, and no T12 review would have been owed. The review was useful (it corrected the material session's too-loose 0.05 tolerance, `2026-09-26-c91-step4-t12.md:83-88`), but it was paid for by a fault that a one-second measurement would have removed.

## Findings

**1. Repeated failure.** The lost-first-click class recurred four times in the window: the smoke (`diag_c91_t0_smoke.log:180`), leg1 ctl a1 (`diag_c91_step4.log:18`, capture 22872738), leg2 min rerun (`:100`, capture 23463992), leg1 min@8 a1 (`diag_c91_step4_b.log:20`, capture 62720394). Every time a non-zero foreign `hwndCapture` sat on click 1 and on no other pick click. The smoke reviewer at 06:24 asked for the capturing window's class and name to be logged before every click (`c91-smoke-k1.md:107`); the step-4 reviewer at 07:17 recorded that it "was never done" (`c91-step4-t12.md:108`) and asked again. Launch 2 at 07:18 was the attempt at which a `GetClassName` read should have been added. It is a read, not a GUI act, and the material session declined it twice as "a HARNESS change ... for judgement" (`c91-smoke-k1.md:138-140`, `c91-step4-t12.md:162-163`). Two of the three reruns (about 22 min of LabVIEW) were forced by this class, and the cycle ends still not knowing which window held the capture, the single fact both reviews asked for. Judgement ratified the deferral in `d1-loop12-17-split-plan.md:1159`.

**2. Missing tool.** Three absences cost something. (a) A trace-file reader verified against a real file, which now exists as the exact rule in `diag_c91_step4_leg.py:161-167` but was built after the failure rather than before the launch. (b) The capture-window class reader above, not built. (c) A stamp on the grab's completion: site 1 was dropped in `d1-loop12-17-split-plan.md:1106-1107` because loop #637 has no grab node, so the frame wait inside each iteration is invisible, and finding 3 follows from that. The bgrun reaper (`task_91-2.json`) was written and not dispatched (`plan:1162-1163`); nothing in this window needed it (audit A2 passed).

**3. Unmeasured steps.** Beyond the float compare, the headline inference of the cycle rests on a confounded baseline. At 8 picks loop #637's period is 11,139 to 11,150 µs (`diag_c91_step4_summary.log:37,50`) against a camera period of 11,111 µs, so the loop is frame-bound: every site's delta-from-i at 8 picks measures the wait for the frame, not compute. The computed "slopes" show it: sites 2, 3, 6 and 8 come out at −181, −92, −182 and −172 µs/bead (`summary.log:62`), which is physically meaningless for a kernel. STATUS:67-69 and `plan:1143-1146` nevertheless state "the kernel does not grow" and "the only site that grows is site 4". What the data supports is narrower: at 15 picks, site 4 fires 12.6 ms after i and the kernel 8.4 ms after i (`summary.log:12-14`). The per-bead cost of the kernel cannot be read from a 15-vs-8 difference when the 8-pick cell is pinned by the camera. The plan records site 4 only as a candidate (`:1147`), which is correct, but the negative slopes are not mentioned anywhere and they are the tell. Also unmeasured, correctly named as NEXT: the CLFN thread setting was inferred from `reentrant=True` in gscript, never read back (`c91-smoke-k1.md:71`).

**4. Rule compliance.** Satisfied: originals untouched (audit A5, `result_91-1.json:27` G91), every run under bgrun with an END line, every review annotated (A4 21/21), two material dispatches under the cap (`guard_card.log:252-253`), one bare launch refused and rerun under bgrun (`material_marker.log:1885-1886`), the retrospective last, NEXT written before it. Formally only: card 91-3's `budget.minutes` 75 was exceeded by 20 min with no mechanical stop and no escalation; the intra-cycle escalation rule triggers on "exceeds budget.minutes" but nothing enforces it while a card is running. Evaded in spirit: the failure budget on card 91-1 (run 1 rc=0 but two card sites skipped, run 2 rc=1 on the quit tail) was spent without a FAIL status, since the card returned PASS 207/2. The audit does not cover: judgement taken inside a material session, confounded measurements, per-card minute budgets, whether a device-failed repair card was dispatched, and its A4 is day-granular. Its A1/A3 lines fail on `jev_gate.log` every cycle (retrospective-cycle90 line 138 shows the same), so the machine "AUDIT VIOLATIONS" line is saturated the same way the slug tally was; STATUS OPEN 47 already names this as a judgement item, not a logclass entry.

**5. Ordering.** The step-3 order (offline tunnel read, per-class probe, incremental ExecState reads, save, smoke) was right and it is why step 3 landed after two failed cycles. Two later steps should have come earlier. First, an unstamped 8-pick control leg belonged inside card 91-3: the smoke reviewer flagged at 06:24 that the stamped run lost roughly three times the unstamped rate and wrote "step 4 should measure it rather than assume it away" (`c91-smoke-k1.md:114`), two minutes before launch 1; launch 2 ended at 31 of its 52 min (`diag_c91_step4_b.log:120`), so one 10-min control leg fitted. Without it the whole 78-min table is provisional and the next cycle's first act is that leg (`next.json:1`). This deferred the answer by a cycle rather than costing minutes, so it is a finding. Second, the capture-class read (finding 1) before launch 2.

**6. What was not reported.** (a) The negative slopes in finding 3; the result card gives the raw medians (`result_91-3.json:22`) but STATUS turns them into "the kernel does not grow". (b) The 15_ctl cell is the rerun leg and 15_min is the first attempt (`summary.log:10,23`), so the ABBA order the card asked for (`task_91-3.json:18`) is broken across the two 15-pick cells; not mentioned. (c) The quit-branch review said the applied try/except "makes the rule-1 hazard silent" and asked that the blocking dialog be captured before taskkill (`c91-t0step3c-quit.md:78`); the material session left it "for judgement" (`:100-101`), `result_91-1.json:32` carries it as open, and neither `next.json` nor plan 198 disposes it. (d) Reported honestly, to its credit: the 95-min overrun, the needless rerun, the frame-accounting excess (+480/+770), and the 9× loss at 8 picks (`result_91-3.json:20,26,29`).

**7. Judgement inside a material session.** Three instances, none large. (a) Card 91-3's material session accepted review §1, withdrew its own mechanism, rejected its own tolerance fix, adopted the exact rule and relaunched (`c91-step4-t12.md:156-160`) with no judgement turn; judgement ratified it afterwards at `plan:1160-1161`. Under the Jev ladder rule the log was `new-problem`, so the path was review then judgement, not review then relaunch. (b) Card 91-1's material session patched its reader (skip by class, `--reuse-probe`) after run 1 and ran run 2 (`result_91-1.json:24`), and after the quit review chose which halves to apply (`c91-t0step3c-quit.md:93-102`). (c) Both cards carry pre-scripted actions: "rerun once", "no third run", "a class left at ExecState 0 is skipped", "first ExecState 0 => site deleted" (`task_91-3.json:58`, `task_91-1.json:22-23`). These are the kind the question names; they also are what let the cycle run 7 legs without seven judgement turns, and the material sessions stopped at the real design lines (the neutral-click release, the stagekit close change). I record it and do not rank it.

## Device effect

Devices with a fault to stop in this window, and what the logs show:

- **Confirm-bait refusal / adversarial set (rule-evaded):** all three review tasks carry the mandatory four-part refutation (`c91-smoke-k1.md:45-51` and the other two). Held.
- **Undisposed-review refusal (repeated-failure-class):** 21/21 annotated (audit A4). Held.
- **C3/C4 cost lines and the COST regex (unreported-fact, device-failed 09-16):** C4b 3 seen / 3 parsed, $4.5143 = 0.9536 + 2.2909 + 1.2698 from the three peer logs. Held.
- **bgrun FAIL scan forcing rc=1 (device-failed 09-17):** `diag_c91_t0_smoke.log:767` rc=1 and `diag_c91_step4.log:150` rc=1 on gate FAILs. Held.
- **bgrun-only launches counted at child start; judgement attempts refused (device-failed 09-25 07:05):** `material_marker.log:1885` REFUSED a bare `py tools/bench/diag_c91_step4_click1.py`, rerun under bgrun 9 s later. Held.
- **Jev exemption by command, guard_peer path (device-failed 09-24 03:53):** no false block on a Jev run; `jev_gate.log`'s A1/A3 failure is the audit's classification, discussed in finding 4, not this device.
- **guard_session refusing SendMessage to material (repeated-failure-class 09-24 05:54):** both dispatches were fresh agents (`guard_card.log:252-253`); no SendMessage in the window.
- **C7 scope list reading the plan from next.json (device-failed 09-25 14:28):** it read `d1-loop12-17-split-plan.md` from `next.json plan.path`. Held; 268 files listed, almost all leg data, so the counter is noise at this granularity.
- **Jev ladder hook budget:** three times the first call hit its 10-s budget and blocked fail-closed with "retry in a minute" (`jev_gate.log:1320,1324,1326`). Slow, not wrong; each cost the material session a minute or two.
- **Stop record, release table, sink gates, motor FAIL exit, parity, unroutable rows, OpLoopEndRef, guard_cycle premature-build:** no recipe or stage launch in this window, so nothing to fire on. Motor session start/end verified (`motor_session_start_cycle91.log:24`, `motor_session_end_cycle90.log:17`).
- **Retrospective-cycle90's device-failed (bgrun END under a tree kill):** the repair is `task_91-2.json`, written and not dispatched; the fault did not recur (audit A2 all accounted). Not a failure in this window, but a threshold-1 device is now one cycle deferred, and STATUS:154 shows the same item was already a carry before cycle 90.

No device failed inside this window.

VIOLATION: inference-over-measurement | loss_min=15 | loss_usd=1.2698 | evidence=tools/bench/diag_c91_step4.log:81

VERDICT {"schema":"verdict/1","id":"retrospective-cycle91","verdict":"refuted","alternative":"The cycle had no structural fault: the float-compare miss is a 15-min script bug inside a card that still delivered, and the provisional step-4 table is the honest outcome of a measurement that could only be judged after the 8-pick legs ran.","discriminating_test":"Run diag_c91_step4_leg.py's launch-1 reader (abs(n-N)<1e-9) on m8_out/replay_s1_20260926_060634/tra001-000 (n=2 known at 06:13); if it reports a mismatch, the 12-min leg2 rerun and the T12 review were avoidable before 06:26:29.","violations":[{"slug":"inference-over-measurement","loss_min":15,"loss_usd":1.2698,"evidence":"tools/bench/diag_c91_step4.log:81"}],"sources":["tools/bench/diag_c91_step4.log:81","tools/bench/diag_c91_step4_dry.log:3","tools/bench/m8_replay_s1_r30.json:36","tools/bench/peer_c91_step4_t12.log:3","tools/bench/diag_c91_step4_summary.log:62","archive/peer/2026-09-26-c91-smoke-k1.md:107","archive/peer/2026-09-26-c91-step4-t12.md:108","tools/bench/cards/result_91-3.json:29","tools/hooks/material_marker.log:1885"],"note":"Next cycle: the 8-pick cell is frame-bound (period 11.14 ms vs camera 11.11 ms), so 'the kernel does not grow' is not shown by the table; negative slopes at summary.log:62 are the tell. Run the unstamped control and read the CLFN thread setting before building on site 4."}

## Sources

(extract from answer)

## What was done with it

- ACCEPTED fault `inference-over-measurement` (float-compare reader launched untested against a known tra file). Carried as a card rule: a reader that gates a leg is run on an existing output file with a known answer before launch.
- ACCEPTED finding 3: the 8-pick cell is frame-bound (11.14 ms vs 11.11 ms), so the 15-vs-8 slope cannot show that "the kernel does not grow"; the negative slopes are the tell. Corrected in `docs/d1-loop12-17-split-plan.md` Pre-decided 198(b) and STATUS NEXT: the claim is withdrawn; what stands is the 15-pick ordering (site 4 at 12.6 ms, kernel at 8.4 ms after i).
- ACCEPTED findings 1/5: the capture-window class read (a read, not a GUI act) is added to the next act together with the unstamped control leg (next.json, cycle 91).
- Finding 6(c) (quit-dialog capture before taskkill) carried into STATUS NEXT as owed with the reaper card.
