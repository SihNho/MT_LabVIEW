---
type: reference
status: current
date: 2026-09-15
tags: [docs, main-vi, hierarchy]
---

# The main VI's diagram hierarchy — what is nested inside what

Asked for by name by the user on 2026-09-15 (*"문서화가 충분히 되지 않은 것 같은데, 다이어그램 계층 구조 확실히
준비하도록"*), after my answer to *"why is the PI motor / rotor communication excluded?"* turned out to rest on
nothing: the project knew the three While-loop **bodies** and had never established what was nested inside them.

## What the VI is made of (measured 2026-09-15, `tools/bench/build_diagram_hierarchy.log` run 3)

| structure class | count |
|---|---|
| WhileLoop | 3 |
| ForLoop | 17 |
| CaseStructure | 37 |
| **FlatSequence** | **21** |
| Sequence (stacked) | 4 |
| EventStructure | 2 |
| **total structures** | **84**, owning 169 diagrams + 1 top level = **170** |

**The 21 Flat Sequence structures had never been catalogued.** `tools/bench/diagram_tree_main.json`'s `structures`
map lists only the other five classes, so every count derived from it — including "the VI has 63 structures" — was
short by a quarter. They were found by asking the machine which class name matches the `FlatSequenceFrame` owner
string rather than by assuming one.

## The three loops (confirmed, and this part is solid)

| loop | body diagram | uid |
|---|---|---|
| motor | 20 | `WhileLoop#25380` |
| **frame** | **43** | **`WhileLoop#637`** |
| display / UI | 99 | `WhileLoop#15173` |

## Instrument work nested INSIDE the frame loop — the answer to the user's question

Two call sites are inside loop 43, and each is confirmed by **two independent measurements**: the position-matched
hierarchy, and the wire-graph slice computed separately on 2026-09-14/15.

| call site | owning structure | that structure lives on | corroboration |
|---|---|---|---|
| **diagram 73 — ASI stage move** (`ASI TG-1000.lvlib:Move Axis Relative.vi`) | `CaseStructure#10407` | **diagram 43** | #10407 is the case that exchanges `Out position` / `Outgoing Handle` with the ASI focus subVI #48 (`tools/bench/slice_cutset_acq_track.py`) |
| **diagram 74 — `Magnet2Force v3_for M270.vi`** | `ForLoop#1359` | **diagram 43** | #1359 is in the tracking kernel's measured FORWARD SLICE (`docs/frame-loop-wire-graph.md`) |

So the frame loop does not merely *call* the ASI focus wrapper — it contains a **stage move** in one of its case
frames, and the magnet-to-force conversion in one of its For loops. Whether `Magnet2Force` performs serial I/O or is
pure computation is NOT established here and must not be assumed.

**The PI motor commands look like startup, not per-frame.** `MOV.vi` on diagram 3 is owned by `CaseStructure#3826`,
which lives on diagram 2; `VEL.vi`/`POS?` on diagram 5 by `Sequence#3593` on diagram 1 — chains heading toward the
top level rather than into any loop. That is consistent with homing and velocity setup, but the chains were not
walked all the way, so **it is a strong indication, not a conclusion**.

## What is NOT resolved, and exactly why

129 of 170 diagrams matched; **41 did not**. The method matches each diagram to the nearest structure of its own
owner class and accepts the match only if the runner-up is ≥3× farther. In this VI the structures sit tens of
pixels apart (`nearest 21, runner-up 43`), so the margin fails. The 21× margin that justifies
`gscript.loop_diagram` was measured on three loops **700 px apart** in 2026-08-28 and does not generalise to a
diagram that Clean Up Diagram compacted.

A second, sharper symptom: several FlatSequence matches that DID pass the margin produced a structure uid that
appears on **no diagram at all** (`lives on []`). Either those matches are wrong, or the node-uid lists in
`diagram_tree_main.json` omit FlatSequence nodes. **Treat every FlatSequence-owned link in the JSON as unverified
until this is settled.**

## A2 — OWNER SEMANTICS PER STRUCTURE CLASS, MEASURED 2026-09-16

`tools/bench/diag_owner_semantics.log` (`BGRUN END rc=0 after 73 s`, **54 gates pass / 0 fail**),
`OpOwnerChain_v1.vi` unchanged, main VI md5 `2a78e17c449cacdaf5da389818526859` before and after. Raw rows:
`tools/bench/owner_semantics.json`. **Facts only; what they mean for A3 is in `STATUS.md` OPEN.**

The owner *class* of all 170 diagrams was already measured (run 3, above). What had never been read from the
machine is the owner **UID** — `report()` returns the owner's class and not its uid, so every diagram→structure
uid this project held came from **position matching**. That is what this run replaces.

| class | diagram uid → owner (read) | structure → its parent diagram | position-matched uid |
|---|---|---|---|
| WhileLoop | 639 → `WhileLoop#637` · 15266 → `WhileLoop#15173` · 25392 → `WhileLoop#25380` | `Diagram#686` · `Diagram#15041` · `Diagram#686` | agrees 3/3 |
| ForLoop | 2603 → `ForLoop#2457` · 7911 → `ForLoop#1359` · 13404 → `ForLoop#13390` | `Diagram#639` · `Diagram#639` · `Diagram#13236` | agrees 3/3 |
| CaseStructure | 206 → `CaseStructure#57` · 253 → `CaseStructure#57` · 1493 → `CaseStructure#195` | `Diagram#639` · `Diagram#639` · `Diagram#759` | agrees 3/3 |
| **FlatSequence** | **113 → `FlatSequenceFrame`, owner uid `0`** | **unreachable** | not in the resolved list |
| Sequence | 3667 → `Sequence#3593` · 5038 → `Sequence#3593` · 15683 → `Sequence#15649` | `Diagram#3628` · `Diagram#3628` · `Diagram#15622` | agrees 3/3 |
| EventStructure | 10213 → `EventStructure#10153` · 15593 → `EventStructure#15544` | `Diagram#639` · `Diagram#15266` | agrees 2/2 |

**Measured, stated exactly:**

1. **Five of the six classes behave like `CaseStructure`.** Diagram → owner returns the structure's class *and a
   non-zero uid* with no error, and the structure → parent hop returns a `Diagram` with a non-zero uid. That hop
   had never returned for any class before this run.
2. **`FlatSequence` is the single exception, and it is now measured twice.** A diagram inside a flat sequence
   reports owner class `FlatSequenceFrame` with **owner uid 0**, `error 1055`, and an **empty cast-class echo** —
   the same shape as `Diagram#686` in `diag_ownerchain_hop.log:7`, on a different diagram (113). The chain
   terminates there.
3. 🔴 **CORRECTED 2026-09-16 (cycle 13, prior-art `A3-i`): `errCO` is NOT "the cast node's own error".**
   `tools/recipes/build_opwiresource_v4.py:108-115` builds it as the `error out` of a `Generic.ClassName`
   **Property Node hanging off the cast's OUTPUT** — downstream of the cast — and the cast itself
   (`To More Specific Class`, a Function) has **no error indicator anywhere in the op**. The same mislabel is in
   `tools/bench/diag_owner_semantics.py:114`, which is a historical artefact and is not edited; read this line
   instead. Consequence: the A2 row below shows that a **downstream** node carries the 1055, and it does **not**
   establish that the cast generated it. Original sentence, kept for the record:
   ~~**`errCO` — the cast node's own error — was read for the first time**~~ (it is labelled `"error out 10"` in
   `tools/bench/opwiresource_v5_labels.json` and `read_owner` never read it; the gap was named by codex and
   confirmed in our code). For the FlatSequence row it reads **`error 1055: Property Node in OpOwnerChain_v1.vi`**,
   i.e. the same string as the merged `errs`, while the op's own `error out` stayed empty. Whether that is the cast
   generating the error or propagating one is **not** settled by this read.
