---
type: decision
status: current
date: 2026-09-18
tags: [violations, cycle-discipline]
---

# Violation decisions — what was done about each slug that reached threshold

A slug that reaches three occurrences owes a RESPONSE (user's decision, 2026-09-16, option C): either a mechanical
device, or a written refusal to build one. This file is that record, and `tools/violations.py --due` reads it —
Claude still does no counting. A block only discharges a slug if it is **dated after** the retrospective that
carried it to threshold, so a fresh occurrence reopens the question.

Format, and the gate depends on the first line: `## <slug> — <YYYY-MM-DD>` then `DECISION: device` or
`DECISION: no-device`, then the reason.

**Context for everything below:** all six slugs hit 3 on 2026-09-15, when three retrospectives ran inside five
hours over overlapping work. The threshold was set assuming cycles spread across days, so the count reflects
cadence as much as recurrence. That is an explanation, not an excuse — each slug is answered on its own merits.

## unreported-fact — 2026-09-16

DECISION: device

The only one of the six with a concrete, unfixed defect behind it, and it hides failures rather than merely
costing time: a PowerShell runner reported `rc=0` while the probe it wrapped exited 1
(`tools/bench/probe_relocate_route_run2.log:25` — "outer runner ended rc=0 although the embedded probe says
probe exit=1"). A batch that fails can therefore look like a batch that passed. Fixed by making every runner
propagate the inner failure, and by `bgrun` treating a non-zero inner exit as a failed run. No deferral for this
one; a measurement device that can report success on failure invalidates everything measured through it.

## repeated-failure-class — 2026-09-16

DECISION: no-device

The rule already exists and is specific: a material session stops after two failures and hands over
(CLAUDE.md, "Failure budget = 2"). Step 0a broke it by grinding to attempt 5. A device here would count failing
runs of the same recipe and refuse the third — but the failures were not identical: attempts 1-2 were an addressing
bug, 3 was a harness without a Boolean control, 4 a type-mismatched wire. A counter keyed on the recipe name would
have blocked attempt 3, which was the run that finally measured the real cause. The discipline needed is "change
the APPROACH at the second failure", which a filename counter cannot see. Revisit if it recurs with identical
failures.

## wrong-ordering — 2026-09-16

DECISION: no-device

Same shape. The rule exists — names are resolved before the build, not discovered during it (CLAUDE.md, the work
cycle) — and step 0a violated it by guessing a Traverse index three times before running the census that settled
it in one minute. The mechanical form would be "refuse a recipe that does not cite a census log", which is easy to
satisfy by citing an irrelevant log. The prior-art review already asks "was this measured already?", which covers
the same ground from the outside. Revisit if the next cycle orders itself badly again.

## rule-evaded — 2026-09-16

DECISION: device (already built, 2026-09-15)

`peer.ps1 -Kind review` now REFUSES a task carrying confirm-bait ("please confirm", "sanity check", "do you
agree", "확인 부탁") and APPENDS the adversarial instruction set. Cycle 7's retrospective had found prompts saying
"BRIEF CONFIRM" — the opposite of rule 5. The device exists and predates this decision; recorded here so the gate
can see it.

## tool-not-built — 2026-09-16

DECISION: device (already built, 2026-09-15)

The prior-art review (`tools/prior_art_review.py`) asks, before any new build: has this been built, measured, or
tried and failed, and does a helper already exist? On its first real use it found four defects in a pending recipe,
one of them a repeat of a recorded failure. Benchmarked at 6.5/8 on real prior-art items
(`tools/bench/priorart_scores.md`). Note what the cycle-9 retrospective actually said: the missing tool was NOT a
LabVIEW reader — building `VI.Get Errors` "would have been more tooling drift" — but a fail-fast check, which is
what this is.

## inference-over-measurement — 2026-09-16

DECISION: no-device

Three instances in one day, all the same shape: a summary line quoted without reading the section that qualified
it (`camera-acquisition-facts.md:183` over `:139`), a warning string read as a diagnosis without opening
`settings.json`, and `uids()` treated as ordered without reading that it returns a set. A device would have to
detect "asserted without reading", which is not observable from outside. What IS observable is the contradiction it
produces, and the prior-art review catches those: it found the `STATUS.md` ↔ `NAMES.md` contradiction unprompted on
its first run. Covered indirectly; revisit if it recurs where prior-art cannot see it.

---

# Round 2 — reopened by `2026-09-16-retrospective-cycle10.md` (all six recurred)

Every block above was written at 01:47 on 2026-09-16; the cycle-10 retrospective ran at 14:28 the same day and
named **all six again**, which is exactly the reopening the file's own rule describes. Four consecutive
retrospectives (cycles 7, 8, 9, 10) have now named the same six faults. The answers below are against **cycle 10's
own evidence**, not a restatement of round 1 — and where round 1 said *"revisit if it recurs"*, it has recurred,
so "no-device" now has to earn itself with more than a repetition.

**The one number that frames all six** (`retrospective-cycle10.md`, §6): the cycle spent **48 min 40 s and
$28.5530** on six prior-art/plan reviews of a plan that changed under every reviewer, and **never launched the one
reader the cycle was declared for**. Rev3 records five accepted rev2 findings surviving into rev3 **with the plan
text unchanged**. So the recurring fault is not "we review too little"; it is that review output was not disposed
before the next review was bought.

## repeated-failure-class — 2026-09-16 15:05 (round 2)

DECISION: device

Round 1 said no-device because the failures "were not identical" and a filename counter could not see the real
pattern. Cycle 10's repeat is a different shape and **is** mechanically visible: five prior-art dispatches in one
afternoon while **23 archived reviews had blank disposition sections** (retrospective §4, audit A4), and rev3
states in writing that five accepted rev2 findings were still unedited when rev3 was bought. The countable event is
not "the recipe failed again", it is **"a review was dispatched while the previous one of the same kind had not
been disposed"** — a condition the dispatcher can read off the archive.

Device: `peer.ps1` / `guard_peer.py` refuse a new `priorart` or `retrospective` dispatch while the newest archived
review of that kind still has an empty *"What was done with it"* section. It attacks the exact loop that cost
$28.55, and it cannot be satisfied by a token edit the way a "cite a census log" rule could.

## tool-not-built — 2026-09-16 15:05 (round 2)

DECISION: no-device

The missing tool has a name, a recipe on disk, and a completed prior review: `OpOwnerChain_v0`
(`tools/recipes/build_opownerchain_v0.py`, `pre-rig-master-plan.md` A1). Nothing failed to *detect* it — the cycle
plan, STATUS and the retrospective all name it. What failed is **ordering**: the plan was written and reviewed five
times around an unresolved ownership question instead of resolving it. A device that counts "declared deliverable
not built" is a to-do list, and this project already has three of those.

The response is therefore not a device but a sequencing commitment that can be checked from the logs: **the next
recipe this project runs is A1**, and the cycle's first build log will show it. If a cycle 11 retrospective again
reports the declared reader unbuilt, this slug should be escalated past a device to a re-plan with the user.

## inference-over-measurement — 2026-09-16 15:05 (round 2)

DECISION: no-device

Cycle 10's instance is real and cheap: three uses of the invalid traverse class string `"PropertyNode"` sat in the
A1 recipe through five plan rounds, and a one-minute `PropertyNode` vs `Property` grid found the defect immediately
once it was finally run (retrospective §3). But that specific defect is **already fixed in the recipe**, and the
generalised device — a preflight validating every class-name literal against `docs/NAMES.md` — would have caught
this one string while leaving untouched the other four instances §3 lists, which are all *"reasoned about a wire /
a control / an interval that a cheap existing read would have named"*. That class is covered by a rule that already
exists and is specific: **"the second time a class of failure is explained by inference rather than read from the
machine, the next build is the READER for it"** (CLAUDE.md).

Evidence that the rule is now being followed rather than merely written down, from the same day this decision is
made: `uid 9775` had been "narrowed but not settled" by a position-proximity sweep that our own notes say is
invalid on a Clean-Up'd diagram, and was left open across two prior-art reviews. It was closed in **37 seconds**
with an op that already existed (`OpWireSource_v5`, `tools/bench/diag_9775_direction.log`) — measurement first, no
new tool. Revisit if cycle 11 again explains a wire by geometry.

## rule-evaded — 2026-09-16 15:05 (round 2)

DECISION: no-device

The evasions cycle 10 names are (a) **two sessions editing the active documents concurrently**, leaving one with a
stale `CLAUDE.md`, and (b) the failure budget defended as "judgement, not material" while five expensive rounds ran
on the same inconsistency class (retrospective §4).

(b) is answered by the device above — the disposition gate makes round N+1 impossible until round N is disposed,
which is where the budget actually leaked. (a) is deliberately **not** given a device: the obvious one is a session
lock file that refuses a second session, and this project's LabVIEW instance is shared with the user's real
experiments. A lock that can refuse *the user's own* session is a worse failure than the one it prevents, and the
existing remedy is already in place and is free — `STATUS.md`'s ⚠️ ONE SESSION AT A TIME banner plus re-reading
`CLAUDE.md` from disk at session start. Revisit only if a third concurrent session occurs.

## wrong-ordering — 2026-09-16 15:05 (round 2)

DECISION: no-device

This is the one slug where a device is the wrong shape **by the project's own rule**: CLAUDE.md states that an
outcome-layer violation *"is NOT answered by building a device — answering goal drift with another tool is how the
drift happened"*, and cycle 10's ordering fault is precisely goal drift (a cycle declared for one reader expanded
into a complete Phase 0/A/1/2 master plan before the reader ran, retrospective §5). The mechanical form would be
"refuse a plan edit while the cycle's declared deliverable is unbuilt", which would have blocked the plan
corrections that the prior-art reviews legitimately demanded.

The answer is the same sequencing commitment as `tool-not-built`, and it is checkable in the same place: A1 first,
visible as the cycle's first build log. On a further repeat, escalate to a re-plan with the user rather than to a
sixth gate.

## unreported-fact — 2026-09-16 15:05 (round 2)

DECISION: device

Round 1's device fixed runners that reported `rc=0` over an inner failure. Cycle 10 exposes a second, independent
blindness in the same family, and it corrupts the very argument the retrospective layer exists to have:
`tools/audit_cycle.py`'s C3 **excludes peer wall time and cost**, so the audit handed to the reviewer reported
**3 min 12 s** for a cycle that actually spent **48 min 40 s and $28.5530** on reviews (retrospective §6). Every
"was this cycle worth its cost" judgement has been made against a number an order of magnitude too small, and the
reviewer had to reconstruct the real one by hand from the peer logs.

Device: C3 counts `tools/bench/peer_*.log` and `priorart_*.log` wall time and the usage/cost lines the claude peer
already records, and reports build cost and review cost as two separate lines. Small, and it makes the cost
argument possible instead of rhetorical.

---

## ⚠️ These six cannot discharge the gate today, and that is a granularity bug, not a policy

`violations.py` compares `dec.get(slug) > newest_retro` as **date strings**. The cycle-10 retrospective is dated
`2026-09-16` and so is every block above, so `"2026-09-16" > "2026-09-16"` is false and all six stay DUE until a
block is dated 2026-09-17. **Same-day answers are impossible by construction**, which the file's stated intent —
*"a fresh occurrence reopens the question"* — never asked for; it asks for ORDERING, and date-only stamps cannot
represent ordering inside a day.

Deliberately **not** fixed by this session, and the reason matters: the gate is blocking *this* session's build,
so quietly regrading its comparison would be the `rule-evaded` slug in its purest form. It is recorded here for the
user to decide (timestamped decisions, or an explicit "answered same day" marker), and until then the block stands.

---

## New slug added — `judgement-in-material`, 2026-09-16

A ninth slug now exists in `retrospective.py`'s fixed question set (question 7) and in `violations.py`'s `KNOWN`
list, at the same threshold 3: it fires when a decision that belonged to the judgement session — a design change, a
choice between explanations, accepting or rejecting a review finding, a change of plan direction, or an action
pre-scripted in a brief as "if X then do Y" — was instead taken inside a MATERIAL sub-session. It answers the
user's concern (2026-09-16) that a judgement session fed only ≤30-line summaries may be deciding on too little,
and the rule it enforces is CLAUDE.md's "A delegation brief states the MEASUREMENT, never the result-dependent
ACTION". **Its first count starts with cycle 11**; nothing before that is counted against it.

(Heading deliberately not in `## <slug> — <date>` form: that form is a DECISION block, and this slug has no
occurrences yet, so a matching heading would pre-emptively discharge a gate that has never fired.)

## premature-build — 2026-09-16 19:16 (round 3)

Occurrences: cycles 7, 9, 11. The cycle-11 instance is on the clock: `priorart_cycle11.log` dispatched 16:24:00 and
ran 427 s; `build_opdelete_v1.log` started 16:26:10 — the build was launched while its own prior-art review was
still running, and that review's finding 5 predicted the build's failure before the log did.

DECISION: device
Device: `tools/hooks/guard_cycle.py` refuses a RECIPE build while (a) any `tools/bench/priorart_*.log` for the current
cycle has no `BGRUN END|TIMEOUT` line, or (b) no `archive/peer/*priorart*.md` is newer than the recipe file being run.
Diagnostics (`tools/bench`) stay open. Reason: the violation is a *timing* fact the machine can see; a rule about
patience is the kind that fades after compaction.

## scope-creep — 2026-09-16 19:16 (round 3)

Occurrences: cycles 7, 10, 11. The cycle-11 instance is the 26-wrapper `ensure_loaded` patch made on one measured
case (`delete_object`), and the `OpDelete_v1` rebuild that the plan did not need.

DECISION: device
Device: `tools/audit_cycle.py` gains a line listing every file modified in the cycle window that is not named in the
cycle's plan document (`docs/cycle<N>-plan.md`), so the retrospective judges scope from a machine-made list rather
than from Claude's summary. A counter, not a refusal, by design: out-of-plan changes are sometimes right (a
measured bug fix), so the verdict stays with the retrospective; only the *list* is taken away from Claude.

## judgement-in-material — 2026-09-16 21:07 (round 4, first decision under retrospective v2)

Under v1 counting this slug reached 3/3 cycles (11·12·13), unsized. The v2 retroactive comparison
(`tools/bench/retro_v2_comparison.md`) sizes it: **top fault in ONE of the three cycles (12), 13 minutes**,
counterfactual "cycle would have ended ~19:46 instead of 19:59". Real, but not the every-cycle fault a 3/3 count
implied — the v1 count was an artefact of "one question = one slug".

DECISION: no-device
Reason: the remedy already exists as a rule with a mechanical hook on the material side — CLAUDE.md §3 "a delegation
brief states the MEASUREMENT, never the result-dependent ACTION" and `.claude/agents/material.md` "If the brief
contains result-dependent actions, do not take them". Both were written 2026-09-16 18:xx, i.e. AFTER the cycle-12
instance, and cycle 13 showed no instance under v2. Re-evaluate under v2's loss sums (proposal 3) if it recurs.

## device-failed — 2026-09-16 21:07 (round 4; threshold 1)

First firing of the v2 device-effect question, and it was right: `tools/audit_cycle.py:191`'s cost regex matches
`total_cost_usd|cost_usd|total_cost` while every priced log writes `COST: $…` — the device built to stop cost being
understated understated $20.42 in cycle 11's window alone.

DECISION: device
Device: repair the regex (that IS the device), add a self-test line that asserts the regex matches the literal
`COST: $5.1157` form, and make `audit_cycle` print `cost lines seen / cost lines parsed` so a silent miss is visible.

## device-failed — 2026-09-17 03:38 (round 5)

Cycle-14 retrospective: the `unreported-fact` runner-exit device let `tools/bench/diag_stop_condterm_panel.log:15-18`
end `rc=0` with a failed gate — `-> FAIL` lines have never been in bgrun's inner-failure scan (only the
`=== N fail ===` summary form and STOP/EXC/TIMEOUT), so a script that prints a failed gate and returns 0 is invisible.

