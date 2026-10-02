---
type: facts
status: current
date: 2026-10-02
---
# Card 141-3 facts: P4 session 1 retried with identity-keyed gates - scratch PASS, launch PASS, in-between file saved and read
- Item 1 owner check `prep_c141_3_owner.log` 6/0: 28004/28979 = 'output array' of #27928/#28916 in the base graph, both nodes deleted (:109,:195 of the 141-2 log); in the scratch they are #6942 t0 'array' and #6805 t2 'new element/subarray' (141-2 log :167,:267).
- Item 2: `tools/stagekit.py` term_key / wire_keys / term_identity_gates (TD, unwired, D keyed by (uid, owner uid, name); wires by uid + source identity); recipe `stage_d1_ring_p4_s01.py:64` uses it and dumps real_end_rows.
- Self-test `selftest_td_key_c141_3.log` 9/0: old raw key reproduces 141-2's FAIL exactly; new key PASS on it; a lost terminal FAILS; a loss masked by uid re-use is blind to the old key and FAILS the new one; recycled wire uid fixed in D. c125_1 rerun `c125_1_offline_measure_c141_3.log` 6/0.
- Item 3: pred census from 141-2 log :278 = {GrowableFunction 3, Terminal 9, Wire 2} (`prep_c141_3_census.log` 5/0, pred md5 5d70ae63). Dry 1/0 + prerun 16/0 for both recipes (`prep_c141_3_{dry,prerun,scr_dry,scr_prerun}.log`).
- Prior-art gate refused the edited recipes (released shas changed); fresh review `archive/peer/2026-10-02-priorart-c141-3-p4s01.md` = novel (notes uid re-use was already on file, vi-scripting.md:601), disposition written.
- Scratch rerun `diag_c141_p4s01_scratch2.log` 23/0 + MEM/MEML/IN/GONE PASS: E1, PRIM 3/3, D 2/2, CEN2 PASS (:281), TD PASS (:285), PB 16 rows; peak 601.7 MB (X10 669.3).
- Scratch Error List `errorlist_scratch_c141_3.log`: count 51 == pred 51 (window's own count); log ends rc=1 'MISMATCH' because no expected file is passed in count-only mode (all 51 'extra'), same as 140-3's.
- Launch `launch_c141_p4s01.log` 23/0, rc 0: saved claudeDev\D1_ring_p4s01_20261002_232547.vi md5 dc61e193e0376ce760f88fdfcda7087b (:276); handles 45626 -> 46036; peak 605.0 MB (X10 674.4); uids identical to the scratch (#29407/#6942/#6805).
- Full Error List `errorlist_launch_c141_p4s01.log` rc 0: 51 items, extra 0 / missing 0 vs errorlist_expected_D1_ring_p3b2b_20261002_130007.json, verdict OK.
- Graph read `diag_c141_3_graph.log` 15/0: MEM after load 596.5 MB, after full read 607.3 MB; graph tools/bench/graph_ring_p4s01_20261002_234419.json md5 f697a0b2 (5967 rows, 10398 objs, 22 FS); E5 edits present.
- Cleanup `diag_c141_3_cleanup.log` 5/0: scratch deleted, bed md5 395118775a52 unchanged, in-between md5 unchanged, no _elc_/scratch file, no LabVIEW.
- X10 over-predicted a 3rd time (scratch 601.7 vs 669.3, launch 605.0 vs 674.4; 140-3 615.5 vs 673.4) - PD323(c)'s 3 points now exist.
