---
type: brief
status: current
date: 2026-10-08
---
# Brief 146-a1-5 — s06 PREP (v18 ops from 115), PROVISIONAL on the stagesim end of s05; dry + prerun reported; NOT launched — offline, beside the s05 scratch

OFFLINE (`labview: none`). Runs BESIDE the LabVIEW card 146-a1-4 (the s05 scratch): it must not touch any s05 file, the s04/s05 adopted VIs, any stage tool, or
anything under `claudeDev`. The s05 scratch is still running, so the REAL s05 graph does not exist yet: build s06 on the SIMULATED end of s05
(`tools/bench/sim/ring_p4_s05v18/`, plan `plan_ring_p4_s05v18.json` 1fc9b486 read-only) exactly as card 145-a1-P1 built the provisional s05 on a simulated s04
(`tools/bench/prep_c145_p1_mk.py`, `tools/bench/prep_c146_a1_3_mk.py` are the makers; copy to `tools/bench/prep_c146_a1_5_mk.py` and edit the copy only). The
`stage_prerun.py --rebase` onto the real s05 graph is a LATER card, after the scratch is adopted.

Facts so far (`tools/bench/diag_c146_a1_3_facts.md`): s05 = v18 ops 98..114; s06 starts at op 115; at the same-start formula it ends at op 138; ops 118/119
(`p4_w_tp_row` / `p4_w_rp_row`, Build Array #2626 `array`) and 132 are in s06, 150 in s07. X10 limits 680 / MEMSTOP 695; one start rule = the gate's own
`x10_start` (`memory_model.json` `load_by_vi`, `stage_prerun.py:2043-2052`).

## Do
1. Make s06: `tools/bench/plan_ring_p4_s06v18.json` (+ `_in.json`, `_pred.json`, `sim/ring_p4_s06v18/`) = the longest v18 prefix from op 115 that splits no 'of' group
   and whose MAIN-recipe prerun X10 is <= 680.0 at the PROVISIONAL start. The s06 start is unmeasured: state the assumption you use (the s05 load is not known until
   the scratch runs; use the memory model's own growth for s05's actions on top of 605.4 and say which formula, file:line) and report the cut at that start AND how the
   cut would move for +-5 MB of start. The cut is provisional; never present it as final.
2. Recipes `tools/recipes/stage_d1_ring_p4_s06v18.py` and `_scratch.py` by the same generator shape as the s05 pair (copy-edit of the s05 recipes; new files only).
3. Pred EL for s06 by `tools/elrule.py` from the s05 pred base (57) — report total and classes.
4. **#2626 / X11:** s06 carries ops 118/119. Draft `tools/bench/plan_ring_p4_s06v18_licence.json` (`pb-licence/1`, modelled on `tools/bench/plan_l2b1_licence.json`):
   `plan` = the s06 plan, `rename_by_uid` node 2626 with the still-open input uids taken BY UID from the sim end of s05, `require` = "every listed uid is an input of
   #2626 in the real end read with the same uid, unwired unless this session wires it, else the licence is void", `decided_by` = "PD352(d)", and a field/why text saying
   PROVISIONAL until the real s05 graph is read. Prerun X11 must then read it licensed; report the exact X11 line.
5. Sandbox dry and prerun (+ `--scratch-required`) of BOTH s06 recipes; report every line; 0 FAIL wanted, every refusal quoted not patched; nothing launched.
6. md5 before/after: every s05 file and recipe, s04 files, v18, memory_model.json (559be4cf), stage tools = unchanged. No LabVIEW process (`tasklist`).

## Never
LabVIEW, camera, motor; a scratch or real launch; editing any s05 file, the s04/s05 adopted VIs, `memory_model.json`, a stage tool or v18; `--rebase` on a real
s05 graph (does not exist yet); clearing a refusal by editing a gate.

## Return
`result/1`; facts `tools/bench/diag_c146_a1_5_facts.md`: cut op / peak / margins and the assumption, the +-5 MB sensitivity, new file md5s, pred EL, licence state and
X11 line, dry/prerun outcome per recipe with every non-PASS quoted, md5 table.
