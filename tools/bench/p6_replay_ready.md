---
type: facts
status: current
date: 2026-10-12
card: 167-a1-4
---
# P6-2 replay readiness (PD404(g), docs/d1/ring-p6.md:87-90) - facts only, no design, no verdict
Written by `tools/bench/diag_c167_a1_4_ready.py` (offline; LabVIEW reads 0). Machine-readable: `tools/bench/p6_replay_ready.json`. Graphs: P5 final `tools/bench/graph_ring_p5s02e_20261012_173009.json` (md5 field 75773b0ded2a08586bb1a542ddda5af6), S1 `docs/wiki/subvi/D1_s1_copy.json`. unread = no stored read holds the value.

## 1 - swap sites (by S1 uid; the recipe resolves them BY UID, not by label)

| uid | S1 callee (src) | recipe route (src) | in 7815af09? | P5 class / loop / frame diagram | same terminal names S1 vs P5 | same wire partners | other P5 SubVI with the same terminal signature | P5 src |
|---|---|---|---|---|---|---|---|---|
| #6810 | get buff image-lost frames.vi (docs/wiki/subvi/D1_s1_copy.json:89810 graph_summary.subvi_calls[node_uid=6810]) | uid (plan swaps[].uid -> replace_object(path, uid, new); A2 census checks basename(callee) == old_callee) (tools/recipes/stage_replay_swap.py:30; tools/recipes/stage_replay_swap.py:39; tools/recipes/stage_replay_swap.py:44) | present (same uid) | SubVI / 1.1 / [639] owner [["WhileLoop", 637]] (S1 diagrams [639]) | True | False {"Image Out": {"s1": ["#5058 SubVI 'Image In'"], "p5": ["#28565 SelectorTunnel 'Image Out'"]}, "current image number": {"s1": ["#1605 LoopTunnel 'current image number'", "#2179 SelectorTunnel 'current image number'", "#3078 SelectorTunnel 'current image number'", "#5119 Function 'x'", "#639 Diagram 'current image number'"], "p5": ["#1605 LoopTunnel 'current image number'", "#2179 SelectorTunnel 'current image number'", "#26879 Comparison 'x'", "#27039 RightShiftRegister 'current image number'", "#28512 SelectorTunnel 'current image number'", "#3078 SelectorTunnel 'current image number'", "#5119 Function 'x'", "#639 Diagram 'current image number'"]}, "error out": {"s1": ["#649 LoopTunnel 'error out'"], "p5": ["#28785 SelectorTunnel 'error out'", "#649 LoopTunnel 'error out'"]}} | none | tools/bench/graph_ring_p5s02e_20261012_173009.json objs[uid=6810] + terminals[owner_uid=6810]; unread (P5 graph stores no SubVI names: graph_summary.subvi_calls absent) |
| #22692 | NI_Vision_Acquisition_Software.lvlib:IMAQdx Get Image.vi (docs/wiki/subvi/D1_s1_copy.json:90152 graph_summary.subvi_calls[node_uid=22692]) | uid (plan swaps[].uid -> replace_object(path, uid, new); A2 census checks basename(callee) == old_callee) (tools/recipes/stage_replay_swap.py:30; tools/recipes/stage_replay_swap.py:39; tools/recipes/stage_replay_swap.py:44) | present (same uid) | SubVI / None / [22650] owner [["Sequence", 22541]] (S1 diagrams [22650]) | True | True {} | none | tools/bench/graph_ring_p5s02e_20261012_173009.json objs[uid=22692] + terminals[owner_uid=22692]; unread (P5 graph stores no SubVI names: graph_summary.subvi_calls absent) |

## 2 - how the 110 replay legs treated the motors (they were NOT kept off)

