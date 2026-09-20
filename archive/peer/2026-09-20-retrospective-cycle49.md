# retrospective-cycle49

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $3.9800  in 14 / out 29367 / cache-create 97318 / cache-read 565126  (432s, 13 turn(s))
- **date:** 2026-09-20 02:32:11
- **outcome:** ANSWERED (433s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 49 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-20 00:34:29  ..  2026-09-20 02:24:56   (110 min)
    basis: start = archive/peer/2026-09-20-retrospective-cycle48.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-20 00:34 .. 2026-09-20 02:24 (110 min, an explicit cycle window): 7 build logs, 4 peer logs, 3 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 7/7 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 0 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 3/3 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 7, failure markers 0, logs carrying a failure 0
  C2 peer reviews dispatched 4, archived 3
  C3 wall-clock inside bgrun, BUILDS ONLY 0 min 0 s
  C4 wall-clock inside bgrun, REVIEWS 16 min 12 s; cost $9.5416 from 2 log(s) that report one
  C4b cost lines seen 2 / parsed 2
  C5 total wall-clock 16 min 12 s  (reviews are 100% of it)

  C6 material-marked recipe/bench runs 1, judgement-session attempts refused 9  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 3 - STATUS.md, tools/bench/.stall_samples.txt, tools/hooks/material_marker.log


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 282/503 ok; 221 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 1 DANGLING of 1115 citations checked:
       STATUS.md:60 -> tools/bench/s2a_legality.json

  WARN  L2c plan documents cite files that do not exist yet: 16 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  WARN  L2b cited line numbers are in range: 1 citation(s) point past the end of the file: ['docs/NAMES.md:1022 -> docs/toolkit-capabilities.md:775 (file has 675 lines)']
  WARN  L3 STATUS.md stays one screen: STATUS.md:122 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 273 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:597', 'docs/NAMES.md:870', 'docs/NAMES.md:884', 'docs/NAMES.md:902', 'docs/NAMES.md:929']

AUDIT VIOLATIONS: L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (7; read them directly, they are the primary record) ===
tools/bench/c49_facts.log  (2026-09-20 01:38:56)
tools/bench/c49s3_astcheck.log  (2026-09-20 02:17:21)
tools/bench/c49s3_astcheck2.log  (2026-09-20 02:18:24)
tools/bench/c49s3_astcheck3.log  (2026-09-20 02:21:08)
tools/bench/c49s3_capscan.log  (2026-09-20 02:05:23)
tools/bench/c49s3_citecheck.log  (2026-09-20 02:19:04)
tools/bench/c49s3_md5.log  (2026-09-20 02:20:53)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (6) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_36.log  (2026-09-20 02:24:56)
tools/bench/cycle_runner.log  (2026-09-20 00:34:29)
tools/bench/cycle_runner_main_20260919b.log  (2026-09-20 00:34:29)
tools/bench/priorart_d1-s2-stage-r2.log  (2026-09-20 01:56:27)
tools/bench/priorart_d1_s2_stage.log  (2026-09-20 01:02:07)
tools/bench/retro.log  (2026-09-20 02:24:56)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle49-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

# Retrospective (v2) — cycle 49, 2026-09-20 00:34:29 .. 02:24:56

## Verdict first

This cycle was mostly run well: no LabVIEW touched, the ORIGINAL verified unchanged before and after (`tools/bench/c49_facts.log:2`), two prior-art rounds that found real launch-dooming defects, and a recipe converged to verified bytes (23/23 citation greps, `tools/bench/c49s3_citecheck.log`; AST OK, `c49s3_astcheck2.log`). But it has one structural fault, and it is the kind that hides rather than costs: **the cycle ended with its launch-release work done but never cashed, and then reported the opposite.** The round-2 review's stop record is unreleased (`tools/bench/stop_records.json:381` — `"released": null`), its `## What was done with it` section is still the literal placeholder `(Claude fills in)` (`archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1263`) — yet STATUS.md:78-79 states "Both prior-art reviews and the cycle-48 retrospective are DISPOSED", and the compliance audit's A4 rubber-stamped "3/3 annotated" against that placeholder.

**Why this changed how the cycle ended.** All five round-2 findings were actually implemented in pass 2 (recipe at sha `789a5c96…` by 02:21, `c49s3_md5.log`). Record 3 has no release stamp, so per the cycle's own measured mechanism (`archive/2026-09-20-status-cycle49-relocate.md` §2: an unreleased record is cleared by valid `FIXED:` lines; the hash re-arm only bites *after* a release is stamped), five `FIXED:` lines citing the recipe — a file changed after the 01:56 review, satisfying condition (b) — would have released the gate that night. Instead the cycle ended BLOCKED, and NEXT (STATUS.md:53) orders "FIRST ACT — ROUND-3 PRIOR-ART REVIEW" — a third paid round (~$4.4–5.2 by this cycle's own two COST lines) for bytes whose review debt was already payable with a file edit. Worse, the undisposed r2 is now the *newest* priorart review, which is exactly what `guard_peer.py:237-242` refuses new priorart dispatches over — the failure mode that cost runner-cycle 34 its entire cycle ($3.93, 11 min; cited at `archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1044-1046`). **Counterfactual:** had the five `FIXED:` lines been written at ~02:21, right after `c49s3_citecheck.log` verified the fixes, the cycle would have ended at ~02:30 RELEASED with `--phases A` launchable, instead of blocked with a redundant paid round and a guard trap scheduled as the next session's first act. No log carries a dollar figure for this specific fault, so the dollars stay honest-unknown.

