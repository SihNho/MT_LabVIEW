---
type: benchmark
status: current
date: 2026-09-16
tags: [retrospective, violations, measurement]
---

# Retrospective v1 vs v2 — measured on cycles 11, 12 and 13

The user's condition for the redesign was **"MEASURE, before adopting"**. This is that measurement, and nothing
here is a decision: v2 is built and runnable, `guard_cycle.py` was **not** switched to require it, and the two
judgement calls at the bottom are left open.

- instrument v1: `tools/retrospective_v1.py` (frozen copy of the exact text that produced cycles 7–13)
- instrument v2: `tools/retrospective.py` (proposals 1, 2 and 4; proposal 3 — threshold re-tuning — deferred)
- runner: `tools/bench/retro_v2_compare_runner.py`, log `tools/bench/retro_v2_compare.log`
  (`BGRUN END rc=0 after 816s`, **13 gates pass / 0 fail**)
- peer for all six runs: codex, `gpt-5.6-sol`, effort medium, `-Kind fact`, `-TimeoutSec 600`
- the three cycles were chosen because **each fired every slug it could** under v1

## 1. The headline table

| | v1 slugs fired | v2 machine lines | v2 REAL violations | v2 top fault | loss (v2) |
|---|---|---|---|---|---|
| **cycle 11** | **9 / 9** | 4 | **2** | `scope-creep` | 20 min, $5.1157 |
| **cycle 12** | **9 / 9** | 4 | **2** | `judgement-in-material` | 13 min, $? |
| **cycle 13** | **6** | 3 | **1** | `wrong-ordering` | 2 min, $? |

"v2 machine lines" counts every line starting `VIOLATION:` in the answer. Two of them are **not** violations in
each of cycles 11 and 12 (and one in cycle 13): the reviewer echoes the format template `VIOLATION: <slug> | …`
and the line `VIOLATION: none` while explaining the contract. `tools/violations.py` ignores both — `<slug>` fails
`[a-z0-9-]+` and `none` is dropped by name — so the tally is unaffected. **It is still a defect of the prompt**
and the cheapest fix is to stop printing the literal template inside the answer; see OPEN-C.

### v2's violation lines, verbatim

```
cycle 11  VIOLATION: scope-creep | loss_min=20 | loss_usd=5.1157 | evidence=tools/bench/priorart_cycle12_a2.log:4
cycle 11  VIOLATION: device-failed | loss_min=0 | loss_usd=20.4241 | evidence=unreported-fact-cost-split@tools/audit_cycle.py:232
cycle 12  VIOLATION: judgement-in-material | loss_min=13 | loss_usd=? | evidence=archive/peer/2026-09-16-retrospective-cycle12.md:218
cycle 12  VIOLATION: device-failed | loss_min=0 | loss_usd=5.1239 | evidence=tools/bench/priorart_cycle13.log:4
cycle 13  VIOLATION: wrong-ordering | loss_min=2 | loss_usd=? | evidence=tools/bench/peer_flatseq_unreachable.log:2
```

