---
type: facts
status: current
date: 2026-10-09
card: 151-a3-2
---
# Card 151-a3-2 facts: s09 cut = whole remainder, but the simulator STILL refuses op 185 on the REAL s08 graph (FS #29721 unmeasured); RETURNED at brief step 3
Offline only; no LabVIEW before or after (`prep_c151_a3_2_check_before.log` / `_after.log`, LV PASS). No stage-tool, hook or elrule edit, no `--launch`. NO plan / pred / licence / recipe written.
## 1. Maker `prep_c151_a3_2_mk.py` (copy of `prep_c150_a3_6_mk.py` f3e6d12c) - log `prep_c151_a3_2_mk.log` RESULT 12/1, rc 1 (:36-38)
- Changes (docstring (1)-(7)):
  - The base moves s07 -> s08: END8 = `sim/ring_p4_s08v18/step_19_wire.json` ccfaa07c, plus the s07 creation map 08c2ad4d (c2d74901). REB reads the rebased s08 plan.
  - The cap is REMOVED: the `nact(...) <= MAXACT` term is gone from `lcut` (`prep_c150_a3_6_mk.py:149`; MAXACT was at :64). The CAP gate became a TAIL fact.
  - REALSIM was added (brief step 3): the pass-A input is simulated with the REAL s08 graph as its base.
- The remainder is v18 **actions 197..202 = ops 185..190** (6 actions). v18 has only 190 ops (`prep_c151_a3_2_probe.log:18-24`), so there are no ops 191..202.
- START 595.0 = x10_start(f99e8414) = 589.1 + op-0 5.9 (X0, mk.log:5), as the brief expected.
- CUT = op 190, the whole remainder (6 actions). No op is left to name as "first op not included". No 'of' group crosses the cut (mk.log:11, :24).
- X10 at the cut: MAIN 638.4, Executor 633.3. Margin 41.6 to 680 and 56.6 to 695 (mk.log:17). No op goes over 680.
- Sensitivity (mk.log:15-16): +13.6 MB -> start 608.6, MAIN 652.0, margin 28.0; +21.4 MB -> start 616.4, MAIN 659.8, margin 20.2. Both keep cut op 190. The cut uses the unshifted rule; no coefficient changed.
- R (mk.log:28-31): IAZ1 -> #30002 IndexArray, IAN1 -> #29879 IndexArray, SQ1 -> #29724 SubVI, TS1 -> #30179 LoopTunnel. Gate R PASS.
- C2: 5 cross refs, all real s01..s07 uids, 0 s08-provisional.
## 2. Simulator outcome on ops 185..190 (the FS #29721 question): STILL REFUSED - brief step 3's return condition
- REALSIM on graph 44858dbf (mk.log:35) failed at n 1, op `wire`, id `p4_x_n2_order` (v18 op 185: src #5058 t5111 -> dst #30002 'array'). Verbatim:
  `diagram chain: frame #29869 belongs to FS #29721 whose diagram is UNMEASURED (no border outer face, or faces disagree; PD289(f))`
  The message is raised at `tools/stagesim.py:1805-1807`.
- Pass A on the provisional END8 base failed the same way at n 1 (gate SA, mk.log:36). No plan was written, so no rebase ran.
- Why (read from the files, not inferred):
  - The s08 graph's `fs_measured.fs_frames['29721']` is [29869] (probe.log:26).
  - `stagesim.base_state` on that graph gives `fs_unmeasured` [2499, 14682, 29721, 43914]. Frame #29869's owner is ['FlatSequence', 29721]; #29721 has no owner (probe.log:29).
  - `_diag_chain(29869)` raises the same error (probe.log:30).
  - The FS has 0 border tunnels (`diag_c151_a1_1_facts.md:42`), so no `fs_parent` is derived for it (`stagesim.py:424-428`, :354).
- FS #29721 rows on frame #29869 (`diag_c151_a1_1_facts.md:40-41`): #29879 IndexArray (array t29882 w30685, element t29885 src, index t29888); #30002 IndexArray (array t30013, element t30025 src, index t30028); #30016 Local (Num t30023 w30685 src).
- Every remaining op depends on frame #29869 (from the plan refs; only op 185 was simulated): 185 dst #30002.array; 187 `p4_x_slot_fs` dst #29879.index (its src TS1 #30179.outer is a LoopTunnel); 189 `p4_x_n2_out` src #29879.element; 186/188/190 are the `wire_remove_loose_ends` of 185/187/189.
## 3. Not reached (the brief orders them after the rebase)
- Not run: rebase, pred V18E-R', the EL base-46 / `elrule.predict` carry measurement, X11, licence, sink-gate census, recipes, dry / prerun / `--scratch-required` / `--check-launch`.
## 4. Files and invariants
- Written: `prep_c151_a3_2_{probe,mk,check}.py` + logs, `prep_c151_a3_2_md5_before.json`, `sim/ring_p4_s09v18/{s08end/base_provisional.json 49cdec8a, _passA/**, _realG/**}`.
- `prep_c151_a3_2_check_after.log`: B 195/195, PIN PASS, A after == before for 195 files, LV none, RESULT 4/0.
  - Unchanged tools: stagekit 604529e8, addrcheck 207beb0d, stagexec, gscript, elrule, stage_prerun, vigraph, stagesim, errorlist_check.
  - Unchanged data: VIs s08 f99e8414 / s07 b3f86b32; graphs 44858dbf / 71935a84; s08 plan/pred/licence/recipes; memory_model a28b6dd7; s07/s08 sim trees; tools/hooks/**.
  - prerun_records and gate_fp_queue are unchanged (CHG md5 before == after). Only material_marker.log changed, appended by the hook.
OPEN: all of ops 185..190 need FS #29721's parent diagram, and the FS has no border tunnel. Measure that owner diagram another way, or route these ops differently?
