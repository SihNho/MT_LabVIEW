---
card: 163-a2-1
status: current
date: 2026-10-10
---
# Brief 163-a2-1 (assignment 163-1) - P5-2 STEP-3 SCRATCH (ONE run), adopt as `D1_ring_p5s02c_<ts>.vi`, add ONE `load_by_vi` entry, record the measured census into the pred; the ONE LabVIEW card

This is `tools/bench/cards/brief_162-a1-1.md` plus the deltas of `brief_162-a1-2.md` (read both, and through them brief_161-b3-1 ...) with ONLY the deltas below. Step 2 became step 3: base p5s02b file
f9ae7751 (`claudeDev\D1_ring_p5s02b_20261010_105511.vi`, graph `graph_ring_p5s02b_20261010_111905.json` 431cfd83), plan `plan_ring_p5s02c.json` 930699ec (group I alone, A41..A52, 8 ops,
checkpoints [0,1,2,4,5,7,8]), recipes `tools/recipes/stage_d1_ring_p5s02c{,_scratch}.py` (6d1d5786 / a517557d), pred fc908036, licence c8fdf33a, predicted Error List
`errorlist_predicted_D1_ring_p5s02c_end.json` 373e0bf4 (53 standing, cleared 0, raised 0, UNPREDICTED 2: A45 t_ci7 and A49 t_co7 groups, upper bound 55).
Offline gates already accepted by card 163-a1-4 (`tools/bench/diag_c163_a1_4_facts.md` a4e93503): dry PASS-UNVERIFIED (CEN2 only) on both recipes, prerun PASS 16/0 (X10 658.3 <= 675), `--scratch-required` rc 3
(CENSUS-UNPREDICTED, the scratch measures the census). They are NOT redone, except what the launch gate re-checks.

## Deltas against brief_162-a1-1 / 162-a1-2
1. **Names:** every `c162` / `162-a1-1` / `p5s02b` becomes `c163` / `163-a2-1` / `p5s02c`; facts `tools/bench/diag_c163_a2_1_facts.md` (<= 45 lines); helper scripts `diag_c163_a2_1_*` / `prep_c163_a2_1_*`
   (CALL shared functions; if you copy a helper, say which lines changed). Adopt tooling: the adopt/inv helpers brief_162-a1-1 names (`diag_c158_a2_2_adopt.py`, `diag_c158_a3_2_inv.py`, `diag_c158_a3_2_checklaunch.py`) or their 162-a1-2 successors - find what card 162-a1-2 actually ran in `diag_c162_a1_2_facts.md`.
2. **Hash first (read only):** re-hash the card inputs in the MAIN TREE; a differing stagekit / plan / pred / licence / EL / recipe md5 = RETURN (stagekit is dd57c1ca now, by 163-a1-4). Pin drift of a frozen self-test is explained, not a RETURN.
3. **Launch command = the recipe's own log constant.** The scratch log name is `tools/bench/diag_c163_p5s02c_scratch.log` (`stage_d1_ring_p5s02c_scratch.py:31`; it does not exist now - confirm; if it exists move it aside with a dated name). Run
   `check_launch` on the FULL command first, expect ALLOW: `py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_163-a2-1.json --log tools/bench/diag_c163_p5s02c_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02c_scratch.py`;
   and `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p5s02c.py` (expect rc 3). Any other result: RETURN with the text. The scratch recipe already has its dry + prerun PASS records (163-a1-4); if the gate says otherwise, RETURN.
   Prior art (purpose item 5): group I creates no `delete_object`; if the launch gate demands a prior-art review, run it (verdict `novel` + disposition), else quote the PROVEN-PATTERN line the gate prints. Do not buy it unprompted.
4. **ONE scratch** on a NEW byte copy of f9ae7751 (never edited). Quote the `SCRATCH-` peak line (`stagekit.py` scratch_tail, METER lines read from the log) and the `GATE MEM:` line: peak <= 675 and every BLOCK gate PASS.
   **Any BLOCK gate FAIL, or a peak above 675 = RETURN with the facts: no adopt, no second run, the copy kept and never loaded.** CEN2 is UNPREDICTED (DRY-UNVERIFIED-OK): quote its measured per-class numbers.
   The PB gate of this run is the first live use of class 3 (fp-86 fix, #376 `error in` / `total data array in`): quote its PB lines (class per row).
5. **`tools/bench/memory_model.json`:** only after a structural PASS and adoption, exactly ONE `load_by_vi` key = the adopted file's md5 (hashlib), format of the existing entries (`value` = post-load MB from the load log line, `vi`, a cite
   to that line). JSON compare old vs new: the only difference is the one key; `fail_above_mb` 680.0 and every other key equal.
6. **Adopt, Error List, graph, pred census:** adopted path + md5 on one line; Error List total and per class; item by item against the predicted file 373e0bf4 (the two unpredicted groups named, differences listed); graph json + md5
   (`graph_ring_p5s02c_<stamp>.json`, expected EL `errorlist_expected_D1_ring_p5s02c_<stamp>.json`); measured census into `plan_ring_p5s02c_pred.json` by a script citing the graph reads, census keys only, old -> new md5;
   an `adopted_scratch.jsonl` record in the format the 162-a1-2 card wrote (the chain walk of `pb_inherit_ctx` reads it).
7. **End of card:** s09 eb1d0f31, P5-1 7f2582ae, 94ffff94 and f9ae7751 hashed unchanged with hashlib; no original opened; LabVIEW closed and verified gone (`tasklist`). No `tools/hooks/**` edit, no recipe / plan / licence / EL /
   stage-tool edit, no motor or camera. Concurrent cards: none.

## Report `tools/bench/diag_c163_a2_1_facts.md`
Pre-check lines (hashes, `--check-launch`, `--scratch-required`); the `SCRATCH-` peak and `GATE MEM` lines; PB lines; gates per op class; E1 per checkpoint; per-op + final measured census; adopted file + md5 + load MB; Error List
total + per class + item diff vs 373e0bf4; graph json + md5; the memory-model compare; pred old -> new md5; invariants; LabVIEW gone. `OPEN:` lines (measurements only). Dispatch a hypothesis peer only if a gate FAILS.
