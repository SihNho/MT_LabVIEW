---
type: facts
status: current
date: 2026-10-09
card: 152-a2-2
---
# Card 152-a2-2 facts: discriminator EQUAL; op 185 now simulates, but the simulator REFUSES op 187 (`p4_x_slot_fs`, LoopTunnel source crossing into FS #29721); RETURNED
Offline only; no LabVIEW before or after (`prep_c152_a2_2_check_before.log` / `_after.log`, LV PASS). No stage-tool, hook or elrule edit, no `--launch`. NO s09 plan / pred / licence / recipe written.
## 1. Discriminator (PD368(d)) - `prep_c152_a2_2_probe.log:13-22`, gate D PASS
- (i) measured: `diag_c152_a1_1_owner.log:25` FS #29721 -> 'Diagram' #23166, echo 'FlatSequence'#29721 == derived e26b4d90 `fs_owner_read['29721']` (:13-14); stagesim c24bd39a `base_state(derived)` owners[29721] ['Diagram', 23166], fs_unmeasured [2499, 14682, 43914] (:15).
- (ii) hops: creation map `plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl:36` real #29721 <- sim -30 ids ['p4_fs_n2'], owner_real 23166 (:17) -> v18 action #85 p4_fs_n2 `diagram` 23166 (`plan_ring_p4_v18.json:1130-1133`), a numeric BASE uid, so no symbolic / rebase hop (:18, :20) -> rebased s04 plan f349c39a same, diagram 23166 (`plan_ring_p4_s04v18.json:255-258`) -> graph 44858dbf #23166 = Diagram owned by WhileLoop #10170 (:21). Equal: 23166 == 23166.
## 2. Maker `prep_c152_a2_2_mk.py` - `prep_c152_a2_2_mk.log` RESULT 13/1, rc 1 (:40-41)
- Copy of `prep_c151_a3_2_mk.py` 04a5cab3. Changes are listed in docstring (c1)-(c4):
  - Card id, session file, and new sub-dirs `_passA152` / `_realG152` (151-a3-2's records are kept).
  - REALSIM runs on derived e26b4d90.
  - Gate P accepts the 12 files 151-a3-2 left in sim/ring_p4_s09v18 (no plan among them) (:4-5).
  - **(c4) NOT a names-only change:** the provisional base = END8 + the measured owner (gate PV, :10-11). Only keys `fs_unmeasured` and `owners['29721']` differ. File `sim/ring_p4_s09v18/s08end/base_provisional_fsowner.json` fd84b364.
  - Why (c4): pass A on the provisional base had refused op 185 before (`prep_c151_a3_2_mk.log:36`). The rebase's `carry_fs` carries only negative-uid owners (`stage_prerun.py:4215-4217`).
- START 595.0 = 589.1 + 5.9 (:6). Cut = op 190, the whole remainder: 6 actions, ops 185..190, tail [] (:14, :27).
  - X10 MAIN 638.4, Executor 633.3; margin 41.6 to 680 and 56.6 to MEMSTOP (:20).
  - Sensitivity +13.6 MB: MAIN 652.0, margin 28.0. +21.4 MB: MAIN 659.8, margin 20.2. Both keep cut 190 (:18-19).
- R 4 symbols -> real: IAZ1 #30002, IAN1 #29879, SQ1 #29724, TS1 #30179 (:35). C2: 5 refs, 0 s08-provisional (:36).
## 3. Simulator on ops 185..190: op 185 PASSES now, op 187 REFUSED (SA FAIL, :39)
- Pass A on the patched provisional base and REALSIM on derived e26b4d90 give the same result:
  - n1 `p4_x_n2_order` (op 185) and n2 (op 186, remove loose ends) PASS.
  - n3 `p4_x_slot_fs` (op 187) FAILS (:38-39; step files `_passA152/ring_p4_s09v18a/step_03_wire.json`, `_realG152/.../step_03_wire.json`).
- Refusal, verbatim: `wire {'uid': 30179, 'term': 'outer'} -> {'uid': 29879, 'term': 'index'}: source 'min slot' on a LoopTunnel - UNMEASURED tunnel naming for that owner class (card 131-1, fs_tunnel_naming_table.json)`
  - Raised at `tools/stagesim.py:1892` (`_cross_tunnel_name`). Measured source classes: named = SubVI/Property/Local/Diagram, empty = Function/BuildArray (`stagesim.py:1882-1883`).
- Source: LoopTunnel #30179 outer face t30192 'min slot', w30166, on diagram 23166 (= FS #29721's parent; graph 44858dbf row). Destination: #29879.index on frame #29869.
  - So op 187 is a ONE-border crossing into FS #29721, and that FS has 0 border tunnels today.
- FS #29721 rows on frame #29869 (`diag_c151_a3_2_facts.md:31`):
  - #29879 IndexArray: array t29882 w30685, element t29885, index t29888.
  - #30002 IndexArray: array t30013, element t30025, index t30028.
  - #30016 Local: Num t30023 w30685.
- Dependence: op 188 is 187's remove-loose-ends. Op 189 `p4_x_n2_out` (#29879.element -> SQ1 #29724.n2) does not use 187's wire. It was not simulated (the run stops at the first failure).
## 4. Not reached (the brief orders them after a passing maker / rebase)
- Rebase, pred V18E-R', the EL 46 / carry measurement, X11, licence, sink-gate census, recipes, dry / prerun / `--scratch-required` / `--check-launch`. The pred / licence copies were deleted unadapted.
## 5. Invariants: `prep_c152_a2_2_check_after.log` B 207/207, PIN PASS, A after == before for 207 files, LV none, RESULT 4/0
- All brief pins hold (stagesim c24bd39a, stage_prerun c739eb86, stagekit/stagexec/gscript/elrule/vigraph/addrcheck/errorlist_check; s08 VI f99e8414, graphs 44858dbf / e26b4d90 / 71935a84, s08 plan/pred/licence/recipes, memory_model, selftest 64918ff7); tools/hooks/**, prerun_records, gate_fp_queue unchanged.
- No JEV-LADDER row exists yet for `prep_c152_a2_2_mk.log` (`jev_gate.log`: preflight lines only, :5602-5607).
OPEN: op 187 needs the name a new FS border tunnel takes from a LoopTunnel source ('min slot'); this has never been measured. Measure it (a scratch FS crossing from a LoopTunnel), or route op 187 another way? Is (c4) acceptable?
