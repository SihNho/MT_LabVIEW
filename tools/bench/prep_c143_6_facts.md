---
type: facts
status: current
date: 2026-10-03
---
# Card 143-6 facts: s03 v18 offline checks on the rebased plan da66a030 - all PASS; scratch required (exit 3)

OFFLINE only; no LabVIEW. Card inputs md5-checked (6/6 match). plan da66a030 and the two recipes unchanged; stagexec/stagekit/stagesim/
stage_prerun/gscript not edited.

## Pred (prep_c143_6_pred.py, log prep_c143_6_pred.log) 8/0
- Copy of prep_c143_5_pred.py with ONE change: the RB negative-uid scan walks action FIELDS recursively and skips keys why/notes/note
  (int < 0, or a '-<digits>' token inside a string). Text negatives are printed, not gated: p4_c_bufdiff.why '-1', p4_k_last.why '-1'.
- RB PASS (neg []), RB2 PASS (base fsmap c4a11939: vi md5 84cac487, fs_carried.real_graph eda9db40), A1 PASS (#6902.'StopAll'), C 20 -> 20 ops.
- X10 at start 596.0: N 20, R 14, peak **676.4** <= 680.0 (margin 3.6 MB) - no re-cut. Prerun's own X10 (its own start): 655.5
  (stage recipe) / 650.4 (scratch).
- EL fixed rule (prep_c143_3_elrule.py) on base 53: new [cond -46, input -46, input -36, input -27, local -49], closed [cond 23166,
  local 6902] -> **predicted 56**; uncertain []. Basis: errorlist_expected_D1_ring_p4s02_20261003_110001.json total 53.
- Pred file plan_ring_p4_s03v18_pred.json md5 7fab8cf0, keyed to plan md5 da66a030. Census: all 20 actions UNPREDICTED (no samples).

## Dry + prerun (both recipes)
- stage_d1_ring_p4_s03v18.py: dry PASS (prep_c143_6_dry.log: E1 20 ops, FR 9 objects, PB 16 rows + 11 open pairs); prerun 16/0
  (prep_c143_6_prerun.log; WARN X13 x5 no replayer/model, X14 rows 20 > budget 15, proven: no).
- stage_d1_ring_p4_s03v18_scratch.py: dry PASS (prep_c143_6_scr_dry.log, reads X10 676.4 from the pred); prerun 16/0 (prep_c143_6_scr_prerun.log).
- `--prerun stage_d1_ring_p4_s03v18.py --scratch-required ...`: exit **3** SCRATCH-REQUIRED, CENSUS-UNPREDICTED rows 1..20 (prep_c143_6_scrreq.log:3).

## '.value' addresses on the s03-created Locals
- stagesim.py:735 (card 100-3): '.value' = the node's one terminal of the wanted direction, not a name match.
- prep_c143_6_probe2.log: p4_w_b_arr src 'new:LRB1.value' -> term -7, the Local's only row 'BufDiff' (source); p4_w_b_out dst
  'new:LWB1.value' -> term -14, the Local's only row 'BufDiff' (sink); both wired in the sim. Resolves; no rename needed offline.
- prep_c143_6_probe.log (first probe run) rc=1 NO RESULT LINE: KeyError in my probe (looked up sym 'LRB1', the key is 'new:LRB1');
  fixed by reading the step's effect term uids. Our-script bug, offline; no LabVIEW. The real executor's handling of '.value' was not read.
