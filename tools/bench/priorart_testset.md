---
type: reference
status: current
date: 2026-09-15
tags: [test-set, prior-art, evaluation]
---

# Prior-art review test set — five failures that actually happened, with their answers

Built 2026-09-15 on the user's instruction (*"실제 테스트 돌려서 숫자 확인 필요"*). Every change to the index or
the document format is scored against THIS, so the question stops being "is this a nicer structure" and becomes
**"does the reviewer catch more, per dollar"**.

Each item is a real mistake made on 2026-09-15, and the answer was sitting in this project's own files at the time.

| # | the mistake | the answer that was already on disk |
|---|---|---|
| **T1** | Quoted `docs/camera-acquisition-facts.md` line 183 to justify moving the ASI serial read out first | **Line ~139 of the same file** is headed *"ANSWERED: the frame loop does NOT transact serial every iteration"* — the serial is conditional, so the ordering had no support |
| **T2** | Called "can we relocate a node to another diagram?" the central risk of the whole method | `docs/toolkit-capabilities.md` already has the heading *"RESOLVED the same day — the build route is clear, and 'move a node' was never needed"*, with the measured sequence that replaces it |
| **T3** | Planned to build `VI.Get Errors` (method 452) as the reader that would settle broken-VI questions | `docs/toolkit-capabilities.md:244` and `tools/bench/build_opgeterrors.log` record it **FAILED twice** (2026-09-09, 2026-09-14): the Invoke node comes up with only reference/error terminals |
| **T4** | Wrote a recipe rewiring the **two** consumers of wire 751 in `OpWireSource_v5` | `tools/bench/build_opwiresource_v5.log:35-39` records that the first v5 rewire failed for exactly this: there is a **third** consumer (node 482), and the op stayed broken until it was re-fed |
| **T5** | Derived a new diagram's Traverse index by hand — `count("Diagram") - 1`, then `list(uids(...)).index(...)` | `tools/gscript.py` already has **`fidx`** (via the ordered `report_all`), **`new_since`** — whose docstring says *"Use this, NOT position matching, to identify what a mutating Op just created"* — and **`loop_diagram`** |

## Scoring

A hit requires the reviewer to **name the file** (line number when the item has one) and state the conclusion that
contradicts the plan. Naming the topic without the citation is a miss: the citation is what releases or blocks work.

Record for every run: **hits / 5, total cost in USD, input+output tokens, wall clock, and the index variant used.**
Results accumulate in `tools/bench/priorart_scores.md`.

## Why these five and not others

They share the property that makes this review worth paying for: in each case the project had **already done the
work**, the answer was written down, and it was missed anyway. T1 and T4 are the sharpest — the contradicting text
was inside a file I had open at the time.
