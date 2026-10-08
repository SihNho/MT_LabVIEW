---
type: facts
status: current
date: 2026-10-08
card: 148-a3-3
---
# Card 148-a3-3 facts: P4 s07 PROVISIONAL prep on stagesim's end of s06 (offline, not launched)
**s07 = v18 ops 136..149, 14 actions (p4_rbA_re2..p4_rbB_out), MAIN X10 679.6 at provisional start 627.7, cdiff vs v18 0, X11 not needed. Dry/prerun do NOT
pass on a provisional base by tool design: dry `BASE ... {'unbound': [-22,-21,-20,-18,-12,-11]}`, prerun 13/3 = X1, X5, X10 "base is PROVISIONAL"
(`stage_prerun.py:2593-2599`; the WAITING class of `:544-582`, recorded as FAIL in prerun_records.jsonl:878-881).**
## 1. Start, cut, X10 (`prep_c148_a3_3_mk.log` RESULT 20/0, rc=0 36 s)
- START 627.7 = rule of `prep_c147_a1_2_mk.py:82-83`: load_by_vi[3f9ac26b] 606.7 + 0.719 x 21 s06 ops (= predicted s06 load 621.8) + op0 5.9 (mk.log:4-5). The
  brief's "s06 scratch peak/end" 674.2/679.3 (`diag_c147_a1_3_facts.md:20`) are in-session peaks, not a file load (as a start: -0.1 MB left, mk.log:6).
- The prerun has no start for a provisional plan (`x10_plan_start` None, `stage_prerun.py:2079-2080`; pred X1 pred.log:12): the cut uses the maker's MAIN
  formula (== x10_model_peak + 2 source reads, `stage_prerun.py:2608-2611`), not a prerun X10 line.
- Cut op 149: MAIN 679.6 (0.4 to 680, 15.4 to MEMSTOP 695), Executor 674.5; first op over = 150 (681.0); no group split (mk.log:11,15). N 14, R 4,
  checkpoints [0,2,10,14]; connect 11 / create 2 / delete_wire 1; all kinds == v18 (mk.log:61-62). Sensitivity 622.7 -> op 152 (678.8, 17 act); 632.7 -> op 145
  (676.6, 10) (mk.log:12-14). Next session at the same start ends op 163.
- Refs: s06 objects stay END6 negatives (TFD1 -5, TDT1 -10, LRVB1 -17, IAVB1 -19; none used by s07); new:SQ1 (s05) -> real #29724 by the s05 creation map,
  class SubVI == SubVI (mk.log:37-39). Negative control REFUSED (mk.log:60). V18E end 18 == v18 #161 18, **cdiff 0**; step 0 == v18 #147 (mk.log:66-68).
## 2. #2626 licence / X11
- Op 150 (`p4_rbB_sel_t4168`) is the first op over the cut: **no #2626 row in s07, no licence file** (mk.log:35). X11 PASS on both recipes (prerun.log:37,
  scr_prerun.log:57). Recipe `REN = K.licence_renames({})` = None (`stagekit.py:1415-1416`).
## 3. Pred (`prep_c148_a3_3_pred.log` RESULT 10/0): `plan_ring_p4_s07v18_pred.json` e888ab67, `provisional: true`
- EL base = s06 PREDICTED 55 (c4a6a35a when read, pred.log:4); elrule a5ee7d5c: new [] closed [sr 23508] -> **54**; uncertain base [[2626,['array']]] (pred.log:17).
- Per class: input 6, local 1, sr 1->0, not-connected 20, loose-ends 20, undirected-tunnel 3, no-source 1, out-tunnel->RAS 1, ->SubVI 1, two-types 1 (pred.log:19-21).
- X10 Executor 674.5 == table; X17 PASS; census UNPREDICTED, 14 rows (pred.log:15-16,22).
## 4. Sink gate + recipes (no gate line changed in either)
- SG census: one wired-source row into a ControlTerminal: `p4_rbA_re2` -> [23166, 'Pos: Diffraction Pattern'] t9519, route indicator (mk.log:63-64).
- main d6c8da7b vs d947df5d: 5,12c5,12 + 14,17c14,18 docstring; 22c23 log; 27c28 PLAN; 29,30c30,31 PRED + REN; **46,47c47,48 SG_ROW p4_rbA_re2 / SG_GATE**;
  95,96c96,97 L0; 133c134 CEN2; 140c141 ES; 156c157, 158c159 R key/level; 162c163 Stage name/out/task.
- scratch 273dc3de vs 31009bfc: 5c5 evidence :159-165; 7,13c7,14, 15c16, 19c20, 22c23, 24c25 docstring; 29c30 import R s07; 34,36c35,37 PLAN/PREDF/LOG;
  96c97 elcls doc; 165,167c166,168 Stage/work/out/task; 174,176c175,177 R key/label; 183c184, 185c186 card id / sum json.
## 5. Dry / prerun / scratch-required (offline)
- main dry: L0, SG (1 gate), L1 PASS (dry.log:22,27-28), then DRY FAIL on the BASE unbound line, RESULT 0/1 (dry.log:34-35). main prerun 13/3 X1, X5, X10 (prerun.log:58).
- scratch dry: same BASE fail (scr_dry.log:54); scratch prerun 13/3, same three (scr_prerun.log:78). Same class as 145-P1 (`prep_c145_p1_facts.md:35-37`).
- `--scratch-required` main: `SCRATCH-REQUIRED | ... CENSUS-UNPREDICTED ... rows [1..14]`, `BGRUN END rc=3` (scrreq.log:4-5), as predicted.
## 6. Protected md5 (`prep_c148_a3_3_check_before.log` / `_after.log`, 96 files): 95 identical
- stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun dcd45aba, s06 plan/in/recipes, sim/ring_p4_s06v18 tree, memory_model
  88eeb037, s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877 unchanged. **`plan_ring_p4_s06v18_pred.json` c4a6a35a -> c1bd6b3e at 17:58:07 by card
  148-a2-4** (its `census_source` block, pred.json:296-308; `diag_c148_a2_4_census.log` same second). LabVIEW pid 7228 is 148-a2-4's; this card started none.
## 7. Files
s07 plan aeae610e, _in 97e4e091, _pred e888ab67, base_provisional eeb22bba, prep_c148_a3_3_session.json efe764c1; mk 5f00cd4f, pred 8b2ec4f1, check 3674a6c8.
OPEN: dry + prerun PASS is unreachable on a provisional base (X10 refuses it): accept this WAITING-class result now and require PASS only after --rebase?
