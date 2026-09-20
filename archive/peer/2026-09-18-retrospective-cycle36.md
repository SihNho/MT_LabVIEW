# retrospective-cycle36

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $4.4824  in 18 / out 30012 / cache-create 114230 / cache-read 697055  (423s, 15 turn(s))
- **date:** 2026-09-18 23:08:56
- **outcome:** ANSWERED (424s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 36 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-18 20:38:36  ..  2026-09-18 23:01:51   (143 min)
    basis: start = archive/peer/2026-09-18-retrospective-cycle35.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-18 20:38 .. 2026-09-18 23:01 (143 min, an explicit cycle window): 8 build logs, 14 peer logs, 57 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 8/8 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 5 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 49/57 annotated; blank: ['2026-09-18-asi-soft-limits-sl-su.md', '2026-09-18-ff-selftest-bgrun-start-regex-codex.md', '2026-09-18-ff-selftest-bgrun-start-regex-opus.md', '2026-09-18-ff-selftest-drycmd-split-codex.md', '2026-09-18-ff-selftest-drycmd-split-opus.md', '2026-09-18-pi-c863-soft-limits.md']??
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1800 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 29, failure markers 11, logs carrying a failure 5
  C2 peer reviews dispatched 14, archived 57
  C3 wall-clock inside bgrun, BUILDS ONLY 649 min 53 s
  C4 wall-clock inside bgrun, REVIEWS 108 min 19 s; cost $19.2568 from 6 log(s) that report one
  C4b cost lines seen 6 / parsed 6
  C5 total wall-clock 758 min 12 s  (reviews are 14% of it)

  C6 material-marked recipe/bench runs 12, judgement-session attempts refused 4  <- delegate to the `material` agent instead

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 13 - STATUS.md, docs/violation-decisions.md, tools/bench/c36_close_runner.py, tools/bench/peer_task_c36_selftest.md, tools/bench/peer_task_stall_c36.md, tools/bench/repair_c36_selftest.py, tools/bench/selftest_bgrun_final_line.py, tools/bench/task_routeb_run4_error2_zdz.md, tools/bgrun.py, tools/hooks/material_marker.log, tools/lv_stallcheck.ps1, tools/recipes/build_d1_routeb_v1.py??


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 281/466 ok; 185 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 857 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 12 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  WARN  L2b cited line numbers are in range: 1 citation(s) point past the end of the file: ['docs/NAMES.md:1008 -> docs/toolkit-capabilities.md:775 (file has 630 lines)']
  WARN  L3 STATUS.md stays one screen: STATUS.md:138 lines > 110. CLAUDE.md rule 4: move the narrative to archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 225 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:583', 'docs/NAMES.md:856', 'docs/NAMES.md:870', 'docs/NAMES.md:888', 'docs/NAMES.md:915']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (8; read them directly, they are the primary record) ===
tools/bench/build_d1_routeb_v1_run4.log  (2026-09-18 22:41:57)
tools/bench/c36_close_runner.log  (2026-09-18 22:02:17)
tools/bench/probe_bgrun_env_c36.log  (2026-09-18 21:00:13)
tools/bench/repair_c36_selftest.log  (2026-09-18 21:00:13)
tools/bench/selftest_bgrun_final_line.log  (2026-09-18 21:48:05)
tools/bench/wait_outcome_c36.log  (2026-09-18 21:31:13)
tools/bench/wait_outcome_c36b.log  (2026-09-18 21:34:00)
tools/bench/wait_runner_exit.log  (2026-09-18 20:40:37)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (15) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_21.log  (2026-09-18 20:40:22)
tools/bench/cycle_22.log  (2026-09-18 20:41:28)
tools/bench/cycle_runner.log  (2026-09-18 20:40:22)
tools/bench/cycle_runner_main_20260918d.log  (2026-09-18 20:40:22)
tools/bench/cycle_runner_main_20260918e.log  (2026-09-18 20:41:28)
tools/bench/doc_ingest_c36.log  (2026-09-18 22:02:17)
tools/bench/outcome_review_c36.log  (2026-09-18 21:34:00)
tools/bench/peer_c36_selftest.log  (2026-09-18 21:57:04)
tools/bench/peer_routeb_run4.log  (2026-09-18 22:57:57)
tools/bench/peer_stall_c36.log  (2026-09-18 21:12:53)
tools/bench/priorart_d1_routeb_v1.log  (2026-09-18 21:42:16)
tools/bench/retro_c35.log  (2026-09-18 20:38:36)
tools/bench/retro_c36.log  (2026-09-18 23:01:51)
tools/bench/stall_pid11424_221324.log  (2026-09-18 22:26:55)
tools/bench/stall_selftest_c36_inner.log  (2026-09-18 21:00:13)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle36-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

All evidence is in hand. Here is the retrospective of cycle 36.

# RETROSPECTIVE — cycle 36 (2026-09-18 20:38:36 → 23:01:51)

## What the cycle produced (baseline for every judgement below)

Cycle 36 did end with a D1 build log: `tools/bench/build_d1_routeb_v1_run4.log` (BGRUN START 22:13:24, END rc=1 after 1713s, line 354) — 80 PASS / 1 FAIL (the Z/dZ row, line 164) followed by an error-2 crash inside `settle_index_modes`. The mandatory failed-prediction review (`tools/bench/peer_routeb_run4.log:2-3`, ANSWERED 566s, $3.9657) refuted both of the session's claims from the project's own files, and the judgement session accepted it in full and specified run 5 down to four line-level patches (STATUS.md:62-71, 89). That is real product. The cycle was not worthless — but it was late, and its lateness is the structural fault.

## FINDINGS

**1. Repeated failure.** Yes, twice over. (a) The stall-watchdog false-positive class is now on its third consecutive cycle: cycle 35's retrospective charged it as its top fault ($5.78, `archive/peer/2026-09-18-retrospective-cycle35.md:238`); cycle 36 then paid $3.1587 / 8.5 min (`tools/bench/peer_stall_c36.log:3`) to discharge cycle-35's stall record, ran the F1–F4 probes and measured the record a false positive (F2/F3/F4 all False — `tools/bench/repair_c36_selftest.log:115-116, 227-228, 346-347`; STATUS.md:95) — and the same watchdog then fired again mid-window, on run 4 itself: `tools/bench/stall_pid11424_221324.log:1` records "CPU +0.00s in the last 113s" at 22:26:52 for a process that ended under its own power 15 minutes later (`build_d1_routeb_v1_run4.log:354`). The approach should have changed at the second occurrence, i.e. in cycle 35: either build the CPU-liveness remedy both review arms discussed (STATUS.md:50, remedy "not built") or stop letting a stall record gate builds until it is validated. Cycle 37 inherits another record of the same class. (b) `repair_c36_selftest` took four attempts (3× rc=1, 20:51→20:59, `repair_c36_selftest.log:15,122,234,353`) — normal iteration, not structural.

**2. Missing tool.** The in-run handle sampler. Run 4's crash is undecidable on the existing record precisely because no handle reading brackets the failing call — the review's whole discriminating test is two lines calling `labview_handles()`, a function that already exists and is already imported elsewhere (`peer_routeb_run4.log:66-77`). Worse, the `finally:` block deleted the crashed working copy, so the state can no longer be examined at any price (`peer_routeb_run4.log:81`). Both repairs are now in the run-5 spec, but the $3.97 review and the whole run-4 ambiguity are what their absence cost.

**3. Unmeasured steps.** The two claims the session sent to the failed-prediction review were both inferences refutable by grep of our own files: claim 1 blamed a handle count that was never measured at the crash (the only reading, 51,284, is the count at which the identical call *succeeded* — `build_d1_routeb_v1_run4.log:26-27`), and claim 2 declared "no by-index route" for a route already implemented in the same recipe at `:1257-1278`, disabled by one boolean at `:285` (`peer_routeb_run4.log:87-98`). The review is mandatory either way, but $3.9657 was spent having an opus/max cell reread files the session had open.

**4. Rule compliance.** A4 fails: 6 blank "What was done with it" sections dated in-window (audit A4 line), on top of a chronic 49/57. The task names this cycle's plan as docs/cycle36-plan.md; that file does not exist — the current plan is docs/cycle27-plan.md (audit C7, doc_lint L4), which is formal drift the audit tolerates. What the audit does NOT cover: (a) the judgement session itself (`tools/bench/cycle_22.log`, opus/max, ~140 min) carries no COST line, so C4's $19.2568 understates real spend — already flagged at STATUS.md:49; (b) C3's duration parser counts *quoted* log lines as real wall-clock (see Device effect — this is the big one); (c) nothing in the audit measures ordering against the user's standing direction, which is exactly where this cycle went wrong. Formally satisfied: retrospective last (23:01:51), peers under bgrun, priorart before build, originals untouched (A5).

**5. Ordering.** Not defensible, and it is the named fault. Timeline: judgement session up 20:41; machinery repairs 20:51–21:00; stall review (mechanically forced) done 21:12:53; outcome review 21:30–21:34; prior-art gate for the D1 recipe clear at 21:42:16 (`priorart_d1_routeb_v1.log:162`). At that moment every gate on the cycle's one deliverable was open. The session instead ran the bgrun final-line selftest (21:48, standalone run rc=1 — `selftest_bgrun_final_line.log:16`), dispatched a $2.7466 opus/max review of that selftest (`peer_c36_selftest.log:1-3`, 21:49–21:57), and ran the close-runner with doc_ingest (21:58–22:02) — cycle-*close* machinery, run before the cycle's build — dispatching D1 only at 22:13:24, minute 95 of 143. And the user's live message at 21:3x said exactly this ("NO machinery repairs, NO watchdog reviews … before that dispatch has RUN", STATUS.md:56-61); the session's own defense (STATUS.md:91-92) covers only the pre-21:3x STEP 0 block, not the 21:48–22:02 block. Counterfactual on the clock: earliest compliant dispatch ≈ 21:32 (stall review discharged 21:13 + 8 min priorart + ~11 min prep); actual 22:13:24 — 41 minutes lost. Run 4 then ends ~22:00, the review ~22:16, and the four run-5 patches (all decided by 22:5x anyway) plus the ~28-min run 5 land inside the window by ~22:50. The cycle would have ended with run 5's S3w ledger and the Z/dZ discriminator instead of instructions to cycle 37 to obtain them — a full cycle's spin-up (judgement session plus ~$3.6 retrospective, by retro_c35.log:5's precedent) deferred onto the next window.

**6. What was not reported.** Three things the summary hides or muddles. (a) The fresh stall record fired *during run 4* (`stall_pid11424_221324.log:1`) — STATUS.md never mentions it; it is discharged only incidentally, because `peer_routeb_run4` (archived 22:57) happens to be newer. (b) The audit's C3/C5 figures are phantom (649 of the claimed 758 minutes are impossible in a 143-minute window — see Device effect); nothing anywhere says the cost lines are contaminated. (c) STATUS.md:97 cites `tools/bench/selftest_bgrun_final_line.log` as the green "8/0" record, but that file's own final line is a failure (`BGRUN END rc=1 after 3s`, line 16); the green 8/0 run lives inside `c36_close_runner.log:13-14`. A reader following the citation sees a failing log.

**7. Judgement inside a material session.** Nothing clear inside this window. The four decisions after run 4's review were taken and marked by the judgement session (STATUS.md:89, "ALL FOUR ANSWERED — cycle-36 judgement"); `c36_close_runner` executed only pre-scripted gates and one bookkeeping rename (`c36_close_runner.log:22`). The one boundary case — a sub-session having created `tools/wait_logs.py` — is already disclosed to the user at STATUS.md:125-129, and the *keeping* decision was made in judgement; the creation predates a clean in-window attribution, so I do not charge it here.

## DEVICE EFFECT

Ten of the eleven devices either held or were not exercised: the rc-masking fix held (run 4's inner FAIL and exception ended `rc=1`, A2 8/8); the confirm-bait refusal shows no in-window bypass (both hypothesis reviews came back refuting); prior-art ran before the build and released it ($5.5237, `priorart_d1_routeb_v1.log:4`); the premature-build guard held (build 22:13 > priorart 21:42); the scope-creep counter fired correctly (its 13-file list is largely the machinery that displaced D1 — it fed this verdict); the cost-regex repair held (C4b 6/6); the FAIL-scan held; the blank-disposition guard, `OpLoopEndRef_v0` and the stop-record gate were not triggered on their own terms (though the disposition guard's narrow priorart/retrospective scope is why A4 can sit at 49/57 without anything refusing).

**One device failed: the C3/C4 cost-line device (`unreported-fact`, decided 2026-09-16 15:05), whose one job is to make the cost argument "possible instead of rhetorical."** The attached audit reports C3 = 649 min 53 s of build wall-clock inside a 143-minute window. The eight listed build logs' genuine in-window END lines sum to ≈39 minutes (run 4's 1713s, close-runner 199s, repair 267s, wait_outcome 160s, and small change; `wait_runner_exit`'s 4022s run started 19:33:35, pre-window). The other ~606 minutes are *quoted* lines: `repair_c36_selftest.log` reproduces `BGRUN END rc=0 after 4022s` six times and `after 4076s` three times as F2/F4 probe evidence (lines 44, 115-116, 156, 227-228, 275, 346-347), and `audit_cycle.py:312` matches them unanchored, wherever they sit in a line (6×4022 + 3×4076 = 36,360s ≈ 606 min). C5 (758 min) inherits the error. This is the exact failure class the project has repaired twice before under `device-failed` (the COST regex on 2026-09-16 21:07, the FAIL-scan on 2026-09-17 03:38): quoted evidence parsed as measurement — and `c36_close_runner` even sanitizes its own quotes to `rc<eq>0` (`c36_close_runner.log:3`) to prevent precisely this, a defense C3's duration scan lacks. C4b guards dollar lines only; durations have no seen/parsed check. Every future loss-minute argument, including the ones this format demands, is built on that line. Threshold is 1; it fired wrong this window; it is broken.

## Verdict

One structural fault of the cycle's own running (the deliverable dispatched at minute 95 of 143, after the gate cleared at 21:42 and after the user's live order, pushing an already-fully-specified run 5 into the next cycle), plus the mandated device-failure emission for the C3 cost line. The dollar figure on the first is the one log-carried cost sitting inside the displaced interval (the machinery review at `peer_c36_selftest.log:3`); the delay itself carries no COST line, so the true dollar loss — most of a deferred cycle — is larger but not log-carried. The device failure cost no wall-clock this cycle; its loss is the validity of the audit's own numbers, for which no log carries a dollar.

VIOLATION: wrong-ordering | loss_min=41 | loss_usd=2.7466 | evidence=tools/bench/build_d1_routeb_v1_run4.log:1
VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/repair_c36_selftest.log:44

## Sources

(extract from answer)

## What was done with it

Disposed by the cycle-37 judgement session, 2026-09-19. Per finding: accepted or refuted, and where it landed.

**`VIOLATION: wrong-ordering | loss_min=41 | loss_usd=2.7466` — ACCEPTED.** Answered `DECISION: no-device` in
`docs/violation-decisions.md` (2026-09-18 23:09) under the user's standing 08:53 no-more-devices order, so it was
acted on structurally rather than mechanically. The remedy was the user's own 21:3x instruction, written into
`STATUS.md` `## NEXT`: a cycle's FIRST act is the D1 build dispatch. Cycle 37 complied — its first act was the
run-5 D1 dispatch, and every machinery repair, watchdog review and doc relocation happened afterwards, in
dispatches 3 and 4. Evidence that the ordering held: `tools/bench/build_d1_routeb_v2_run5.log`.

**`VIOLATION: device-failed | loss_min=0` (threshold 1) — ACCEPTED, no device built.** `DECISION: no-device` in
`docs/violation-decisions.md` (2026-09-18 23:09), recorded as a FINDING because the threshold rule is SUSPENDED by
the user's order of 2026-09-18 08:53 (CLAUDE.md §3, "Every cycle ends with a RETROSPECTIVE", item 3).

**Finding (i) — the cycle-36 stall record was discharged only incidentally ("do not rely on that next time").
ACCEPTED AND ACTED ON.** The class fired twice more in cycle 37. Both times a peer review was dispatched
DELIBERATELY rather than relied on incidentally: `archive/peer/2026-09-18-stall-waitlogs-c37.md` and
`archive/peer/2026-09-19-stall-waitlogs-c37b.md` (both ANSWERED, opus/max). `tools/lv_stallcheck.ps1:136` now skips
`tools/wait_logs.py` leaves, which produced two of the four records of this class; self-test 6/6,
`tools/bench/repair_c37b_selftest.log`. ⚠️ Residual carried into cycle 37's NEXT, not fixed here: the c37b reviewer
MEASURED that all four records were false positives — neither build client was killed at its deadline — so the
clause moves precision 0/4 → 0/2, and its one-line alternative (write the record only when the dialog check at
`tools/lv_stallcheck.ps1:257` returns `VERDICT: BLOCKED`) is NOT built.

**Finding (ii) — `audit_cycle`'s C3/C5 cost figures are PHANTOM (649 of 758 claimed minutes impossible inside a
143-minute window). ACCEPTED, NOT FIXED.** Honoured negatively in cycle 37: no cost number from any `audit_cycle`
run was quoted in this cycle's record, in STATUS, or to the user. The only cost figures used are the peers' own
`COST:` lines. The repair is unbuilt and named in `STATUS.md` `## NEXT`.

**Finding (iii) — the bad `tools/bench/selftest_bgrun_final_line.log` citation. ACCEPTED; already fixed before this
review was archived.** The correct green record is `tools/bench/c36_close_runner.log:13-14` (8/0).
