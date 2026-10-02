---
type: facts
status: current
date: 2026-10-02
---
# Card 140-3 facts — P4 session 1 (v15 #1..#16): plan + scratch PASS; scratch Error List 52 != predicted 51/53 → NO launch
## 0. Review of 140-2's op-3 failure (item 0)
- No JEV-LADDER row existed for `diag_c140_2_scratch.log`; hypothesis review dispatched: `archive/peer/2026-10-02-c140-3-rle1055.md`
  ANSWERED, verdict `unverified` (not refuted): 1055 is from the op's after-read; "whole wire removed" vs "wire replaced" unmeasured;
  fix sound regardless. Disposition written. Side fact: executor FACT line printed err '' while the op returned 1055
  (`diag_c140_2_scratch.log:72` vs `:75`).
## 1-3. Gate, v15, s01 — all PASS
- Gate (`prep_c140_3_gate.log`, 3/0): w23255 = source LoopTunnel #23417 t23435 → sinks only #10171 `x` t23292 / `y` t23283.
- v15 (`prep_c140_3_mkv15.log`, 16/0): `plan_ring_p4_v15.json` eb4ffb6e (185 actions; #2 `p4_dw_23255`, #3 `p4_do_10171`, RLE
  dropped), base without provisional, fs_routes regenerated (5 keys), replay END 186 steps, end cdiff == v14's 24, per-step cdiff equal
  at every other id, route_check PASS, compile 167 == 167, route diff only on the 2 changed ids; meta `plan_ring_p4_v15_meta.json` d012bd2c.
- s01 (`prep_c140_3_s01.log`, 10/0): `plan_ring_p4_s01.json` ff041e6c FINAL (16 actions, 11 open pairs, all 16 end rows bed-declared),
  pred 567daa6e: X10 673.4 (R 11), EL predicted 51 (alt 53).
- Recipes (names only edited): dry PASS both; prerun 15/0 both; X10 launch 678.5 (R 13), scratch 673.4. Prior-art review
  `archive/peer/2026-10-02-priorart-c140-3-p4s01.md` NOVEL (disposed; 140-2's prior-art review disposed too).
## 4. Scratch run (`diag_c140_3_scratch.log`, BGRUN END rc=0, 437 s) — PASS 19/0 + MEM/IN/GONE
- L1 16 ops == pred, E1 every checkpoint == sim, FR, D (new 5 / lost 2 = w23255, w23310), TD, PB cdiff == pred 16 rows, HB 45658→46181.
- CENSUS-ALL net: Comparison −1, Wire +3 (new 5), GrowableFunction +1, Local +4 (new 3), constants +3. Peak private **615.5 MB** (≤ 675).
- Error List (`errorlist_scratch_c140_3.log`, full read, 1021 s, window count 52): **52 items**. rc 1 / MISMATCH only because the
  scratch read has no expected file. Compared with the bed's expected 51 (`diag_c140_3_elcmp.log`): extra 1 =
  "Insert Into Array 'Insert Into Array': Contains unwired or bad terminal", missing 0, all other classes equal.
## 5-6. Launch NOT made (gate: EL == prediction FAILED: 52 not in {51, 53}). No in-between file, no graph read.
- `tools/bench/diag_c140_3_graph.py` (+ needs `diag_c140_3_graph_plan.json`) written for the post-launch read, NOT run.
- Hygiene (`prep_c140_3_cleanup.log` 3/0): scratch deleted, bed md5 395118775a52bc90073f4449b99f899d unchanged, no LabVIEW.
## Review of the EL mismatch — `archive/peer/2026-10-02-c140-3-el52.md`, verdict SUPPORTED (count), with a RULE-1A FINDING
- The 52nd item is the node made by `p4_ras_bufdiff` (plan `prim` "Replace Array Subset", donor `$work` #29157). The review says #29157 is
  a real Insert Into Array (grows the array), the design needs Replace Array Subset, and bed nodes #29265 / #29316 (P3b-2) may carry the
  same defect (`launch_p3b2_c135_b.log:94-103`, `main_vi_node_labels.json:1120`). Test it names: `errorlist_shots/bd_210806_after11.png`
  + #29157's role in the original.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c140_2_scratch.log | (no row) | - | dispatched c140-3-rle1055 | ANSWERED, unverified, not refuted |
| diag_c140_3_elcmp.log | new-problem 0.782 | hypothesis review owed | dispatched c140-3-el52 | ANSWERED, supported + rule-1a finding |
OPEN: is the ring's per-slot write node (donor #29157, and bed #29265/#29316) an Insert Into Array where Replace Array Subset is meant?
