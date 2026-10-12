---
type: facts
status: current
date: 2026-10-12
card: 167-a1-3
---
# Card 167-a1-3 - P6-0 (c)(e) closure table, OFFLINE (facts only, classes by citation, no fix, no verdict)
- Script `tools/bench/diag_c167_a1_3_closure.py` (0bc95060) -> log `tools/bench/diag_c167_a1_3_closure.log` (final run :37-71): RESULT PASS 24/0, rc 0.
- Outputs: `tools/bench/p6_closure.json` 502a43d416dca9dbddf73c39b945bed7; `tools/bench/p6_closure.md` 1c2304a0140bc94ed85c2430378874c9.
- Hashes: 13 card inputs + 7 VIs (75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d) equal before and after; no LabVIEW process
  (`diag_c167_a1_3_hash_before.log` 9/0, `_hash_after.log` 9/0, closure log B/A gates). No VI opened; no shared module/STATUS/plan/hook edit.
- Equality: both open_rows lists (`plan_ring_p5s02e.json:12` and `:319`) = 24 (node, term) pairs each, equal as sets.
  Frame-keyed `computation_diff(S1, 7815af09)` = 31 rows / 29 pairs: NOT equal to open_rows - 5 pairs only in cdiff, none only in open_rows:
  #376 'cal cluster path', 'error in', 'file size', 'selected path', 'total data array in' = exactly the PB rows the P5 scratch RECORDED
  (`diag_c165_p5s02e_scratch.log:152-156`; frame-tag-only differences). Default-mode cdiff = 26 rows / 24 pairs = open_rows, equal (log :19-20).
- Rows 75 (31 cdiff + 44 more from EL items; the 47 EL items all sit on >= 1 row, gate E1). Per class: R 27, D 19, DISP 5, C 2, U 22.
- U rows (22) = all the EL item-only rows (uid unread, no sink to cite): looseends EL[0,1,4,6,14,21,25,31..42,45,46] (21) + twotypes EL[3] (1).
  No terminal-keyed row is U.
- C rows: t10083 (#10068 'x') and t29256 (#29240 'x'), both <- #30240 'element' (FrameIdx), cite p6_crows.json:414 / :383.
- DISP (5): #11261 'array' t11270 and 'element' t11273 (unfed in P5, ring-p4.md:52 PD295(b)); indicator t8323 'Force (pN) vs Extension (nm)';
  t17272 'min value'; t28786 'Extension (nm) vs Time (Frame #)' (PD298(d) display, plan_ring_p4_s06v18.json:374 / s07v18.json:215).
- R rows cite PD374(b)/(d), PD379(b), PD366(d), PD293(b) SR A-F (plan_ring_p4_s07v18/s08v18 "Select -> right SR inner" lines, matched by the
  Select's output register uid in the P5 graph), PD295(a), PD255(e)/PD257(a), PD233(f)(1), PD300(b)/PD308(a) (#10382 'x' via Select #4577 ->
  indicator t25557 -> Local, plan_ring_p4_s08v18.json:349). 5 R rows (#376 inputs) are tag-only; cited PD374(d) + the plan action that wired them.
- D (19) = 18 rows of 16 termless F1 wires (17 S1-sink rows, w28847 and w31166 have 2 sinks each, + `wire:23556`, no S1 terminal row) + t10080
  (source-only w10103; #10068 'y' fed in P5 by #30287 '# FD points'). The other 6 termless wires sit on R rows (w5637, w5975; 'also D') and DISP
  rows (w10908, w11352, w17287, w32890). w12256's sink #11261 'element' is NOT fed elsewhere in P5, so that row is DISP without 'also D'.
- After RBW: 46 of 47 EL items gone (no item of their text left); EL[2] (item 9, #2626 'Build Array: Contains unwired or bad terminal') =
  "unknown which item": 1 item with that text is left and its uid is unread. Rows whose EL item(s) are all gone: 48; rows with the unknown item: 4
  (the #2626 rows t4168 t2832 t4160 t4165); rows with no EL item: 23.
- RBW wire per row: the termless/source-only F1 wires map 1:1 to their rows; the one data-carrying deleted wire w25618 (#11261 -> t8323) maps to
  the DISP row t8323, which therefore has no feed in the RBW'd copy.
- Prep: `prep_c167_a1_3_explore.log` (its guess "cdiff 26" was wrong - 31, above; RESULT FAIL 0/1; jev_gate RULE-OFFLINE-CARD), `_scan.log` PASS.
- Duplicates written again (not importable, shared module outside the write globs): Graph json hand-off (diag_c167_a1_2_crows.py:94-104 =
  diag_c166_a1_5_census.py:105-115) and the FS-frame owner-chain step (diag_c167_a1_2_crows.py:109-118,130-147 = census :139-153).
