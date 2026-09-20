---
type: reference
status: current
date: 2026-09-15
tags: [docs, stage2, reseed]
---

# Stage 2 — step E: the reseed Case (plan item 3) — overnight cycle 6, 2026-09-15 04:2x

Parents: [stage2-plan.md](stage2-plan.md) item 3 ("Kernel state faithfully": cases #5540 and #2222 reproduced
case-for-case, read from the graph before building); rows 40–41 (replay cores bit-identical BEFORE the first lost
bead; after it they diverge from the reference exactly as the plain-feedback driver did, because the original's
Case #5540 replaces the fed-back state when a bead is lost).

## What is known, and what must be measured first (rule 1a: never an "equivalent")

- Reference semantics as the driver encodes them (`run_fixture_compare.py --reseed=main`): if the previous
  frame's kernel `x,y,z array out` contains −1.0, the next frame's inputs are `x,y,(blankz) array` from the loader
  (calibration positions), all-TRUE good flags, and the kernel's own `pos in cal image out`. That driver reproduced
  the `.tra` with worst deviation 0.00000 over 10,043 frames, so it IS the original's behaviour on this recording.
- Measured on the reference jsonl: 13 frames carry −1.0 in x,y,z; the same 13 carry −1 in `pos`; 26 frames carry
  a FALSE good flag (a strict superset — the flag alone is NOT the trigger).
- The original's selector is a compound: upstream of #5540 sit `Less?` #10950, `Or` #10247, `And` #9647 and an
  implicit `min value`.Value property #17289 (frame-loop wire graph). **Phase E0 = a read-only census of that chain**
  (`tools/bench/census_case5540.py`): which quantity `Less?` compares against what, what `Or` adds (the periodic
  auto-reset that never fired on this recording), and which Case frame carries which passthrough. The new Case is
  built from THAT reading, not from the driver's paraphrase.

## Corrections from the plan review (`archive/peer/2026-09-15-stage2-step-e-reseed-case-plan.md`)

- **`min value` is an INDICATOR, not a control** (panel object 36): fed by `Array Max & Min` #10969 of the kernel's
  `pos in cal image out`, and read back by the implicit property node #17289 that feeds `Less?` #10950. It is
  computed per frame and must never be baked; E0 must measure its frame age (does `Less?` see this frame's minimum
  through the property read, or the previous frame's?). Replacing the property read with a direct dataflow value
  could remove a lag — that would be a computation change.
- **The periodic auto-reset term is bigger** than one `Or`: `# of Auto-Reset`.Value #9879, `Quotient & Remainder`
  #10068, `Equal?` #10019, Not/And nodes. It never fired on this recording, so the 10,043-frame run cannot validate
  it — it gets a separate small-interval test.
- **`Create Less?.vi` does not exist** in the library (Equal / Or Array / And Array / Index Array / Case (Boolean) /
  Exit Structure do). The comparison primitive comes from `copy_by_index` of a donor, or `Create Equal.vi` if the
  census shows that is what the original computes.
- Placement equivalence (reseed after the kernel, before the registers) holds only with the result queues branching
  from the RAW outputs and `pos` fed back raw — both already true in `build_track_v6_queue.py`.

## E0 measured (04:3x, `tools/bench/census_case5540.log`, main VI by reference only)

- **#5540's inputs are the kernel's RAW outputs** — t5 ← `x,y,z array out` (wire 1681), t3 ← `Bead is good?
  array out` (6041) — plus two outside values t1 (5979) and t4 (5746); its outputs 5975 (`x,y,z array`) and 5637
  (`Bead is good? array in`) feed the RIGHT shift registers. So the original's Case sits **after the kernel, before
  the registers** — exactly `Reseed.vi`'s placement; the reviewer's condition (results branch from the raw outputs)
  matches the original's own topology.
- Selector 5709 ← `Or` #10247: `x` ← **another Case #10445** (output 10573), `y` ← 10312 (from outside diagram 43).
- Lost-bead term: `Less?` #10950 `x` ← `min value`.Value (property read #17289 of the indicator written by
  `Array Max & Min` #10969 whose `array` ← the kernel's `pos in cal image out`, wire 121); `y` ← 10850 (outside);
  `Less?` → `And` #9647 `x`; `And.y` ← 9806 (outside); `And` → 9921 (sink to find).
- **MEASURED 2026-09-15 06:00 (`OpConstValueN_v1.vi`, `tools/bench/opconstvaluen_scan.log`, read-only, main VI
  byte-identical after): wire 10850 (`Less?.y`) ← DigitalNumericConstant uid 10739 (scan index 70), value `0`,
  representation I32 (TD 0x03), displayed text `0`.** So the lost-bead term is **`min(pos in cal image out) < 0`** —
  i.e. "any bead whose position came back negative", which is exactly the `pos == -1` lost marker the fixture shows.
  **ALL FOUR FEEDERS RESOLVED (12:06-12:09; `OpWireSource_v1.vi` UID->source walk, `build_opwiresource_v1.log`
  29/29 PASS, confirmed independently by `panel_wiring` in `census_selector_sources.log`; main VI byte-identical):**

  | wire | role in #5540's selector | source | value / meaning |
  |---|---|---|---|
  | 10850 | `Less?.y` | `DigitalNumericConstant` uid 10739 | **I32 `0`** -> lost term = `min(pos in cal image out) < 0` |
  | 9806 | `And.y` | front-panel **control `Auto-Reset`** (uid 17472) | gates the lost-bead reseed - it fires only while the user has Auto-Reset on |
  | 10312 | `Or.y` | front-panel **control `Reset Tracking`** (uid 5605) | manual reseed, OR'd on top of the computed condition |
  | 10142 | `Equal?.y` | front-panel **control `Limit of Program`** (uid 9654) | **the cap on how many auto-resets one run may take** (user, 2026-09-15). `Equal?` compares it with `# of Auto-Reset` — equality, not ">=" — and when it is hit the run **stops and saves what it has**. Operational reason: an overnight MT run loses beads (they come unstuck and fly off); each loss auto-resets, and past this many the run is no longer producing data worth continuing. (The earlier note here cited GLOSSARY for "the run ends when the counter reaches this limit"; GLOSSARY actually said "safety bounds on focus travel", which was simply wrong — both are corrected.) |

  Only ONE feeder is a constant; the other three are **runtime controls**. Rule 1a therefore fixes the interface:
  `Reseed.vi` must receive `Auto-Reset`, `Reset Tracking` and `Limit of Program` as INPUTS carrying those controls'
  values, never as constants baked into the new code.
  *(Retrospect: `docs/main-vi-panel-map.md` already listed these three wire uids against those controls - consult the
  panel map before building a new reader.)*
🔴 **CORRECTED 2026-09-16 (cycle 13; found by the prior-art review, `A3-iii`). The two bolded claims in the next
bullet are REFUTED BY MEASUREMENT and are kept only so the correction is legible.** `tools/bench/owner_semantics.json`
(`diag_owner_semantics.log`, 54/54) reads **`LoopTunnel #10177 → owner ForLoop#1359`** and **`ForLoop#1359 →
Diagram#639`**, and `tools/bench/main_vi_tunnels.json` records #10177 with `out_is_source False`, i.e. an **INPUT**
tunnel. So (1) #10177 does **not** "LEAVE the frame loop" — the remainder flows **into** a For loop; (2) that For
loop sits on **diagram 639**, the frame loop's own diagram, so "the periodic term is assembled outside diagram 43"
does not follow; and (3) the link is no longer missing — `OpOwnerChain_v1` was built and works. See `STATUS.md`
OPEN 1.

- Periodic term: `# of Auto-Reset`.Value #9879 → `Equal?` #10019 `x`; `Equal?.y` ← 10142; `Quotient & Remainder`
  #10068 remainder 10187 → ~~**`LoopTunnel` #10177 — it LEAVES the frame loop**~~ (measured 2026-09-16,
  `tools/bench/diag_reset_arm.log`); `x` ← 3268, `y` ← **`LoopTunnel` #10114, i.e. the period ENTERS from outside**.
  Second hop: `census_case5540_hop2.py`. ~~**So the periodic term is assembled outside diagram 43**~~, and whether
  `Auto-Reset` gates it cannot be answered from inside the loop — that needs the structure→home-diagram link
  (`OpOwnerChain_v0`). The `And` #9647 that IS inside takes the `Auto-Reset` control (wire 9806) and
  `Comparison` #10950 (wire 9868), and its output 9921 selects Case #10445 **and**, negated, suppresses the
  autofocus enable (`camera-acquisition-facts.md`, the A6 block) — answering the other `sink to find` at :55.
- **Timing hazard confirmed structurally:** the indicator `min value` is written by a terminal and read by a
  property node in the same iteration with no wire between them — a race in the original; the fixture driver's
  rule ("previous frame's raw output contains −1 → reseed") reproduced the recording exactly, so on THIS recording
  the effective reading equals "min of this iteration's `pos out` < y". The rebuild uses that direct dataflow
  (deterministic) and records the original's racy read as an OPEN item for the user (rule 1a: the step cannot be
  shown structurally identical; it is shown numerically identical on the fixture).
  **DECIDED 2026-09-15 — the user chose the current frame:** *"min value는 이번 장면 기준이 맞는 듯. 이대로 진행."*
  So the rebuild wires `pos in cal image out`'s minimum straight into the lost-bead test, always reading THIS
  iteration's value. The rule-1a deviation is accepted on the user's word, on the evidence that it is bit-identical
  to the reference across all 10,043 fixture frames.

