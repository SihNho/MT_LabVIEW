---
type: facts
status: current
date: 2026-10-09
card: 152-b2-1
---
# Card 152-b2-1 facts: P4 session 9 MADE offline (v18 ops 185..190, the whole remainder); ops 187 and 189 now simulate; NOT launched
Offline only; no LabVIEW before or after (`prep_c152_b2_1_check_before.log` / `_after.log`: LV PASS, A 219/219 equal). No stage-tool / hook / elrule edit, no `--launch`.
## 1. Discriminator re-run - `prep_c152_b2_1_probe.log` RESULT 2/0
- (i) measured FS #29721 -> 'Diagram' #23166 (`diag_c152_a1_1_owner.log:25`, probe :13); stagesim 128bacfb `base_state(derived)` owners[29721] ['Diagram', 23166] (:15).
- (ii) creation map s04 f349c39a :36 owner_real 23166 -> v18 #85 p4_fs_n2 diagram 23166 (numeric base uid, no rebind hop) -> s04 plan 23166 (:17-20). Gate D EQUAL (:22).
## 2. Maker `prep_c152_b2_1_mk.py` (copy of 5c426b71) - `prep_c152_b2_1_mk.log` RESULT 20/0 (:75)
- START 595.0 = 589.1 + 5.9 (:6). Cut = op 190 = whole remainder, 6 actions, tail [] (:14, :27). MAIN 638.4 / Executor 633.3, margin 41.6 to 680, 56.6 to MEMSTOP (:20).
- Sensitivities: +13.6 MB -> MAIN 652.0 (margin 28.0); +21.4 MB -> MAIN 659.8 (margin 20.2); cut 190 both (:18-19).
- REALSIM on derived e26b4d90: failed null, 7 steps (:38). Pass A on base_provisional_fsowner fd84b364: failed null, 21 end rows (:53). Gates SA, TIE, SB FINAL (19 open pairs) PASS (:54-56).
- Per op, both runs reach the end (step files under `sim/ring_p4_s09v18/_realGb21|_passAb21/ring_p4_s09v18a/`, :39-52):
  - op 185 step_01_wire; op 186 step_02; **op 187 `p4_x_slot_fs` step_03_wire OK** (REALSIM 456d9855, pass A eb546423); op 188 step_04;
    **op 189 `p4_x_n2_out` step_05_wire OK** (REALSIM 2137cdcd, pass A c5808f97); op 190 step_06.
- KIND: all 6 same kind (:57-62). V18E end diff 3 == step-0 inherited 3 (2626 array rows) (:70-72). Sink-gate census 0 rows (:68).
- Copy changes: card id, session file, sub-dirs `_passAb21`/`_realGb21`, gate-P label, and FACT-only `FACT STEP` lines. No gate added.
## 3. Rebase - `prep_c152_b2_1_rebase.log` rc 0 (:21-22)
- `--rebase plan_ring_p4_s09v18.json --graph graph_ring_p4s08_..._fsowner.json` (the derived file; :1).
- s08 creation map c328fdaf: 3 nodes, 9 terminals, 0 fallback (:3-6). Re-simulation steps 01..06 all ok (cdiff 21) (:8-13).
- Plan 9d622c95; base `sim/ring_p4_s09v18_base_real_fsmap.json` 2f58241c; 17 uids bound. No RENAMED-OLD / FLIPPED-OLD line.
## 4. Pred `prep_c152_b2_1_pred.py` (copy of 7996f5b1) - `prep_c152_b2_1_pred.log` RESULT 14/0 (:46); pred 85dbb0ba
- V18E-R' gate PASS (:24): (1) only-s09 [] (:17); (2) 3 only-v18 rows on #2626 (:21); (3) #2626 sink names {'array': 1, 'element': 3} == S1 (:22).
  - RENAMED-OLD read from 3 rebase logs (s09 1f18f0fd, s08 0c298253, s07 28341ad1); owners 2626/9503 come from the s07 log (:15).
- X1 595.0 == prerun start (:26). X10 Executor 633.3, margin 46.7 (:27-29). X17 PASS, 0 primitive creates (:30).
- Carry (:31): `elrule.predict` for s08 c328fdaf, base 50.
  - No carry -> 48 (== s08 pred cf2eccbf). Carry {4538, 29843, 29879, 30002, 2626} -> 47 (closes input #4538, local #30016, sr #9603).
  - Measured s08 = 46, so the carry does NOT reproduce it.
  - s09 pred uses no carry: 46 (new 0, closed 0). With carry it would be 45 (closes input #29879). Stored as `alternative_total` (:32-33).
- PC: 46 read items == 46 expected (:37).
## 5. Licence, X11, recipes, preruns
- X11 `--buildarray-check` CLEAN (`prep_c152_b2_1_x11.log:3`).
- Licence 6d003b8d (`prep_c152_b2_1_licence.log` 5/0): rename_by_uid [], renames [].
  - All 3 s09 dsts are name-form. They resolve in the base to #30002 t30013 'array', #29879 t29888 'index' and #29724 t29970 'n2', all sinks (:8-10).
  - The copied rule reads term_uid dsts only, so it gives 0. Gate R changed from ">= 1" to "zero allowed" (docstring, stated before the run).
- Recipes `stage_d1_ring_p4_s09v18.py` 4be3ff28 and `_scratch.py` b1f6a87c: names / pins, plus ONE gate change.
  - FR `on` became `(on or NC == 0)`, because s09 creates no object.
  - Dry FR then passes: "0 created objects ... real frames == the sim end's" (`prep_c152_b2_1_dry.log:53`).
- Main recipe: dry 1/0 (dry.log:64), prerun 16/0 (prerun.log:88; X10 peak 638.4 <= 680 :83; X14 6 rows, budget 15, not proven :84). Scratch: dry 1/0, prerun 16/0.
- `--scratch-required` rc 3: CENSUS-UNPREDICTED rows [1..6] (`prep_c152_b2_1_scrreq.log:3`). `--check-launch` scratch: ALLOW, rc 0 (`_checklaunch.log:3`). NOT launched.
## 6. Invariants - `prep_c152_b2_1_check_after.log` RESULT 4/0
- B 219/219; PIN PASS (stagesim 128bacfb, table 769ae8d0, ring-p4d cf2ffa4a, stage_prerun c739eb86 + rest, s08 VI f99e8414, graphs 44858dbf/e26b4d90/71935a84, s08 plan/pred/licence/recipes, memory_model, selftest 64918ff7); A after == before 219 (tools/hooks/** incl.); LabVIEW 0.
OPEN: accept two s09-shape adaptations: recipe FR `(on or NC == 0)` and licence R "zero allowed" (renames 0, every dst name-form)? The carry gives 47, not 46 (no carry used).
