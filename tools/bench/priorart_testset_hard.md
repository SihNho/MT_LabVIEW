---
type: reference
status: current
date: 2026-09-15
tags: [test-set, prior-art, evaluation]
---

# Prior-art test set II — the HARD set, split by whether the answer is in the index

The first test set (`priorart_testset.md`) had no discriminating power: all three arms scored 5/5, because its five
items were recent, prominently recorded, and mostly from the same day. This set is built to separate the arms, and
its split answers the question that actually matters for the document-reformat decision.

| group | where the answer lives | does the index carry it? |
|---|---|---|
| **A** | a marked line in an active document, already extracted into a shard | **yes, with substance** |
| **B** | an **old, unannotated** peer exchange — the index has only its slug | **no** |

**If the index earns its keep, the indexed arm beats the control on GROUP A and ties on GROUP B.** And because
reformatting a document is exactly the act of moving an item from B to A, that comparison prices the reformat work
directly instead of assuming it.

## Group A — the answer is in the index

| # | the plan's claim (wrong) | the answer, and where |
|---|---|---|
| **A1** | shift registers cannot be created by script, so the feedback path needs another mechanism | They **are** creatable — `Loop.Add Shift Register` **6361000**, VERIFIED 2026-09-14. `docs/NAMES.md:675`, INDEX row 37 |
| **A2** | the four-fold kernel is called from several places, so each call site must be patched | **Exactly ONE call site**, uid 5058. `docs/MAIN_VI_MAP.md:168` |
| **A3** | the display path is cheap, so it can stay in the frame loop | Measured **2.7 ms CPU + ≈6.5 ms paint while visible** — above the whole 6 ms budget. `docs/g9-core-budget.md:28`, INDEX rows 22/25 |
| **A4** | the GPU path is slow because the CUDA kernels are slow, so optimise the kernels | Measured: **every CUDA call uniformly 3.5–4.5× slower — host-side latency**, not kernel cost. `archive/peer/2026-09-14-g9…` (in the kernel-tracking shard) |

## Group B — the answer is in an old, unannotated exchange

| # | the plan's claim (wrong) | the answer, and where |
|---|---|---|
| **B1** | a parallel For loop's completion order scrambles its auto-indexed outputs, so an explicit bead-index array must be carried | **False.** An auto-indexed output tunnel on a parallel For loop maps iteration *k* to index *k* regardless of completion order. `archive/peer/2026-08-30-2026-08-30-parallel-forloop-output-order.md` |
| **B2** | the xyz array layout is settled, so the Decimate route can be wired now | It was left **UNDETERMINED** — *"Do not wire the Decimate plan yet"*, no decisive producer-side evidence. `archive/peer/2026-08-30-2026-08-30-xyz-array-layout-refute.md` |
| **B3** | save fixture frames as an image container (PNG/TIFF) for bit-exact replay | For bit-exact fixtures the route is **`IMAQ ImageToArray` → binary stream → `ArrayToImage`**, bypassing container encoding. `archive/peer/2026-08-31-2026-08-31-imaq-image-save-exact-roundtrip.md` |
| **B4** | LabVIEW's ActiveX interface cannot write 1-D arrays of clusters, so that route is out | **It can.** The silent failure was **pywin32 dimension mangling** — a 2-D SAFEARRAY where LabVIEW wants 1-D. `archive/peer/2026-08-30-2026-08-30-activex-cluster-array-setcontrolvalue.md` |

## Scoring

A hit requires naming the FILE (line where the item has one) and stating the conclusion that contradicts the plan.
Record per run: **hits in A / 4, hits in B / 4, cost, tokens, turns**, into `priorart_scores.md`.

## Design note found while building this

Of the 54 peer exchanges older than 2026-09-08, 25 are "annotated" — but their verdicts are single words
(`adopted`, `rejected`) that say nothing about **what** was adopted. They are in the index and carry no
information. So annotation PRESENCE is not the variable; annotation **substance** is. Group A deliberately uses
entries with real content.
