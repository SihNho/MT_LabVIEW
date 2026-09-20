---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# display-bench-results

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (31s)
- **why asked:** interpretation of the first display-bench run (Draw → Picture +7.4 ms, first cell anomalous) before writing it into a report.
- **verdict:** ACTED ON, and the peer's key cell decided it: disp4 (Draw with the indicator removed) — construction +1.6 ms, Picture indicator write/paint **+6.5 ms only when the panel is visible** (0.2 ms closed). Cold-cache artefact confirmed (full pre-read: first cell 1.83 ms); run 1's "closed" cells had been measured with panels the build left open — fixed (panels closed after build). COM-Run-per-frame confound stated in the report; within-condition deltas only. Report: archive/bench-2026-09-14-display-path/REPORT.md.

## Question

RESULT REVIEW (attack the interpretation; brief). tools/bench/run_display_bench.log, harnesses built by tools/recipes/build_harness_display.py (disp0 = IMAQ Create + IMAQ ReadFile(File Path control); disp1 = + IMAQ ImageToArray (U8); disp2 = + Flatten Pixmap.vi; disp3 = + Draw Flattened Pixmap.vi -> Picture indicator), fixture 1280x1024 8-bit TIFF frames, one COM Run per frame timed from Python (perf_counter), 10 warm + 200 timed, medians: closed panel: disp0 15.54 (p90 28.2 - FIRST cell of the run), disp1 6.96, disp2 7.10, disp3 14.71; panel opened via COM: disp0 7.03, disp1 7.30, disp2 7.37, disp3 14.70. MY READING: (a) the first cell is a cold OS file cache artefact (the same 210 files are re-read by every later cell; rerun with a full pre-read warm-up is queued); (b) base ~7.0 ms = COM Run overhead + IMAQ ReadFile of a 1.3 MB TIFF; (c) ImageToArray ~+0.3 ms, Flatten Pixmap ~+0.1 ms, Draw Flattened Pixmap -> Picture ~+7.4 ms per frame, IDENTICAL with the panel closed or open, so the cost is the picture construction (a 1280x1024 8-bit -> picture data string), not painting; (d) conclusion for the restructuring: the main VI's display route (diagram 99: ImageToArray -> Flatten Pixmap -> Draw Flattened Pixmap, docs said 'the slowest documented path') costs ~7.5 ms of CPU per frame - above the whole 6 ms/frame budget at 150 Hz - so the display loop must be decoupled and decimated (Last mode, own loop, e.g. 10-20 Hz), or replaced by the IMAQ Image Display control route (not measured, no donor). ATTACK: is +7.4 ms plausibly Draw Flattened Pixmap's own CPU work for 1.3 Mpx (what does it do internally - builds a bitmap record; NI/community numbers?), or could the Picture INDICATOR write (a 1.3 MB picture string into a front-panel object, even with the panel closed - LabVIEW still copies the data to the control) be the cost - i.e. would disp3 without the indicator (output unwired) be cheaper, and is that the right discriminator? Any other confound (COM Run overhead scaling with the VI's panel data size: the Picture indicator holds 1.3 MB, so each Run's completion/marshalling could cost more; the harness's own Flatten Pixmap output unwired in disp2 = never computed by LabVIEW's optimizer?). Propose the cheapest discriminating cells.

## Answer

Your restructuring conclusion is directionally sound, but ?쏡raw Flattened Pixmap itself consumes 7.4 ms CPU??is not yet established.

The equal closed/open timings rule out most actual screen painting, but they do not distinguish:

- constructing the picture-data string;
- copying it into the Picture indicator terminal;
- invalidating/updating the indicator?셲 retained front-panel state;
- synchronization or allocation costs completed before COM `Run` returns.

NI explicitly treats Draw Flattened Pixmap as producing the data used by a Picture indicator, while indicator writes have their own data/update semantics and front-panel invalidation can impose cost even apart from visible redraws. [NI: Open and Display Image File](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P72USAS&l=en-US), [NI: control/indicator performance differences](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LXrSAM&l=en-US), [NI: front-panel invalidation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kHjFSAU&l=en-US)

The optimizer concern is real. An unwired Flatten Pixmap output is not a valid measurement of Flatten Pixmap execution?봞nd the same concern applies transitively to ImageToArray?봟ecause LabVIEW performs dead/unreachable-code elimination, particularly around inlined code. [NI: LabVIEW Compiler Under the Hood](https://www.ni.com/en/support/documentation/supplemental/10/ni-labview-compiler--under-the-hood.html)

Cheapest discriminating cells:

1. `ReadFile ??ImageToArray ??Array Size ??scalar indicator`  
   Forces ImageToArray while retaining only tiny output.

2. `????Flatten Pixmap ??String Length ??scalar indicator`  
   Forces Flatten Pixmap without retaining its large result.

3. `????Draw Flattened Pixmap ??String Length ??scalar indicator`  
   This is the key cell. If it remains ??4.7 ms, the ??.4 ms is picture construction/allocation, not the Picture indicator.

4. Same as cell 3, additionally wire the picture data to the Picture indicator.  
   The difference from cell 3 measures terminal assignment/retention/invalidation.

5. Optional control: generate or reuse a same-sized picture string and write it to the Picture indicator without calling Draw.  
   This directly estimates large-indicator assignment cost.

Run cells randomized or interleaved, not as a fixed disp0?뭗isp3 sequence. The first-cell cache explanation is plausible, but the existing ten warm-ups do not prove it; random ordering or fully pre-reading every fixture is the cheap settlement.

I would phrase the present conclusion as: ?쏷he Draw-plus-Picture-terminal route adds ??.4 ms wall time per COM invocation.??Do not yet call that CPU time or attribute it solely to Draw. Also, one COM `Run` per frame may exaggerate allocation, scheduling, and synchronization relative to a persistent in-VI loop.

Decoupling and Last-value decimation still follows: the measured complete display route already exceeds the 6 ms acquisition budget. The proposed 10??0 Hz rate is an engineering policy, not something these cells themselves establish. An IMAQ Image Display control remains a promising but unmeasured alternative.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