## E0 hop 2 (04:4x, `census_case5540_hop2.log`) and the blocker it exposed

`And(Less?, y)` feeds both the inner Case #10445's selector and a `Not` #10382; #10445 outputs a Boolean into
`Or.x` (10573) and passes a `Value` through (10763 → 11389); `Q&R(tunnel 2213 ← outer 2187, '# FD points')` sends
its remainder into For loop #1359; `Equal?` → `Compound Arithmetic` #11639; #5540's t1/t4 arrive through tunnels
5569/5752 (outer 5812/2731). **Four feeders come from outside diagram 43** — `Less?.y` 10850, `Or.y` 10312, `And.y` 9806,
`Equal?.y` 10142 — and at the time none of them could be read. RESOLVED above: one constant (I32 0) and three
front-panel controls. The reader that settled it began as a `Constant.Value` reader**: `tools/recipes/build_opconstvalue_v1.py` — the seed comes from NI's
`Navigating Nodes and Wires.vi` (diagram 3: TMSC → Property `Value`, uid 284; `census_constant_seed.log`), both
nodes copied by reference (`copy_by_index`) into an `OpReport_v3` donor. `Navigating Structures.vi` diagram 1 holds
a `CaseStructure.Selector` property node — the seed for the Case work that follows.

## The uid 3628 scare, and why the threshold value stands (2026-09-15 12:4x-13:0x)