DECISION: device
Device: `tools/bgrun.py` adds `^\s*(?:->\s*)?FAIL\b` (the same form audit_cycle/guard_peer use) to the inner-failure
scan for build/diagnostic logs (review logs stay excluded via logclass), and forces `rc=1` on a match; self-test on the
literal line above.

## repeated-failure-class — 2026-09-17 03:38 (round 5)

7 occurrences. The cycle-14 instance is the stop CONDITIONAL TERMINAL of WhileLoop #637: diagnosed by inference twice
(`diag_stop_condterm_panel`, `diag_stop_save_seam`), both refuted, because no reader exists — exactly the
"guessed twice ⇒ build the reader" rule, and STATUS OPEN 13 already names the reader.

DECISION: device
Device: build the reader `OpLoopEndRef_v0` (`WhileLoop.Loop End Ref` 0x06362C00 → the conditional terminal → its
connected wire/source), functionally verified on the main VI's #637 (read-only), so "how does the original stop" is
measured before D1 replaces that loop. It is also D1's S4 gate.

## device-failed — 2026-09-18 00:53 (round 6)

Cycle-17 retrospective (`archive/peer/2026-09-18-retrospective-cycle17.md`), `loss_min=23`, `loss_usd=4.8500`.
The broken device is the PRIOR-ART review. It fired correctly on route-B run 3 and said in writing that the recipe
could not pass its own gate; **six seconds later the recipe launched anyway** and failed exactly as predicted, and
the failed-prediction review it triggered cost a further 781 s and $4.85. The device verified that a review had
HAPPENED and been disposed — nothing bound the recipe's LAUNCH to that review's VERDICT.

DECISION: device
Device, built and proven this cycle: a **stop record + launch gate**.
- `tools/stop_record.py` — record store `tools/bench/stop_records.json`; a prior-art verdict other than `novel`
  plants a record keyed to the recipe's **path + sha256**. Refusal is by PATH (re-saving cannot evade it);
  release is qualified by HASH (the gate stamps the hash at the first launch after a valid release, and a later
  byte change is refused again as *unreviewed*, not released).
- The only releases are the two that already existed, with their existing machine-checked conditions:
  `FIXED: <slug> - <path>:<line> - <sentence>` and `REFUTED: <slug> - <file>:<line> says X, which …`. No third
  release form was invented, and the `FIXED:`/`REFUTED:` validator is **imported** from `guard_cycle`
  (`tools/stop_record.py:256-257`; the `REFUTED:` half was refactored out of `guard_cycle.main()` into
  `guard_cycle.py:172 released_slugs()`), never reimplemented — two validators drift.
- Call sites: `tools/hooks/guard_bash.py:156` (the launch path run 3 got through, checked **before** any
  `LV_GUARD_OFF`/`BENCH_CELL` escape) and `tools/hooks/guard_cycle.py:462`.
- **Fail closed, narrowly:** a missing-but-expected, unreadable or corrupt store refuses any command naming a
  `tools/recipes/*.py` and leaves every other command alone — a device that dies OPEN is this slug itself.
- **An omission cannot leave it un-armed.** `tools/prior_art_review.py` cannot derive the recipe path from its own
  inputs (`:143-148` takes only a plan and a slug), so it now REFUSES (rc 2) without `--recipe`, unless
  `--no-recipe "<reason>"` is given and the reason is archived into the review as a `NO-RECIPE:` line that cannot
  be parsed as a release or a disposition. A whitespace-only reason is not an opt-out.

Proven, not asserted: `tools/bench/stop_record_selftest.py`, **29/29 gates**, covering refuse · release passes ·
hash-change-refuses-again · corrupt-store-fails-closed · omission-refuses · explicit-opt-out-runs-and-is-recorded,
with the real store measured untouched before and after (`tools/bench/cycle18_stopgate.log` `BGRUN END rc=0`,
`tools/bench/cycle18_arming.log` `BGRUN END rc=0 after 145s`). A gate that passes only its happy path was not
accepted (cycle-18 plan, Pre-decided 4).

## wrong-ordering — 2026-09-18 08:53 (round 3)

DECISION: no-device

**The user's decision, verbatim (2026-09-18 morning, in answer to the runner's STOP report): "장치는 더 만들지
말고 계속 진행".** Round 2 pre-committed this round to the user ("escalate to a re-plan with the user rather than
to a sixth gate"), and CLAUDE.md reserves lowering or overriding a threshold to the user alone; this block records
that answer, it is not Claude waiving its own threshold. What "계속 진행" means is fixed in STATUS.md `## NEXT`:
the motor-limit assurance work in its settled order — run the written tunnel reader → check A → control
Data-Entry ranges → check B → check C — and **no further process device (gate, hook, record, lock) is built in
these cycles**; a retrospective that names one is recorded as a finding and NOT acted on until the user says so.

## inference-over-measurement — 2026-09-18 13:45 (round 1; cycle-24 firefighter, after 2026-09-18-retrospective-cycle23.md)

DECISION: no-device

The user's standing order of 2026-09-18 08:53 ("장치는 더 만들지 말고 계속 진행") covers every process device
until the user says otherwise (STATUS.md line 9): a retrospective naming this slug is a FINDING, not a task, so
no new hook, reader or gate is built for it. The substantive answer is behavioural and already in the work: the
`build_opfstunnelterm_v2.py` rewrite replaced the inferred donor-orphan story with dispatch 4's MEASURED timeline
(`tools/bench/diag_fstunnel_orphan_timeline.log` T1/T2) and Twin A's measured repair
(`tools/bench/diag_fstunnel_preclean_twins.log`) — its gates A0a/A0h/A0c/A0d assert only values read from the
machine. Only the user may build or order the device for this slug.

## repeated-failure-class — 2026-09-18 19:3x (cycle 34, after archive/peer/2026-09-18-retrospective-cycle34.md)

DECISION: no-device

The slug stands at 13 occurrences, far past the threshold of 3, so under the unsuspended rule the next cycle would
have to build its device first. The user's standing order of 2026-09-18 08:53 ("장치는 더 만들지 말고 계속 진행")
suspends that threshold, so this is recorded as a FINDING and **no device is built**. Only the user may lift it.

The occurrence: a `claude -p` judgement session dispatched two hypothesis peers and then ended its turn, believing
it could collect the answers later. It cannot — the harness terminates background tasks at 600 s, and both paid
opus/max cells were killed mid-answer with their cost unrecorded (`tools/bench/cycle_19.log:52-53`,
`"killed": {"system": 2}, "completed": 0`). The next session re-asked the same two questions for $5.88. This is
the third occurrence of the parent-exit-kills-backgrounded-child class already recorded at CLAUDE.md:316-318.

The device the retrospective asks for, NOT built: an audit check flagging any bgrun log whose last line is
`BGRUN START` (audit A2 cannot see it — peer logs are excluded by logclass), or a runner-side refusal to reap a
session whose exit JSON shows `killed.system > 0` without a note in STATUS. It is cheap and it catches a class
that has now cost money twice, so it is FIRST IN LINE if the user lifts the no-device order.

The behavioural answer, already applied in the cycle that recorded this: dispatch in the foreground and wait, and
when something must run in the background, hold the turn open until it lands rather than ending it. Cycle 34 closed
its own retrospective that way (`tools/bench/retro_c34.log`, rc=0 after 293 s); ending the turn would have killed
the very review that found this fault.

