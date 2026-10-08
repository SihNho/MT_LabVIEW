---
type: facts
status: current
date: 2026-10-08
---
# Card 150-a1-3 facts: the s07 rebase refusal is two PRE-EXISTING s06 nodes whose input NAMES LabVIEW changed (licensed renames), not extra objects
Offline, no LabVIEW (check_before/after LV gate). Probe `diag_c150_a1_3_probe.py` (692020200c) -> `diag_c150_a1_3_probe.log` 5/0, rc 0. No tool edited.
## 1. before / prov / real (`stage_prerun.rebase`, :4252-4258; compared in `rebind` :3829-3849)
- before = stage N's plan (s06 cfbd9823) `finalized.base` = `sim/ring_p4_s06v18_base_real_fsmap.json` (the REAL s05 graph + FS map), :4253/:4256. 6022 rows.
- prov = s07 plan `base.path` = `sim/ring_p4_s07v18/s06end/base_provisional.json` (eeb22bba, stagesim end of s06), :4257. 6030 rows.
- real = `graph_ring_p4s06_20261008_192149.json` (a3ecb92b), :4258. 6030 rows. Both s07 plans (30-act and prov148) carry the SAME base + sim_of (probe log BASES).
- sim_new = prov rows with node uid < 0 (:3832-3834); real_new = real rows whose key (term uid, owner uid, **term_name**) is not in before (:3829, :3835-3837).
## 2. The unmatched objects (probe.log:12-35) - the real s06 has NO extra object; two old nodes enter real_new by NAME
- Created + matched: While LoopTunnels #30287 ('# FD points') / #30290 ('# DT points') = sim #-5 / #-10, both in the s06 creation map (cmap :2-8).
- Extra BuildArray = #2626 (pre-existing, obj owner Diagram in before/prov/real): rows t2832/t4160/t4165 named 'element' in real, 'array' in before
  (owner unchanged, 2626). The partial node (3 rows) gives key ('BuildArray', 3x ('Terminal', False)). t2813/t4168 unchanged. probe.log:27-31.
- Extra LoopTunnel = #9503 (pre-existing, on a ForLoop): t9505/t9508 named '' in real, 'Value' in before. Same LoopTunnel key. probe.log:32-35.
- Rows that touched them in s06 (`plan_ring_p4_s06v18.json`): `p4_w_tp_mag` :108-117 (dst 9503 t9508), `p4_w_tp_row` :121-130 (2626 t4160),
  `p4_w_rp_row` :134-143 (2626 t4165), `p4_w_bd_row` :349-355 (2626 t2832). These exact renames are LISTED in `plan_ring_p4_s06v18_licence.json:16-30`
  (`renames`: 2626 array->element; 9503 Value->''), read by `stagekit.licence_renames`/`rename_check` (stagekit.py:1412-1448).
- stage_prerun.rebind takes no licence: `renames` occurs nowhere in stage_prerun.py; tkey keeps term_name (:3829) though the docstring says names are
  never keyed (:3788). So a licensed rename on an OLD node becomes a 'created' node in real_new and breaks the shape count at :3846-3849. Not a data
  fault: uids/owners of 2626/9503 unchanged; the names are what LabVIEW wrote (licence :22/:29). Key: ('LoopTunnel',(('InnerTerminal',True),('OuterTerminal',False))).
## 3. Why s05 -> s06 passed (`prep_c147_a1_3_rebase.log:3-5,59`, rc 0)
Same kind of inputs: s06 `_in` base = stagesim end `sim/ring_p4_s06v18/s05end/base_provisional.json`, before = `ring_p4_s05v18_base_real_fsmap.json`,
real = graph_ring_p4s05_20261008_013759. Recomputed (probe.log:89-102): sim_new 8 nodes, real_new 8, counters EQUAL - in s05 no pre-existing node had a
terminal renamed (the 2626/9503 renames first happen in s06, PD356(d)). Difference is the input data (renames), not the code path.
## 4. PD364(c) fallback (probe.log:103-107; `stage_prerun.rebase()` called as the CLI does at :4972, out_root = diag_c150_a1_3_sim, nothing written)
`plan_ring_p4_s07v18_fb150.json` = byte copy of prov148 (aeae610e). Result: `CREATION-MAP ...cfbd9823_20261008_175325.jsonl (entries {'obj': 4, 'diag': 0,
'term': 8}; steps with a diff [])` / `REBASE REFUSED: BINDING: the created objects differ (name-free shape): ['BuildArray x0 simulated vs x1 real',
'LoopTunnel x2 simulated vs x3 real']` - the SAME BINDING list. fb150 md5 after = aeae610e (not rewritten). Expected: shape check is plan-independent.
## 5. Invariants (`diag_c150_a1_3_check_before.log` / `_after.log`, 107 files, PIN pass, A equal, LV none)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun dcd45aba, s06 569ffbf5, s05 3f9ac26b, s04 95e408ff, bed 39511877,
memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b, s06 plan/in/pred/licence/recipes, sim/ring_p4_s06v18 tree, s07 plan 10a4f59a, _in 7b890070.
OPEN: fix class = TOOL EDIT in stage_prerun.py rebind (:3829-3849: key old terminals by (uid, owner) or apply the s06 licence `renames`) - judgement to pick.