While building a wire-source reader, one run reported that wire 10850's source was a `DigitalNumericConstant` with
uid **3628**, contradicting the constant scan's **10739** (value I32 0). It was an instrumentation artifact, found by
the reviewer's own prescribed test: the UID branch of that op had been hung on `OpReport_v3`'s identity property node
(which describes the object the op TRAVERSED, whose owner is a Diagram - uid 3628, invariant), not on the `Owner`
node fed by the terminal being inspected. The class branch was always correct.

What is therefore MEASURED and stands:

- wire 10850 has exactly ONE source terminal and one sink (`Terminal.Is Source?`, each with a reciprocal
  `Connected Wire` pointing back at 10850) - the net is sound, not a multi-source broken wire;
- the source's CLASS is `DigitalNumericConstant` (wire side) and the constant that reports feeding wire 10850 is
  uid **10739** with value **I32 0** (constant side, per-read identity gated, 180/180 rows, no duplicate claims);
- so the lost-bead comparison is `min(pos in cal image out) < 0`, as already written above.

**CLOSED 13:0x by `OpWireSource_v5` (12/12 PASS, `tools/bench/build_opwiresource_v5.log`)**: with the branch rewired
by dataflow and reference provenance asserted, the wire side now reports wire 10850 Terms[0] = SOURCE, owner
`DigitalNumericConstant` **uid 10739** (cast-output class agrees), and Terms[1] = sink, owner `Comparison`
**uid 10950** - which is exactly `Less?` #10950 from the E0 census. Two independent chains and the earlier topology
census now agree on the same edge, so the threshold constant is settled: **`Less?.y` = I32 0**.