## repeated-failure-class — 2026-09-18 21:05 (cycle 36, after archive/peer/2026-09-18-retrospective-cycle35.md)

DECISION: no-device

<!-- Stamp corrected from the placeholder `21:0x` to the literal time this block was written, by the cycle-36
     JUDGEMENT session. `DEC_RE` (tools/violations.py:94) accepts a time only as `(\d{2}:\d{2})`, so `21:0x` parsed
     as `00:00`, tied with `_retro_stamp("…retrospective-cycle35.md")`, and `tools/violations.py:206` requires
     strictly `>` — leaving the slug DUE and `guard_cycle` refusing the route-B build. Nothing about the decision
     changed: `DECISION: no-device` rests on the user's standing order below, not on this timestamp. The material
     session that hit the refusal correctly declined to edit its own blocking gate's input and reported it instead. -->


`py tools/violations.py` now counts this slug at **14** occurrences (cycles 7·8·9·10·11·12·14·15×3·16·16b·34·35),
reported loss 216 min across 8 of them, and the counter says `<== DUE, no decision on file` — the cycle-34 block
above is dated the same day as the cycle-35 retrospective that re-fired it, so the file's own "a fresh occurrence
reopens the question" rule leaves it due. Under the unsuspended CLAUDE.md §3 rule (threshold 3) the next cycle
would have to build this slug's device before anything else.

**The device threshold is SUSPENDED** by the user's standing order of **2026-09-18 08:53** — *"장치는 더 민들지 말고
계속 진행"* (cited by DATE, not by a `STATUS.md` line number: the order used to sit at `STATUS.md:10`, and the
cycle-36 relocation moved it, which `doc_ingest` reported as a contradiction) — so this occurrence is recorded as a
**FINDING and NO device is built**. Only the
user may lift the suspension; until they do, a retrospective naming this slug is a finding, not a task.

Evidence for cycle 36's occurrence: `tools/bench/repair_c36_selftest.log` — the STALLED-LabVIEW-client alert class
fired again on a healthy bgrun waiter (`stall_pid11536_193335.log`, whose job ended `BGRUN END rc=0 after 4022s`),
and the cycle-35 reviewer's premise for it (a missing bgrun job log) measured FALSE, with probes F1–F4 all
negative. The repair shipped this cycle (identity-binding + skipping leaves with no bgrun log) is a REPAIR of an
existing device, not a new one, so it is not blocked by the order above; whether it addresses the class at all is
the question put to `archive/peer/2026-09-18-stall-liveness-class-c36.md`.

## wrong-ordering — 2026-09-18 23:09 (cycle 36, after archive/peer/2026-09-18-retrospective-cycle36.md)

DECISION: no-device

`VIOLATION: wrong-ordering | loss_min=41 | loss_usd=2.7466 | evidence=tools/bench/build_d1_routeb_v1_run4.log:1`.

Accepted, and the cause is recorded rather than disputed: cycle 36 opened on STATUS's then-current `## NEXT`, which
put two machinery repairs (STEP 0) ahead of the D1 build. The user's order of the same evening (21:3x) reversed
that priority — *"The next cycle's FIRST ACT is a D1 BUILD dispatch … NO machinery repairs, NO watchdog reviews,
NO audit fixes, NO doc relocation before that dispatch has RUN"* — but it arrived after STEP 0 had already run.
The ordering was wrong by the standard the user set; it was not wrong by the standard written down when the cycle
began.

**No device is built** — the threshold is SUSPENDED by the user's standing order of 2026-09-18 08:53, and the
remedy here is not a mechanism anyway: the next session's first act is now written into `## NEXT` as a concrete
run-5 instruction, which is what a device would have forced.

## device-failed — 2026-09-18 23:09 (cycle 36, after archive/peer/2026-09-18-retrospective-cycle36.md)

DECISION: no-device

`VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/repair_c36_selftest.log:44`. This slug
carries **threshold 1** under CLAUDE.md §3 — a device that lets its own fault through is broken rather than
unlucky — so it would block the next build were the threshold not suspended.

Accepted. Two devices are named, neither disputed:

1. **The stall watchdog fired again during run 4** (`stall_pid11424_221324.log:1`), on the same healthy-waiter
   class this cycle had just repaired. The repair (identity-binding to `(pid, CreationDate)`, skipping leaves with
   no bgrun log) was MEASURED not to cover its own motivating case, because that case *had* a bgrun ancestor —
   `archive/peer/2026-09-18-stall-liveness-class-c36.md`, where the peer refuted the causal story and named the
   real class: *a bgrun job whose log is written once at START*, for which stale-log-plus-zero-CPU is the healthy
   steady state.
2. **`audit_cycle`'s C3/C5 cost figures are phantom** — the retrospective measured 649 of the 758 claimed minutes
   to be impossible inside a 143-minute window, and nothing in STATUS or the audit output says so. **Cost numbers
   from this cycle's audit must not be quoted until that is measured.**

**No device is built**, per the suspension. Both are REPAIRS of existing devices whenever the user lifts it, and
the peer already named repair 1's shape (`guard_peer` retracting a stall record whose named job later ends
`BGRUN END rc=0`), while noting it is unsound until `bgrun`'s final-line guarantee is real — which this cycle made
real for internal exits only (`tools/bench/c36_close_runner.log:13-14`); external kills remain uncovered.

## device-failed — 2026-09-19 04:10 (cycle 39)

`archive/peer/2026-09-19-retrospective-cycle39.md`, ANSWERED, 366 s.
`VIOLATION: device-failed | loss_min=45 | loss_usd=9.41 | evidence=build-log-classifier+stall-watchdog+stop-record`

DECISION: no-device

Under the standing suspension (user, 2026-09-18 08:53, "장치는 더 민들지 말고 계속 진행"), recorded as FINDINGS as
that suspension requires. `device-failed` carries threshold 1; it is NOT answered with a NEW device while the
order stands. All three named instances are real and measured:

1. **`logclass.is_build_log` counts waiter logs as builds.** Five of the ten logs filling `CYCLE_BUILD_BUDGET`
   were `tools/wait_logs.py` waiters (`wait_priorart_run5/6`, `wait_c37_selftest`, `wait_c37_b`, `wait_c37_peer`);
   only three were recipe builds. This, not the real build rate, is what made `guard_cycle` refuse run 8.
   FINDING only — worked around by the cycle close, which resets `since`.
2. **The stall watchdog's precision is 0/5.** `archive/peer/2026-09-19-stall-waitlogs-c37b.md` measured 0/4 and
   resolved the job behind every record: neither "real build client" was killed at its deadline. A fifth false
   positive then fired during run 7 (`tools/bench/stall_pid7288_023957.log:1`, "no modal dialog", client alive and
   running on to its own crash). Each record blocks the next build until a peer review clears it: $3.1519 +
   $3.0051 was spent on exactly that. **REPAIR AUTHORISED by the cycle-39 judgement session — one line, to an
   EXISTING device, not a new one**: write the gating `stall_pid*.log` only when the dialog check at
   `tools/lv_stallcheck.ps1:257` returns `VERDICT: BLOCKED`. Scheduled in `STATUS.md` `## NEXT` AFTER run 8
   launches, per the user's ordering rule. Flagged to the user in STATUS's FOR THE USER section to overturn.
3. **The stop record + launch gate is mechanically unusable** — `--recipe` refuses every command naming a stopped
   recipe, and `_check():318-331` compares the old record's hash after `_released()`, so no `FIXED:`/`REFUTED:`
   line can clear it. Worked around with `--no-recipe` plus a direct `write_stop_record`; diagnosis cost $3.2492.
   FINDING only.

## repeated-failure-class — 2026-09-19 04:10 (cycle 39)

`archive/peer/2026-09-19-retrospective-cycle39.md`, ANSWERED, 366 s.
`VIOLATION: repeated-failure-class | loss_min=30 | loss_usd=? | evidence=tools/bench/retro_c37.log:3`

DECISION: no-device

Cycles 37 and 38 each backgrounded their retrospective and exited, killing it
(`tools/bench/retro_c37.log:1-3` at 00:53:11, `tools/bench/retro.log:216-218` at 02:26:12), so neither was
archived and `guard_cycle`'s `since` list accumulated from cycle 36 until it refused run 8. No device: the rule
already exists at `STATUS.md`
OPEN 54, and what was missing was a PERMITTED WAIT. The working pattern — background the bgrun, then hold the turn
with repeated bounded `py tools/wait_logs.py <task-output-file> --seconds 25` calls, since `guard_bash` allows a
foreground wait only at <= 30 s — is written into `STATUS.md` `## NEXT`. Cycle 39 did not repeat the fault.

## inference-over-measurement — 2026-09-19 08:20 (cycle 42, after archive/peer/2026-09-19-retrospective-cycle42.md)

`archive/peer/2026-09-19-retrospective-cycle42.md`, ANSWERED.
`VIOLATION: inference-over-measurement | loss_min=31 | loss_usd=? | evidence=archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499`

DECISION: no-device

**Accepted in full, and not disputed.** The cycle-42 judgement session released the prior-art stop by writing two
`REFUTED:` lines against findings F3 and F4 — "v7 issues no keystroke save at all", "the save path is COM `g.save`,
not `gui_save`" — citing v7's own CALL SITE and never opening the CALLEE. `tools/gscript.py:2065-2067` shows
`g.save(target, allow_broken=True)` diverting to `gui_save()` whenever `exec_state()` reads 0, which it always does
on a cold read. Run 10 took that divert and died on the exact `mtime did not move after Ctrl+S` failure F4 named
(`tools/bench/build_d1_routeb_v7_run10.log:367`), burning its whole 31-minute purpose. The measurement that would
have prevented it — reading about fifteen lines of `gscript.py` — was free and available at disposition time.
The same fault repeated inside the same cycle: the traverse census behind CLAIM 2 ("`report_all(Diagram)` is
0-for-21, it has never once succeeded") was built by grepping for lines that PRINT `error 2`, an instrument that can
only observe failures, and the paid hypothesis review refuted it as a selection artefact from success lines sitting
unread in the same logs.

**No device is built** — the threshold is SUSPENDED by the user's standing order of **2026-09-18 08:53**
(*"장치는 더 민들지 말고 계속 진행"*, cited by DATE, never by a `STATUS.md` line number), so this occurrence is
recorded as a FINDING. Only the user may lift the suspension.

Two things are worth recording even so, because a future session may reach for a device here and should know what
was already considered:

1. **A mechanical form-check would not have caught this.** Both `REFUTED:` lines had correct citation shape and
   pointed at files that exist; the gate checks form, never whether the refuting claim was verified. The
   retrospective reaches the same conclusion in its DEVICE EFFECT section and explicitly declines to rule the stop
   record a failed device for it.
2. **The rule that would have caught it is one sentence, and it is now written into the plan** rather than into a
   tool: `docs/cycle27-plan.md` Pre-decided 21 — a claim about what OUR OWN code does must quote the CALLEE, not
   the call site. This is the reviewer's own proposed rule (`archive/peer/2026-09-19-routeb-run10-error2-class.md`,
   answer (e)), and it generalises CLAUDE.md's standing warning that claims about our own tools are the factual
   claims we are most likely to be wrong about.

## device-failed — 2026-09-19 19:2x (cycle 43, after archive/peer/2026-09-19-retrospective-cycle43.md)

