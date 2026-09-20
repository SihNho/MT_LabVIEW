---
type: narrative
status: historical
date: 2026-08-27
tags: [archive, benchmark]
---

# Benchmarks — archived, both concluded

Two benchmark efforts, merged here during the 2026-08-27 doc audit. Their conclusions already live
in the active docs (`STATUS.md` "Resolved facts" and the `labview-automation` skill); this file keeps
the evidence behind them.

---

# Benchmark — model quality at LabVIEW GUI control

**Why:** the user observed (2026-08-26) that screenshot-and-click automation is too slow and costly,
and asked for a standard to be established before more GUI work. This measures whether model choice
materially changes that cost, so the decision rests on data rather than on my impression.
Proposed originally in `WORKLOG.md` (2026-08-26 session 1) and deferred; the user chose to run it.

## Task (identical for every model)

On a **pre-created blank VI's block diagram**, using only mouse/keyboard automation:

1. Place a **For Loop** on the diagram.
2. Place a **numeric constant** on empty canvas to the **left of, and outside**, the For Loop.
3. Wire that constant to the For Loop's **N** (count) terminal.

This exercises the three things real diagram editing needs: palette navigation, placement, and wiring
to a small terminal.

> **Task revised 2026-08-26 after run 2 — the original was impossible.** It asked for the constant to
> be placed *inside* the loop and then wired to that loop's own `N` terminal. LabVIEW forbids this by
> dataflow: `N` must be resolved **before** the loop starts executing, so a value produced inside the
> loop can never feed it. LabVIEW correctly rendered a broken (dashed, red-X) wire. The agent
> diagnosed this correctly and was right to push back; the fault was in the benchmark design, not the
> run. Any result measured against the original task is not comparable and has been discarded.

## Protocol revision (2026-08-26) — first run aborted, and why

A first Sonnet run was **stopped and discarded**, for two reasons, both about protocol validity
rather than the model:

1. The prompt told agents `drag` could be used "for drawing a wire". That is **wrong** — LabVIEW
   wiring is click-source-then-click-destination. Misleading agents on the hardest of the three
   steps would not measure what we want to measure.
2. The user then pointed out that **LabVIEW snaps to terminals** (verified: hovering names the
   terminal in a tip strip), which materially changes how hard the task is. Benchmarking the old,
   harder-than-necessary technique would answer a question we no longer care about.

That aborted run still produced one genuinely useful data point, recorded here because it is the
dominant failure mode: **it used image-pixel coordinates as screen coordinates without adding the
window offset**, and the click therefore landed in a *different VI's window*. Coordinate-frame
confusion is both the top cost driver and a **safety issue** for delegated GUI work — a stray click
could land on a VI that must not be modified. The revised protocol makes agents read
`GUI_PLAYBOOK.md` (whose §1 is exactly this law) and verify the target window rect before clicking.

Agents now read `GUI_PLAYBOOK.md` rather than receiving hints inline. That deliberately measures
**model + playbook**, which is the configuration we will actually use from here on.

## Rules given to every agent

- Only `tools/lv_gui.ps1` for GUI actions; only the assigned `Untitled N` window.
- **VI Scripting is forbidden** — the point is to measure *GUI* control.
- Never `Save`, never open another VI, never touch anything outside the assigned window.
- Hard cap of **40 tool calls**; stop and report failure if exceeded.
- Report: tool calls used, success/partial/failure, and what specifically went wrong.

## Controls

Only one agent runs at a time — `CLAUDE.md` §3 allows exactly one execution path to touch LabVIEW.
Each model gets its own pre-made blank VI so no run inherits another's mess. Every agent gets the
same prompt, including the same hard-won hints from `tools/lv_gui.ps1`'s header (so we measure
judgement, not knowledge of our tooling quirks).

## Results

