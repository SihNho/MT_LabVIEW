# retrospective-cycle52

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.3311  in 12 / out 25489 / cache-create 129639 / cache-read 463753  (348s, 16 turn(s))
- **date:** 2026-09-20 05:39:39
- **outcome:** ANSWERED (350s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 52 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-20 03:25:12  ..  2026-09-20 05:33:48   (129 min)
    basis: start = archive/peer/2026-09-20-retrospective-cycle50.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-20 03:25 .. 2026-09-20 05:33 (129 min, an explicit cycle window): 20 build logs, 8 peer logs, 8 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 20/20 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 2 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 8/8 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 21, failure markers 6, logs carrying a failure 2
  C2 peer reviews dispatched 8, archived 8
  C3 wall-clock inside bgrun, BUILDS ONLY 58 min 39 s
  C4 wall-clock inside bgrun, REVIEWS 47 min 38 s; cost $33.1355 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C5 total wall-clock 106 min 17 s  (reviews are 44% of it)

  C6 material-marked recipe/bench runs 27, judgement-session attempts refused 6  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 13 - STATUS.md, tools/bench/c51m2_astcheck.py, tools/bench/c52_astcheck.py, tools/bench/c52r2_astcheck.py, tools/bench/c52r3_astcheck.py, tools/bench/diag_donor_census.py, tools/bench/diag_movein_set.py, tools/bench/diag_qdonor2_ia.py, tools/bench/diag_qdonor2_stage.py, tools/bench/diag_queue_donor.py, tools/bench/diag_queue_donor2.py, tools/bench/verify_d1_s2.py??


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 282/508 ok; 226 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 1237 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 16 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  WARN  L2b cited line numbers are in range: 1 citation(s) point past the end of the file: ['docs/NAMES.md:1022 -> docs/toolkit-capabilities.md:775 (file has 675 lines)']
  PASS  L3 STATUS.md stays one screen: 71 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 284 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:597', 'docs/NAMES.md:870', 'docs/NAMES.md:884', 'docs/NAMES.md:902', 'docs/NAMES.md:929']

AUDIT PASS


=== BUILD LOGS INSIDE THE WINDOW (20; read them directly, they are the primary record) ===
tools/bench/c51_astcheck.log  (2026-09-20 03:32:11)
tools/bench/c51_facts.log  (2026-09-20 03:42:30)
tools/bench/c51m2_astcheck.log  (2026-09-20 03:51:26)
tools/bench/c52_astcheck.log  (2026-09-20 04:22:19)
tools/bench/c52_lvrestart.log  (2026-09-20 04:26:40)
tools/bench/c52r2_astcheck.log  (2026-09-20 04:41:15)
tools/bench/c52r2_lvrestart.log  (2026-09-20 04:50:22)
tools/bench/c52r2_lvrestart2.log  (2026-09-20 05:04:29)
tools/bench/c52r2b_astcheck.log  (2026-09-20 04:46:31)
tools/bench/c52r2c_astcheck.log  (2026-09-20 05:00:47)
tools/bench/c52r3_astcheck.log  (2026-09-20 05:17:45)
tools/bench/diag_donor_census.log  (2026-09-20 05:22:45)
tools/bench/diag_movein_set.log  (2026-09-20 05:19:45)
tools/bench/diag_qdonor2_ia.log  (2026-09-20 05:02:27)
tools/bench/diag_qdonor2_stage.log  (2026-09-20 04:48:25)
tools/bench/diag_queue_donor.log  (2026-09-20 04:25:08)
tools/bench/diag_queue_donor2.log  (2026-09-20 04:43:37)
tools/bench/stage_d1_s2_loops.log  (2026-09-20 04:06:11)
tools/bench/verify_d1_s2.log  (2026-09-20 04:21:54)
tools/bench/wait_priorart_c51.log  (2026-09-20 03:41:55)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (8) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_38.log  (2026-09-20 03:55:17)
tools/bench/cycle_39.log  (2026-09-20 03:55:17)
tools/bench/cycle_runner.log  (2026-09-20 03:55:17)
tools/bench/cycle_runner_main_20260920a.log  (2026-09-20 03:55:17)
tools/bench/ingest_c51.log  (2026-09-20 03:51:44)
tools/bench/peer_qdonor2_p8.log  (2026-09-20 04:58:39)
tools/bench/priorart_d1-s2-loops.log  (2026-09-20 03:41:54)
tools/bench/retro.log  (2026-09-20 05:33:47)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle52-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

I have what I need — and the primary record contradicts the hand-off document on the window's central event. Here is the retrospective of cycle 52 (window 2026-09-20 03:25:12 → 05:33:48; note this window in fact contains both the runner's CYCLE 38 session, 03:25–03:55, and CYCLE 39, 03:55 onward — `tools/bench/cycle_runner.log:69`).

