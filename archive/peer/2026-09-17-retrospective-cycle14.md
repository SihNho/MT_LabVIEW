# retrospective-cycle14

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (299s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 14 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-16 20:19:33  ..  2026-09-17 03:25:34   (426 min)
    basis: start = archive/peer/2026-09-16-retrospective-cycle13.md mtime (cycle 13 closed there; a plan mtime lags the work - see the docstring); end = now (this cycle's retrospective has not run yet)
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

== cycle audit, 2026-09-16 20:19 .. 2026-09-17 03:25 (426 min, an explicit cycle window): 13 build logs, 16 peer logs, 50 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 13/13 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 5 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 40/50 annotated; blank: ['2026-09-16-case-frame-identity-and-contents.md', '2026-09-16-case-frame-identity-retry.md', '2026-09-16-load-vs-editmode-23c-agy.md', '2026-09-16-load-vs-editmode-23c-retry.md', '2026-09-16-load-vs-editmode-23c.md', '2026-09-16-priorart-master-plan-rev3.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1769 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 13, failure markers 5, logs carrying a failure 5
  C2 peer reviews dispatched 16, archived 50
  C3 wall-clock inside bgrun, BUILDS ONLY 30 min 25 s
  C4 wall-clock inside bgrun, REVIEWS 68 min 8 s; cost $13.1671 from 4 log(s) that report one
  C4b cost lines seen 5 / parsed 4   <- MISMATCH: a cost line in the logs is not being parsed; the C4 figure is an UNDERSTATEMENT, not a measurement
  C5 total wall-clock 98 min 33 s  (reviews are 69% of it)

  C6 material-marked recipe/bench runs 16, judgement-session attempts refused 2  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs\cycle14-plan.md: 76 - docs/cycle11-plan.md, docs/cycle12-plan.md, docs/cycle13-plan.md, docs/d1-build-plan.md, docs/doc-lint-plan.md, docs/frame-ownership-design.md, docs/gpu-backend.md, docs/instrument-libraries.md, docs/main-vi-stop-and-save.md, docs/questions-for-user-2026-09-14.md, docs/restructure-plan-4.6.md, docs/stage2-plan.md??


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 273/338 ok; 65 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 493 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 9 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:111 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle15-plan.md'] current
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 77 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:581', 'docs/NAMES.md:854', 'docs/NAMES.md:868', 'docs/benchmark-report-2026-09-04.md:14', 'docs/benchmark-report-2026-09-04.md:48']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (13; read them directly, they are the primary record) ===
tools/bench/d0_clickprobe.log  (2026-09-17 02:32:52)
tools/bench/detach_canary.log  (2026-09-17 01:41:51)
tools/bench/detach_canary_balive.log  (2026-09-17 01:45:22)
tools/bench/detach_test.log  (2026-09-17 01:31:23)
tools/bench/detach_timeout_test.log  (2026-09-17 01:32:35)
tools/bench/diag_stop_condterm_panel.log  (2026-09-16 22:14:18)
tools/bench/diag_stop_save_seam.log  (2026-09-16 22:07:04)
tools/bench/drive_original_copy.log  (2026-09-17 01:47:16)
tools/bench/drive_original_copy_run2.log  (2026-09-17 01:52:38)
tools/bench/drive_original_copy_v2.log  (2026-09-17 02:22:16)
tools/bench/drive_original_copy_v3.log  (2026-09-17 02:48:53)
tools/bench/gpu_n1_deltas.log  (2026-09-17 02:59:11)
tools/bench/gpu_n1_full_fixture.log  (2026-09-17 01:33:01)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (17) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/ingest_20260916.log  (2026-09-16 21:28:49)
tools/bench/outcome_review_c14.log  (2026-09-16 21:35:23)
tools/bench/peer_bandpass_click.log  (2026-09-17 02:18:21)
tools/bench/peer_bgrun_detach.log  (2026-09-17 01:40:15)
tools/bench/peer_bgrun_treekill.log  (2026-09-17 01:44:27)
tools/bench/peer_d0_com_blocked.log  (2026-09-17 01:57:46)
tools/bench/peer_d0_hwnd.log  (2026-09-17 02:38:51)
tools/bench/peer_d0_hwnd_agy.log  (2026-09-17 02:43:36)
tools/bench/peer_d0v3-stop-heuristic.log  (2026-09-17 02:56:34)
tools/bench/peer_stopterm.log  (2026-09-16 22:11:34)
tools/bench/peer_stopterm2.log  (2026-09-16 22:17:17)
tools/bench/priorart_cycle14.log  (2026-09-16 20:21:06)
tools/bench/priorart_cycle15_d1.log  (2026-09-16 22:03:43)
tools/bench/priorart_d1_build.log  (2026-09-17 03:19:02)
tools/bench/priorart_doc_lint.log  (2026-09-16 21:15:55)
tools/bench/retro_cycle14.log  (2026-09-17 03:25:34)
tools/bench/retro_v2_compare.log  (2026-09-16 21:03:42)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle14-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

## Verdict

The cycle’s costliest structural fault was the repeated D0 bandpass failure inside attempt 3. `drive_original_copy_v2` observed the decisive failure at 02:12:25, 91.6 seconds into run 1, but executed the same path again in run 2 and reproduced it at 410.1 seconds (`tools/bench/drive_original_copy_v2.log:62`, `:201`). The batch finally ended after 683 seconds with thirteen failures (`:392-395`). The approach should have changed immediately after run1.P6 to the click-transaction/HWND probe later used successfully, rather than running the second full cycle.

Estimated loss is 10 minutes; no build log carries a dollar amount. Had attempt 3 stopped at run1.P6 around 02:12 and launched the discriminating review/probe then, the downstream sequence could have advanced roughly ten minutes sooner and the cycle ended around 03:16 instead of 03:25.

A device failure must also be recorded. The exit-propagation device did not protect `diag_stop_condterm_panel`: its own summary reported a failed gate, yet the enclosing run ended with rc=0 (`tools/bench/diag_stop_condterm_panel.log:15-18`). Correct propagation would have produced rc=1 at the same time, so its direct measured time loss is zero.

## Findings

1. **Repeated failure.** D0 attempt 1 ended in a harness exception (`drive_original_copy.log:18-29`); attempt 2 exposed the serialized COM-worker defect and was appropriately followed by adversarial review (`drive_original_copy_run2.log:25-34`; `archive/peer/2026-09-17-d0-com-blocked-in-picking-loop.md:96-115`). Attempt 3 changed the approach, but then repeated its identical bandpass failure internally. The approach should have changed at attempt 3, run1.P6—not after run 2—to the foreground/HWND/input-state probe later embodied by `d0_clickprobe` (`d0_clickprobe.log:13-15`, `:46-50`). Separately, the stop-terminal hypothesis failed twice and was correctly stopped rather than retried; the mandated reader is recorded in `STATUS.md:75-77`.

2. **Missing tool.** No reader should have been built before the first stop-terminal failure. After the second, however, the recursive `ControlTerminal` census followed by `WhileLoop.Loop End Ref` became the specifically required missing reader. Its absence leaves the identity of wire 3457’s conditional-terminal sink unresolved (`STATUS.md:75-77`; `archive/peer/2026-09-16-stop-condterm-panel-fail2.md:125-144`). It would have answered both the mistaken `CaseStructure#22082` identification and the inconclusive panel-wire test. The cycle correctly queued it rather than attempting a third inference.

3. **Unmeasured steps.** D0 v3 declared R11 successful because `current image number` stayed constant even though `ExecState` remained 2 (`drive_original_copy_v3.log:83-126`). Cleanup then spent 60 seconds trying the stop controls and finally aborted the VI (`:128-221`). A cheap VI-Server test—write/read each stop Boolean and poll `ExecState`—was available; the peer review identified precisely that test (`archive/peer/2026-09-17-d0v3-stop-heuristic.md:53-55`). This invalidates R11 but was caught before the retrospective, so I treat it as a finding rather than another structural slug.

4. **Rule compliance.** The cycle satisfied the bgrun discipline, accounted for all terminated runs, preserved the original’s checksum, reviewed every failing log, and stopped the stop-terminal line after two failed explanations. The material failure budget was not honored inside D0 v2: run 2 repeated the already-failed run-1 path (`CLAUDE.md:252-254`; `drive_original_copy_v2.log:62`, `:201`).

   The attached audit does not cover several important things:

   - A4 is explicitly day-granular, so its 40/50 figure cannot attribute all blank dispositions to this window.
   - C6 counts refused judgement-session attempts but does not inspect decisions written inside material-session disposition text.
   - A6 says GUI use is “n-a,” although v3 records ten GUI actions (`drive_original_copy_v3.log:308`); it therefore does not actually audit this window’s GUI actions.
   - C4b’s 5/4 mismatch is a false positive, not missing spend: the four genuine price lines total exactly $13.1671, while the fifth “seen” match is prose containing the token `cost_usd` in `retro_v2_compare.log:100`. The cost parser itself successfully parsed every genuine price line.

5. **Ordering.** The major ordering was defensible: the outcome review caused a user-approved delivery re-plan; cycle-15 prior art completed before its diagnostics; the full GPU fixture ran before D1 construction; and the D1 build review completed without any D1 recipe build appearing in the window (`cycle15-plan.md:14-20`; `priorart_cycle15_d1.log:1-6`; `gpu_n1_full_fixture.log:1-4`; `priorart_d1_build.log:1-6`).

   One gate hole remains: `priorart_cycle14.log` started at 20:21 and never recorded an end or archive result, yet another prior-art dispatch began at 21:56 (`priorart_cycle14.log:1`; `priorart_cycle15_d1.log:1`). Thus the repeated-review disposition device did not catch an in-flight, never-disposed review. No dollar or completed wall-time figure exists for the abandoned review, so its loss cannot be sized.

6. **What the session summary understated.** The headline “16 pass, 0 fail” hides three material facts:

   - R11 used an invalid frozen-counter predicate while the VI remained running (`drive_original_copy_v3.log:126`).
   - Cleanup required an abort after another 60 seconds (`:219-221`).
   - The run created 2,041 TIFFs totalling 2,675,689,770 bytes before cleanup (`:228`, `:270-302`).

   The later peer review and current `STATUS.md:92-97` now expose these facts, but the raw batch summary itself did not.

7. **Judgement inside a material session.** Yes. The D0 material session explicitly accepted a review, rejected one finding, refused a retry strategy, and decided that the next build required judgement (`archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md:171-203`). More starkly, the D1 prior-art disposition says a material session accepted all ten findings, rewrote the plan, and let A1/A6 and A4 change cycle direction (`archive/peer/2026-09-17-priorart-priorart-d1-build.md:476-499`). Those are decisions reserved to judgement by `CLAUDE.md:250-274`. This changed what the cycle produced, but the evidence does not establish a defensible additional time or dollar loss, so it remains a finding rather than displacing the measurable repeated-failure fault.

## Device effect

- `unreported-fact`, runner exit propagation: **failed**—an internal failed gate ended rc=0 (`diag_stop_condterm_panel.log:15-18`).
- `rule-evaded`, adversarial prompt gate: worked; review prompts attacked hypotheses rather than soliciting confirmation, for example `peer_d0_com_blocked.log:1`.
- `tool-not-built`, prior-art review: worked and materially caught existing contradictions before D1 construction (`priorart_d1_build.log:6-29`, `:132-145`).
- `repeated-failure-class`, disposition gate: **failed at its in-flight edge**—cycle-15 prior art was dispatched while cycle-14 prior art had neither ended nor produced a disposition (`priorart_cycle14.log:1`; `priorart_cycle15_d1.log:1`).
- `unreported-fact`, split build/review cost: worked; the four real price lines sum to the reported $13.1671. C4b’s mismatch is a prose-token false positive, not understated cost.
- `premature-build`: worked; both cycle-15 prior-art reviews completed before any corresponding D1 recipe build, and no D1 build appears among the in-window build logs.
- `scope-creep`: worked as designed by exposing the 76-file C7 list. The list includes bulk document maintenance and earlier plan files, so visibility worked even though the retrospective must still judge attribution.
- `device-failed`, cost-regex self-check: the actual price parser worked. Its “seen” sentinel fired once on quoted prose; there is not evidence that such false alerts are routinely bypassed.

VIOLATION: repeated-failure-class | loss_min=10 | loss_usd=? | evidence=tools/bench/drive_original_copy_v2.log:62
VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=unreported-fact-runner-exit@tools/bench/diag_stop_condterm_panel.log:18

## Sources

(extract from answer)

## What was done with it

Written 2026-09-17 by the material session running cycle 15's D1 build, which `guard_peer.py` blocked until this
section existed. Per finding: accepted and where it landed, or escalated with the reason. Nothing is refuted.

| finding | disposition |
|---|---|
| **1. Repeated failure** — D0 attempt 3 repeated its own bandpass failure internally instead of switching to the foreground/HWND probe at run 1 P6 | **ACCEPTED.** Counted as `repeated-failure-class`, loss 10 min; its device was already decided (`docs/violation-decisions.md`, 2026-09-16 15:05 — the disposition gate in `guard_peer.py`, i.e. the gate that forced *this* section). The slug is not at threshold, so no new device is owed. |
| **2. Missing tool** — after the SECOND stop-terminal failure the reader was the required next build | **ACCEPTED, and it was built:** `OpLoopEndRef_v0` (`WhileLoop.Loop End Ref` 6362C00), 16 pass / 0 fail, `tools/bench/build_oploopendref_v0.log`; it resolved `#637` → terminal 648 ← wire 3457 ← `#11639`, which is now D1's S4 gate. Closed by the artefact, not by a promise. |
| **3. Unmeasured step** — D0 v3's R11 scored the RESTART, not the stop, so "the stop works" is unproven | **ACCEPTED.** Carried as STATUS OPEN 17b and written into the plan's F2 gate (*"F2 gates on the stop itself, not on the fact that a restart succeeded afterwards"*). Stays open because D1 is not built. |
| **4. Rule compliance** — the material failure budget was not honoured inside D0 v2 (run 2 repeated run 1's failed path); plus four audit blind spots (A4 day-granularity, C6, A6's "n-a" GUI line, C4b's false positive) | **ACCEPTED.** The budget breach is the same `repeated-failure-class` count as finding 1. The four audit gaps are **ESCALATED to judgement**: each changes `tools/audit_cycle.py`'s own measurements, and a material session patching the auditor that judges it is precisely finding 7's fault. |
| **5. Ordering** — defensible except the in-flight gate hole: `priorart_cycle14.log` never recorded an end, yet another prior-art dispatch began 95 min later | **ACCEPTED.** `guard_cycle.py` now refuses a recipe build while any `tools/bench/priorart_*.log` lacks a `BGRUN END|TIMEOUT` line (device (a) of the `premature-build` decision, 2026-09-16 19:16). That covers **builds**; it does **not** cover a second *dispatch* — escalated. |
| **6. Understated summary** — R11's invalid frozen-counter predicate, the 60 s abort, the 2,041 TIFFs / 2,675,689,770 B | **ACCEPTED and already surfaced:** STATUS OPEN 18 carries the TIFF rate as **measured ≈122 MB/s**, and that is what corrected the D1 plan's F1 arithmetic (60 s ≈ **7.3 GB**, not 4 GB — rev-4 review A4). |
| **7. Judgement inside a material session** — the D0 and D1 prior-art dispositions had material sessions accept findings, rewrite a plan and change cycle direction | **ACCEPTED, and it binds this session.** Applied here: only the **mechanical** halves of the two prior-art reviews were acted on (a census scope, a walk cache, four documentation corrections of measured facts); every finding that changes the design was escalated unchanged — the move table (rev4c A3), the transport's drop-new defect (rev4b A3), the op freeze (rev4c A2). `judgement-in-material` stands at 3 with its device recorded (`docs/violation-decisions.md`, 2026-09-16 21:07). |

**Device effect, as reported:** two device failures — the `unreported-fact` runner-exit device (an internal failed
gate still exited rc 0) and the `repeated-failure-class` disposition gate at its in-flight edge. Both already
answered in `docs/violation-decisions.md`; `py tools/violations.py` reports **0 slugs awaiting a response**, so no
new device was owed at this cycle's close.
