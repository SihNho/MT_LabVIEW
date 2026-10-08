---
type: facts
status: current
date: 2026-10-08
card: 150-a3-5
---
# Card 150-a3-5 facts: s08 maker stops at the pass-A simulation, action 20 `p4_x_n2_order` crosses FS #29721, whose diagram is UNMEASURED (FAIL, returned at step 1)
Offline only. No LabVIEW process before or after (`prep_c150_a3_5_check_before.log` / `_after.log`, LV gate PASS). No stage tool, hook or elrule was edited.
There was no `--rebase` and no `--launch`. The card stopped at the first unexpected result, as its rules say. The cause was not diagnosed and nothing was retried.
## 1. Maker (`prep_c150_a3_5_mk.py`, a copy of `prep_c150_a1_1_mk.py`; `prep_c150_a3_5_mk.log` RESULT 11/1, `BGRUN END rc=1 after 21s`)
- Input: s07's SIMULATED end `sim/ring_p4_s07v18/step_30_create.json` c2b902b7. This is the s07 plan's finalized last step, the same route s06->s07 took (END6 step_25_wire). Gate E7 PASS.
- No s08 file existed before, so nothing was byte-copied (gate P PASS). No s07 file was written.
- START 595.3 = `stage_prerun.x10_start(b3f86b32..)` = load_by_vi 589.4 + op-0 5.9 (mk.log X0 PASS).
- Cut by formula: op 190, so the WHOLE remainder fits (ops 166..190, 25 actions `p4_rbE_t`..`p4_rle_x_n2_out`). MAIN 672.5 (margin 7.5 to 680, 22.5 to 695), Executor 667.4.
  - No op is over 680 and the 40-action cap is never reached. No 'of' split.
  - Sensitivity: -5 MB gives op 190 / 667.5; +5 MB gives op 190 / 677.5; +13.6 MB (the s07 start deviation) gives op 186 (21 actions) / 675.6.
- Gates PASS: S7 (v18 ops 1..165 == s01..s07 ids); CM (s06 map `plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl` 99f9d253 header cfbd9823); R 5 s01..s06 symbols -> real uids (SQ1 29724, LRN5 30016, IAN1 29879, IAZ1 30002, TS1 30179).
  - In R, the class in END7 equals the class in sim, and SQ1 == the rebased s07 plan's binding. C2: 14 cross refs, none bad or late. S0: input validates.
- **FAIL `SA pass A replays to its end` (mk.log:53)**: `{'n': 20, 'op': 'wire', 'id': 'p4_x_n2_order', 'error': 'diagram chain: frame #29869 belongs to FS #29721 whose diagram is UNMEASURED (no border outer face, or faces disagree; PD289(f))'}`.
  - Raised at `tools/stagesim.py:1805-1807`. `fs_unmeasured` is set for an FS with no border outer face at `:348-354`.
- The real s07 graph has the same FS: `diag_c150_a3_2_graph.log:296` `FS #29721: frames [29869] (terminating err 'error 1055: Property Node in OpFsDiagrams_v0.vi')`. The same line is in the s04/s05/s06 graph logs (`diag_c145_2_graph.log:296`, `diag_c147_a1_1_graph.log:296`, `diag_c149_a3_2_graph.log:296`).
  - Inference, not run: the "plan's real end" input would meet the same PD289(f) refusal.
  - FS #29721 is the s04-created Flat Sequence: uid re-used, `diag_c144_p4s04v18_scratch.log:172` observed owner Diagram 23166.
## 2. Not run (steps after the failure)
- These did not happen: the plan `plan_ring_p4_s08v18.json` / `_in` were not written; no rebase onto 71935a84; no X10 after the rebase; no pred / V18E-R'; no X11.
- Also not done: sink-gate census, recipes, licence, dry / prerun / `--scratch-required`.
- Written: `sim/ring_p4_s08v18/s07end/base_provisional.json` 982b7244 and the partial `sim/ring_p4_s08v18/_passA/` tree (pass-A steps up to 19).
## 3. Files
- New: `prep_c150_a3_5_probe.py` (read-only probe, log RESULT 1/0: all 11 card inputs == card md5), `prep_c150_a3_5_mk.py`, `prep_c150_a3_5_check.py`, their logs, and `prep_c150_a3_5_md5_before.json`.
## 4. Invariants (`prep_c150_a3_5_check_after.log`: B 145/145, PIN PASS, LV PASS)
- Unchanged: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, dispo 4b456b18.
- Unchanged: VIs s07 b3f86b32 / s06 569ffbf5 / s05 3f9ac26b / bed 39511877; memory_model b4a6eec6; adopted_scratch 450c894c; graphs 71935a84 / a3ecb92b.
- Unchanged: every s07 plan/pred/in/licence/recipe file and the `sim/ring_p4_s07v18` tree.
- The A gate reports exactly ONE changed file: `tools/hooks/material_marker.log` b32b8b4c -> 98c5703d. The guard hook appends to it on every `--material` command, so this card did not edit it. No other `tools/hooks/**` file changed.
## 5. Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c150_a3_5_mk.log | no JEV-LADDER row in jev_gate.log | - | returned | FAIL SA n20 PD289(f) |

OPEN: s08's action 20 (`p4_x_n2_order`) wires into frame #29869 of FS #29721, which every real graph since s04 reads as border-less, so its diagram is unmeasured. Should the simulator get the FS's parent from another measurement (stage-tool card)? Or should s08 be cut before action 20 (19 actions)?