## Verdict first

This was a productive window run mostly well: the prior-art gate refused a flawed stage recipe, both findings were fixed and released properly, the S2 build ran and saved its artefact, the queue-donor question was measured to the fleet's hard boundary, and `move_in`'s wire-severing semantics — the likeliest killer behind ten route-B deaths — were finally measured (STATUS.md:58). But the cycle's largest single expenditure was built on a false premise that a two-second log read would have removed, and one safety device is measurably broken. Those are the two faults; everything else is findings.

**Fault 1 — the cycle re-verified an artefact whose verification had already completed and passed, because it inferred "killed mid-verification" from a mid-run log read and never re-read the finished log.** STATUS's own record claims cycle 51's build "killed its own child mid-verification: the post-save gates G12 … and G15 … NEVER RAN, and `tools/bench/stage_d1_s2_loops.log` simply stops inside the cold re-read" (STATUS.md:25), and repeats it as "OPEN 54(b) RECURRED AND COST A CYCLE ITS VERIFICATION" (STATUS.md:63). The primary record says otherwise: the build was dispatched detached (`BGRUN DETACH pid=10924 mode=breakaway`, stage_d1_s2_loops.log:1), survived the 03:55:17 session exit, and finished with `PASS G12 … COLD 1 PRELOADED 1` (stage_d1_s2_loops.log:145), `PASS G15 FATAL` (stage_d1_s2_loops.log:287), and `BGRUN END rc=0 after 776s` at 04:06:12 (stage_d1_s2_loops.log:300). `verify_d1_s2.py` was then launched at 04:08:08 — two minutes AFTER that END line existed — still asserting in its own banner that "cycle 51's client was KILLED" (verify_d1_s2.log:1-3), and spent `BGRUN END rc=0 after 825s` (verify_d1_s2.log:289) re-running hash checks, child COLD/PRELOADED ExecState, and both 260-second SubVI-table censuses that the stage log already carried as PASSes. The genuinely new content (the S1-vs-S2 loop-identity settlement refuting the #10170 worry) needed perhaps a third of that run. Counterfactual, on the clock: had the 04:08 dispatch been preceded by re-reading the finished log — available since 04:06:12, one grep for `BGRUN END` — the verify run shrinks to the loop-identity read, the queue-donor round starts ~10 minutes earlier, and the cycle's last diagnostic lands ~05:23 instead of 05:33. Equally costly and unpriceable: STATUS now hands cycle 53 a false fact in three places (the 54(b)-recurrence narrative, the "G12/G15 NEVER RAN" claim, the "cycle 52 verifies the file it left" framing), when what actually happened is that bgrun's breakaway detach *worked* — the one device in this story that performed better than the session believed. No log carries a dollar figure for build wall-clock, so the dollar loss is honestly unknown.

**Fault 2 — a device failed, threshold 1: the FAIL-marker scan family behind the mandatory-review gate never fired on a failing run.** `diag_movein_set` failed its gate P6 (`  **FAIL**  P6 …`, diag_movein_set.log:57; `BGRUN END rc=1 after 101s`) at 05:19:45 — a failed prediction under the CLAUDE.md rule ("A FAILED PREDICTION triggers mandatory peer review"). No review of it exists: the window's eight archived reviews (audit C2) cover the three retros, the prior-art rounds, the boundary recut, and qdonor2-p8 — none covers P6. `guard_peer.py`'s `FAILURE_RE` (`^\s*(?:->\s*)?FAIL\b`, tools/hooks/guard_peer.py:73) matches the documented `  FAIL  ` form but not the `  **FAIL**  ` these diagnostics print, so `diag_donor_census` launched at ~05:20 past a failing, unreviewed log with the gate silent. This is the on-file 2026-09-17 03:38 `device-failed` repair's own family — its decision text says the added regex is "the same form audit_cycle/guard_peer use" — failing again on a new literal spelling, in the never-fired-when-it-should-have mode. bgrun's half of the family held (it forced rc=1); the guard_peer half did not. In-window monetary loss is roughly zero — the failure was self-inflicted (a mis-stated gate: the brief said Diagram #686 where the nodes live on #639) and correctly understood — but a scan that hides failures is this project's named worst class (`unreported-fact`'s founding defect), and the audit's A3 PASS ("unreviewed: none") over this same window shows the blindness extends to the auditor. To the cycle's credit, the judgement session found this itself and scheduled the repair (STATUS.md:59); the device is still broken until that lands. Counterfactual: had the regex matched, the 05:20 census dispatch would have been refused until a P6 review was archived — the rule would have held mechanically instead of by luck of the fail being trivial.

## FINDINGS

**1. Repeated failure.** The "stage ends with no savable artefact" class recurred exactly twice at the same place — round 1's queue-donor probe left nothing savable (STATUS.md:24, `create_control` produced no ControlTerminal), and round 2's `diag_qdonor2_stage` replay ended `BGRUN INNER FAILURE` 11/1 with ExecState 0 from step 1 onward, `g.save()` unreachable (STATUS.md:23). The approach changed at exactly the right attempt: the re-split trigger (CLAUDE.md, "Big or blocked work is SPLIT…", clause 3) fired on the second occurrence and the decomposition plan was correctly deferred to a judgement session (STATUS.md:23). Also of note: the session's own explanation for the ExecState 0 ("the unwired Index Array broke it") was refuted by its own falsification criterion in `diag_qdonor2_ia` — the compile-state-perturbation family (the cycle-23 `Connect Wire` family) recurred and was this time *measured* rather than argued.

**2. Missing tool.** A `Terminal.DataType` reader. Its absence is now measured, not asserted: no built op reads it (`node_terms:870`, `report_all:488`, `node_info:2459` — STATUS.md:22, B1), building one is forbidden by Pre-decided 2, and its absence forces next cycle's 18-node trial census in place of a one-line type query. It did not make *this* cycle more expensive — the census was bounded work — but it converts the queue-donor question from a lookup into an experiment. The other absence that would have paid for itself is not a tool: a habit of grepping `BGRUN END` before deciding a child's fate (Fault 1).

**3. Unmeasured steps.** The headline is Fault 1: "the gates never ran / the client was killed" was decided by inference from a log read taken mid-run at ~04:00, recorded as fact at release time, and never re-measured, though the finished log sat on disk from 04:06:12. Everything else in the window was unusually well-measured — both queue-donor shapes were run rather than argued, the loop-identity worry was settled by set comparison, and the IA explanation was submitted to its own discriminating test and lost.

**4. Rule compliance.** Broken: the mandatory-review rule for the P6 failed prediction (Fault 2 — no review archived). Broken by the *previous* session but landing in this window: OPEN 54(b)'s "hold the turn open until BGRUN END" — the 03:55:17 exit with a running child was a real breach even though breakaway detach rescued the work; the rule failed, the mechanism saved it. Satisfied genuinely: A5 (originals untouched, md5 `2a78e17c…` pinned in every log), prior-art-before-build with both findings fixed and `FIXED:`-released, 8/8 dispositions, retro dispatched last (retro.log stamp 05:33:47). What the audit does NOT cover: (a) it cannot distinguish a finished log from a mid-run one, so it can never catch Fault 1's class; (b) A3 passed while a failing log (movein, 05:19:45) had no review newer than it — its FAIL detection shares the `**FAIL**` blindness and its review-matching is day-granular; (c) C4's $33.1355 reconciles to priorart $4.7775 (priorart_d1-s2-loops.log:4) + qdonor2-p8 $4.4815 (peer_qdonor2_p8.log:3) + the CYCLE 38 judgement session's $23.8765 (cycle_runner.log:69), but the CYCLE 39 judgement session — the bulk of this cycle's thinking — had no cost line yet at audit time, so C5/C4 understate true spend by roughly the size of one judgement session; (d) C7 still lints scope against `docs/cycle27-plan.md` for a cycle numbered 52 — the 13 out-of-plan files are almost all pre-decided diagnostic work, and the counter's plan-name scheme has been noise since cycle 28.

**5. Ordering.** Defensible and mostly exemplary: prior-art → fix → release → launch → verify → measure → retro. Two inversions, one per fault: verify was launched before the finished stage log was read (the single cheapest reordering in the window), and `diag_donor_census` launched before the P6 failure had any review (let through by the broken gate rather than chosen, so I charge it to Fault 2).

**6. What was not reported.** The session's summary *inverted* the window's central fact: STATUS.md:25 and STATUS.md:63 report G12/G15 as never-run and 54(b) as recurred, while stage_d1_s2_loops.log:145/287/300 shows both gates PASS and a clean rc=0 END. A reader of STATUS alone concludes the runner's session-exit behavior destroyed a verification it demonstrably did not, and credits cycle 52 with rescue work that was substantially re-work. Credit where due: STATUS.md:59 reports the guard_peer blind spot against itself, plainly and with the right evidence line.

**7. Judgement inside a material session.** One borderline instance: the c52m2 record states the mandatory qdonor2-p8 review "is ACCEPTED and its discriminating test was RUN" (STATUS.md:23) — acceptance of a review finding is a judgement-session call under CLAUDE.md's delegation rule, and the acceptance verdict appears inside a material-session release note. Mitigation: running the review's own named discriminating test is close to a pre-decided act under Pre-decided 35(b)'s facts-only brief, the test's *outcome* (the session's explanation refuted) was recorded without spin, and the same session explicitly refused the adjacent judgement ("that plan is a design decision and was deliberately NOT written by this material session", STATUS.md:23). The boundary bent, held where it mattered; a finding, not a slug. C6 corroborates the machinery working: 6 judgement-session material attempts refused.

## DEVICE EFFECT

- **Prior-art review + premature-build guard + stop record/launch gate**: WORKED, and together — the c51 recipe was refused (`PRIOR-ART: contradicted`, archive/peer/2026-09-20-priorart-d1-s2-loops.md; $4.7775, priorart_d1-s2-loops.log:4), both findings were built in (`cond_read()`, the G15 SubVI TABLE gate — c51m2_astcheck.log), released via `FIXED:` lines, and only then launched. The refused findings then *passed as gates* in the real run (stage log G12/G15). This is the device chain functioning end to end.
- **Confirm-bait refusal (`rule-evaded`)**: held — the qdonor2-p8 dispatch ran adversarial (`-Role hypothesis`) and genuinely attacked: it refuted the session's own explanation, and the refutation survived the discriminating test.
- **Blank-disposition refusal (`repeated-failure-class`)**: held — A4 8/8.
- **Cost lines (`unreported-fact` C3/C4) and cost-regex self-test**: held — C4b 3/3 parsed, sum reconciles to the cent; the CYCLE 39 blind spot is a scope limit, not a parse miss.
- **bgrun FAIL-scan (`device-failed` 2026-09-17 03:38)**: split verdict — bgrun's own half held (both failing diagnostics forced to rc=1), but the family's guard_peer half FAILED on the `**FAIL**` form: never fired on diag_movein_set.log:57, and the mandatory review it exists to force was never dispatched. This is Fault 2's emission.
- **`OpLoopEndRef_v0` reader (`repeated-failure-class`)**: held and load-bearing — every conditional-terminal readback in the stage and verify runs went through `cond_read()` with UNREAD as a scored outcome.
- **Scope counter (`scope-creep` C7)**: produced its 13-file list as designed (a counter, not a refusal); degraded by the stale plan-name scheme but no scope fault got through — the files are the cycle's pre-decided diagnostics.
- **Session-boundary machinery (not on the list but adjacent)**: bgrun's breakaway detach outperformed its reputation — the 03:55 session exit that STATUS blames for killing verification killed nothing.

---

VIOLATION: inference-over-measurement | loss_min=10 | loss_usd=? | evidence=tools/bench/stage_d1_s2_loops.log:300
VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/diag_movein_set.log:57

## Sources

(extract from answer)

## What was done with it

Disposed by the **cycle-52 judgement session, 2026-09-20 05:4x**, immediately on delivery. Both violations are
**ACCEPTED**. Fault 1 is mine and I checked it against the machine before accepting it.

### `VIOLATION: inference-over-measurement` (evidence `tools/bench/stage_d1_s2_loops.log:300`) — ACCEPTED, CONFIRMED

**The review is right and my framing was false.** I re-read the file after the verdict landed:
`tools/bench/stage_d1_s2_loops.log` is **50,905 B / 300 lines, last written 04:06**, and ends
`=== GATES: 35 pass / 0 fail` … `BGRUN END rc=0 after 776s`, with **G15 FATAL PASS** (the SubVI table against the
ORIGINAL), G13 refs 6/6/0 and G14 the ORIGINAL's md5 unchanged. Cycle 51's verification **completed and passed**.

What I actually did: at session start I read `tail -c 3000` of that file when it was **12,978 B with mtime 03:55**
— i.e. **while it was still being written** — saw it stop inside the cold re-read with no `BGRUN END`, and
concluded the session exit had killed the child. It had not: bgrun's breakaway detach kept the child alive and it
finished 11 minutes later. **A log read while its run may still be in flight is not a reading**, and the terminal
`BGRUN END`/`TIMEOUT` line is the only proof a run finished — which is the same discipline the fleet already
applies to `bgrun` and which I failed to apply to my own first read of the cycle.

Cost, honestly: the `verify_d1_s2.py` dispatch (825 s of LabVIEW, inside a material session) largely re-ran G12 and
G15, which had already passed. It was not wholly waste — the **loop-identity** measurement in it was new (S1's
`{637, 15173, 25380}` vs S2's added `{10170, 23032, 23041}`, and the side-by-side proof that no pre-existing loop's
conditional terminal changed), and cycle 51's log does not contain it. But that reading could have been a 60-second
question rather than a full re-verification.

⇒ Landed: (1) `STATUS.md`'s NEXT line claiming "OPEN 54(b) RECURRED AND COST A CYCLE ITS VERIFICATION" is
**withdrawn and replaced** by the true account — 54(b) *was* breached at 03:55:17 (a session exited with a child
running) but breakaway detach rescued the work, and the cost was mine, from inferring instead of re-reading;
(2) `docs/cycle27-plan.md` Pre-decided **37(a)** now records that S2 is accepted on **cycle 51's own 35/0 plus
cycle 52's independent 23/0**, which is a stronger footing than either alone; (3) the same correction is written
into my disposition of `archive/peer/2026-09-20-retrospective-cycle50.md`, where I had repeated the false claim;
(4) the general rule is added as **37(j)**: never read a log for a verdict until its terminal line is present.

### `VIOLATION: device-failed` (evidence `tools/bench/diag_movein_set.log:57`) — ACCEPTED, and it was found twice

The same fault was found independently by this session earlier in the cycle and is already recorded at
`docs/violation-decisions.md` `## device-failed — 2026-09-20 05:34` and `docs/cycle27-plan.md` Pre-decided
**37(i)**: `guard_peer.py:73`'s `FAILURE_RE` matches the documented `  FAIL  ` (`:71`) but not the `  **FAIL**  `
the cycle-50/52 diagnostics print, so the mandatory-review gate cannot see their failures. The repair — conform the
diagnostics **and** widen the regex to `\*{0,2}FAIL`, then self-test both ways — is the next cycle's SECOND ACT. It
is a repair of an existing gate, so the user's 2026-09-18 08:53 no-device order does not reach it.

**The half I had wrong: I ruled the P6 review not owed, and I withdraw that.** Pre-decided 37(f) argued no
hypothesis review was due because P6 was a drafting error in the gate's own assertion rather than a diagnosis
driving work. That is judgement overriding a mechanical rule — exactly what this layer exists to catch — and
CLAUDE.md is explicit that one's own successful discriminating test does not discharge the mandate. ⇒ **The P6
review is owed and is a prerequisite to the S3 build**, not an optional extra; it is cheap and it bears directly on
S3, since P6's subject is where `#48` actually lives (`Diagram #639`, not `#686`). Written into `STATUS.md`'s NEXT
and into 37(f), which is amended rather than deleted so the withdrawn reasoning stays readable.

### The other findings

**2. Missing tool (`Terminal.DataType` reader)** — ACCEPTED as a finding, NOT built: Pre-decided 2 forbids a new
op. The consequence the review names is already the plan: 36(d) turns the queue-donor question into an 18-node
**trial census** by construction instead of a type lookup. **4. Rule compliance** — accepted in full, including
that 54(b) was genuinely breached by the previous session even though the mechanism rescued the work; the rule
failed and the machine covered for it, which is worth saying plainly rather than scoring as a pass.
