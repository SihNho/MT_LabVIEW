---
card: 154-a2-1
status: current
date: 2026-10-09
---
# 154-a2-1 facts - DonorQueue_v0.vi BUILT and SAVED (ExecState 1); read-back STOPPED on a script bug; json, handles-after, cold read NOT done

Run: `tools/bench/diag_c154_a2_1_donor.py` -> `tools/bench/diag_c154_a2_1_donor.log` (BGRUN END rc=1 after 68 s; 18 pass / 1 fail).
- Build route: EMPTY_v0 copy -> DonorQueue_v0.vi (diag_c140_5_run.py:29 form); const = create_primitive_nested DonorRingConst_v0 #101;
  Obtain typed from a TEMPORARY Replace Array Subset (DonorRAS1D_v0 #175 'output array') via queue_node, temp node deleted + Remove Bad Wires,
  then connect_term_uid const -> 'element data type'; Enqueue/Dequeue/Release by queue_node from Obtain 'queue out'; const branched to Enqueue 'element'.
- Objects (log lines "PASS C1..Q release"): ArrayConstant #52 (element DigitalNumericConstant #73; source t51 'x,y,z array'; DBL[20] 0.0, NOT empty),
  Obtain #108 ('element data type' t117 <- w82), Enqueue #44 ('element' t89 <- w82), Dequeue #45, Release #46 (all class Function by queue_node delta).
- Wires: W1 / W2 err '' Is Broken? False (w82). Temp RAS #85 gone ({85}), Remove Bad Wires -> (0, 0). ExecState 1. Saved by COM SaveInstrument.
- DonorQueue_v0.vi md5 81dba822efec5226123b3b88ee4383bc (still on disk; json does NOT exist).
- FAIL (script bug, diag_c154_a2_1_donor.py:82): `g.node_labels(DON, 0, strict=False)` rows are lists, indexed x["uid"] -> TypeError.
  Not done therefore: per-object terminal read-back + donor_queue_v0.json, handles AFTER (BEFORE = 34470), cold re-read.
- Close-out: ref_counts opened 9 / closed 9 / live 0; LabVIEW processes 0 (Get-Process); warm scratch deleted; 27 pins unchanged (s09 eb1d0f31,
  7 tools, memory_model, 4 OpQueue*_v0, every Donor*.vi).

OPEN: rerun only the read-back (json + handles + cold read) on the saved donor, or rebuild (script gate S refuses an existing DonorQueue_v0.vi).
