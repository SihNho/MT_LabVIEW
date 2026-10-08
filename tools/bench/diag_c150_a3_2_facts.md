---
type: facts
status: current
date: 2026-10-08
card: 150-a3-2
---
# Card 150-a3-2 facts: s07 scratch PASS 27/0, ADOPTED b3f86b32; EL 50 (s06 51, pred 52; item 6 GONE); graph 15/0; load_by_vi added
## Before
- `diag_c150_a3_2_inv_before.log` 34/0: 20 card inputs == card md5; stage tools, s06 569ffbf5, s05, s04, s03, bed, graph a3ecb92b, memory_model 8eec443c.
- Scratch `--dry` PASS 1/0 (`diag_c150_a3_2_scr_dry.log`); `--prerun` PASS 16/0, X10 673.7 (margin 6.3/680, 21.3/695), X11 PASS licensed
  (`diag_c150_a3_2_scr_prerun.log:137,155-156,159`); X14 WARN rows 30 / 15 (proven: no). `--check-launch` ALLOW. Same as 150-a3-1.
## Prior art
- guard_cycle REFUSED the first launch: no prior-art review newer than the recipe; DIFF-ONLY vs s06 scratch, 3 substantive lines.
- Ran `prior_art_review.py --slug c150-s07-scratch --diff-from stage_d1_ring_p4_s06v18_scratch.py` (`diag_c150_a3_2_priorart.log`, 37 s):
  ANSWERED `PRIOR-ART: novel` (`archive/peer/2026-10-08-priorart-c150-s07-scratch.md:291`); NOVEL RECORD sha a37b5f90; disposition written (:299).
## Scratch (ONE run) `diag_c150_p4s07v18_scratch.log` RESULT 27/0 (:401), BGRUN END rc=0 after 481 s (:408)
- NEW byte copy of 569ffbf5 = `claudeDev\D1_ring_p4s07_20261008_222709.vi` (K3 :62); saved md5 b3f86b322292a6ec6c67976a589b5b06, 319897 B (S2 :379, PS :381).
- SG :65 two declared gates; SG-p4_rbA_re2 PASS :358 (t9519 'Pos: Diffraction Pattern' on w23807, source t5171 #5058); SG-p4_rbD_sel_t25573
  PASS :359 (t25573 'autofocus reset count (1.2 to 1.1)' on w30597, source t30408 #4586 's? t:f').
- E1 30 ops real == sim :360; NG :361; FR 5 created on [23166] :362; PRIM 5x Select/Function (#30398, #4594, #4590, #4586, #4538) :95,171,233,288,354.
- D :363 new 8 == 8, lost 4 == 4, reuse none; TD :368 renames 0, unlicensed []; PB :370 cdiff == pred 19 rows / 17 open pairs, unlicensed [].
- Licence: no rename happened (TD/PB renames 0, unlicensed []); X11 op 150 licensed at prerun. HB :372 (45999, 46518); H5 20 == 20 :385; H2/H3/H6 PASS.
- Memory: METER start 613.3 MB (:67) vs pred start 599.7 (d +13.6); peak 661.7 MB (:355) vs X10 673.7 (d -12.0); MEM / MEML PASS (:404-405), MEMSTOP not hit.
- CENSUS-ALL net {Function 5, ParameterTerminal 20, Wire 4}, new {Wire 8, ParameterTerminal 19, Function 5}, lost 3 (:365-367). GONE PASS :407.
## Adopt `diag_c150_a3_2_adopt.log` 3/0 (stagexec.adopt_scratch by import)
- Artefact `claudeDev\D1_ring_p4s07_20261008_222709.vi` md5 b3f86b322292a6ec6c67976a589b5b06, input 569ffbf5; adopted_scratch.jsonl -> 450c894c; L PASS.
## Final Error List (elrun wrapper) `diag_c150_a3_2_el.log`: 50 items == window N 50, OCR rapidocr; rc 1 MISMATCH vs s06 expected (extra 1, missing 2)
- Read `errorlist_D1_ring_p4s07_20261008_222709_20261008_223629.json` aa27c138; bed md5 unchanged; handles 37248 -> 31284. Jev: RULE-SAME-ROW discharged (jev_gate.log).
- Expected `errorlist_expected_D1_ring_p4s07_20261008_222709.json` 42c5718d, total 50, 12 entries (`diag_c150_a3_2_elexp.log` 5/0).
  Dropped: 'connected two terminals of different types (new in session 6)' x1; added: 'Select: contains unwired or bad terminal' x1.
- vs s06 51 (elcls): types-differ 2 -> 1; total -1. vs pred 52: input -1, types-differ -1; total -2 (|d| <= 3, no unseen class).
- Raw-class vs s06: IndexArray unwired 3 -> 2, Select unwired 0 -> 1, Local (s07 name) 0 -> 1 / '' 1 -> 0 (OCR name), types-differ 2 -> 1.
- Item 6 'source void -> sink I32': GONE in s07 (s06 read index 6; s07 none).
## Graph `diag_c150_a3_2_graph.log` 15/0, 172 s (prerun 15/0 with --graph graph_ring_p4s06_20261008_192149.json, s149 form)
- `tools/bench/graph_ring_p4s07_20261008_224835.json` md5 71935a845efedd8123044aab288cd81c: 6082 rows, 10600 objs, 25 loops, 23 FS, 71 border tunnels.
- MEM after load 589.4 MB (:24), after read 600.6, after FS 600.7; E5 PASS (5 made Function, 4 deleted wires absent, 8 new present) :299.
- Plan `diag_c150_a3_2_graph_plan.json` ea69bd08 (`diag_c150_a3_2_mkgraph.log` 4/0).
## memory_model `diag_c150_a3_2_memload.log` 5/0: 8eec443c -> b4a6eec6; added /load_by_vi/b3f86b32.../{cite,value 589.4,vi} only; removed [], changed [].
## After `diag_c150_a3_2_inv_after.log` 33/0: all pins unchanged (s06 569ffbf5, s05, s04, s03, bed, stage tools, graph, s07 plan/pred/licence/recipes);
no _elc_/scratch_c150_* left; tasklist LabVIEW count 0. Handles: scratch 34318 -> 46063 (op0) -> 40540 exit; graph 45615 -> 45892, exit 33953.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c150_a3_2_el.log (rc 1 MISMATCH, by design vs s06 file) | RULE-SAME-ROW (c149-a1-2-el51) | none | expected file written from the read | 50 recorded |
OPEN: metered scratch start 613.3 vs pred start 599.7 (+13.6) while peak stayed 12 MB under X10 - recalibrate the s08 start term?
