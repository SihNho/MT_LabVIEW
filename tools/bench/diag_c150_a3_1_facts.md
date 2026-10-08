---
type: facts
status: current
date: 2026-10-08
card: 150-a3-1
---
# Card 150-a3-1 facts: s07 prepared offline on plan 08c2ad4d - V18E-R' PASS, X10 673.7 / 678.8, two sink gates, licence, dry + prerun PASS both; NOT launched
Offline only, no LabVIEW process before/after (`prep_c150_a3_1_check_before.log` / `_after.log` LV PASS). No stage tool, hook or elrule edit; no `--rebase` (plan md5 unchanged 08c2ad4d).
## 1. Pred (`prep_c150_a3_1_pred.py` 2644bdd4 = copy of a2_5's 85196a77, V18E-R' only; log `prep_c150_a3_1_pred.log` RESULT 11/0, rc 0)
- RENAMED-OLD read from `prep_c150_a2_5_rebase.log` (28341ad1): 2832/4160/4165 #2626 'array'->'element', 9508/9505 #9503 'Value'->'' -> owners [2626, 9503] (log :9).
- (1) only-s07 rows [] PASS (:11). (2) only-v18 `2626|Terminal|array|1..3`: each `before: null` in v18 cdiff_detail at #177, node 2626 owns RENAMED-OLD -> PASS (:12-15).
- (3) #2626 sink-name multiset real s06 graph {'array':1,'element':3} == S1 (D1_s1_copy, stagesim.load_s1) {'array':1,'element':3} PASS (:16). Excluded keys: the 3 rows above (:17).
- Pred written `plan_ring_p4_s07v18_pred.json` e888ab67 -> **6f46fc3c**; EL base 51 -> predicted 52 (input +1, sr +1/-1) (:25-29).
## 2. X10 (no cut needed)
- Pred: start 599.7 (593.8 + op-0 5.9), Executor peak **673.7** <= 680, margin 6.3 / 695 margin 21.3; next op 166 677.6; first op over 680 = 168 (pred log :21-23).
- Prerun MAIN: predicted peak **678.8** (R 8: + 2 census_snapshot reads), margin 1.2 / 16.2 (`prep_c150_a3_1_prerun.log:129-131`). Scratch: 673.7, margin 6.3 / 21.3 (`prep_c150_a3_1_scr_prerun.log:153-155`).
## 3. X11 (`prep_c150_a3_1_x11.log`, rc 2 before licence)
- FLAG row p4_rbB_sel_t4168 node #2626 wired 'array' open sibling ['element'] licensed None -> op 150 flagged. After licence: prerun X11 PASS, licensed by the s07 licence (`prep_c150_a3_1_prerun.log:113`).
## 4. Sink gates (MAIN `stage_d1_ring_p4_s07v18.py` d6c8da7b -> **e0f1152f**)
- s06 form (`stage_d1_ring_p4_s06v18.py:46-52,89-90`): ONE `SG_ROW` typed, `SINK_GATES = [{"gate": SG_GATE, "sink": SINK}]`.
- s07: rows READ from `prep_c150_a1_1_session.json` sink_gate_census (needs_sink_gate) at :50-51; spec per row `_sg_spec` :54-74; `SINK_GATES`/`SINK_FNS` :119-120; sg_read pass rule (a)-(d) unchanged, takes the spec.
- Count 2 because the census lists exactly two ControlTerminal sinks fed from a wired source (route indicator): n1 p4_rbA_re2 -> [23166,'Pos: Diffraction Pattern'] src 5058 'pos in cal image out';
  n28 p4_rbD_sel_t25573 -> [23166,'autofocus reset count (1.2 to 1.1)'] src `new:RB4.s? t:f` (created in s07; resolved on the sim end by stagesim.resolve_addr -> 's? t:f') (`prep_c150_a3_1_dry.log:28`).
- Scratch `_scratch.py` 273dc3de -> **80dbdb41**: names c148->c150, assert = one gate per census row (:33-35), evidence header :161-167.
## 5. Licence (`prep_c150_a3_1_licence.py` da47cb38, log RESULT 5/0) -> `plan_ring_p4_s07v18_licence.json` **aedbe1f1** (pb-licence/1, s06 form)
- rename_by_uid: #2626 term_uids [4168] (X11 row p4_rbB_sel_t4168). renames: 8 entries / 9 uids, from/to unset, owners 2626[4168], 2765[2811], 10757[10871], 10850[25246],
  23166[9519,25573], 23508[23798], 25339[25347], 25371[25385] (log :6-14). Read-back used a copy of stagekit.licence_renames (guard_write refused importing stagekit under labview:none); the real reader ran in both dry runs (REN, :33).
## 6. Dry / prerun / scratch-required (final bytes; plan 08c2ad4d, pred 6f46fc3c, licence aedbe1f1)
- MAIN dry PASS (`prep_c150_a3_1_dry.log:110`); MAIN prerun PASS 16/0 (`_prerun.log:135`); scratch dry PASS (`_scr_dry.log:134`); scratch prerun PASS 16/0 (`_scr_prerun.log:159`).
- `--scratch-required` MAIN rc **3** (CENSUS-UNPREDICTED rows 1-30) (`prep_c150_a3_1_scrreq.log`). `--check-launch` scratch: ALLOW rc 0 (`prep_c150_a3_1_checklaunch.log`).
- PROVEN-PATTERN: NOT emitted; prerun X14 WARN "rows 30, budget 15 (proven: no)" (`_prerun.log:132`). No prior-art review run (card peers []).
## 7. Files (md5 before -> after)
| plan / _in / _pred / _licence | 08c2ad4d / 7b890070 / e888ab67 / absent | 08c2ad4d / 7b890070 / **6f46fc3c** / **aedbe1f1** |
| recipes MAIN / scratch | d6c8da7b / 273dc3de | **e0f1152f** / **80dbdb41** |
New: prep_c150_a3_1_check.py 1b935cd2, _pred.py 2644bdd4, _licence.py da47cb38, their logs, _md5_before.json. sim/ring_p4_s07v18_base_real_fsmap.json 765c687c unchanged.
## 8. Invariants (`prep_c150_a3_1_check_after.log`: B 102/102, PIN pass, A after == before 102 files, LV none)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s06 569ffbf5, s05 3f9ac26b, bed 39511877,
memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b, sim/ring_p4_s06v18/**, s06 plan/pred/licence/recipes: unchanged. No hooks edit, no --launch.
OPEN: launch-time prior-art: X14 says proven: no (30 rows > 15) - does guard_cycle require a diff-only prior-art review of the scratch recipe before the s07 launch (card had no peers)?
