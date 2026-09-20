# retrospective-cycle42

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $3.7537  in 14 / out 20434 / cache-create 110587 / cache-read 520140  (313s, 13 turn(s))
- **date:** 2026-09-19 08:03:43
- **outcome:** ANSWERED (314s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 42 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-19 06:21:00  ..  2026-09-19 07:58:28   (97 min)
    basis: start = archive/peer/2026-09-19-retrospective-cycle41.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-19 06:21 .. 2026-09-19 07:58 (97 min, an explicit cycle window): 3 build logs, 9 peer logs, 16 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 3/3 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 1 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 13/16 annotated; blank: ['2026-09-19-routeb-run10-error2-class.md', '2026-09-19-stall-selftest-c39-g78.md', '2026-09-19-stoprecord-release-deadlock-codex.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 3, failure markers 2, logs carrying a failure 1
  C2 peer reviews dispatched 9, archived 16
  C3 wall-clock inside bgrun, BUILDS ONLY 31 min 17 s
  C4 wall-clock inside bgrun, REVIEWS 20 min 44 s; cost $11.9877 from 3 log(s) that report one
  C4b cost lines seen 3 / parsed 3
  C5 total wall-clock 52 min 1 s  (reviews are 39% of it)

  C6 material-marked recipe/bench runs 2, judgement-session attempts refused 4  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 4 - STATUS.md, tools/bench/task_c42_user_report.md, tools/bench/task_routeb_run10_error2_class.md, tools/hooks/material_marker.log


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 281/485 ok; 204 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 1 DANGLING of 927 citations checked:
       STATUS.md:64 -> tools/recipes/build_d1_routeb_v8.py

  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  WARN  L2b cited line numbers are in range: 1 citation(s) point past the end of the file: ['docs/NAMES.md:1008 -> docs/toolkit-capabilities.md:775 (file has 630 lines)']
  WARN  L3 STATUS.md stays one screen: STATUS.md:133 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 225 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:915']

AUDIT VIOLATIONS: A4 every archived review says what was done with it, L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (3; read them directly, they are the primary record) ===
tools/bench/build_d1_routeb_v7_run10.log  (2026-09-19 07:25:42)
tools/bench/prose_cycle42.log  (2026-09-19 07:56:46)
tools/bench/v7_syntax_c42.log  (2026-09-19 06:54:24)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (9) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/audit_cycle42.log  (2026-09-19 07:38:26)
tools/bench/cycle_27.log  (2026-09-19 06:25:01)
tools/bench/cycle_28.log  (2026-09-19 06:25:01)
tools/bench/cycle_runner.log  (2026-09-19 06:25:01)
tools/bench/cycle_runner_main_20260918e.log  (2026-09-19 06:41:30)
tools/bench/doc_ingest_c42.log  (2026-09-19 07:41:10)
tools/bench/peer_routeb_run10_error2_class.log  (2026-09-19 07:49:02)
tools/bench/priorart_d1_routeb_run10.log  (2026-09-19 06:42:42)
tools/bench/retro.log  (2026-09-19 07:58:27)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle42-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

# Retrospective (v2) — cycle 42, outcome review

## THE ONE STRUCTURAL FAULT

**The cycle-42 judgement session released the prior-art stop by refuting two correct findings (F3, F4) on an unverified claim about our own code — and run 10 then spent its entire 31-minute purpose proving the refutation wrong.**

The refutation on record (`archive/peer/2026-09-19-priorart-d1-routeb-run10.md:496-497`) asserts "v7 issues no keystroke save at all" and "the save path is COM g.save, not gui_save" — citing v7's own call site (`v7:2276`) but never opening the callee. `gscript.py:2065-2067` shows `g.save(target, allow_broken=True)` diverts to `gui_save` whenever ExecState reads 0, which it always does cold. Run 10 took that divert and died at `tools/bench/build_d1_routeb_v7_run10.log:367` on the exact mtime failure F4 named — its one gate that mattered failed (`run10.log:368`), the fresh-instance census was never taken, all 51 rows UNREAD (`run10.log:370`), no D1 VI saved. The session's own correction says it plainly: *"The refutation was made from a call-site summary without reading the callee"* (`…priorart-d1-routeb-run10.md:499`).

- **Slug:** `inference-over-measurement` (the measurement — reading ~15 lines of `gscript.py`, or one dry `save()` on a scratch file — was free and available at disposition time, ~06:45).
- **Loss:** run 10's wall clock, `BGRUN END rc=1 after 1835s` (`run10.log:514`) ≈ **31 min**, essentially all of the audit's C3 build figure (31 min 17 s). No bgrun build log carries a dollar figure, so the dollar loss is honestly unknown. I deliberately do **not** book the $5.5451 failed-prediction review (`tools/bench/peer_routeb_run10_error2_class.log:3`) as loss: it fired because of this fault's missed predictions, but it returned the cycle's single most valuable product (see findings 2 and 6).
- **Counterfactual:** the prior-art review returned at 06:42 (`priorart_d1_routeb_run10.log:167`); had the session opened `gscript.py` before writing the two REFUTED lines, F2+F4 stand together ("save-first is dead as designed"), E3 is removed or redesigned before launch, and the 06:55:08–07:25:43 run is not spent on a known-dead mechanism. The cycle ends ~07:27 instead of 07:58, or that half hour funds the v8 cut that STATUS NEXT now orders anyway.

No second fault is of the same magnitude. Everything else below is a finding.

## FINDINGS

**1. Repeated failure.** Yes — *keystroke save of a broken/unloaded target* recurred for the **third** time: `cycle3b_toolkit.log:78` and `build_keystone.log:903` (both cited in the refutation itself, `…priorart-d1-routeb-run10.md:497`), then `run10.log:367`. The approach should have changed at attempt 3 — i.e., at the disposition step before launch, by accepting F4 rather than refuting it. The prior-art layer put the change point in the session's hands at 06:42 and the session declined it. Separately, `error 2` recurred across runs 8/9/10; the approach *did* change at run 10 (E3), but on a wrong causal model — the correct change (the Close Reference leak repair, `docs/REFERENCES.md:126`) only emerged from the post-run review.

**2. Missing tool.** A **memory-pressure reader (LabVIEW private bytes)**. The $5.5451 review established that `error 2` is "Memory is full" and that the handle count — quoted for weeks as refuting a memory cause ("healthy at 51,334, error 2 at 35,541", `…routeb-run10-error2-class.md:25`) — measures nothing relevant. Every handle-based refutation across runs 8–10 was a category error (STATUS.md:88-89). Had a private-bytes reader existed, the leak diagnosis was reachable a cycle or two earlier, and run 10's whole save/restart premise would likely never have been designed. STATUS NEXT's P1 now builds exactly this logging.

**3. Unmeasured steps.** Two, both inside the window. (a) The F3/F4 refutation (above). (b) CLAIM 2's census — "`report_all(Diagram)`: 21 occurrences, 0 successes" (`…routeb-run10-error2-class.md:21`) — was built by grepping for error strings while successes sat unread in the same logs (`run10.log:39, :44, :352`); the reviewer refuted it as a selection artifact and STATUS NEXT withdraws the claim (STATUS.md:91-92). Both are inference where the measurement was already on disk.

**4. Rule compliance.** Broken or formal: the prior-art release rule ("open the citation and show in writing") was satisfied only *formally* — the two REFUTED lines have citation shape but the load-bearing citation (`gscript.py`) was never opened; this also breaks CLAUDE.md's "claims about our own tools are factual claims" (external-search section). Audit A4 FAIL: 3 reviews blank, including the cycle's own $5.55 review `2026-09-19-routeb-run10-error2-class.md` — its findings were absorbed into STATUS NEXT but the annotation the gate reads is empty. L2: `STATUS.md:64 → tools/recipes/build_d1_routeb_v8.py` dangles (a forward reference STATUS gets no L2c leniency for). L3: STATUS at 133 lines. What the audit does **not** cover: (i) truth of REFUTED lines — it can never catch this cycle's fault class; (ii) the judgement session's own cost (acknowledged in the user report, `archive/prose/2026-09-19-c42-user-report.md`, OPEN 56); (iii) **GUI actions issued from inside gscript**: run 10 sent Ctrl+S keystrokes to "every candidate window" (`run10.log:367`), yet `tools/gui_actions.log`'s last entry is 2026-09-18 18:12 — A6's "this cycle used no GUI if the retrospective agrees" must be answered **no, and the ledger missed it**, because `gui_save` bypasses `lv_gui.ps1`'s logging; (iv) C7 judges scope against `docs/cycle27-plan.md` while everything else calls this cycle 42, and the plan file this task names (`docs/cycle42-plan.md`) does not exist.

**5. Ordering.** Defensible, and better than the recent norm: the cycle obeyed STATUS NEXT's "first act is a D1 build dispatch" — v7 cut (material), prior-art review, disposition, launch, mandatory review, corrections, report, audit, retro, in that order. The prior-art gate ran *before* the launch (review ended 06:42, launch 06:55). The only inversion is the micro one already named: read the callee before writing the refutation.

**6. What was not reported.** The user report is unusually candid (it volunteers that both dismissals were wrong), but three things sit only in raw logs: (a) the **cost totals disagree three ways** — the report says ~$12.69, the audit C4 says $11.9877, and the four COST lines in the window sum to **$12.8005** ($5.6462 + $5.5451 + $0.7964 + $0.8128); C4 missed the prose report's $0.8128 because `prose_cycle42.log` is classified as a *build* log (it is in this dispatch's build-log list, and C3's 31:17 = 1835 s + 42 s of prose), and C4b's "3 seen / 3 parsed" reads as complete while a fourth cost line went uncounted — the self-visibility line the cost device added did not make this miss visible; (b) the judgement session tried to run material-marked work itself **4 times** and was refused (audit C6) — no summary mentions it; (c) the unlogged Ctrl+S keystrokes from finding 4.

**7. Judgement inside a material session.** None found. The disposition of all seven prior-art findings, both refutations, the correction at `…priorart-d1-routeb-run10.md:486-499`, and the run-11 re-plan were all taken by the judgement session; the material step applied pre-disposed edits only (STATUS.md:23, :26). The failure ran the *other* way — material work attempted inside judgement, caught 4 times by the guard (audit C6).

## DEVICE EFFECT

Judged device by device, against this window only:

- **Stop record + launch gate** (2026-09-18): the closest call, and I rule it **did not fail**. It fired exactly as designed — refused run 10 at the reviewed sha (`STATUS.md:26`, "ARMED, NOT RELEASED"), demanded written releases, re-armed on the new sha, and released only after `FIXED:`/`REFUTED:` lines existed (`STATUS.md:23`). The already-failed mechanism ran anyway, but it got through the *judgement valve* the device explicitly delegates ("writing REFUTED:/FIXED: is JUDGEMENT's call"). A wrong judgement fed through the sanctioned channel is not a fired-and-worked-around bypass; calling it one would make every wrong disposition a device failure and re-saturate the slug this format exists to protect. The gap it exposes is real — a REFUTED line is checked for form, never for whether the refuting claim was verified — but that is a design limit to weigh, not a broken device.
- **Prior-art review** (tool-not-built device): **worked**, conspicuously — F4 was proven right by the machine 30 minutes after being dismissed (`run10.log:367`). The detector did its job; disposition failed it.
- **UNREAD-vs-BARE census contract** (unreported-fact, 2026-09-16): **held under fire** — a save that never happened printed `0 bare / 51 unread` (`run10.log:370-371`) instead of a fabricated wiring catastrophe. This is the clearest device *success* on record.
- **bgrun rc/END + FAIL scan** (both device-failed repairs): worked — `**FAIL**` at `run10.log:368`, `BGRUN END rc=1` at `:514`; audit C1 counted the failure.
- **COST regex + C4b self-test**: parsed 3/3 of what it looked at, but see finding 6(a) — a fourth cost line escaped via log *classification*, outside the regex's scope and invisible to the self-test. A scope hole worth one line in the decisions file, not a fault that changed how the cycle ended ($0.81 of invisibility).
- **guard_cycle premature-build gate**: worked — prior-art log ended (06:42) before the recipe launch (06:55).
- **confirm-bait refusal / adversarial append**: the $5.55 dispatch carries the full adversarial preamble (`…routeb-run10-error2-class.md:39-45`) and the reviewer did refute, hard. Worked.
- **C7 out-of-plan list**: fired, listed 4 files. Worked (against the wrong-numbered plan, finding 4(iv)).
- **guard_peer blank-disposition refusal**: its scoped condition (newest *priorart/retrospective* review annotated) was met — the run-10 prior-art file has a filled disposition section — so the 3 blank files A4 flags are hypothesis-kind, outside its scope. Not failed; scope note only.
- **OpLoopEndRef_v0 reader**: not exercised in the window; the terminal `count(LoopTunnel)` crash recurred (`run10.log:491, :513`) but D1's S4 was never reached.

No device met the failure bar, so no device-failed line is emitted.

---

VIOLATION: inference-over-measurement | loss_min=31 | loss_usd=? | evidence=archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499

## Sources

(extract from answer)

## What was done with it

ACCEPTED IN FULL by the cycle-42 judgement session, 2026-09-19, and acted on in the same cycle.

- **The named fault is right and is mine.** `VIOLATION: inference-over-measurement | loss_min=31` is recorded with
  a `DECISION: no-device` block in `docs/violation-decisions.md` (the threshold is suspended by the user's standing
  order of 2026-09-18 08:53), and the rule that would have prevented it — *a claim about what our own code does must
  quote the CALLEE, not the call site* — is written into `docs/cycle27-plan.md` Pre-decided 21(f).
- **Finding 1 (repeated failure, keystroke save, 3rd occurrence):** accepted. Run 11 removes the save entirely;
  `docs/cycle27-plan.md` Pre-decided 20 is marked SUPERSEDED so no future session re-cuts a save→restart build on
  its strength.
- **Finding 2 (missing tool — a private-bytes reader):** accepted and already ordered. STATUS `## NEXT` P1/P2 log
  LabVIEW private bytes per iteration; Pre-decided 21(a) forbids the handle count as the meter in terms.
- **Finding 3 (unmeasured steps):** accepted, both. The census selection artefact is WITHDRAWN in Pre-decided 21(e).
- **Finding 4 (rule compliance):** accepted. (i)/(ii) are the fault above. (iii) is a genuine and previously unknown
  hole and is carried into STATUS as an OPEN item: **`gui_save` sends Ctrl+S without going through `lv_gui.ps1`, so
  its keystrokes never reach `tools/gui_actions.log`** — the GUI ledger under-reports, and the user's
  capture→locate→act→capture→confirm rule cannot bind a path that does not log. (iv) the plan-number mismatch is
  noted; the current plan is `docs/cycle27-plan.md` and no `docs/cycle42-plan.md` exists by design.
  The dangling `STATUS.md` → `build_d1_routeb_v8.py` reference is DELIBERATE and was already decided in cycle 41:
  naming the exact file the next cycle must cut is what `## NEXT` is for, and it self-clears when run 11 cuts it.
- **Finding 5 (ordering):** noted, no action — the cycle obeyed the user's "first act is a D1 build dispatch" order.
- **Finding 6 (what was not reported):** accepted, and the cost figure is CORRECTED in STATUS from ~$12.69 to the
  true four-line sum **$12.8005**; the classification hole that hid `prose_cycle42.log`'s $0.8128 from C4 is
  recorded but NOT fixed with a new device, under the same standing order.
- **Finding 7 (judgement inside material):** none found; the four guard refusals of material work attempted inside
  the judgement session are recorded here rather than being left only in the audit.
- **DEVICE EFFECT:** no device-failed line, and the UNREAD-vs-BARE census contract is recorded as the clearest
  device success on record — it printed `0 bare / 51 unread` for a save that never happened.

(Claude fills in)
