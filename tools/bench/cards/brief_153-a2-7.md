---
card: 153-a2-7
status: current
date: 2026-10-09
---
# Brief 153-a2-7 - apply the doc correction that the finished measurement of card 153-a2-6 supports (PD371(c)); offline, docs only

The measurement is DONE and is not repeated: `tools/bench/cards/result_153-a2-6.json` and `tools/bench/diag_c153_a2_6_original_frame_index.md`,
`tools/bench/diag_c153_a2_6_orig_read.log:11-13`. In the CURRENT original (md5 2f048e3a, read through ONE claudeDev byte copy, since deleted),
#376 SubVI `frame index` = term 5763, wire 3268 <- term #644 (leaf Terminal) owner Diagram #639, whose owner is the While loop = loop `i`;
the sink set equals S1's (`D1_s1_copy.json:35865-35870`, `:36385-36392`, `cycle27-plan.md:3748-3751`); #5119 x-y feeds only #2626 'element'
(`orig_read.log:20`). Card 153-a2-6's gate FAILs were defects of its own script's predictions (the #644 row appears twice, S1's json has the same
duplicate at `:36395`; wrong census-set scope; a handle DROP of 6552, not growth) - they do not touch the comparison. So the pre-scripted branch
"same source" applies. You may re-read `orig_read.log` and the .md; you do NOT run LabVIEW and do NOT open any .vi.

## What to do
1. `docs/NAMES.md:112` and `docs/fixture-recording.md:18`: add a dated note directly under or beside the old text (keep the old text):
   "2026-10-09 (card 153-a2-7): corrected - frame index is fed by the While loop `i` (wire 3268 <- #644/#639), not #5119 x-y; evidence
   tools/bench/diag_c153_a2_6_orig_read.log:11-13, docs/cycle27-plan.md:3748-3751". Read both lines first and keep the doc's own style.
2. `tools/bench/p5_facts.md` F4 (line 48 region, "Doc conflict" ~line 57) and `p5_facts.json`: cite the correction (same evidence). Nothing else in F4 changes.
3. Quote the edited lines file:line and the md5 of the four files before/after. `p5_facts.json` must still parse (`py -c "import json;json.load(...)"`).

## Invariants
original VI untouched; s09 eb1d0f31; stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86,
stagesim 78b8d5a1, vigraph 13be0847. No tools/hooks edit, no plan file, no `docs/d1/ring-p5.md`, no LabVIEW, no motor or camera.

## Return (<= 20 lines)
Edited file:lines, md5 table, JSON parse OK. `OPEN:` for anything needing judgement. Failure budget 2.
