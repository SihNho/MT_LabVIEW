# retrospective-cycle60

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $3.3017  in 12 / out 21098 / cache-create 90823 / cache-read 430234  (320s, 17 turn(s))
- **date:** 2026-09-21 21:52:58
- **outcome:** ANSWERED (322s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 60 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-21 20:22:20  ..  2026-09-21 21:47:34   (85 min)
    basis: start = archive/peer/2026-09-21-retrospective-cycle53.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-21 20:22 .. 2026-09-21 21:47 (85 min, an explicit cycle window): 4 build logs, 7 peer logs, 40 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 4/4 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 2 logs recorded a failure; unreviewed: none
  PASS  A4 every archived review says what was done with it: 40/40 annotated
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 5, failure markers 3, logs carrying a failure 2
  C2 peer reviews dispatched 7, archived 40
  C3 wall-clock inside bgrun, BUILDS ONLY 3 min 36 s
  C4 wall-clock inside bgrun, REVIEWS 113 min 22 s; cost $52.7455 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C5 total wall-clock 116 min 58 s  (reviews are 96% of it)

  C6 material-marked recipe/bench runs 17, judgement-session attempts refused 3  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 4 - tools/bench/.stall_samples.txt, tools/bench/next_snapshot.md5, tools/cycle_prompt.md, tools/hooks/material_marker.log


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 282/569 ok; 287 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 1487 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 16 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 62 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 353 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:391', 'docs/NAMES.md:530', 'docs/NAMES.md:652', 'docs/NAMES.md:925', 'docs/NAMES.md:939']

AUDIT PASS


=== BUILD LOGS INSIDE THE WINDOW (4; read them directly, they are the primary record) ===
tools/bench/build_d1_m3a1.log  (2026-09-21 21:23:46)
tools/bench/c68_astcheck.log  (2026-09-21 20:37:22)
tools/bench/c68_pins.log  (2026-09-21 20:38:04)
tools/bench/c69_astcheck.log  (2026-09-21 21:17:46)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (7) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_54.log  (2026-09-21 20:46:19)
tools/bench/cycle_55.log  (2026-09-21 21:47:34)
tools/bench/cycle_runner.log  (2026-09-21 20:47:31)
tools/bench/cycle_runner_main_20260921d.log  (2026-09-21 20:46:19)
tools/bench/peer_c69_border.log  (2026-09-21 21:38:17)
tools/bench/priorart_c68_m3a1.log  (2026-09-21 21:01:08)
tools/bench/retro.log  (2026-09-21 21:47:34)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

All evidence is in hand. Here is the outcome review of cycle 60.

---

## VERDICT SUMMARY

This cycle earned its cost. It produced the project's first genuine product in several cycles: the only NO-ROUTE row was actually written (`tools/bench/build_d1_m3a1.log:473` region, sink terminals 6→7, op error empty), the A4 bare-sink gate caught a silent rule-1a consumer drop on its first firing (`build_d1_m3a1.log:551-552`), and a hypothesis review correctly demolished the cycle's own acceptance test before anyone believed it (`archive/peer/2026-09-21-c69-border-wiredelta.md:70` — "the acceptance line quotes an input argument as if it were an observation"). One structural fault, named at the end: the known, deliberately-unrepaired dispatch-lifecycle failure class recurred and cost roughly 15 of the window's 85 minutes.

Window caveat honored: `tools/bench/cycle_54.log` ($15.2384, line 62; END 20:46:19) is the *previous* judgement session's tail landing inside this window. Its cost belongs to the prior cycle and is not charged here, but its final act — a prior-art dispatch at 20:46:00 killed 19 seconds later by its own session exit — is charged here, because this cycle paid to redo it.

## FINDINGS

**1. Repeated failure — yes, one class, many instances: launching a guarded command in a form the guard refuses, and dispatching a child a dying turn then kills.** Instances inside the window: (a) `tools/bench/priorart_c68_m3a1.log:1` — BGRUN START 20:46:00 with no END or TIMEOUT line ever written; the parent session ended at 20:46:19 (`cycle_54.log:63`) and killed it, the *second* kill of this same review (commit 438b973 records the first); re-dispatched 20:54:39 (`priorart_c68_m3a1.log:3`). (b) Six launch attempts for the c68 astcheck, 20:36:12–20:37:22, using the dead `MATERIAL=1` prefix (`tools/hooks/material_marker.log:851-856`). (c) Eight more attempts of the *same wrong form* for the c69 astcheck, 21:13:00–21:17:29 (`material_marker.log:861-868`), succeeding only at 21:17:46 with `--material` (`:869`). The approach should have changed on **attempt 2 of the c68 round (20:36:43)**: the correct `--material` form had been used successfully by the same machinery 30 minutes earlier (`material_marker.log:848-850`), and `guard_bash.py:99-104` states the fix in its refusal. Instead the identical mistake was re-typed eight more times at 21:13.

**2. Missing tool — yes: the OPEN 54(b) repair, "named, deliberately NOT BUILT" (STATUS.md:47).** A dispatch wrapper that survives the dispatching turn's end (or a hook that refuses a background dispatch as a session's final act) would have prevented both kills of the prior-art review and the hand-rolled `until grep BGRUN END; sleep 10` wait loops that were themselves denied (`cycle_55.log:62`, denial entries toolu_01KGfdnf, toolu_016XVWCb). The project has now paid for this absence at least three times and has twice written it down instead of building it.