## CENSUS B MEASURED (2026-09-15 13:5x-14:1x) - and it corrects the topology

`OpTunnelRead_v0` (24/24) and `OpWireSource_v5` (12/12), all reads identity-checked, main VI byte-identical:

| what | measured |
|---|---|
| frames of Case #5540 | exactly TWO: diagrams **5582** and **5592** |
| output tunnels | **SelectorTunnel 6016** -> `x,y,z array` (wire 5975), **SelectorTunnel 5680** -> `Bead is good? array in` (wire 5637) |
| frame 5582 contents | pure pass-through of input tunnels 5825 / 5702, whose outer wires 1681 / 6041 are driven by **LeftShiftRegister 1142** and **LeftShiftRegister 5805** - the PREVIOUS iteration's state |
| frame 5592 contents | pure pass-through of input tunnels 5725 / 5967, whose outer wires 5746 / 5979 are driven by **LoopTunnel 5752** and **LoopTunnel 5569** - values from OUTSIDE the tracking loop |
| consumer of both outputs | **SubVI 5058 = `Track N beads four-fold over-kernel-v3.vi`** (the cached subVI census, diagram 43) - i.e. THE KERNEL |

**Correction to the E0 note:** the case does NOT sit "after the kernel, before the registers". It sits between the
state sources and the KERNEL INPUT: each iteration it decides whether the kernel starts from the previous state (the
left shift registers) or from the reseed values carried in from outside the loop. That is exactly what the fixture
driver encodes ("the next frame's kernel INPUTS become the calibration positions, all-TRUE flags..."), and neither
frame computes anything - both are pass-throughs, which is what makes the two-`Select` `ReseedMux` legitimate.

**What the reseed frame forwards (measured 14:1x):** outer wire 2731 is driven by `FlatSequenceInnerTunnel` **2886**
and outer wire 5812 by `FlatSequenceInnerTunnel` **5818** - and each of those wires has TWO sinks: the left shift
register it initialises (1142 for x,y,z, 5805 for good) AND the loop tunnel feeding the case's reseed frame. So the
reseed values are literally **the loop's INITIALISERS**: reseeding restarts the kernel from the same state the loop
started in (the calibration `x,y,(blank z)` array and the initial good array), which is precisely what the fixture
driver reproduces.

**Design consequence:** `ReseedMux.vi` belongs BEFORE the kernel in `Track_v6_CPU_queue_v0`, selecting the kernel's
input state - not after it - and its `xyz0` / `good0` inputs are the same arrays that initialise the loop's state
registers, which that VI already has in hand. Still open: which diagram is the TRUE frame (needs
`CaseStructure.Frame Names` 6365002; semantically frame 5592 is the reseed frame, but polarity is not assumed).

## Which trigger to build — settled on the data (2026-09-15 12:1x, offline, no LabVIEW)

The driver's rule ("the previous frame's `x,y,z array out` contains −1.0") and the original's own quantity
(`min(pos in cal image out) < 0`) are different measurements, so they were compared on every frame of the reference
session `2026-09-07 16:00:38` (`tools/bench/fixture_compare_results.jsonl`, 10,043 frames):

| test | frames that fire |
|---|---|
| `x,y,z` contains −1.0 | 13 — 11798, 11800, 11804, 11806, 11808, 11810, 11812, 11814, 11816, 11818, 11820, 11822, 11824 |
| `min(pos) < 0` | the SAME 13 |
| any `good` FALSE | 26 (a strict superset — never the trigger) |

Per-bead: 50,215 comparisons of "this bead's x is −1.0" against "this bead's pos < 0" — **0 disagreements**.
So `Reseed.vi` builds the ORIGINAL's quantity (`Array Max & Min(pos in).min < 0`), and the fixture still validates it
bit-for-bit. `good` stays out of the condition.

## Design review of cycle 7 (`archive/peer/2026-09-15-reseed-vi-design-cycle7.md`) — BUILD BLOCKED until two censuses

The reviewer refused the proposed `Reseed.vi`, and the objections are sound:

