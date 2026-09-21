# retrospective-cycle63

- **agent:** claude
- **role:** outcome
- **model:** fable (effort medium; peer.ps1 default for role outcome)
- **kind:** fact
- **cost:** $2.7788  in 10 / out 18034 / cache-create 80563 / cache-read 265718  (253s, 13 turn(s))
- **date:** 2026-09-22 01:09:11
- **outcome:** ANSWERED (256s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RETROSPECTIVE (v2) of cycle 63 (read-only; you may open any file in the project).

=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===
    2026-09-22 00:16:21  ..  2026-09-22 01:04:53   (49 min)
    basis: start = archive/peer/2026-09-22-retrospective-cycle62.md stamp (the LAST retrospective written before this one; a plan mtime lags the work - see the docstring); end = now, at window computation (minutes before the dispatch itself; codex E4-1)
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

== cycle audit, 2026-09-22 00:16 .. 2026-09-22 01:04 (49 min, an explicit cycle window): 2 build logs, 7 peer logs, 4 archived reviews
   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)

  PASS  A1 every build log came from bgrun: 2/2 ok
  PASS  A2 every bgrun ended (END or TIMEOUT): all runs accounted for
  PASS  A3 every failing log is followed by an archived review: 1 logs recorded a failure; unreviewed: none
  FAIL  A4 every archived review says what was done with it: 3/4 annotated; blank: ['2026-09-22-c72-guisave-foreground.md']
  PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c?? mtime 2026-09-01 12:07
  PASS  A7 no archive note wikilinks into the active set: archive links stay inside archive
  n-a   A6 state-changing GUI actions are recorded: 1804 lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees

  C1 builds run 3, failure markers 2, logs carrying a failure 1
  C2 peer reviews dispatched 7, archived 4
  C3 wall-clock inside bgrun, BUILDS ONLY 9 min 36 s
  C4 wall-clock inside bgrun, REVIEWS 22 min 19 s; cost $3.6507 from 1 log(s) that report one
  C4b cost lines seen 1 / parsed 1
  C5 total wall-clock 31 min 55 s  (reviews are 69% of it)

  C6 material-marked recipe/bench runs 6, judgement-session attempts refused 0

  C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter `status: current`]: 8 - tools/bench/.stall_samples.txt, tools/bench/m3a1_save_after_20260922_002234.png, tools/bench/m3a1_save_before_20260922_002234.png, tools/bench/next_snapshot.md5, tools/bench/peer_task_c72_guisave.md, tools/gui_actions.log, tools/hooks/material_marker.log, tools/recipes/build_opconnectfromwire_v0.py


== document lint (tools/doc_lint.py; CLAUDE.md section 4)

  WARN  L1 frontmatter present and valid: 282/580 ok; 298 missing, 0 incomplete. Fix with `py tools/frontmatter.py`. first: ['archive/peer/2026-09-15-cycle8-plan-attack.md', 'archive/peer/2026-09-15-cycle8-plan-rule-audit.md', 'archive/peer/2026-09-15-frameloop-seam-77-crossings.md', 'archive/peer/2026-09-15-outcome-review-20260915.md', 'archive/peer/2026-09-15-peerps1-bomless-cp949-parse.md']
  PASS  L2 every cited project path exists: 1517 citations checked, none dangling
  WARN  L2c plan documents cite files that do not exist yet: 16 forward reference(s) in plan documents (expected while the cycle is open): ['docs/cycle14-plan.md:95 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:106 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:168 -> tools/recipes/build_opflatseqdiagrams_v0.py', 'docs/cycle14-plan.md:169 -> tools/bench/build_opflatseqdiagrams_v0.log', 'docs/cycle14-plan.md:169 -> tools/bench/opflatseqdiagrams_labels.json', 'docs/cycle14-plan.md:170 -> tools/bench/diag_a3_complete.py']
  PASS  L2b cited line numbers are in range: no citation points past a file's end
  PASS  L3 STATUS.md stays one screen: 62 lines (limit 110)
  PASS  L4 at most one current plan per family: ['docs/cycle27-plan.md'] current
  PASS  L8 the current plan has a `## Pre-decided` section: docs/cycle27-plan.md ok
  PASS  L5 superseded documents are not still current: no `supersedes:` target is still marked current
  PASS  L6 archived reviews are disposed: skipped - audit_cycle A4 owns this condition
  WARN  L7 decision/measurement sentences carry a mark: 360 unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be inferred rather than extracted. first: ['docs/NAMES.md:391', 'docs/NAMES.md:530', 'docs/NAMES.md:652', 'docs/NAMES.md:925', 'docs/NAMES.md:939']

