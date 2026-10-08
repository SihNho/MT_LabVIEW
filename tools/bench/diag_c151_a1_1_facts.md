---
type: facts
status: current
date: 2026-10-09
card: 151-a3-1
---
# Card 151-a3-1 (re-issue of 151-a1-1) facts: s08 scratch PASS 22/0, ADOPTED f99e8414; EL 46 (s07 50, pred 48); graph 15/0; load_by_vi 589.1 added
(Card 151-a1-1's FAIL-before-launch facts are in git history of this file and in `result_151-a1-1.json`.)
## Before
- `diag_c151_a1_1_inv_before.log` (2nd segment) 34/0 with stagekit pin 604529e8; addrcheck.py md5 207beb0d before and after (md5sum).
- Scratch `--dry` PASS 1/0 (`diag_c151_a1_1_scr_dry.log`); `--prerun` PASS 16/0, X10 651.6, X14 WARN rows 19 / 15 (proven: no), CENSUS-UNPREDICTED rows 1-19
  (`diag_c151_a1_1_scr_prerun.log`); `--scratch-required` MAIN rc 3 rows 1-19 (`diag_c151_a1_1_scrreq.log`); `--check-launch` ALLOW. All == 150-a3-6.
## Prior art
- Not demanded: the launch went through (guard_cycle / check-launch did not refuse); no prior-art review run.
## Scratch (ONE run) `diag_c150_p4s08v18_scratch.log` RESULT 22/0 (:305), BGRUN END rc=0 after 343 s (:312)
- NEW byte copy of b3f86b32 = `claudeDev\D1_ring_p4s08_20261009_031503.vi` (K3 :62); saved md5 f99e8414a2081538552e26ba24ee713d, 320157 B (S2 :283, PS :285).
- SG 0 declared gates, 0 census rows (:65). L1 19 actions -> 19 ops, checkpoints (0, 6, 13, 14, 19) (:66).
- E1 every checkpoint real == sim, 19 ops incl. action 19 `p4_w_n2_arr` (:264); NG 0 ops (:265); FR 3 created on [23166] (:266).
- PRIM Select #4576 (p4_rbF_sel :124), Select #4577 (p4_rbR_sel :191); Local #30675 (p4_rbR_lr, mkgraph STEPX :223).
- D new 11 == sim 11, lost 5 == 5, reuse none (:267); TD position keys, renames 0, unlicensed [] (:272); PB cdiff == pred 21 rows / 19 open pairs, unlicensed [] (:274).
- Licence: no rename happened (TD renames [] / unlicensed_renames []); per review c151-a1-1-stalepin (c) this list is always [] after T6, so it could not fail.
- Memory: METER start 616.7 MB (:67) vs pred start 595.3 (d +21.4); peak 645.4 MB vs X10 651.6 (d -6.2); MEM / MEML PASS (:308-309), MEMSTOP not hit.
- CENSUS-ALL net {Function 2, Local 1, ParameterTerminal 8, Terminal 1, Wire 6}, lost 2 (:269-271). HB (46001, 46583) :276; H5 16 == 16 :289; IN / GONE PASS :310-311.
## Adopt `diag_c151_a1_1_adopt.log` 3/0 (stagexec.adopt_scratch by import)
- Artefact `claudeDev\D1_ring_p4s08_20261009_031503.vi` md5 f99e8414a2081538552e26ba24ee713d, input b3f86b32; adopted_scratch.jsonl -> 7925d951; L PASS.
## Final Error List (elrun wrapper) `diag_c151_a1_1_el.log`: 46 items == window N 46, rc 1 MISMATCH vs s07 expected (extra 0, missing 4) (:82-84)
- Read `errorlist_D1_ring_p4s08_20261009_031503_20261009_032121.json` b5b9a3f1; bed md5 unchanged; handles 37243 -> 31285; 578.6 s.
- Expected `errorlist_expected_D1_ring_p4s08_20261009_031503.json` c19cde96, total 46, 9 entries (`diag_c151_a1_1_elexp.log` 5/0); added [].
  Dropped s07 entries: Local (#30001/#30016) x1, Shift Register x1, Select 'Select' x1; Index Array 2 -> 1.
- elcls vs pred 48: input -2, total -2. vs s07 50: input -2, local -1, sr -1, total -4. Wire classes 22 / 21 == s07 (no OCR row loss).
- Review `archive/peer/2026-10-09-c151-a3-1-el46.md` (hypothesis, ANSWERED, $1.60): outcome holds; the 2 below pred = Select #4538 (s07-made, wired
  by p4_rbE_t/f/s/out) and IndexArray #29879 (action 19) - planned closures the pred missed because `elrule.predict` got no `carry` (elrule.py:170-177).
- The offline `--el-advisory` mode of the scratch recipe was refused by the adopted-scratch LAUNCH GATE (guard_bash) - not run; the same per-class
  diff is in elexp.log. `gate_fp.py log` for it was refused by the same gate (the command text names the recipe) - NOT queued.
## Graph `diag_c151_a1_1_graph.log` 15/0, 174 s (dry 1/0, prerun 15/0 with --graph graph_ring_p4s07_20261008_224835.json)
- `tools/bench/graph_ring_p4s08_20261009_033522.json` md5 44858dbfa0e77628359f7a86727e250f: 6091 rows, 10618 objs, 25 loops, 23 FS, 71 border tunnels.
- MEM after load 589.1 MB (:25), after read 600.6, after FS 600.6; handles 45644 -> 45926; E5 PASS (3 made, 2 deleted wires absent, 11 new present) :300.
- Plan `diag_c151_a1_1_graph_plan.json` 5a65025e (`diag_c151_a1_1_mkgraph.log` 4/0).
## FS #29721 (`diag_c151_a1_1_fs.log` 2/0): graph records fs_frames (23 FS) and borders (71); FS #29721 frames [29869]; owner of #29869 read ('FlatSequenceFrame', 0)
- 7 rows on #29869 (owner, index, class, name, term, wire): #29879 0 IndexArray 'array' t29882 w30685 | 1 'element' t29885 w0 (src) | 2 'index' t29888 w0;
  #30002 0 'array' t30013 w0 | 1 'element' t30025 w0 (src) | 2 'index' t30028 w0; #30016 0 Local 'Num' t30023 w30685 (src).
- 0 border tunnels of FS #29721 in the graph's borders map.
## memory_model `diag_c151_a1_1_memload.log` 5/0: b4a6eec6 -> a28b6dd7; added /load_by_vi/f99e8414.../{cite,value 589.1,vi} only; removed [], changed [].
## After `diag_c151_a1_1_inv_after.log` 33/0: stagekit 604529e8, stagexec, gscript, elrule, stage_prerun, vigraph, stagesim, errorlist_check, s07 b3f86b32,
s06, bed 39511877, graph 71935a84, s08 plan/pred/licence/recipes, briefs, diag_c150 scripts unchanged; addrcheck 207beb0d; no _elc_/scratch left; tasklist LabVIEW 0.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c151_a1_1_el.log | already-reviewed-class 0.524 (old path) | hypothesis review owed | dispatched c151-a3-1-el46, waited, disposed | ANSWERED; outcome holds |
OPEN: run the review's offline check (elrule.predict with carry {4538,29843,29879,30002,2626} -> 46?) and fix pred `carry` before s09? Metered start +21.4 over pred.
