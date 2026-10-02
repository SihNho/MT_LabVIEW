---
type: facts
status: current
date: 2026-10-02
---
# Card 140-2 facts — P4 LabVIEW session 1 (v14 #1..#16): plan + recipes PASS offline; the ONE scratch run FAILED at op 3; NO launch
## 1. Plan (item 1) — PASS 10/0 (`prep_c140_2_s01_r3.log`)
- `plan_ring_p4_s01.json` 6fa94e2e (in 571a636e, pred 6ae28374), maker `prep_c140_2_s01.py` (copy of `prep_c139_7_s1.py`): 16 actions
  `p4_dw_23310`..`p4_w_b_out`, no `of` pair / new: symbol crossing the cut (op 17/18 = x_i_rab1 / rle_i_rab1 stay together), FINAL, route
  PASS, 16 end-cdiff rows all bed-declared (0 made by session 1), 11 open pairs.
- v14's top-level base carries a STALE `provisional: true` + sim_of plan_ring_p3b2b (also v10..v13, p4s1); its path IS the real read
  `graph_ring_p3b2b_20261002_133824.json`. `check_launch` (`stage_prerun.py:4033-4039`) refuses it; `--rebase` refused too ("created
  objects differ ... x0 simulated vs x2 real", `prep_c140_2_s01_r2.log`). Maker drops the flag for THIS plan only, gate PV on measured
  evidence (`diag_c136_1_graph.log:8,300,315,331` K1/WROTE 50595c62/H2/rc 0, bed md5 now 39511877, 0 negative uids). Review
  `archive/peer/2026-10-02-c140-2-provisional-base.md`: core claim not refuted; its header-string criticism applied. Its "What was done"
  section is NOT filled (archive/peer is outside this card's write flags).
## 2. Recipe + checks (item 2)
- `tools/recipes/stage_d1_ring_p4_s01.py` (90 lines) + `_scratch.py` (82), copies of the p4s1 pair, names only. Prior-art review NOVEL
  (`archive/peer/2026-10-02-priorart-c140-2-p4s01.md`).
- dry PASS (`prep_c140_2_dry_r3.log`), prerun PASS 15/0 (`prep_c140_2_prerun_r3.log`); scratch dry/prerun PASS (`prep_c140_2_scr_dry_r3.log`,
  last run of `prep_c140_2_scr_prerun.log`). `--scratch-required` = SCRATCH-REQUIRED rc 3 (CENSUS-UNPREDICTED rows 1..16, `prep_c140_2_scrreq_r3.log`).
- X10 at measured start 606.1: Executor-only R 11 **673.4** (== PD320); the LAUNCH recipe's prerun adds its own 2 census reads
  (`census_snapshot@28x2`) => R 13 **678.5 MB > 675** card limit (<= 690 fail) (`prep_c140_2_prerun_r3.log`). Scratch prerun shows 673.4.
- Error List predicted at session end: **51** (alternative 53 = + 2 unwired created sinks of p4_ras_bufdiff `index`, `new element/subarray`).
## 3. Scratch run (item 3) — FAIL 10/2 (`diag_c140_2_scratch.log`, BGRUN END rc=1 after 174 s)
- L0, K1-K3, L1 (16 ops == pred) PASS. Op 1 `delete_wire` w23310 and op 2 `delete_object` Comparison #10171 (err '', node 664 -> 663,
  `:63-67`) ran. **Op 3 `wire_remove_loose_ends` w23255 STOPPED (E1)**: `{'echo': 23255, 'broken_before': True, 'broken_after': False,
  'err': 'error 1055: Property Node in OpWireRemoveLooseEnds_v0.vi'}` (`:72-75`); the op's own call returned err '' in 1.8 s.
- Peak private 585.2 MB (k 0 read; X10 673.4; nothing past op 3). MEM PASS, bed md5 unchanged PASS, LabVIEW gone PASS (tasklist 20:33
  empty), scratch deleted (H4/H6 PASS), refs 4/4 closed (H5). No census, no PB, no save, so NO Error List read.
## 4-5. Launch / after-launch NOT RUN (needs an all-PASS scratch). No in-between file, no graph read. Reviews + gate records:
- `archive/peer/2026-10-02-c140-2-failed-logs.md` (hypothesis): covers prep_c139_7_s1.log X10 750.7 (owed from 139-7; claim 1 says the
  X10 provisional fallback is a code path to watch), the r2 stale-pin L0 failures, and `--scratch-required` rc 3.
- gate-fp **fp-34** logged: guard_peer counts `--scratch-required` rc 3 (a verdict) as a failed run (6th such log).
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c140_2_s01_r2.log | new-problem 0.734 | hypothesis review owed | dispatched c140-2-provisional-base | ANSWERED, not refuted |
| prep_c139_7_s1.log | new-problem 0.656 | hypothesis review owed | dispatched c140-2-failed-logs | ANSWERED |
| diag_c140_2_scratch.log | (no row yet at 20:33) | - | returned per chat-P2 | - |
OPEN: op 3's RLE of w23255 after op 2 deleted #10171 (error 1055 on the wire ref, broken_after False) - plan order or op behaviour?