I considered a second fault and rejected it — see finding 6(c).

## FINDINGS

**1. Repeated failure.** Yes: the launch-gate release mechanics were mishandled twice in one cycle, in mirror image. Attempt 1 (01:24 local): the session wrote the eight round-1 `FIXED:` lines *before* finishing the recipe edit, stamping `released.sha256 3be69ba5…` (`stop_records.json:362-363`) against bytes that then kept changing to `71f12e…`, so the launch at ~01:3x was refused (`archive/2026-09-20-status-cycle49-relocate.md` §2, verbatim refusal). Attempt 2 (02:21): the edits were finished first — correct lesson learned — but the release was then never written at all (`…-r2.md:1263`). The approach should have changed at attempt 2: the mechanism note in relocate §2 was already on disk by then; "edit fully, release last" was the known fix, and only its second half was executed. A smaller recurring class: the judgement session retried guard-refused commands in syntactic variants (the same facts-script dispatch attempted three ways — `cycle_36.log:61`, permission_denials `toolu_01NXi…`/`toolu_01Xfr…`/`toolu_015hUL…`), burning expensive-model turns on refusals the first denial already predicted.

**2. Missing tool.** A cycle-close release-status check. The facts script already dumps the stop-record store (`c49_facts.log:7-8`) but ran only at 01:38, before pass 2; nothing re-read the store or the review file's disposition section at close. A ten-line "is the gate released and is the newest review disposed" op, run before STATUS is rewritten, would have contradicted the "DISPOSED" sentence and prompted the five missing `FIXED:` lines.

**3. Unmeasured steps.** Mostly exemplary — the cycle re-measured where it mattered (the `_grep` 400-char truncation was caught by measurement, `c49s3_capscan.log`; citations verified by grep, not memory). The one inference: NEXT's premise that round 3 is *required* was carried over from record 2's stamped-release mechanics to record 3, where `released: null` means `FIXED:` suffices — decided by inference when `py tools/stop_record.py check …` after pass 2 was free and would have measured it.

**4. Rule compliance.** Rule 4's STATUS cap satisfied only formally: two relocations in-window, yet STATUS sat at 122 lines at audit time (L3 WARN). L2 FAIL is real: STATUS.md:60 cites `tools/bench/s2a_legality.json`, which does not exist — a forward reference written as a citation. §3.3's judgement/material split held mechanically (7 subagents did the material work) but with heavy friction: the audit's C6 counts 9 refused judgement-session attempts, and `cycle_36.log:61` records 40+ permission denials. What the audit does NOT cover: (a) judgement-session spend — C5 declares "total wall-clock 16 min 12 s" and $9.54, while the session itself cost **$61.07** over 110 minutes (`cycle_36.log:61`, `total_cost_usd`), a ~7× understatement of the cycle's real cost (the standing C4 caveat, retrospective-cycle31 F4); (b) A4's annotation check, which passed a review whose disposition section is a placeholder — it evidently matches quoted "What was done with it" text earlier in the file (`…-r2.md:59-61`) rather than the real terminal section; (c) the window's plan mismatch — the audit judges scope against `docs/cycle27-plan.md` while this task names `docs/cycle49-plan.md`, which does not exist.

**5. Ordering.** The macro-order was right and cheap-first: facts before dispatch, prior-art before any launch attempt, all LabVIEW work refused rather than forced. The two micro-ordering errors are the release-vs-edit sequences already counted under finding 1; I do not double-count them as a separate fault.

**6. What was not reported.** (a) The $61.07 session cost appears nowhere in STATUS or the summary; the audit's $9.54 is what a reader sees. (b) STATUS.md:78-79's "Both prior-art reviews … are DISPOSED" is false for r2 — this is the violation. (c) The session's closing summary says the premature release "cost the launch and a second $5.15 review round" (`cycle_36.log:61`) — that overstates its own error's cost: round 2's A3 finding proves a launch of the `71f12e…` bytes would have ended `rc=1` on the mis-regexed A3-complete gate (`tools/bench/priorart_d1-s2-stage-r2.log:70-81`), so the gate refusal likely *saved* a doomed LabVIEW run plus a mandatory failed-prediction review; the $5.15 bought findings a live failure would have cost more to learn. This is also why I did not slug the premature release as a second structural fault: its counterfactual does not end the cycle better. (d) The 40+ guard denials and retry loops are absent from the summary.