| model | tool calls | outcome | notes |
|---|---|---|---|
| Sonnet (run 1, **discarded**) | ~10 | aborted | Protocol bug: prompt wrongly said `drag` draws wires. Failed by using image coords as screen coords -> clicked into a *different VI's window*. |
| Sonnet (run 2, **discarded**) | 60 | task complete but over cap | Measured against the impossible task. **No genuine misclick occurred at any point.** Overrun caused by two of my errors: playbook said `shotwin` prints `W,H` (it prints `right,bottom`), and the task itself was illegal. |
| Sonnet (run 3) | 40 (cap) | PARTIAL | Placed both objects cleanly. **Skipped the hover-verify step to conserve calls**, eyeballed the terminals, and the wire click selected the loop instead. |
| **Claude (me) + new composite tools** | **2** | **SUCCESS** | `probe` to locate both terminals exactly, then `wire`. Solid unbroken wire, verified. |
| Haiku 4.5 (with new tools) | 40 (cap) | **FAILURE** | 0 of 3 steps. Entire budget spent on palette navigation; kept opening the **Controls** palette, which only exists on a Front Panel - i.e. it was clicking the wrong window while believing it had focused the block diagram. Same coordinate-frame failure as run 1. |
| **Opus 5** | **31** | **SUCCESS** | Only run to finish inside budget, with a verified solid-blue wire. Also found two real playbook bugs (below), which account for most of its 31 calls. |
| **Fable** | **40** (exactly at cap) | **SUCCESS** | All 3 verified. Ran with the z-order fix and hardened `wire`, so not strictly comparable. Lost 6 calls to a third playbook bug: aiming the wire source exactly ON the constant's border resolves to the positioning tool. |

### Final scoreboard

| config | calls | steps done | verdict |
|---|---|---|---|
| Haiku 4.5 | 40 (cap) | **0 / 3** | FAILURE |
| Sonnet | 40 (cap) | 2 / 3 | PARTIAL |
| **Opus 5** | **31** | **3 / 3** | **SUCCESS** |
| **Fable** | **40** (at cap) | 3 / 3 | SUCCESS* |

\* Fable ran with the z-order fix and hardened `wire` already in place, and still needed the full cap.
Opus succeeded in 31 **without** either fix.

**This vindicates the user's cost argument** (*"attempting multiple times with lower model might be
more costly than applying higher model"*). Haiku and Sonnet each consumed a full 40-call budget and
produced **nothing usable** — the cheaper runs saved nothing, because the fallback after a failure is
the user doing the work by hand. Opus produced a verified result in 31. Score by *calls to a verified
success*, and count a failure as a failure, not as a cheap partial.

**Practical reading:** Haiku 4.5 is **not viable** for LabVIEW GUI control here - it never got past the
palette. Sonnet is competent at placement but runs out of budget before wiring. Neither result argues
for buying a bigger model; both argue for **removing round-trips**.

### What Opus found that three other runs did not

Both are now fixed in the tooling and the playbook, and both had been silently costing every run:

1. **Z-order defeats the rect check.** `shotwin` uses `PrintWindow`, so it reports the rect of a window
   even when that window is *completely occluded*. A coordinate can be provably inside the target's
   rect and still land on whatever is on top. Opus's click landed on a **different VI entirely** and
   opened its label context menu — a rule-adjacent near-miss (no modification occurred; a select-click
   and a right-click do not change a VI, and that window already carried a `*`). **This very likely
   also explains Haiku's failure** — it kept getting the Controls palette, i.e. it was reaching a
   *front panel* it had not focused. The fix is `focus` -> re-`shotwin` -> click.
2. **`wire` could leave the wire dangling in rubber-band mode, silently.** `wire` returned normally and
   `probe` read all white while LabVIEW was in fact holding a pending rubber-band wire. A single plain
   `click` at the destination committed it. My earlier "`wire` is a reliable 2-call primitive" claim
   was over-sold — it happened to work first time in my own test. The primitive has since been
   hardened (approach each terminal before clicking; drop the +1 px jiggle that can nudge off a small
   terminal), and the failure mode plus its recovery are now documented.

Opus's own estimate: with those two known, the task would have taken **~20 calls** rather than 31.

### CONCLUSION (2026-08-26): the bottleneck is round-trips, not model choice

Three runs converge on the same answer, and a control experiment confirms it.

Every run placed the objects competently. Every run then lost its budget to the same thing: locating a
~4-pixel terminal took 3-4 calls of crop-and-eyeball, so under a call budget the model is *pushed*
into skipping verification - and skipping it is exactly what fails. Sonnet run 3 said so explicitly:
"I skipped the mandatory hover-verify step to conserve calls."

So the fix was never a better model. It was **collapsing the verify loop into one deterministic call.**
Adding `probe` (colour-scan a pixel line to find terminals exactly) and `wire` (click-click) reduced
the step that had defeated a whole 40-call budget to **2 calls, first try, verified working**.

