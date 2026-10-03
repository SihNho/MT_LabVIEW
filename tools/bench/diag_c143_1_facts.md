---
type: facts
status: current
date: 2026-10-03
---
# Card 143-1 facts: P4 v18 session 2 - prior-art 3 rounds -> novel, scratch 21/0 PASS, Error List 53 (pred 51/52) = RETURN, not adopted

## Prior-art (step 1)
- r1 `archive/peer/2026-10-03-priorart-c143-1-p4s02v18.md` settled-already (contradicted, helper-exists): scratch stop 690 vs PD328(a) 680;
  no `work_name` (PD329(a)). FIXED: `stage_d1_ring_p4_s02v18_scratch.py:21` (SX.MEM_STOP_MB = SX.X10_FAIL_MB, MEM gate :84), `:73`
  (Stage(work_name="D1_ring_p4s02_<ts>.vi")); log/out names -> diag_c143_1_scratch*.
- r2 `...-r2.md` settled-already: ExecStop handler lacked `SX.save_for_resume` (PD329(b)). FIXED: `stage_d1_ring_p4_s02v18.py:47-51`
  (save_for_resume before report_stop, try/except so the stop report is still written).
- r3 `...-r3.md` **novel**; NOVEL RECORD shas 31d1a272b115 / 13f0772661b3. Release slugs must be the verdict slugs
  (`FIXED: contradicted` / `FIXED: helper-exists`); a review-slug FIXED line was refused by stop_record (first launch attempt).
- Offline after the edits: dry PASS both (`diag_c143_1_dry2.log`, `diag_c143_1_scr_dry2.log`), scratch prerun 16/0 (`diag_c143_1_prerun.log`,
  X10 652.0 by the prerun model, pred 678.5), `--scratch-required` exit 3 CENSUS-UNPREDICTED rows 1..34 (`diag_c143_1_prerun_main.log:3`).

## Scratch (steps 2-3) `tools/bench/diag_c143_1_scratch.log` (BGRUN END rc=0, 478 s)
- RESULT 21/0 (:424) + MEM/MEML/IN/GONE PASS (:427-430). L0, K1-K3, L1 (34 ops, checkpoints 0,7,17,30,31,32,34), PRIM 2/2 (:122,:208),
  E1 34 ops (:383), NG, FR 6 objects (:385), D new 4 / lost 5 (:386), TD (:391), PB 16 rows / 11 open (:393), HB 45657->46173, PS, H2/H3/H5/H6.
- Peak 620.3 MB (X10 678.5, d -58.2) (:426). CEN2 UNPREDICTED (:387, declared {}).
- Saved (gui_save, ExecState 0): claudeDev\D1_ring_p4s02_20261003_110001.vi md5 84cac48781c7c915c8f0d7e8fb079341, 315545 B.
- Bound uids: -2->6869, -8->6859 (Replace Array Subset), -14->6850 BooleanConstant, -16->29516 ControlTerminal 'StopAll' (indicator),
  -18->6899 Local write, -20->6902 Local read (:125,:211,:313,:321,:346,:382).
- Census MEASURED (:389) {BooleanConstant 1, ControlTerminal 1, GrowableFunction 2, Local 2, Terminal 6, Wire 4}, lost uids 19; written into
  `plan_ring_p4_s02v18_pred.json` (518b01b8 -> 67c3bf29) by `diag_c143_1_census.py` 5/0 (`diag_c143_1_census.log`).

## Error List (step 3 prediction) - THE MISS
- `errorlist_c143_1_p4s02.log` (--role final, expected = bed list 51): window count **53**, extra 2, missing 0, verdict MISMATCH, rc 1, 711 s;
  JSON `errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json` 16132ddc (:5638-5642).
- Extra 1: "Local Variable 'D1_ring_p4s02_20261003_110001.vi': This variable is not connected to anything." (item 0; uid not readable -
  Selection List op unbuilt). Candidate: created Local read #6902 (op 34, last op) whose output is wired in a later session (UNVERIFIED).
- Extra 2: "While Loop 'While Loop': Conditional terminal is not wired". Pred alternative was base #23166 term '' newly unwired
  (pred errorlist.base_nodes_newly_unwired) - whether this item is that one is UNVERIFIED (no uid in the item).
- Pred rule PD322(e) counts only created nodes with an unwired INPUT; a Local READ has only an output.

## State
- NOT adopted (adopted_scratch.jsonl untouched); no graph read; no launch. `diag_c143_1_check.log` 5/0: bed 39511877 and s01 dc61e193 unchanged,
  session-2 file 84cac487 unchanged, no _elc_/scratch_c143 file, no LabVIEW.
- Prepared, not run: `diag_c143_1_graph.py` + `diag_c143_1_graph_plan.json` (E5 = 6 made / 4 deleted nodes / 5 deleted wires / 4 new wires).
- JEV-LADDER: no row for errorlist_c143_1_p4s02.log in jev_gate.log.