AUDIT VIOLATIONS: A4 every archived review says what was done with it


=== BUILD LOGS INSIDE THE WINDOW (2; read them directly, they are the primary record) ===
tools/bench/build_d1_m3a1.log  (2026-09-22 01:01:46)
tools/bench/diag_c68_echo_accept.log  (2026-09-22 00:20:38)

=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW (7) - NOT builds, and not part of
the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the
output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.
tools/bench/cycle_57.log  (2026-09-22 00:16:53)
tools/bench/cycle_58.log  (2026-09-22 00:16:56)
tools/bench/cycle_runner.log  (2026-09-22 00:16:53)
tools/bench/cycle_runner_main_20260921d.log  (2026-09-22 00:16:53)
tools/bench/peer_c72_guisave.log  (2026-09-22 00:45:17)
tools/bench/peer_c72_guisave2.log  (2026-09-22 00:54:46)
tools/bench/retro.log  (2026-09-22 01:04:53)

The rules are in CLAUDE.md at the project root; this cycle's own plan is docs/cycle27-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of this cycle is in archive/peer/.

## Answer

All evidence is read. Here is the outcome retrospective of cycle 63 (the escalated fable/medium firefighter, 00:16:21–01:04:53).

# Verdict summary

This cycle delivered: the M3a-1 artefact is on disk after run 5 (`build_d1_m3a1.log:3434`, 22 pass / 0 fail, `BGRUN END rc=0 after 254s` at `:3436`), the repaired identity reader passed its discriminating acceptance first (`diag_c68_echo_accept.log` — the file on disk is `tools/bench/diag_c68_quote_echo.log`, 8/0, rc=0 after 78s), and a weeks-old silent defect was found and fixed: `gscript._lv_gui` joined args unquoted into `powershell -Command`, so no `-Evidence`-carrying GUI action had ever dispatched. Total recorded spend $3.6507, 49 minutes. It also honoured cycle 62's prescription to the letter — the 75-second measurement ran as the first batch, before any build.

It still carries one structural fault, and it is the same slug the cycle itself raised to threshold at 00:22.

**The fault.** Run 4 failed its save gate at 00:26:38 (`build_d1_m3a1.log:1999,2714-2716` — `gui_save … file mtime did not move after Ctrl+S on every candidate window`, rc=1 after 244s). The previous cycle's review had already specified the exact falsifier for precisely this failure: a `keys … Key=^s` row in `tools/gui_actions.log` inside the save window — a grep costing seconds (`archive/peer/2026-09-22-c72-guisave-foreground-r2.md:19`: *"The test was specified and not run; the new claim was built on top of the same unchecked assumption"*). The session did not run it. Instead it built a foreground/home-window theory from two screenshots, applied a clickprobe repair to `gui_save` on that theory (`tools/bench/peer_task_c72_guisave.md:19-22`, "FIX ALREADY APPLIED"), wrote "quoting" into the task's ALREADY RULED OUT block on the strength of a test that exercised the wrong argument (`diag_c68_quote_echo.log:10` tested `-Title "LabVIEW"`, a form that carries no spaced payload, and printed "quoting exonerated"), and dispatched an opus/max review — which timed out once at 780s (`peer_c72_guisave.log:2-3`, rc=2, blank archive) and on retry ($3.6507, `peer_c72_guisave2.log:3`) opened with the log-silence fact the grep would have given for free: `gui_actions.log`'s last row was 2026-09-18 18:12:14 — nothing was ever sent (`…-c72-guisave-foreground-r2.md:15-17`). Counterfactual on the clock: run 4 ended 00:26:38; the grep at ~00:27 shows silence, which kills the foreground theory instantly and points upstream of LabVIEW; reading `_lv_gui`'s call construction (the reviewer needed one table for it) yields the quoting fix by ~00:33; run 5 (254s) ends rc=0 by ~00:40 instead of 01:01:46. The mandatory failed-prediction review still gets dispatched, but attacking the measured claim, and the cycle closes roughly 22–27 minutes earlier. The dollar component of the pure waste — the timed-out first dispatch, a full 780s opus/max run — carries no `COST:` line anywhere, so it stays an honest unknown; the $3.6507 that is recorded bought the correct diagnosis and is not chargeable as loss.

