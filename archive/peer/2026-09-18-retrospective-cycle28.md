# retrospective-cycle28

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $3.8577  in 12 / out 23252 / cache-create 114055 / cache-read 413880  (329s, 12 turn(s))
- **date:** 2026-09-18 16:42:54
- **outcome:** ANSWERED (330s)
- **why asked:** cycle 28 exited without its retrospective; cycle 29 ran it at 16:37 to pay the debt. Its window is 14:07:40–16:37:22, so it is in fact cycle 29's own closing review under cycle 28's label (see `archive/peer/2026-09-18-retro-closes-session.md`).
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 28 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-18 14:07:40  ..  2026-09-18 16:37:22   (150 min)
    basis: start = archive/peer/2026-09-18-retrospective-cycle26.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-18 14:07 .. 2026-09-18 16:37 (150 min, an explicit cycle window): 12 build logs, 16 peer logs, 39 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  FAIL  A1 every build log came from bgrun: 11/12 ok; NO BGRUN line in ['motor_gate.log']
  FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['p2_open_copy.log']
  PASS  A3 every failing log is followed by an archived review: 4 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 31/39 annotated; blank: ['2026-09-18-asi-soft-limits-sl-su.md', '2026-09-18-ff-selftest-bgrun-start-regex-codex.md', '2026-09-18-ff-selftest-bgrun-start-regex-opus.md', '2026-09-18-ff-selftest-drycmd-split-codex.md', '2026-09-18-ff-selftest-drycmd-split-opus.md', '2026-09-18-pi-c863-soft-limits.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1775 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 19, failure markers 8, logs carrying a failure 4
  C2 peer reviews dispatched 16, archived 39
  C3 wall-clock inside bgrun, BUILDS ONLY 0 min 52 s
  C4 wall-clock inside bgrun, REVIEWS 52 min 46 s; cost $22.1619 from 4 log(s) that report one
  C4b cost lines seen 4 / parsed 4
  C5 total wall-clock 53 min 38 s  (reviews are 98% of it)

  C6 material-marked recipe/bench runs 19, judgement-session attempts refused 14  <- delegate to the `material` agent instead

  C7 out-of-plan files: no docs/cycle<N>-plan.md found - scope cannot be checked mechanically


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 281/448 ok; 167 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 775 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  WARN  L3 STATUS.md stays one screen: STATUS.md:112 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 176 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:915']

AUDIT VIOLATIONS: A1 every build log came from bgrun, A2 every bgrun ended (END or TIMEOUT), A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (12; read them directly, they are the primary record) ===
tools/bench/motor_gate.log  (2026-09-18 15:59:00)
tools/bench/motor_gate2_live.log  (2026-09-18 15:59:02)
tools/bench/p2_asi_query_limits.log  (2026-09-18 15:09:15)
tools/bench/p2_asi_set_limits.log  (2026-09-18 15:23:21)
tools/bench/p2_open_copy.log  (2026-09-18 14:35:35)
tools/bench/p2_pi_query_ron.log  (2026-09-18 15:51:16)
tools/bench/p2_pi_ron_off.log  (2026-09-18 15:08:40)
tools/bench/p2_pi_softlimit_test.log  (2026-09-18 14:50:37)
tools/bench/p2_pi_softlimit_test2.log  (2026-09-18 15:08:52)
tools/bench/p2_pos_before.log  (2026-09-18 14:32:25)
tools/bench/selftest_audit_cost_window.log  (2026-09-18 16:26:03)
tools/bench/selftest_motor_gate2.log  (2026-09-18 15:53:20)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (16) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_14.log  (2026-09-18 14:11:36)
tools/bench/cycle_15.log  (2026-09-18 16:34:50)
tools/bench/cycle_16.log  (2026-09-18 16:34:50)
tools/bench/cycle_runner.log  (2026-09-18 16:34:50)
tools/bench/cycle_runner_main_20260918c.log  (2026-09-18 14:11:36)
tools/bench/cycle_runner_main_20260918d.log  (2026-09-18 16:34:50)
tools/bench/peer_asi_softlimits.log  (2026-09-18 14:50:49)
tools/bench/peer_permdeadlock.log  (2026-09-18 16:32:50)
tools/bench/peer_pi_err5.log  (2026-09-18 15:51:51)
tools/bench/peer_pi_softlimits.log  (2026-09-18 14:45:52)
tools/bench/peer_prose_controller_limits.log  (2026-09-18 16:23:48)
tools/bench/peer_roles_selftest.log  (2026-09-18 16:07:54)
tools/bench/peer_stall_p2_open_copy.log  (2026-09-18 14:49:32)
tools/bench/retro.log  (2026-09-18 16:37:22)
tools/bench/retro_cycle26.log  (2026-09-18 14:07:40)
tools/bench/stall_pid20500_143532.log  (2026-09-18 14:45:28)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle28-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

## Verdict first

Cycle 28 was a productive cycle — arguably the most productive in days: live-verified controller soft limits on both stages (10/10 gates, `tools/bench/motor_gate2_live.log:279`), the ERR-5/unreferenced-axis defect found and fixed, the material-marker deadlock broken (STATUS OPEN 52a), the audit cost window repaired and self-tested 7/0 (`tools/bench/selftest_audit_cost_window.log`), and the D0 copy opened runnable with the original's md5 unchanged (`tools/bench/p2_open_copy.log:2-7`). Total logged spend $22.16 / ~54 min machine wall-clock inside a 150-min window, and it closed OPEN items 51, 52, 52a and 53.

The one structural fault is that the project's own verification devices got the cycle's two most important runs **wrong in both directions**, and only human reading corrected the record. That is `device-failed`, and the task's own threshold for it is 1.

- **False PASS (the exact fault the 2026-09-16 `unreported-fact` device exists to stop, and it never fired):** in the 15:37 live run, gate L4 printed `RESULT: reached 0 (target 0)` and `PASS L4 PI back at 0` while `ERR? right after send = 5` — the axis never moved; it was simply already at 0 (`tools/bench/motor_gate2_live.log:55-60`). No scan caught it; it was caught by the opus arm of the pi_err5 review (STATUS.md:80-82: "L4's 'MOV 1 0 reached 0' … was a FALSE PASS"). Had L2/L3 not happened to fail in the same run, an entirely motionless PI test would have been recorded as a passing one.
- **False FAIL (the 2026-09-17 03:38 failure-scan device fired on the wrong thing):** the 15:58 rerun passed 10/10, yet bgrun forced `rc=1` because its scan matched the *expected* controller refusal being tested — `BGRUN INNER FAILURE … first: … REJECTED BY THE CONTROLLER` (`tools/bench/motor_gate2_live.log:280-281`). The same misfire hit the gate's own selftest (`tools/bench/selftest_motor_gate2.log:93`, "inner failure; the process itself said 0"). This is not cosmetic: `BGRUN END rc≠0` is the exact token `cycle_runner` reads to trigger firefighter cycles (CLAUDE.md §3.2), and it inflates C1's "failure markers 8 / logs carrying a failure 4" that A3 review obligations hang on. The cycle's flagship result now exists in the machine record as a failure and in STATUS as a success — the next audit, gate, or firefighter decision reads the machine record.

Counterfactual for the false FAIL alone: had the scan carried a refusal-class exception, the 15:53 selftest rerun and the rc=1 corrections would not have happened and the record would need no prose override (~10 min). The deeper loss — a possible spurious firefighter cycle — did not materialize this window, so I do not charge it.

A second candidate of the same family, reported in prose rather than as a second line: **the scope-creep device was blind for the whole cycle.** `audit_cycle` C7: "no docs/cycle<N>-plan.md found — scope cannot be checked mechanically", because cycle 28 deliberately runs on `docs/cycle27-plan.md` (STATUS.md:90) and the device only looks for the cycle's own number. Files like `tools/hooks/guard_bash.py` and `tools/audit_cycle.py` were modified in-window with no mechanical out-of-plan listing possible. It never fired when it should have.

## FINDINGS

**1. Repeated failure.** The ERR-5/no-motion class occurred three times: probe `MOV 1 40 → ERR 5, no motion` at 14:50 (`tools/bench/p2_pi_softlimit_test.log:16-17`), fixed manually at 15:08 (`p2_pi_ron_off.log:2-4`, RON 1 0 + POS 1 0 → FRF 1, and `p2_pi_softlimit_test2.log:6-9` then passed), then it recurred at attempt 3, the 15:37 live gate run (`motor_gate2_live.log:25-46`) because each `--session start` re-runs SPA and SPA clears the reference. The approach should have changed **before attempt 3**: the manual RON repair demonstrated at 15:08 should have been folded into the gate's session-start before any live run. That would have removed the failed 15:37 run, the 21-minute gap to the 15:58 pass, and (with no failed prediction) the mandatory $3.8839/722 s pi_err5 review (`tools/bench/peer_pi_err5.log:86`). Mitigating: the causal link "SPA itself clears FRF" was only proven by the recurrence, so I score this a finding, not the violation.

**2. Missing tool.** A reference-state readback in the gate's DRY mode. The 15:34/15:35 DRY passes (`tools/bench/motor_gate.log:83-86`) validated ALLOW/REFUSE classification only; a DRY-mode `FRF?/RON?` assertion would have shown FRF=0 at 15:34 and answered the 15:37 L2/L3 failures before they happened. It was effectively built into the gate afterwards (`REFSTATE RON=0 FRF=1 …`, `motor_gate2_live.log:145`) — one run too late.

**3. Unmeasured steps.** Minor only. The stall review's named cheapest test (`py-spy dump --pid 20500`, `tools/bench/peer_stall_p2_open_copy.log:15-23`) was never run; "deliberate sleep" was accepted from the script's own code and its log line ("holding references 10000 s", `p2_open_copy.log:8`) — which is itself a measurement of intent, so acceptable. Nothing decision-bearing was left to inference.

**4. Rule compliance.** Real breach: A4 — six archived reviews with blank "What was done with it" (`2026-09-18-asi-soft-limits-sl-su.md`, the four ff-selftest files, `2026-09-18-pi-c863-soft-limits.md`); the soft-limits reviews were plainly consumed (the limits were set at 15:23, `p2_asi_set_limits.log`) but never annotated — the annotation discipline holds only inside the narrow priorart/retro device scope. A1 and A2, by contrast, are audit false positives, not session breaches: `motor_gate.log` is the gate's own transmit/decision trail dating to 09-17 (`motor_gate.log:1`), not a build log; `p2_open_copy.log` was still legitimately inside its 180-min bgrun limit at audit time (`p2_open_copy.log:1`). What the audit does not cover: cell-level false PASSes (L4), the true cost of codex arms (their logs carry no `COST:` line — `peer_asi_softlimits`, `peer_pi_softlimits`, `peer_stall_p2_open_copy` — so C4's $22.16 understates spend), the interactive user-present session's own tokens, and scope (C7 blind, above). C4's $22.1619 does reconcile exactly: 3.8839 + 3.6059 + 0.4017 + 14.2704 (`cycle_runner.log:21`) — the 16:26 repair works.

