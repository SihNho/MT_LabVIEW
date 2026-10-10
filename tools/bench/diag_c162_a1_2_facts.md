---
type: facts
status: current
date: 2026-10-10
card: 162-a1-2
---
# 162-a1-2 facts: the ONE step-2 scratch PASSED 20/0 (peak 657.1 <= 675) and was ADOPTED (f9ae7751); EL 53 (pred 51, +2 loose ends); graph + load_by_vi + pred census written; LabVIEW gone.
## Pre-checks (offline)
- Hashes before (diag_c162_a1_2_hash_before.log) 9/0: 25 card inputs equal; s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, p5s02a 94ffff94; stagekit/stagesim/stagexec/stage_prerun pins equal.
- Scratch recipe dry (diag_c162_a1_2_scr_dry.log:86) PASS-UNVERIFIED, unverified 1 = only `CEN2 new-object census ...` (:66); prerun (_scr_prerun.log:109) 16/0, X10 656.2 (:105).
- check_launch FULL command ALLOW (diag_c162_a1_2_checklaunch.log, brief form; _checklaunch2.log, launched form). log file absent before launch (ls).
- DEVIATION 1: the brief's command (`--unverified-card` before `--log`) died in bgrun argparse, rc 2, 0 s, no log written, nothing launched (bgrun has no such option).
  Launched with `--unverified-card` AFTER the recipe path, the form of diag_c156_p5s02a_scratch.log:1,285; check_launch on that exact text = ALLOW first.
- DEVIATION 2 (stated in brief): launch log = recipe constant diag_c161_p5s02b_scratch.log (recipe :29, read at stagekit.py:2836); byte copy diag_c162_p5s02b_scratch.log; both md5 91304eff.
## Scratch diag_c161_p5s02b_scratch.log: RESULT PASS 20/0 (:197), BGRUN END rc=0 after 606 s (:204)
- `SCRATCH-P5S02B peak 657.1 MB (X10 656.2, d 0.9); final ...D1_ring_p5s02b_20261010_105511.vi md5 f9ae7751...; bed md5 94ffff94` (:199)
- `GATE MEM peak <= 680.0 and peak <= X10 + 10: PASS` (:200); MEML/IN/GONE PASS (:201-203). METER start 615.4 MB (:54) vs memory-model start 599.7 (+15.7).
- E1 diff 0 at checkpoints 0,1,2,3,4,5,7,8,9,10 (STEPX :56,68,77,85,94,102,119,128,136,146; op 6 not a checkpoint :111); E1 PASS (:147).
- Ops 5/9 connect_term_uid: STEPX 05 bound {-12: 31593} diff 0 (:102), 09 bound {-24: 31628} diff 0 (:136); SG 0 declared sink gates (:52), so no sink check rows exist.
- L1 20 actions -> 10 ops (:53); NG, FR (0 created), D pairs 12 == sim 12 / lost 2 == 2, re-used uid 24264 noted (:148-150); TD PASS (:155).
- PB PASS by position, 26 slots + 5 RECORDED tag-only rows (376 cal cluster path / error in / file size / selected path / total data array in) (:157-162).
- HB 45936 -> 46362 (:164); PS saved 323850 B (:171-173); H5 9 == 9, H2 input unchanged, H3, H6 only the work copy added (:181-191). No CD / INV gate line in this recipe's log.
- CEN2 UNPREDICTED (:151). MEASURED census: new uids {InnerTerminal 10, OuterTerminal 5, SelectorTunnel 5, Wire 11} (:153); net {.. Wire 7} (:152); lost 4 (:154).
- OPCENSUS op 3 {SelectorTunnel 1, InnerTerminal 2, OuterTerminal 1, wires 2} (:174); op 5 lost_wires 1 (:175); op 7 not measured (:176); op 9 lost_wires 1 (:177).
- term_identity (diag_c161_p5s02b_scratch.json): lost_w [24264, 24285, 24300, 24312]; new 12 incl. re-used 24264; so MERGE wires 24285/24312 were NOT kept (the pred EL text expected uid 24285 kept).
## Adopt diag_c162_a1_2_adopt.log 3/0 (copy of diag_c158_a3_2b_adopt.py, names/input/note only)
- ADOPTED C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p5s02b_20261010_105511.vi md5 f9ae77513a0188f0d88652a44267b1dd (adopt/1 2026-10-10 11:05:49)
## Error List diag_c162_a1_2_el.log (elrun --role final vs 79ec3207): 53 items == window 53 (:27,:89), extra 2 missing 0, SOFT loose-end (:88), verdict OK (:91), rc 0, 708 s
- Read errorlist_D1_ring_p5s02b_20261010_105511_20261010_110607.json a754a08c; bed md5 unchanged; handles 37245 -> 31285.
- Per class: loose ends 23, not connected 22, no source 3, Loop Tunnel undirected 2, input (Build Array) 1, two types 1, While-input-to-SubVI 1 (diag_c162_a1_2_elexp.log).
- vs 79ec3207 (51): extra = 2 x `Wire: Wire has loose ends.`, missing none, no predicted entry dropped; == the pred's alternative_total 53 (A32 w_gr / A39 w_hr each raising one).
  The OCR read carries no uid, so which 2 loose ends (A32/A39 vs un-cleared MERGE A28/A35) is NOT attributed. vs p5s02a 56: no-source -2, not-connected -1.
- Expected file tools/bench/errorlist_expected_D1_ring_p5s02b_20261010_105511.json md5 60e02787 total 53 (diag_c162_a1_2_elexp.log, 5/0).
## Graph diag_c162_a1_2_graph.log 15/0, BGRUN END rc=0 173 s (plan diag_c162_a1_2_graph_plan.json e05f5e4d from _mkgraph.log 4/0; dry PASS, prerun 15/0)
- tools/bench/graph_ring_p5s02b_20261010_111905.json md5 431cfd833310cde7d66a238db3db16f8: 6190 rows, 10796 objs, 25 loops, 23 FS (:307)
- `MEM after load: 601.2 MB private` (:24); E5 PASS: 5 SelectorTunnels 31588/31593/31598/31628/31640, wires 24285/24300/24312 absent, 12 new present (:305).
## memory_model.json (diag_c162_a1_2_memload.log 6/0): 5b87de43 -> def9e640; ONLY added load_by_vi/f9ae7751 {value 601.2, cite diag_c162_a1_2_graph.log:24};
  flattened diff added 3 leaves, removed [], changed []; fail_above_mb 680.0 old == new; memstop/formula/start_mb equal.
## Pred census (prep_c162_a1_2_census.log 4/0, stagekit.scratch_census on scratch log :153): plan_ring_p5s02b_pred.json a1fd43fb -> 4cef0a8c;
  changed keys exactly [census, census_overall (UNPREDICTED -> MEASURED-SCRATCH), census_source]; plan md5 key unchanged; before-copy sim/ring_p5s02b_c162/pred_before_a1_2.json.
## End: hashes after (diag_c162_a1_2_hash_after.log 9/0): s09, P5-1a, P5-1, 94ffff94 and all tool pins unchanged; tasklist LabVIEW count 0. No original opened, no hook/recipe/plan/licence/EL edit.
OPEN: metered scratch start 615.4 MB vs model 599.7 (+15.7); peak stayed within X10 + 0.9 - recalibrate start for the MAIN launch?
OPEN: the 2 extra loose ends are not attributed by uid (A32/A39 raise vs MERGE A28/A35 not clearing); MERGE wires 24285/24312 did not survive as uids.
