---
type: peer-review
status: historical
date: 2026-09-16
comparison: true
tags: [retrospective, v1-v2-comparison]
---

<!-- comparison: true — a RETROACTIVE re-review of a cycle already reviewed under v1, run only to measure v1
     against v2 (tools/bench/retro_v2_comparison.md). tools/violations.py SKIPS any archive carrying this flag,
     so cycles 11-13 are not counted twice. Flag-based, never name-based: a rename would silently re-enter the
     tally. Decided 2026-09-16 (OPEN-B of the comparison). -->

# retrospective-v2-cycle13

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (212s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 13 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-16 19:59:00  ..  2026-09-16 20:22:59   (24 min)
    basis: start = docs/cycle13-plan.md mtime; end = docs/cycle14-plan.md mtime
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

=== END YOUR ANSWER WITH MACHINE-READABLE LINES ===
One line per structural fault you named - normally ONE, at most two - in exactly this form:
  VIOLATION: <slug> | loss_min=<number> | loss_usd=<number or ?> | evidence=<file:line>
or, if the cycle had no structural fault:
  VIOLATION: none
Slugs: repeated-failure-class 쨌 tool-not-built 쨌 inference-over-measurement 쨌 rule-evaded 쨌 wrong-ordering 쨌 unreported-fact 쨌 scope-creep 쨌 premature-build 쨌 judgement-in-material 쨌 device-failed
Do not invent new slugs; map to the closest one and explain in the prose. `loss_min` is a whole number
of minutes. `loss_usd` is a number only when a log carries it, otherwise `?`. `evidence` is one
file:line that a reader can open.

=== COMPLIANCE AUDIT (tools/audit_cycle.py --from/--to, machine-generated) ===

== cycle audit, 2026-09-16 19:59 .. 2026-09-16 20:22 (24 min, an explicit cycle window): 2 build logs, 3 peer logs, 36 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 2/2 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 1 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 28/36 annotated; blank: ['2026-09-16-case-frame-identity-and-contents.md', '2026-09-16-case-frame-identity-retry.md', '2026-09-16-load-vs-editmode-23c-agy.md', '2026-09-16-load-vs-editmode-23c-retry.md', '2026-09-16-load-vs-editmode-23c.md', '2026-09-16-priorart-master-plan-rev3.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1730 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 2, failure markers 1, logs carrying a failure 1
  C2 peer reviews dispatched 3, archived 36
  C3 wall-clock inside bgrun, BUILDS ONLY 5 min 37 s
  C4 wall-clock inside bgrun, REVIEWS 5 min 42 s; no log reported a cost - treat the review cost as UNKNOWN, not as zero
  C5 total wall-clock 11 min 19 s  (reviews are 50% of it)

  C6 material-marked recipe/bench runs 2, judgement-session attempts refused 0

  C7 files modified in the window but NOT named in docs\cycle13-plan.md: 2 - tools/bench/diag_flatseq_diagrams_attach.py, tools/bench/retro_cycle13_runner.py

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (2; read them directly, they are the primary record) ===
tools/bench/diag_flatseq_diagrams_attach.log  (2026-09-16 20:10:37)
tools/bench/diag_hierarchy_a3.log  (2026-09-16 20:05:58)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (3) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/peer_flatseq_unreachable.log  (2026-09-16 20:09:01)
tools/bench/priorart_cycle14.log  (2026-09-16 20:21:06)
tools/bench/retro_cycle13.log  (2026-09-16 20:18:14)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle13-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

The one structural fault was wrong ordering: the FlatSequence-specific property lookup should have preceded attempt 1’s negative traversal sweep. That mistake triggered a false failed prediction and a 125-second review; the later 33-second census immediately found the correct accessor (`tools/bench/diag_flatseq_diagrams_attach.log:7-14`).

Loss is 2 minutes, rounded from the logged 125 seconds. No dollar amount was recorded (`tools/bench/peer_flatseq_unreachable.log:2`; the archive’s cost field is blank at `archive/peer/2026-09-16-flatseq-frame-unreachable.md:6`). Counterfactual: had the `FlatSequence.Diagrams[]` census run at attempt 1, around 20:00, the same necessary 33-second measurement would have occurred first and the 125-second corrective review would not have run; sequential downstream work could have ended around 20:21 instead of 20:23.

## Findings

1. Repeated failure

No failure class recurred inside the specified window. Attempt 1 failed once at B2, reaching 0/57 diagrams (`tools/bench/diag_hierarchy_a3.log:25-35`). The approach changed immediately after attempt 1 to the class-specific accessor, confirmed 5/5 (`tools/bench/diag_flatseq_diagrams_attach.log:7-27`).

The five historical `OpCaseFrames_v0` attempts were already recorded when the plan was written (`docs/cycle13-plan.md:88-100`); they predate 19:59 and must not be charged to this cycle.

2. Missing tool

`OpFlatSeqDiagrams_v0`—`FlatSequence → Diagrams[] → GObject.UID`—was absent. It would have resolved the remaining 57 frame diagrams and completed A3’s 170/170 hierarchy; cycle 14 consequently specifies exactly that op (`docs/cycle14-plan.md:27-32`).

This is a finding, not a separate structural fault: cycle 13 explicitly prohibited building a new op and contained a prewritten stop condition (`docs/cycle13-plan.md:32-37,98-100`). The session followed that stop rather than forgetting the reader.

3. Unmeasured steps

The session generalized from “our tested generic routes returned none” to “no traverse-class plus property route can reach these diagrams” (`archive/peer/2026-09-16-flatseq-frame-unreachable.md:14-19`). That was broader than the measurements at `tools/bench/diag_hierarchy_a3.log:25-36`.

A cheap measurement was available: the subsequent 33-second census found both `Diagrams[]` and `Frames[]` (`tools/bench/diag_flatseq_diagrams_attach.log:7-14`). This is part of the single ordering fault, not another violation.

4. Rule compliance

Broken or only formally satisfied:

- Mandatory external search occurred only after the universal negative was drafted. The rule specifically says to search before writing that a route is impossible (`CLAUDE.md:416-424`).
- Judgement/material separation was crossed; see finding 7 (`CLAUDE.md:228-255`).
- Cycle-14’s prior-art review began at 20:21:06 before the cycle-14 plan received its boundary mtime at 20:22:59 (`tools/bench/priorart_cycle14.log:1`). That is poor session/cycle separation under `CLAUDE.md:220-222`, although no completed cost or harmful result is available inside this window.
- C7 found two unplanned files. The recovery diagnostic is understandable, and the retrospective runner is cycle machinery; neither demonstrably changed the outcome enough to constitute scope creep.

Complied with:

- Both builds used `bgrun` and ended explicitly (`tools/bench/diag_hierarchy_a3.log:124`; `tools/bench/diag_flatseq_diagrams_attach.log:27`).
- The failed prediction received an answered adversarial review before recovery (`tools/bench/peer_flatseq_unreachable.log:1-4`).
- The main VI checksum remained unchanged (`tools/bench/diag_hierarchy_a3.log:121`).
- The scratch VI was deleted (`tools/bench/diag_flatseq_diagrams_attach.log:23-24`).
- No GUI or hardware activity is evidenced.
- The failure budget was respected.

The audit does not establish exact-window A4 compliance: it says explicitly that A4 is day-granular. Its blank reviews therefore cannot be attributed to 19:59–20:22. It also does not check review correctness, external-search timing, judgement inside a nominally material session, every original file, or whether A3’s 170/170 deliverable was completed.

5. Ordering

The 3a, 3c, and 3d measurements were defensible and useful. The FlatSequence branch was not: the class-specific lookup and 33-second attachment census should have been attempt 1, before generic negative traversal.

A second, smaller ordering concern is that `priorart_cycle14.log` started before the cycle-14 plan’s final mtime. Because that review has no end or cost line inside the window, the evidence does not support assigning it structural loss yet.

6. What was not reported

The current handoff is substantially more accurate than the first retrospective:

- It explicitly says A3 completed 112 clean diagrams and left 57 frames (`STATUS.md:87-90`).
- It preserves the limitation that 3c located where 1055 became observable, not where it originated (`tools/bench/diag_hierarchy_a3.log:64-65`).

What the earlier retrospective understated or misattributed is its own accounting. It charged a 591-second, $5.1239 prior-art review that occurred before the 19:59 boundary (`archive/peer/2026-09-16-retrospective-cycle13.md:191`). Within the exact window, builds were 5:37 and completed reviews were 5:42; review cost was unknown, not $5.1239. `priorart_cycle14.log` had only started by the cutoff and cannot yet be counted as completed review time.

7. Judgement inside a material session

Yes. After the failed measurement, the material trajectory:

- accepted the peer’s competing explanation;
- chose and ran the confirming diagnostic;
- selected the surviving interpretation for the documentation;
- deferred the new op as a judgement question.

Those decisions are recorded at `archive/peer/2026-09-16-flatseq-frame-unreachable.md:161-189`, while `CLAUDE.md:232-233` reserves accepting review findings and choosing between explanations for judgement sessions.

I am not promoting this to a second structural violation: no counterfactual shows that placing the same decision in a judgement session would have reduced cost or changed the produced evidence. It is a real rule-compliance finding, but not one with a defensible loss estimate.

## Device effect

None of the seven listed devices demonstrably failed:

- `unreported-fact`, exit propagation: worked. B2 failed at `diag_hierarchy_a3.log:34`, and the outer log correctly ended `rc=1` at line 124.
- `rule-evaded`, adversarial-review gate: worked. The prompt explicitly ordered an attack (`archive/peer/2026-09-16-flatseq-frame-unreachable.md:14-19`), and the answer opened by rejecting the claim (`tools/bench/peer_flatseq_unreachable.log:4`).
- `tool-not-built`, prior-art review: no applicable recipe build occurred. Cycle 13 deliberately stopped before a new op, while cycle 14 began its prior-art gate at `tools/bench/priorart_cycle14.log:1`.
- `repeated-failure-class`, disposition gate: no repeated in-window failure occurred. Attempt 1 was followed by an annotated review and changed approach (`archive/peer/2026-09-16-flatseq-frame-unreachable.md:161-189`).
- `unreported-fact`, build/review cost separation: worked. The attached audit separately reported C3 and C4, matching the implementation at `tools/audit_cycle.py:221-240`.
- `premature-build`: no recipe build occurred after the unfinished cycle-14 prior-art review; cycle 14 also records the recipe as blocked (`docs/cycle14-plan.md:15-23,43`).
- `scope-creep`: worked as designed. C7 surfaced both unplanned files; the device is a counter, not a refusal (`tools/audit_cycle.py:312`).

VIOLATION: wrong-ordering | loss_min=2 | loss_usd=? | evidence=tools/bench/peer_flatseq_unreachable.log:2

## Sources

(extract from answer)

## What was done with it

This is a **retroactive v2 comparison run**, not the cycle's live retrospective. Cycle 13's own
retrospective is `archive/peer/2026-09-16-retrospective-cycle13.md` (v1), and its findings were
disposed there. This archive exists because the user asked for v2 to be MEASURED against v1 before it is
adopted (2026-09-16): same cycle, same evidence, new question set and a cycle-boundary evidence window.

- dispatched by `tools/bench/retro_v2_compare_runner.py` under bgrun, run 212 s, outcome ANSWERED
- v1 fired 9 slugs on this cycle; this run's machine lines are reproduced verbatim below
- `VIOLATION: <slug> | loss_min=<number> | loss_usd=<number or ?> | evidence=<file:line>`
- `VIOLATION: none`
- `VIOLATION: wrong-ordering | loss_min=2 | loss_usd=? | evidence=tools/bench/peer_flatseq_unreachable.log:2`

**Disposition of the findings: `tools/bench/retro_v2_comparison.md`**, which is the artefact this run
was bought for. No verdict is accepted or rejected in this file - whether v2 replaces v1, and what to do
about `judgement-in-material`, are judgement calls and are left OPEN for the judgement session.