**Standing recommendation:** spend effort on composite tooling and on VI Scripting, not on model
upgrades for GUI work. Re-test cheaper models against the *new* tooling before assuming a big model is
needed - the task is now far easier than the one they were measured on.

### What the discarded runs already established

- **Coordinate-frame confusion is the #1 failure mode**, and it is a *safety* issue: a mis-framed
  click lands in another VI's window. Mitigated in code — `shotwin` now prints self-describing
  `left=/top=/right=/bottom=` plus the exact conversion.
- **Mechanical GUI control is not actually the bottleneck.** Palette navigation, drag-to-place and
  click-click wiring all worked; the cost came from bad documentation and a bad task. That is a
  meaningful finding in its own right, and it argues the standard should be "good playbook" at least
  as much as "better model".

## Interpretation guide

The number that matters is **tool calls to success**, because that is what wall-clock and token cost
both track. A model that succeeds in 15 calls is worth more than one that succeeds in 35 even if the
per-token price is higher. A model that *fails* at any price is the worst outcome, since the fallback
is a human doing it.

---

## FINAL RECOMMENDATION (2026-08-26)

**Use Opus for LabVIEW GUI control. Do not delegate it to cheaper models.**

| model | calls | steps | outcome | notes |
|---|---|---|---|---|
| Haiku 4.5 | 40 (cap) | 0 / 3 | **FAILURE** | never got past the palette |
| Sonnet | 40 (cap) | 2 / 3 | PARTIAL | placed both objects, ran out before wiring |
| **Opus 5** | **31** | 3 / 3 | **SUCCESS** | and did it *without* the z-order or `wire` fixes |
| Fable | 40 (cap) | 3 / 3 | SUCCESS* | *with* both fixes and extra hints, still needed the full cap |

The gap is not marginal. Opus succeeded under the **hardest** conditions of the four runs; Fable
needed every fix plus the whole budget; Sonnet and Haiku produced nothing usable at the same cost.
This is exactly the user's argument — *"attempting multiple times with lower model might be more
costly than applying higher model"* — and the data is unambiguous.

### The benchmark's real payoff was the bugs, not the ranking

Each capable run found a defect that had been silently taxing every other run. All are now fixed:

1. **Z-order defeats the rect check** (Opus). `PrintWindow` reports rects for fully occluded windows,
   so a "valid" coordinate can land on a different VI. Fix: `focus` -> re-`shotwin` -> click.
2. **`wire` could leave a pending rubber-band wire** (Opus). Silent; `probe` reads white.
3. **Aiming the wire source ON the border resolves to the positioning tool** (Fable) — start 2-3 px
   *outside* it. My documented example had aimed at the border and worked once by luck.
4. Palette **categories** need two clicks, **leaves** one; palette geometry does not track the click
   point; freshly placed objects stay selected and need a commit click before probing.

**Standing advice:** the durable win here was tooling and documentation, not model shopping — but
given a task that still needs GUI driving, spend the tokens on Opus.


---

# Pipeline benchmark — GUI-automation configurations compared (2026-08-26)

Design: `OPTIONS_beyond_gui.md` §(1). Task (same as `BENCHMARK_gui_control.md`): on a fresh empty VI,
**place a For Loop → place a numeric constant → wire it to `N`**. Model for all runs: Fable 5
(this session). LabVIEW 2026, window at (0,0) 1000×700, single display.

## Results at a glance

| # | configuration | tool calls | wall clock | outcome |
|---|---|---|---|---|
| A | Claude + composite tools (`probe`/`wire`) | 31 (Opus, prior run) | — | SUCCESS (baseline) |
| B | Claude + UI-TARS grounder (zoom) | **~16 (13 PS + 3 grounder)** | **5 m 20 s** | SUCCESS — but the grounder contributed little (see below) |
| C | Claude + UI-TARS 1× only | 3 grounding queries (accuracy probe only) | ~20 s | 2/3 targets hit; same semantic miss as B |
| D | Claude + Gemini executor | not run | — | blocked on `GEMINI_API_KEY` |
| E | VI Scripting, one Run | **~10 (incl. 1 misclick recovery; ~5 with known toolbar offsets)** | **2 m 21 s** | SUCCESS — and produced far MORE than the task (shift registers, conditional terminal, tunnels) |

