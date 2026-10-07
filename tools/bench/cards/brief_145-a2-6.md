---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-6 — re-make s05 (v18 ops 98..124) on the REAL s04 graph, EL by the fixed rule; report dry + prerun + scratch-required; NOT launched (PD351(d))

OFFLINE (`labview: none`), runs ALONE. Everything s05 needs is now measured:
- real s04 graph `tools/bench/graph_ring_p4s04_20261007_223245.json` (094ba298), fresh-load peak **605.4 MB**
  (`diag_c145_a2_1_facts.md`), adopted file `claudeDev\D1_ring_p4s04_20261007_215031.vi` 95e408ff;
- s04 plan `plan_ring_p4_s04v18.json` f349c39a = the base whose simulated end the s05 plan starts from; v18 `plan_ring_p4_v18.json` 2ea6cafa;
- EL rule fixed: `tools/elrule.py` a5ee7d5c + `tools/bench/subvi_requiredness.json` 13b0d75f (SubVI items only for a measured Required terminal;
  `selftest_elpred` 21/0, S04 = 58);
- X11 facts `tools/bench/diag_c145_a2_x_facts.md` (593cc6f0): ops 118/119 wire Build Array #2626 t4160/t4165 while (2626, `array`) is an
  open row; `plan_l2b1_licence.json` does NOT cover it (facts :44-50); the refusing gate is `stage_prerun.py` X11.

A PROVISIONAL s05 already exists (card 145-a1-P1: `plan_ring_p4_s05v18.json`, `_in.json`, `_pred.json`, `prep_c145_p1_*`, built on the
provisional simulated s04). Re-make it on the real graph; do not edit any of it by hand.

## Do
1. Copy the provisional s05 files (plan, `_in`, `_pred`, `sim/ring_p4_s05v18/`) to `*_prov` names first (md5 recorded). Then re-make with
   the same recipe shape as `tools/bench/prep_c145_p1_mk.py` (c7fdf263; read it, report any change): ops 98..124 of v18 from the f349c39a sim
   end, `--rebase` onto the real s04 graph (`stage_prerun.py --rebase`; on a re-bind refusal print the line, do not patch around it).
2. Pred: EL expected for s05 by the FIXED rule (`tools/elrule.py` predict, base = s04's recorded 58), written as
   `plan_ring_p4_s05v18_pred.json` (the provisional copy stays as `_prov`). Report the predicted total and each counted item class.
3. X10 (memory) at the measured s04 load 605.4 MB with `tools/bench/memory_model.json` (db163e03): report predicted peak vs limit 680 / MEMSTOP 695.
4. Run, report every line, patch nothing: sandbox dry, `stage_prerun` prerun, and `--scratch-required` check. **X11 is expected to refuse
   the two rows `p4_w_tp_row` / `p4_w_rp_row` (no licence).** Quote the refusal; do NOT edit the plan, the licence file or the gate to clear it
   (no licence = no re-cut; the judgement session decides). Any OTHER refusal: quote it with file:line, classify it (plan fault / tool fault /
   stale-binding) and stop there.
5. s04 plan/pred/recipes, v18, stage tools, the s04 adopted file, s03, bed: md5 before/after, unchanged. Nothing launched; no LabVIEW process
   started (`tasklist` after).

## Never
LabVIEW, camera, motor; a scratch or real launch; editing the licence file, the X11 gate, any stage tool or any s04 file; clearing a refusal by
changing the plan.

## Return
`result/1`; facts `tools/bench/diag_c145_a2_6_facts.md`: new s05 files + md5, op range/row count, predicted EL total and classes, X10 figures,
dry / prerun / scratch-required outcome with each refusal quoted, md5 table.
