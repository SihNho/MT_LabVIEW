# retrospective-cycle39

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.1163  in 10 / out 25580 / cache-create 126108 / cache-read 315023  (364s, 10 turn(s))
- **date:** 2026-09-19 03:52:04
- **outcome:** ANSWERED (365s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 39 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-18 23:08:56  ..  2026-09-19 03:45:58   (277 min)
    basis: start = archive/peer/2026-09-18-retrospective-cycle36.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-18 23:08 .. 2026-09-19 03:45 (277 min, an explicit cycle window): 10 build logs, 21 peer logs, 67 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 10/10 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 6 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 58/67 annotated; blank: ['2026-09-18-asi-soft-limits-sl-su.md', '2026-09-18-ff-selftest-bgrun-start-regex-codex.md', '2026-09-18-ff-selftest-bgrun-start-regex-opus.md', '2026-09-18-ff-selftest-drycmd-split-codex.md', '2026-09-18-ff-selftest-drycmd-split-opus.md', '2026-09-18-pi-c863-soft-limits.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 21, failure markers 10, logs carrying a failure 6
  C2 peer reviews dispatched 21, archived 67
  C3 wall-clock inside bgrun, BUILDS ONLY 154 min 24 s
  C4 wall-clock inside bgrun, REVIEWS 406 min 22 s; cost $114.2799 from 10 log(s) that report one
  C4b cost lines seen 10 / parsed 10
  C5 total wall-clock 560 min 46 s  (reviews are 72% of it)

  C6 material-marked recipe/bench runs 9, judgement-session attempts refused 14  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 12 - STATUS.md, docs/violation-decisions.md, tools/bench/.stall_samples.txt, tools/bench/priorart_routeb_run5_plan.md, tools/bench/repair_c37_stall_selftest.py, tools/bench/task_stall_waitlogs_c37.md, tools/bench/task_zdz_wirecontrol_5001.md, tools/hooks/material_marker.log, tools/lv_stallcheck.ps1, tools/recipes/build_d1_routeb_v3.py, tools/recipes/build_d1_routeb_v4.py, tools/recipes/build_d1_routeb_v5.py


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 281/476 ok; 195 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 911 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  WARN  L2b cited line numbers are in range: 1 citation(s) point past the end of the file: ['docs/NAMES.md:1008 -> docs/toolkit-capabilities.md:775 (file has 630 lines)']
  PASS  L3 STATUS.md stays one screen: 103 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 225 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:915']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (10; read them directly, they are the primary record) ===
tools/bench/build_d1_routeb_v2_run5.log  (2026-09-19 00:18:08)
tools/bench/build_d1_routeb_v3_run6.log  (2026-09-19 02:06:49)
tools/bench/build_d1_routeb_v4_run7.log  (2026-09-19 03:10:37)
tools/bench/repair_c37_selftest.log  (2026-09-19 00:26:01)
tools/bench/repair_c37b_selftest.log  (2026-09-19 00:50:43)
tools/bench/wait_c37_b.log  (2026-09-19 00:33:28)
tools/bench/wait_c37_peer.log  (2026-09-19 00:33:28)
tools/bench/wait_c37_selftest.log  (2026-09-19 00:25:12)
tools/bench/wait_priorart_run5.log  (2026-09-18 23:28:40)
tools/bench/wait_priorart_run6.log  (2026-09-19 01:15:26)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (21) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_22.log  (2026-09-18 23:12:20)
tools/bench/cycle_23.log  (2026-09-19 00:53:20)
tools/bench/cycle_24.log  (2026-09-19 02:26:52)
tools/bench/cycle_25.log  (2026-09-19 02:26:52)
tools/bench/cycle_runner.log  (2026-09-19 02:26:52)
tools/bench/cycle_runner_main_20260918e.log  (2026-09-19 02:26:52)
tools/bench/peer_run6_regression.log  (2026-09-19 02:24:28)
tools/bench/peer_run7_index_shift.log  (2026-09-19 03:29:00)
tools/bench/peer_stall_waitlogs_c37.log  (2026-09-18 23:50:12)
tools/bench/peer_stall_waitlogs_c37b.log  (2026-09-19 00:48:30)
tools/bench/peer_stoprecord_deadlock.log  (2026-09-19 01:29:57)
tools/bench/peer_zdz_5001.log  (2026-09-19 00:33:27)
tools/bench/priorart_d1_routeb_run6.log  (2026-09-19 01:15:26)
tools/bench/priorart_routeb_run5.log  (2026-09-18 23:28:40)
tools/bench/retro.log  (2026-09-19 03:45:58)
tools/bench/retro_c36.log  (2026-09-18 23:08:56)
tools/bench/retro_c37.log  (2026-09-19 00:53:12)
tools/bench/stall_pid1556_002547.log  (2026-09-19 00:28:40)
tools/bench/stall_pid18476_232310.log  (2026-09-18 23:26:05)
tools/bench/stall_pid3792_235020.log  (2026-09-19 00:00:37)
tools/bench/stall_pid7288_023957.log  (2026-09-19 02:57:26)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle39-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

All evidence is in hand. Here is the retrospective of cycle 39 (window 2026-09-18 23:08:56 → 2026-09-19 03:45:58).

## Verdict first

This window did real, advancing work: three D1 route-B builds ran (runs 5, 6, 7), the `Z/dZ` row was wired for the first time (`tools/bench/build_d1_routeb_v3_run6.log:408` per `archive/2026-09-19-status-cycle39-run8.md` §1), each failed prediction got its paid review, all four prior-art findings were disposed, and v5 was cut, released, and gate-checked. But the cycle **ended with its build stranded**: run 8 fully built and released, refused by `guard_cycle`'s retrospective gate (`archive/2026-09-19-status-cycle39-run8.md:61-93`). That ending was manufactured by two faults of the same magnitude, and they are the review.

**Fault 1 — a recorded failure class recurred twice: retrospective dispatches were backgrounded and killed by session exit.** `tools/bench/retro_c37.log:1-3` shows a cycle-37 retrospective launched 00:53:11 (limit 15 min) — the log ends at "task written", no `OUTCOME`, no `BGRUN END`; `cycle_23.log`'s mtime is 00:53:20, nine seconds later — the judgement session exited and the child died. The identical thing happened at 02:26:12 for cycle 38 (`tools/bench/retro.log:216-218`, again no END line; `cycle_runner.log` mtime 02:26:52). This is the exact class STATUS OPEN 54 records from cycle 33, with its rule in capitals: *"dispatch in the FOREGROUND and wait — HOLD THE TURN OPEN until it lands"* (`STATUS.md:49`). Consequence: no retrospective for cycles 37 or 38 was ever archived (the newest on disk is `archive/peer/2026-09-18-retrospective-cycle36.md`), so `guard_cycle`'s counter kept accumulating from cycle 36 and refused run 8. Counterfactual, on the clock: a completed retro of this vintage takes ~5–7 min (`retro.log:50` 354 s, `:119` 332 s); had the 00:53 dispatch been held in the foreground, `retrospective-cycle37.md` lands ~01:00, the gate's `since` list at run-8 launch time holds at most 5 logs (< budget 10, hours 3.70 < 8.0 per `archive/2026-09-19-status-cycle39-run8.md:78-79`), and run 8 launches ~03:30 instead of the cycle closing at 03:45 with v5 stranded and both dead retros owed again. The killed cells' spend is unrecorded — no COST line exists for either, which is itself the known F4 blind spot — so the dollar figure is honestly unknown.

**Fault 2 — devices failed, in three separate on-file instances, threshold 1.** (a) The **build-log classifier feeding `guard_cycle`**: five of the ten logs that filled the budget are `tools/wait_logs.py` waiter logs that `logclass.is_build_log` counts as builds — "the budget was reached by waiters, not by builds" (`archive/2026-09-19-status-cycle39-run8.md:80-89`); only 3 real builds ran. Without this miscount the gate does not block run 8 even with the retros dead. (b) The **stall watchdog**: `archive/peer/2026-09-19-stall-waitlogs-c37b.md` measured its precision at **0/4** — every stall record it had written was a false positive, neither "real build client" was killed at its deadline — and its own `:136` clause "kills that clause's peer-reviewed guarantee at `:192`" (`STATUS.md:26`). The one-line repair the review named (write a record only on `VERDICT: BLOCKED`) was deliberately not made, and the device then fired a **fifth** false positive during run 7 (`tools/bench/stall_pid7288_023957.log:1`, "no modal dialog", while the client was alive and ran to its own crash at 03:10). Clearing this device's misfires cost two paid reviews inside the window: $3.1519 (`tools/bench/peer_stall_waitlogs_c37.log:3`) + $3.0051 (`peer_stall_waitlogs_c37b.log:3`). (c) The **stop record + launch gate** (decided 2026-09-18 00:53, on the device list): measured "MECHANICALLY UNUSABLE" — `--recipe` refuses every command naming a stopped recipe, and `_check():318-331` compares the old record's hash *after* `_released()`, so no `FIXED:`/`REFUTED:` line can ever clear it; it was worked around via the `--no-recipe` opt-out and a direct `write_stop_record` (`STATUS.md:24`), and its deadlock consumed a $3.2492 review (`tools/bench/peer_stoprecord_deadlock.log:34`). Also in this family: bgrun's "always writes a final END|TIMEOUT line" guarantee was broken by both external kills above (the known-open gap (e), `STATUS.md:83`), and audit A2 still reports "all runs accounted for" because it scans build logs only — a dispatch that dies silently is invisible to the very check that exists to see it. Logged dollars directly forced by device misfires: $3.1519 + $3.0051 + $3.2492 = **$9.41**; wall-clock ≈ 45 min of review and repair dispatches.

## FINDINGS

**1. Repeated failure.** Beyond the orphan-kill class above: the `error 2` crash at `count(LoopTunnel)` in `settle_index_modes` occurred in all three runs — run 5 (`archive/2026-09-19-status-cycle39-run8.md` §2, log `:406`), run 6 (§1, log `:430`), run 7 (`tools/bench/build_d1_routeb_v4_run7.log:452-455`) — and in run 4 before the window. The approach should have changed **before run 7 (attempt 3 in-window)**: the run-6 review's Q-B3 named the cheap discriminator — a read-only 5-step pass over the preserved crash copy (`STATUS.md:25`) — and it was still UNRUN when run 7 launched at 02:39 and crashed identically at 03:10. Three crash copies now sit on disk unread (`build_d1_routeb_v4_run7.log:440`; "nothing deletes them", `STATUS.md:21`), and v5's K1–K3 address the −96 wire deletion, not error 2 — run 8 carries the same unmeasured crash forward. Mitigating, and why this is a finding rather than a third slug: each run had independent `Z/dZ` value (run 6 first WIRED; run 7 produced the J2 −96 delta and the readable destination-side 5001), so the recurring loss is each run's settle/verify tail, not the runs themselves.

**2. Missing tool.** Three absences with demonstrated cost: (a) the Q-B3 crash-copy reader — proposed by a $3.66 review (`peer_run6_regression.log:3`), never built or run, leaving the error-2 cause open after three crashes; (b) a waiter-log class in `logclass` — its absence is what let 5 `wait_c37_*`/`wait_priorart_*` logs fill the build budget; (c) cost capture for judgement `claude -p` cells and killed dispatches — carried forward from retrospective-cycle31 F4 (`STATUS.md:46`) and bit again: the two dead retros' spend is unattributable anywhere.

**3. Unmeasured steps.** Run 7's J2(b) gate read the **VI-wide** wire count (1937→1841, `build_d1_routeb_v4_run7.log:420`) where the per-diagram count was available — v5's K2 is precisely that repair, one run late; and the run-6 review had to point out that `sink wire 0 -> 0` "is NOT a measurement, it is the initialiser" (`STATUS.md:25`) — a reading presented as one. Both were caught by paid reviews instead of at build time. Credit where due: the K2 `net_map` rejection was measured, not preferred (`gscript.py:2507-2516`, run8 §3), and the crash copy's md5/ExecState were measured rather than assumed.

**4. Rule compliance.** Broken: A4 (audit FAIL) — 6+ reviews with blank dispositions, the same six named for two prior cycles; the annotation discipline holds only inside the priorart/retro scope the device gates. Broken in effect: "every cycle ends with a RETROSPECTIVE" (CLAUDE.md §3) — formally attempted for cycles 37 and 38, actually discharged for neither, because the OPEN-54 foreground rule was evaded twice. Satisfied genuinely: A5 (original untouched, md5 `2a78e17c…` before/after every run), A1/A2 on real builds, prior-art before every launch, the material brief's refusal to self-clear the gate (run8 §3). What the audit does NOT cover: A2 sees only build logs, so the two dead retro bgruns are invisible; C4's $114.2799 counts only `peer_*`/`priorart_*` logs — in-window retro costs (e.g. $4.4824, `retro_c36.log:5`) and all judgement-cell spend are outside it, so it is a floor; C7 checks scope against `docs/cycle27-plan.md` — `docs/cycle39-plan.md`, which this task names as the cycle's plan, **does not exist**; and the window itself is a superset: the same 23:08:56 start served the c37 (104 min), c38 (197 min) and c39 (277 min) retro dispatches, so per-cycle cost attribution inside it is impossible — C5's 560 min of wall-clock inside a 277-min window is parallel machinery, not one cycle's serial time.

**5. Ordering.** The macro-order obeyed the user's 21:3x directive — the first act was a D1 build (run 5 launched 23:50 after its prior-art cleared at ~23:35), and machinery repairs (c37 stall clauses) came after. Two inversions: run 7 before the Q-B3 discriminator (finding 1), and the 00:53 retro launched as the session's last backgrounded act instead of a held foreground wait — the single cheapest reordering in the window, worth the whole run-8 strand.

**6. What was not reported.** STATUS is unusually candid about the block and even the waiter miscount. What it omits: (a) any mention that the cycle-37 and cycle-38 retrospectives were dispatched and died — `retro_c37.log` and `retro.log:216` are the only trace, yet this is the direct cause of the run-8 refusal STATUS does report; (b) the fifth stall false positive is described only as "discharged", not as the fifth misfire of a device measured at 0/4 precision whose named repair was declined; (c) the review-to-build ratio: 21 review/machinery dispatches against 3 real builds, with C4's $114.28 (a floor) against ~154 min of build time — reviews are 72% of wall-clock (audit C5), and roughly $9.41 of that spend serviced the machinery's own misfires rather than D1.

**7. Judgement inside a material session.** The boundary largely held, and visibly: C6 shows 14 judgement-session material attempts refused, and the run-8 material dispatch measured the blocking gate in-process and stopped — "whether this cycle closes now or the waiter-log classification is repaired first is judgement's call" (`archive/2026-09-19-status-cycle39-run8.md:93`), with no `CYCLE_GUARD_OFF`, no self-run retro. One borderline instance: the choice to implement K2 with `build_d1_v0.wmap` instead of the peer-proposed `net_map` was made inside material dispatch 3 (run8 §3:43-52) — technically rejecting a review's proposal, but it rests on a cited measurement (`gscript.py:2507-2516`: `net_map` would have fired the reaper K1 removes, twice, inside the row loop) and the J-disposition itself is credited to the judgement session; a finding, not a breach.

## DEVICE EFFECT

- **`unreported-fact` (rc/END guarantee, 2026-09-16):** FAILED — two bgrun dispatches ended with no `BGRUN END|TIMEOUT` line ever written (`retro_c37.log:3`, `retro.log:218`) and A2 still reports all runs accounted for; a dispatch that died looks like one still running.
- **`rule-evaded` (confirm-bait refusal):** held; hypothesis dispatches carried the adversarial set.
- **`tool-not-built` (prior-art):** worked — both priorart rounds preceded their builds and run 6's returned 4 real findings that changed v3 (`priorart_d1_routeb_run6.log:4`, $5.4953).
- **`repeated-failure-class` (blank-disposition refusal):** held inside its scope — the `FIXED:` lines were written into the run-7 and priorart reviews before v5 (`STATUS.md:21`); A4's blanks all sit outside the kinds it gates.
- **`unreported-fact` (C3/C4 split):** mechanically worked (C4b 10/10) but blind to retro and judgement costs — degraded, the F4 finding still open.
- **`premature-build` (guard_cycle):** worked — ALLOW on run 8 after real `FIXED:` lines citing v5 (run8 §3 gate table).
- **`scope-creep` (C7 counter):** fired and listed 12 files; verdict correctly left to this review (the 12 are the cycle's own recipes/repairs, not creep) — but it counts against a plan two numbering-generations old.
- **`device-failed` (cost regex):** held (C4b 10/10 parsed).
- **`device-failed` (bgrun FAIL-scan):** held on builds — runs 5/6/7 all ended rc=1 on real crashes.
- **`repeated-failure-class` (`OpLoopEndRef_v0`):** not exercised this window.
- **`device-failed` (stop record + launch gate, 2026-09-18 00:53):** FAILED — measured mechanically unusable on its `--recipe` path and worked around via `--no-recipe` (`STATUS.md:24`; review $3.2492, `peer_stoprecord_deadlock.log:34`).

Off the list but of the same kind: the stall watchdog (0/4 measured precision, fifth false positive at `stall_pid7288_023957.log:1` after the named repair was declined) and `logclass.is_build_log` (5 waiters counted as builds, run8 §3:80-89). Three on-file devices failed plus two adjacent ones; threshold is 1; the second machine line below carries the family, ranked by what it did to the cycle's ending.

VIOLATION: repeated-failure-class | loss_min=30 | loss_usd=? | evidence=tools/bench/retro_c37.log:3
VIOLATION: device-failed | loss_min=45 | loss_usd=9.41 | evidence=build-log-classifier+stall-watchdog+stop-record@archive/2026-09-19-status-cycle39-run8.md:80

## Sources

(extract from answer)

## What was done with it

Disposed in full by the cycle-39 judgement session, 2026-09-19, immediately on receipt. Both violations ACCEPTED;
neither is answered with a new device (user's standing order of 2026-09-18 08:53).

**`repeated-failure-class` — ACCEPTED, and it is the cycle's most useful finding.** The reviewer is right that
cycles 37 and 38 each launched a retrospective and then exited, killing the child (`tools/bench/retro_c37.log:1-3`
at 00:53:11 with the runner's mtime nine seconds later; `tools/bench/retro.log:216-218` at 02:26:12), so neither
was archived and `guard_cycle`'s `since` list kept accumulating from cycle 36 until it refused run 8. The clock
counterfactual is accepted as stated: run 8 would have launched around 03:30.

DECISION: no-device. The rule already exists in capitals at `STATUS.md` OPEN 54 and needed no device — it needed a
usable WAIT. **This cycle did not repeat the fault**, and the mechanism that prevented it is written into
`STATUS.md` `## NEXT` so the next session inherits it rather than re-deriving it: launch the retrospective with
`run_in_background`, then hold the turn with repeated **bounded** `py tools/wait_logs.py <task-output-file>
--seconds 25` calls (the hook `tools/hooks/guard_bash.py` permits a foreground wait only at timeout <= 30 s, which
is why the single long wait that earlier sessions reached for is refused, and why they backgrounded and left).
Note the flag spelling: `wait_logs.py` takes `--seconds`, not `--max-min`. Also recorded: `tools/bench/retro.log`
is APPEND-SHARED across cycles, so grepping it for `BGRUN END` matches OLD runs — wait on the task's own output
file instead. That mistake cost this session one wasted watch.

**`device-failed` (three instances, threshold 1) — ACCEPTED as findings, recorded in `docs/violation-decisions.md`.**
All three are real and all three are measured: (a) `logclass.is_build_log` counts `tools/wait_logs.py` waiter logs
as builds, and five of the ten logs that filled `CYCLE_BUILD_BUDGET` were waiters against only three real builds —
this is what actually refused run 8; (b) the stall watchdog's precision is now **0/5**, a fifth false positive
having fired during run 7 (`tools/bench/stall_pid7288_023957.log:1`, "no modal dialog", while the client was alive
and ran on to its own crash), at a logged cost of $3.1519 + $3.0051 in reviews written only to clear its misfires;
(c) the stop record + launch gate is mechanically unusable and cost a $3.2492 review to diagnose.

DECISION: no-device for (a) and (c) — both are worked around and neither is on the deliverable's critical path
now that retrospectives land again. **DECISION: repair-authorised for (b), ONE line, and it is a repair of an
existing device, not a new one.** Judgement's grounds, and this is a call the user may overturn: the watchdog has
been wrong every single time it has fired, each record blocks the next build until a peer review clears it, and
the repair was already named and peer-reviewed in `archive/peer/2026-09-19-stall-waitlogs-c37b.md` — write the
gating `stall_pid*.log` only when the dialog check at `tools/lv_stallcheck.ps1:257` returns `VERDICT: BLOCKED`
(all records so far say "no modal dialog", so the correct count written is zero). It is scheduled in `## NEXT`
**after** run 8 launches, never before, per the user's ordering rule that no machinery repair precedes a D1 build
dispatch.

**One `unreported-fact` sub-finding also accepted, no slug raised:** bgrun's "always writes a final `END|TIMEOUT`
line" guarantee does not survive an external kill, and `audit_cycle` A2 still reports "all runs accounted for"
because it scans build logs only — so a dispatch that died silently is invisible to the check that exists to see
it. This is the already-open gap (e) from cycle 36 and is not re-opened here.
