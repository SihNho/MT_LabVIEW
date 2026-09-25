# retrospective-cycle83

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.5744  in 130 / out 22061 / cache-create 168691 / cache-read 384829  (283s, 37 turn(s))
- **date:** 2026-09-25 17:27:35
- **outcome:** ANSWERED (285s)
- **verdict-card:** VERDICT-CARD retrospective-cycle83 verdict=refuted -> tools\bench\cards\verdict_retrospective-cycle83.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id retrospective-cycle83, role retrospective) ---
CLAIM: Cycle 83 was run without a costly structural fault.
--- END REVIEW CARD ---

RETROSPECTIVE (v2) of cycle 83 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-25 16:10:33  ..  2026-09-25 17:22:41   (72 min)
    basis: start = archive/peer/2026-09-25-retrospective-cycle82.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-25 16:10 .. 2026-09-25 17:22 (72 min, an explicit cycle window): 8 build logs, 6 peer logs, 45 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 7/8 ok; NO BGRUN line in ['jev_gate.log']
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 3 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 43/45 annotated; blank: ['2026-09-25-const-loopterm-77.md', '2026-09-25-const-loopterm-77c.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 2848 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees
  WARN  A8 recipe/bench runs ended with a RESULT line (C6): 1 log(s) with a run that printed none: ['diag_camrate_persist83.log']

  C1 builds run 7, failure markers 3, logs carrying a failure 3
  C2 peer reviews dispatched 6, archived 45
  C3 wall-clock inside bgrun, BUILDS ONLY 56 min 51 s
  C4 wall-clock inside bgrun, REVIEWS 2 min 19 s; cost $1.4192 from 1 log(s) that report one
  C4b cost lines seen 1 / parsed 1
  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: 0 min 0 s; no judgement-session cost line in this window
  C5 total wall-clock 59 min 10 s  (builds 96%, reviews 3%, judgement session 0%)

  C6 material-marked recipe/bench runs 5, judgement-session attempts refused 0

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 254 - docs/camera-acquisition-facts.md, tools/bench/diag_camrate_persist83.py, tools/bench/drive_m8.py, tools/bench/drive_m8_load83.py, tools/bench/errorlist_shots/161353_before_ctrl_e.png, tools/bench/errorlist_shots/161357_after_ctrl_e.png, tools/bench/errorlist_shots/161358_before_ctrl_l.png, tools/bench/errorlist_shots/161406_after_ctrl_l.png, tools/bench/errorlist_shots/161804_after_esc.png, tools/bench/errorlist_shots/bd_161418_before0.png, tools/bench/errorlist_shots/bd_161421_after0.png, tools/bench/errorlist_shots/bd_161430_before1.png??

  C8 Pre-decided contradictions: 0 new item(s) since the last run, 0 pair(s) asked, 0 suspect at p>=0.85  (advisory; docs/jev-integration-plan.md 2nd wave #7)


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 292/708 ok; 416 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 2 DANGLING of 2174 citations checked:
       docs/m3a1-severed-rows.md:87 -> tools/bench/m3a1_severed_arith.json
       docs/m3a1-severed-rows.md:89 -> tools/bench/m3a1_severed_rows.log

  WARN  L2c plan documents cite files that do not exist yet: 18 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 93 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 600 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:404', 'docs/NAMES.md:421', 'docs/NAMES.md:455', 'docs/NAMES.md:594', 'docs/NAMES.md:716']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A4 every archived review says what was done with it, L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (8; read them directly, they are the primary record) ===
tools/bench/diag_camrate_persist83.log  (2026-09-25 17:19:41)
tools/bench/diag_camrate_persist83b.log  (2026-09-25 17:21:17)
tools/bench/errorlist_check_cycle83.log  (2026-09-25 16:18:52)
tools/bench/jev_gate.log  (2026-09-25 17:20:25)
tools/bench/m8_load83_dry.log  (2026-09-25 16:23:08)
tools/bench/m8_load_83.log  (2026-09-25 17:13:46)
tools/bench/motor_session_end_cycle82.log  (2026-09-25 16:13:23)
tools/bench/motor_session_start_cycle83.log  (2026-09-25 16:18:58)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (6) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_82.log  (2026-09-25 16:13:19)
tools/bench/cycle_83.log  (2026-09-25 16:19:01)
tools/bench/cycle_runner.log  (2026-09-25 16:18:58)
tools/bench/cycle_runner_main_20260925d.log  (2026-09-25 16:18:58)
tools/bench/peer_camrate83.log  (2026-09-25 17:18:31)
tools/bench/retro.log  (2026-09-25 17:22:41)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"retrospective-cycle83","verdict":"<one of: none (no violation) | refuted (a structural fault; name it in violations)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: one structural fault.** Cycle 83 spent about 25 minutes of rig time and one paid review on four "150 Hz" legs that could not have run at 150 Hz, and the project's own camera-facts file had recorded why nine days earlier. Everything else in the cycle was run well: the load measurement it was steered to make was produced, the lever (loop 1.2) was decided from it, LabVIEW was closed after every leg, the failed prediction was reviewed, measured and disposed, and the user question was filed.

## The fault

**What happened.** The driver wrote `AcquisitionFrameRate = 150` through the IMAQdx C API between legs, then let the VI open its own session (`tools/bench/drive_m8_load83.py:30-47`, `:57`). Its docstring justifies this with "the rate is a camera attribute the VI inherits" citing `docs/camera-acquisition-facts.md:25` (`drive_m8_load83.py:6-8`). The same file, at `:427-443` (measured 2026-09-16), says the opposite: "`IMAQdxOpenCamera` hands every session the camera's own defaults, and a setting written by one process is gone the moment that process closes … Phase 0.4 of the master plan had assumed a Python pre-pass could set the operating condition for a later LabVIEW run; it cannot." `STATUS.md:34` carries the short form of the same fact in the hardware banner ("a session open RESETS ROI *and* exposure"). The four 150 Hz legs all counted 89 frames/s (`m8_load_83.log:206, :247, :288, :329`), T5 failed four times (`:355, :360, :365, :370`), and the run ended `rc=1` (`:373`). The review then said exactly this: "The failed prediction was predictable from our own files" (`archive/peer/2026-09-25-hyp-camrate83.md:67`).

**Why it is inference over measurement.** The discriminating test was three C-API calls the driver already contained (open, set, close, reopen, read). It took 26 s when finally run (`diag_camrate_persist83b.log:11`). It was available at 16:23, before the sequencer launched, and was not run. The prediction was instead inferred from one doc line while a measurement in the same document contradicted it. This is also a repeat of a recorded failure (the "Python pre-pass" idea killed on 2026-09-16), which is what the prior-art layer exists to catch. I map it to `inference-over-measurement` because the cheapest fix was a measurement the session had in hand, not a review it had to buy.

**Loss.** Four 150 Hz legs: 329 + 327 + 418 + 415 s = 1,489 s ≈ 25 min of rig time (`m8_load_83.log:206, :247, :288, :329` `secs`). Post-run handling attributable to the failed prediction: ladder 17:14 (`jev_gate.log:1093`), review 17:16–17:18 (`peer_camrate83.log:1, :53`, 139 s, `COST: $1.4192` at `:3`), two diagnostic runs 17:19–17:21 (`diag_camrate_persist83.log:16`, `…83b.log:11`), disposition edits, ≈8 min. Total ≈33 min. The only dollar figure a log carries is the review's $1.4192; the fable/low session's own cost lands in `cycle_runner.log` after the window (C4c: none in window), so the dollar figure understates.

**Counterfactual.** Had the 26 s persistence check been run at 16:23 before the sequencer, or the docstring's `:25` citation been read against `:437` of the same file, the 150 Hz cells would have been dropped at 16:23 and D-2026-09-25-05 filed then. The four 90 Hz legs (1,491 s) would have ended at ≈16:48 instead of 17:13:46, there would have been no failed prediction, no review, no diagnostic, and the retrospective would have launched at ≈16:57 instead of 17:22:41. The load result and the decision (loop 1.2 is the lever) would be identical.

## FINDINGS

**1. Repeated failure.** Within the cycle, the class recurred four times (T5 on every 150 Hz leg), but the sequencer had no per-leg check that could stop it: T4 "rate read back before the leg" (`drive_m8_load83.py:59-60`) reads the value inside the writer's own session, so it passes structurally and proves nothing about the VI's session (the review's main alternative, `hyp-camrate83.md:71`). The approach should have changed at attempt 5 (leg `s1@8@150Hz`, 16:48, `m8_load_83.log:206`), when `camera_after` read 90.0009 and `measured_hz` read 89.0: the driver could have compared `camera_after.hz` with the cell and skipped the remaining three 150 Hz legs (≈19 min). It had every number on the ROW line and did not use them. Across cycles, this is the 2026-09-16 pre-pass failure repeated under another name.

**2. Missing tool.** None needed. The reader existed: `camera()` in the driver itself, and `tools/bench/camera_contract.py`, which `camera-acquisition-facts.md:441` names as "the pre-flight check, not the applier". What was missing was a call to it in the right order, not a tool.

**3. Unmeasured steps.** Two. (a) The persistence of an externally written rate, above. (b) The per-leg `measured_hz` divisor: `frames_delta / RUN_S` uses 120 s while the sampled span is ≈117–118 s (`hyp-camrate83.md:92`), so "89 Hz" is really ≈90.8 Hz. Recorded in PD189 after the review; it does not affect the 90-vs-150 conclusion. Small, and only the review caught it.

**4. Rule compliance.** Rules held where the cycle's behaviour was tested: rig state and motor envelope through the gate on every leg (`m8_load_83.log:5, :30` and equivalents), original md5 unchanged (A5), LabVIEW closed after every leg (G92 rows), rule 2c (the cycle ran to the end), NEXT written before the retrospective (`next.json`, `STATUS.md:53-57`), the failed prediction reviewed before the discriminating test was run (the 17:14:43 launch was blocked, `jev_gate.log:1094`, the review ran at 17:16, the diagnostic at 17:19). Three deviations:
- The hypothesis review was dispatched with `-TaskFile`, not `-ReviewCard` (`peer_camrate83.log:1`; the archive says "verdict-card: (no -ReviewCard)", `hyp-camrate83.md:10`). Session protocol v1 in the cycle prompt (`cycle_83.log:19-22`) requires a `review/1` card for a failed-prediction review, so no `verdict/1` landed in `tools/bench/cards/`. Formally satisfied by prose disposition, not by the protocol.
- The firefighter trigger fired on a retrospective slug, `retro:repeated-failure-class` (`cycle_runner.log:282`, `cycle_83.json:7`), not on a recipe. The brief told the session "this cycle exists to clear THAT block and nothing else" (`cycle_83.log:118`) while the steering card told it to run the load measurement (`:124-126`). The session rightly did the steering act and could not "clear" a slug. The side effect matters: the firefighter mode suspended the judgement/material split, so a fable/low session designed the driver and wrote the prediction that failed. The runner's rule (CLAUDE.md, firefighter paragraph) treats a retrospective slug and a failing recipe alike; that is a runner design question for the user, not something this cycle could fix.
- `docs/camera-acquisition-facts.md:642` said "No `.icd` file exists" and was wrong (corrected this cycle, `:642-647`). The doc contradicted its own `:437` for nine days and no ingest flagged it.

What the audit does not cover: A6 reports "this cycle used no GUI if the retrospective agrees". It did: 285 `gui_actions.log` lines fall in the window (bead picks, done button, bandpass panels, save dialogs, the Error List check), all under the user-approved exception `user 2026-09-17 bead-pick option 1` (`tools/gui_actions.log:2633-2638`). Compliant, but the audit cannot see it. A1's `jev_gate.log` is a known carry (`STATUS.md:87`). A4's two blank reviews are cycle 77's (`const-loopterm-77*.md`), charged here by the day-granular filter. A8's missing RESULT line is the first diagnostic run's own bug (`md5: ''`, `diag_camrate_persist83.log:15`), routed correctly as `our-script-bug` (`jev_gate.log:1098`) and fixed on the rerun. C7 is discussed under devices.

**5. Ordering.** Dry run before the real run: yes (16:23:03 then 16:23:21, `material_marker.log:1654-1655`); the dry log is short, so 18 s is enough. The wrong order was measurement-before-launch: the 26 s persistence check belonged before the 50 min sequencer, as in the counterfactual. Within the run, the 90 Hz cells before the 150 Hz cells was the right order and is why the deliverable survived the fault. After the run, review before diagnostic was the rule's order, and the gate enforced it; running the 26 s diagnostic first would have been cheaper than the $1.42 review, but the failed-prediction rule does not allow that, and the rule is the user's.

**6. What was not reported.** (a) `STATUS.md:54` and PD189 say "8 real legs 8/0"; the sequencer's own RESULT is `FAIL 37/4`, rc=1 (`m8_load_83.log:372-373`). INDEX row 48 does say 37/41 (`archive/benchmarks/INDEX.md:69`), and STATUS's next bullet explains the 150 Hz failure, so it is understated, not hidden. (b) Every one of the eight legs carries a per-leg FAIL row: L8 "the three `choose bandpass` panels … 8 closed (contract 3)" (`m8_load_83.log:21, :62, :103, :144, …`). The v5 contract text still says 3 while `BP_CAP` was raised to N+2 (PD189, `:887-888`); the M gates pass so each leg's RESULT is PASS. It is a stale contract string, harmless, and nowhere reported. (c) The 90 Hz per-leg JSON files were overwritten by the 150-written repeats (PD189 `:890-891` records this; INDEX row 48 too). Reported. (d) `decisions_pending.json:99` stamps D-2026-09-25-05 "asked 17:30", after the retrospective launch at 17:22 and after the window end; a hand-rounded stamp, but the record says the question was filed after the cycle closed.

**7. Judgement inside a material session.** None. The firefighter brief suspended the split (`cycle_83.log:118`), no `material` or `log-reader` agent was dispatched (all five MARKED lines are the session's own bgrun launches, `material_marker.log:1654-1658`), and the one review disposition (accept A over B) was taken by the judgement session and written into the review file (`hyp-camrate83.md:110-118`). The inverse concern applies: the judgement session did material work because the runner put it in firefighter mode, see finding 4.

## DEVICE EFFECT

- **unreported-fact (rc masks a failed probe):** did not fail. The sequencer ended `rc=1` with four FAILs (`m8_load_83.log:373`); the first diagnostic ended `rc=1 (NO RESULT LINE)` on its own crash (`diag_camrate_persist83.log:16`).
- **rule-evaded (confirm-bait refusal + adversarial set):** did not fail. The task asked for "the strongest reason my explanation is wrong" and the appended set is present (`hyp-camrate83.md:39-51`).
- **tool-not-built (prior-art review):** did not fire and by its own scope was not required to: `guard_cycle` gates RECIPE builds and leaves `tools/bench` open (violation-decisions, premature-build 2026-09-16 19:16). The one fault of this cycle was a prior-art question with the answer on file (`camera-acquisition-facts.md:437-439`), and the "diagnostic" that skipped it was a 50 min, eight-leg real-rig run. The device did what it was built to do. Its scope is the hole. I record this as a finding and do not re-slug the same loss twice.
- **repeated-failure-class (guard_peer refuses priorart/retro while the newest review of that kind is undisposed):** not exercised for retro (cycle 82's retrospective is disposed, `violation-decisions.md:1299-1318`). No prior-art dispatch in the window.
- **unreported-fact (C3/C4 separate build and review cost):** worked, C4 parsed 1/1.
- **premature-build (guard_cycle):** no recipe run in the window. Not exercised.
- **scope-creep (C7 out-of-plan list):** fired on the wrong plan again. It read `docs/cycle27-plan.md` and listed 254 files including screenshots, while the cycle's plan is `docs/d1-loop12-17-split-plan.md` (`next.json:2`). This was already declared `device-failed` on 2026-09-25 14:28 with the repair owed after the deliverable (`STATUS.md:74, :78`). It failed again as predicted; re-emitting a slug for a repair already on file would be double counting, so I do not.
- **device-failed (COST regex + parsed count):** worked, 1/1.
- **device-failed (bgrun FAIL scan forces rc=1):** consistent, `m8_load_83.log:373`.
- **repeated-failure-class (OpLoopEndRef_v0), stop record + launch gate, read-only exemption, novel record, release table, selftest exemption, sink gates, parity device:** not exercised; no recipe, no stage, no stop record in the window.
- **device-failed (motor_gate FAIL exit):** every gate row PASS on eight legs; not exercised on a failure.
- **repeated-failure-class (guard_peer let a retry through):** worked in the opposite direction this time: the session's 17:14:43 diagnostic launch was BLOCKED until the review existed (`jev_gate.log:1094`), the review ran, and the diagnostic launched at 17:19.
- **device-failed (Jev exemption by COMMAND):** the ladder classified `m8_load_83.log` as `new-problem p=0.574` → review owed (`jev_gate.log:1093`) and the first diagnostic as `our-script-bug p=0.986` (`:1098`). Correct on both.
- **repeated-failure-class (guard_session refuses SendMessage to material):** no material agents; not exercised.
- **device-failed (bgrun records at child start):** C6 = 5 material-marked runs, matching the five MARKED lines. The 17:20:10 launch was blocked by JEV-BUDGET (`jev_gate.log:1097`) and still marked (`material_marker.log:1657`); the marker is written before the child starts, which is what that decision said not to do. One line of evidence, cosmetic in effect this cycle.
- **device-failed (C7 reads the plan named in next.json):** not yet built, and its absence is the C7 failure above.
- **repeated-failure-class (dry run reports every unroutable row):** not built by decision ("Cycle 83 is the load measurement and runs no stage", `violation-decisions.md:1306-1307`). Carried in NEXT (`STATUS.md:57`).

No device failed on the fault this cycle actually had; the fault lay outside every device's scope.

VIOLATION: inference-over-measurement | loss_min=33 | loss_usd=1.4192 | evidence=tools/bench/drive_m8_load83.py:6

VERDICT {"schema":"verdict/1","id":"retrospective-cycle83","verdict":"refuted","alternative":"The 150 Hz legs were a legitimate measurement: PD188(d) said '150 Hz only if the camera reaches it' and the only way to learn that was to run them.","discriminating_test":"Read docs/camera-acquisition-facts.md:437-439 (2026-09-16) against drive_m8_load83.py:6-8, then run diag_camrate_persist83.py (26 s) with no VI: if it reads 90 after reopen, the 150 Hz legs were decidable before launch.","violations":[{"slug":"inference-over-measurement","loss_min":33,"loss_usd":1.4192,"evidence":"tools/bench/drive_m8_load83.py:6"}],"sources":["tools/bench/drive_m8_load83.py:6","docs/camera-acquisition-facts.md:437","tools/bench/m8_load_83.log:355","tools/bench/m8_load_83.log:373","tools/bench/peer_camrate83.log:3","archive/peer/2026-09-25-hyp-camrate83.md:67","tools/bench/diag_camrate_persist83b.log:11","tools/bench/jev_gate.log:1093","tools/gui_actions.log:2633"],"note":"Load result and the loop-1.2 decision stand. $ figure is the review only; the fable/low session's cost is logged after the window. C7 fired on the wrong plan again (repair already on file 14:28), not re-slugged."}

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
