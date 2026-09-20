---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, vi-scripting]
---

# copyloop-gate-controlnames-fail

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (21s)
- **why asked:** failed prediction: for_loop(tunnels=[label], indexing=[True]) created the loop but no tunnel (tools/bench/build_harness_copyloop.log)
- **verdict:** unverified

## Question

FAILED PREDICTION check, brief. tools/bench/build_harness_copyloop.log (recipe tools/recipes/build_harness_copyloop.py): gscript.for_loop(target, pos, tunnels=['8-bit pixmap'], indexing=[True]) (erdosmiller Create For Loop.vi, 'Control Names' = the label of an existing UNWIRED 2D U8 array control) created the For loop (ForLoop 0->1) but NO LoopTunnel (0), the control's terminal stayed unwired (panel_wiring wire 0), ExecState 0 (an empty loop has no N) - the gate you asked for said NO. Reading: Create For Loop's Control Names does not wire an existing control into the new loop (perhaps it expects controls it creates itself, or terminals already wired to something). FALLBACK (proven pieces): (1) g.build_index_array(target, pos, ...) dropped INSIDE the loop body (build_index_array takes a diagram? if not, the IA lands on the top diagram - I will check its signature) ; (2) g.wire_control(target, ['8-bit pixmap'], 'IndexArray', idx, ['array']) - wiring a top-level control to a node inside a structure auto-creates the tunnel (measured 2026-09-09 for a Case structure: +2 wires); (3) g.set_index_mode(tunnel, 1) to force auto-indexing; gate again: one LoopTunnel, IndexMode 1, control wire != 0, ExecState 1 (N now supplied by the array). ATTACK: (a) any reason a For loop's input tunnel created by wiring an array would default to NON-indexed (then N missing -> ExecState 0 until set_index_mode 1 - fine) or that Index Array inside the loop receiving a 1D row (element of the 2D auto-index) rejects the type; (b) alternative cheaper N source: wire the SAME array control to the loop's N terminal? (not addressable by script - agreed?); (c) is there any risk the auto-indexed tunnel iterates over COLUMNS rather than rows for a 2D array (LabVIEW: outermost dimension = rows)? One paragraph.

## Answer

The fallback is sound, with one correction: a newly wired array input tunnel on a For Loop should default to auto-indexing, so `set_index_mode(tunnel, 1)` is a useful explicit safeguard rather than something normally needed; auto-indexing supplies `N` automatically. A 2D array becomes one 1D row per iteration, so an Index Array node inside the loop accepts the resulting type, and LabVIEW indexes rows?봭ot columns?봟y default ([NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG), [NI array documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html)). Wiring the same 2D array directly to `N` is not a cheaper alternative: `N` requires a scalar iteration count, so this is a type mismatch; the explicit equivalent would require Array Size plus selection of dimension 0 ([NI For Loop documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYFCA4&l=en-US)). Thus the real remaining uncertainty is only your wrapper API?봶hether `build_index_array` accepts/places into a structure subdiagram?봭ot LabVIEW?셲 typing or loop semantics.

## Sources

(extract from answer)

## What was done with it

Confirmed the remaining uncertainty was our wrapper: build_index_array places only on the top diagram, so the Index-Array-in-body fallback is not buildable as is. Took the peer's N-type point (a 2D array cannot feed N) and switched to a scalar N source: IMAQ GetImageSize Y Resolution -> loop N via Terminal.Connect Wire (build_harness_copyloop2.py). Verdict: correct on typing; the N route is under test (see 2026-09-14-copyloop2-forloop-terminals-unnamed.md).