| fact | source |
|---|---|
| card 110-6 launched nothing (status BLOCKED): 'Nothing launched: no swap copy saved, no replay leg run, no compare; LabVIEW not running at exit' | tools/bench/cards/result_110-6.json facts[7] |
| the two replay legs ran under card 110-7 (drive_m8_replay_110.py, 15/0) | tools/bench/cards/result_110-7.json facts[5] (R3) |
| only #6810 and #22692 (camera) are swapped; no motor call site is in any plan's swaps | tools/bench/plans/plan_replay_swap_110.json swaps |
| leg chain: drive_m8_replay_110 -> diag_c104_leg -> drive_m8 --leg replay_s1 -> v5.main() (runs the swapped copy) | tools/bench/drive_m8_replay_110.py:41; tools/bench/diag_c104_leg.py:33; tools/bench/diag_c104_leg.py:175; tools/bench/drive_m8.py:99 |
| before each leg: VISA open+close of 'Rotor' and 'ASRL5::INSTR' (no byte sent); nonzero status refuses the leg | tools/bench/drive_original_copy_v5.py:540; tools/bench/drive_legguard.py:15; tools/bench/drive_legguard.py:34; tools/bench/drive_m8_replay_110.py:36 |
| before Run: `motor_gate.py --session start` (v5 G0); comment: running the copy executes the original's device init, which drives the PI stage and the ASI; gate exit != 0 refuses the run | tools/bench/drive_original_copy_v5.py:550; tools/bench/drive_original_copy_v5.py:554; tools/bench/drive_original_copy_v5.py:560; tools/bench/drive_original_copy_v4.py:205; tools/bench/drive_original_copy_v4.py:210 |
| after the run: LabVIEW must be gone (G92), then a post-run TMX? read through the gate (G93 TMX? == 39) | tools/bench/drive_original_copy_v5.py:715; tools/bench/drive_original_copy_v5.py:719; tools/bench/drive_original_copy_v5.py:723 |
| the scripts' scope headers say `hardware: none` although the legs pass through the motor gate | tools/bench/drive_m8_replay_110.py:103; tools/bench/diag_c104_leg.py:237; tools/bench/drive_m8.py:150 |
| leg A_S1replay_a1: motor_tmx_after 39.0, lost 0, v5_failing ["run1.L6", "run1.L8"], run_dir files {"cal001": 857376, "tra001-000": 1706560} | tools/bench/t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json facts / m8 |
| leg B_dispreplay_a1: motor_tmx_after 39.0, lost 0, v5_failing ["run1.L8"], run_dir files {"cal001": 857376, "tra001-000": 3282880} | tools/bench/t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json facts / m8 |
| v5 json (last writer, mtime 2026-09-27 19:09:30): step '0p VISA precheck: open+close Rotor/ASRL5::INSTR before Run (no byte, no attribute)' ok True - bypassed=False dry=False [('Rotor', '0x00000000'), ('ASRL5::INSTR', '0x00000000')] | tools/bench/m8_v5_replay_s1_p15_r120.json:9 |
| v5 json (last writer, mtime 2026-09-27 19:09:30): step '0 G0 motor gate --session start (BEFORE LabVIEW opens COM3/COM4)' ok True - exit=0; LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0; REFSTATE RON=1 FRF=1 POS=0 POS_BEFORE=0 ERR=0 travelled=0.000; SESSION START OK -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\motor_session.json | tools/bench/m8_v5_replay_s1_p15_r120.json:16 |
| v5 json (last writer, mtime 2026-09-27 19:09:30): step '92 G92 LabVIEW exited before the motor port is touched' ok True - waited 255s; forced kill used=True; running now=False | tools/bench/m8_v5_replay_s1_p15_r120.json:184 |
| v5 json (last writer, mtime 2026-09-27 19:09:30): step '93 G93 post-run TMX? still 39' ok True - TMX?=39.0 from 'PRELIMITS TMN=0 TMX=39'; gate exit=0; LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0; REFSTATE RON=1 FRF=1 POS=-5E-05 POS_BEFORE=30 ERR=0 travelled=30.000 | tools/bench/m8_v5_replay_s1_p15_r120.json:191 |

## 3 - saved files compared

| item | value | source |
|---|---|---|
| files compared | tra* (first sorted file starting 'tra' in each run_dir); cal* (first sorted file starting 'cal'); other files: not compared (only tra*/cal*); TIFFs deleted by v5 cleanup | tools/bench/m8b_replay_compare.py:16; tools/bench/m8b_replay_compare.py:18; tools/bench/drive_original_copy_v5.py:688 |
| X/Y/Z 'bit-identical' meaning | by VALUE bits per f64 cell (u8 view) over columns 3.. of the first n = min(rows_A, rows_B) rows; not file bytes | tools/bench/m8b_replay_compare.py:35; tools/bench/m8b_replay_compare.py:36; tools/bench/m8b_replay_compare.py:45 |
| cal meaning | BYTE compare (md5 + first differing byte offset); recorded in R['cal'], NOT in the gates dict G | tools/bench/m8b_replay_compare.py:26; tools/bench/m8b_replay_compare.py:47; tools/bench/m8b_replay_compare.py:50 |
| 110-7 tra result | {"rows_s1": 4443, "rows_s3": 8548, "common": 4443, "identical_prefix": 4443, "rows_xyz_not_bit_identical": 0, "max_abs_diff_xyz": 0.0, "trans_rot_rows_differ": 114, "nan_rows_s1": 4443} | tools/bench/m8b_replay_110.json |
| 110-7 per-column rows differ (non-zero) | {"1": 114, "2": 1} (col 0 time/frame, 1 trans, 2 rot) | tools/bench/m8b_replay_110.json per_column_rows_differ; tools/bench/drive_m8_replay_110.py:73 |
| 110-7 cal result | {"md5_s1": "e5570a96b7dfd4f68247c29b66e02533", "md5_s3": "ea1ed8a3774e852e6ea1d1819c45a456", "len": [857376, 857376], "first_diff_offset": 857296} | tools/bench/m8b_replay_110.json cal |
| 110-7 gates | {"G1 both tra parse (dims, LE header length prefix, exponent byte at pos 7)": true, "G2 >= 1000 common rows": true, "G3 X/Y/Z bit-identical over the common rows": true} | tools/bench/m8b_replay_110.json gates |