1. **The mux must be stateless and the decision must live outside it.** Final shape: `ReseedMux.vi`
   (`xyz raw`, `good raw`, `xyz0`, `reseed?` → `xyz next`, `good next`) made of **two `Select` primitives** — no Case
   structure, which also removes three of the four missing ops (Boolean-Case builder, node-output selector, Exit
   Structure). The selector expression and the `# of Auto-Reset` counter stay at loop level, computed once per frame;
   a parallel instance must never own the counter. `reseeded?` logs the FINAL selector, not the lost-bead term.
2. **The periodic auto-reset term stays in.** Dropping it would be a labelled stub, not a behaviour-preserving
   rebuild (rule 1a). Where the Boolean is computed does not change behaviour — dataflow does — so it may be computed
   at loop level and passed in.
3. **Case #10445 may not be collapsed into an `Or` until its frames are read**: a Case executes only the selected
   frame, so an equivalent-looking Boolean expression can change execution if either frame holds active code.
4. **Both frames of #5540 must be read before building**: "TRUE = `xyz0` + all-TRUE good" is the driver's paraphrase,
   not yet the diagram's word — and a wrong frame polarity or a wrong array-size source would pass every non-loss
   frame and fail only at the 13 reseeds.

**Census A (Case #10445):** labels and polarity, every node/tunnel per frame, the inside source of output 10573,
tunnel "default if unwired", and any side effects (writes, locals, property nodes, registers).
**Census B (Case #5540):** for each frame, the backward source cone of output tunnels 5975 and 5637 ONLY — what
determines the good array's size, and whether the xyz source is t1 or t4.
Both are read-only on the main VI and need a case-frame reader op (property IDs being confirmed before it is built).

## Construction (after E0), with the primitives the fleet lacks named up front

The reseed lives INSIDE the tracking loop between the kernel outputs and the registers' right sides; the fleet
can build Cases and comparison primitives only at a VI's top level, so it is a sub-VI:

`Reseed.vi` (pane: `x,y,z in`, `good in`, `pos in`, `xyz0`, `min value`(if the census says so) → `x,y,z next`,
`good next`) built at top level from: a detector (`Less?`/`Equal` + `Or Array Elements` — whichever the census
shows, created by wrapping erdosmiller `Create Less?.vi` / `Create Equal.vi` / `Create Or Array Elements.vi` as ops
in the `OpBuildIA_v0` pattern), a **Boolean Case** (`Create Case Structure (Boolean).vi` → `OpBuildCaseBool_v0`,
selector from the detector's output — `build_case` today takes a CONTROL as selector, so a variant fed by
`Get Outputs` is needed) and **Case output tunnels** (`Exit Structure.vi`/`Exit Multi Frame Structure.vi` →
`OpExitCase_v0`), each frame wiring its passthrough (TRUE: `xyz0` / all-TRUE; FALSE: `x,y,z in` / `good in`).
Integration in `Track_v6_CPU_queue_v0`: kernel outs → `Reseed.vi` → `RightIn` for xyz and good; `pos` unchanged.

Toolkit gaps (each = one op + one functional test, the row-32 pattern): `OpBuildLess_v0`/`OpBuildEqual_v0`,
`OpBuildOrArray_v0`, `OpBuildCaseBool_v0` (selector from a node output), `OpExitCase_v0`. Estimated 4 ops.

## Acceptance

`--full`: **all 10,043 frames** XYZ/GOOD/POS bit-identical to the reference (the 25 post-loss frames included) —
the first time the new structure matches the original across a lost bead. Same 1 → 2 → 200 → full sequence.

## Frame polarity: the functional argument, pending the structural one (2026-09-15 14:4x)

The structural measurement (`CaseStructure.Frame Names` 6365002 paired with `Frames[]` 6363801, op `OpCaseFrames_v0`)
is still being built. Independently of it, polarity is already constrained by the fixture: the driver reproduced the
recording to 0.00000 over 10,043 frames under the rule "condition TRUE -> the kernel's next inputs are the
calibration state", and the census now shows one frame forwarding the loop's INITIALISERS and the other the LEFT
shift registers. Had the polarity been the other way round, the replay would have reseeded on every non-lost frame
and diverged immediately. So the reseed frame is the one that forwards the initialisers (diagram 5592); the
structural read is wanted as confirmation, not as the only evidence.
