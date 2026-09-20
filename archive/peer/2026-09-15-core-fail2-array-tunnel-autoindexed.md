---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# core-fail2-array-tunnel-autoindexed

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (47s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting over COM; rule 1a: the kernel's per-frame inputs must be byte-identical to the original). Log: tools/bench/build_track_v6_core.log run 2 (31/32), script tools/recipes/build_track_v6_core.py, your gate from archive/peer/2026-09-15-core-fail1-border-wire-gate.md.
OBSERVED: gscript.wire(HARNESS_loadcal.'Array of cal clusters' [top level, a 1-D array of clusters] -> PARALLEL_kernel_v3clean.'Array of cal clusters' [inside the For loop body]) created exactly one new tunnel, continuous 550 -> tunnel -> 534, correct direction, clean errors - but IndexMode 1 (AUTO-INDEXED), so the gate (IndexMode 0 required) stopped the build. The scalar image refnum wire two steps earlier came out IndexMode 0.
MY DIAGNOSIS: erdosmiller Wire Inputs.vi (or LabVIEW's tunnel creation it calls) applies LabVIEW's editor default - an ARRAY wired into a For loop auto-indexes - so every whole-array input (cal clusters, the two window arrays) will arrive indexed: one element per iteration into an input that expects the whole array (the wire is then element-into-array: broken, or worse, legal-but-wrong if the element type happened to match). This is precisely the computation change rule 1a forbids and the gate caught it.
FIX PLANNED: in wire_sub, when the new tunnel reads IndexMode 1 for a whole-value input, call set_index_mode(tunnel, 0) (OpSetIndexMode_v0, verified) and re-read: require IndexMode 0, inner wire still == the sink's wire, outer == source, then ExecState at the end. This is the mirror of the L3 route proven in phase D (wire then flip to indexed) - here flip to NON-indexed.
Attack: (1) Does changing a tunnel from indexed to non-indexed keep the existing inner wire (it retypes the inner terminal from element to array, which then MATCHES the kernel's array input) - or does LabVIEW delete/break the inner wire on mode change? Cite NI. (2) Is there a way to make Wire Inputs create the tunnel non-indexed from the start (a library input, or wiring the sink first)? (3) For the cross-check: which other inputs must be verified IndexMode 0 - 'Array of cal clusters', 'Cosine bandpass for Hilbert', 'Real-space cosine window' (all arrays) - and 'cross size' (scalar I32)? (4) Rule 1a: with IndexMode 0 the whole array enters each iteration unchanged - confirm no copy that alters values. (5) Cheapest readback proving the fix beyond IndexMode 0 (e.g. after the flip, ExecState goes from 0 to 1 only when all required inputs are wired - so use the FINAL ExecState plus the 1-frame exact run). Read-only; cite what you read.


## Answer

Your diagnosis is substantially right, but claim (1) is stronger than the available NI evidence supports.

1. Changing indexed ??non-indexed

NI explicitly documents that:

- Array inputs to a For Loop are auto-indexed by default.
- Auto-indexing passes one element per iteration.
- Disabling indexing passes the entire array into every iteration.
- `LoopTunnel.IndexMode` is read/write, with `0 = Regular` and `1 = Auto Index`.  
  [NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG), [NI IndexMode API reference](https://www.ni.com/docs/ko-KR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/tunnel/looptunnel/indexmode.html)

However, I found no NI documentation guaranteeing that changing `IndexMode` preserves the existing inner wire object or its identity. NI only documents the semantic toggle, not scripting-side object survival. Therefore:

- ?쏶et `IndexMode=0`, then re-read and verify both wire identities/connectivity??is the correct defensive procedure.
- Do not assume `inner_wire_id` must remain numerically identical unless your existing scripting experiment establishes that contract. The meaningful invariant is that the tunnel?셲 inner terminal remains connected to the intended sink by one continuous, unbroken wire.
- Also re-check the tunnel?셲 direction and terminal types after the flip. NI notes that incompatible types produce broken wires and prevent execution. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

Thus the planned fix is sound, but wire preservation is an experimentally verified postcondition, not an NI-guaranteed premise.

2. Creating it non-indexed initially

I found no documented input to Erdos Miller?셲 `Wire Inputs.vi` that specifies a newly created loop tunnel?셲 indexing mode. The public project describes itself as a convenience library over VI Scripting, but its published documentation does not advertise tunnel-mode control. [Erdos Miller lv-scripting repository](https://github.com/erdosmiller/lv-scripting)

Nor did I find NI documentation saying that wiring the inside sink first changes the For Loop?셲 default. NI states broadly that auto-indexing is the default whenever an array is wired into a For Loop. [NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

Therefore the dependable public-API sequence is:

`wire ??identify the newly created tunnel ??set IndexMode=0 ??verify topology/types`

Sink-first wiring might alter a particular helper?셲 behavior, but it is not a documented guarantee and is inferior to explicit mode setting.

3. Inputs that require the gate

Given the types you supplied:

- `Array of cal clusters`: require `IndexMode == 0`.
- `Cosine bandpass for Hilbert`: require `IndexMode == 0`.
- `Real-space cosine window`: require `IndexMode == 0`.
- `cross size` (`I32` scalar): require `IndexMode == 0`, or more precisely require a regular, non-indexing input tunnel.

The scalar check is still valuable as a topology/invariant check even though scalar input cannot meaningfully deliver ?쐎ne array element per iteration.??I would apply `IndexMode == 0` to every whole-value input, not only arrays. This prevents correctness from depending on LabVIEW?셲 type-sensitive editor defaults.

A second danger strengthens your diagnosis: auto-indexed arrays can also determine or shorten the For Loop iteration count. If several indexed arrays differ in length, LabVIEW uses the smallest applicable count. [NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

4. Byte identity and copying

`IndexMode=0` gives the required value semantics: the entire array is available in every iteration rather than an extracted element. [NI arrays documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html)

A memory copy, if LabVIEW chooses to make one, does not itself alter the logical value. Arrays and clusters are by-value LabVIEW types, and compiler buffer decisions are implementation optimizations. [NI by-value explanation](https://www.ni.com/en/support/documentation/supplemental/06/labview-object-oriented-programming-faq.html), [NI compiler/inplaceness explanation](https://www.ni.com/en/support/documentation/supplemental/10/ni-labview-compiler--under-the-hood.html)

One wording correction: `IndexMode=0` establishes value identity, not necessarily the absence of a physical copy. NI even warns in an embedded-performance context that loop passage can involve copying. [NI embedded optimization guidance](https://www.ni.com/en/support/documentation/supplemental/21/optimizing-labview-embedded-applications.html)

So rule 1a should test byte-equivalent contents, dimensions, element representation, and cluster layout?봭ot buffer address or ?쐍o allocation.??
5. Cheapest convincing readback

Use layered gates:

1. Immediately after each flip:
   - `IndexMode == 0`
   - correct tunnel direction
   - outer connection reaches the intended source
   - inner connection reaches exactly the intended sink
   - no extra tunnel
   - no broken-wire/error report

2. After all wiring:
   - final `ExecState` runnable check.

3. Semantic proof:
   - one-frame execution with exact comparison against the original for every observable kernel result.
   - Prefer bitwise comparison of flattened outputs, including dimensions and type representation, rather than numeric tolerance.

Final `ExecState` alone is insufficient: a runnable VI can be legal but computationally wrong, including an accidentally auto-indexed connection whose element type happens to match. NI only presents the broken run state as evidence of wiring/type errors, not semantic equivalence. [NI debugging documentation](https://www.ni.com/getting-started/labview-basics/debug.htm)

Bottom line: proceed with the flip-and-reverify design. The gate caught a real default-behavior hazard. The only rejected part is treating preservation of the existing inner wire as documented fact; make connectivity after mutation a required observed postcondition.

## Sources

(extract from answer)

## What was done with it

Adopted. `wire_sub` flips a freshly created IndexMode-1 tunnel to 0 and then re-reads BOTH ends (the sink's wire
uid and the tunnel's `in_wires`) before the gate — wire survival is treated as a measured postcondition, not a
premise; the IndexMode-0 requirement applies to every whole-value input (arrays and the scalar `cross size`
alike). Recorded in NAMES.md ("an ARRAY wired INTO a For loop by name arrives AUTO-INDEXED"). Rerun:
`tools/bench/build_track_v6_core.log` (run 3).