**7. Judgement inside a material session.** One borderline instance: the material pass-2 record (`STATUS.md:22`, `owner_c49s3`) shows the material session redesigning gate structure — "C6 is now C6s+C6/C6w+C8 FATAL ExecState 1 before the save" — and ruling that "the six added ops are all READERS/CREATORS, so 32(d) rule (1) still has no winner and `stop_after_a` stands." Applying 32(d)'s selection rule mechanically is delegation-legal; adding a new FATAL gate (C8) is a design change, which belongs to judgement unless Pre-decided 33's A5 explicitly specified it — STATUS credits "Pre-decided 33's A5" for part of the pass, so I record this as a borderline finding, not a fault. The 9 refused judgement-session attempts (audit C6) show the inverse leak was tried and mechanically stopped.

## DEVICE EFFECT

- **stop record + launch gate** (2026-09-18): fired twice, correctly, and was not worked around — it refused the ~01:3x launch of edited bytes (relocate §2) and round 2 then proved those bytes would have failed `rc=1` (`priorart_d1-s2-stage-r2.log:70-81`). This device *worked*, and arguably paid for itself this cycle. Not failed.
- **premature-build guard** (`guard_cycle.py`): passed appropriately once a priorart log had END and a newer priorart archive existed; no wrong firing seen. Not failed.
- **repeated-failure-class / disposition gate** (`guard_peer.py` empty-"What was done with it" refusal): had no trigger inside the window (no priorart dispatch occurred after r2 landed at 01:56; the 02:24 retrospective dispatch is gated on the newest *retrospective* review, which is disposed). Not failed in-window — but this cycle left it armed against the next session's own first act, and its audit-side twin A4 was fooled by quoted text into "3/3 annotated" (`…-r2.md:1263` vs the audit's A4 PASS). A4 is not on the device list, so per the list this is charged to the violation above rather than as a device failure; if A4's parser is not repaired it will keep certifying undisposed reviews.
- **unreported-fact rc-masking fix, C3/C4 cost split, cost-regex self-test, bgrun FAIL-scan, C7 scope list**: all behaved — C4b parsed 2/2 cost lines and they sum exactly to C4's $9.5416; no rc=0-over-inner-failure instance appears in the seven build logs (all genuinely rc=0); review-log FAIL text was correctly not read as build failure; C7 produced its 3-file list. Not failed.
- **rule-evaded confirm-bait gate, prior-art tool, OpLoopEndRef_v0 reader**: no in-window trigger or use; nothing to score.

No listed device failed inside this window, so no device-failed line is emitted.

---

VIOLATION: unreported-fact | loss_min=10 | loss_usd=? | evidence=archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1263

## Sources

(extract from answer)

## What was done with it

DISPOSED by the cycle-50 judgement session, 2026-09-20. `VIOLATION: unreported-fact` is ACCEPTED in full, and so
is every prose finding. What changed as a result:
- Findings 1 / 1b / 6b (the launch gate released twice wrongly; "both prior-art reviews are DISPOSED" was false for
  r2; guard-refused commands retried in three syntactic variants): this cycle disposed r2 before dispatching
  anything, and `docs/cycle27-plan.md` Pre-decided 34(i) retires `tools/recipes/stage_d1_s2.py` instead of re-arming
  its bytes for a third paid prior-art round. The gate is no longer in the cycle's critical path at all.
- Finding 3 (NEXT's "round 3 is required" was inferred, not measured): accepted, and it is the reason this cycle
  measured the gate state with `tools/hooks/guard_cycle.py` / `guard_peer.py` / `tools/stop_record.py` read directly
  before planning around them.
- Finding 4 (STATUS 122 lines; the dangling cite to `tools/bench/s2a_legality.json`): fixed in this cycle's STATUS
  rewrite — that file was never created, so the citation is removed rather than left pointing at nothing.
- Findings 4b / 6a / 6c / 6d (the $61.07 judgement-session spend appears nowhere; `audit_cycle` C4 understates it
  ~7x; 40+ guard denials unreported): the spend line is carried into STATUS for the user, who is the only one who
  can act on it. Already an OPEN item; now it has its number.
- Finding 4c (A4's "3/3 annotated" was fooled by quoted text) and finding 2 (no cycle-close "gate released / newest
  review disposed" check): both name a mechanical device. The user's standing order of 2026-09-18 08:53 forbids
  building one, so each is recorded as a FINDING in `docs/violation-decisions.md` and nothing is built.
- Finding 7 (borderline judgement-in-material: material pass 2 added a new FATAL gate C8): ACCEPTED as a real
  instance, not a borderline one. A new fatal gate is a design change. It is why Pre-decided 34 was written by the
  judgement session itself and why the recipe was retired rather than handed back for another edit.
- Finding 5 and the DEVICE EFFECT section: no action — macro-order was right and no listed device failed in window.