**5. Ordering.** Largely defensible: position snapshot → probes → limits → gate selftest → live → rerun. The one inversion is finding 1's: gate patch before live run. The side-item ordering (marker fix and audit repair inside runner cycle 15 at 16:10-16:34, after the user-present hardware work) was right — hardware while the user was present, bookkeeping after.

**6. Not reported.** STATUS.md:12-13 reports the live gate test as "10/10" without mentioning that the machine record of that same run is `BGRUN END rc=1` (`motor_gate2_live.log:281`) — anyone reconciling C1's failure counts against STATUS will find a contradiction with no pointer. Also the stall watchdog false-fired on the deliberate hold (`stall_pid20500_143532.log:1`, "CPU +0.00s") and cost a 118 s codex dispatch (`peer_stall_p2_open_copy.log:24`); STATUS does not record that the watchdog needs a "declared hold" concept.

**7. Judgement inside a material session.** None found. The deadlock disposition ("partial refutation accepted") and the marker-fix acceptance were taken in the cycle-15 judgement session (`archive/2026-09-18-status-cycle28-marker-fix.md:43-46`); the P2 decisions were taken with the user present (STATUS.md:12). C6 shows the boundary device working in the correct direction: 14 judgement-session material attempts refused, 19 material-marked runs executed.

## DEVICE EFFECT