## 4 - missing pieces for pointing the chain at a ring file (facts, no design)

| id | fact | source |
|---|---|---|
| X1 | swap sites in 7815af09: #6810 present=True class=SubVI loop=1.1 same_terms=True same_partners=False; #22692 present=True class=SubVI loop=None same_terms=True same_partners=True; callee names in P5 unread | tools/bench/graph_ring_p5s02e_20261012_173009.json objs/terminals; this file 'sites' |
| X2 | files tools/bench/*ring* whose bytes hold either swapped callee name: ['tools/bench/build_ringpickslot_v0.py']; of these, stored reads (.json/.log): none | glob tools/bench/*ring* content search (this script) |
| X3 | P5 SubVI call sites with no S1 call row (new or re-created uids, callee unread): 4 [{'uid': 9317, 'diagrams': [32464], 'loop': None, 'terms': ['', 'Image Dst', 'Image Dst Out', 'Image Src', 'error in (no error)', 'error out']}, {'uid': 23099, 'diagrams': [23169], 'loop': None, 'terms': ['', 'Border Size', 'Image Name', 'Image Type', 'New Image', 'error in (no error)', 'error out']}, {'uid': 29719, 'diagrams': [29699], 'loop': 'while#16483', 'terms': ['', 'Num', 'found', 'last', 'min Num', 'min slot']}, {'uid': 29724, 'diagrams': [23166], 'loop': '1.2', 'terms': ['', 'Latest', 'discards', 'last', 'n1', 'n2', 'next discards', 'next last', 'valid']}] | tools/bench/graph_ring_p5s02e_20261012_173009.json objs[class=SubVI] minus docs/wiki/subvi/D1_s1_copy.json graph_summary.subvi_calls[].node_uid |
| X4 | S1 SubVI call rows whose uid is not a SubVI obj in P5: 5 [7774, 9944, 14858, 19705, 28233] | docs/wiki/subvi/D1_s1_copy.json graph_summary.subvi_calls minus tools/bench/graph_ring_p5s02e_20261012_173009.json objs[class=SubVI] |
| X5 | recipe loads only the named plans 78/95/110 (a ring plan is not among them) | tools/recipes/stage_replay_swap.py:22 |
| X6 | driver hard-codes the S1 replay copy D1_s1_replay_20260925_075422.vi + md5 126f8497 and reads stage_replay_swap_110.json for leg B's md5 | ["tools/bench/drive_m8_replay_110.py:20", "tools/bench/drive_m8_replay_110.py:19"] |
| X7 | driver writes card label 110-7 and INDEX text naming the display-loop VI | ["tools/bench/drive_m8_replay_110.py:80", "tools/bench/drive_m8_replay_110.py:86"] |
| X8 | leg runner forces drive_m8 --leg replay_s1 and reads m8_replay_s1_p<N>_r<S>.json; drive_m8 accepts replay_s1/replay_s3 only | ["tools/bench/diag_c104_leg.py:33", "tools/bench/diag_c104_leg.py:176", "tools/bench/drive_m8.py:68"] |
| X9 | drive_m8 M7 checks fixed md5s of BED/S3/ORIG/S1 and the leg source | tools/bench/drive_m8.py:121 |
| X10 | compare gates X/Y/Z only (G1-G3); cal bytes and other saved files are not gated; PD374(f) asks 'the saved files bit-identical' | ["tools/bench/m8b_replay_compare.py:50", "docs/d1/ring-p5.md:70"] |
| X11 | 110-7 cal files differ: len [857376, 857376], first differing byte offset 857296 | tools/bench/m8b_replay_110.json cal |
| X12 | recorded-frame source = G:\m8_replay_frames (exists True, manifest exists True); stand-in frame = f(k mod 10044), k = the stand-in's own call counter (uninitialised SR); buf stand-in BN Out = BN In, cal stand-in BN Out = k | ["tools/bench/diag_replay_frames.py:2", "tools/bench/diag_replay_standins.py:9", "tools/bench/diag_replay_standins.py:8"] |
| X13 | replay VIs on disk vs plan pins: {'replay_get_buff_image.vi': '842ecad9 ==pin', 'replay_get_image_cal.vi': 'afce0d04 ==pin', 'replay_imaqdx_get_image_buf.vi': 'a89dafc1 ==pin', 'D1_s1_replay_20260925_075422.vi': '126f8497 ==pin'} | ["tools/bench/plans/plan_replay_swap_110.json swaps[].new_md5, extra_pins"] |
| X14 | no ring file D1_ring_p6_*.vi exists under claudeDev yet: none | glob C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p6_*.vi |
| X15 | the swap uids are taken from S1 graph rows; the recipe's A2 gate is fatal if a uid's callee basename differs | tools/recipes/stage_replay_swap.py:40 |
