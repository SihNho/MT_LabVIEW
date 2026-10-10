---
card: 159-a1-1
status: current
date: 2026-10-10
---
# Brief 159-a1-1 (assignment 159-1) - READ-ONLY graph read of the adopted step-1 file 94ffff94 + its load_by_vi entry (PD387(a)(b))

The ONE LabVIEW card of this round. Plan: `docs/d1/ring-p5.md` PD387 (line 387), items (a) and (b). Cycle 158 adopted
`claudeDev\D1_ring_p5s02a_20261010_023239.vi` md5 94ffff94 as an in-between file (scratch 23/0, Error List 56 vs P5-1 45). It is NOT yet the
step-2 base. This card only READS it. Context: `tools/bench/diag_c158_a3_2b_facts.md` (all of it).

## Rules for this card
- NO scratch run, NO rebuild of 94ffff94, NO re-run of the step-1 recipes, NO expected Error List written from the 56 items (PD387(a)).
- The adopted file is read from a never-saved byte copy made by the graph script itself (`K.Stage(..., preload=False)`); the adopted file's md5 is
  quoted before and after and must be equal. No original, no P5-1 file, no s03..s09 opened for editing. No motor or camera.
- Prepared, already dry 1/0 and prerun 15/0 on the old graph (`tools/bench/diag_c158_a3_2b_graph_prerun.log`): `tools/bench/diag_c158_a3_2b_graph.py`
  (c4a0ef66, plan `diag_c158_a3_2b_graph_plan.json` 91fcfbec) and `tools/bench/diag_c158_a3_2b_memload.py` (0a0745db). Do NOT edit them. If either
  needs an edit to run, RETURN with the reason (the assignment session decides); a tool defect that repeats on the same function is a scratch-VI
  verification card, not a third attempt.

## Steps
1. Quote md5 before: the adopted file (94ffff94...), s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, memory_model.json c87d170a,
   adopted_scratch.jsonl 83e74ded. Confirm no LabVIEW process is running (`tasklist`); rig-state is 조립 (STATUS banner) so LabVIEW is allowed.
2. Re-run the graph script's dry + prerun on the CURRENT bytes (`py tools/stage_prerun.py --prerun tools/bench/diag_c158_a3_2b_graph.py --graph
   tools/bench/graph_ring_p5s01_20261009_125622.json`, as in the prerun log's first line, under `bgrun --material --max-min 5`). Expect 15/0. Anything else: RETURN.
3. Launch the read exactly as the script's docstring says: `py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c158_a3_2b_graph.log --
   py -u tools/bench/diag_c158_a3_2b_graph.py`. If the launch gate refuses your own command text, that is a false positive: `py tools/gate_fp.py log`,
   no env bypass, RETURN with the refusal text.
4. Quote the script's gate lines (G1, G2, G3, FS1, B, E5, X) with their PASS/FAIL, `MEM after load`, `MEM after full read`, the graph json path + md5
   (`tools/bench/graph_ring_p5s02a_<ts>.json`) and its row counts (objs, terminals, wires). The prediction in the script's docstring is a prediction, not
   a requirement: a gate FAIL is a fact to report, not a reason to edit the script.
5. After the read: LabVIEW closed AND verified gone (`tasklist`); adopted file md5 == 94ffff9413599d5153a5e6fb409294ab; the other pins unchanged.
6. Only if step 4 produced the graph json and exactly one `MEM after load` line: run `py tools/bgrun.py --material --max-min 2 --log
   tools/bench/diag_c158_a3_2b_memload.log -- py -u tools/bench/diag_c158_a3_2b_memload.py`. Quote its gates and the key-by-key diff of
   `tools/bench/memory_model.json` (the ONLY difference is one added `load_by_vi` entry keyed 94ffff94...). md5 after.

## Report `tools/bench/diag_c159_a1_1_facts.md` (<= 40 lines)
md5 before/after table; prerun verdict; graph gate outcomes; MEM numbers; graph json path + md5 + row counts; memload diff; LabVIEW gone.
Facts only, then `OPEN:` lines. Do not attribute Error List items (that is the next card).