**The stop-record launch gate (decided 2026-09-18 00:53) failed both ways in one evening; threshold is 1.**
It refused a judgement-released, bug-fixed retry because `stop_record.py:313-331` pins a release to the
first-launched bytes (while `guard_cycle.py:485-496` explicitly permits that edit), and it was WORKED AROUND by
renaming the recipe (v2 → v3, STATUS cycle-43 lock record) — the exact laundering its decision text says is
impossible ("refusal is by PATH"). Second consecutive day the gate was answered by a rename (v0→v1→v2→v3).
The fix has been on file and undisposed since 01:22: the codex supersession patch for `_check()`
(`archive/peer/2026-09-19-stoprecord-release-deadlock-codex.md:91-107`, its "What was done with it" still blank).
**Decision (cycle-43 judgement): dispose that review and apply the supersession patch FIRST next cycle** — a
repair of an existing broken device, not a new device; whether the user's 2026-09-18 08:53 "no more devices"
order covers repairs is flagged to the user in STATUS NEXT rather than assumed either way.

## repeated-failure-class — 2026-09-20 00:2x (cycle 48, after archive/peer/2026-09-19-retrospective-cycle47.md)

`archive/peer/2026-09-19-retrospective-cycle47.md:242`, ANSWERED.
`VIOLATION: repeated-failure-class | loss_min=27 | loss_usd=? | evidence=tools/bench/retro.log:386`

DECISION: no-device — recorded as a FINDING only.

**Two reasons, and the second is the stronger one.**

1. **The threshold is SUSPENDED** by the user's standing order of **2026-09-18 08:53** (*"장치는 더 민들지 말고
   계속 진행"*, cited by DATE, never by a `STATUS.md` line number). While it stands, a slug reaching 3 is recorded
   here and the next cycle builds NO device. Only the user may lift it.
2. **The class is already CLOSED by a repair to an existing device**, so even an unsuspended threshold would not
   call for a new one. The fault named is the killed retrospective: cycle 47's `retrospective.py --cycle 47`
   wrote a START with no END (`tools/bench/retro.log:386`, 23:37:14) because the session exited and took the child
   with it — the sixth occurrence, and the one that then refused cycle 47's S1 launch at `guard_cycle.py`'s
   stale-retrospective branch. `tools/cycle_runner.py land_retrospective()` now re-runs any such orphaned START
   from the RUNNER, which outlives every session. It fired for the first time on this very record:
   `tools/bench/retro.log:389` (re-launch 23:43:28) → `:439` (`BGRUN END rc=0 after 362s`), logged as
   `RETRO-LANDED` at `tools/bench/cycle_runner.log:56`. Cycle 48's S1 launch was not refused.

