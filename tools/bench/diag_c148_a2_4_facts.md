---
type: facts
status: current
date: 2026-10-08
card: 148-a2-4
---
# Card 148-a2-4 facts: s06 scratch PASS 22/0 (first run on the new gate API); Error List read FAILED on a tool/env fault (no comtypes, no OCR) -> RETURN, NOT adopted

## Before
- `diag_c148_a2_4_check.log` 26/0: 20 card inputs == card md5, stage_prerun dcd45aba; s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877; no LabVIEW.
- Scratch `--dry` 1/0 (`diag_c148_a2_4_scr_dry.log`); `--prerun` 16/0, X10 674.2, X11 PASS licensed (`diag_c148_a2_4_scr_prerun.log:117,136,141`);
  build `--scratch-required` rc 3, census unpredicted rows 1..25 (`diag_c148_a2_4_scrreq.log:3`). Same as 147-c3-3. No gate refused the launch.
- Launch: `py tools/bgrun.py --material --max-min 50 --retry-card tools/bench/cards/task_148-a2-4.json --log tools/bench/diag_c147_p4s06v18_scratch.log -- py -u tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`

## Scratch (ONE run) `tools/bench/diag_c147_p4s06v18_scratch.log` lines 691-1047 (bgrun appends), RESULT 22/0 (:1040), BGRUN END rc=0 after 589 s (:1047)
- Work copy `claudeDev\D1_ring_p4s06_20261008_174730.vi` = NEW byte copy of 3f9ac26b (K3 :748); saved, md5 569ffbf51eb6051bf0fdb58946f9bb02, 319389 B (S2 :1018, PS :1020).
- SG :751 one declared sink gate; SG-p4_rbA_re1 PASS :998 readback (a) t3173 on w23807 (b) t5171 #5058 on w23807 (c) sources [5171] (d) rows 6030 after op 21.
- E1 every checkpoint == sim (21 ops) :999; NG :1000; FR :1001; PRIM #30300 Index Array :938; L0/K1/K2/L1 PASS.
- D PASS :1002 new 16 == 16, lost 8 == 8 (wire_keys_356); reuse NOTED [23807] (kept_by_key), bad [].
- TD PASS :1007 renames 5 licensed: (2832/4160/4165 #2626) 'array'->'element', (9505/9508 #9503) 'Value'->''; unlicensed [].
- PB PASS :1009 extra [] missing [], restored 5, unlicensed []; HB (45921, 46457) :1011; H5 refs 23 == 23 :1024; H2 :1026; H3 :1032; H6 :1034.
- Licence PASS (TD/PB renames == licence 7f70bbf9 `renames`, unlicensed []).
- MEMORY: METERED start 605.2 MB (:753) vs prerun assumption 612.6 (d -7.4); this run's peak 659.5 MB (METER read k21, log :996) vs X10 674.2 (d -14.7);
  <= 680, MEMSTOP 695 not hit. The recipe's own SCRATCH line (:1042) says 661.8 = whole-file max incl. 147-a1-8's run (the recipe reads every METER line of the log, stage_d1_ring_p4_s06v18_scratch.py:171).
- CENSUS-ALL new {IndexArray 1, InnerTerminal 2, Local 1, LoopTunnel 2, OuterTerminal 2, Terminal 4, Wire 12}, lost 2 (:1005-1006) -> written to
  `plan_ring_p4_s06v18_pred.json` by `diag_c148_a2_4_census.py` (5/0, `diag_c148_a2_4_census.log`); pred c4a6a35a -> c1bd6b3e.
- Handles: after restart 34245 (:745), op-0 45987 (:753), exit 33294 (:1035). LabVIEW gone (GATE GONE :1046).

## Error List read (step after the scratch) - FAILED, tool/environment fault
- `py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c148_a2_4_el.log -- py -u tools/errorlist_check.py --vi <work copy> --expected
  tools/bench/errorlist_expected_D1_ring_p4s05_20261008_002621.json --role final` -> BGRUN END rc=2 after 49 s.
- `diag_c148_a2_4_el.log:12-13` UIA and MSAA RAISED `ModuleNotFoundError: No module named 'comtypes'`; :19 'no OCR engine; captures kept, text not
  extracted'; items 0, missing 55; RESULT 9/2 first_fail count_read (:20). Read json `errorlist_D1_ring_p4s06_20261008_174730_20261008_175750.json` (83ffb717, 0 items).
- The same reader worked at 01:23 today (`diag_c147_a1_1_el.log:12-24`: UIA tree, MSAA, OCR engine rapidocr-onnxruntime). The scratch itself ran (it does not use comtypes).
- Error List window opened and Esc closed it (:10, :15); scratch `_elc_*.vi` gone from claudeDev; work copy md5 unchanged (bed md5 unchanged True :19); handles 37247 -> 31279.
- Logged **fp-61** (`checker:errorlist_check:count_read`, `tools/bench/gate_fp_queue.jsonl`). I could not run `py -c "import comtypes"` here (permission prompt).

## Not done (RETURN at the first differing result): EL-ADVISORY, adopt, final EL expected file, fresh load, graph, load_by_vi.
- Ready, unrun: `diag_c148_a2_4_adopt.py`, `_elexp.py <read json>`, `_mkgraph.py`, `_graph.py`, `_memload.py` (copies of the 147-a1-8 set, card id/names only).
- Nothing written to adopted_scratch.jsonl or memory_model.json (88eeb037 unchanged).

## Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c148_a2_4_el.log | no JEV-LADDER line yet (jev_gate.log, 18:0x) | - | fp-61 queued; returned | - |

## After: `diag_c148_a2_4_check_after.log` 24/0: inputs unchanged except pred (census, on purpose); memory_model 88eeb037 unchanged; s05 3f9ac26b,
s04 95e408ff, s03 282301ca, bed 39511877 unchanged; no LabVIEW process (tasklist count 0).

OPEN: the Python env lost `comtypes` (and the OCR engine) between 01:23 and 17:57 - reinstall/repoint, then rerun only the EL read + adopt chain on 569ffbf5 (no new scratch)?