I rank nothing else at this magnitude. The 13-minute timeout is a component of the same fault (the review only existed because the grep didn't), not a second one.

# FINDINGS

**1. Repeated failure.** Two recurrences. (a) The save-failure class ran a second consecutive time: run 3's `gui_save` raise (reviewed in `archive/peer/2026-09-22-c71-run3.md`) and run 4's (`build_d1_m3a1.log:2714`). The approach should have changed at the moment run 4's raise appeared — before writing the clickprobe repair — to the machine-record check the run-3 reviewer had already specified. (b) Subtler and worse: "quoting is ruled out" was concluded twice on the wrong operand — cycle 62's `diag_c68_quote2.log` and this cycle's `[Q]` test (`diag_c68_quote_echo.log:7-10`) both tested the single-word `-Title` form, never the spaced `-Evidence` payload that was the actual failure; the false exoneration was then handed to the reviewer as settled fact (`peer_task_c72_guisave.md:24-25`), and only the reviewer's refusal to accept it (`…r2.md:21-39`) recovered the truth.

**2. Missing tool.** The delivery-proof assertion the reviewer named at `…r2.md:78` — `_lv_gui` raising on non-zero exit, and `gui_save` believing a keystroke only on a fresh `gui_actions.log` row — is the reader whose absence let a parse error stand for weeks and cost cycles of "silently did nothing" GUI mysteries (STATUS.md:53 says any such past run is explained by it). The quoting fix landed; whether the row-assertion gate landed is not visible in any log I can open, and it is the piece that prevents the class, not the instance. The `Modifications:*Bitset` dirty-reader (`…r2.md:79`) was deferred with an explicit trigger (STATUS.md:53) — a defensible deferral, not a gap.

**3. Unmeasured steps.** The headline fault, plus its enabler: the `[Q]` quoting test generalized from `-Title` to all quoting (`diag_c68_quote_echo.log:10`), a measurement of the wrong thing dressed as exoneration. Note the irony of the clock: `docs/violation-decisions.md:902-904` records this very slug reaching threshold (13 occurrences, DECISION: no-device under the user's 2026-09-18 08:53 suspension) at **00:22** — the same minute run 4 launched carrying the unchecked assumption.

**4. Rule compliance.** The audit's A4 FAIL is real but thin: the blank review is the timed-out first c72 dispatch (`archive/peer/2026-09-22-c72-guisave-foreground.md:7-10` — empty cost, "(Claude fills in)"), which per CLAUDE.md "told you nothing" and was correctly superseded by the r2 file, itself disposed (STATUS.md:53). It needs a one-line "superseded by r2" annotation, not a substantive disposal. The mandatory-review rule was followed (an attack prompt, `peer_task_c72_guisave.md:29-35`), and the timeout was correctly re-dispatched rather than accepted. But the devil's-advocate rule was satisfied only formally: CLAUDE.md's own health check — "if the peer is the one raising the objections, the internal pass is not running" — describes this cycle exactly; the internal pass never asked "was a keystroke sent at all?". What the audit does NOT cover: a timed-out peer leaves no `COST:` line, so C4's $3.6507 understates true review spend by one full opus/max run (the standing C4 rider at STATUS.md:44 recurring in a new form); A6 prints "this cycle used no GUI if the retrospective agrees" — the retrospective does not agree: `gui_actions.log` grew 1800→1804 rows this window (audit A6 line vs cycle 62's), the four rows being run 5's now-actually-dispatched save actions, and they were properly recorded; and no gate can see that a task file's ALREADY RULED OUT block encodes a false exoneration — the reviewer is the only device that caught it.

**5. Ordering.** Better than any recent cycle at the top: the 78-second reader acceptance ran first (00:19:20), exactly as cycle 62's retrospective prescribed, and run 4 ran only after it. The single inversion is the fault above — the free grep belonged between run 4's failure and everything that followed it.

**6. What was not reported.** STATUS is unusually honest this cycle — it credits the reviewer with refuting the session's own diagnosis (STATUS.md:53) and quotes the r2 finding fully. Understated: the 785-second timed-out dispatch appears nowhere in STATUS (only `peer_c72_guisave.log:3` and the blank archive show it), and its unrecorded cost makes the cycle's $3.65 headline look cheaper than the truth. Trivial: STATUS.md:57-60 duplicates its two closing user-facing items verbatim.

**7. Judgement inside a material session.** C6: 6 material-marked runs, 0 refused judgement-session attempts. The peer review prescribed next builds (`…r2.md:76-80`) and the judgement session adopted them selectively — quoting fix and observed-record raise taken, dirty-reader deferred with a trigger, all recorded in STATUS.md:53 — which is the correct division. Nothing in the window shows a material cell deciding what belonged to judgement.

# DEVICE EFFECT

Checked all eleven against the window; **none failed inside it**, and I am not manufacturing one. The rc-masking fix held — the timeout reported rc=2 (`peer_c72_guisave.log:3`) and run 4's FAIL forced rc=1 (`build_d1_m3a1.log:2716`); the cost regex parsed 1/1 (audit C4b); the confirm-bait refuser had an attack prompt and nothing to refuse; the premature-build guard and stop-record had a hash-released recipe re-run, legitimately; C7 printed its 8-file out-of-plan list (all firefighter repairs and evidence — justified); the A4-blank refusal device guards only `priorart`/`retrospective` dispatch, and the newest retrospective was annotated when this one launched. Two scope limits to record, neither a firing failure: the A4-blank device cannot see a blank *hypothesis* archive (the timed-out c72 file sat blank all cycle inside its blind spot), and the C3/C4 cost device counts only cost lines the peer emits — a peer that times out emits none, so an entire opus/max run vanished from C4. Both are holes in coverage, not devices that fired wrong or were bypassed; the standing no-new-device order (2026-09-18 08:53) means they go here as findings.

---

VIOLATION: inference-over-measurement | loss_min=25 | loss_usd=? | evidence=archive/peer/2026-09-22-c72-guisave-foreground-r2.md:19

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-22 01:2x by the same cycle-63 firefighter session, before exit:

- **The named fault (inference-over-measurement: the foreground diagnosis was written, and its repair
  coded, before the free `gui_actions.log` grep):** ACCEPTED as stated. The slug's threshold answer is
  already on file (`docs/violation-decisions.md`, `## inference-over-measurement — 2026-09-22 00:22`,
  no-device under the user's suspension); this occurrence post-dates that block and re-opens the question
  for the next retrospective per the file's own rule. The lesson recorded: a "ruled out" line in an ATTACK
  brief must name the operand it tested — both quote tests measured `-Title`, never the spaced `-Evidence`.
- **F1(b)/F3 (false exoneration handed to the reviewer as settled fact):** ACCEPTED — same lesson; the
  reviewer's refusal to accept the brief's premise is what recovered the truth, and that is the review
  structure working, not luck.
- **F2 (the delivery-proof assertion — `_lv_gui` raising on non-zero exit, `gui_save` believing a
  keystroke only on a fresh `gui_actions.log` row):** NOT BUILT this cycle; carried OPEN in STATUS NEXT
  with the same trigger as the dirty-reader — if any GUI action "silently does nothing" again, that
  assertion is the next build before any retry.
- **F4 (blank timed-out first c72 archive):** FIXED — `2026-09-22-c72-guisave-foreground.md` now carries
  the one-line "superseded by r2" annotation. The C4 undercount (a timed-out opus/max run leaves no COST
  line) is noted in STATUS NEXT so the spend headline is not read as complete.
- **F5 (ordering):** accepted; no action — the prescription it praises (measurement first) is already the
  standing rule.
- **F6 (timeout dispatch invisible in STATUS):** FIXED — STATUS NEXT now names the 785 s TIMEOUT dispatch
  and its uncounted cost.
- **F7:** no action needed — the division it describes as correct is kept.