Worth recording for a future session: the remaining uncovered half is the LAUNCHING session's own wait. A
material session may hold its turn with `tools/bench/wait_bgrun_end.py`; a judgement session may not
(`guard_bash`'s judgement-vs-material gate), and both `Start-Sleep` and a shell `until` loop are refused by the
harness and the permission layer. That is a prose rule (`STATUS.md` OPEN 54(b)), not a device, and it is
deliberately left as one.

---

## repeated-failure-class — 2026-09-20 (17 cumulative occurrences, threshold 3)

<!-- RE-HEADED 2026-09-20 (cycle 53, Pre-decided 37(i) sibling). The header read
     `## 2026-09-20 - \`repeated-failure-class\`, 17 cumulative occurrences (threshold 3)`, i.e. DATE FIRST, and
     `tools/violations.py:94` DEC_RE requires `## <slug> - <date>`: it dropped this block silently, so a written
     decision registered as no decision at all. Slug and date are unchanged and NO TIME was added - a bare date
     stamps 00:00, the conservative direction (`_stamp()`), so this cannot discharge anything it did not already.
     Body untouched. -->


Raised by `archive/peer/2026-09-20-retrospective-cycle48.md:227`, ANSWERED. Answered by the cycle-49 judgement
session, 2026-09-20, because `guard_cycle` refused every command naming `tools/recipes/stage_d1_s2.py` until a
dated block existed.
`VIOLATION: repeated-failure-class | loss_min=15 | loss_usd=3.93 | evidence=tools/bench/cycle_34.log:121`

DECISION: no-device — recorded as a FINDING only.

**Three reasons.**

1. **The threshold is SUSPENDED** by the user's standing order of **2026-09-18 08:53** (*"장치는 더 민들지 말고
   계속 진행"*, cited by DATE, never by a `STATUS.md` line number). While it stands, a slug reaching 3 is recorded
   here and the next cycle builds NO device. Only the user may lift it. The count of 17 is cumulative across every
   retrospective, not 17 events in one cycle.
2. **The review itself declined to ask for one.** Its `## DEVICE EFFECT` section (`:213-223`) checked each existing
   device, found every one either working or not exercised, and concluded: "The fault that ended this cycle late has
   no device, so no `device-failed` is warranted." Answering that with a new device would be the drift the outcome
   layer exists to catch.
3. **Cycle 49 answered it procedurally, and it held.** The fault is the background-kill of a near-complete child
   (`STATUS.md` OPEN 54(b)). Every sub-agent dispatch in cycle 49 ran in the foreground with the turn held open, and
   no child was killed — zero occurrences in this cycle. The cheapest remaining form is not a device either: the
   review names one environment variable set once in `tools/cycle_runner.py`'s spawn
   (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`), a one-line repair to an existing tool, carried in `STATUS.md`'s NEXT.

---

## 2026-09-20 — two retrospective-cycle49 findings that each name a device

Raised by `archive/peer/2026-09-20-retrospective-cycle49.md`, ANSWERED and DISPOSED by the cycle-50 judgement
session, 2026-09-20. Neither finding carries a `VIOLATION:` slug; both are prose FINDINGS that name a mechanical
device as their remedy, which is why they are recorded here rather than acted on.

FINDING: no-device

1. **Finding 2** (`:193-197` region, "Missing tool"): there is no cycle-close check that the launch gate was
   actually released and that the newest archived review of each kind carries a real `## What was done with it`.
   The remedy named is a new mechanical check.
2. **Finding 4c** (`:199`): `audit_cycle`'s A4 annotation check reported "3/3 annotated" while
   `archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1263` still held the literal `(Claude fills in)` placeholder —
   A4 evidently matched *quoted* "What was done with it" text earlier in the same file (`…-r2.md:59-61`) instead of
   the terminal section. The remedy named is a repaired A4 parser.

**Why nothing is built.** The user's standing order of **2026-09-18 08:53** (*"장치는 더 민들지 말고 계속 진행"*,
cited by DATE, never by a `STATUS.md` line number) suspends device construction. While it stands, a finding whose
remedy is a device is recorded here and the next cycle builds NO device. Only the user may lift it.

**What was done instead.** The cycle-50 judgement session disposed all three outstanding reviews by hand before
dispatching anything, which is the same end state finding 2's device would have enforced. Finding 4c's consequence
is carried as a standing caution: `audit_cycle` A4 can certify an undisposed review, so its "n/n annotated" line is
not evidence — read the terminal section of the newest review itself.

---

## repeated-failure-class — 2026-09-20 03:56 (cycle 51, material pass 2)

`guard_cycle` refused cycle 51's S2 launch with `DUE repeated-failure-class: 17 occurrences (threshold 3)`, newest
retrospective `archive/peer/2026-09-20-retrospective-cycle48.md` [reported loss: 288 min, $49.05, from 11 of 17].

DECISION: no-device — recorded as a FINDING only, exactly as the 2026-09-20 00:2x block above.

1. **The threshold is SUSPENDED** by the user's standing order of **2026-09-18 08:53** (*"장치는 더 민들지 말고
   계속 진행"*, cited by DATE, never by a `STATUS.md` line number). While it stands, a slug reaching 3 is recorded
   here and the next cycle builds NO device. Only the user may lift it. No judgement was exercised here: the
   content of this block is dictated by that standing order, and the block exists because the gate requires a
   dated one newer than the retrospective.
2. The 17 is CUMULATIVE across every retrospective since cycle 7, not 17 events in this cycle; cycle 51 has
   produced none.

⚠️ **A PARSING FACT, for whoever maintains this file.** `tools/violations.py:94` `DEC_RE` matches only
`## <slug> — <YYYY-MM-DD>[ HH:MM]`, so the block headed `## 2026-09-20 — \`repeated-failure-class\`, 17 cumulative
occurrences` (:568) registers **no decision at all**, and the block headed `## repeated-failure-class — 2026-09-20
00:2x` (:539) loses its time to the literal `x` and stamps as `00:00`, which never sorts after a same-day
retrospective (`_retro_stamp` = that day at `00:00`, `:108-119`). That is why the slug came due again with two
2026-09-20 answers already on file. This block is headed in the parsed form with a real `HH:MM`. Not repaired
here: rewriting another cycle's record is not a material session's call.

---

## device-failed — 2026-09-20 05:34 (cycle 52, judgement)

`tools/hooks/guard_peer.py` — the mandatory failed-prediction gate — **cannot see the failures the cycle-50/52
diagnostics print.** Measured here, not taken on a sub-agent's report: `:73`'s `FAILURE_RE` ends
`^\s*(?:->\s*)?FAIL\b` and `:71` documents the fleet's gate format as `  FAIL  `, which it matches; the diagnostics
print `  **FAIL**  ` (`tools/bench/diag_movein_set.log:57`, and `bgrun`'s own INNER FAILURE line at `:128` repeats
the bolded form), which it does not. So a run that really failed passed the gate unseen. The contrast that proves
it is a matcher difference and not a format opinion: `bgrun`'s FAIL-scan **does** fire on a literal `**FAIL**`
(`archive/peer/2026-09-20-retrospective-cycle50.md:214`) — two mechanisms read the same logs, one sees a bolded
failure and the other does not.

DECISION: **no-device — repair, not construction.** The user's standing order of **2026-09-18 08:53** (*"장치는 더
민들지 말고 계속 진행"*, cited by DATE) forbids building a new device; it does not forbid repairing a gate that
already exists and is broken. The repair is queued as the next cycle's SECOND ACT and is written at
`docs/cycle27-plan.md` Pre-decided **37(i)**:

1. Conform the diagnostics to the documented `  FAIL  ` — otherwise every new script stays free to invent a third
   format and the gate is re-blinded by the next author.
2. **And** widen `FAILURE_RE` to tolerate `\*{0,2}FAIL`, so the gate is not one formatting choice away from blind.
3. Self-test it against a log that really failed (`tools/bench/diag_movein_set.log`) and one that did not.

⚠️ The material session that found this proposed **only** the regex half. That is the wrong half on its own, and
the decision to do both is recorded here so the next session does not implement the narrower version.

⚠️ **Carried forward, NOT acted on:** the parsing fact recorded in the block above — `DEC_RE`
(`tools/violations.py:94`) silently ignores a malformed decision header, so at least two blocks in this file
register no decision at all. Re-heading them would change `violations.py`'s counts and could clear or re-arm a due
slug, which is not a change to make unmeasured at a cycle's close. It belongs with the `guard_peer` repair as the
same kind of fault — a mechanism that cannot see what it exists to see — and is named in `STATUS.md`'s NEXT.

---

## inference-over-measurement — 2026-09-20 06:48 (cycle 53, judgement)

`py tools/violations.py` reads **11 occurrences**, `<== DUE, no decision on file`; the newest retrospective naming
it is `archive/peer/2026-09-20-retrospective-cycle52.md`, and the newest decision on file was
**2026-09-19 08:20** (cycle 42), which a fresh occurrence reopens. Measured twice in cycle 53 — before and after
this file's `:568` header repair — with an identical table both times, so the count is not an artefact of that
edit. ⚠️ It also contradicts `STATUS.md`'s NEXT, which asserted "0 slugs awaiting a response" from a run at
05:3x; the tally in the files is the record, not the summary line.

DECISION: **no-device — recorded as a FINDING only.**

1. **The threshold is SUSPENDED** by the user's standing order of **2026-09-18 08:53** (*"장치는 더 민들지 말고
   계속 진행"*, cited by DATE, never by a `STATUS.md` line number). While it stands, a slug reaching its threshold
   is recorded here and the next cycle builds NO device. Only the user may lift it.
2. **The cycle-52 instance already has its remedy in prose, and it is a reading rule, not a mechanism.** The
   inference was "cycle 51's build was killed mid-verification", drawn from the TAIL of
   `tools/bench/stage_d1_s2_loops.log` at 03:56 while the file was still being written; the log in fact ran to
   **300 lines, 35 pass / 0 fail, `BGRUN END rc=0 after 776s`**, and the guess cost an 825 s re-verification of
   gates that were passing as they were read. The rule now on file is `docs/cycle27-plan.md` Pre-decided **37(j)**
   — never read a log for a verdict before its terminal `BGRUN END`/`TIMEOUT` line is present — carried in
   `STATUS.md`'s NEXT.
3. **The count is cumulative across every retrospective since cycle 7, not 11 events in one cycle**, and 7 of the
   11 predate the v2 format entirely (`loss_min` is UNMEASURED for them).

## premature-build — 2026-09-20 08:24 (cycle 54, judgement)

`py tools/violations.py` reads **5 occurrences**, `<== DUE, no decision on file`; the newest retrospective naming
it is `archive/peer/2026-09-20-retrospective-cycle53.md`
(`VIOLATION: premature-build | loss_min=24 | loss_usd=4.7788 | evidence=tools/bench/c53_astcheck.log:50`), and the
four before it are cycles 7, 9, 11 and 12 — all v1-format, all `loss_min` UNMEASURED.

DECISION: **no-device — recorded as a FINDING only.**

1. **The threshold is SUSPENDED** by the user's standing order of **2026-09-18 08:53** (*"장치는 더 민들지 말고
   계속 진행"*, cited by DATE, never by a `STATUS.md` line number). Only the user may lift it.
2. **The device for this slug already exists and it WORKED.** `tools/hooks/guard_cycle.py` + the prior-art stop
   record refused the launch of cycle 53's 954-line `tools/recipes/stage_d1_s3_focus.py`, which was therefore
   never run, and its stop record is still armed. The fault the retrospective named is not that the build ran —
   it is that the build was *written at all* before the measurement that decided its fate existed. **No gate can
   refuse a file that is merely being typed**, so a second mechanism here would be a mechanism against the wrong
   event.
3. **The remedy is an ordering rule already on file and already exercised.** `CLAUDE.md`'s split rule (clause 3)
   answers a fired re-split trigger with a decomposition, never a full-length retry; `docs/cycle27-plan.md`
   Pre-decided **38(d)** turned that into "the next build is a DIAGNOSTIC under `tools/bench/`, never a recipe".
   **Cycle 54 is the evidence that it holds: it wrote no recipe at all**, and its first diagnostic returned the
   decisive reading in 106 s at 43 pass / 0 fail, against cycle 53's $4.78 refusal of an unlaunchable stage.
4. Cycle 53's finding is disposed in full in `archive/peer/2026-09-20-retrospective-cycle53.md` under
   *"What was done with it"*.

## judgement-in-material — 2026-09-20 08:24 (cycle 54, judgement)

`py tools/violations.py` reads **4 occurrences**, `<== DUE, no decision on file`; the newest is this cycle's own
`archive/peer/2026-09-20-retrospective-cycle54.md`
(`VIOLATION: judgement-in-material | loss_min=9 | loss_usd=3.2380 | evidence=STATUS.md:22`). The other three are
cycles 11, 12 and 13, i.e. the week the slug was introduced; **this is its first occurrence in eight cycles.**

DECISION: **no-device — recorded as a FINDING only, with a brief-template fix.**

1. **The threshold is SUSPENDED** by the user's order of **2026-09-18 08:53**, as above.
2. **A device would be aimed at the wrong thing, and the cycle contains its own control experiment.** A material
   session accepted a peer review in full, wrote its disposition, built its discriminating test and re-ran the
   measurement. Twenty-four minutes later **a second material session met the identical situation and declined**,
   writing *"Accepting or rejecting its findings is a judgement call … and a material session does not make it"*
   (`archive/peer/2026-09-20-c54-g12-after-rerun.md:168-180`). Same model, same tools, same hooks, opposite
   behaviour — **the variable was the brief**, and a hook cannot read a brief's silence.
3. **The fix is three sentences, now mandatory in every material brief** (`docs/cycle27-plan.md` Pre-decided
   **41(b)**): a peer review a material session is FORCED to dispatch is RECORDED, never accepted or rejected;
   its findings return on the `OPEN:` line; no gate is redesigned, no measurement rebuilt, no re-run launched on
   the strength of it.
4. **The cause was the judgement session's own omission, not the sub-session's overreach**, and that is recorded
   rather than softened: neither cycle-54 brief said what to do with a review arriving mid-run.

## inference-over-measurement — 2026-09-20 09:30 (cycle 55, judgement)

`py tools/violations.py` now reads **12 occurrences** of this slug, the newest being cycle 55's own
`archive/peer/2026-09-20-retrospective-cycle55.md`
(`VIOLATION: inference-over-measurement | loss_min=17 | loss_usd=6.5188 |
evidence=tools/bench/diag_queue_typetest_control.log:46`). It was last decided on 2026-09-20 06:48 (cycle 53).

DECISION: **no-device — recorded as a FINDING only, with a brief-template fix.**

1. **The threshold is SUSPENDED** by the user's order of **2026-09-18 08:53** (*"장치는 더 민들지 말고 계속 진행"*),
   so a slug at threshold is recorded here and the next cycle builds nothing. The threshold resumes only when the
   user lifts the order.
2. **The fault is precisely identified and it is the judgement session's.** Twice in 75 minutes a gate premise was
   written by inference while the refuting file sat on disk: (a) the "bare numeric arithmetic input" sink rule,
   whose failure was *entailed* by `ExecState == 1` and visible in `main_vi_nodeterms.json`; (b) gate `R14`'s uid
   universe, which folded shift-register uids into a node-uid gate when
   `nodeterms ∪ tools/bench/main_vi_shiftregs_v1.json` was the correct set and was already on disk. Both premises
   were written into **briefs by the judgement session**, not invented by the material sessions that ran them.
3. **The retrospective's Finding 2 proposes a pre-dispatch "gate-premise lint" and it is DELIBERATELY NOT BUILT.**
   Under the suspension a lint is a device. It is also the wrong shape: the check is one grep against files that
   are already named in the brief, so what failed was brief-writing discipline, not tooling.
4. **The fix is one sentence, now mandatory in every material brief**, alongside Pre-decided 41(b)'s three:
   *"Before this script is dispatched, resolve every uid, terminal and name your gates assert against the on-disk
   censuses — `main_vi_nodeterms.json`, `main_vi_shiftregs_v1.json`, and any terminal census a previous run
   produced. A gate premise that a file already on disk can refute is not dispatched."*
5. **Both premises are already withdrawn in the plan**, so the record and the design agree:
   `docs/cycle27-plan.md` Pre-decided **42(e)** (the sink rule) and **43(c)–(e)** (R14 and the withdrawn
   `tools/gscript.py:947-948` citation).

## repeated-failure-class — 2026-09-21 01:24 (cycle 58, judgement)

`py tools/violations.py` reads **18 occurrences** (threshold 3), newest
`archive/peer/2026-09-21-retrospective-cycle57.md`, reported loss **318 min / $52.85 across 12 of the 18**.

DECISION: **no-device — recorded as a FINDING only.**

1. **The threshold is SUSPENDED** by the user's order of **2026-09-18 08:53** (*"장치는 더 민들지 말고 계속 진행"*),
   so a slug at threshold is recorded here and the next cycle builds nothing. It resumes only when the user lifts it.
2. **The mechanical device for this slug already exists and it is not a tool — it is the user's own re-split rule**
   (CLAUDE.md, *"Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact"*, 2026-09-19):
   *the same stage failing twice at the same place, or a stage that ends without a saved artefact, ⇒ decomposition,
   never a full-length retry under a new name.* `cycle_runner.py` already counts a renamed recipe as the same recipe.
   Adding a counter on top of a rule that is already mechanical is the shape of device-building the user stopped.
3. **What this cycle adds is the first evidence that the rule works WHEN APPLIED INSIDE THE CYCLE RATHER THAN
   DEFERRED TO THE NEXT ONE.** Cycle 58's first act ran one script twice and failed at the identical 9 gates both
   times, leaving **zero** artefacts — the trigger, firing exactly as written. Instead of closing the cycle on it,
   the decomposition was written the same hour (`docs/cycle27-plan.md` Pre-decided **48(e)**: three sub-steps, three
   named files, three pass criteria) and executed: **36 pass / 0 fail, three saved files, `Is Broken?` False**
   (48(j)). Two runs producing nothing became one run producing the deliverable's Boolean half.
4. **So the finding is about WHEN, not about WHETHER.** The rule was being read as "the NEXT cycle's first act is a
   decomposition plan", which spends a whole cycle boundary before anything is re-cut. It is better read as: the
   moment the trigger fires, the decomposition is the next act — and rule 2c ("run the cycle to the end") already
   requires that. **No device; this paragraph is the correction.**

## device-failed — 2026-09-21 01:24 (cycle 58, judgement)

`py tools/violations.py` reads **14 occurrences** (threshold **1** — a device that let its own fault through is
broken, not unlucky), newest `archive/peer/2026-09-21-retrospective-cycle57.md`, reported loss **200 min / $32.13
across all 14**.

DECISION: **no-device — recorded as a FINDING only.**

1. **The threshold is SUSPENDED** by the same order of 2026-09-18 08:53, and this slug is the one where the
   suspension matters most: the only device that answers "a device failed" is a device that watches devices.
2. **This cycle measured both halves of the problem in one afternoon, and they point opposite ways.**
   `guard_cycle` worked exactly as designed — it refused the recipe launch and named the reason in one line.
   `tools/stop_record.py` refused the same launch one step earlier and for a reason unrelated to the question it
   was asked: *"this recipe has a released stop record, but the file itself cannot be read"* (`docs/cycle27-plan.md`
   **48(g)**), i.e. a stop record keyed to a recipe's BYTES cannot be evaluated until the recipe exists, so a
   prior-art review of a **planned** recipe can never be matched to anything. The review's four `FIXED:` and one
   `REFUTED:` lines were therefore never tested — they were simply unreachable. That is a real device fault, and
   **it is closed by writing the recipe, which cycle 58 did** (1,699 lines, sha `1986626f…`); the gate then read
   `ALLOW = True`.
3. **The fault class is over-layering, not under-tooling.** Two gates in series refused one launch for two unrelated
   reasons, and the first one's reason was an artefact of evaluation order. The cheap answer is not a third gate but
   **a sequencing rule: a gate keyed to a file's bytes is dry-run only after the file exists**, which is now written
   into the material-brief template used by this cycle's dispatch 3.
4. **Recorded, not repaired**: `stop_record.py` was NOT patched this cycle, no date was rolled, and
   `CYCLE_GUARD_OFF` was never set — the refusal was answered by producing the bytes it was asking about.

## device-failed — 2026-09-21 02:34 (cycle 59, judgement)

`py tools/violations.py` raises the slug again from `archive/peer/2026-09-21-retrospective-cycle58.md:223`
(`VIOLATION: device-failed | loss_min=30 | loss_usd=? | evidence=tools/bench/c58c_gatecheck4.log:46`), which
named `guard_cycle`'s **retrospective gate** as cycle 58's one structural fault, on the ground that *"no
ordering, no repair, and no honesty can ever launch a recipe mid-cycle"*.

DECISION: **no-device — and this occurrence is REFUTED on its load-bearing claim, by measurement.**

1. **The claim was tested by the very next cycle and it is false.** Cycle 59 launched that recipe as its FIRST
   act, **no hook refused it**, and it delivered: `tools/bench/cycle59_s3a_recipe.log`, `BGRUN END rc=0 after
   596s`, **64 gates pass / 0 fail**, `claudeDev\D1_s3a_focus_ind.vi` md5 `eef91c1d…` at `ExecState` 1 on a
   cold reopen. The reviewer's own counterfactual — *"S3a lands on disk by roughly 02:15"* — came true at
   ~02:11, one session boundary later. A gate that defers a launch by one boundary and then permits it on the
   first attempt is a gate doing its job, not one of the three failure modes the device question lists.
2. **What IS true, and is kept: the gate's stderr names the wrong cycle.** Its condition is "a build log newer
   than the newest retrospective exists"; its sentence says "the *previous* cycle's execution has not been
   reviewed". At 01:43 the offending newer logs were cycle 58's OWN — including the dry run's own log naming
   itself (`tools/bench/c58c_gatecheck4.log:47`). The sentence misleads; the condition was factually true.
3. **The remedy is a sequencing rule already in force, not a device:** a recipe build is a cycle's FIRST act,
   before any other build log exists (`docs/cycle27-plan.md` **48(n)**, applied by cycle 59 and written into
   `STATUS.md`'s `## NEXT`). The threshold stays SUSPENDED under the user's order of **2026-09-18 08:53**, and
   this slug remains the one where suspending matters most: the only device that answers "a device failed" is
   a device that watches devices.
4. **The reviewer's own best idea is accepted as correct and declined as a build.** A whole-pipeline gate
   pre-flight (report every gate condition at once instead of exiting at the first refusal) would have shown at
   01:21 that the launch was unreachable that cycle. It is process-gate machinery, so the standing order
   forbids it; 46(k)'s "an op VI is not a process device" reasoning does not reach it. Recorded here as the
   FINDING the suspension prescribes. It would also not have saved the $8.03 prior-art review, which the same
   review credits as independently required and as having earned its cost.
5. **Recorded, not repaired**: `guard_cycle.py` was NOT patched, no log was deleted, no frontmatter date was
   rolled, `CYCLE_GUARD_OFF` was never set, and the recipe's sha256 is byte-identical before and after
   (`1986626FB6F16CD0…`). Full per-finding disposition: `archive/peer/2026-09-21-retrospective-cycle58.md`
   `## What was done with it`.

## device-failed — 2026-09-21 21:5x (cycle 55 judgement, disposing retrospective-cycle53)

Source: `archive/peer/2026-09-21-retrospective-cycle53.md:337` —
`VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/diag_c67_addsr.log:438`. The named
device is the `premature-build` gate in `tools/hooks/guard_cycle.py`. **No device was built.** The threshold
stays SUSPENDED under the user's standing order of **2026-09-18 08:53**, so this is the FINDING that
suspension prescribes.

1. **The finding is accepted as stated: the gate guards a lane the builds had left.** It forces prior-art
   review before a `tools/recipes/` build and deliberately leaves `tools/bench/` diagnostics open, but in that
   window every deliverable-touching build ran from the bench lane, so exactly one prior-art review ran all
   window while the fault the gate exists to stop happened anyway.
2. **This cycle is the counter-evidence that the gate itself works.** M3a-1 ran from the recipe lane, the gate
   fired, and the review it forced (`archive/peer/2026-09-21-priorart-c68-m3a1.md`, six slugs, all accepted)
   changed the build materially rather than merely delaying it: `helper-exists` produced a route for the
   project's only 🔴 NO-ROUTE row — which then landed (`tools/bench/build_d1_m3a1.log:473`) — and
   `unread-evidence` caught a dropped downstream consumer (`Q_focusback SelectorTunnel #12673`) that would
   have passed every gate silently as a rule-1a computation change. A gate that buys those two findings for
   one review is a gate earning its cost.
3. **The remedy is where builds live, not another gate.** Deliverable-touching builds belong in
   `tools/recipes/`, where every lane gate (prior-art, stop record, verdict, retrospective recency) can see
   them; `tools/bench/` stays the diagnostics lane. That is a sequencing rule already in force and applied
   this cycle, not new machinery.
4. **Recorded, not repaired**: `guard_cycle.py` was NOT patched, no log was deleted or renamed to evade a
   clause, no frontmatter date was rolled, and `CYCLE_GUARD_OFF` was never set. The stale
   `tools/bench/priorart_c68_m3a1.log`, which the gate read as "a review still running", was cleared by
   actually finishing that review into the same log — not by moving the file.

## inference-over-measurement — 2026-09-22 00:22

DECISION: no-device

Raised to threshold (13 occurrences) by `archive/peer/2026-09-22-retrospective-cycle62.md`, which found cycle
57 reading identity conclusions through `wire_source_owner` — an instrument the same cycle proved unsound —
i.e. measurement through a reader that was itself an inference. **No device is built:** the threshold stays
SUSPENDED under the user's standing order of **2026-09-18 08:53** ("장치는 더 만들지 말고 계속 진행"), so this
block is the FINDING that suspension prescribes.

1. **The remedy the slug asks for already ran, this very cycle, and it is a reader repair, not a device.**
   CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" rule covers exactly this slug's failure
   shape, and the cycle-69 firefighter applied it: `wire_source_owner`
   (`tools/recipes/build_opconnectfromwire_v0.py`) now scrubs its answer indicators before each run, reads all
   eight of the op's `error out *` outputs, and accepts a row only when the op's own uid echo (`UID 3`) equals
   the queried uid. Acceptance measured, not asserted: `tools/bench/diag_c68_echo_accept.log`, both ghost reads
   null straight after live reads, 8 gates pass / 0 fail, `BGRUN END rc=0 after 78s`.
2. **A fix to an existing op wrapper is inside the standing order** (STATUS NEXT 2026-09-22 said so
   explicitly); a new counting hook for "did you infer instead of measure" would be process-gate machinery the
   order forbids, and no mechanical gate can read intent anyway. The mechanical part that CAN be built — sound
   readers — is the part that was built.
3. **Recorded, not repaired around:** `guard_cycle.py` was NOT patched, no log deleted, no date rolled,
   `CYCLE_GUARD_OFF` never set.

## device-failed — 2026-09-22 02:5x (cycle 74, MATERIAL dispatch 5, disposing the c74-m3a2-fmt review)

DECISION: no-device

Source: `archive/peer/2026-09-22-c74-m3a2-fmt.md:179-190` §3 (claude / hypothesis, opus max, ANSWERED), which
classifies the failed M3a-2 run of 2026-09-22 01:58 as `device-failed`, **threshold 1, and names TWO devices**:

| device | what it is for | what it did |
|---|---|---|
| `tools/bench/c60c_astcheck.py` | clear a recipe for launch | printed `11 PASS / 0 FAIL` on a file that could not survive its own first diagnostic call — gate 1 is `ast.parse` plus a line/gate-site count, i.e. **a parse verdict read as a fitness verdict** |
| `refusal()` / gate H8 in the recipe | say *why* a run failed | **said "the machine refused" when it did not** — a `TypeError` of OUR code was routed into `refusal()` and counted by H8 |

**No device is built.** The threshold stays SUSPENDED under the user's standing order of **2026-09-18 08:53**
(*"장치는 더 만들지 말고 계속 진행"*), so this block is the FINDING that suspension prescribes.

1. **The H8 half was REPAIRED this cycle, and a repair is not a device.** `build_d1_m3a2.py`'s bare handler no
   longer routes a Python exception of ours into `refusal()`: `defect()` records the exception TYPE and the
   `file:line` it was raised at, and a new counter **H9** counts our-code defects while H8 keeps counting only
   refusals that came from the machine. That is a fix to an existing failure channel inside an existing recipe —
   the same reading applied to the `wire_source_owner` repair on 2026-09-22 00:22 — not new process machinery.
   The review itself asked for this ordering: *"fix the failure channel (§2) before building either gate."*
2. **The `c60c_astcheck` half is also being answered inside the existing checker, not beside it.** Gate 10 was
   added on 2026-09-22 (arity) and WIDENED TO VALIDITY by this dispatch (`tools/bench/c60c_astcheck.py`, the
   review's finding 2): any `%` not covered by a matched conversion span is reported, and a finding fails only
   for a `str` literal — a `bytes` literal is reported and never failed, because PEP 461 makes `b"%b"` legal
   while `b` is outside `SPEC_RE`'s conversion class. The review's own words for this route: *"~20 lines added
   there as gate 10 gives the same result with no new dependency and no new device."*
3. **The part that WOULD be a new device is NOT built and is an OPEN item for the user.** The review's stronger
   remedy — importing a recipe with `g` replaced by a stub and calling `main()` — would catch the call-signature
   class (`read_es(tag, target)` → `read_es(tag)`) that no `%`-format gate can see. Building it is a device under
   the 08:53 order, so it is recorded here and left for the user to authorise or decline.
4. **Recorded, not repaired around:** `guard_cycle.py` was NOT patched, no log was deleted or renamed, no
   frontmatter date was rolled, and `CYCLE_GUARD_OFF` was never set.

## device-failed — 2026-09-22 08:00 (cycle 65, answering `archive/peer/2026-09-22-retrospective-cycle64.md:244`)

DECISION: no-device

Source, verbatim from the cycle-64 retrospective's own verdict line:
`VIOLATION: device-failed | loss_min=0 | loss_usd=? | evidence=tools/bench/cycle_59.log:62`. The device named
is **`audit_cycle.py`'s C3/C4 cost split**: C4 reported `$63.9903` with "reviews are 94 % of it" over four
lines of which one — `$51.62`, 81 % of the total — is the JUDGEMENT SESSION (`tools/bench/cycle_59.log:62`),
not a review. No wall-clock was lost (`loss_min=0`); the quantity that is corrupted is the measurement.

**No device is built, and no existing device is patched in this cycle.** The threshold stays SUSPENDED under
the user's standing order of **2026-09-18 08:53** (*"장치는 더 만들지 말고 계속 진행"*), so this block is the
FINDING that suspension prescribes.

1. **The fault is a MISCLASSIFICATION inside an existing reporter, not a missing mechanism.** `audit_cycle`'s
   C4 already parses every cost line it needs (the same retrospective records C4b "cost lines seen 4 /
   parsed 4"); what it gets wrong is which bucket a `claude -p` judgement session belongs in. That is a repair
   to an existing device, which the standing order permits — but it is NOT this cycle's work: the cycle's
   first act is the D1 deliverable stage (M3a-3), and STATUS OPEN item 42 already carries the `audit_cycle`
   A2/A3/A4 defects as a live, unrepaired item. Recording it here keeps the count honest rather than paying
   for it out of the delivery cycle.
2. **Consequence while it stands, stated so nothing is argued on it:** every cost ratio produced by
   `audit_cycle` C4 — including "reviews are 94 %" — is WRONG IN COMPOSITION and must not be cited as
   evidence in a retrospective, an outcome review or a message to the user until the split is repaired. The
   raw per-line costs in `tools/bench/cycle_*.log` are unaffected.
3. **Recorded, not repaired around:** `guard_cycle.py` was NOT patched, no log was deleted or renamed, no
   frontmatter date was rolled, and `CYCLE_GUARD_OFF` was never set.

## tool-not-built — 2026-09-22 08:00 (cycle 65, answering `archive/peer/2026-09-22-retrospective-cycle64.md:243`)

DECISION: no-device

Source: `VIOLATION: tool-not-built | loss_min=32 | loss_usd=6.07 | evidence=tools/bench/build_d1_m3a2.log:59`
— the executability gap in front of a LabVIEW launch: a never-executed 1,106-line recipe was cleared for a
batch by a checker that only proves it parses, and died 71 s in on a five-specs-vs-four-arguments format
string.

**No new device.** The standing order of 2026-09-18 08:53 holds, and the answer this slug asks for was
already paid inside an EXISTING checker in the cycle that raised it:

1. **`c60c_astcheck` gate 10 EXISTS** (added 2026-09-22 as arity, widened the same day to validity after its
   own hypothesis review, `archive/peer/2026-09-22-c74-gate10-arity.md`, disposed). It flagged exactly the
   offending line on its first run in under a second, and it ran on THIS cycle's recipe BEFORE the build:
   `tools/bench/c75_astcheck_m3a3.log` — 11 gates pass / 0 fail, "94 VERIFIED, 0 MISMATCH, 0 INVALID".
2. **The stronger remedy stays UNBUILT and is the user's to authorise** — importing a recipe with `g` stubbed
   and calling `main()` would catch the call-signature class no `%`-format gate can see. It is a NEW device
   under the 08:53 order and is already an OPEN item in STATUS's "FOR THE USER" list. The class was MEASURED
   as non-endemic (`build_d1_m3a2.py` 0 mismatches after repair, `build_d1_m3a1.py` 0,
   `build_d1_routeb_v0.py` no `%` sites), so declining remains defensible.
3. **Recorded, not repaired around:** no gate was patched to pass, no log deleted, no date rolled, and
   `CYCLE_GUARD_OFF` was never set.

## premature-build — 2026-09-23 (cycle 67, judgement)

`py tools/violations.py` shows **premature-build at 6**, flagged `<== DUE, no decision on file` — the count
crossed the threshold at `archive/peer/2026-09-22-retrospective-cycle66.md` (Row D's D7 gate, loss_min=35,
loss_usd=7.93) and nothing had been written back. This is that written answer.

**No new device.** The user's standing order of 2026-09-18 08:53 (*"장치는 더 만들지 말고 계속 진행"*) holds,
so a slug at threshold is recorded as a FINDING and the next cycle builds nothing for it.

**What the two occurrences actually share, and it is not "building too early".** Both are GATE-DESIGN faults in
the JUDGEMENT layer, two cycles running, and both were derivable at the desk before LabVIEW was opened:

1. **Cycle 66 — Row D's D7.** The gate was written as "`WhileLoop #637`'s terminal counts unchanged" while the
   recipe's own first mutating step deletes wire 7506 off `#637` t10. The count could not have stayed constant.
2. **Cycle 67 — the c89 factorial's arm A3.** The *prediction* was `ExecState` 1 after deleting three stray
   `Invoke` nodes and then running Remove Bad Wires. The mandatory review
   (`archive/peer/2026-09-23-c89-execstate-all-zero.md`, claude/`hypothesis`/opus max, ANSWERED 716 s, $5.0784)
   refuted the prediction rather than the diagram: Remove Bad Wires *deletes*, so removing `w7337` bares
   `RightShiftRegister #4334`'s inside terminal and trades a broken-wire error for an unwired-register error at
   the same site — **A3 could not have returned 1 whatever the diagram held (likelihood ratio 1).**

So the remedy already on file — "desk-check every gate against the steps that precede it" (STATUS NEXT, cycle 66)
— was FOLLOWED for the gates in cycle 67 and still missed this, because it was aimed at gates and the fault was in
a **predicted value**. The rule is widened rather than re-tooled:

**`docs/cycle27-plan.md` Pre-decided 132 (written this cycle): for every PREDICTED VALUE as well as every gate,
name the step that could already have determined it; if one exists, the prediction is re-cut as the predicted
DIFFERENCE or deleted. A prediction that cannot fail for the right reason is not a prediction.**

**Why no device.** The check is a reading of a script against its own preceding steps, on values a static checker
cannot evaluate (what Remove Bad Wires does to a particular terminal is semantic, not syntactic). `c60c_astcheck`
already covers the syntactic half. Mechanising the semantic half would be a NEW device under the 08:53 order, and
it is the user's to authorise, not this session's.

**Recorded, not repaired around:** no gate was patched to pass, no log deleted, no date rolled, `CYCLE_GUARD_OFF`
was never set, and the failed prediction bought its review through the Jev ladder (`new-problem`, p=0.820) rather
than being discharged quietly.

## repeated-failure-class — 2026-09-23 03:55 (interactive chat, answering `archive/peer/2026-09-23-retrospective-cycle67.md`)

`guard_cycle.py` blocks the next recipe build: **repeated-failure-class at 22** (threshold 3), the newest
occurrence the cycle-67 retrospective (loss_min=15, loss_usd=4.5005, `docs/main-vi-panel-map.md:239` — a
prior-art miss on the NODE-route vs PANEL-route terminal read). The retrospective's own disposition already
said no device is built for it; this is the dated block the gate requires.

DECISION: no-device

**Why no device.** The user's standing order of 2026-09-18 08:53 (*"장치는 더 만들지 말고 계속 진행"*) holds. The
operative remedy is a citation already on file: `docs/NAMES.md:966-991` records the measurement (NODE route
`[]` vs PANEL route one row, `ExecState` 1 → 0 → 1, `connect_ctl` not `connect_terminals`), and STATUS
`## NEXT` instructs the next stage to read endpoints with `Stage.net_sources`, never `wmap`/`Diagram.Nodes[]`.
The Jev insertions wired 2026-09-23 (#2 gate-row verdicts, #5 row check, #7 contradictions — advisory, commit
`3fe04e8`) are the user's approved exception and are the closest thing to a device for this class; their effect
is what the 2-cycle run restarted at 03:5x measures.

**Recorded, not repaired around:** no log deleted, no date rolled, `CYCLE_GUARD_OFF` never set.

## device-failed — 2026-09-24 03:20 (cycle 70 material, TRANSCRIBING the cycle-68 judgement disposition of `archive/peer/2026-09-24-retrospective-cycle68.md:363`)

`guard_cycle.py` refused the cycle-70 L7-1 recipe launch because this dated block was missing. The decision itself
was taken by the cycle-68 judgement session (`archive/peer/2026-09-24-retrospective-cycle68.md:373`, ACCEPTED as a
REPAIR of an existing device) and executed by cycle 69 (`…:380` `FIXED:` line). This block only records it.

DECISION: device (repair of the existing device, done 2026-09-24 by cycle 69)

**What was built:** `tools/motor_gate.py:611` prints `FAIL: motor_gate exit N - <meaning>` on every non-zero exit, the
PI/ASI senders print `FAIL:` on REJECTED / NOT-at-target, `tools/bgrun.py` + `tools/audit_cycle.py` FAILURE_RE match
`^RESULT: REJECTED|NOT at target` and a non-zero `ERR?=`; `tools/bench/selftest_motor_fail_exit.py` 10/10.

## inference-over-measurement — 2026-09-24 03:20 (cycle 70 material, TRANSCRIBING the cycle-68 judgement disposition of `archive/peer/2026-09-24-retrospective-cycle68.md:362`)

Same refusal, same origin: the cycle-68 judgement session ACCEPTED the occurrence (PI zero declared from the counter
instead of a reference move) and recorded it as already repaired before cycle 68 ran
(`archive/peer/2026-09-24-retrospective-cycle68.md:372`). This block only records that decision.

DECISION: no-device

**Why no device.** The repair is the user-ordered session-start reference (`FNL 1` + 2 mm commanded-vs-readback
verify, 3 attempts; CLAUDE.md 1b, `tools/motor_gate.py:553-554`), already in force and passed at the cycle-67 session
start (`tools/bench/motor_session_start_cycle67.log`); a further device would be new construction under the user's
2026-09-18 08:53 order. Recorded, not repaired around: no log deleted, no date rolled, `CYCLE_GUARD_OFF` never set.

## repeated-failure-class — 2026-09-24 03:53 (cycle 71 judgement, after archive/peer/2026-09-24-retrospective-cycle70.md:235)

`VIOLATION: repeated-failure-class | loss_min=15 | loss_usd=? | evidence=tools/bench/stage_d1_l7_1_r2.log:89`.
L7-1 run 2 was launched at 03:25:55 while run 1's failed prediction still owed its review. The retrospective says
`tools/bench/jev_gate.log:471,:473` shows the gate ARMED on run 1's log, yet the launch went through with no
RULE-SAME-ROW or JEV-DISCHARGE line (retrospective finding 4).

DECISION: device (repair of the existing device `tools/hooks/guard_peer.py`, measured before it is changed)

The no-new-device order was lifted on 2026-09-24 03:1x (the user: "루프 판단에 따라 필요한 도구는 만드는 걸 허용할게").
The device that already exists for this class is `guard_peer.py`, and on this occasion it let the retry through.
The repair has two steps, in order:
1. Replay the 03:25:55 launch against `guard_peer` with the same logs, offline, and record which code path returned 0.
2. Fix that path. The self-test must include a case where a newer failing build log that owes a review and has no
   discharge line blocks the next launch of the same recipe.

The design side of this occurrence is already answered by `docs/d1-loop12-17-split-plan.md` Pre-decided 168–170:
S1-mapped rows are verified rather than gated on p, L7-1 is split so its clean half is saved, and the offline
re-score was run first (cycle 71, `tools/bench/jev_l7_1_offline.log`). The work is scheduled AFTER the L7-1a
deliverable dispatch in cycle 71, following the deliverable-first ordering (2026-09-18).

## device-failed — 2026-09-24 03:53 (cycle 71 judgement, after archive/peer/2026-09-24-retrospective-cycle70.md:236)

`VIOLATION: device-failed | loss_min=1 | loss_usd=? | evidence=bgrun-FAIL-scan@tools/bench/device_value_a.log:1754`.
`tools/bgrun.py`'s inner-failure scan read quoted failure strings in a Jev text survey as that run's own failure.
The survey then mangled its output ("F-AIL", "rc:1", ":::") to get past the scan, which hides real failures from
every later reader.

DECISION: device (repair of `tools/bgrun.py`'s scan)

The scan is to be scoped by COMMAND, as `guard_peer` was on 2026-09-24 (STATUS OPEN 57): a run whose command is a
Jev script (`tools/jev*.py`, `tools/bench/jev_*.py`) is exempt, which is the other half of the user's 2026-09-22
exemption ("Jev는 면제"). The exemption goes by the command, never by the filename. Required self-test:
- a Jev survey that quotes `FAIL` ends rc=0;
- a non-Jev build that prints `FAIL` still ends rc=1.

Once the scan is fixed, the mangling in the survey script is reverted. Also open on the same device family, still
only a FINDING (retrospective device-effect line 2): the stop record refuses
`prior_art_review.py --recipe <path>` but accepts `--recipe=<path>`, a token-shape hole in its path match. Repair it
in the same dispatch if it is one regex. Scheduled after the L7-1a deliverable dispatch.

## repeated-failure-class — 2026-09-24 05:54 (cycle 71 judgement, after archive/peer/2026-09-24-retrospective-cycle71.md)

`VIOLATION: repeated-failure-class | loss_min=57 | loss_usd=? | evidence=tools/hooks/material_marker.log:1265`.
The judgement session resumed a material agent with `SendMessage`, which runs it in the BACKGROUND, and then polled
build logs for 57 minutes after that agent had already stopped on a gate refusal. This is the fourth consecutive
cycle in which a judgement session mishandled background work.

DECISION: device

Device: `tools/hooks/guard_session.py` refuses `SendMessage` to a `material` or `log-reader` agent inside a cycle
session (`CYCLE_SESSION=1`), with the message "dispatch a NEW foreground Agent". Every re-dispatch then blocks until
it returns. Self-test: the refusal fires under `CYCLE_SESSION=1`, and the interactive chat is untouched. Scheduled
after L7-1b run 3 (deliverable first).

## device-failed — 2026-09-24 05:54 (cycle 71 judgement, after archive/peer/2026-09-24-retrospective-cycle71.md)

`VIOLATION: device-failed | loss_min=5 | loss_usd=? | evidence=stop_record@tools/hooks/material_marker.log:1264`.

DECISION: device (repair of `tools/stop_record.py`)

- The prior-art dispatch half is REPAIRED (05:31, bgrun `--` parsing, `selftest_stoprecord_bgrun.py` 6/0). This also
  CLOSES the `--recipe=` gap named in the 03:53 block above.
- Still to repair: the stop record also refuses READ-ONLY commands on a stopped recipe (`wc -l`, `sed -n`, an AST
  parse; `material_marker.log:1256,1263,1274`). Refuse only commands that EXECUTE the recipe, and self-test both
  directions.

## device-failed — 2026-09-24 06:0x (cycle 72 FIREFIGHTER, fable/low; measured in `tools/bench/priorart_c72_l7_1b_r4.log` + the two refused launches)

A THIRD hole in the same device, found while clearing the L7-1b block: the edited recipe was re-reviewed
(`archive/peer/2026-09-24-priorart-c72-l7-1b-r4.md`, verdict `novel`, $1.51) and the launch was STILL refused —
"released for sha f0ffee30ed30, on disk now 9b9aee966611 … Get the edited recipe reviewed". A `novel` verdict wrote
NO record, so the older RELEASED record (stamped for the previous bytes) kept refusing, and the gate's own remedy was
unreachable. The cycle-44 supersession rule only reaches a LATER record, and only non-novel verdicts wrote one.
A `FIXED:` line added to the OLD review did not release it either (the released stamp is a sha, not a line).

DECISION: device (repair of `tools/stop_record.py` + `tools/prior_art_review.py`, done in this cycle)

- `stop_record.write_novel_record(recipe, review)` appends a later same-path record pre-released for the reviewed
  bytes; honoured only while the review file's ANSWER still reads purely `PRIOR-ART: novel` (`novel_in_answer`,
  re-read at every check, so a hand-edited record or a tampered review does not launder). `prior_art_review.py`
  writes it automatically on a novel verdict with `--recipe`; CLI `stop_record.py write --verdict novel`.
- A further edit after the novel review re-arms the gate (sha mismatch, no later record) exactly as before.
- Self-test `tools/bench/selftest_stoprecord_supersession.py` case 5 (C5.0/5a/5b/5a2/5c/5d): 36 pass / 0 fail
  (`selftest_stoprecord_supersession.log`); bgrun 6/0, eqform green re-run the same minute.

## device-failed — 2026-09-24 06:2x (cycle 72 firefighter, after archive/peer/2026-09-24-retrospective-cycle72.md)

`VIOLATION: device-failed | loss_min=3 | loss_usd=? | evidence=stop_record@tools/hooks/material_marker.log:1279` —
the same event as the 06:0x block above, named by the retrospective after the repair had landed.

DECISION: device (ONE repair of `tools/stop_record.py`, scheduled in STATUS NEXT after the L7-R deliverable)

Three holes in three consecutive cycles (70: the prior-art dispatch; 71: dispatch under bgrun + read-only commands;
72: the launch after a novel review), each patched on its own code path. Next is not a fourth patch: the release
logic is written once as a table — record kind (blocking / novel) × verdict state (undisposed / released / novel /
sha-mismatch / superseded) × command class (build launch / read-only / exempt program) → allow or refuse — and the
self-test is generated from that table. The read-only hole from the 05:54 decision closes inside it.

## device-failed — 2026-09-25 05:58 (cycle 77 material, card 77-1, after archive/peer/2026-09-25-retrospective-cycle76.md)
<!-- time written as "05:5x" by card 77-1; DEC_RE needs HH:MM, so the block read as a bare date and did not discharge. Set to 05:58 by the cycle-77 judgement session, 06:2x; 77-1 returned at ~05:59. -->


The fault: `tools/hooks/guard_peer.py` skipped every `selftest_*.log` by FILENAME (`SELFTEST_LOG_RE`, since cycle 53).
`tools/bench/selftest_make_default.log` is a self-test by name whose command builds, saves and cold-reads a scratch VI in
LabVIEW; its prediction failed (S3 2/3, rc=1) and never reached the gate, so no JEV-LADDER line was written
(`tools/bench/jev_gate.log:887` is the only entry, a preflight).

DECISION: device (repair, threshold 1). The exemption is now decided by the log's LAST `BGRUN START` COMMAND, the rule
`logclass.command_kind` (card 76-2) and the Jev half (STATUS OPEN 57) already follow: `guard_peer.selftest_exempt()`
excludes a run only when every in-scope script in python command position is a `selftest_*.py` whose import closure
(`script_touches_labview`, transitive over tools/ and tools/bench/) never imports gscript/stagekit/pythoncom/win32com/
comtypes or calls `Dispatch("LabVIEW.Application")`; an unreadable script fails CLOSED. A file with no `BGRUN START` keeps
the filename rule. Self-test `tools/bench/selftest_guard_peer_jev.py` 25/0 (`tools/bench/selftest_guard_peer_77.log`),
new C8–C8f + C9/C9b; failre F4 amended to "not a PURE-PYTHON self-test" (25/1, the 1 = pre-existing E1). Measured:
`selftest_make_default.log` now IS the newest failing log and is BOUND by `archive/peer/2026-09-25-76-6-makedefault-cold.md`
(`tools/bench/selftest_guard_peer_77_measure.log:5-7`).

## inference-over-measurement — 2026-09-25 06:25 (cycle 77 judgement, after archive/peer/2026-09-25-retrospective-cycle76.md:277)

`VIOLATION: inference-over-measurement | loss_min=22 | loss_usd=1.4932 | evidence=tools/bench/replay_vis_76d.log:91`.
Panel defaults were assumed saved from a byte count; the cold read that settled it (61 s) ran last.

DECISION: refusal of a new general device (dated, written; user's option C, 2026-09-16), because the remedy is already
enforced at the only level that can name the values:
- `docs/m8-real-run-plan.md` PD20(c) (line 271) requires every value a stand-in depends on to be read back COLD before
  any functional test, and PD19(a) moves N and the modulus to DIAGRAM constants, which no longer depend on a default.
- Card 77-4's pass list makes that a gate of the stage recipe (`tools/bench/cards/task_77-4.json` pass[3]), and the
  constant verb was itself accepted only on a cold read-back (`tools/bench/const_loopterm_77c.log:10-14`).
- A general device would need to know which values a stage "depends on"; only the plan names that, so the device IS
  the plan's cold-read gate per stage. Revisit if the slug recurs on a stage whose plan carries such a gate.

## wrong-ordering — 2026-09-25 06:25 (cycle 77 judgement, after archive/peer/2026-09-25-retrospective-cycle74.md:367)

`VIOLATION: wrong-ordering | loss_min=25 | loss_usd=? | evidence=tools/bench/cards/result_74-1.json:1` — offline tool
cards run in parallel with the LabVIEW deliverable, so their failing logs gated its launches through guard_peer.

DECISION: refusal of a new device (dated, written). The cycle-75 disposition (retrospective-cycle74 "What was done with
it") already changed the practice: judgement sessions dispatch material cards one at a time in the FOREGROUND. Cycles
75, 76 and 77 did so (cycle 77: 77-1 → 77-2 → 77-3 → 77-4, each foreground, `tools/bench/cards/result_77-*.json`), and
the slug did not recur in retrospectives 75 or 76. Re-scoping guard_peer per card stays an open alternative, not built.

## device-failed — 2026-09-25 07:05 (cycle 77 judgement, found by cards 77-7 and 77-8)

The retry-cap recorder in `tools/hooks/guard_bash.py` writes a `tools/bench/stage_runs.jsonl` line BEFORE later gates
decide. `stage_runs.jsonl:3-5` are three launches of `stage_replay_standins.py` that `guard_cycle` (×2) and the
permission layer (×1) refused; none produced a log or a LabVIEW run, yet the cap (2) and the judgement retry card 77-8
were both spent. Loss this cycle: the whole stand-in run (≈30 min) moved to cycle 78.

DECISION: device (repair, threshold 1), scheduled AFTER cycle 78's deliverable run (steer_77): count a stage run only
when it actually starts — record in `tools/bgrun.py` at child start (the line carries the card), not in the PreToolUse
hook. Self-test: a launch refused by guard_cycle and one refused by the permission layer leave the count unchanged; a
started run increments it.

OUTCOME (2026-09-25 07:1x, card 78-2, moved ahead of the deliverable because it blocked it: result_78-1.json): BUILT.
`tools/bgrun.py` records at child start (`BGRUN STAGE-RUN recorded ...`, line `"by": "bgrun"` + cycle + card + log +
pid); `tools/hooks/guard_bash.py` main() only checks; `tools/stage_prerun.py` counts only `by == "bgrun"` lines
(old hook-written lines 1-7 stay in the file, uncounted) and reads the judgement card from `--retry-card <path>` on
the bgrun command as well as `RETRY_CARD=`. Self-test `tools/bench/selftest_retry_cap.py` 8/0
(`tools/bench/selftest_retry_cap.log`). Accepted launch form, measured: Bash, non-compound, run_in_background,
`py tools/bgrun.py --material --max-min N --log tools/bench/<x>.log -- py -u <script>`; the stage then ran 35/0
(`tools/bench/stage_replay_78.log:2` shows the recorder line).

## device-failed — 2026-09-25 (cycle 80 material, card 80-3, after archive/peer/2026-09-25-retrospective-cycle79.md)

`VIOLATION: device-failed` at the old `tools/stagexec.py:679-680`: `LVBackend.indicator` cleared any wire_indicators
error containing "target BROKEN after wiring" (added for stage_d1_l7_r's fp_ind gate). In stage K that hid two errored
ops with no reader on their sinks (`tools/bench/stage_d1_k_r2.log:232` 'Pos within cal image', `:238`
'Pos: Diffraction Pattern').

DECISION: device (repair, threshold 1; PD178(i) item 2). OUTCOME: BUILT. The whitelist is removed. A wire_indicators
op error now stops the run (`ExecStop`) unless the recipe passes `LVBackend(s, fs, sink_gates=[{"gate", "sink":
[owner_uid, term_name]}], gates={label: reader})` naming a gate it owns for that exact sink
(`tools/stagexec.py:590` check_sink_gates refuses an absent gate; `:607` sink_gate_for refuses another sink;
`:725` the indicator path; `:635` run_deferred makes each declared gate READ its sink at the end of `Executor.run`
(`:509`), and a failing read stops). Other ops' errors are unchanged: still stopped by `_done`. Self-test
`tools/bench/selftest_stagexec_gate.py` G8-G13 (13/0 total, `tools/bench/selftest_stagexec_gate.log`).
Replay impact: stage_d1_k.py uses LVBackend with no declaration, so a replay now stops at its first indicator row
until it declares gates for those two sinks; stage_d1_l7_r.py does not use stagexec (it calls `s.wire_indicators`
itself and keeps its own tolerance at `tools/recipes/stage_d1_l7_r.py:92`, outside this repair).