- **`unreported-fact` (rc-vs-inner-failure, 2026-09-16):** FAILED — the fault it exists to stop occurred: L4's false PASS, `motor_gate2_live.log:57-60`, caught only by a reviewer (STATUS.md:80-82). Never fired.
- **`rule-evaded` (confirm-bait refusal):** no confirm-bait dispatched in-window; the stall task got the full adversarial treatment (`peer_stall_p2_open_copy.log:4-23`). Held.
- **`tool-not-built` (prior-art gate):** no recipe builds in-window (all 12 logs are diagnostics); not exercised.
- **`repeated-failure-class` (blank priorart/retro blocks dispatch):** in-scope reviews were annotated (retro_cycle26 annotated per STATUS); held — but A4's six blanks show the discipline leaks everywhere the device doesn't reach.
- **`unreported-fact` (C3/C4 cost lines):** works after the in-cycle 16:26 repair; C4b 4/4, sum reconciles to the cent. Held.
- **`premature-build` (guard_cycle):** no recipe launch attempted; not exercised.
- **`scope-creep` (C7 out-of-plan list):** FAILED — blind all cycle because the plan is numbered 27 (audit C7 line; STATUS.md:90). Never fired.
- **`device-failed` (cost-regex self-test, 2026-09-16 21:07):** held (C4b 4/4 parsed).
- **`device-failed` (bgrun FAIL-scan, 2026-09-17 03:38):** FAILED — fired on the wrong thing twice: `motor_gate2_live.log:280` (10/10 pass forced to rc=1 on an *expected* controller refusal) and `selftest_motor_gate2.log:93`.
- **`repeated-failure-class` (OpLoopEndRef_v0 reader):** not exercised (no D1 work in-window).
- **`device-failed` (stop record + launch gate, 2026-09-18 00:53):** not exercised (no recipe launches).