**3. Unmeasured steps — one, serious, and caught in-cycle.** The build's border acceptance test asserted "SOURCE-side wire 9649" without any post-write read of wire 9649 — the value was the input argument, last measured *before* the write (`c69-border-wiredelta.md:70`, quoting `build_d1_m3a1.log:488`). The discriminating measurement (`OpWireSource_v5` re-walk, ~0.2 s, already built) was available and not run. The reviewer also spotted an unexamined measurement sitting in the log: the junk node minted *carrying uid 9649* (`build_d1_m3a1.log:475` per the review at `c69-border-wiredelta.md:78-81`), which nobody looked at. Both are now Pre-decided 70/71. Inference-over-measurement occurred, but the cycle's own review layer caught it before acceptance — so it is a finding, not the top fault.

**4. Rule compliance.** The audit passes and mostly deserves to. Broken or bent: the judgement session attempted material work 3 times and was refused (audit C6) — the delegation split held only because the hook held; a `python - <<'EOF'` multi-line heredoc was attempted (denial toolu_01AyvH5v in `cycle_55.log:62`; `material_marker.log:859` REFUSED) against the heredoc rule, read-only so borderline; and CLAUDE.md's "hold the turn open until BGRUN lands" was broken by the 20:46:00 dispatch. What the audit does NOT cover: **(a)** A2 says "every bgrun ended: all runs accounted for," yet `priorart_c68_m3a1.log:1` is a START with no terminal line — a parent-killed bgrun writes no END, and A2 either scopes review logs out or matched the second run's END to the first START; either way a killed run is invisible to it. **(b)** C4 books the judgement sessions themselves ($15.24 + $29.98 of the $52.7455) as "review" cost — actual peer reviews cost $7.5229 ($4.1677 + $3.3552) and ~17 min, so "reviews are 96% of wall-clock" is true only under an aggregation that lumps the orchestrator in with the reviewers. **(c)** Refused launch attempts cost turns on a $30 session and appear nowhere except C6's count of 3, which misses the ~14 material-side wrong-form attempts.

**5. Ordering — defensible, and the required order was actually followed:** re-review of the edited recipe (answered 21:01:08) → disposal with FIXED releases (`2026-09-21-priorart-c68-m3a1.md:261-266`) → AST gate 21:17 → build 21:20 → hypothesis review of the result 21:38 → NEXT → retrospective last (21:47). One small inversion: the c68 astcheck at 20:37 was spent on a recipe version whose pending prior-art review then changed it (three FIXED lines cite recipe edits), forcing the c69 re-check — the first check bought nothing.

**6. What the summary would hide.** The session's own closing summary (`cycle_55.log:62`, result field) says "both process faults that cost this cycle two blocked attempts are written down." The machine record says the launch-form fault alone produced **fourteen** wrong-form attempts across two rounds (`material_marker.log:851-856, 861-868`) plus ~20 permission denials in the session JSON, and the killed 20:46:00 dispatch is not mentioned at all. "Two blocked attempts" understates the churn by roughly a factor of seven. Also understated: the cycle's only build cost 3 min 36 s (audit C3) while the session that orchestrated it cost $29.98 and 61 minutes — the summary presents the milestone, not the overhead ratio.

