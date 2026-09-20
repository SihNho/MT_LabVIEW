---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# core-fail1-border-wire-gate

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (67s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS (LabVIEW 2026 VI Scripting over COM). Log: tools/bench/build_track_v6_core.log (28/29; script tools/recipes/build_track_v6_core.py, reviewed as archive/peer/2026-09-15-stage2-cycle4-replay-core-recipe-v2.md). Everything through L3 passed (scratch discriminator of the tunnel route, temp-kernel controls, String[] control, the indexed Frame Paths tunnel with inner wire == StrToPath.string). The first L4 wire, gscript.wire(IMAQ Create.'New Image' [top level] -> IMAQ ReadFile.'Image' [inside the For loop body]), FAILED my gate "same wire uid on both ends": the source terminal reports wire 531, the sink 506.
MY DIAGNOSIS: the gate is wrong for a wire that crosses a structure border - erdosmiller Wire Inputs creates a tunnel and the connection is TWO Wire objects (outer: source -> tunnel outer terminal; inner: tunnel inner terminal -> sink). This project measured exactly that on 2026-09-14 (INDEX row 36 T3: a control wired through two borders -> "outer 530->514, inner 514->497"). So 531/506 is the expected signature of a correct border-crossing wire, and the correct gate is: both ends non-zero AND a NEW LoopTunnel exists whose outer terminal carries the source's wire uid (531) and whose inner terminal carries the sink's (506), IndexMode 0 (non-indexed) for these whole-value inputs.
Attack: (1) any reading where 531/506 indicates a WRONG connection (e.g. the sink wired from something else, or a second tunnel)? (2) is the corrected gate sufficient, and should it also require IndexMode 0 for every non-indexed border crossing (the cal-cluster array, windows, the image refnum) so an accidental auto-index cannot slip in? (3) rule 1a: a non-indexed tunnel passes the whole array unchanged into each iteration - confirm no copy/coercion that could alter DBL arrays (NI doc). (4) cheapest discriminating readback with the fleet's tunnels() reader. Read-only; cite what you read.


## Answer

Verdict: your diagnosis is substantially correct. `531/506` is consistent with a valid one-border connection and invalidates the old same-Wire-UID gate. However, the proposed replacement needs two additional uniqueness/direction checks.

1. Could `531/506` still be wrong?

Yes, by itself. Non-zero unequal UIDs prove only that both endpoint terminals are wired. Possible false positives include:

- The source reaches tunnel A while the sink is fed through tunnel B.
- The matching tunnel exists, but the operation also created an unintended second tunnel.
- The intended connection exists but has an unintended branch to another sink.

Your same-tunnel condition rules out the first case:

```python
t["out_wire"] == source_wire
and sink_wire in t["in_wires"]
```

That establishes a continuous source ??tunnel ??sink route. The recorded direction convention also supports it: an input tunnel has an outside sink and an inside source (`out_is_source == False`, `in_is_source == [True]`), as measured in [test_optunnels.log](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/test_optunnels.log:3).

But the current implementation uses `any(...)` across `new_t`; it does not require exactly one new tunnel. For a single-border, previously unwired source-to-sink operation, strengthen it to:

```python
len(new_t) == 1
and t["out_wire"] == source_wire
and t["in_wires"] == [sink_wire]
and t["out_is_source"] is False
and t["in_is_source"] == [True]
and t["out_conn_err"] == 0
and t["out_wire_err"] == 0
and t["index_mode"] == 0
```

Thus `531/506` is expected, but not sufficient without the tunnel readback. Unintended fan-out on either wire remains outside `tunnels()`?셲 scope; that requires a terminal/net-map census or eventual functional comparison. It does not make the requested source-to-sink connection wrong, but could make the overall VI wrong.

2. Is the corrected gate sufficient, and require `IndexMode == 0`?

With the uniqueness and direction additions above, it is a strong structural gate for the requested one-border connection.

Yes: require `IndexMode == 0` for every input intended to be delivered whole on every iteration:

- calibration-cluster array;
- window/parameter arrays;
- image refnum;
- any other loop-invariant whole value.

This is especially important for arrays. For-loop array inputs normally default to auto-indexing, and auto-indexing changes the inside value from the whole array to one element per iteration. NI explicitly says disabling indexing makes the loop handle all elements at once. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

For the scalar image refnum, mode 0 is still the appropriate intent gate: it prevents a later datatype or creator-behaviour change from silently changing the tunnel contract. Retain the final `ExecState == 1` and functional fixture gates as protection against type-invalid or misconnected diagrams.

3. Rule 1a: whole DBL array and coercion/copy

Semantically confirmed: with input auto-indexing disabled, LabVIEW passes the entire array into the loop rather than one element per iteration. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG), [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

But ?쐍o copy??is too strong. NI?셲 documentation establishes value/indexing semantics, not a guarantee that the compiler never creates an internal buffer copy. LabVIEW may copy data for memory-management reasons without changing its values.

Likewise, the tunnel itself does not imply numeric conversion, but a receiving terminal with a different compatible datatype can cause coercion. NI says such conversion is marked by a coercion dot and may affect memory, performance, and numerical accuracy. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

The defensible rule is:

> A non-indexed tunnel presents the complete DBL array, with unchanged array rank and element representation, on every iteration. It does not promise zero buffer copies. Exclude datatype conversion separately by checking the receiving terminal?셲 expected type/coercion state or by an exact functional comparison.

4. Cheapest discriminating `tunnels()` readback

For each `wire_sub` crossing:

1. Snapshot `LoopTunnel` UIDs.
2. Perform the wire operation.
3. Require exactly one new tunnel.
4. Read that tunnel once with `tunnels()`.
5. Require:

```text
tunnel UID is new
index_mode == 0
out_wire == source terminal wire UID
in_wires == [sink terminal wire UID]
out_is_source == False
in_is_source == [True]
out_conn_err == 0
out_wire_err == 0
source wire != 0
sink wire != 0
```

This is cheaper and more discriminating than rescanning the entire diagram. The fleet reader explicitly defines `out_wire` as the parent-diagram wire and `in_wires` as the loop-body wire(s), matching this use in [gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:728).

So: replace the equality gate, but change the current `any(...)` implementation to an exactly-one-new-tunnel, exact-wire-list, direction-and-error gate. Keep `IndexMode == 0` mandatory for all loop-invariant inputs.

## Sources

(extract from answer)

## What was done with it

Diagnosis confirmed; the strengthened gate adopted verbatim in `build_track_v6_core.py::wire_sub` for every
border-crossing wire: exactly one new LoopTunnel, `out_wire == source`, `in_wires == [sink]`, outer sink / inner
source direction flags, clean `out_conn_err`/`out_wire_err`, IndexMode 0 (the whole-value inputs: image refnum,
cal clusters, windows, cross size — the two param controls go through `wire_control` with their own gate). Fan-out
beyond the requested connection stays outside `tunnels()`' scope and is caught functionally by the 1/2/200-frame
exact runs. Rerun: `tools/bench/build_track_v6_core.log` (run 2).
