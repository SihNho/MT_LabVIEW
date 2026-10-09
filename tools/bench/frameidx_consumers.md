---
type: fact
status: current
date: 2026-10-09
card: 154-a1-2
---
# Consumers of the frame counter: original `#644`/w3268 and s09 `#644`/w29454 + `FrameIdx` (PD374(g), `docs/d1/ring-p5.md:71-74`)
Offline, stored json only, LabVIEW reads 0. Readers `tools/bench/diag_c154_a1_2_census.py` -> `.log` (8/0), `diag_c154_a1_2_chain.py` ->
`diag_c154_a1_2_chain{,2,3}.log`. S1 = `docs/wiki/subvi/D1_s1_copy.json` (byte copy of the original, VI md5 3e3d23ce); s09 = graph 22f967b5.
"census:N" = `tools/bench/diag_c154_a1_2_census.log:N`; "chain:N" = `diag_c154_a1_2_chain.log:N`, "chain3:N" = `diag_c154_a1_2_chain3.log:N`.
COUNTER y = Q&R / every-N / modulo / equality against a count shown by the graph or a cited doc line; n = the graph shows another use.

## 1. ORIGINAL: the 8 sinks of w3268 (source term #644 on Diagram #639 = While #637 body, the frame loop)
Count 8 confirmed twice: S1 json 8 sink rows, 8 owners (census:8-9, gate P1); live read of a byte copy of the CURRENT original 2f048e3a gives
the same 8 owners (`diag_c153_a2_6_orig_read.log:15`). `cycle27-plan.md:1673` lists 6 = Node terminals only (#3191 instead of the 3 tunnels).
| sink (uid, class/name) | loop | what it computes (graph / doc) | COUNTER | evidence |
|---|---|---|---|---|
| #376 SubVI `save trace.vi` t5763 'frame index' | #637 (d639) | inside: Q&R(frame index, file size); remainder = row index of Replace Array Subset; Equal?(remainder, file size-1) -> case writes the file | y | census:11,58; `p5_facts.md:51-53` (`save trace.json:816-1066`) |
| #1114 SubVI `WLC function sub.vi` t3509 'index i' | #637 (d639) | worm-like-chain fit (`frame-loop-anatomy.md:51`); use of 'index i' inside: unmeasured | unmeasured | census:63-64 |
| #2136 Function (Q&R) 'x' | #637 (d639) | x mod y, y <- Property #30146 'Value' (`Frame rate`); remainder -> #3057 'x = 0?' -> #10686 AND (y <- NOT 'Fix to a Certain Pattern') -> #10429 -> autofocus case #10407; w3050 also -> #3302 (case #3191) and #12633 (case #12589) | y | census:89-111; `cycle27-plan.md:3786-3789`; `camera-acquisition-facts.md:189-197` |
| #2213 LoopTunnel (out of #637 to d686) | leaves #637 | after the loop: #1628 x-y, y = tunnel value, x <- #194 x-y ('current image number' #1605 - 'LastBufferNumber' Property #250); result -> FS tunnel #2283 -> Local 'Total Lost Frames' write + #7223 'x != 0?' | n (x-y subtrahend) | census:113-121; chain:39; `diag_c154_a1_2_chain2.log:60-61` |
| #3045 SelectorTunnel of CaseStructure #3191 | #637 (d639, case #3191) | frame d3292: #3162 x-y, y = i, x <- #2347 x-y ('current image number' #3078 - 'LastBufferNumber' #3340) -> indicator terminal 'Total Lost Frames'; frame d3227: unwired (w0); #3191 selector <- #3057 'x = 0?' (w3050) | n (x-y subtrahend) | census:241,385-387; chain:4-5; `chain2.log:58-59`; `cycle27-plan.md:1666-1667` |
| #10068 Function (Q&R) 'x' | #637 (d639) | x mod y, y <- LoopTunnel #10114 '# FD points'; remainder w10187 -> LoopTunnel #10177 -> ForLoop #1359 body d7911 -> #8634 'index (col)' (ring position of the history array) | y | census:392-429; `d1-loop12-17-split-plan.md:1293-1297` |
| #12195 FlatSequenceOuterTunnel (FS #16543, frame d16565) | #637 (d639) | #12045 'x = 0?' (i == 0) -> Tunnel #11942 on CaseStructure #11869 (inner terminals w0) | y (equality with 0) | census:431,589-591; chain:9-11; `chain2.log:57` |
| #29240 Function (Q&R) 'x' | #637 (d639) | x mod y, y <- LoopTunnel #29415 '# DT points'; remainder -> LoopTunnel #29777 -> ForLoop #29874 body d29894 -> #29625 'index (col)' + #29973 BuildArray 'element' | y | census:597-624; `d1-route-b-plan.md:237` |

## 2. s09: consumers of #644 i (w29454), FrameIdx write/read, #10068/#29240, autofocus cadence
#644 now has one wire, w29454, 6 sink owners (census:626-629, gate P2); w3268 does not exist in s09 (census:628). All on d639 = #637 = loop 1.1.
| sink (uid, class/name) | loop | what it computes (graph / doc) | COUNTER | evidence |
|---|---|---|---|---|
| #376 'frame index' t5763 | 1.7 (#23041) | UNWIRED (w0); not a w29454 sink | - | `p5_facts.md:19` |
| #1114 `WLC function sub.vi` 'index i' | 1.1 #637 | as original row | unmeasured | census:631-632 |
| #2136 Q&R 'x' | 1.1 #637 | as original: mod `Frame rate` #30146 -> #3057 'x = 0?' -> #10686 / #3302 / #12633; #10686 out w23526 -> Diagram #639 terminal 'Automatic Error Handling' (sink) | y | census:653-671, 1089-1107; chain3:77 |
| #2213 LoopTunnel | leaves 1.1 | as original (#1628 x-y -> 'Total Lost Frames') | n (x-y subtrahend) | census:673-681 |
| #3045 SelectorTunnel (case #3191) | 1.1 #637 | as original (#3162 x-y -> 'Total Lost Frames') | n (x-y subtrahend) | census:748,807-809 |
| #12195 FS outer tunnel (FS #16543) | 1.1 #637 | as original (#12045 'x = 0?' -> #11942, case #11869) | y (equality with 0) | census:814,877-879 |
| #29440 SelectorTunnel (case #22694, frame d27219) | 1.1 #637 > case #22694 | -> FS outer tunnel #29411 -> FS #27509 frame d32464 -> #6859 'new element/subarray' | n (value stored) | census:885,944-954; chain:6-8,23; `diag_c153_a1_1_census4.log:4-5` |
| #6859 GrowableFunction (terminals array / index / new element/subarray / output array) | FS #27509 in case #22694 in 1.1 | FrameIdx[index w28367 <- FS tunnel #28413] := i; array <- FrameIdx read Local #29313; output -> FrameIdx write Local #29380 | n (value stored) | census:993-1005; `diag_c153_a1_1_census3.log:16-19` |
| FrameIdx terminal t27025 on d4866 (FS #681 frame) | none (init frame) | <- ArrayConstant #26244 (initial value) | n | census:957,989; chain:19 |
| #30239 Local 'FrameIdx' READ -> #30240 IndexArray | 1.2 #10170 (d23166) | element at index w30763 (<- LoopTunnel #30179 'min slot') -> w30278 -> #10068 x, #29240 x | n (indexing only) | census:1006-1028; gate P3 census:1109 |
| #10068 Q&R 'x' | 1.2 #10170 | x mod y, y <- LoopTunnel #30287 '# FD points'; remainder -> #10177 -> ForLoop #1359 (now in 1.2) -> #8634 'index (col)' | y | census:1050-1069; chain:12,27 |
| #29240 Q&R 'x' | 1.2 #10170 | x mod y, y <- LoopTunnel #30290 '# DT points'; remainder -> #29777 -> ForLoop #29874 (1.2) -> #29625 'index (col)' + #29973 | y | census:1073-1087; chain:13,28 |
| autofocus case #10407 selector Tunnel #10429 | #23032 (d23058) | fed by #9996 'x .and. y?' on d23058 (w23847), not by #10686 | not a counter consumer (no #644/FrameIdx path read) | chain3:78; chain:15-16,26 |
Only 4 'FrameIdx' terminal rows exist in s09 (census:957): #4866 term, #29313 read, #29380 write, #30239 read.

## 3. Pairing (same uid in both graphs; facts only)
- #1114, #2136, #2213, #3045, #12195: same uid, same loop #637, same downstream; source wire w3268 -> w29454 (census:8 vs 626).
- #10068 <-> #10068, #29240 <-> #29240: same uid and same y/remainder route; loop #637 -> 1.2 #10170; x from w3268 (i) -> FrameIdx[min slot] via #30240 (census:392 vs 1050; 597 vs 1073).
- #376: original sink on w3268; s09 t5763 unwired -> unpaired.  s09 #29440 / #29411 / #6859 / FrameIdx locals / #30240: no original counterpart -> unpaired.
- Autofocus: original #10686 -> #10429 -> case #10407 on d639 (S1 `chain2.log:54,62`); s09 #10686 -> 'Automatic Error Handling' term, #10429 <- #9996 in #23032 -> unpaired.

## 4. Unmeasured
U1 use of 'index i' inside `WLC function sub.vi` (no wiki json for it in `docs/wiki/subvi/`). U2 #2213 tunnel mode (last value / indexing).
U3 which selector value frame d3292 of #3191 is. U4 what case #11869 does and whether #11942 is its selector (inner terminals w0).
U5 case #12589 contents (#12633 inner w0). U6 selector value of save trace's write frame d110 (`p5_facts.md:53`).
U7 what object the s09 d639 terminal 'Automatic Error Handling' is. U8 selector source of case #22694 (when the FrameIdx write runs).
U9 function names of GrowableFunction #6859/#8634/#29625 (stored graphs hold class + terminal names only). U10 run-time values (nothing run).
Doc conflict, recorded only: `stage2-assembly-step-e.md:36` lists #10068 in the periodic auto-reset term; the S1 graph shows its only output
w10187 -> #10177 -> #8634 'index (col)' (census:394-397).

## 5. Invariants
md5 before == after (census:3-7, gate P4 census:1164): ring-p5.md 58f168cb, graph 22f967b5, p5_facts 1df5c37d, brief 0a16d9d6, s09 VI eb1d0f31 (bytes
hashed, never opened), stagekit 604529e8, stagexec 1bab9cf9, stagesim 78b8d5a1, vigraph a7eb58c7, stage_prerun c739eb86, gscript 1a80236e.
OPEN: which of the counter-y consumers (#376, #2136, #10068, #29240, #12195) P6 must feed with the original i vs FrameIdx is judgement's (PD374(g)).
