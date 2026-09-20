# retrospective-cycle15-routeb

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (364s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 15 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-17 07:10:02  ..  2026-09-17 13:32:51   (383 min)
    basis: start = archive/peer/2026-09-17-retrospective-cycle14.md mtime (cycle 14 closed there; a plan mtime lags the work - see the docstring); end = 2026-09-17-retrospective-cycle15.md mtime - 253s (its dispatch)
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

== cycle audit, 2026-09-17 07:10 .. 2026-09-17 13:32 (383 min, an explicit cycle window): 33 build logs, 25 peer logs, 59 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 33/33 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 20 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 45/59 annotated; blank: ['2026-09-17-d0-bandpass-click-was-delivered-hwnd-token.md', '2026-09-17-d0-bandpass-hwnd-token-agy.md', '2026-09-17-d1-s1-diagram-count.md', '2026-09-17-d1-s1-stale-in-memory-copy.md', '2026-09-17-d1-s3-stale-traverse-index.md', '2026-09-17-d1-s3b-uid-reuse-after-delete.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1774 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 37, failure markers 60, logs carrying a failure 20
  C2 peer reviews dispatched 25, archived 59
  C3 wall-clock inside bgrun, BUILDS ONLY 68 min 37 s
  C4 wall-clock inside bgrun, REVIEWS 179 min 47 s; cost $49.3391 from 10 log(s) that report one
  C4b cost lines seen 10 / parsed 10
  C5 total wall-clock 248 min 24 s  (reviews are 72% of it)

  C6 material-marked recipe/bench runs 52, judgement-session attempts refused 2  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs\cycle15-plan.md: 22 - docs/vi-server-ids.json, tools/audit_cycle.py, tools/bench/d1_rewire_map.py, tools/bench/diag_connectnested_donors.py, tools/bench/diag_connectnested_v1_facts.py, tools/bench/diag_create_const_equal.py, tools/bench/diag_exitwhile_front.py, tools/bench/diag_filewrite_donor.py, tools/bench/diag_savetrace_376.py, tools/bench/diag_true_original_tiff.py, tools/bench/plan_connectnested_v1.md, tools/bench/selftest_guard_cycle_fixed.py??


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 274/390 ok; 116 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 611 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 11 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:127 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle15-plan.md'] current
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 144 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:901']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (33; read them directly, they are the primary record) ===
tools/bench/bench_prep_restart.log  (2026-09-17 13:19:22)
tools/bench/build_d1_v0.log  (2026-09-17 07:13:18)
tools/bench/build_d1_v0_run2.log  (2026-09-17 07:16:43)
tools/bench/build_d1_v0_run3.log  (2026-09-17 07:21:00)
tools/bench/build_d1_v0_run4.log  (2026-09-17 07:25:54)
tools/bench/build_d1_v0_run5.log  (2026-09-17 08:18:35)
tools/bench/build_d1_v0_run6.log  (2026-09-17 09:57:12)
tools/bench/build_d1_v0_run7.log  (2026-09-17 10:58:33)
tools/bench/build_opconnectnested_v0.log  (2026-09-17 11:55:04)
tools/bench/build_opconnectnested_v0_run1.log  (2026-09-17 11:24:37)
tools/bench/build_opcreateconstonterm_v0.log  (2026-09-17 10:47:39)
tools/bench/build_opsentinel_ops.log  (2026-09-17 09:45:13)
tools/bench/build_opsentinel_ops_run2.log  (2026-09-17 09:49:29)
tools/bench/build_opsentinel_ops_run3.log  (2026-09-17 09:52:18)
tools/bench/build_opstopfromnode_v0.log  (2026-09-17 08:04:50)
tools/bench/build_opstopfromnode_v0_run2.log  (2026-09-17 08:15:39)
tools/bench/build_opstopfromnode_v0_run3.log  (2026-09-17 08:17:20)
tools/bench/diag_connectnested_donors.log  (2026-09-17 11:10:47)
tools/bench/diag_connectnested_v1_facts.log  (2026-09-17 13:20:40)
tools/bench/diag_create_const_equal.log  (2026-09-17 09:34:53)
tools/bench/diag_d1_full_route.log  (2026-09-17 09:59:07)
tools/bench/diag_d1_full_route_run2.log  (2026-09-17 10:27:55)
tools/bench/diag_exitwhile_front.log  (2026-09-17 07:41:42)
tools/bench/diag_filewrite_donor.log  (2026-09-17 07:39:46)
tools/bench/diag_filewrite_donor2.log  (2026-09-17 07:40:14)
tools/bench/diag_loopendref_front.log  (2026-09-17 07:45:35)
tools/bench/diag_savetrace_376.log  (2026-09-17 07:52:38)
tools/bench/diag_true_original_tiff.log  (2026-09-17 09:52:59)
tools/bench/prep_run8.log  (2026-09-17 11:09:05)
tools/bench/prep_run8b.log  (2026-09-17 12:01:58)
tools/bench/test_opconnectnested_v0.log  (2026-09-17 12:02:09)
tools/bench/test_opconnectnested_v1.log  (2026-09-17 12:06:37)
tools/bench/test_run_poison.log  (2026-09-17 12:21:41)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (25) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/outcome_review.log  (2026-09-17 10:13:00)
tools/bench/peer_connectnested_stall.log  (2026-09-17 11:56:51)
tools/bench/peer_connectnested_stall2.log  (2026-09-17 11:57:16)
tools/bench/peer_connectnested_stall3.log  (2026-09-17 12:00:01)
tools/bench/peer_connectnested_t2b.log  (2026-09-17 12:04:28)
tools/bench/peer_d1_s1_diagram_count.log  (2026-09-17 07:15:36)
tools/bench/peer_d1_s1_stale_memory.log  (2026-09-17 07:23:00)
tools/bench/peer_d1_s3_stale_index.log  (2026-09-17 07:20:30)
tools/bench/peer_d1_uid_reuse.log  (2026-09-17 07:28:21)
tools/bench/peer_nesteddiag.log  (2026-09-17 12:20:44)
tools/bench/priorart_connect_nested.log  (2026-09-17 11:17:10)
tools/bench/priorart_connectnested_v1.log  (2026-09-17 13:27:12)
tools/bench/priorart_createconst-term.log  (2026-09-17 10:43:50)
tools/bench/priorart_d1-full-route-rev2.log  (2026-09-17 09:03:53)
tools/bench/priorart_d1-full-route-rev3.log  (2026-09-17 09:17:39)
tools/bench/priorart_d1-full-route.log  (2026-09-17 08:46:43)
tools/bench/priorart_d1-op-exitwhile-node.log  (2026-09-17 07:43:55)
tools/bench/priorart_d1-op-stopfromnode.log  (2026-09-17 07:59:40)
tools/bench/priorart_d1-op-streamwrite.log  (2026-09-17 07:43:42)
tools/bench/priorart_d1-sentinel-ops.log  (2026-09-17 09:37:15)
tools/bench/retro_cycle15.log  (2026-09-17 07:12:48)
tools/bench/retro_cycle15_d1build3.log  (2026-09-17 10:05:56)
tools/bench/retro_cycle16.log  (2026-09-17 08:09:46)
tools/bench/retro_cycle16b.log  (2026-09-17 08:13:45)
tools/bench/stall_pid2832_112502.log  (2026-09-17 11:46:50)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle15-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

## Verdict

The costliest structural fault was continuing the `OpConnectNested` material work after its two-attempt failure budget was exhausted.

Attempt 1 produced no runnable route (`tools/bench/build_opconnectnested_v0_run1.log:41-66`). Attempt 2 then failed its functional test and remained blocked until the 30-minute process deadline (`tools/bench/build_opconnectnested_v0.log:120-134`). The required adversarial review finished around 12:00 (`tools/bench/peer_connectnested_stall3.log:1-42`), which was the point to stop and hand the unresolved timeout-versus-design choice to judgement. Instead, material performed two more failed tests, diagnosed the shared COM timeout layer, ran another reader, and bought another prior-art review.

Counterfactual: had the session handed off after attempt 2’s review at 12:00, this material cycle would have ended around 12:00 instead of 13:32—93 minutes earlier. The priced post-boundary review cost was $5.1763 (`tools/bench/priorart_connectnested_v1.log:5-6`).

A failure-visibility device also failed, mandating the second verdict below: `diag_connectnested_v1_facts` measured the alleged named source as `None`, immediately marked the condition PASS, and ended `rc=0` (`tools/bench/diag_connectnested_v1_facts.log:29-30,62-63`). The gate was literally hard-coded true (`tools/bench/diag_connectnested_v1_facts.py:131-138`). The later prior-art review caught this before construction, so its measured time loss is zero and no dollar figure can be attributed.

## Findings

1. **Repeated failure.** The `OpConnectNested` sequence had four attempts:

   - Attempt 1: route A and fallback B both left `ExecState 0` (`build_opconnectnested_v0_run1.log:41-66`).
   - Attempt 2: the functional test failed, then the client timed out after 1,801 seconds (`build_opconnectnested_v0.log:120-134`).
   - Attempt 3: the isolated v0 test still failed compilation (`test_opconnectnested_v0.log:11-17,37-38`).
   - Attempt 4: even a prevalidated, type-compatible test changed `ExecState 1 → 0` (`test_opconnectnested_v1.log:20-27,43-44`).

   The approach should have changed after attempt 2: hand the timeout/design fork to judgement, then authorize one discriminating experiment. This also repeated an earlier cycle-window breach already identified at D1 attempt 3: the session-wide budget had been reinterpreted as “two per micro-class” (`archive/peer/2026-09-17-retrospective-cycle15-d1-build3.md:182-186`).

2. **Missing tool.** `VI.Get Errors` remained unbuilt despite being the named reader for unexplained broken-VI states (`CLAUDE.md:321-328`). It would have replaced inference around:

   - `OpStopFromNode` remaining broken after the conditional terminal was wired (`build_opstopfromnode_v0_run3.log:55-56`);
   - the sentinel scratch’s `ExecState 0` (`build_opsentinel_ops.log:31-44`);
   - `OpConnectNested` producing a present wire while changing `ExecState 1 → 0` (`test_opconnectnested_v1.log:22-27`).

   The material cycle was frozen against silently adding another general-purpose op, so the correct response was to request a judgement decision—not continue explaining broken states indirectly.

3. **Unmeasured steps.** The clearest false measurement was D2: the source walk returned no node, label, terminal, or panel object, but the gate passed “source is NAMED” (`diag_connectnested_v1_facts.log:28-30`). A cheap Boolean check of the values already in memory was available; instead, line 136 passed literal `True` (`diag_connectnested_v1_facts.py:131-138`). Separately, `OpWireSource_v5` failed its published control with error 1055 across every queried wire, and the run correctly marked its conclusions invalid (`diag_d1_full_route_run2.log:27-66`); that disciplined handling contrasts directly with D2.

4. **Rule compliance.**

   - Broken: the session-wide failure budget of two (`CLAUDE.md:250-254`).
   - Broken: decisions reserved for judgement were made in material sessions (`CLAUDE.md:246-274`).
   - Formally failed: A4 reported six blank dispositions. At least some are parser-visible empty duplicate headings followed by real dispositions—for example `d1-s1-diagram-count.md:55-66` and `d1-s1-stale-in-memory-copy.md:57-79`. Thus the archival format violated the mechanical contract even where prose disposition existed.
   - Satisfied: all supplied build runs were bounded; failed gates ended nonzero or timed out, and the original checksum remained unchanged—for example `build_d1_v0_run7.log:354-356,400-401`.
   - No GUI or hardware action appears in the build record.

   The audit does not evaluate semantic failure-budget compliance, decisions embedded in material dispositions, hard-coded false-positive gates, whether C7 changes were justified, or individual `BGRUN START` records when multiple invocations share one log. A4 is also day-scoped rather than limited to the stated window.

5. **Ordering.** Initial measurement and prior-art-before-build ordering was defensible. It ceased being defensible after the second `OpConnectNested` attempt. Judgement or the broken-VI reader should have preceded attempts 3–4, the nested-terminal research, the shared timeout-tool experiment, and the v1 plan review. The later review itself concluded that one proposed reader inherited an already-failing `OpWireSource_v5` chain (`archive/peer/2026-09-17-priorart-connectnested-v1.md:338-350`).

6. **What was not reported.** The raw D1 run did not merely have a few unfinished wires: only 35 of 66 attempted routes succeeded, seven failed, and 24 had no route (`build_d1_v0_run7.log:326-328`). Stage 2 was entirely skipped, `ExecState` remained zero, and the working copy was deleted rather than delivered (`:342-355`). Thus the cycle ended with no runnable D1.

   The apparently successful v1 facts report also concealed the `None → PASS` contradiction above. Cost-wise, the three successive full-route prior-art rounds alone consumed 1,812 seconds and $18.4911 (`priorart_d1-full-route.log:3-4`; `priorart_d1-full-route-rev2.log:3-4`; `priorart_d1-full-route-rev3.log:3-4`).

7. **Judgement inside material.** Yes. The material disposition accepted a new timeout mechanism as its working hypothesis, classified it as a shared-tool defect, changed the test strategy, and armed a new experiment (`archive/peer/2026-09-17-connectnested-stall.md:117-145`). Another material disposition accepted all six prior-art findings and changed the donor, input signature, and test contract (`archive/peer/2026-09-17-priorart-connect-nested.md:329-339`). Those are design and explanation choices explicitly reserved for judgement.

## Device effect

- **Runner exit propagation:** failed on the hard-coded D2 false pass: `None` was scored PASS and the batch ended `rc=0` (`diag_connectnested_v1_facts.log:29-30,62-63`).
- **Confirm-bait refusal:** worked; the mandatory adversarial instructions appear in the review (`archive/peer/2026-09-17-connectnested-stall.md:62-68`).
- **Prior-art review:** worked, albeit late; it found existing two-cast donors, an already-failing dependency, and the insufficient wire-UID gate (`archive/peer/2026-09-17-priorart-connectnested-v1.md:338-373`).
- **Undisposed-review gate:** no demonstrated bypass. The A4 blanks concern duplicate/ordinary hypothesis-review headings rather than an undisposed prior-art or retrospective followed by another same-kind dispatch.
- **Split build/review cost reporting:** worked; the audit found and parsed all ten price lines.
- **Premature-build guard:** worked. The corresponding prior-art reviews completed before the sentinel, constant, and nested-connect recipes began (`priorart_d1-sentinel-ops.log:1-4`; `build_opsentinel_ops.log:1`; `priorart_createconst-term.log:1-6`; `build_opcreateconstonterm_v0.log:1`; `priorart_connect_nested.log:3-6,103`; `build_opconnectnested_v0.log:1`).
- **Scope counter:** worked by exposing the 22 out-of-plan changes. It is intentionally observational, so a nonzero list is not itself device failure.
- **Cost-regex repair:** worked; all ten observed cost lines were parsed.
- **Inner-failure scan:** worked for actual failure markers: representative failed runs ended `rc=1`, and the stalled run ended TIMEOUT (`build_d1_v0_run7.log:400-401`; `build_opconnectnested_v0.log:128-134`).
- **`OpLoopEndRef_v0`:** worked for its intended question. The original loop’s terminal and source were measured directly as terminal 648, wire 3457, source `#11639` (`build_d1_v0_run7.log:334-338`). The 1055 errors concern newly created loops, not renewed guessing about original loop `#637`.

VIOLATION: repeated-failure-class | loss_min=93 | loss_usd=5.1763 | evidence=tools/bench/build_opconnectnested_v0.log:134
VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=unreported-fact-runner-exit@tools/bench/diag_connectnested_v1_facts.log:30

## Sources

(extract from answer)

## What was done with it

Dispatched because `guard_cycle.py` blocked route B's run 2 — the work done since the last retrospective had
spent the cycle budget. **It reviewed the WRONG WINDOW**, exactly as STATUS OPEN 31 says it does: every finding
is about the morning's `OpConnectNested` work, and none of it about the route-B session that triggered it (the
`build_d1_routeb_v0` run does not appear once). The cause is recorded: `retrospective.py:282-286` +
`guard_cycle.stamp()` = min(ctime, mtime). That is not a reason to discount the findings, which are sound about
the window they saw.

**`VIOLATION: repeated-failure-class | loss_min=93 | loss_usd=5.1763`** — accepted, and it is the same fault
this session is under a hard budget for. Taken as binding here: route B's build has had TWO runs, run 1 (84/2)
and run 2, and there is no third. Every remaining NO-ROUTE row is handed to judgement, not attempted again.

**`VIOLATION: device-failed | loss_min=0`** — accepted. `diag_connectnested_v1_facts.py:131-138` scored a
literal `True` and the runner exited `rc=0` on a measurement that had returned `None`. That threshold is 1.
It is already answered in `docs/violation-decisions.md` (2026-09-17 03:38), and this session's own gates are
written the opposite way: every gate in `build_d1_routeb_v0.py` and `diag_moved_structure_terminals.py` compares
a value the machine returned, and the from-tunnel path REFUSES rather than passes when the sink reads wrong
(`build_d1_routeb_v0.py:786-796`, `:640-657`) — a refusal cannot be hard-coded true.

Finding 2 (`VI.Get Errors` 452 still unbuilt) is confirmed again by this session and is carried to judgement
under OPEN, not answered here: building it is a new op, which a material session may not authorise.
