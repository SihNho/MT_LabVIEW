---
type: facts
status: current
date: 2026-10-09
card: 153-a2-1
---
# Card 153-a2-1: source of #376 'frame index' - original vs S1 (facts only; card stopped before any doc fix)

Reader: `tools/bench/diag_c153_a2_1_orig_read.py` -> `.log` (offline, json only, 4/0). **LabVIEW reads: 0.** No copy made.

## Original (on-disk census, no LabVIEW)
`tools/bench/orig_3state_nodeterms.json` (md5 b9e6849f; `vi` = `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`,
census-time original md5 before/after **c39f36e0** `:2-6`).
- `#376` (`:12191`, diagram 43 WhileLoop) t7 `frame index`, is_source false, **wire 3268** (`:12278-12281`).
- w3268 has **no Node-terminal source** in the census; node sinks #2136 t3 'x', #3191 t1, #376 t7, #10068 t3 'x', #1114 t0
  'index i', #29240 t3 'x' (`diag_c153_a2_1_orig_read.log:20-21`). The census sees Node terminals only (scope limit,
  `docs/frame-loop-wire-graph.md:29`), so the source end (a diagram-owned terminal) is not visible in it.
- `#5119` (`:14993`) t0 `x-y` is a SOURCE of **wire 16483** (`:14996-14999`) -> `#2626` (`:14861`) t1 `element`
  (`:14876-14879`). So #5119 does NOT feed 'frame index' in the original.
- Corroboration on V6 (= original + 2 fixture nodes, md5 2a78e17c): w3268 Terms[0] source owner `Diagram` 639
  (`tools/bench/diag_autofocus_border.log:20`).

## S1
`docs/wiki/subvi/D1_s1_copy.json:36385-36392`: term_uid **644**, is_source true, wire_uid **3268**, owner Diagram 639
(= While #637 body) - #637 `i` (`docs/cycle27-plan.md:3748-3751`).

## Comparison
Same wire uid 3268, same five non-#376 node sinks, no node source in either, #5119 x-y on a different wire (16483).
Wire-level: SAME as S1. Not read in the original: the source terminal's own uid (#644) - the census cannot see it.

## Why the card stopped (unexpected result)
The original on disk now hashes **2f048e3a18de3b5e3ca8368f6a24dae0**, not the census-time c39f36e0
(`diag_c153_a2_1_md5_before.log:13`). The census therefore describes an earlier state of the original. No doc was edited
(NAMES.md:112, fixture-recording.md:18, p5_facts F4 untouched).