**Prediction check** (`OPTIONS_beyond_gui.md` predicted E ≪ B < A; C ≈ A): E ≪ B < A held.
C ≈ A partially wrong — see finding 2: 1× was *fine* on 2 of 3 targets; the interesting failure was
semantic, not resolution.

## Config E detail — the ceiling

`BenchE_Example8_ForLoops.vi` (copy of lv-scripting `Example 8 - For Loops.vi`, see REFERENCES.md
[R6]) opened and Run once: complete For Loop generated in a new VI — constant `3` wired to `N`,
shift registers, auto-indexed tunnels, conditional terminal. Timeline 18:20:26 open → 18:22:38
result on screen, including one toolbar misclick + crop-verify recovery. GUI cost of "run a script"
≈ 3 clicks (focus, Run, verify). **One scripted Run replaced the entire GUI task and threw in four
bonus operations.**

## Config B detail — grounder-assisted GUI (task 18:25:09 → 18:30:29)

Steps that worked and what they cost:
- **For Loop via Quick Drop**: works for structures, but placement is **two clicks — anchor then
  complete** (rectangle corners). The mid-way screenshot looks empty (pending rubber-band is
  invisible to `shotwin`) — do not misread that as failure. ~3 composite calls incl. one wasted
  palette right-click.
- **Numeric constant via Quick Drop + type value**: 1 composite call, worked first try.
- **Wire to `N`**: grounder was supposed to find both ends. It did not (below). `probe` found both
  (`N` box (358,257): borders y=250/251 & 264/265, interior `#FFFFCC`; constant right edge x=287).
  First `wire` failed (source 4 px out → destination click selected the loop; marching ants);
  re-aim 2 px closer → clean blue wire, run arrow solid.

**Grounder scorecard (zoom mode), 4 queries:**

| target | coarse | fine (3× zoom) | verdict |
|---|---|---|---|
| Run arrow (warm-up) | good | (392,97) — **dead-on** | HIT |
| constant `3` | (283,252) — **dead-on** | (167,216) — drifted AWAY | coarse HIT, zoom hurt |
| `N` terminal | (283,252) = the constant | nonsense | **MISS — wrong object** |
| `N` terminal, re-phrased | the constant again | nonsense | **MISS — wrong object** |

## Config C detail — 1× accuracy vs probe ground truth

| target | truth | 1× result | error |
|---|---|---|---|
| constant `3` | (281,253) | (285,252) | ~4 px HIT |
| `N` terminal | (358,257) | (284,252) | ~74 px MISS (the constant again) |
| Run arrow | (71,66) | (75,66) | ~4 px HIT |

## Findings

1. **E wins outright.** Scripting is not just cheaper; it over-delivers (a complete, runnable loop
   with tunnels and shift registers). All kernel-build work should go through lv-scripting, with GUI
   only for opening/running driver VIs.
2. **UI-TARS's real failure mode today was semantic, not resolution.** On a sparse canvas with two
   small blue objects (`N` box vs numeric constant), it grounded "the N terminal" to the constant in
   4/4 attempts across both modes and two phrasings. The zoom pass did not help — and for the
   constant the zoom *fine* stage actively degraded a dead-on coarse hit. This nuances the earlier
   calibration (where zoom rescued `N` on a denser canvas): zoom fixes *small-target* misses, but
   cannot fix *wrong-object* grounding.
3. **Practical division of labour confirmed**: UI-TARS is reliable for large, unambiguous chrome
   (Run arrow, menus, buttons — 1× is enough, ~2 s) and unreliable for semantically confusable
   diagram terminals — those belong to `probe`, which was 100 % (4/4 wire-relevant pixels).
4. **Composite tooling + batching is what beat config A**, not grounding: 31 calls (A) → ~16 (B)
   came from batching PS commands and the probe/wire idiom, while the grounder consumed 3 of those
   calls for one useful hit.
5. Quick Drop structure placement = two clicks (new; recorded in the skill).

## Recommendation

- Kernel build: **scripting only** (config E path) — resume `KernelBuilder_v1.vi` Edit #2.
- Grounder: keep for chrome-level targets at **1×** (drop the default zoom for those); never use it
  to find wire endpoints — `probe` is the terminal-finder.
- Config D: run the same protocol if/when the user supplies `GEMINI_API_KEY`.
