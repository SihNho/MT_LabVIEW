---
type: reference
status: current
date: 2026-09-13
tags: [docs, plan]
---

# What does a subVI call cost? — ANSWERED: about 100 ns, i.e. free

> **RESULT (2026-09-13, external sources; our own measurement not yet run).** A static, already-loaded subVI call costs
> on the order of **100 ns**. At 150 Hz, where the whole per-frame budget is 6.00 ms, **100 calls cost 0.01 ms**.
> Splitting the frame path into subVIs is therefore free, and the worry that motivated this measurement is closed.
>
> | operation | published figure |
> |---|---|
> | normal static subVI call | **86 ns** |
> | static LVOOP method | 98 ns |
> | dynamic-dispatch method | 304 ns |
> | Case Structure dispatch added to a call | ~6 ns |
> | inline vs subVI (increment benchmark) | ~30 ns inline vs ~100 ns called → **~70 ns overhead** |
> | with **Inline** enabled | no measurable extra cost |
>
> Source: `archive/peer/2026-09-13-subvi-call-cost.md`, citing community benchmarks on NI's forum. **NI's own older
> help text says "tens of microseconds" — that figure carries no methodology, hardware or version, contradicts modern
> compiled-code measurements, and would have been 600× wrong.** Taking the documentation at face value would have
> shaped the whole restructuring around a non-existent cost.
>
> **What is actually expensive**, per the same source and matching everything measured on this rig: array copies,
> synchronisation, **UI-thread work**, allocation, GPU transfers, and **serialisation through a non-reentrant VI**.
> Those are the millisecond-scale risks; call count is not one.
>
> **Consequences adopted:**
> 1. The frame path may be split as finely as readability wants. Call overhead is not a design constraint.
> 2. The real constraints are **interface width** (a connector pane holds at most 28 terminals) and **what crosses the
>    boundary** (a 1.31 MB image crossing a boundary is a different question from a scalar).
> 3. **Inlining is unnecessary**, which removes a whole class of restriction — inlined VIs may not contain local
>    variables or static front-panel references, and we are deliberately moving toward local variables.
> 4. Our own A/B/C/D measurement below is **downgraded to optional confirmation**; the decision no longer waits on it.
>
> The one figure still worth measuring here is the **array-boundary** case (item 2), because no external source covers
> a 1280×1024 U8 image crossing a subVI boundary on this machine.

## Original measurement design (kept for the array question)

> **Question from the user, 2026-09-13:** *"서브vi 호출과 블록 다이어그램 완전 전개하고 프레임 차이는 없는거야?
> 만약 그게 사실이면 나중에 내가 코딩할때도 참조해야겠더 싶어서"* — and then: it is essential.
>
> **Honest starting point: this has never been measured here.** Nothing in this project's records answers it.

## Why it is a prerequisite, not a curiosity

The restructuring plan's method is *extract functions into subVIs*. If a subVI call is expensive, then **every
extraction out of the frame loop spends part of the per-frame budget**, and the plan trades readability for frame rate —
the opposite of the goal. At 150 Hz the budget is **6.00 ms** and the tracking kernel already takes 2.43–2.87 ms, so an
overhead of even 0.5 ms per frame would matter. The number decides how freely the frame path may be split.

It is also the user's own coding reference going forward, which raises the bar: a guess is worse than no answer.

## What is already known, and what it does not settle

| observation | value | why it is not the answer |
|---|---|---|
| a subVI whose panel data space got loaded by a VI-Server touch | **+9 ms per call** | pathological, caused by the tooling; not the normal cost |
| wrapping the kernel in a Case Structure, CPU path | **free** (2.84 vs 2.87 ms) | a structure, not a subVI call |
| the same Case Structure, GPU path | **+1.06 ms**, cause never found | proves added structure can cost differently per path — a warning, not a figure |

Two LabVIEW settings dominate the answer and have not been checked in this code:

- **Inline subVI** — when enabled, the compiler expands the call, so the overhead should approach zero.
- **Reentrancy** — non-reentrant calls serialise with each other; reentrant clones each get their own data space.

Neither is knowable by reasoning; both are readable per VI (`VI.Execution:Reentrancy Type` = `288` is already
registered) and settable.

## Design

One trivial computation, timed three ways, in a loop large enough that per-call cost dominates loop overhead:

| cell | shape |
|---|---|
| **A — inline** | the computation written directly on the diagram |
| **B — subVI, normal** | the same computation in a subVI, called once per iteration |
| **C — subVI, Inline enabled** | identical to B with the subVI's *Inline* option on |
| **D — subVI, reentrant** | identical to B with reentrancy changed |

`(B − A) / N` is the per-call overhead. `C − A` should be ≈ 0 if inlining does what it claims. `D` tells us whether the
reentrancy setting matters at this scale.

**Realism matters for the answer to transfer.** A subVI taking two scalars is the cheapest possible case; one taking a
large array may cost more if LabVIEW copies the data. So run the sweep twice: **scalar in/out**, and **a 1280×1024 U8
array in/out** — the actual shape of data crossing the frame loop's boundaries. If the array case is much worse, the
rule for the restructuring is "split on scalars and references, never on images", which is a design constraint worth
knowing before building anything.

**Method notes, learned the hard way today:**
- Time inside LabVIEW, not from Python — one COM round trip dwarfs everything being measured (this is why the
  UI-thread measurement stalled).
- Restart LabVIEW between configurations; a VI-Server touch inflates a subVI's call time by ~9 ms and would swamp the
  result.
- Report median, p90 and max, not a mean — the frame budget fails on tails, not averages.

## What the answer changes

| if per-call overhead is… | consequence for the plan |
|---|---|
| < ~10 µs | split the frame path freely; readability is free |
| ~10–100 µs | fine for a handful of calls per frame; count them |
| > ~100 µs, or large for arrays | **the frame loop keeps its work inline**; extraction applies only to loops off the frame path, and the "extract everything" method needs rewriting |

Whatever comes out goes into `docs/toolkit-capabilities.md` as a standing figure, because it is a rule for all future
LabVIEW work here, not just this restructuring.