4. **Position matching agreed with the machine everywhere it had an answer: 14/14, zero disagreements.** So the
   geometric links in `diagram_hierarchy.json` are not silently wrong for these classes — but the 41 unresolved
   diagrams and the FlatSequence links are exactly where position matching had no answer to check.
5. Tripwires held: `report_all(MAIN,'Diagram')` = 170 rows with the recorded owner-class histogram
   (CaseStructure 76 · FlatSequenceFrame 57 · ForLoop 17 · Sequence 11 · EventStructure 5 · WhileLoop 3 · `''` 1),
   and the class census re-read 3 / 17 / 37 / 21 / 4 / 2.

## A3 — THE 112 CLEAN DIAGRAMS ARE NOW READ FROM THE MACHINE, 2026-09-16

`tools/bench/diag_hierarchy_a3.log` (`BGRUN END rc=1 after 304 s`, **12 gates pass / 1 fail** — the one failure is
the FlatSequence arm below), rows in `tools/bench/diagram_tree_a3.json`, `OpOwnerChain_v1.vi` unchanged, main VI
md5 `2a78e17c449cacdaf5da389818526859` before and after. **Facts only.**

**112 diagrams → 63 distinct structures → parent diagram, every hop read from the machine.** Gates: every clean
diagram resolved (non-zero structure uid, no error, owner class as recorded); every structure resolved to a
`Diagram` with a non-zero uid; every structure uid was in `diagram_tree_main.json`'s `structures[<class>]`.

| cross-check | result |
|---|---|
| machine vs the **position-matched** `owner_uid` (`diagram_hierarchy.json`) | **100 agree, 0 DISAGREE**, 12 had no position answer |
| of the **41** diagrams position matching could not resolve | **12 are now resolved** (the other 29 are the FlatSequence-owned ones and the top-level diagram) |
| machine's structure → parent vs the `diagram_tree_main.json` `uids` lookup | **112 agree, 0 disagree, 0 unanswered** |

