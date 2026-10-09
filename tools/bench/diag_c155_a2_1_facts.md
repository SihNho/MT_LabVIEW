---
type: facts
status: current
date: 2026-10-09
card: 155-a2-1
---
# 155-a2-1 facts - P5-1b = actions 21..32 / 8 ops on the REAL P5-1a graph, frame '#30914'; plan, pred, licence, recipes written; dry + prerun PASS; prior-art novel; NOT launched (offline, LabVIEW 0)
## Pins / maker (`prep_c155_a2_1_mk.py` 2c766af9, log `prep_c155_a2_1_mk.log` RESULT 21/0, BGRUN END rc=0 after 36 s)
- M0: graph bd67a511, _in fabc4b9c, P5-1 plan ed6ceb9e, P5-1a plan ed62e8d6, session a50bf0a5, memory_model 386a4cf4, ring-p5.md a4b596f0, stagesim eb99c6ba, stagexec 53e17623, stage_prerun 9decb20f, vigraph a7eb58c7.
- Changes vs prep_c154_a4_1_mk.py e65b41d3 (docstring c1-c4): pins; frame map; every compile gets `owners=stagexec.plan_base_owners({'base': graph ref})` (gate BO: 252 entries == graph owners); OPS gate; the 154-a4-1 probe pass-A dropped.
## Symbol / frame map (log MAP, FRM)
- Same 7 symbols as 154-a4-1: CQ1 -> #30726, CQ1.f1 -> #30922, EQ1 -> #30756, QO1 -> #31258, SN1R -> #30996, TC1 -> #31175, TC2 -> #31186 (MAP PASS).
- FRM, 4 ends (w_false_pass TC1/TC2, w_q_false TQ1/TQ2): 'False' = index 0 of c_case frames ['False','True'] -> new:CQ1.f0 -> sim -18 -> bound #30914; `stagesim.base_case_frames(owners, 30726)` = [30914, 30922], [0] == 30914: True.
## Compile vs brief item 4 (log FACT OPS, gate OPS PASS)
- 8 ops: case_frame_wire [1] (case 30726, '#30914', index 0, new_wire); create [2]; connect [3]; add_sr [4]; connect [5]; connect_term_uid [6,7,8] and [9,10,11] (register_end_case_border, case 30726); case_frame_wire [12] (same frame). Kinds and act groups == P5-1 ops 15..22.
## Cut / replay
- Start 608.5 = x10_start(2482fe7b) = 602.6 (load_by_vi, diag_c154_a3_3_graph.log:24) + op-0 read 5.9 (stage_d1_ring_p3b1.log:42-43). Per-prefix MAIN 637.4 .. 657.2; n* = 8 of 8, all 12 actions, k 12 <= 40, remainder none.
- Pass A `sim/ring_p5s01b/_passA/` 13 steps, failed null, 0 PROVISIONAL. REALSIM `sim/ring_p5s01b/step_00_base.json`..`step_12_wire.json`: FINAL, route check PASS, fs_border_gate PASS, open_rows_match, 0 PROVISIONAL; states == pass A at 13 steps.
- TIE: 21 end rows, all step-0 declared P5-1a open rows (19 pairs); none made by a P5-1b action. X8 clean, X17 PASS (0 primitive creates), SG census 0 rows.
## Pred (`prep_c155_a2_1_pred.py` 20726b40, log RESULT 11/0)
- RB/RB2 base = graph bd67a511, vi 2482fe7b; C 12 actions -> 8 ops; X1 608.5 == prerun == maker; Executor 652.1, MAIN 657.2, margin 22.8; MEMSTOP margin 37.8.
- E1 6 checkpoints [0,2,4,6,7,8], each a step file + md5. VG a7eb58c7 (D/TD/PB position key). Census UNPREDICTED (12 rows), census {}.
- OPEN-NEW 1: QS1R (RightShiftRegister) outer source unwired at the sim end.
- EL vs base 47 (aee0d9fe, read 286e7c12 47 items): elrule no carry 47, carry 47; new 0, closed 0. Per class start = predicted: input 2, tunnel-missing-assignment 1, not-connected 22, loose-ends 21, two-types 1. Non-gating.
- Brief hand prediction 45 (tunnel -1, Enqueue 'queue' input -1) recorded in pred `errorlist.brief_hand_prediction`; P5-1a offsets (read - elrule: input -2, tunnel +1) in `p5s01a_measured_offsets`. elrule sees neither closing: both nodes are base nodes, not created here.
## Licence / X11 (`prep_c155_a2_1_licence.py` d286d438, log 5/0; `prep_c155_a2_1_x11.log` CLEAN)
- renames 0, rename_by_uid 0. Base sinks wired NOT by term_uid (outside the rule, printed only): w_false_pass dst #31186 inner '#30914', w_qi_enq dst #30756 'queue'.
## Recipes = stage_template_ring pair shape (stagekit.RingSession, census_all_install, pred_x10, scratch_offline_modes, scratch_tail), not a copy of the P5-1a pair
- Main dry PASS 1/0 (coverage 35/36, first mutation wire_case_frame_wire); prerun PASS 16/0 (`prep_c155_a2_1_prerun.log`): X10 :78-80 N 8, BIND 4, R 8, peak 657.2, Executor 652.1; X17 PASS :69; X14 INFO rows 12, budget 15, proven: no :81; CENSUS-UNPREDICTED advisory :71.
- Scratch dry PASS 1/0, prerun PASS 16/0. `--scratch-required` rc 3 (CENSUS-UNPREDICTED rows 1..12). `--check-launch` scratch: ALLOW rc 0. NOT launched.
- PB behaviour differs from the P5-1a recipe: by POSITION (stagekit.pb_check), as the template states.
## Prior-art (`archive/peer/2026-10-09-priorart-priorart-c155-a2-1-p5s01b.md`, 47 s): `PRIOR-ART: novel`; no waiver (no PROVEN-PATTERN line). NOVEL RECORD for stage_d1_ring_p5s01b.py.
- Its alternative: base-case R1/R2 may not give ONE SelectorTunnel in LabVIEW (measured only on a plan-made case, diag_c124_p3a_scratch.log:53,61); test = the scratch run.
## Files (md5)
- plan_ring_p5s01b.json 75a77a00; _in 114b3159; _pred 2f2cbcc3; _licence e592cf7a; stage_d1_ring_p5s01b.py 6de2378d; _scratch.py 9233749f; session prep_c155_a2_1_session.json 79447fab.
- Invariants `prep_c155_a2_1_inv_before.log` / `_after.log`: 177 files, before == after, pins PASS. LabVIEW processes 0 before and after.
## Duplicate blocks across the prep_c154_* makers (not extracted; my makers still copy them)
- OPEN: gate(): prep_c154_a3_2b_mk.py:56, _pred.py:71, _licence.py:45, _inv.py:47, prep_c154_a4_1_mk.py:58, _inv.py:53, prep_c154_a3_2_mk.py:55.
- OPEN: step_facts: prep_c154_a3_2_mk.py:166, prep_c154_a3_2b_mk.py:119, prep_c154_a4_1_mk.py:222. TIE loop: same files :186 / :139 / :241 (from prep_c152_b2_1_mk.py:337-350). SG census: :248 / :201 / :301.
- OPEN: X10 MAIN formula main_of: prep_c154_a3_2b_mk.py:84, prep_c154_a4_1_mk.py:196 (+ pred :105-107). Symbol map refs/sub + STEPX bound parse: prep_c154_a4_1_mk.py:83-145 (+ selftest_c155_basecase_frame.py:69-70).
- OPEN: copies of shared functions: elcls/norm_ocr prep_c154_a3_2b_pred.py:53-68 (= stagekit.el_class, used here); licence_renames prep_c154_a3_2b_licence.py:22-31 (= stagekit.licence_renames, used here).