v1's, for the same three cycles: cycles 11 and 12 each emitted `repeated-failure-class · tool-not-built ·
inference-over-measurement · rule-evaded · wrong-ordering · unreported-fact · scope-creep · premature-build ·
judgement-in-material`; cycle 13 emitted six of those nine. **No loss figure appears in any v1 archive** —
`grep -c loss_min` returns 0 for all three.

## 2. Cost of the v2 runs

| | peer wall-clock | dispatcher cost line |
|---|---|---|
| cycle 11 | 362 s | none — codex prints no cost line |
| cycle 12 | 241 s | `$5.1239` appears in the log, but it belongs to `priorart_cycle13.log` quoted in the answer, **not** to this dispatch |
| cycle 13 | 212 s | none |
| **total** | **815 s ≈ 13 min 35 s** (runner wall-clock 816 s) | **unknown in dollars** |

**The dollar cost of a codex retrospective has never been measurable**, v1 or v2: `peer.ps1` only writes a `COST:`
line when the agent prints one, and codex does not. Do not read the absence as zero. The only priced reviews in
this project are the claude-peer prior-art runs ($4.47–$5.87 each).

v2 is not more expensive than v1 in wall-clock: the v1 runs of the same three cycles took 258 s, 247 s and 215 s
(720 s total) against v2's 815 s — **+13 %**, for a window that is correct and a device audit v1 did not perform.

## 3. What the DEVICE EFFECT question found — and it is the strongest single result

The question had never been asked, and on its first outing it found a **broken device**, twice, independently:

> `unreported-fact` round 2 (`docs/violation-decisions.md`, 2026-09-16 15:05) — *"C3 counts `tools/bench/peer_*.log`
> and `priorart_*.log` wall time and the usage/cost lines the claude peer already records"*.

**It does not read the cost lines.** `tools/audit_cycle.py:191` matches only
`total_cost_usd | cost_usd | total_cost`, while every priced log in this project writes `COST: $4.9719  in 48 / …`.
Verified here independently of the reviewer:

```
tools/bench/priorart_a1_v1.log:COST: $4.9719
tools/bench/priorart_a1_v1_rev2.log:COST: $5.8660
tools/bench/priorart_a1_v1_rev3.log:COST: $4.4705
tools/bench/priorart_cycle12_a2.log:COST: $5.1157      -> $20.4241 in cycle 11's window alone
```
and the regex returns `[]` on that exact line. So C4 has printed *"no log reported a cost — treat the review cost
as UNKNOWN"* for every cycle since it was built, and **the device that exists specifically to stop cost being
understated is itself understating cost**. That is the fault it was built to prevent, verbatim.

Cycle 13's v2 run reports **no device failure** — "none of the seven listed devices demonstrably failed" — because
its window contains no priced log. The device list is therefore not a rubber stamp in either direction.

The other six devices were each judged individually per cycle, with citations. Summary of the verdicts:
`rule-evaded` (adversarial prompt) worked 3/3 · `tool-not-built` (prior-art review) worked 2/2, n-a once ·
`repeated-failure-class` (disposition gate) worked 3/3 · `premature-build` worked/n-a 3/3 · `scope-creep` (C7
counter) worked 3/3 · `unreported-fact` (exit propagation) worked in 12 and 13, **failed in 11** (it fired on the
successful string "20 pass, 0 fail" — already repaired afterwards, `tools/bgrun.py:56`, so that half is a
stale-at-the-time observation, not an open defect).

## 4. VERDICT 1 — does v2 discriminate between cycles?

**Yes, and this is the clearest result.** Under v1 the three cycles were indistinguishable: 9, 9 and 6 slugs, the
same six names every time, no sizes. Under v2 they have **three different top faults** (`scope-creep`,
`judgement-in-material`, `wrong-ordering`) and **three different magnitudes** (20 min, 13 min, 2 min). Cycle 13 —
the cycle that produced A3's 112 diagrams and the FlatSequence accessor — comes out as a **well-run cycle with one
2-minute ordering mistake**, which is what the logs actually show and what v1 could not say.

The findings did not vanish: v2's prose still answers all seven questions and still names, for instance,
judgement-in-material in cycle 11's FINDINGS. It simply **refused to promote it to a violation**, explicitly:
*"This is a finding, not the cycle's principal violation, because no implementation decision was taken from the
inference."* That is the finding/violation split doing exactly its job.

## 5. VERDICT 2 — do v2's top faults match what the judgement session believed?

**Partly, and where they do not, the reason is the evidence window — which is a defect in proposal 4, not in the
reviewer.** The judgement session nominated two candidates for the day's costliest error:

| judgement session's candidate | when it happened | which v2 window contains it |
|---|---|---|
| prior-art-then-build: `build_opdelete_v1.log` started **16:26:10** inside `priorart_cycle11.log` | 16:26 | **NOT cycle 11's** (which starts 17:38:44) — it lands in cycle 10's window |
| the 26-wrapper `ensure_loaded` patch made on one measured case | `tools/gscript.py` mtime **17:38:29** | **NOT cycle 11's** — by **15 seconds** |

Both of "cycle 11's" defining errors fall **outside** the window the plan documents define for cycle 11. Cycle 11's
v2 answer says so itself: *"Its delete failures, autofocus retries, missing flag reader, and premature
`OpDelete_v1` build all occurred before 17:38:44."* Two more of the same shape: `diag_load_vs_editmode.log` (17:26)
and `diag_bdloaded_reader.log` (17:37) — the 2-failure stop STATUS attributes to cycle 11 — are also outside it,
and `priorart_cycle13.log` (19:52) sits in **cycle 12's** window, not cycle 13's.

**The cause is structural: a plan document in this project is written and last edited AFTER the cycle's work has
started**, so its mtime is a lagging boundary, not a leading one. Proposal 4 removed v1's 24-hour over-capture and
introduced a systematic under-capture in its place. Both v2 answers flag the same thing from the other side —
*"the many failures cited by retrospective v1 came from its 20/24-hour sliding audit and predate 19:33:32"* — so
v1 was charging one cycle for three cycles' work, and v2 is now charging it for a suffix of its own.

So: v2's cycle-11 verdict (`scope-creep`, 20 min, cycle-12 work inside the cycle-11 window) is **true and
verifiable but is not the error the judgement session was thinking of**, and the reason is measurable.

## 6. VERDICT 3 — what does v2 say about `judgement-in-material`?

Its decision was HELD pending this comparison. The numbers:

- **v1 fired it in all three cycles** (11, 12, 13) — which is how it reached threshold 3 and blocked cycle 14 — but
  it fired it *alongside eight or five other slugs every time*, with no size and no counterfactual.
- **v2 fired it once in three** (cycle 12), as that cycle's **top fault**, with a **13-minute** loss and a
  counterfactual: *"had the material session stopped at the retrospective disposition at 19:46 and handed the nine
  findings to judgement, this cycle would have ended at ~19:46 rather than 19:59."* Evidence:
  `archive/peer/2026-09-16-retrospective-cycle12.md:218` — a MATERIAL session accepted all nine v1 findings and
  declared cycle 13 unblocked.
- In cycle 11 v2 **found the same behaviour and ranked it below** `scope-creep` and `device-failed`; in cycle 13 it
  did not raise it at all.

So the slug is **real, not an artefact** — the behaviour is cited in all three v1 answers and in two of three v2
answers — but its measured magnitude is **13 minutes in one cycle**, not the every-cycle systemic fault a count of
3/3 implies. Whether that earns a device, a written no-device, or a change to how briefs are written is a
judgement call and is **not made here**.

## 7. CLOSED — all five decided by the judgement session, 2026-09-16 21:xx

| | decision | where it landed |
|---|---|---|
| **A** | **v2 IS the retrospective.** `retrospective_v1.py` stays frozen for reference only | `CLAUDE.md` retrospective §, steps 2–3 rewritten to the v2 output contract |
| **B** | the three comparison archives are **flagged out of the tally**, flag-based | `comparison: true` in each archive's frontmatter; `violations.py:is_comparison()`. `--due` now prints nothing, rc=0 |
| **C** | the prompt must **forbid echoing its own template** | `retrospective.py`, the closing block's last instruction |
| **D** | **repair the cost regex** (that is the `device-failed` device) | `audit_cycle.py`: `COST_RE` + `COST_SEEN_RE`, an import-time `_self_test()`, and the new `C4b cost lines seen/parsed` line. Cycle 11's window: **$0.0000 → $19.6411 from 4 logs** |
| **E** | the window is the **previous cycle's retrospective → this cycle's retrospective dispatch**; plan mtime is the fallback only | `retrospective.py:cycle_window()`. Cycle 11 = `14:33:20 .. 19:08:16` and now contains `build_opdelete_v1.log` (16:27:59), `gscript.py` (17:38:29), `diag_load_vs_editmode.log` (17:26:58), `diag_bdloaded_reader.log` (17:37:41) — all four excluded by the old start of 17:38:44 |

The original text of the five open items follows, unedited.

## 7-original. OPEN — for the judgement session only

- **OPEN-A. Does v2 replace v1 as the cycle gate?** `guard_cycle.py` was deliberately left accepting either form.
- **OPEN-B. The v2 archives entered the LIVE tally, and that changed what is blocked.** `tools/violations.py --due`
  now reports, verbatim:

  ```
  DUE judgement-in-material: 4 occurrences (threshold 3) -> ...-cycle11.md, ...-cycle12.md, ...-cycle13.md, ...-v2-cycle12.md [reported loss: 13 min, from 1 of 4 occurrence(s)]
  DUE device-failed: 2 occurrences (threshold 1) -> ...-v2-cycle11.md, ...-v2-cycle12.md [reported loss: 0 min, $25.55, from 2 of 2 occurrence(s)]
  ```

  These are **retroactive re-reviews of cycles already counted**, so cycles 11–13 are now counted twice for
  `judgement-in-material`. The literal reading of the brief was followed (the slug was changed only to avoid a
  filename collision; no counting exclusion was requested), but whether a comparison run should feed the live gate
  is a judgement call. If the answer is no, the fix is one line in `violations.py:scan()` or a rename of the three
  archives — both reversible.
- **OPEN-C. The prompt's format template is echoed into the answer** as a literal `VIOLATION: <slug> | …` line, in
  all three runs. Harmless to the tally, ugly in the archive. One-line fix in `retrospective.py`'s closing block.
- **OPEN-D. `audit_cycle.py:191`'s cost regex does not match `COST: $…`.** Measured above, independently of the
  reviewer. It is a one-line repair of a device that is currently falsifying every cycle's cost line, but it is a
  change beyond what this task named, so it was **not** made.
- **OPEN-E. The plan-mtime window under-captures (section 5).** Candidate replacements, none evaluated: stamp the
  boundary explicitly when a cycle closes (a line in STATUS or a `cycle<N>.done` marker), use the *creation* time
  of the plan rather than mtime, or use the previous cycle's retrospective archive time as the start.