Three devices failed; the costliest single evidence is the bgrun failure-scan misfire on the cycle's flagship run, with the L4 false PASS as the same family's blind spot. One line, per the contract — the ranking above is the review.

VIOLATION: device-failed | loss_min=10 | loss_usd=? | evidence=tools/bench/motor_gate2_live.log:280

## Sources

(extract from answer)

## What was done with it

Annotated by the cycle-29 judgement session, 2026-09-18. ⚠️ Read §1 of
`archive/2026-09-18-status-cycle29-retro-trap.md` first: this retrospective was run by cycle 29 to pay cycle 28's
debt, and running it is what closed cycle 29 for material dispatches — so the actions below are the ones a session
with no material agent could take.

1. **`VIOLATION: device-failed` (bgrun FAIL-scan forcing rc=1 on an expected controller refusal,
   `tools/bench/motor_gate2_live.log:280`) — ACCEPTED as the ranking, recorded as a FINDING, no device built.**
   The user's standing order of 2026-09-18 08:53 ("장치는 더 만들지 말고 계속 진행") suspends the build-a-device
   response; `py tools/violations.py` confirms the slug is already answered (2026-09-18 00:53) and reports
   **0 slugs awaiting a response**, so `guard_cycle` does not hold cycle 30's build on it. Operational consequence
   carried into STATUS: **`motor_gate2_live.log` ending `rc=1` is a KNOWN FALSE RED** — the run was 10/10 with the
   controller's ERR 7 refusal being the expected result. Nobody should re-diagnose it.
2. **Finding 6 ACCEPTED and fixed this cycle**: STATUS.md reported the live gate test as "10/10" while the machine
   record of the same run says `BGRUN END rc=1`, with no pointer reconciling them. STATUS's hardware banner now
   carries both numbers and the reason.
3. **Finding 4 (A4: six archived reviews with blank "What was done with it") ACCEPTED, not fixed** — annotating
   six reviews is material bookkeeping and this session had no material agent. Handed to cycle 30 in STATUS NEXT.
4. Findings 1/5 (gate patch before live run) and the `scope-creep` C7 blindness (audit keyed to a plan numbered 27)
   noted, no action this cycle: both are process, and D0 delivery outranks them under the delivery-first re-plan.
