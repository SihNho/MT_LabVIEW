---
type: facts
status: current
date: 2026-10-09
card: 153-a2-6
---
# Card 153-a2-6: source of #376 'frame index' in the CURRENT original (2f048e3a) - facts only; card returned FAIL before any doc fix

## md5 change (offline, `tools/bench/diag_c153_a2_6_rsrc.log`, 4/0)
- Original 4.5 now: 471,361 B, mtime 2026-10-07 15:48:44, md5 2f048e3a18de3b5e3ca8368f6a24dae0 (`diag_c153_a2_6_rsrc.log:3`).
- 2026-09-18 snapshot `claudeDev\Track_D0_copy_20260918.vi`: 471,257 B, md5 c39f36e0675339673b707c59f0784fee (`:4`) = census-time original.
- Both saved by LV2026 (`26 00 80 00` at offset 36, `:7`). RSRC blocks 45 = 45; 35 identical; 10 differ: BDHb 190531 B -> 190531 B (same size,
  other bytes), FPHb +111 B, DFDS -1 B, BDPW, HIST, LVSR, PICC, RTSG, STR, SUID (`:8-10`).
- No project BGRUN START from 15:30 to 16:00 on 2026-10-07 (grep of tools/bench/*.log); no gui_actions.log line 13:00-16:59 that day.
  Hypothesis review: `archive/peer/2026-10-09-c153-a2-6-origmd5.md` (ANSWERED; it says a no-edit resave is possible and the md5 cannot say who saved).

## ONE byte-copy read (`tools/bench/diag_c153_a2_6_orig_read.py` -> `.log`, 10 pass / 4 fail)
Copy `claudeDev\scratch_c153_a2_6_orig.vi`, md5 == original 2f048e3a (`:7`); loaded headless, GObject census 9,967 objects +
OpAllTerms_v1 5,738 rows (`:9`); no edit, no save, no Run; copy deleted, LabVIEW gone, original md5 before == after (`:23-27`).
- `#376` is SubVI (`:10`); its 'frame index' = term **5763**, sink, **wire 3268**, frame_diagram 639 (`:11`).
- Source of w3268: term **#644**, leaf class `Terminal`, owner **Diagram #639**, whose owner class is **WhileLoop** (`:13`) = the loop's `i`.
- w3268 sinks: #376 frame index, #1114 index i, #2136 x, #2213 LoopTunnel, #3045 SelectorTunnel, #10068 x, #12195 FS outer tunnel, #29240 x (`:15`).
- `#5119 x-y` -> wire 16483 -> #2626 'element' only (`:20`).

## S1 (unchanged)
`docs/wiki/subvi/D1_s1_copy.json:36385-36392`: term 644, source, wire 3268, owner Diagram 639; the same row twice (`:36395-36400`); sinks on
w3268 = terms 29256/#29240, 12200/#12195, 3509/#1114, 10083/#10068, 3272/#3045, 3211/#2136, **5763/#376**, 2218/#2213 (grep of that file).

## Comparison
Source by what the wire comes FROM: SAME - Diagram-owned `Terminal` #644 on WhileLoop body #639, both sides, same uids; sink set on w3268
identical to S1 (8 owners). The 2026-09-18 census lists #3191 instead of the three tunnels (Node terminals only).

## Why the card returned FAIL (prediction defects of this script, recorded, not retried)
R3/R4 FAIL: read_terms gives the #644 row TWICE (`:13-14`; S1's json has the same duplicate) and the gates demanded one row.
R5 FAIL: the census set was the wrong comparison set (census scope differs: +2213 +3045 +12195, -3191, `:19`).
H FAIL: handle count FELL 57667 -> 51115 (`:22`); the gate tested |delta| <= 100. No doc edited: NAMES.md:112, fixture-recording.md:18, p5_facts F4 untouched.
