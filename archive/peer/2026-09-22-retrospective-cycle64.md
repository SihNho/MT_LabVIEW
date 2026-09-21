# retrospective-cycle64

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.6898  in 20 / out 26028 / cache-create 118674 / cache-read 1014737  (392s, 21 turn(s))
- **date:** 2026-09-22 02:58:11
- **outcome:** ANSWERED (393s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 64 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-22 01:09:11  ..  2026-09-22 02:51:36   (102 min)
    basis: start = archive/peer/2026-09-22-retrospective-cycle63.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-22 01:09 .. 2026-09-22 02:51 (102 min, an explicit cycle window): 11 build logs, 7 peer logs, 8 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 11/11 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  FAIL  A3 every failing log is followed by an archived review: 2 logs recorded a failure; unreviewed: ['build_d1_m3a2.log']
  FAIL  A4 every archived review says what was done with it: 7/8 annotated; blank: ['2026-09-22-c74-m3a2-fmt.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1808 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 13, failure markers 4, logs carrying a failure 2
  C2 peer reviews dispatched 7, archived 8
  C3 wall-clock inside bgrun, BUILDS ONLY 7 min 11 s
  C4 wall-clock inside bgrun, REVIEWS 125 min 45 s; cost $63.9903 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C5 total wall-clock 132 min 56 s  (reviews are 94% of it)

  C6 material-marked recipe/bench runs 24, judgement-session attempts refused 3  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 12 - tools/bench/.stall_samples.txt, tools/bench/c74_gate10_report.py, tools/bench/diag_c73_m3a2_rows.py, tools/bench/diag_c74_m3a2_verify.py, tools/bench/m3a2_save_after_20260922_023029.png, tools/bench/m3a2_save_before_20260922_023029.png, tools/bench/next_snapshot.md5, tools/bench/peer_task_c74_gate10.md, tools/bench/peer_task_c74_m3a2_execstate.md, tools/bench/priorart_task_c74_m3a2.md, tools/gui_actions.log, tools/hooks/material_marker.log


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 282/584 ok; 302 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  FAIL  L2 every cited project path exists: 1 DANGLING of 1546 citations checked:
       STATUS.md:56 -> archive/2026-09-22-status-cycle64-locknotes.md

  WARN  L2c plan documents cite files that do not exist yet: 16 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 63 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 379 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:391', 'docs/NAMES.md:530', 'docs/NAMES.md:652', 'docs/NAMES.md:925', 'docs/NAMES.md:939']

AUDIT VIOLATIONS: A3 every failing log is followed by an archived review, A4 every archived review says what was done with it, L2 every cited project path exists


=== BUILD LOGS INSIDE THE WINDOW (11; read them directly, they are the primary record) ===
tools/bench/build_d1_m3a2.log  (2026-09-22 02:32:30)
tools/bench/c74_astcheck_m3a2.log  (2026-09-22 01:41:52)
tools/bench/c74_astcheck_m3a2_r2.log  (2026-09-22 01:58:20)
tools/bench/c74_astcheck_m3a2_r3.log  (2026-09-22 02:30:12)
tools/bench/c74_astcheck_verify.log  (2026-09-22 02:43:43)
tools/bench/c74_gate10_census.log  (2026-09-22 02:29:42)
tools/bench/c74_gate10_m3a2.log  (2026-09-22 02:15:26)
tools/bench/c74_gate10_report.log  (2026-09-22 02:45:48)
tools/bench/diag_c73_import.log  (2026-09-22 01:21:37)
tools/bench/diag_c73_m3a2_rows.log  (2026-09-22 01:24:15)
tools/bench/diag_c74_m3a2_verify.log  (2026-09-22 02:45:27)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (8) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_58.log  (2026-09-22 01:10:40)
tools/bench/cycle_59.log  (2026-09-22 02:51:35)
tools/bench/cycle_runner.log  (2026-09-22 01:10:40)
tools/bench/cycle_runner_main_20260921d.log  (2026-09-22 01:10:40)
tools/bench/peer_c74_gate10.log  (2026-09-22 02:27:18)
tools/bench/peer_c74_m3a2_fmt.log  (2026-09-22 02:07:34)
tools/bench/priorart_c74_m3a2.log  (2026-09-22 01:51:23)
tools/bench/retro.log  (2026-09-22 02:51:36)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

All evidence read. Here is the retrospective of cycle 64.

---

## SUMMARY OF THE CYCLE'S OUTCOME

This cycle delivered what it set out to deliver: `D1_s3b_m3a2_20260922_023029.vi` (md5 `3842f5e6…`), 25/0 gates on the build (`tools/bench/build_d1_m3a2.log:321`), 15/0 on a separate read-only verification anchored at register UIDs (`tools/bench/diag_c74_m3a2_verify.log:101`), both predicted sources landed (#4194→#23880, #3974→#23909), originals byte-unchanged on every pin. After cycles 55–58 produced nothing at all on M3a-1, this is the first cycle in days whose outcome fully matches its plan item. The work was worth doing, and the review costs it paid ($12.37 across three reviews) each returned something the cycle then used — the B2 save-capture repair from the prior-art review is *measurably* discharged in run 2 (`build_d1_m3a2.log:286-288`, both PNGs on disk for the first time in the project's history).

The blemish is a 32-minute, ~$6 detour caused by launching a 1,106-line, never-executed, hand-written recipe on the strength of a parse-only clearance.

---

## FINDINGS

**1. Repeated failure.** No same-class recurrence *inside* the window: the `%`-format crash happened once (run 1, `build_d1_m3a2.log:31-32,59`, rc=1 after 71s) and run 2 passed 25/0. The response at attempt 1 was correct per the project's own rules — no patch-and-rerun in the same dispatch, mandatory review dispatched (`archive/peer/2026-09-22-c74-m3a2-fmt.md`). Across cycles, though, the class "defect in a hand-transcribed recipe that no gate ever executes" is the same one that ate cycles 55–58 on M3a-1; the approach should have changed **before run 1 of this recipe**, not after — the recipe "had never been executed before this run" (`archive/peer/2026-09-22-c74-m3a2-fmt.md:110`) and the pinned clearance is `ast.parse` plus counts (11 PASS on a file that died at its first `fact()` call, `tools/bench/c74_astcheck_m3a2_r2.log`, cited at `c74-m3a2-fmt.md:100-103`).

**2. Missing tool.** The stubbed-`g` dry run — import the recipe with the LabVIEW gateway mocked, call `main()` — named explicitly by the fmt review (`2026-09-22-c74-m3a2-fmt.md:198`) and put to the user in STATUS.md:59. It would have caught the `read_es` arity/signature bug in seconds, and unlike gate 10 it also catches the `KeyError`/signature-drift class that %-arity linting cannot. It stayed unbuilt because of the user's 2026-09-18 08:53 no-new-devices order — a defensible refusal, and STATUS.md:59 honestly gives the counter-measurement (0 further mismatches in 3 files, so the class measured as non-endemic). Its absence is what the one structural fault below prices.

**3. Unmeasured steps.** Mostly the opposite — this cycle measured things other cycles would have argued: the "45 minutes lost" framing was corrected to 71s from the log (`c74-gate10-arity.md`-adjacent, `peer_c74_gate10.log:72`); the gate-10 "no further defect after repair" claim, caught as unmeasured inference by the second peer (`peer_c74_gate10.log:50`), was then actually measured (`tools/bench/c74_gate10_report.log:15-24`, 6/6 fixture + 0 defects across 3 files). One measurement was available, cheap, and deferred: run 1's handle jump 30,689 → 45,677 in 71 seconds with 0 live refs (`build_d1_m3a2.log:24,51`) — H6/H7 both PASS and say nothing about it; the verify run repeated the pattern (+11,650, `diag_c74_m3a2_verify.log:99`) and it is now a "standing FACT, not yet a gate" (STATUS.md:55). `handle_audit.py` exists precisely to attribute handle growth (CLAUDE.md:196) and was not pointed at it.

**4. Rule compliance.** Rule 1 held mechanically (all pins, every run). The failed-prediction protocol (CLAUDE.md §5) was followed to the letter. Two rules satisfied only formally: (a) the disposition rule — `archive/peer/2026-09-22-c74-m3a2-fmt.md:235-237` still reads "(Claude fills in)" although its findings were in fact acted on (H9 gate, gate 10 — STATUS.md:53), i.e. the substance was done and the annotation the machinery checks was not, the exact inverse of the token-edit evasion A4 was built against; (b) rule 4 layering — STATUS.md:56 *names* the relocation file for the ~8KB lock-purpose chain (`archive/2026-09-22-status-cycle64-locknotes.md`) but never created it, which is the audit's one dangling citation (L2). What the audit does NOT cover: cost *attribution* (see fault 2 below — C4's headline number is wrong in kind); multi-run logs (A3 flags `build_d1_m3a2.log` as unreviewed even though `c74-m3a2-fmt.md` reviews exactly its failure — run 2's append post-dates the review, so the day-granular matcher misses it); whether a passing clearance gate measures what its PASS implies; and the judgement session's own spend, which appears in no project document.

**5. Ordering.** Defensible, and better than most cycles: measurement (`diag_c73_m3a2_rows`) → recipe → prior-art *before* build (enforced and honored: priorart END 01:51, build 01:58) → review before re-run → independent verify after. The one inversion is the subject of the violation: the executability check (gate 10, <1s once built) came after the launch instead of before it.

**6. What was not reported.** The largest single number of the cycle appears nowhere in the session's own account: the judgement session cost **$51.62** (`tools/bench/cycle_59.log:62`, `total_cost_usd":51.62158950000003`) — 81% of the cycle's total dollar spend. STATUS.md itemizes $6.30, $2.69 and $3.38 and never mentions it. Second: run 1's +15,000 handle spike reached the record only because a peer reviewer flagged it unasked (`c74-m3a2-fmt.md:223`). Third: STATUS honestly reports M3a-1's save had *no* captures at all (STATUS.md:53) — credit where due, that one was volunteered.

**7. Judgement inside a material session.** None found. The fmt review's brief states "DISPOSITION IS THE JUDGEMENT SESSION'S" and offers no diagnosis of its own (`2026-09-22-c74-m3a2-fmt.md:10`); the gate-10 widening was "accepted with the judgement session's scope limit" (STATUS.md:26 lock purpose); the stop-record release by `FIXED:` lines is recorded as the judgement session's call. C6 shows 3 judgement-session material attempts *refused* — the guard doing its job, at the cost of a few wasted turns.

---

## DEVICE EFFECT (each listed device, against this window)

- **unreported-fact (rc/END guarantee)** — WORKED: run 1's crash produced `BGRUN END rc=1 after 71s` (`build_d1_m3a2.log:59`); nothing failed silently.
- **rule-evaded (confirm-bait refusal)** — NOT TRIGGERED; both task files carry the adversarial instruction set (`peer_task_c74_m3a2_execstate.md:129-135`).
- **tool-not-built (prior_art_review)** — WORKED, its best outing on record: 4 findings, all disposed, B2's fix verified by the machine in run 2 (`build_d1_m3a2.log:286-288`).
- **repeated-failure-class (guard_peer blank-disposition refusal)** — did not fire, and by its own terms was not required to: the blank review (`c74-m3a2-fmt.md:237`) is kind `hypothesis`, the device guards only `priorart`/`retrospective` dispatches. A scope gap, not a failure — but note this retrospective was dispatched with that blank standing, which is the loop shape the device was built against.
- **unreported-fact (C3/C4 cost split)** — **FAILED, on the wrong-thing axis.** C4 reports "REVIEWS … cost $63.9903 from 4 log(s)". The four lines are $6.3017 (`priorart_c74_m3a2.log:4`) + $2.6899 (`peer_c74_m3a2_fmt.log:3`) + $3.3771 (`peer_c74_gate10.log:3`) + **$51.6216, which is the judgement session itself** (`cycle_59.log:62`) — the sum matches to the cent. Likewise C4's "125 min 45 s review wall-clock": the three actual reviews total 1,419s (~24 min); the remaining ~102 min is the judgement session's bgrun. So the device built to "make the cost argument possible instead of rhetorical" states that reviews are 94% of the cycle when they are ~19% of wall and $12.37 of cost. This is precisely the failure mode the project records being burned by — a cost argument made against a figure that is wrong by nature, here 5.2× on the review side, and it feeds every retrospective including this one (the prompt instructed me to quote C4 as authoritative).
- **premature-build (guard_cycle)** — WORKED: priorart ended 01:51:23 before the 01:58:42 launch; stop record armed (`priorart_c74_m3a2.log:85`), released by `FIXED:` lines, re-planted for the edited sha (STATUS.md:26).
- **scope-creep (C7 out-of-plan list)** — WORKED as a counter; the 12 files are this cycle's own bench outputs and screenshots, all measurement artifacts. Verdict: the out-of-plan changes were right.
- **device-failed (cost-regex repair)** — WORKED: C4b "cost lines seen 4 / parsed 4"; the parse is fine — the *classification* is what's broken (above).
- **device-failed (bgrun FAIL scan)** — WORKED: run 1 forced rc=1.
- **repeated-failure-class (OpLoopEndRef_v0)** — not exercised in this window (M3a-2 touches no conditional terminal); no evidence either way.
- **device-failed (stop record + launch gate)** — WORKED end to end: armed on a non-novel verdict, refused launch, released by hash-qualified `FIXED:` lines, re-armed for the post-edit bytes.

One device *outside* the extracted list also failed and should be said plainly: the pinned launch-clearance checker `c60c_astcheck.py` printed 11 PASS / 0 FAIL (`c74_astcheck_m3a2_r2.log`) on a file that could not survive its first diagnostic call — a parse verdict read as a fitness verdict, the same class its own docstring memorializes (`c60c_astcheck.py:22-28` per `c74-m3a2-fmt.md:185`). It is priced inside fault 1 rather than as a separate device line because it is not on the machine-extracted device list this section governs.

---

## THE STRUCTURAL FAULTS — ranked, two, both of magnitude

**1. `tool-not-built` — the executability gap in front of a LabVIEW launch.** A never-executed 1,106-line hand-adapted recipe was cleared for a LabVIEW batch by a checker that only proves it parses. It crashed at 71s on a five-specs-vs-four-args format string (`build_d1_m3a2.log:31,59`), which triggered the mandated $2.69 review, the gate-10 build, its $3.38 adversarial review, and a widening pass. Counterfactual, on the clock: gate 10 took under a second once built and flagged exactly this line on its first run (`c74_gate10_m3a2.log`, 1 MISMATCH); had that check — or the stubbed-`g` run — existed at 01:57, run 1 at 01:58 would have been run 2, the artefact lands ~02:00 instead of 02:30:29, and the cycle closes roughly half an hour earlier without $6.07 of review spend. Loss: 32 min (launch 01:58:42 → relaunch 02:30:29), $6.07 carried by `peer_c74_m3a2_fmt.log:3` + `peer_c74_gate10.log:3`. Mitigation acknowledged: the detour was converted into two permanent gates and the class was then *measured* as non-endemic — this is the best possible way to pay for the fault, but the fault was still paid for.

**2. `device-failed` — the C3/C4 cost-split device (audit_cycle) files the judgement session as review cost.** Threshold 1 per this contract, and the failure is inside this window: C4's $63.9903 and "reviews are 94% of it" are arithmetic over four lines of which one — $51.62, 81% of the total — is the judgement session (`cycle_59.log:62`), not a review. Every dollar argument downstream of C4, including the one this retrospective was told to rely on, is wrong in composition. No wall-clock was lost to it this cycle, hence loss_min=0; the corrupted quantity is the measurement itself.

---

VIOLATION: tool-not-built | loss_min=32 | loss_usd=6.07 | evidence=tools/bench/build_d1_m3a2.log:59
VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/cycle_59.log:62

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