**7. Judgement inside a material session — none found.** The accept/reject decisions on all six prior-art findings, the withdrawal of Pre-decided 61, and the adoption of the identity-gate acceptance test were taken by the judgement session (its result text in `cycle_55.log:62` claims them in first person; Pre-decided 65/66/70-73 are plan edits). The recipe's step [6b] explicitly *refuses* to decide — "It is NOT attempted here and it is NOT worked around... reported to judgement" (`build_d1_m3a1.log:551`) — which is the split working as designed. The audit's 3 refused judgement-session attempts (C6) were attempts to do *material* work in judgement, the opposite direction, and the hook stopped them.

## DEVICE EFFECT

- **unreported-fact (rc truthfulness):** held — the build's inner FAIL forced `BGRUN END rc=1` (`build_d1_m3a1.log:552, 591`).
- **rule-evaded (confirm-bait / adversarial append):** held — the c69 task carries the full adversarial set and the reviewer refuted rather than confirmed (`c69-border-wiredelta.md:47-53, 61`).
- **tool-not-built (prior-art review):** held, and this cycle is its best result to date — six findings, all accepted, three of which changed the recipe itself (`2026-09-21-priorart-c68-m3a1.md:261-266`), one of which found the route that retired the NO-ROUTE verdict.
- **repeated-failure-class (guard_peer empty-disposal refusal):** no failure observed; the review was disposed before release.
- **unreported-fact (C3/C4 cost split):** fired and made the cost argument possible (C3 3 m 36 s vs C4 113 m 22 s), but see finding 4(b): its "review" bucket includes the orchestrator sessions, so it fires with a misleading denominator. Not one of the three failure modes; a defect worth fixing, recorded here as a finding.
- **premature-build (guard_cycle):** **held under real pressure** — a build launch was attempted at 20:37:31 (`material_marker.log:857`), 24 minutes *before* the fresh prior-art review answered, and it never ran: `build_d1_m3a1.log:1` shows exactly one BGRUN START, at 21:20:10, after disposal and release.
- **scope-creep (C7 list):** fired correctly — 4 out-of-plan files listed, all bookkeeping/hook artefacts, none suspicious.
- **device-failed (cost regex):** held — C4b "4 seen / 4 parsed".
- **device-failed (bgrun FAIL scan):** held — the `FAIL` at `build_d1_m3a1.log:552` produced rc=1.
- **repeated-failure-class (OpLoopEndRef_v0 reader):** not exercised in this window; no failure to report.
- **device-failed (stop record + launch gate):** held — `tools/bench/stop_records.json` shows path-keyed records with hash-qualified releases, and the one launch of the recipe post-dates its release.

No listed device failed inside the window, so no `device-failed` is emitted. The nearest miss is not a listed device: bgrun's "always writes a final END|TIMEOUT" guarantee is defeated by parent death (`priorart_c68_m3a1.log:1`), and audit A2 passed over it — that gap should reach `docs/violation-decisions.md` as the concrete defect behind the one fault named below.

## THE ONE STRUCTURAL FAULT

The dispatch-lifecycle failure class — a known fault, its repair explicitly "named, deliberately NOT BUILT" (STATUS.md:47) — recurred throughout the window and is the only thing that changed what this cycle cost: the killed 20:46:00 prior-art dispatch forced an 8.7-minute re-buy delay (20:46:00 → 20:54:39, `priorart_c68_m3a1.log:1,3`) and consumed two of the session's eight guarded dispatches, and the same class (wrong launch form, background-then-turn-end) burned fourteen refused attempts totaling ~6 more minutes (`material_marker.log:851-856, 861-868`). Counterfactual on the clock: had the 20:46:00 dispatch survived its parent, the review lands ~20:52 instead of 21:01:08; had the c69 astcheck used `--material` on attempt 1 at 21:13:00, the build launches ~21:06 instead of 21:20:10 — the cycle ends ~21:33 rather than 21:47:34. No log carries a dollar figure for the killed dispatch (it died before a COST line) or for the denial churn, so the dollar loss is honestly unknown.

VIOLATION: repeated-failure-class | loss_min=15 | loss_usd=? | evidence=tools/bench/priorart_c68_m3a1.log:1

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