So **position matching was not silently wrong anywhere it had an answer** — 100/100 on top of A2's 14/14 — and A3
adds the 12 it never had. What remains unresolved is exactly the **57 `FlatSequenceFrame`-owned diagrams**.

### 🟢 AND THE ROUTE EXISTS AFTER ALL — `FlatSequence.Diagrams[]` **3578BC00**, measured the same hour

The table below says the route is closed **with the ops we own**, and that much stands. But the mandatory peer
review of that failed prediction (`archive/peer/2026-09-16-flatseq-frame-unreachable.md`, codex, ANSWERED 125 s)
refuted the *general* claim, and the refutation was then **confirmed on the machine**
(`tools/bench/diag_flatseq_diagrams_attach.log`, 5/5, 33 s): `FlatSequence` (class id 16459) has its own
accessors — **`Diagrams[]` `3578BC00` attaches with data terminal `Diagrams[]`**, and `Frames[]` `3578BC07`
attaches too. The 1077 below means *that id belongs to `MultiFrameStructure`*, not *unreachable*.
**So the 57 frames are reachable; what is missing is an op that walks `Diagrams[]`, which is a new build and a
judgement call.** Do not quote the table below as "FlatSequence frames cannot be read".

### FlatSequence: the top-down route is CLOSED with the ops we own — four independent measurements

| probe | result |
|---|---|
| traverse class `Tunnel` | **works, 468 objects** — owner histogram `CaseStructure 173 · ForLoop 130 · WhileLoop 91 · Sequence 58 · EventStructure 16`, i.e. **ZERO owned by a FlatSequence**, so `OpTunnelRead_v0` has nothing to seed |
| traverse class `Structure` | **63** — and 84 structures − 21 FlatSequence = **63** |
| traverse class `MultiFrameStructure` | **43** = 37 Case + 4 stacked Sequence + 2 Event. **FlatSequence is not a MultiFrameStructure** |
| `SequenceTunnel` / `FlatSequenceTunnel` | both **error 1092** |
| `build_property('VI Server:FlatSequence', Frames[] 6363801)` | **error 1077, creator refused** — while the same id on `VI Server:MultiFrameStructure` attaches with data terminal `Frames[]` (5 recorded runs, `build_opcaseframes_v0.log`) |

### The 1055 is generated DOWNSTREAM of the cast — the `Owner` read itself succeeds

Every error indicator of `OpOwnerChain_v1` read separately, on `FlatSequenceFrame` diagram 113 and on clean
diagram 639 as control (the control came back **all-empty**, 8/8):

| indicator | what it is | diagram 113 |
|---|---|---|
| `errO` `"error out 4"` | the **`Generic.Owner`** property node — UPSTREAM of the cast | **empty** |
| `errL`, `errT`, `errU`, `errS`, `errWU` | the rest of the upstream chain | **empty** |
| `errG` `"error out 7"` | the **UID** property node, downstream of the cast | **`error 1055`** |
| `errCO` `"error out 10"` | the **`Generic.ClassName`** property node hanging off the cast's OUTPUT | **`error 1055`** |

⚠️ This does **not** say "the cast generated it": the cast (`To More Specific Class`) is a Function and has **no
error indicator in the op at all**. What is measured is that the `Owner` reference comes back clean and only the
two nodes reading the **cast's output** fail — the shape codex's mechanism predicts
(`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md:74`: the cast yields `Not A Refnum` and the
downstream node dereferences it). The `ClassName` read taken from the **uncast** owner still returns
`'FlatSequenceFrame'`, which is why the class is known and the uid is not.

## The link that would finish this — ⛔ SUPERSEDED 2026-09-16

> **SUPERSEDED — do not act on this section.** The reader it asks for was **built and run** the same day as
> `OpOwnerChain_v1` (20/20 gates, functional on the main VI), and owner semantics were then validated 54/54; both
> are recorded in the **A2 / A3 sections above in this same file** and in `docs/pre-rig-master-plan.md` rows A1–A3.
> Kept verbatim below as the original statement of the problem. Resolves
> `archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 2 (lines 93–95): this section was the stale side.

Every chain stops at the same place: a diagram's owning structure is known, but **which diagram that structure
itself lives on** is not. Position matching cannot supply it here. The reader that can:

**`OpOwnerChain_v0`** — a UID in, its owner's UID and class out. The semantics are already MEASURED
(`docs/NAMES.md`: a node's `Generic.Owner` is its frame Diagram, and that Diagram's `Owner` is the structure), and
the donor exists: `OpWireSource_v5` already performs `Generic.Owner` → `ClassName` + cast(GObject) → `UID`, seeded
from a Wire; removing that Wire cast is the whole change. With it, every chain walks to its While loop in one pass
and this document's open half closes.

## Artefacts

`tools/bench/build_diagram_hierarchy.py` (read-only; the main VI is opened by reference and never modified — md5
`2a78e17c449cacdaf5da389818526859` before and after), its output `tools/bench/diagram_hierarchy.json`, and
`tools/bench/which_loop_owns_motor.py` which walks the call sites upward and reports where each chain stops.
